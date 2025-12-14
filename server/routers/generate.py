"""
이미지 생성 라우터
AI를 사용하여 새로운 이미지를 생성합니다.
"""
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException

from server.schemas import GenerateRequest, GenerateResponse
from server.services.storage import storage
from server.services.generator import generator

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest) -> GenerateResponse:
    """
    이미지 생성 엔드포인트
    
    분석 결과를 기반으로 AI 이미지를 생성합니다.
    
    Args:
        request: 생성 요청 (이미지 ID, 스타일 등)
        
    Returns:
        생성 결과
    """
    # 이미지 메타데이터 확인
    metadata = storage.get_metadata(request.image_id)
    if not metadata:
        raise HTTPException(
            status_code=404, 
            detail="이미지를 찾을 수 없습니다."
        )
    
    # 이미 생성된 경우 기존 결과 반환
    if metadata.get("generated") and metadata.get("generated_s3_key"):
        generated_id = f"{request.image_id}_gen"
        generated_url = storage.get_generated_url(request.image_id)
        return GenerateResponse(
            success=True,
            image_id=request.image_id,
            generated_image_id=generated_id,
            generated_url=generated_url or "",
            prompt_used=metadata.get("prompt_used", ""),
            created_at=datetime.fromisoformat(metadata.get("generated_time", datetime.now().isoformat()))
        )
    
    # 키워드 결정 (요청에 포함된 키워드 또는 분석된 키워드)
    keywords = request.keywords or metadata.get("keywords", [])
    if not keywords:
        raise HTTPException(
            status_code=400, 
            detail="키워드가 필요합니다. 먼저 이미지 분석을 수행하세요."
        )
    
    # 원본 이미지 경로 (S3에서 임시 다운로드)
    source_image_path = storage.get_upload_path(request.image_id)
    
    # 이미지 생성
    result = await generator.generate_image(
        keywords=keywords,
        description=metadata.get("description", ""),
        mood=metadata.get("mood", ""),
        style=request.style,
        prompt_override=request.prompt_override,
        source_image_path=source_image_path
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "이미지 생성 실패")
        )
    
    # 생성된 이미지를 S3에 저장
    save_result = await storage.save_generated(
        image_data=result["image_data"],
        image_id=request.image_id,
        prompt_used=result.get("prompt_used", "")
    )
    
    return GenerateResponse(
        success=True,
        image_id=request.image_id,
        generated_image_id=save_result["generated_id"],
        generated_url=save_result["url"],
        prompt_used=result.get("prompt_used", ""),
        created_at=datetime.now()
    )


@router.get("/{image_id}", response_model=GenerateResponse)
async def get_generated(image_id: str) -> GenerateResponse:
    """
    생성된 이미지 정보 조회 엔드포인트
    
    Args:
        image_id: 조회할 이미지 ID
        
    Returns:
        생성 결과
    """
    metadata = storage.get_metadata(image_id)
    if not metadata:
        raise HTTPException(
            status_code=404, 
            detail="이미지를 찾을 수 없습니다."
        )
    
    if not metadata.get("generated"):
        raise HTTPException(
            status_code=404, 
            detail="생성된 이미지가 없습니다. 먼저 이미지 생성을 수행하세요."
        )
    
    generated_id = f"{image_id}_gen"
    generated_url = storage.get_generated_url(image_id)
    
    return GenerateResponse(
        success=True,
        image_id=image_id,
        generated_image_id=generated_id,
        generated_url=generated_url or "",
        prompt_used=metadata.get("prompt_used", ""),
        created_at=datetime.fromisoformat(metadata.get("generated_time", datetime.now().isoformat()))
    )
