"""
라즈베리파이 설정 파일
서버 연결 정보 및 카메라 설정을 관리합니다.
"""
from dataclasses import dataclass


@dataclass
class ServerConfig:
    """서버 연결 설정"""
    host: str = "http://localhost"
    port: int = 8000
    upload_endpoint: str = "/upload"
    
    @property
    def base_url(self) -> str:
        return f"{self.host}:{self.port}"
    
    @property
    def upload_url(self) -> str:
        return f"{self.base_url}{self.upload_endpoint}"


@dataclass
class CameraConfig:
    """카메라 설정"""
    width: int = 1280
    height: int = 720
    format: str = "RGB888"
    capture_interval: float = 2.0  # 촬영 간격 (초)


@dataclass
class DetectionConfig:
    """사람 감지 설정"""
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    cooldown_seconds: float = 5.0  # 연속 촬영 방지 쿨다운


# 기본 설정 인스턴스
server_config = ServerConfig()
camera_config = CameraConfig()
detection_config = DetectionConfig()

