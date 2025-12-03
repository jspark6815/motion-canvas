"""
사람 감지 및 전처리 모듈
OpenCV와 MediaPipe를 사용하여 사람을 감지하고 특징을 추출합니다.
"""
import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple
import mediapipe as mp


class PersonDetector:
    """사람 감지 및 특징 추출 클래스"""
    
    def __init__(self):
        """MediaPipe 초기화"""
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 사람 감지를 위한 YOLO 또는 MediaPipe Selfie Segmentation
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1
        )
    
    def detect_person(self, frame: np.ndarray) -> Dict:
        """
        프레임에서 사람을 감지하고 특징을 추출합니다.
        
        Args:
            frame: 입력 이미지 프레임
            
        Returns:
            {
                'has_person': bool,
                'bbox': (x, y, w, h) or None,
                'silhouette': np.ndarray or None,
                'keypoints': List[Tuple] or None,
                'processed_image': np.ndarray
            }
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 포즈 감지
        pose_results = self.pose.process(rgb_frame)
        
        # 실루엣 추출
        segmentation_results = self.segmentation.process(rgb_frame)
        mask = segmentation_results.segmentation_mask
        
        has_person = False
        bbox = None
        silhouette = None
        keypoints = None
        
        # 사람이 감지되었는지 확인
        if pose_results.pose_landmarks:
            has_person = True
            
            # Bounding box 계산
            landmarks = pose_results.pose_landmarks.landmark
            xs = [lm.x for lm in landmarks]
            ys = [lm.y for lm in landmarks]
            
            x_min = int(min(xs) * frame.shape[1])
            x_max = int(max(xs) * frame.shape[1])
            y_min = int(min(ys) * frame.shape[0])
            y_max = int(max(ys) * frame.shape[0])
            
            bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
            
            # 키포인트 추출
            keypoints = [
                (int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0]))
                for lm in landmarks
            ]
        
        # 실루엣 마스크 생성 (임계값 적용)
        if mask is not None:
            mask_binary = (mask > 0.5).astype(np.uint8) * 255
            silhouette = cv2.cvtColor(mask_binary, cv2.COLOR_GRAY2BGR)
        
        # 처리된 이미지 생성 (포즈 랜드마크 그리기)
        processed_frame = frame.copy()
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                processed_frame,
                pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        
        return {
            'has_person': has_person,
            'bbox': bbox,
            'silhouette': silhouette,
            'keypoints': keypoints,
            'processed_image': processed_frame
        }
    
    def extract_person_region(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Bounding box 영역을 추출합니다.
        
        Args:
            frame: 원본 이미지
            bbox: (x, y, w, h) 형식의 bounding box
            
        Returns:
            추출된 영역 이미지
        """
        x, y, w, h = bbox
        return frame[y:y+h, x:x+w]
    
    def cleanup(self):
        """리소스 정리"""
        self.pose.close()
        self.segmentation.close()

