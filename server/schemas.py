"""
Pydantic 스키마 정의
API 요청/응답 모델을 관리합니다.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """이미지 업로드 응답"""
    success: bool
    image_id: str
    message: str
    filename: str
    created_at: datetime


class AnalyzeRequest(BaseModel):
    """이미지 분석 요청"""
    image_id: str


class AnalyzeResponse(BaseModel):
    """이미지 분석 응답"""
    success: bool
    image_id: str
    keywords: List[str] = Field(default_factory=list)
    description: str = ""
    mood: str = ""
    colors: List[str] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    """이미지 생성 요청"""
    image_id: str
    keywords: Optional[List[str]] = None
    style: str = "artistic"
    prompt_override: Optional[str] = None


class GenerateResponse(BaseModel):
    """이미지 생성 응답"""
    success: bool
    image_id: str
    generated_image_id: str
    generated_url: str
    prompt_used: str
    created_at: datetime


class ImageMetadata(BaseModel):
    """이미지 메타데이터"""
    image_id: str
    original_filename: str
    upload_time: datetime
    analyzed: bool = False
    keywords: List[str] = Field(default_factory=list)
    description: str = ""
    generated: bool = False
    generated_image_path: Optional[str] = None


class GalleryItem(BaseModel):
    """갤러리 아이템"""
    id: str
    original_url: str
    generated_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    description: str = ""
    created_at: datetime


class GalleryResponse(BaseModel):
    """갤러리 응답"""
    total: int
    items: List[GalleryItem]
    page: int = 1
    page_size: int = 20


class DetailResponse(BaseModel):
    """상세 정보 응답"""
    id: str
    original_url: str
    generated_url: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    description: str = ""
    mood: str = ""
    colors: List[str] = Field(default_factory=list)
    prompt_used: Optional[str] = None
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: datetime

