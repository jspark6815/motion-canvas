"""
Picamera2 기반 카메라 소스 모듈
라즈베리파이 카메라 모듈3 제어를 담당합니다.
"""
from typing import Optional
import numpy as np
from numpy.typing import NDArray

# TODO: 라즈베리파이에서 실행 시 주석 해제
# from picamera2 import Picamera2

from raspberry.config import CameraConfig, camera_config


class PiCameraSource:
    """Picamera2 래퍼 클래스"""
    
    def __init__(self, config: CameraConfig = camera_config) -> None:
        self.config = config
        self._camera: Optional[object] = None
        self._is_running: bool = False
    
    def start(self) -> None:
        """카메라 초기화 및 시작"""
        if self._is_running:
            return
        
        # TODO: 라즈베리파이에서 실행 시 아래 코드 활성화
        # self._camera = Picamera2()
        # camera_config = self._camera.create_still_configuration(
        #     main={"size": (self.config.width, self.config.height), 
        #           "format": self.config.format}
        # )
        # self._camera.configure(camera_config)
        # self._camera.start()
        
        self._is_running = True
        print(f"[PiCameraSource] 카메라 시작: {self.config.width}x{self.config.height}")
    
    def stop(self) -> None:
        """카메라 정지"""
        if not self._is_running:
            return
        
        # TODO: 라즈베리파이에서 실행 시 아래 코드 활성화
        # if self._camera:
        #     self._camera.stop()
        #     self._camera.close()
        
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
        
        # TODO: 라즈베리파이에서 실행 시 아래 코드 활성화
        # frame = self._camera.capture_array()
        # return frame
        
        # 개발용 더미 이미지 생성 (640x480 검정 이미지)
        dummy_frame = np.zeros(
            (self.config.height, self.config.width, 3), 
            dtype=np.uint8
        )
        return dummy_frame
    
    @property
    def is_running(self) -> bool:
        """카메라 동작 상태"""
        return self._is_running
    
    def __enter__(self) -> "PiCameraSource":
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

