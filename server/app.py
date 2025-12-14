"""
FastAPI 메인 애플리케이션
AI 미디어 아트 서버 진입점입니다.
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from server.routers import upload_router, analyze_router, generate_router, gallery_router, admin_router, stream_router
from server.schemas import HealthResponse
from server.services.analyzer import analyzer
from server.services.generator import generator
from datetime import datetime

# 환경 변수 로드 (.env 경로 명시)
# 프로젝트 루트에서 실행해도 server/.env를 읽도록 절대경로 지정
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 생명주기 관리"""
    # 시작 시
    print("🚀 AI 미디어 아트 서버 시작 중...")
    
    # 서비스 초기화
    analyzer.initialize()
    generator.initialize()
    
    # AWS S3 연결 확인
    s3_bucket = os.getenv("AWS_S3_BUCKET", "미설정")
    print(f"📦 S3 버킷: {s3_bucket}")
    
    print("✅ 서버 준비 완료")
    
    yield
    
    # 종료 시
    print("👋 서버 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title="AI 미디어 아트 서버",
    description="라즈베리파이로 촬영한 이미지를 AI로 분석하고 새로운 예술 작품을 생성하는 서버",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (React 웹에서 접근 허용)
# 환경변수에서 허용할 origin 목록 가져오기
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

# 개발 환경에서는 모든 origin 허용
if os.getenv("ENV", "development") == "development":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(generate_router)
app.include_router(gallery_router)
app.include_router(admin_router)
app.include_router(stream_router)


@app.get("/", tags=["root"])
async def root() -> dict:
    """루트 엔드포인트"""
    return {
        "message": "AI 미디어 아트 서버에 오신 것을 환영합니다!",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """헬스체크 엔드포인트"""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now()
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "server.app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
