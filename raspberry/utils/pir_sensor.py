"""
PIR(적외선) 인체감지 센서 제어 모듈
라즈베리파이 GPIO를 사용하여 PIR 센서를 제어합니다.

PIR 센서는 적외선을 감지하여 사람의 움직임을 탐지합니다.
OpenCV HOG 감지와 조합하면 정확도를 높일 수 있습니다.

일반적인 PIR 센서 (HC-SR501 등) 연결:
- VCC: 5V (또는 3.3V, 센서에 따라 다름)
- GND: GND
- OUT: GPIO 핀 (기본: GPIO 4)
"""
import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    print("[PIRSensor] RPi.GPIO 없음. Mock 모드로 동작합니다.")


@dataclass
class PIRConfig:
    """PIR 센서 설정"""
    enabled: bool = False
    pin: int = 4  # GPIO 핀 번호 (BCM)
    debounce_time: float = 0.5  # 디바운스 시간 (초)
    cooldown_time: float = 2.0  # 감지 후 쿨다운 시간 (초)


class PIRSensor:
    """PIR 인체감지 센서 제어 클래스"""
    
    def __init__(self, config: PIRConfig) -> None:
        """
        PIR 센서 초기화
        
        Args:
            config: PIR 센서 설정
        """
        self.config = config
        self._initialized: bool = False
        self._last_detection_time: float = 0
        self._motion_detected: bool = False
        self._callback: Optional[Callable[[], None]] = None
        self._lock = threading.Lock()
    
    def initialize(self) -> bool:
        """PIR 센서 초기화"""
        if not self.config.enabled:
            print("[PIRSensor] PIR 센서 비활성화됨")
            return False
        
        if self._initialized:
            return True
        
        if not HAS_GPIO:
            print("[PIRSensor] Mock 모드 초기화 (GPIO 없음)")
            self._initialized = True
            return True
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # PIR 센서 핀 설정 (입력, 풀다운)
            GPIO.setup(self.config.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            self._initialized = True
            print(f"[PIRSensor] 초기화 완료 (GPIO {self.config.pin})")
            return True
            
        except Exception as e:
            print(f"[PIRSensor] 초기화 실패: {e}")
            return False
    
    def start_detection(self, callback: Optional[Callable[[], None]] = None) -> bool:
        """
        인터럽트 기반 감지 시작
        
        Args:
            callback: 감지 시 호출할 콜백 함수
            
        Returns:
            시작 성공 여부
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        self._callback = callback
        
        if HAS_GPIO:
            try:
                # 기존 이벤트 제거
                GPIO.remove_event_detect(self.config.pin)
            except Exception:
                pass
            
            # 상승 에지 감지 (LOW → HIGH)
            GPIO.add_event_detect(
                self.config.pin,
                GPIO.RISING,
                callback=self._on_motion_detected,
                bouncetime=int(self.config.debounce_time * 1000)
            )
            print("[PIRSensor] 인터럽트 감지 시작")
        
        return True
    
    def stop_detection(self) -> None:
        """인터럽트 감지 중지"""
        if HAS_GPIO and self._initialized:
            try:
                GPIO.remove_event_detect(self.config.pin)
            except Exception:
                pass
        
        self._callback = None
        print("[PIRSensor] 감지 중지")
    
    def _on_motion_detected(self, channel: int) -> None:
        """
        인터럽트 콜백 (내부용)
        
        Args:
            channel: GPIO 채널 번호
        """
        current_time = time.time()
        
        with self._lock:
            # 쿨다운 체크
            if current_time - self._last_detection_time < self.config.cooldown_time:
                return
            
            self._last_detection_time = current_time
            self._motion_detected = True
        
        print(f"[PIRSensor] 🔴 움직임 감지! (GPIO {channel})")
        
        # 콜백 호출
        if self._callback:
            try:
                self._callback()
            except Exception as e:
                print(f"[PIRSensor] 콜백 오류: {e}")
    
    def is_motion_detected(self) -> bool:
        """
        현재 움직임 감지 상태 확인 (폴링 방식)
        
        Returns:
            움직임 감지 여부
        """
        if not self._initialized or not self.config.enabled:
            return False
        
        if not HAS_GPIO:
            # Mock 모드: 항상 False
            return False
        
        try:
            current_time = time.time()
            
            # 쿨다운 체크
            with self._lock:
                if current_time - self._last_detection_time < self.config.cooldown_time:
                    return False
            
            # GPIO 상태 읽기
            if GPIO.input(self.config.pin) == GPIO.HIGH:
                with self._lock:
                    self._last_detection_time = current_time
                    self._motion_detected = True
                print("[PIRSensor] 🔴 움직임 감지!")
                return True
            
            return False
            
        except Exception as e:
            print(f"[PIRSensor] 읽기 오류: {e}")
            return False
    
    def check_and_clear(self) -> bool:
        """
        움직임 감지 상태 확인 후 클리어
        
        Returns:
            움직임이 감지되었는지 여부
        """
        with self._lock:
            detected = self._motion_detected
            self._motion_detected = False
            return detected
    
    def wait_for_motion(self, timeout: float = 10.0) -> bool:
        """
        움직임 감지 대기 (블로킹)
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            움직임 감지 여부
        """
        if not self._initialized or not self.config.enabled:
            return False
        
        if not HAS_GPIO:
            time.sleep(timeout)
            return False
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_motion_detected():
                return True
            time.sleep(0.1)
        
        return False
    
    @property
    def is_enabled(self) -> bool:
        """PIR 센서 활성화 여부"""
        return self.config.enabled and self._initialized
    
    def cleanup(self) -> None:
        """리소스 정리"""
        self.stop_detection()
        
        if HAS_GPIO and self._initialized:
            try:
                GPIO.cleanup(self.config.pin)
            except Exception:
                pass
        
        self._initialized = False
        print("[PIRSensor] 리소스 해제")
    
    def __enter__(self) -> "PIRSensor":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()


# 테스트
if __name__ == "__main__":
    print("🔴 PIR 센서 테스트")
    print("움직임을 감지하면 메시지가 출력됩니다.")
    print("Ctrl+C로 종료\n")
    
    config = PIRConfig(enabled=True, pin=4)
    
    with PIRSensor(config) as pir:
        try:
            while True:
                if pir.is_motion_detected():
                    print("✅ 움직임 감지됨!")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n종료")

