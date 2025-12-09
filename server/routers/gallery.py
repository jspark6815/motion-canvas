"""
갤러리 라우터
웹에서 이미지 목록과 상세 정보를 조회합니다.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from server.schemas import GalleryResponse, GalleryItem, DetailResponse
from server.services.storage import storage

router = APIRouter(prefix="/gallery", tags=["gallery"])


@router.get("", response_model=GalleryResponse)
async def get_gallery(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    page_size: int = Query(default=20, ge=1, le=100, description="페이지당 아이템 수"),
    generated_only: bool = Query(default=False, description="생성된 이미지만 표시")
) -> GalleryResponse:
    """
    갤러리 목록 조회 엔드포인트
    
    Args:
        page: 페이지 번호
        page_size: 페이지당 아이템 수
        generated_only: 생성된 이미지만 필터링
        
    Returns:
        갤러리 응답 (이미지 목록)
    """
    # 이미지 목록 조회
    images = storage.get_all_images(
        page=page, 
        page_size=page_size, 
        generated_only=generated_only
    )
    
    # 총 개수
    total = storage.count_images(generated_only=generated_only)
    
    # GalleryItem 리스트 변환
    items = []
    for img in images:
        image_id = img.get("image_id", "")
        stored_filename = img.get("stored_filename", "")
        
        # URL 생성
        original_url = f"/static/uploads/{stored_filename}" if stored_filename else ""
        generated_url = None
        
        if img.get("generated"):
            generated_url = f"/static/generated/{image_id}_gen.png"
        
        # 썸네일 URL (현재는 원본과 동일, 추후 썸네일 생성 구현 가능)
        thumbnail_url = generated_url or original_url
        
        # 업로드 시간 파싱
        upload_time_str = img.get("upload_time", "")
        try:
            created_at = datetime.fromisoformat(upload_time_str)
        except (ValueError, TypeError):
            created_at = datetime.now()
        
        items.append(GalleryItem(
            id=image_id,
            original_url=original_url,
            generated_url=generated_url,
            thumbnail_url=thumbnail_url,
            keywords=img.get("keywords", []),
            description=img.get("description", ""),
            created_at=created_at
        ))
    
    return GalleryResponse(
        total=total,
        items=items,
        page=page,
        page_size=page_size
    )


@router.get("/{image_id}", response_model=DetailResponse)
async def get_detail(image_id: str) -> DetailResponse:
    """
    이미지 상세 정보 조회 엔드포인트
    
    Args:
        image_id: 조회할 이미지 ID
        
    Returns:
        이미지 상세 정보
    """
    metadata = storage.get_metadata(image_id)
    if not metadata:
        raise HTTPException(
            status_code=404, 
            detail="이미지를 찾을 수 없습니다."
        )
    
    stored_filename = metadata.get("stored_filename", "")
    original_url = f"/static/uploads/{stored_filename}" if stored_filename else ""
    
    generated_url = None
    if metadata.get("generated"):
        generated_url = f"/static/generated/{image_id}_gen.png"
    
    # 시간 파싱
    def parse_time(time_str: Optional[str]) -> Optional[datetime]:
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str)
        except (ValueError, TypeError):
            return None
    
    created_at = parse_time(metadata.get("upload_time")) or datetime.now()
    analyzed_at = parse_time(metadata.get("analyzed_time"))
    generated_at = parse_time(metadata.get("generated_time"))
    
    return DetailResponse(
        id=image_id,
        original_url=original_url,
        generated_url=generated_url,
        keywords=metadata.get("keywords", []),
        description=metadata.get("description", ""),
        mood=metadata.get("mood", ""),
        colors=metadata.get("colors", []),
        prompt_used=metadata.get("prompt_used"),
        created_at=created_at,
        analyzed_at=analyzed_at,
        generated_at=generated_at
    )

