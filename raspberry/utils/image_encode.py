"""
이미지 인코딩 유틸리티
numpy 배열을 JPEG/PNG 바이트로 변환합니다.
"""
from typing import Optional
from datetime import datetime
import io
import uuid
import numpy as np
from numpy.typing import NDArray

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def encode_jpeg(
    frame: NDArray[np.uint8],
    quality: int = 85
) -> Optional[bytes]:
    """
    numpy 배열을 JPEG 바이트로 인코딩
    
    Args:
        frame: BGR 이미지 (numpy array, Picamera2 RGB888 출력은 실제로 BGR 순서)
        quality: JPEG 품질 (1-100)
        
    Returns:
        JPEG 인코딩된 바이트 또는 None
    """
    try:
        # OpenCV를 우선 사용 (스트림과 동일한 방식으로 인코딩)
        if HAS_CV2:
            # cv2.imencode는 BGR 입력을 기대하며, Picamera2 출력도 BGR 순서
            success, encoded = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            if success:
                return encoded.tobytes()
        
        if HAS_PIL:
            # PIL은 RGB를 기대하므로 BGR → RGB 변환 필요
            rgb_frame = frame[:, :, ::-1]  # BGR → RGB
            image = Image.fromarray(rgb_frame)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=quality)
            return buffer.getvalue()
        
        print("[ImageEncode] PIL 또는 OpenCV가 필요합니다.")
        return None
        
    except Exception as e:
        print(f"[ImageEncode] JPEG 인코딩 실패: {e}")
        return None


def encode_png(frame: NDArray[np.uint8]) -> Optional[bytes]:
    """
    numpy 배열을 PNG 바이트로 인코딩
    
    Args:
        frame: BGR 이미지 (numpy array, Picamera2 RGB888 출력은 실제로 BGR 순서)
        
    Returns:
        PNG 인코딩된 바이트 또는 None
    """
    try:
        # OpenCV를 우선 사용 (스트림과 동일한 방식으로 인코딩)
        if HAS_CV2:
            success, encoded = cv2.imencode(".png", frame)
            if success:
                return encoded.tobytes()
        
        if HAS_PIL:
            # PIL은 RGB를 기대하므로 BGR → RGB 변환 필요
            rgb_frame = frame[:, :, ::-1]  # BGR → RGB
            image = Image.fromarray(rgb_frame)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()
        
        print("[ImageEncode] PIL 또는 OpenCV가 필요합니다.")
        return None
        
    except Exception as e:
        print(f"[ImageEncode] PNG 인코딩 실패: {e}")
        return None


def generate_filename(prefix: str = "capture", extension: str = "jpg") -> str:
    """
    타임스탬프 기반 파일명 생성
    
    Args:
        prefix: 파일명 접두사
        extension: 파일 확장자
        
    Returns:
        생성된 파일명 (예: capture_20240101_120000_abc123.jpg)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    
    return f"{prefix}_{timestamp}_{short_uuid}.{extension}"
