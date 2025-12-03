"""
카메라 캡처 모듈
라즈베리파이 카메라 모듈을 사용하여 이미지를 캡처합니다.
"""
import cv2
import numpy as np
from typing import Optional, Tuple


class CameraCapture:
    """라즈베리파이 카메라 캡처 클래스"""
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Args:
            camera_index: 카메라 인덱스 (기본값: 0)
            width: 캡처 이미지 너비
            height: 캡처 이미지 높이
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        
    def initialize(self) -> bool:
        """카메라 초기화"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            return True
        except Exception as e:
            print(f"카메라 초기화 실패: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """현재 프레임 캡처"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    
    def release(self):
        """카메라 리소스 해제"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def __enter__(self):
        """Context manager 진입"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.release()

