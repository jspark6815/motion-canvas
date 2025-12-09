"""
LED 제어 모듈
라즈베리파이 GPIO를 사용하여 LED를 제어합니다.
"""
import time
from typing import Optional

try:
    from gpiozero import LED
    HAS_GPIOZERO = True
except ImportError:
    try:
        import RPi.GPIO as GPIO
        HAS_RPI_GPIO = True
    except ImportError:
        HAS_RPI_GPIO = False
    HAS_GPIOZERO = False


class LEDController:
    """LED 제어 클래스"""
    
    def __init__(self, pin: int = 18) -> None:
        """
        LED 초기화
        
        Args:
            pin: GPIO 핀 번호 (기본값: 18)
        """
        self.pin = pin
        self._led: Optional[object] = None
        self._initialized: bool = False
    
    def initialize(self) -> bool:
        """LED 초기화"""
        if self._initialized:
            return True
        
        if HAS_GPIOZERO:
            try:
                self._led = LED(self.pin)
                self._initialized = True
                print(f"[LEDController] GPIO Zero로 LED 초기화 (핀 {self.pin})")
                return True
            except Exception as e:
                print(f"[LEDController] GPIO Zero 초기화 실패: {e}")
        elif HAS_RPI_GPIO:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.OUT)
                self._initialized = True
                print(f"[LEDController] RPi.GPIO로 LED 초기화 (핀 {self.pin})")
                return True
            except Exception as e:
                print(f"[LEDController] RPi.GPIO 초기화 실패: {e}")
        else:
            print("[LEDController] GPIO 라이브러리 없음. Mock 모드로 동작합니다.")
            self._initialized = True
            return True
        
        return False
    
    def on(self) -> None:
        """LED 켜기"""
        if not self._initialized:
            self.initialize()
        
        if HAS_GPIOZERO and self._led:
            self._led.on()
        elif HAS_RPI_GPIO:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            print("[LEDController] LED ON (Mock)")
    
    def off(self) -> None:
        """LED 끄기"""
        if not self._initialized:
            return
        
        if HAS_GPIOZERO and self._led:
            self._led.off()
        elif HAS_RPI_GPIO:
            GPIO.output(self.pin, GPIO.LOW)
        else:
            print("[LEDController] LED OFF (Mock)")
    
    def blink(self, times: int = 1, duration: float = 0.5) -> None:
        """
        LED 깜빡이기
        
        Args:
            times: 깜빡임 횟수
            duration: 깜빡임 간격 (초)
        """
        for _ in range(times):
            self.on()
            time.sleep(duration)
            self.off()
            time.sleep(duration)
    
    def cleanup(self) -> None:
        """리소스 정리"""
        self.off()
        if HAS_RPI_GPIO:
            try:
                GPIO.cleanup(self.pin)
            except Exception:
                pass
        self._initialized = False
        print("[LEDController] 리소스 해제")
    
    def __enter__(self) -> "LEDController":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()

