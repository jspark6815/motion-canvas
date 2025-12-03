"""
디스플레이 UI 모듈
터치 디스플레이에 이미지와 UI를 표시합니다.
"""
import cv2
import numpy as np
from typing import Optional, Callable, Dict
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import os


class DisplayMode(Enum):
    """디스플레이 모드"""
    LIVE_CAMERA = "live_camera"
    GENERATED_IMAGE = "generated_image"
    SILHOUETTE = "silhouette"
    MIXED = "mixed"


class Display:
    """터치 디스플레이 UI 클래스"""
    
    def __init__(self, width: int = 800, height: int = 480, fullscreen: bool = True):
        """
        Args:
            width: 디스플레이 너비
            height: 디스플레이 높이
            fullscreen: 전체화면 모드 여부
        """
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.window_name = "Interactive AI Canvas"
        self.current_mode = DisplayMode.LIVE_CAMERA
        self.generated_image: Optional[np.ndarray] = None
        self.silhouette: Optional[np.ndarray] = None
        
        # 터치 이벤트 콜백
        self.touch_callbacks: Dict[str, Callable] = {}
        
        # 한글 폰트 로드
        self.font = self._load_font()
        self.font_small = self._load_font(size=20)
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        if fullscreen:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow(self.window_name, width, height)
    
    def _load_font(self, size: int = 30) -> Optional[ImageFont.FreeTypeFont]:
        """한글 폰트 로드"""
        font_paths = [
            # 라즈베리파이 일반적인 한글 폰트 경로
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.otf",
            # macOS 경로 (개발용)
            "/System/Library/Fonts/AppleGothic.ttf",
            "/Library/Fonts/AppleGothic.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    print(f"폰트 로드 실패 ({font_path}): {e}")
                    continue
        
        # 폰트를 찾지 못한 경우 기본 폰트 사용
        print("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
        try:
            return ImageFont.load_default()
        except:
            return None
    
    def set_mode(self, mode: DisplayMode):
        """디스플레이 모드 설정"""
        self.current_mode = mode
    
    def update_generated_image(self, image: np.ndarray):
        """생성된 이미지 업데이트"""
        self.generated_image = image.copy()
    
    def update_silhouette(self, silhouette: np.ndarray):
        """실루엣 업데이트"""
        self.silhouette = silhouette.copy()
    
    def render(self, camera_frame: np.ndarray):
        """
        현재 모드에 따라 화면을 렌더링합니다.
        
        Args:
            camera_frame: 카메라 프레임
        """
        display_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if self.current_mode == DisplayMode.LIVE_CAMERA:
            display_frame = self._resize_to_fit(camera_frame, self.width, self.height)
            
        elif self.current_mode == DisplayMode.GENERATED_IMAGE:
            if self.generated_image is not None:
                display_frame = self._resize_to_fit(self.generated_image, self.width, self.height)
            else:
                display_frame = self._resize_to_fit(camera_frame, self.width, self.height)
                self._draw_text(display_frame, "이미지 생성 중...", (50, 50))
                
        elif self.current_mode == DisplayMode.SILHOUETTE:
            if self.silhouette is not None:
                display_frame = self._resize_to_fit(self.silhouette, self.width, self.height)
            else:
                display_frame = self._resize_to_fit(camera_frame, self.width, self.height)
                
        elif self.current_mode == DisplayMode.MIXED:
            if self.generated_image is not None and self.silhouette is not None:
                # 생성된 이미지와 실루엣을 블렌딩
                gen_resized = self._resize_to_fit(self.generated_image, self.width, self.height)
                sil_resized = self._resize_to_fit(self.silhouette, self.width, self.height)
                display_frame = cv2.addWeighted(gen_resized, 0.7, sil_resized, 0.3, 0)
            elif self.generated_image is not None:
                display_frame = self._resize_to_fit(self.generated_image, self.width, self.height)
            else:
                display_frame = self._resize_to_fit(camera_frame, self.width, self.height)
        
        # UI 오버레이 (모드 표시, 터치 영역 등)
        self._draw_ui_overlay(display_frame)
        
        cv2.imshow(self.window_name, display_frame)
    
    def _resize_to_fit(self, image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """이미지를 화면 크기에 맞게 리사이즈 (비율 유지)"""
        h, w = image.shape[:2]
        scale = min(target_width / w, target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h))
        
        # 중앙 정렬
        result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        y_offset = (target_height - new_h) // 2
        x_offset = (target_width - new_w) // 2
        result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return result
    
    def _draw_text(self, frame: np.ndarray, text: str, position: tuple, 
                   font_scale: float = 1.0, color: tuple = (255, 255, 255), 
                   use_korean: bool = True):
        """
        텍스트 그리기 (한글 지원)
        
        Args:
            frame: OpenCV 이미지 프레임
            text: 표시할 텍스트
            position: (x, y) 위치
            font_scale: 폰트 크기 스케일
            color: 텍스트 색상 (B, G, R)
            use_korean: 한글 폰트 사용 여부
        """
        # 한글이 포함되어 있고 폰트가 있으면 PIL 사용
        if use_korean and self.font and any('\uAC00' <= char <= '\uD7A3' for char in text):
            # PIL을 사용하여 한글 텍스트 렌더링
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            
            # 폰트 크기 조정
            font = self.font
            if font_scale < 0.8:
                font = self.font_small
            
            # PIL은 RGB 색상 사용
            rgb_color = (color[2], color[1], color[0])
            
            draw.text(position, text, font=font, fill=rgb_color)
            
            # 다시 OpenCV 형식으로 변환
            frame[:] = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        else:
            # 영문만 있거나 폰트가 없으면 OpenCV 기본 함수 사용
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, color, 2, cv2.LINE_AA)
    
    def _draw_ui_overlay(self, frame: np.ndarray):
        """UI 오버레이 그리기 (모드 표시, 터치 영역 등)"""
        # 모드 표시
        mode_names = {
            DisplayMode.LIVE_CAMERA: "실시간 카메라",
            DisplayMode.GENERATED_IMAGE: "생성된 이미지",
            DisplayMode.SILHOUETTE: "실루엣",
            DisplayMode.MIXED: "혼합 모드"
        }
        mode_text = f"모드: {mode_names.get(self.current_mode, self.current_mode.value)}"
        self._draw_text(frame, mode_text, (10, 30), 0.6, (255, 255, 255))
        
        # 터치 영역 표시 (모서리)
        touch_area_size = 80
        cv2.rectangle(frame, (0, 0), (touch_area_size, touch_area_size), (255, 255, 255), 2)
        self._draw_text(frame, "모드", (10, 50), 0.5, (255, 255, 255))
    
    def handle_touch(self, x: int, y: int):
        """터치 이벤트 처리"""
        # 모서리 터치 영역 (모드 전환)
        touch_area_size = 80
        if x < touch_area_size and y < touch_area_size:
            self._cycle_mode()
    
    def _cycle_mode(self):
        """모드를 순환 전환"""
        modes = list(DisplayMode)
        current_index = modes.index(self.current_mode)
        next_index = (current_index + 1) % len(modes)
        self.current_mode = modes[next_index]
    
    def cleanup(self):
        """리소스 정리"""
        cv2.destroyAllWindows()

