"""
라즈베리파이 설정 파일
환경변수(.env)를 통해 설정을 관리합니다.
"""
import os
from dataclasses import dataclass
from pathlib import Path

# python-dotenv로 .env 파일 로드
try:
    from dotenv import load_dotenv
    
    # .env 파일 위치 (raspberry 폴더 내)
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[Config] 환경변수 로드: {env_path}")
    else:
        print(f"[Config] .env 파일 없음. 기본값 사용: {env_path}")
except ImportError:
    print("[Config] python-dotenv 미설치. 시스템 환경변수 사용.")


def get_env(key: str, default: str) -> str:
    """환경변수 조회"""
    return os.getenv(key, default)


def get_env_int(key: str, default: int) -> int:
    """정수형 환경변수 조회"""
    return int(os.getenv(key, str(default)))


def get_env_float(key: str, default: float) -> float:
    """실수형 환경변수 조회"""
    return float(os.getenv(key, str(default)))


def get_env_bool(key: str, default: bool) -> bool:
    """불리언 환경변수 조회"""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


@dataclass
class ServerConfig:
    """서버 연결 설정"""
    host: str
    port: int
    upload_endpoint: str
    
    @property
    def base_url(self) -> str:
        return f"{self.host}:{self.port}"
    
    @property
    def upload_url(self) -> str:
        return f"{self.base_url}{self.upload_endpoint}"


@dataclass
class CameraConfig:
    """카메라 설정"""
    width: int
    height: int
    format: str
    capture_interval: float  # 촬영 간격 (초)


@dataclass
class DetectionConfig:
    """사람 감지 설정"""
    min_detection_confidence: float
    cooldown_seconds: float  # 연속 촬영 방지 쿨다운
    enabled: bool  # 감지 기능 활성화 여부


# 환경변수에서 설정 로드
server_config = ServerConfig(
    host=get_env("SERVER_HOST", "http://localhost"),
    port=get_env_int("SERVER_PORT", 8000),
    upload_endpoint=get_env("SERVER_UPLOAD_ENDPOINT", "/upload"),
)

camera_config = CameraConfig(
    width=get_env_int("CAMERA_WIDTH", 1280),
    height=get_env_int("CAMERA_HEIGHT", 720),
    format=get_env("CAMERA_FORMAT", "RGB888"),
    capture_interval=get_env_float("CAMERA_CAPTURE_INTERVAL", 2.0),
)

detection_config = DetectionConfig(
    min_detection_confidence=get_env_float("DETECTION_MIN_CONFIDENCE", 0.5),
    cooldown_seconds=get_env_float("DETECTION_COOLDOWN_SECONDS", 5.0),
    enabled=get_env_bool("DETECTION_ENABLED", True),
)


# 설정 출력 (디버깅용)
def print_config() -> None:
    """현재 설정 출력"""
    print("=" * 50)
    print("📋 현재 설정")
    print("=" * 50)
    print(f"[Server]")
    print(f"  - Host: {server_config.host}")
    print(f"  - Port: {server_config.port}")
    print(f"  - Upload URL: {server_config.upload_url}")
    print(f"[Camera]")
    print(f"  - Resolution: {camera_config.width}x{camera_config.height}")
    print(f"  - Format: {camera_config.format}")
    print(f"  - Capture Interval: {camera_config.capture_interval}초")
    print(f"[Detection]")
    print(f"  - Enabled: {detection_config.enabled}")
    print(f"  - Min Confidence: {detection_config.min_detection_confidence}")
    print(f"  - Cooldown: {detection_config.cooldown_seconds}초")
    print("=" * 50)


if __name__ == "__main__":
    print_config()
