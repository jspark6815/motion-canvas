"""
이미지 분석 서비스
Gemini Vision API를 사용하여 이미지에서 키워드와 설명을 추출합니다.
"""
import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional

# Gemini API
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class ImageAnalyzer:
    """이미지 분석기 클래스"""
    
    def __init__(self) -> None:
        self._model: Optional[object] = None
        self._initialized: bool = False
        self._use_api: bool = False
        self._model_name: str = os.getenv("GEMINI_VISION_MODEL", "models/gemini-1.5-flash-latest")
    
    def initialize(self) -> bool:
        """
        Gemini Vision API 초기화
        
        Returns:
            초기화 성공 여부
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("[Analyzer] GEMINI_API_KEY가 설정되지 않았습니다. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
        
        if not HAS_GENAI:
            print("[Analyzer] google-generativeai 패키지가 설치되지 않았습니다. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
        
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self._model_name)
            self._initialized = True
            self._use_api = True
            print("[Analyzer] Gemini Vision API 초기화 완료")
            return True
        except Exception as e:
            print(f"[Analyzer] API 초기화 실패: {e}. Mock 모드로 동작합니다.")
            self._initialized = True
            self._use_api = False
            return True
    
    async def analyze_image(
        self, 
        image_path: Path
    ) -> Dict[str, Any]:
        """
        이미지 분석 수행
        
        Args:
            image_path: 분석할 이미지 경로
            
        Returns:
            분석 결과 딕셔너리
        """
        if not self._initialized:
            self.initialize()
        
        if not image_path.exists():
            return {
                "success": False,
                "error": "이미지 파일을 찾을 수 없습니다."
            }
        
        if self._use_api and self._model:
            return await self._analyze_with_gemini(image_path)
        else:
            return self._analyze_mock(image_path)
    
    async def _analyze_with_gemini(
        self, 
        image_path: Path
    ) -> Dict[str, Any]:
        """
        Gemini Vision API를 사용한 실제 분석
        
        Args:
            image_path: 이미지 경로
            
        Returns:
            분석 결과
        """
        try:
            # 이미지 로드 및 Base64 인코딩
            image_data = image_path.read_bytes()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 이미지 MIME 타입 결정
            suffix = image_path.suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(suffix, 'image/jpeg')
            
            # 분석 프롬프트
            prompt = """
이 이미지에 있는 사람을 분석해주세요.

다음 JSON 형식으로만 응답해주세요 (다른 텍스트 없이):
{
    "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
    "description": "이미지에 대한 상세 설명 (2-3문장)",
    "mood": "전체적인 분위기 (예: 평화로운, 역동적인, 신비로운, 몽환적인, 강렬한 중 하나)",
    "colors": ["주요 색상1", "주요 색상2", "주요 색상3"],
    "pose": "자세 설명",
    "suggested_art_style": "추천 예술 스타일 (예: 추상 표현주의, 미니멀리즘, 초현실주의, 인상주의 중 하나)"
}

반드시 한국어로 응답하고, 유효한 JSON 형식을 지켜주세요.
"""
            
            # Gemini API 호출
            response = self._model.generate_content([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": base64_image
                }
            ])
            
            # 응답 텍스트 정제 및 파싱
            response_text = response.text.strip()
            
            # JSON 블록 추출 (```json ... ``` 형식 처리)
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            # JSON 파싱
            result = json.loads(response_text)
            result["success"] = True
            
            print(f"[Analyzer] Gemini 분석 완료: {result.get('keywords', [])}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"[Analyzer] JSON 파싱 실패: {e}")
            print(f"[Analyzer] 응답 원문: {response_text if 'response_text' in dir() else 'N/A'}")
            # JSON 파싱 실패 시 Mock 결과 반환
            return self._analyze_mock(image_path)
            
        except Exception as e:
            print(f"[Analyzer] Gemini API 오류: {e}")
            # API 오류 시 Mock 결과 반환
            return self._analyze_mock(image_path)
    
    def _analyze_mock(self, image_path: Path) -> Dict[str, Any]:
        """
        Mock 분석 결과 반환 (개발/테스트용)
        
        Args:
            image_path: 이미지 경로
            
        Returns:
            Mock 분석 결과
        """
        import random
        
        # 다양한 Mock 데이터
        keyword_sets = [
            ["사람", "실루엣", "그림자", "존재", "형태"],
            ["인물", "포즈", "움직임", "에너지", "생명"],
            ["형상", "빛", "어둠", "대비", "균형"],
            ["신체", "표현", "감정", "순간", "포착"]
        ]
        
        moods = ["신비로운", "평화로운", "역동적인", "몽환적인", "강렬한"]
        
        color_sets = [
            ["검정", "회색", "흰색"],
            ["파랑", "보라", "검정"],
            ["따뜻한 갈색", "베이지", "흰색"],
            ["차가운 파랑", "회색", "은색"]
        ]
        
        descriptions = [
            "한 사람의 형상이 공간 속에 존재하고 있습니다. 빛과 그림자의 경계에서 인간의 본질적인 형태가 드러납니다.",
            "움직임의 순간이 포착된 인물입니다. 에너지와 생명력이 실루엣을 통해 표현되고 있습니다.",
            "정적인 포즈 속에서 내면의 감정이 느껴지는 형상입니다. 차분하면서도 깊은 존재감을 가지고 있습니다.",
            "역동적인 자세의 인물이 프레임 안에서 공간을 지배하고 있습니다. 강한 의지와 결단력이 느껴집니다."
        ]
        
        return {
            "success": True,
            "keywords": random.choice(keyword_sets),
            "description": random.choice(descriptions),
            "mood": random.choice(moods),
            "colors": random.choice(color_sets),
            "pose": "서있는 자세" if random.random() > 0.5 else "움직이는 자세",
            "suggested_art_style": random.choice([
                "추상 표현주의", "미니멀리즘", "초현실주의", "인상주의"
            ])
        }


# 싱글톤 인스턴스
analyzer = ImageAnalyzer()
