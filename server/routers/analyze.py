"""
이미지 분석 라우터
이미지에서 키워드와 설명을 추출합니다.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException

from server.schemas import AnalyzeRequest, AnalyzeResponse
from server.services.storage import storage
from server.services.analyzer import analyzer

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_image(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    이미지 분석 엔드포인트
    
    업로드된 이미지를 분석하여 키워드, 설명, 분위기 등을 추출합니다.
    
    Args:
        request: 분석 요청 (이미지 ID 포함)
        
    Returns:
        분석 결과
    """
    # 이미지 메타데이터 확인
    metadata = storage.get_metadata(request.image_id)
    if not metadata:
        raise HTTPException(
            status_code=404, 
            detail="이미지를 찾을 수 없습니다."
        )
    
    # 이미 분석된 경우 캐시된 결과 반환
    if metadata.get("analyzed"):
        return AnalyzeResponse(
            success=True,
            image_id=request.image_id,
            keywords=metadata.get("keywords", []),
            description=metadata.get("description", ""),
            mood=metadata.get("mood", ""),
            colors=metadata.get("colors", [])
        )
    
    # 이미지 경로 가져오기
    image_path = storage.get_upload_path(request.image_id)
    if not image_path:
        raise HTTPException(
            status_code=404, 
            detail="이미지 파일을 찾을 수 없습니다."
        )
    
    # 분석 수행
    result = await analyzer.analyze_image(image_path)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "분석 실패")
        )
    
    # 메타데이터 업데이트
    storage.update_metadata(request.image_id, {
        "analyzed": True,
        "analyzed_time": datetime.now().isoformat(),
        "keywords": result.get("keywords", []),
        "description": result.get("description", ""),
        "mood": result.get("mood", ""),
        "colors": result.get("colors", [])
    })
    
    return AnalyzeResponse(
        success=True,
        image_id=request.image_id,
        keywords=result.get("keywords", []),
        description=result.get("description", ""),
        mood=result.get("mood", ""),
        colors=result.get("colors", [])
    )


@router.get("/{image_id}", response_model=AnalyzeResponse)
async def get_analysis(image_id: str) -> AnalyzeResponse:
    """
    분석 결과 조회 엔드포인트
    
    Args:
        image_id: 조회할 이미지 ID
        
    Returns:
        분석 결과
    """
    metadata = storage.get_metadata(image_id)
    if not metadata:
        raise HTTPException(
            status_code=404, 
            detail="이미지를 찾을 수 없습니다."
        )
    
    if not metadata.get("analyzed"):
        raise HTTPException(
            status_code=404, 
            detail="분석 결과가 없습니다. 먼저 분석을 수행하세요."
        )
    
    return AnalyzeResponse(
        success=True,
        image_id=image_id,
        keywords=metadata.get("keywords", []),
        description=metadata.get("description", ""),
        mood=metadata.get("mood", ""),
        colors=metadata.get("colors", [])
    )

