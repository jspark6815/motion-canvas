"""
사람 감지 모듈
MediaPipe를 사용하여 이미지에서 사람을 감지합니다.
"""
from typing import Optional, List, Tuple
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

# TODO: 라즈베리파이에서 실행 시 주석 해제
# import mediapipe as mp

from raspberry.config import DetectionConfig, detection_config


@dataclass
class BoundingBox:
    """사람 감지 바운딩 박스"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    
    @property
    def x2(self) -> int:
        return self.x + self.width
    
    @property
    def y2(self) -> int:
        return self.y + self.height
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """(x, y, width, height) 튜플 반환"""
        return (self.x, self.y, self.width, self.height)


class PersonDetector:
    """MediaPipe 기반 사람 감지기"""
    
    def __init__(self, config: DetectionConfig = detection_config) -> None:
        self.config = config
        self._detector: Optional[object] = None
        self._is_initialized: bool = False
    
    def initialize(self) -> None:
        """MediaPipe 감지기 초기화"""
        if self._is_initialized:
            return
        
        # TODO: 라즈베리파이에서 실행 시 아래 코드 활성화
        # self._mp_pose = mp.solutions.pose
        # self._detector = self._mp_pose.Pose(
        #     static_image_mode=False,
        #     min_detection_confidence=self.config.min_detection_confidence,
        #     min_tracking_confidence=self.config.min_tracking_confidence
        # )
        
        self._is_initialized = True
        print("[PersonDetector] 초기화 완료")
    
    def detect(self, frame: NDArray[np.uint8]) -> List[BoundingBox]:
        """
        프레임에서 사람 감지
        
        Args:
            frame: RGB 이미지 (numpy array)
            
        Returns:
            감지된 사람들의 바운딩 박스 리스트
        """
        if not self._is_initialized:
            print("[PersonDetector] 감지기가 초기화되지 않았습니다.")
            return []
        
        # TODO: 라즈베리파이에서 실행 시 아래 코드 활성화
        # results = self._detector.process(frame)
        # 
        # if not results.pose_landmarks:
        #     return []
        # 
        # # 랜드마크에서 바운딩 박스 계산
        # h, w = frame.shape[:2]
        # landmarks = results.pose_landmarks.landmark
        # 
        # xs = [lm.x * w for lm in landmarks if lm.visibility > 0.5]
        # ys = [lm.y * h for lm in landmarks if lm.visibility > 0.5]
        # 
        # if not xs or not ys:
        #     return []
        # 
        # x_min, x_max = int(min(xs)), int(max(xs))
        # y_min, y_max = int(min(ys)), int(max(ys))
        # 
        # # 여유 공간 추가 (20%)
        # padding_x = int((x_max - x_min) * 0.2)
        # padding_y = int((y_max - y_min) * 0.2)
        # 
        # bbox = BoundingBox(
        #     x=max(0, x_min - padding_x),
        #     y=max(0, y_min - padding_y),
        #     width=min(w, x_max - x_min + 2 * padding_x),
        #     height=min(h, y_max - y_min + 2 * padding_y),
        #     confidence=0.9
        # )
        # return [bbox]
        
        # 개발용 더미 감지 결과
        h, w = frame.shape[:2]
        dummy_bbox = BoundingBox(
            x=w // 4,
            y=h // 4,
            width=w // 2,
            height=h // 2,
            confidence=0.95
        )
        return [dummy_bbox]
    
    def has_person(self, frame: NDArray[np.uint8]) -> bool:
        """
        프레임에 사람이 있는지 확인
        
        Args:
            frame: RGB 이미지
            
        Returns:
            사람 감지 여부
        """
        detections = self.detect(frame)
        return len(detections) > 0
    
    def release(self) -> None:
        """리소스 해제"""
        # TODO: 라즈베리파이에서 실행 시 아래 코드 활성화
        # if self._detector:
        #     self._detector.close()
        
        self._detector = None
        self._is_initialized = False
        print("[PersonDetector] 리소스 해제")
    
    def __enter__(self) -> "PersonDetector":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

