"""
사람 감지 모듈
OpenCV를 사용하여 이미지에서 사람을 감지합니다.
"""
from typing import Optional, List, Tuple
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("[PersonDetector] OpenCV가 설치되지 않았습니다. Mock 모드로 동작합니다.")

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
    """OpenCV 기반 사람 감지기"""
    
    def __init__(self, config: DetectionConfig = detection_config) -> None:
        self.config = config
        self._detector: Optional[cv2.HOGDescriptor] = None
        self._is_initialized: bool = False
    
    def initialize(self) -> None:
        """OpenCV 감지기 초기화"""
        if self._is_initialized:
            return
        
        if not HAS_CV2:
            print("[PersonDetector] OpenCV가 설치되지 않았습니다. Mock 모드로 동작합니다.")
            self._is_initialized = True
            return
        
        try:
            # OpenCV HOG (Histogram of Oriented Gradients) 사람 감지기 사용
            # HOG는 사람 감지에 효과적인 알고리즘입니다
            self._detector = cv2.HOGDescriptor()
            self._detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            self._is_initialized = True
            print("[PersonDetector] OpenCV HOG 감지기 초기화 완료")
        except Exception as e:
            print(f"[PersonDetector] 초기화 실패: {e}. Mock 모드로 동작합니다.")
            self._is_initialized = True  # Mock 모드로 계속 진행
    
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
        
        if not HAS_CV2 or not self._detector:
            # Mock 모드 (OpenCV가 없거나 초기화 실패 시)
            h, w = frame.shape[:2]
            dummy_bbox = BoundingBox(
                x=w // 4,
                y=h // 4,
                width=w // 2,
                height=h // 2,
                confidence=0.95
            )
            return [dummy_bbox]
        
        try:
            # OpenCV는 BGR 형식을 사용하므로 변환 필요
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # RGB -> BGR 변환
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                bgr_frame = frame
            
            # 사람 감지
            # winStride: 윈도우 스트라이드 (작을수록 느리지만 정확)
            # padding: 패딩
            # scale: 이미지 스케일 (1.05는 적당한 속도와 정확도 균형)
            # hitThreshold: 기본값 사용
            # finalThreshold: 최소 감지 임계값 (낮을수록 더 많이 감지)
            # 일부 OpenCV 버전에서는 finalThreshold 키워드가 지원되지 않으므로
            # 최소한의 인자만 사용합니다.
            (rects, weights) = self._detector.detectMultiScale(
                bgr_frame,
                winStride=(4, 4),
                padding=(8, 8),
                scale=1.05,
            )
            
            detections = []
            h, w = frame.shape[:2]
            
            for i, (x, y, width, height) in enumerate(rects):
                # weights는 감지 신뢰도 (높을수록 확실함)
                # 일부 버전에서 weights가 튜플/리스트가 아닐 수 있으니 방어적으로 처리
                confidence = float(weights[i]) if (isinstance(weights, (list, tuple)) and i < len(weights)) else 0.5
                
                # 신뢰도 필터링
                if confidence < self.config.min_detection_confidence:
                    continue
                
                # 여유 공간 추가 (20%)
                padding_x = int(width * 0.2)
                padding_y = int(height * 0.2)
                
                bbox = BoundingBox(
                    x=max(0, x - padding_x),
                    y=max(0, y - padding_y),
                    width=min(w, width + 2 * padding_x),
                    height=min(h, height + 2 * padding_y),
                    confidence=min(1.0, confidence)
                )
                detections.append(bbox)
            
            if detections:
                print(f"[PersonDetector] {len(detections)}명 감지됨 (평균 신뢰도: {sum(d.confidence for d in detections) / len(detections):.2f})")
            
            return detections
            
        except Exception as e:
            print(f"[PersonDetector] 감지 오류: {e}")
            # 오류 시 Mock 결과 반환
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
        self._detector = None
        self._is_initialized = False
        print("[PersonDetector] 리소스 해제")
    
    def __enter__(self) -> "PersonDetector":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

