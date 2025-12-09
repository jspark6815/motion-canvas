"""
카운트다운 표시 모듈
터미널에 카운트다운을 표시합니다.
"""
import time
import sys
from typing import Optional


def show_countdown(
    seconds: int,
    message: str = "촬영까지",
    show_led: Optional[object] = None
) -> None:
    """
    카운트다운 표시
    
    Args:
        seconds: 카운트다운 시간 (초)
        message: 표시할 메시지
        show_led: LED 컨트롤러 (선택사항)
    """
    print(f"\n{'=' * 50}")
    print(f"📸 {message}")
    print(f"{'=' * 50}")
    
    for i in range(seconds, 0, -1):
        # LED 깜빡이기 (마지막 3초)
        if show_led and i <= 3:
            show_led.blink(times=1, duration=0.2)
        elif show_led:
            show_led.on()
        
        # 큰 숫자로 표시
        countdown_str = f"\n{' ' * 20}{i:2d}\n"
        sys.stdout.write(countdown_str)
        sys.stdout.flush()
        
        time.sleep(1)
        
        # 이전 줄 지우기
        sys.stdout.write("\033[F\033[K")  # 커서 위로 이동 후 줄 지우기
    
    # 최종 메시지
    print(f"\n{' ' * 15}📸 촬영!")
    print(f"{'=' * 50}\n")
    
    if show_led:
        show_led.off()


def show_simple_countdown(seconds: int) -> None:
    """
    간단한 카운트다운 (한 줄)
    
    Args:
        seconds: 카운트다운 시간 (초)
    """
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r⏱️  촬영까지 {i:2d}초...")
        sys.stdout.flush()
        time.sleep(1)
    
    sys.stdout.write("\r✅ 촬영!                    \n")
    sys.stdout.flush()

