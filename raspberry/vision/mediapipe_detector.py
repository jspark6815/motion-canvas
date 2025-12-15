"""
MediaPipe 기반 사람 감지 모듈
Pose Detection을 사용하여 더 정확한 사람 감지를 수행합니다.

MediaPipe 장점:
- 딥러닝 기반으로 HOG보다 높은 정확도
- 33개 신체 랜드마크(포즈) 감지 가능
- 실시간 처리 가능

설치: pip install mediapipe
"""
from typing import Optional, List, Tuple
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False
    print("[MediaPipeDetector] mediapipe 미설치. pip install mediapipe")

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

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


@dataclass
class PoseLandmarks:
    """포즈 랜드마크 데이터"""
    landmarks: List[Tuple[float, float, float]]  # (x, y, visibility) 리스트
    bbox: BoundingBox
    
    @property
    def nose(self) -> Optional[Tuple[float, float]]:
        """코 위치 (랜드마크 0)"""
        if len(self.landmarks) > 0:
            return (self.landmarks[0][0], self.landmarks[0][1])
        return None
    
    @property
    def left_shoulder(self) -> Optional[Tuple[float, float]]:
        """왼쪽 어깨 (랜드마크 11)"""
        if len(self.landmarks) > 11:
            return (self.landmarks[11][0], self.landmarks[11][1])
        return None
    
    @property
    def right_shoulder(self) -> Optional[Tuple[float, float]]:
        """오른쪽 어깨 (랜드마크 12)"""
        if len(self.landmarks) > 12:
            return (self.landmarks[12][0], self.landmarks[12][1])
        return None


class MediaPipeDetector:
    """MediaPipe Pose 기반 사람 감지기"""
    
    def __init__(self, config: DetectionConfig = detection_config) -> None:
        self.config = config
        self._pose: Optional[object] = None
        self._is_initialized: bool = False
    
    def initialize(self) -> bool:
        """MediaPipe Pose 초기화"""
        if self._is_initialized:
            return True
        
        if not HAS_MEDIAPIPE:
            print("[MediaPipeDetector] mediapipe 미설치. HOG 감지기로 폴백됩니다.")
            return False
        
        try:
            # MediaPipe Pose 초기화
            mp_pose = mp.solutions.pose
            self._pose = mp_pose.Pose(
                static_image_mode=False,  # 비디오 모드 (연속 프레임)
                model_complexity=1,  # 0=Lite, 1=Full, 2=Heavy
                enable_segmentation=False,  # 세그멘테이션 비활성화 (속도 향상)
                min_detection_confidence=self.config.min_detection_confidence,
                min_tracking_confidence=0.5
            )
            
            self._is_initialized = True
            print("[MediaPipeDetector] MediaPipe Pose 초기화 완료")
            return True
            
        except Exception as e:
            print(f"[MediaPipeDetector] 초기화 실패: {e}")
            return False
    
    def detect(self, frame: NDArray[np.uint8]) -> List[BoundingBox]:
        """
        프레임에서 사람 감지
        
        Args:
            frame: BGR 이미지 (numpy array)
            
        Returns:
            감지된 사람들의 바운딩 박스 리스트
        """
        if not self._is_initialized:
            if not self.initialize():
                return []
        
        if not HAS_MEDIAPIPE or not self._pose:
            return []
        
        try:
            h, w = frame.shape[:2]
            
            # MediaPipe는 RGB를 기대하므로 변환
            # (Picamera2 RGB888은 실제 BGR이므로 변환 필요)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Pose 감지 수행
            results = self._pose.process(rgb_frame)
            
            detections = []
            
            if results.pose_landmarks:
                # 랜드마크에서 바운딩 박스 계산
                landmarks = results.pose_landmarks.landmark
                
                # 모든 랜드마크의 x, y 좌표 수집
                x_coords = []
                y_coords = []
                visibilities = []
                
                for lm in landmarks:
                    if lm.visibility > 0.5:  # 가시성이 50% 이상인 랜드마크만
                        x_coords.append(lm.x * w)
                        y_coords.append(lm.y * h)
                        visibilities.append(lm.visibility)
                
                if len(x_coords) >= 5:  # 최소 5개 랜드마크가 보여야 함
                    # 바운딩 박스 계산 (여유 공간 추가)
                    padding_ratio = 0.1
                    
                    min_x = max(0, int(min(x_coords) - w * padding_ratio))
                    max_x = min(w, int(max(x_coords) + w * padding_ratio))
                    min_y = max(0, int(min(y_coords) - h * padding_ratio))
                    max_y = min(h, int(max(y_coords) + h * padding_ratio))
                    
                    # 평균 가시성을 신뢰도로 사용
                    confidence = sum(visibilities) / len(visibilities)
                    
                    if confidence >= self.config.min_detection_confidence:
                        bbox = BoundingBox(
                            x=min_x,
                            y=min_y,
                            width=max_x - min_x,
                            height=max_y - min_y,
                            confidence=confidence
                        )
                        detections.append(bbox)
                        
                        print(f"[MediaPipeDetector] 사람 감지 (신뢰도: {confidence:.2f}, 랜드마크: {len(x_coords)}개)")
            
            return detections
            
        except Exception as e:
            print(f"[MediaPipeDetector] 감지 오류: {e}")
            return []
    
    def detect_with_pose(self, frame: NDArray[np.uint8]) -> List[PoseLandmarks]:
        """
        프레임에서 사람 감지 및 포즈 랜드마크 반환
        
        Args:
            frame: BGR 이미지 (numpy array)
            
        Returns:
            감지된 사람들의 포즈 랜드마크 리스트
        """
        if not self._is_initialized:
            if not self.initialize():
                return []
        
        if not HAS_MEDIAPIPE or not self._pose:
            return []
        
        try:
            h, w = frame.shape[:2]
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self._pose.process(rgb_frame)
            
            pose_results = []
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # 랜드마크 데이터 추출
                landmark_list = []
                x_coords = []
                y_coords = []
                visibilities = []
                
                for lm in landmarks:
                    landmark_list.append((lm.x * w, lm.y * h, lm.visibility))
                    if lm.visibility > 0.5:
                        x_coords.append(lm.x * w)
                        y_coords.append(lm.y * h)
                        visibilities.append(lm.visibility)
                
                if len(x_coords) >= 5:
                    padding_ratio = 0.1
                    min_x = max(0, int(min(x_coords) - w * padding_ratio))
                    max_x = min(w, int(max(x_coords) + w * padding_ratio))
                    min_y = max(0, int(min(y_coords) - h * padding_ratio))
                    max_y = min(h, int(max(y_coords) + h * padding_ratio))
                    
                    confidence = sum(visibilities) / len(visibilities)
                    
                    bbox = BoundingBox(
                        x=min_x,
                        y=min_y,
                        width=max_x - min_x,
                        height=max_y - min_y,
                        confidence=confidence
                    )
                    
                    pose_results.append(PoseLandmarks(
                        landmarks=landmark_list,
                        bbox=bbox
                    ))
            
            return pose_results
            
        except Exception as e:
            print(f"[MediaPipeDetector] 포즈 감지 오류: {e}")
            return []
    
    def has_person(self, frame: NDArray[np.uint8]) -> bool:
        """
        프레임에 사람이 있는지 확인
        
        Args:
            frame: BGR 이미지
            
        Returns:
            사람 감지 여부
        """
        detections = self.detect(frame)
        return len(detections) > 0
    
    def release(self) -> None:
        """리소스 해제"""
        if self._pose:
            self._pose.close()
            self._pose = None
        self._is_initialized = False
        print("[MediaPipeDetector] 리소스 해제")
    
    def __enter__(self) -> "MediaPipeDetector":
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()


# 테스트
if __name__ == "__main__":
    print("🎯 MediaPipe 사람 감지 테스트")
    
    if not HAS_MEDIAPIPE:
        print("❌ mediapipe가 설치되지 않았습니다.")
        print("   pip install mediapipe")
        exit(1)
    
    # 카메라 테스트
    try:
        from raspberry.camera.picam_source import PiCameraSource
        from raspberry.config import camera_config
        
        with PiCameraSource(camera_config) as camera:
            detector = MediaPipeDetector()
            detector.initialize()
            
            print("카메라 프레임 캡처 중...")
            frame = camera.capture()
            
            if frame is not None:
                detections = detector.detect(frame)
                print(f"감지된 사람 수: {len(detections)}")
                
                for i, bbox in enumerate(detections):
                    print(f"  [{i}] 위치: ({bbox.x}, {bbox.y}), 크기: {bbox.width}x{bbox.height}, 신뢰도: {bbox.confidence:.2f}")
            
            detector.release()
            
    except Exception as e:
        print(f"테스트 오류: {e}")

