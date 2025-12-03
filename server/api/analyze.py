"""
CLIP 기반 이미지 분석 및 키워드 추출 모듈
"""
import base64
import io
import numpy as np
from PIL import Image
from typing import List, Dict
import torch
import clip


class ImageAnalyzer:
    """CLIP을 사용한 이미지 분석 클래스"""
    
    def __init__(self, model_name: str = "ViT-B/32"):
        """
        Args:
            model_name: CLIP 모델 이름 (기본값: "ViT-B/32")
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.model = None
        self.preprocess = None
        self._load_model()
    
    def _load_model(self):
        """CLIP 모델 로드"""
        try:
            self.model, self.preprocess = clip.load(self.model_name, device=self.device)
            self.model.eval()
            print(f"CLIP 모델 로드 완료: {self.model_name} (device: {self.device})")
        except Exception as e:
            print(f"CLIP 모델 로드 실패: {e}")
            raise
    
    def decode_image(self, image_base64: str) -> Image.Image:
        """
        base64 문자열을 PIL Image로 디코딩합니다.
        
        Args:
            image_base64: base64 인코딩된 이미지 문자열
            
        Returns:
            PIL Image 객체
        """
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        return image.convert('RGB')
    
    def extract_keywords(self, image: Image.Image, 
                        candidate_keywords: List[str] = None) -> List[str]:
        """
        이미지에서 키워드를 추출합니다.
        
        Args:
            image: 분석할 이미지 (PIL Image)
            candidate_keywords: 후보 키워드 리스트 (None이면 기본 키워드 사용)
            
        Returns:
            추출된 키워드 리스트
        """
        if candidate_keywords is None:
            candidate_keywords = [
                "person", "human", "portrait", "figure", "silhouette",
                "artistic", "abstract", "modern", "classic", "minimalist",
                "colorful", "monochrome", "dynamic", "static", "expressive",
                "calm", "energetic", "mysterious", "bright", "dark",
                "geometric", "organic", "flowing", "rigid", "soft",
                "bold", "subtle", "textured", "smooth", "layered"
            ]
        
        # 이미지 전처리
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # 텍스트 토큰화
        text_tokens = clip.tokenize(candidate_keywords).to(self.device)
        
        # 이미지와 텍스트 임베딩 계산
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            text_features = self.model.encode_text(text_tokens)
            
            # 코사인 유사도 계산
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            
            # 상위 키워드 선택
            values, indices = similarity[0].topk(min(5, len(candidate_keywords)))
        
        # 키워드 추출
        keywords = [candidate_keywords[idx] for idx in indices.cpu().numpy()]
        
        return keywords
    
    def analyze_image(self, image_base64: str) -> Dict:
        """
        이미지를 분석하고 키워드를 추출합니다.
        
        Args:
            image_base64: base64 인코딩된 이미지 문자열
            
        Returns:
            {
                'keywords': List[str],
                'analysis': Dict
            }
        """
        try:
            image = self.decode_image(image_base64)
            keywords = self.extract_keywords(image)
            
            return {
                'keywords': keywords,
                'analysis': {
                    'image_size': image.size,
                    'model': self.model_name
                }
            }
        except Exception as e:
            print(f"이미지 분석 오류: {e}")
            return {
                'keywords': [],
                'analysis': {'error': str(e)}
            }


# 전역 분석기 인스턴스
_analyzer: ImageAnalyzer = None


def get_analyzer() -> ImageAnalyzer:
    """분석기 인스턴스 가져오기 (싱글톤)"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ImageAnalyzer()
    return _analyzer

