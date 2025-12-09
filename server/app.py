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
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from server.routers import upload_router, analyze_router, generate_router, gallery_router, admin_router
from server.schemas import HealthResponse
from server.services.analyzer import analyzer
from server.services.generator import generator
from datetime import datetime

# 환경 변수 로드
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 생명주기 관리"""
    # 시작 시
    print("🚀 AI 미디어 아트 서버 시작 중...")
    
    # 서비스 초기화
    analyzer.initialize()
    generator.initialize()
    
    # static 디렉토리 확인 및 생성
    static_path = Path("static")
    (static_path / "uploads").mkdir(parents=True, exist_ok=True)
    (static_path / "generated").mkdir(parents=True, exist_ok=True)
    (static_path / "metadata").mkdir(parents=True, exist_ok=True)
    
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # 개발 환경에서는 모든 origin 허용
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 라우터 등록
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(generate_router)
app.include_router(gallery_router)
app.include_router(admin_router)


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

