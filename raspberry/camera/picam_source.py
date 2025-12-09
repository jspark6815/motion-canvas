"""
Picamera2 기반 카메라 소스 모듈
라즈베리파이 카메라 모듈3 제어를 담당합니다.
"""
from typing import Optional
import numpy as np
from numpy.typing import NDArray

try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False
    print("[PiCameraSource] picamera2 미설치. Mock 모드로 동작합니다.")

from raspberry.config import CameraConfig, camera_config


class PiCameraSource:
    """Picamera2 래퍼 클래스"""
    
    def __init__(self, config: CameraConfig = camera_config) -> None:
        self.config = config
        self._camera: Optional[Picamera2] = None
        self._is_running: bool = False
    
    def start(self) -> None:
        """카메라 초기화 및 시작"""
        if self._is_running:
            return
        
        if HAS_PICAMERA:
            try:
                self._camera = Picamera2()
                cam_config = self._camera.create_still_configuration(
                    main={
                        "size": (self.config.width, self.config.height),
                        "format": self.config.format
                    }
                )
                self._camera.configure(cam_config)
                self._camera.start()
                print(f"[PiCameraSource] 카메라 시작: {self.config.width}x{self.config.height}")
            except Exception as e:
                print(f"[PiCameraSource] 카메라 초기화 실패: {e}")
                self._camera = None
        else:
            print("[PiCameraSource] Mock 모드: 더미 이미지 반환")
        
        self._is_running = True
    
    def stop(self) -> None:
        """카메라 정지"""
        if not self._is_running:
            return
        
        if self._camera and HAS_PICAMERA:
            try:
                self._camera.stop()
                self._camera.close()
            except Exception as e:
                print(f"[PiCameraSource] 카메라 정지 오류: {e}")
        
        self._camera = None
        self._is_running = False
        print("[PiCameraSource] 카메라 정지")
    
    def capture(self) -> Optional[NDArray[np.uint8]]:
        """
        단일 프레임 캡처
        
        Returns:
            캡처된 이미지 (RGB numpy array) 또는 None
        """
        if not self._is_running:
            print("[PiCameraSource] 카메라가 시작되지 않았습니다.")
            return None
        
        # 실제 카메라가 있으면 캡처
        if self._camera and HAS_PICAMERA:
            try:
                frame = self._camera.capture_array()
                return frame
            except Exception as e:
                print(f"[PiCameraSource] 캡처 실패: {e}")
                return None
        
        # Mock 모드: 더미 이미지 생성
        dummy_frame = np.zeros(
            (self.config.height, self.config.width, 3),
            dtype=np.uint8
        )
        # 테스트용으로 랜덤 노이즈 추가
        dummy_frame[:] = np.random.randint(0, 50, (self.config.height, self.config.width, 3), dtype=np.uint8)
        return dummy_frame
    
    @property
    def is_running(self) -> bool:
        """카메라 동작 상태"""
        return self._is_running
    
    @property
    def has_camera(self) -> bool:
        """실제 카메라 존재 여부"""
        return HAS_PICAMERA and self._camera is not None
    
    def __enter__(self) -> "PiCameraSource":
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
