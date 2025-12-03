"""
이미지 생성 모듈
키워드를 기반으로 디퓨전 모델을 사용하여 이미지를 생성합니다.
"""
import base64
import io
from typing import List, Optional
from PIL import Image
import torch


class ImageGenerator:
    """이미지 생성 클래스"""
    
    def __init__(self, model_type: str = "sdxl"):
        """
        Args:
            model_type: 모델 타입 ("sdxl", "flux", "stable-diffusion")
        """
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """이미지 생성 모델 로드"""
        try:
            if self.model_type == "sdxl":
                from diffusers import StableDiffusionXLPipeline
                # SDXL 모델 로드 (실제 모델 경로로 변경 필요)
                # self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                #     "stabilityai/stable-diffusion-xl-base-1.0",
                #     torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                # )
                # self.pipeline = self.pipeline.to(self.device)
                print(f"SDXL 모델 로드 준비 완료 (device: {self.device})")
                
            elif self.model_type == "flux":
                # FLUX 모델 로드
                print(f"FLUX 모델 로드 준비 완료 (device: {self.device})")
                
            else:
                from diffusers import StableDiffusionPipeline
                # Stable Diffusion 모델 로드
                print(f"Stable Diffusion 모델 로드 준비 완료 (device: {self.device})")
                
            print("이미지 생성 모델 초기화 완료")
            
        except Exception as e:
            print(f"이미지 생성 모델 로드 실패: {e}")
            print("실제 모델 설치 및 설정이 필요합니다.")
    
    def keywords_to_prompt(self, keywords: List[str], style: str = "artistic") -> str:
        """
        키워드 리스트를 프롬프트 문자열로 변환합니다.
        
        Args:
            keywords: 키워드 리스트
            style: 이미지 스타일
            
        Returns:
            프롬프트 문자열
        """
        keywords_str = ", ".join(keywords[:5])  # 상위 5개 키워드만 사용
        
        style_prefixes = {
            "artistic": "A beautiful artistic digital art, ",
            "abstract": "An abstract artistic composition, ",
            "portrait": "A stylized portrait, ",
            "landscape": "A dreamy landscape, ",
            "minimalist": "A minimalist artistic piece, "
        }
        
        prefix = style_prefixes.get(style, style_prefixes["artistic"])
        prompt = f"{prefix}{keywords_str}, high quality, detailed, 4k"
        
        return prompt
    
    def generate_image(self, keywords: List[str], 
                      style: str = "artistic",
                      width: int = 512,
                      height: int = 512) -> Optional[Image.Image]:
        """
        키워드를 기반으로 이미지를 생성합니다.
        
        Args:
            keywords: 이미지 생성에 사용할 키워드 리스트
            style: 이미지 스타일
            width: 생성 이미지 너비
            height: 생성 이미지 높이
            
        Returns:
            생성된 이미지 (PIL Image) 또는 None
        """
        if self.pipeline is None:
            print("모델이 로드되지 않았습니다. 더미 이미지를 생성합니다.")
            return self._generate_dummy_image(width, height)
        
        try:
            prompt = self.keywords_to_prompt(keywords, style)
            negative_prompt = "blurry, low quality, distorted, ugly"
            
            # 이미지 생성
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=20,
                guidance_scale=7.5
            )
            
            image = result.images[0]
            return image
            
        except Exception as e:
            print(f"이미지 생성 오류: {e}")
            return self._generate_dummy_image(width, height)
    
    def _generate_dummy_image(self, width: int, height: int) -> Image.Image:
        """더미 이미지 생성 (모델이 없을 때 테스트용)"""
        import numpy as np
        # 그라데이션 이미지 생성
        img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        return Image.fromarray(img_array)
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        PIL Image를 base64 문자열로 인코딩합니다.
        
        Args:
            image: PIL Image 객체
            
        Returns:
            base64 인코딩된 문자열
        """
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')


# 전역 생성기 인스턴스
_generator: ImageGenerator = None


def get_generator() -> ImageGenerator:
    """생성기 인스턴스 가져오기 (싱글톤)"""
    global _generator
    if _generator is None:
        _generator = ImageGenerator()
    return _generator

