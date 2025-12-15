"""
라즈베리파이 메인 실행 파일
사람 감지 시 자동으로 사진을 촬영하여 서버에 업로드합니다.
"""
import time
import signal
import sys
from typing import Optional

from raspberry.config import (
    camera_config, 
    detection_config,
    led_config,
    server_config,
    stream_config,
    pir_config,
    print_config
)
from raspberry.camera.picam_source import PiCameraSource
from raspberry.vision.person_detector import PersonDetector
from raspberry.vision.mediapipe_detector import MediaPipeDetector, HAS_MEDIAPIPE
from raspberry.vision.segmentation import ImageSegmenter
from raspberry.network.api_client import APIClient
from raspberry.utils.image_encode import encode_jpeg, generate_filename
from raspberry.utils.led_controller import LEDController
from raspberry.utils.rgb_led_controller import RGBLEDController
from raspberry.utils.pir_sensor import PIRSensor
from raspberry.utils.countdown import show_countdown
from raspberry.stream.mjpeg_server import MJPEGStreamServer
from raspberry.stream.websocket_pusher import WebSocketStreamPusher


class AIArtCapture:
    """AI 아트 캡처 시스템 메인 클래스"""
    
    def __init__(self) -> None:
        self.camera: Optional[PiCameraSource] = None
        self.detector: Optional[PersonDetector] = None
        self.mediapipe_detector: Optional[MediaPipeDetector] = None
        self.segmenter: Optional[ImageSegmenter] = None
        self.api_client: Optional[APIClient] = None
        self.led: Optional[LEDController] = None
        self.rgb_led: Optional[RGBLEDController] = None
        self.pir_sensor: Optional[PIRSensor] = None
        self.stream_server: Optional[MJPEGStreamServer] = None
        self.stream_pusher: Optional[WebSocketStreamPusher] = None
        
        self._running: bool = False
        self._last_capture_time: float = 0
        self._pir_motion_detected: bool = False  # PIR 센서 감지 플래그
        self._use_mediapipe: bool = False  # 실제로 MediaPipe 사용 여부
    
    def initialize(self) -> bool:
        """시스템 초기화"""
        print("=" * 50)
        print("🎨 AI Art Capture System 초기화 중...")
        print("=" * 50)
        
        # 설정 출력
        print_config()
        
        try:
            # 카메라 초기화
            self.camera = PiCameraSource(camera_config)
            self.camera.start()
            
            # 사람 감지기 초기화
            if detection_config.enabled:
                # MediaPipe 사용 시도
                if detection_config.use_mediapipe and HAS_MEDIAPIPE:
                    self.mediapipe_detector = MediaPipeDetector(detection_config)
                    if self.mediapipe_detector.initialize():
                        self._use_mediapipe = True
                        print("🎯 MediaPipe 사람 감지 활성화 (딥러닝 기반)")
                    else:
                        print("⚠️ MediaPipe 초기화 실패, HOG로 폴백")
                        self.mediapipe_detector = None
                
                # MediaPipe 사용 불가 시 HOG 사용
                if not self._use_mediapipe:
                    self.detector = PersonDetector(detection_config)
                    self.detector.initialize()
                    print("🎯 HOG 사람 감지 활성화 (OpenCV)")
            else:
                print("[Main] 사람 감지 비활성화됨 - 모든 프레임 업로드")
            
            # 세그멘터 초기화
            self.segmenter = ImageSegmenter()
            
            # LED 초기화 (RGB LED 우선)
            if led_config.rgb_enabled:
                self.rgb_led = RGBLEDController(
                    red_pin=led_config.rgb_red_pin,
                    green_pin=led_config.rgb_green_pin,
                    blue_pin=led_config.rgb_blue_pin,
                    common_anode=led_config.rgb_common_anode
                )
                self.rgb_led.initialize()
                print("🌈 RGB LED 활성화")
            elif led_config.enabled:
                self.led = LEDController(pin=led_config.pin)
                self.led.initialize()
            
            # PIR 센서 초기화
            if pir_config.enabled:
                self.pir_sensor = PIRSensor(pir_config)
                if self.pir_sensor.initialize():
                    # 인터럽트 기반 감지 시작
                    self.pir_sensor.start_detection(callback=self._on_pir_motion)
                    print(f"🔴 PIR 센서 활성화 (GPIO {pir_config.pin})")
                    if pir_config.require_pir_for_capture:
                        print("   → PIR + HOG 조합 필수 모드")
                    else:
                        print("   → PIR 감지 시 HOG 확인 모드")
                else:
                    print("⚠️ PIR 센서 초기화 실패")
                    self.pir_sensor = None
            
            # API 클라이언트 초기화
            self.api_client = APIClient(server_config)
            
            # 서버 연결 확인
            if self.api_client.check_health():
                print(f"✅ 서버 연결 성공: {server_config.base_url}")
            else:
                print(f"⚠️ 서버 연결 실패: {server_config.base_url}")
                print("   서버가 실행 중인지 확인하세요.")
            
            # MJPEG 스트림 서버 시작 (로컬 네트워크용, 백그라운드)
            if stream_config.enabled and not stream_config.push_enabled:
                self.stream_server = MJPEGStreamServer(self.camera, stream_config)
                self.stream_server.start()
            
            # EC2로 스트림 푸시 (외부 네트워크용)
            if stream_config.push_enabled:
                self.stream_pusher = WebSocketStreamPusher(
                    camera_source=self.camera,
                    server_url=stream_config.push_url,
                    secret=stream_config.push_secret,
                    config=stream_config
                )
                self.stream_pusher.start()
            
            print("✅ 시스템 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self) -> None:
        """리소스 정리"""
        print("\n🔄 시스템 종료 중...")
        
        if self.stream_server:
            self.stream_server.stop()
        if self.stream_pusher:
            self.stream_pusher.stop()
        if self.camera:
            self.camera.stop()
        if self.detector:
            self.detector.release()
        if self.mediapipe_detector:
            self.mediapipe_detector.release()
        if self.pir_sensor:
            self.pir_sensor.cleanup()
        if self.led:
            self.led.cleanup()
        if self.rgb_led:
            self.rgb_led.cleanup()
        if self.api_client:
            self.api_client.close()
        
        print("✅ 정리 완료")
    
    def _on_pir_motion(self) -> None:
        """PIR 센서 감지 콜백"""
        self._pir_motion_detected = True
    
    def _can_capture(self) -> bool:
        """쿨다운 확인"""
        current_time = time.time()
        elapsed = current_time - self._last_capture_time
        return elapsed >= detection_config.cooldown_seconds
    
    def _process_frame(self) -> bool:
        """
        단일 프레임 처리
        
        Returns:
            사람 감지 및 업로드 성공 여부
        """
        if not self.camera or not self.segmenter:
            return False
        
        # PIR 센서 확인 (활성화된 경우)
        pir_triggered = False
        if self.pir_sensor and pir_config.enabled:
            # 인터럽트로 설정된 플래그 확인
            if self._pir_motion_detected:
                pir_triggered = True
                self._pir_motion_detected = False
                print("🔴 PIR 센서: 움직임 감지!")
            
            # PIR 감지가 필수인데 감지되지 않았으면 스킵
            if pir_config.require_pir_for_capture and not pir_triggered:
                return False
        
        # 프레임 캡처
        frame = self.camera.capture()
        if frame is None:
            return False
        
        # 사람 감지 (활성화된 경우)
        if detection_config.enabled and (self.detector or self.mediapipe_detector):
            # MediaPipe 또는 HOG로 감지
            if self._use_mediapipe and self.mediapipe_detector:
                detections = self.mediapipe_detector.detect(frame)
                detector_name = "MediaPipe"
            else:
                detections = self.detector.detect(frame) if self.detector else []
                detector_name = "HOG"
            
            # 감지 결과 확인
            if not detections:
                # PIR만 감지되고 사람 감지 실패한 경우 로그
                if pir_triggered:
                    print(f"   → {detector_name} 감지 실패 (사람 아님 또는 범위 밖)")
                return False
            
            if not self._can_capture():
                print("⏳ 쿨다운 중...")
                return False
            
            # 감지 소스 표시
            if pir_triggered:
                print(f"👤 사람 감지! [PIR+{detector_name}] (신뢰도: {detections[0].confidence:.2f})")
            else:
                print(f"👤 사람 감지! [{detector_name}] (신뢰도: {detections[0].confidence:.2f})")
            
            # 카운트다운 표시 (RGB LED 우선)
            if self.rgb_led and led_config.rgb_enabled:
                # RGB LED 카운트다운: 빨강 → 노랑 → 초록 → 찰칵!
                countdown = detection_config.countdown_seconds if detection_config.countdown_seconds > 0 else 3
                self.rgb_led.countdown_blink(count=countdown)
            elif detection_config.countdown_seconds > 0:
                show_countdown(
                    seconds=detection_config.countdown_seconds,
                    message="촬영까지",
                    show_led=self.led if (led_config.enabled and led_config.blink_on_countdown) else None
                )
            elif self.led and led_config.enabled:
                # 카운트다운 없으면 LED만 깜빡임
                self.led.blink(times=2, duration=0.3)
            
            # 최종 프레임 캡처 (카운트다운 후)
            frame = self.camera.capture()
            if frame is None:
                return False
            
            # 전체 프레임 사용 또는 크롭
            if detection_config.use_full_frame:
                # 전체 프레임 업로드 (사람이 잘리는 문제 방지)
                print("[Main] 전체 프레임 사용")
                processed = frame
            else:
                # 바운딩 박스 크롭 (너무 작으면 확대)
                bbox = detections[0]
                h, w = frame.shape[:2]
                area_ratio = (bbox.width * bbox.height) / (w * h)

                if area_ratio < detection_config.min_bbox_area_ratio:
                    print(f"[Main] 감지 영역이 작음 ({area_ratio:.3f}). 영역 확대 후 사용.")
                    bbox = self.segmenter.expand_bbox(
                        bbox=bbox,
                        frame_shape=frame.shape,
                        scale=detection_config.bbox_scale_up
                    )

                processed = self.segmenter.crop_bbox(frame, bbox)
                processed = self.segmenter.add_padding(processed, padding=10)
        else:
            # 감지 비활성화: 전체 프레임 사용
            if not self._can_capture():
                return False
            processed = frame
        
        # JPEG 인코딩
        image_bytes = encode_jpeg(processed, quality=90)
        if not image_bytes:
            print("❌ 이미지 인코딩 실패")
            return False
        
        # 서버 업로드
        filename = generate_filename()
        print(f"📤 업로드 중: {filename}")
        
        if self.api_client:
            response = self.api_client.upload_image(image_bytes, filename)
            
            if response.success:
                print(f"✅ 업로드 성공! ID: {response.image_id}")
                self._last_capture_time = time.time()
                return True
            else:
                print(f"❌ 업로드 실패: {response.error}")
        
        return False
    
    def run(self) -> None:
        """메인 루프 실행"""
        self._running = True
        
        print("\n" + "=" * 50)
        print("🚀 캡처 시스템 시작")
        print(f"   - 촬영 간격: {camera_config.capture_interval}초")
        print(f"   - 쿨다운: {detection_config.cooldown_seconds}초")
        print(f"   - 감지 활성화: {detection_config.enabled}")
        if detection_config.enabled:
            if self._use_mediapipe:
                print(f"   - 감지 방식: 🎯 MediaPipe (딥러닝)")
            else:
                print(f"   - 감지 방식: 📊 HOG (OpenCV)")
        print(f"   - 카운트다운: {detection_config.countdown_seconds}초")
        if led_config.rgb_enabled:
            print(f"   - LED: 🌈 RGB LED (R:{led_config.rgb_red_pin}, G:{led_config.rgb_green_pin}, B:{led_config.rgb_blue_pin})")
        elif led_config.enabled:
            print(f"   - LED: 단색 (핀 {led_config.pin})")
        else:
            print(f"   - LED: 비활성화")
        # PIR 센서 정보
        if pir_config.enabled and self.pir_sensor:
            mode = "PIR+HOG 필수" if pir_config.require_pir_for_capture else "PIR 보조"
            print(f"   - PIR 센서: 🔴 활성화 (GPIO {pir_config.pin}, {mode})")
        else:
            print(f"   - PIR 센서: 비활성화")
        print(f"   - 최소 감지영역 비율: {detection_config.min_bbox_area_ratio}")
        print(f"   - 감지영역 확대 비율: {detection_config.bbox_scale_up}")
        if stream_config.enabled and not stream_config.push_enabled:
            print(f"   - 로컬 스트림: http://0.0.0.0:{stream_config.port}/stream.mjpg")
        if stream_config.push_enabled:
            print(f"   - EC2 스트림 푸시: {stream_config.push_url}")
        print("   - 종료: Ctrl+C")
        print("=" * 50 + "\n")
        
        while self._running:
            try:
                self._process_frame()
                time.sleep(camera_config.capture_interval)
                
            except KeyboardInterrupt:
                print("\n⚠️ 사용자 중단 요청...")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)
        
        self._running = False
    
    def stop(self) -> None:
        """실행 중지"""
        self._running = False


def signal_handler(signum, frame):
    """시그널 핸들러"""
    print("\n🛑 종료 시그널 수신...")
    sys.exit(0)


def main() -> None:
    """메인 함수"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 시스템 생성 및 실행
    system = AIArtCapture()
    
    try:
        if system.initialize():
            system.run()
    finally:
        system.cleanup()


if __name__ == "__main__":
    main()
