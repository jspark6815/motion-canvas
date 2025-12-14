"""
RGB LED 제어 모듈
라즈베리파이 GPIO PWM을 사용하여 RGB LED를 제어합니다.
"""
import time
from typing import Tuple, Optional
from dataclasses import dataclass

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    print("[RGBLEDController] RPi.GPIO 없음. Mock 모드로 동작합니다.")


@dataclass
class RGBColor:
    """RGB 색상 정의"""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    
    @classmethod
    def RED(cls) -> "RGBColor":
        return cls(255, 0, 0)
    
    @classmethod
    def GREEN(cls) -> "RGBColor":
        return cls(0, 255, 0)
    
    @classmethod
    def BLUE(cls) -> "RGBColor":
        return cls(0, 0, 255)
    
    @classmethod
    def WHITE(cls) -> "RGBColor":
        return cls(255, 255, 255)
    
    @classmethod
    def YELLOW(cls) -> "RGBColor":
        return cls(255, 255, 0)
    
    @classmethod
    def CYAN(cls) -> "RGBColor":
        return cls(0, 255, 255)
    
    @classmethod
    def MAGENTA(cls) -> "RGBColor":
        return cls(255, 0, 255)
    
    @classmethod
    def ORANGE(cls) -> "RGBColor":
        return cls(255, 165, 0)
    
    @classmethod
    def OFF(cls) -> "RGBColor":
        return cls(0, 0, 0)


class RGBLEDController:
    """RGB LED 제어 클래스 (PWM 사용)"""
    
    def __init__(
        self, 
        red_pin: int = 17, 
        green_pin: int = 27, 
        blue_pin: int = 22,
        common_anode: bool = False,
        pwm_frequency: int = 1000
    ) -> None:
        """
        RGB LED 초기화
        
        Args:
            red_pin: 빨강 GPIO 핀 번호 (BCM)
            green_pin: 초록 GPIO 핀 번호 (BCM)
            blue_pin: 파랑 GPIO 핀 번호 (BCM)
            common_anode: Common Anode 타입이면 True
            pwm_frequency: PWM 주파수 (Hz)
        """
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.common_anode = common_anode
        self.pwm_frequency = pwm_frequency
        
        self._red_pwm: Optional[object] = None
        self._green_pwm: Optional[object] = None
        self._blue_pwm: Optional[object] = None
        self._initialized: bool = False
    
    def initialize(self) -> bool:
        """RGB LED 초기화"""
        if self._initialized:
            return True
        
        if not HAS_GPIO:
            print("[RGBLEDController] Mock 모드 초기화")
            self._initialized = True
            return True
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # 핀 설정
            GPIO.setup(self.red_pin, GPIO.OUT)
            GPIO.setup(self.green_pin, GPIO.OUT)
            GPIO.setup(self.blue_pin, GPIO.OUT)
            
            # PWM 초기화
            self._red_pwm = GPIO.PWM(self.red_pin, self.pwm_frequency)
            self._green_pwm = GPIO.PWM(self.green_pin, self.pwm_frequency)
            self._blue_pwm = GPIO.PWM(self.blue_pin, self.pwm_frequency)
            
            # PWM 시작 (duty cycle 0%)
            self._red_pwm.start(0)
            self._green_pwm.start(0)
            self._blue_pwm.start(0)
            
            self._initialized = True
            print(f"[RGBLEDController] 초기화 완료 (R:{self.red_pin}, G:{self.green_pin}, B:{self.blue_pin})")
            return True
            
        except Exception as e:
            print(f"[RGBLEDController] 초기화 실패: {e}")
            return False
    
    def _value_to_duty(self, value: int) -> float:
        """RGB 값(0-255)을 duty cycle(0-100)로 변환"""
        duty = (value / 255) * 100
        if self.common_anode:
            duty = 100 - duty  # Common Anode는 반전
        return duty
    
    def set_color(self, color: RGBColor) -> None:
        """RGB 색상 설정"""
        if not self._initialized:
            self.initialize()
        
        if HAS_GPIO and self._red_pwm and self._green_pwm and self._blue_pwm:
            self._red_pwm.ChangeDutyCycle(self._value_to_duty(color.r))
            self._green_pwm.ChangeDutyCycle(self._value_to_duty(color.g))
            self._blue_pwm.ChangeDutyCycle(self._value_to_duty(color.b))
        else:
            print(f"[RGBLEDController] 색상 설정 (Mock): R={color.r}, G={color.g}, B={color.b}")
    
    def set_rgb(self, r: int, g: int, b: int) -> None:
        """RGB 값으로 색상 설정 (0-255)"""
        self.set_color(RGBColor(r, g, b))
    
    def off(self) -> None:
        """LED 끄기"""
        self.set_color(RGBColor.OFF())
    
    def on(self, color: Optional[RGBColor] = None) -> None:
        """LED 켜기"""
        if color is None:
            color = RGBColor.WHITE()
        self.set_color(color)
    
    def blink(
        self, 
        times: int = 3, 
        color: Optional[RGBColor] = None,
        on_duration: float = 0.3,
        off_duration: float = 0.3
    ) -> None:
        """
        LED 깜빡이기
        
        Args:
            times: 깜빡임 횟수
            color: 깜빡일 색상 (기본: 흰색)
            on_duration: 켜져있는 시간 (초)
            off_duration: 꺼져있는 시간 (초)
        """
        if color is None:
            color = RGBColor.WHITE()
        
        for i in range(times):
            self.set_color(color)
            time.sleep(on_duration)
            self.off()
            if i < times - 1:  # 마지막이 아니면 대기
                time.sleep(off_duration)
    
    def countdown_blink(
        self, 
        count: int = 3,
        colors: Optional[list] = None,
        blink_duration: float = 0.5
    ) -> None:
        """
        카운트다운 깜빡임 (촬영 전 사용)
        
        Args:
            count: 카운트다운 숫자
            colors: 각 카운트에 사용할 색상 리스트 (기본: 빨강 → 노랑 → 초록)
            blink_duration: 각 깜빡임 지속 시간 (초)
        """
        if colors is None:
            # 기본: 빨강 → 노랑 → 초록 (신호등 순서)
            if count == 3:
                colors = [RGBColor.RED(), RGBColor.YELLOW(), RGBColor.GREEN()]
            elif count == 2:
                colors = [RGBColor.YELLOW(), RGBColor.GREEN()]
            else:
                colors = [RGBColor.GREEN()] * count
        
        for i, color in enumerate(colors[:count]):
            remaining = count - i
            print(f"📸 촬영까지 {remaining}...")
            self.set_color(color)
            time.sleep(blink_duration)
            self.off()
            time.sleep(blink_duration * 0.5)
        
        # 촬영 순간 흰색 플래시
        print("📸 찰칵!")
        self.set_color(RGBColor.WHITE())
        time.sleep(0.2)
        self.off()
    
    def rainbow_cycle(self, duration: float = 2.0, steps: int = 100) -> None:
        """무지개 색상 순환 (테스트용)"""
        delay = duration / steps
        
        for i in range(steps):
            # HSV to RGB 간단 변환
            h = i / steps
            if h < 1/6:
                r, g, b = 255, int(255 * h * 6), 0
            elif h < 2/6:
                r, g, b = int(255 * (2 - h * 6)), 255, 0
            elif h < 3/6:
                r, g, b = 0, 255, int(255 * (h * 6 - 2))
            elif h < 4/6:
                r, g, b = 0, int(255 * (4 - h * 6)), 255
            elif h < 5/6:
                r, g, b = int(255 * (h * 6 - 4)), 0, 255
            else:
                r, g, b = 255, 0, int(255 * (6 - h * 6))
            
            self.set_rgb(r, g, b)
            time.sleep(delay)
        
        self.off()
    
    def cleanup(self) -> None:
        """리소스 정리"""
        self.off()
        
        if HAS_GPIO:
            if self._red_pwm:
                self._red_pwm.stop()
            if self._green_pwm:
                self._green_pwm.stop()
            if self._blue_pwm:
                self._blue_pwm.stop()
            
            try:
                GPIO.cleanup([self.red_pin, self.green_pin, self.blue_pin])
            except Exception:
                pass
        
        self._initialized = False
        print("[RGBLEDController] 리소스 해제")
    
    def __enter__(self) -> "RGBLEDController":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()


# 테스트
if __name__ == "__main__":
    print("🌈 RGB LED 테스트")
    
    with RGBLEDController(red_pin=17, green_pin=27, blue_pin=22) as led:
        print("\n1. 기본 색상 테스트")
        for name, color in [
            ("빨강", RGBColor.RED()),
            ("초록", RGBColor.GREEN()),
            ("파랑", RGBColor.BLUE()),
            ("노랑", RGBColor.YELLOW()),
            ("흰색", RGBColor.WHITE()),
        ]:
            print(f"  {name}")
            led.set_color(color)
            time.sleep(0.5)
        
        led.off()
        time.sleep(0.5)
        
        print("\n2. 깜빡임 테스트 (3회)")
        led.blink(times=3, color=RGBColor.WHITE())
        
        time.sleep(0.5)
        
        print("\n3. 카운트다운 테스트")
        led.countdown_blink(count=3)
        
        print("\n✅ 테스트 완료!")

