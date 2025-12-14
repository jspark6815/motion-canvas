"""
Picamera2 기반 카메라 소스 모듈
라즈베리파이 카메라 모듈3 제어를 담당합니다.
싱글톤 패턴으로 카메라 리소스를 공유합니다.
"""
from typing import Optional
import threading
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
    """Picamera2 래퍼 클래스 (싱글톤)"""
    
    _instance: Optional["PiCameraSource"] = None
    _lock = threading.Lock()
    
    def __new__(cls, config: CameraConfig = camera_config) -> "PiCameraSource":
        """싱글톤 인스턴스 생성"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config: CameraConfig = camera_config) -> None:
        if self._initialized:
            return
        self.config = config
        self._camera: Optional[Picamera2] = None
        self._is_running: bool = False
        self._latest_frame: Optional[NDArray[np.uint8]] = None
        self._frame_lock = threading.Lock()
        self._initialized = True
    
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
        
        frame = None
        
        # 실제 카메라가 있으면 캡처
        if self._camera and HAS_PICAMERA:
            try:
                frame = self._camera.capture_array()
            except Exception as e:
                print(f"[PiCameraSource] 캡처 실패: {e}")
                return None
        else:
            # Mock 모드: 더미 이미지 생성
            frame = np.zeros(
                (self.config.height, self.config.width, 3),
                dtype=np.uint8
            )
            # 테스트용으로 랜덤 노이즈 추가
            frame[:] = np.random.randint(0, 50, (self.config.height, self.config.width, 3), dtype=np.uint8)
        
        # 최신 프레임 저장 (스트림용)
        if frame is not None:
            with self._frame_lock:
                self._latest_frame = frame.copy()
        
        return frame
    
    def get_latest_frame(self) -> Optional[NDArray[np.uint8]]:
        """
        최신 프레임 조회 (스트림용, 스레드 안전)
        
        Returns:
            최신 프레임 또는 None
        """
        with self._frame_lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
            return None
    
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
