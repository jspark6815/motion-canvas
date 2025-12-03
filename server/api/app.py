"""
FastAPI 서버 애플리케이션
이미지 분석 및 생성 API를 제공합니다.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from analyze import get_analyzer
from generate import get_generator

app = FastAPI(title="Interactive AI Canvas API")

# CORS 설정 (라즈베리파이에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """이미지 분석 요청 모델"""
    image: str  # base64 인코딩된 이미지
    format: str = "jpg"


class GenerateRequest(BaseModel):
    """이미지 생성 요청 모델"""
    keywords: List[str]
    style: str = "artistic"
    width: int = 512
    height: int = 512


class AnalyzeResponse(BaseModel):
    """이미지 분석 응답 모델"""
    keywords: List[str]
    analysis: dict


class GenerateResponse(BaseModel):
    """이미지 생성 응답 모델"""
    image: str  # base64 인코딩된 이미지
    prompt: str


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok", "message": "Interactive AI Canvas API is running"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_image(request: AnalyzeRequest):
    """
    이미지를 분석하고 키워드를 추출합니다.
    
    Args:
        request: 분석 요청 (base64 인코딩된 이미지 포함)
        
    Returns:
        추출된 키워드와 분석 결과
    """
    try:
        analyzer = get_analyzer()
        result = analyzer.analyze_image(request.image)
        
        return AnalyzeResponse(
            keywords=result['keywords'],
            analysis=result['analysis']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 분석 실패: {str(e)}")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest):
    """
    키워드를 기반으로 이미지를 생성합니다.
    
    Args:
        request: 생성 요청 (키워드 리스트 포함)
        
    Returns:
        생성된 이미지 (base64 인코딩)
    """
    try:
        generator = get_generator()
        prompt = generator.keywords_to_prompt(request.keywords, request.style)
        
        image = generator.generate_image(
            keywords=request.keywords,
            style=request.style,
            width=request.width,
            height=request.height
        )
        
        if image is None:
            raise HTTPException(status_code=500, detail="이미지 생성 실패")
        
        image_base64 = generator.image_to_base64(image)
        
        return GenerateResponse(
            image=image_base64,
            prompt=prompt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

