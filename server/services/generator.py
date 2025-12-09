"""
이미지 생성 서비스
Gemini API (google.genai)를 사용하여 AI 이미지를 생성합니다.
"""
import os
import io
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional

# 새로운 Gemini API
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    print("[Generator] google-genai 패키지가 설치되지 않았습니다. pip install google-genai")

# 이미지 처리
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageGenerator:
    """AI 이미지 생성기 클래스 (google.genai 클라이언트 사용)"""
    
    def __init__(self) -> None:
        self._client: Optional[genai.Client] = None
        self._initialized: bool = False
        self._use_api: bool = False
        self._model_name: str = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.0-flash-exp")
    
    def initialize(self) -> bool:
        """
        Gemini API 초기화
        
        Returns:
            초기화 성공 여부
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("[Generator] GEMINI_API_KEY가 설정되지 않았습니다. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
        
        if not HAS_GENAI:
            print("[Generator] google-genai 패키지가 설치되지 않았습니다. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
        
        try:
            self._client = genai.Client(api_key=api_key)
            self._initialized = True
            self._use_api = True
            print(f"[Generator] Gemini API 초기화 완료 (모델: {self._model_name})")
            return True
            
        except Exception as e:
            print(f"[Generator] API 초기화 실패: {e}. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
    
    def build_prompt(
        self, 
        keywords: List[str], 
        description: str = "",
        mood: str = "",
        style: str = "artistic"
    ) -> str:
        """
        이미지 생성 프롬프트 구성
        """
        style_prompts = {
            "artistic": "artistic and abstract style, fine art quality",
            "surreal": "surrealistic and dreamlike, Salvador Dali inspired",
            "minimal": "minimalist and clean, simple geometric forms",
            "expressive": "expressionist style, bold and emotional brushstrokes",
            "dreamy": "soft and ethereal, dreamy atmosphere with gentle colors"
        }
        
        style_text = style_prompts.get(style, style_prompts["artistic"])
        keywords_text = ", ".join(keywords) if keywords else "human figure"
        
        prompt = f"""Create an artistic interpretation based on this person.
Transform this into a creative artistic image with:
- Style: {style_text}
- Key elements: {keywords_text}
- Mood: {mood if mood else 'artistic'}
{f'- Context: {description}' if description else ''}

Make it abstract, creative, and suitable for gallery display.
Generate an artistic image, not text."""
        
        return prompt.strip()
    
    async def generate_image(
        self, 
        keywords: List[str],
        description: str = "",
        mood: str = "",
        style: str = "artistic",
        prompt_override: Optional[str] = None,
        source_image_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        AI 이미지 생성
        
        Args:
            keywords: 키워드 리스트
            description: 설명
            mood: 분위기
            style: 스타일
            prompt_override: 사용자 지정 프롬프트
            source_image_path: 원본 이미지 경로 (이미지 기반 생성 시)
            
        Returns:
            생성 결과 딕셔너리
        """
        if not self._initialized:
            self.initialize()
        
        # 프롬프트 생성
        if prompt_override:
            prompt = prompt_override
        else:
            prompt = self.build_prompt(keywords, description, mood, style)
        
        # API 사용 가능 여부 확인
        if self._use_api and self._client:
            return await self._generate_with_gemini(prompt, source_image_path, mood)
        else:
            return self._generate_mock(prompt, keywords, mood)
    
    async def _generate_with_gemini(
        self, 
        prompt: str,
        source_image_path: Optional[Path] = None,
        mood: str = ""
    ) -> Dict[str, Any]:
        """
        Gemini API를 사용한 이미지 생성
        """
        try:
            contents = [prompt]
            
            # 원본 이미지가 있으면 함께 전달
            if source_image_path and source_image_path.exists():
                try:
                    source_image = Image.open(source_image_path)
                    # 이미지 크기 제한 (API 제한)
                    max_size = 1024
                    if source_image.width > max_size or source_image.height > max_size:
                        source_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    contents.append(source_image)
                    print(f"[Generator] 원본 이미지 포함: {source_image_path}")
                except Exception as e:
                    print(f"[Generator] 원본 이미지 로드 실패: {e}")
            
            # Gemini API 호출 (이미지 생성 모드)
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["Text", "Image"]
                )
            )
            
            # 응답에서 이미지 추출
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # 이미지 데이터 추출
                    image_data = part.inline_data.data
                    
                    # base64 디코딩이 필요한 경우
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)
                    
                    print("[Generator] Gemini 이미지 생성 완료")
                    return {
                        "success": True,
                        "image_data": image_data,
                        "prompt_used": prompt
                    }
            
            # 이미지가 없으면 텍스트 응답 확인
            text_response = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    text_response += part.text
            
            print(f"[Generator] 이미지 생성 실패 (텍스트 응답): {text_response[:200] if text_response else 'No response'}")
            return self._generate_mock(prompt, [], mood)
                
        except Exception as e:
            print(f"[Generator] Gemini API 오류: {e}")
            return self._generate_mock(prompt, [], mood)
    
    def _generate_mock(
        self, 
        prompt: str, 
        keywords: List[str],
        mood: str
    ) -> Dict[str, Any]:
        """
        Mock 이미지 생성 (개발/테스트용)
        """
        if not HAS_PIL:
            return {
                "success": False,
                "error": "PIL 라이브러리가 필요합니다."
            }
        
        import random
        
        # 분위기별 색상 팔레트
        palettes = {
            "신비로운": [
                (30, 0, 60), (75, 0, 130), (138, 43, 226), 
                (72, 61, 139), (148, 103, 189)
            ],
            "평화로운": [
                (70, 130, 180), (135, 206, 250), (176, 224, 230), 
                (240, 248, 255), (173, 216, 230)
            ],
            "역동적인": [
                (200, 30, 30), (255, 69, 0), (255, 140, 0), 
                (255, 215, 0), (220, 80, 50)
            ],
            "몽환적인": [
                (180, 140, 180), (255, 182, 193), (221, 160, 221), 
                (230, 230, 250), (216, 191, 216)
            ],
            "강렬한": [
                (80, 0, 0), (139, 0, 0), (178, 34, 34), 
                (220, 20, 60), (150, 40, 40)
            ]
        }
        
        palette = palettes.get(mood, random.choice(list(palettes.values())))
        
        # 512x512 이미지 생성
        width, height = 512, 512
        img = Image.new('RGB', (width, height), palette[0])
        draw = ImageDraw.Draw(img)
        
        # 배경 그라데이션
        for y in range(height):
            ratio = y / height
            r = int(palette[0][0] * (1 - ratio) + palette[1][0] * ratio)
            g = int(palette[0][1] * (1 - ratio) + palette[1][1] * ratio)
            b = int(palette[0][2] * (1 - ratio) + palette[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 추상적인 원형 레이어
        for _ in range(random.randint(8, 15)):
            color = random.choice(palette[1:])
            alpha_color = (*color, random.randint(50, 150))
            
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            cx = random.randint(width // 4, 3 * width // 4)
            cy = random.randint(height // 4, 3 * height // 4)
            radius = random.randint(30, 150)
            
            overlay_draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=alpha_color
            )
            
            overlay = overlay.filter(ImageFilter.GaussianBlur(radius=random.randint(10, 30)))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        # 실루엣
        silhouette_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        sil_draw = ImageDraw.Draw(silhouette_layer)
        sil_color = (20, 20, 30, 200)
        
        cx, cy = width // 2, height // 2
        head_y = cy - 100
        sil_draw.ellipse([cx-35, head_y-40, cx+35, head_y+40], fill=sil_color)
        body_y = cy + 20
        sil_draw.ellipse([cx-50, body_y-80, cx+50, body_y+80], fill=sil_color)
        leg_y = cy + 140
        sil_draw.ellipse([cx-40, leg_y-60, cx-5, leg_y+60], fill=sil_color)
        sil_draw.ellipse([cx+5, leg_y-60, cx+40, leg_y+60], fill=sil_color)
        
        silhouette_layer = silhouette_layer.filter(ImageFilter.GaussianBlur(radius=8))
        img = Image.alpha_composite(img.convert('RGBA'), silhouette_layer)
        
        # 빛 효과
        light_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        light_draw = ImageDraw.Draw(light_layer)
        
        for _ in range(5):
            lx = random.randint(0, width)
            ly = random.randint(0, height)
            lr = random.randint(20, 50)
            light_alpha = random.randint(30, 80)
            light_draw.ellipse(
                [lx-lr, ly-lr, lx+lr, ly+lr],
                fill=(255, 255, 255, light_alpha)
            )
        
        light_layer = light_layer.filter(ImageFilter.GaussianBlur(radius=20))
        img = Image.alpha_composite(img, light_layer)
        
        img = img.convert('RGB')
        
        # 서명
        try:
            font = ImageFont.load_default()
            draw = ImageDraw.Draw(img)
            draw.text(
                (width - 120, height - 25), 
                "AI Generated Art", 
                fill=(255, 255, 255, 128), 
                font=font
            )
        except Exception:
            pass
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        
        print("[Generator] Mock 이미지 생성 완료")
        
        return {
            "success": True,
            "image_data": buffer.getvalue(),
            "prompt_used": prompt
        }


# 싱글톤 인스턴스
generator = ImageGenerator()
