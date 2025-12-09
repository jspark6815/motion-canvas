"""
이미지 인코딩 유틸리티
numpy 배열을 JPEG/PNG 바이트로 변환합니다.
"""
from typing import Optional
import io
import numpy as np
from numpy.typing import NDArray

# TODO: 라즈베리파이에서 실행 시 PIL 사용
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
        frame: RGB 이미지 (numpy array)
        quality: JPEG 품질 (1-100)
        
    Returns:
        JPEG 인코딩된 바이트 또는 None
    """
    try:
        if HAS_PIL:
            image = Image.fromarray(frame)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=quality)
            return buffer.getvalue()
        elif HAS_CV2:
            # OpenCV는 BGR 순서이므로 변환 필요
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            success, encoded = cv2.imencode(
                ".jpg", 
                bgr_frame, 
                [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            if success:
                return encoded.tobytes()
        
        print("[ImageEncode] PIL 또는 OpenCV가 필요합니다.")
        return None
        
    except Exception as e:
        print(f"[ImageEncode] JPEG 인코딩 실패: {e}")
        return None


def encode_png(frame: NDArray[np.uint8]) -> Optional[bytes]:
    """
    numpy 배열을 PNG 바이트로 인코딩
    
    Args:
        frame: RGB 이미지 (numpy array)
        
    Returns:
        PNG 인코딩된 바이트 또는 None
    """
    try:
        if HAS_PIL:
            image = Image.fromarray(frame)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()
        elif HAS_CV2:
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            success, encoded = cv2.imencode(".png", bgr_frame)
            if success:
                return encoded.tobytes()
        
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
    from datetime import datetime
    import uuid
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    
    return f"{prefix}_{timestamp}_{short_uuid}.{extension}"

