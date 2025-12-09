"""
이미지 세그멘테이션/크롭 모듈
감지된 사람 영역을 추출합니다.
"""
from typing import Optional
import numpy as np
from numpy.typing import NDArray

from raspberry.vision.person_detector import BoundingBox


class ImageSegmenter:
    """이미지 세그멘테이션 처리기"""
    
    def __init__(self) -> None:
        # TODO: 고급 세그멘테이션 모델 로드 (예: SAM, DeepLab)
        pass
    
    def crop_bbox(
        self, 
        frame: NDArray[np.uint8], 
        bbox: BoundingBox
    ) -> NDArray[np.uint8]:
        """
        바운딩 박스 영역 크롭
        
        Args:
            frame: 원본 이미지
            bbox: 바운딩 박스
            
        Returns:
            크롭된 이미지
        """
        h, w = frame.shape[:2]
        
        # 경계 검사
        x1 = max(0, bbox.x)
        y1 = max(0, bbox.y)
        x2 = min(w, bbox.x2)
        y2 = min(h, bbox.y2)
        
        cropped = frame[y1:y2, x1:x2].copy()
        return cropped
    
    def extract_silhouette(
        self, 
        frame: NDArray[np.uint8], 
        bbox: Optional[BoundingBox] = None
    ) -> NDArray[np.uint8]:
        """
        사람 실루엣 추출
        
        TODO: MediaPipe Selfie Segmentation 또는 
              다른 세그멘테이션 모델로 구현 예정
        
        Args:
            frame: 원본 이미지
            bbox: 선택적 바운딩 박스 (제공 시 해당 영역만 처리)
            
        Returns:
            실루엣 이미지 (배경 제거됨)
        """
        # 현재는 단순 bbox 크롭으로 대체
        if bbox:
            return self.crop_bbox(frame, bbox)
        
        # TODO: 세그멘테이션 구현
        # import mediapipe as mp
        # mp_selfie_segmentation = mp.solutions.selfie_segmentation
        # with mp_selfie_segmentation.SelfieSegmentation(
        #     model_selection=1
        # ) as segmenter:
        #     results = segmenter.process(frame)
        #     mask = results.segmentation_mask > 0.5
        #     silhouette = frame.copy()
        #     silhouette[~mask] = [255, 255, 255]  # 배경을 흰색으로
        #     return silhouette
        
        return frame.copy()
    
    def add_padding(
        self, 
        frame: NDArray[np.uint8], 
        padding: int = 20,
        color: tuple = (255, 255, 255)
    ) -> NDArray[np.uint8]:
        """
        이미지에 패딩 추가
        
        Args:
            frame: 원본 이미지
            padding: 패딩 크기 (픽셀)
            color: 패딩 색상 (RGB)
            
        Returns:
            패딩이 추가된 이미지
        """
        h, w = frame.shape[:2]
        padded = np.full(
            (h + 2 * padding, w + 2 * padding, 3),
            color,
            dtype=np.uint8
        )
        padded[padding:padding+h, padding:padding+w] = frame
        return padded

