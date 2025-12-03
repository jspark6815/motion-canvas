"""
메인 실행 파일
인터랙티브 AI 디지털 액자의 메인 루프를 실행합니다.
"""
import cv2
import time
from camera.capture import CameraCapture
from camera.detect import PersonDetector
from network.client import ServerClient
from ui.display import Display, DisplayMode


class InteractiveAICanvas:
    """인터랙티브 AI 디지털 액자 메인 클래스"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Args:
            server_url: 서버 URL
        """
        self.camera = CameraCapture()
        self.detector = PersonDetector()
        self.client = ServerClient(server_url)
        self.display = Display()
        
        self.running = False
        self.last_detection_time = 0
        self.detection_interval = 5.0  # 5초마다 감지
        self.last_generation_time = 0
        self.generation_interval = 10.0  # 10초마다 이미지 생성
        
    def initialize(self) -> bool:
        """초기화"""
        print("시스템 초기화 중...")
        
        # 카메라 초기화
        if not self.camera.initialize():
            print("카메라 초기화 실패")
            return False
        
        # 서버 연결 확인
        if not self.client.health_check():
            print("서버 연결 실패. 서버가 실행 중인지 확인하세요.")
            return False
        
        print("초기화 완료")
        return True
    
    def run(self):
        """메인 루프 실행"""
        if not self.initialize():
            return
        
        self.running = True
        print("시스템 시작. 'q'를 눌러 종료하세요.")
        
        try:
            while self.running:
                # 카메라 프레임 캡처
                frame = self.camera.capture_frame()
                if frame is None:
                    continue
                
                # 사람 감지
                detection_result = self.detector.detect_person(frame)
                
                current_time = time.time()
                
                # 사람이 감지되었고 일정 시간이 지났으면 분석 요청
                if (detection_result['has_person'] and 
                    current_time - self.last_detection_time > self.detection_interval):
                    
                    print("사람 감지됨. 서버로 분석 요청...")
                    
                    # 실루엣 업데이트
                    if detection_result['silhouette'] is not None:
                        self.display.update_silhouette(detection_result['silhouette'])
                    
                    # 서버로 이미지 전송 및 분석
                    analysis_result = self.client.send_image_for_analysis(frame)
                    
                    if analysis_result:
                        keywords = analysis_result.get('keywords', [])
                        print(f"추출된 키워드: {keywords}")
                        
                        # 일정 시간이 지났으면 이미지 생성 요청
                        if current_time - self.last_generation_time > self.generation_interval:
                            print("이미지 생성 요청...")
                            generated_image = self.client.request_image_generation(keywords)
                            
                            if generated_image is not None:
                                self.display.update_generated_image(generated_image)
                                self.display.set_mode(DisplayMode.GENERATED_IMAGE)
                                self.last_generation_time = current_time
                                print("이미지 생성 완료")
                    
                    self.last_detection_time = current_time
                
                # 디스플레이 업데이트
                self.display.render(frame)
                
                # 키 입력 처리
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('m'):
                    # 모드 전환
                    self.display._cycle_mode()
                
        except KeyboardInterrupt:
            print("\n시스템 종료 중...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """리소스 정리"""
        print("리소스 정리 중...")
        self.camera.release()
        self.detector.cleanup()
        self.display.cleanup()
        print("종료 완료")


if __name__ == "__main__":
    # 서버 URL 설정 (라즈베리파이에서는 노트북/서버의 IP 주소로 변경)
    SERVER_URL = "http://localhost:8000"  # 개발 환경
    # SERVER_URL = "http://192.168.1.100:8000"  # 라즈베리파이에서 사용 시
    
    canvas = InteractiveAICanvas(SERVER_URL)
    canvas.run()

