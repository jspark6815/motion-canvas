"""
이미지 생성 서비스
Gemini API를 사용하여 AI 이미지를 생성합니다.
"""
import os
import io
from pathlib import Path
from typing import Dict, Any, List, Optional

# Gemini API
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# 이미지 처리
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageGenerator:
    """AI 이미지 생성기 클래스"""
    
    def __init__(self) -> None:
        self._model: Optional[object] = None
        self._imagen_model: Optional[object] = None
        self._initialized: bool = False
        self._use_api: bool = False
        self._model_name: str = os.getenv("GEMINI_VISION_MODEL", "models/gemini-1.5-flash-latest")
        self._imagen_name: str = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")
    
    def initialize(self) -> bool:
        """
        Gemini Image Generation API 초기화
        
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
            print("[Generator] google-generativeai 패키지가 설치되지 않았습니다. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
        
        try:
            genai.configure(api_key=api_key)
            
            # Gemini Pro Vision 모델 (프롬프트 개선용)
            self._model = genai.GenerativeModel(self._model_name)
            
            # Imagen 모델 사용 시도 (이미지 생성용)
            # 참고: Imagen API가 사용 가능한 경우에만 동작
            try:
                self._imagen_model = genai.ImageGenerationModel(self._imagen_name)
                print(f"[Generator] Imagen 모델 사용 가능: {self._imagen_name}")
            except Exception:
                print(f"[Generator] Imagen 모델을 사용할 수 없습니다: {self._imagen_name}. 텍스트 프롬프트만 생성합니다.")
                self._imagen_model = None
            
            self._initialized = True
            self._use_api = True
            print("[Generator] Gemini API 초기화 완료")
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
        
        Args:
            keywords: 키워드 리스트
            description: 설명
            mood: 분위기
            style: 스타일 지정
            
        Returns:
            생성된 프롬프트
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
        
        # 영어 프롬프트 (이미지 생성 AI는 영어에 최적화)
        prompt = f"""Create an artistic interpretation of a human silhouette.

Style: {style_text}
Key elements: {keywords_text}
{'Mood: ' + mood if mood else ''}
{'Context: ' + description if description else ''}

Requirements:
- Abstract representation of human form
- Creative and unique artistic interpretation
- High quality digital art
- Harmonious color palette
- Professional composition
- Suitable for gallery display"""
        
        return prompt.strip()
    
    async def enhance_prompt_with_gemini(
        self, 
        base_prompt: str
    ) -> str:
        """
        Gemini를 사용하여 프롬프트 개선
        
        Args:
            base_prompt: 기본 프롬프트
            
        Returns:
            개선된 프롬프트
        """
        if not self._model or not self._use_api:
            return base_prompt
        
        try:
            enhancement_prompt = f"""
다음 이미지 생성 프롬프트를 더 예술적이고 상세하게 개선해주세요.
영어로 응답해주세요. 프롬프트만 반환하세요.

원본 프롬프트:
{base_prompt}

개선된 프롬프트:"""
            
            response = self._model.generate_content(enhancement_prompt)
            enhanced = response.text.strip()
            
            print(f"[Generator] 프롬프트 개선 완료")
            return enhanced
            
        except Exception as e:
            print(f"[Generator] 프롬프트 개선 실패: {e}")
            return base_prompt
    
    async def generate_image(
        self, 
        keywords: List[str],
        description: str = "",
        mood: str = "",
        style: str = "artistic",
        prompt_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI 이미지 생성
        
        Args:
            keywords: 키워드 리스트
            description: 설명
            mood: 분위기
            style: 스타일
            prompt_override: 사용자 지정 프롬프트 (지정 시 자동 생성 무시)
            
        Returns:
            생성 결과 딕셔너리 (이미지 바이트 포함)
        """
        if not self._initialized:
            self.initialize()
        
        # 프롬프트 생성
        if prompt_override:
            prompt = prompt_override
        else:
            prompt = self.build_prompt(keywords, description, mood, style)
        
        # Gemini로 프롬프트 개선 (선택적)
        if self._use_api and self._model and not prompt_override:
            prompt = await self.enhance_prompt_with_gemini(prompt)
        
        # Imagen API 사용 가능 여부 확인
        if self._use_api and self._imagen_model:
            return await self._generate_with_imagen(prompt, mood)
        else:
            return self._generate_mock(prompt, keywords, mood)
    
    async def _generate_with_imagen(
        self, 
        prompt: str,
        mood: str = ""
    ) -> Dict[str, Any]:
        """
        Imagen API를 사용한 실제 이미지 생성
        
        Args:
            prompt: 생성 프롬프트
            mood: 분위기
            
        Returns:
            생성 결과
        """
        try:
            result = self._imagen_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_only_high"
            )
            
            if result.images:
                # PIL Image를 바이트로 변환
                pil_image = result.images[0]._pil_image
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                
                print("[Generator] Imagen으로 이미지 생성 완료")
                return {
                    "success": True,
                    "image_data": buffer.getvalue(),
                    "prompt_used": prompt
                }
            else:
                print("[Generator] Imagen 생성 결과 없음, Mock으로 대체")
                return self._generate_mock(prompt, [], mood)
                
        except Exception as e:
            print(f"[Generator] Imagen API 오류: {e}")
            # API 오류 시 Mock으로 대체
            return self._generate_mock(prompt, [], mood)
    
    def _generate_mock(
        self, 
        prompt: str, 
        keywords: List[str],
        mood: str
    ) -> Dict[str, Any]:
        """
        Mock 이미지 생성 (개발/테스트용)
        예술적인 추상 이미지를 생성합니다.
        
        Args:
            prompt: 사용된 프롬프트
            keywords: 키워드 리스트
            mood: 분위기
            
        Returns:
            Mock 생성 결과
        """
        if not HAS_PIL:
            return {
                "success": False,
                "error": "PIL 라이브러리가 필요합니다."
            }
        
        import random
        import math
        
        # 분위기별 색상 팔레트 정의
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
        
        # 배경 그라데이션 효과
        for y in range(height):
            ratio = y / height
            r = int(palette[0][0] * (1 - ratio) + palette[1][0] * ratio)
            g = int(palette[0][1] * (1 - ratio) + palette[1][1] * ratio)
            b = int(palette[0][2] * (1 - ratio) + palette[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 추상적인 원형 레이어 추가
        for _ in range(random.randint(8, 15)):
            color = random.choice(palette[1:])
            alpha_color = (*color, random.randint(50, 150))
            
            # 투명도가 있는 레이어용 이미지
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            cx = random.randint(width // 4, 3 * width // 4)
            cy = random.randint(height // 4, 3 * height // 4)
            radius = random.randint(30, 150)
            
            overlay_draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=alpha_color
            )
            
            # 블러 효과
            overlay = overlay.filter(ImageFilter.GaussianBlur(radius=random.randint(10, 30)))
            
            # 합성
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        # 중앙에 사람 실루엣 형태 (추상적)
        silhouette_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        sil_draw = ImageDraw.Draw(silhouette_layer)
        
        # 실루엣 색상 (어두운 톤)
        sil_color = (20, 20, 30, 200)
        
        cx, cy = width // 2, height // 2
        
        # 머리 (원)
        head_y = cy - 100
        sil_draw.ellipse([cx-35, head_y-40, cx+35, head_y+40], fill=sil_color)
        
        # 몸통 (타원)
        body_y = cy + 20
        sil_draw.ellipse([cx-50, body_y-80, cx+50, body_y+80], fill=sil_color)
        
        # 다리 (두 개의 타원)
        leg_y = cy + 140
        sil_draw.ellipse([cx-40, leg_y-60, cx-5, leg_y+60], fill=sil_color)
        sil_draw.ellipse([cx+5, leg_y-60, cx+40, leg_y+60], fill=sil_color)
        
        # 블러 효과 적용
        silhouette_layer = silhouette_layer.filter(ImageFilter.GaussianBlur(radius=8))
        
        # 실루엣 합성
        img = Image.alpha_composite(img.convert('RGBA'), silhouette_layer)
        
        # 빛 효과 추가
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
        
        # RGB로 변환
        img = img.convert('RGB')
        
        # 텍스트 추가 (하단 서명)
        try:
            font = ImageFont.load_default()
            signature = "AI Generated Art"
            draw = ImageDraw.Draw(img)
            draw.text(
                (width - 120, height - 25), 
                signature, 
                fill=(255, 255, 255, 128), 
                font=font
            )
        except Exception:
            pass
        
        # 바이트로 변환
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
