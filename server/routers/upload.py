"""
이미지 업로드 라우터
라즈베리파이에서 업로드한 이미지를 처리합니다.
"""
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from server.schemas import UploadResponse
from server.services.storage import storage
from server.services.analyzer import analyzer
from server.services.generator import generator

router = APIRouter(prefix="", tags=["upload"])


async def process_image_pipeline(image_id: str) -> None:
    """
    이미지 분석 및 생성 파이프라인 (백그라운드 작업)
    
    Args:
        image_id: 처리할 이미지 ID
    """
    try:
        # 1. 이미지 경로 가져오기
        image_path = storage.get_upload_path(image_id)
        if not image_path:
            print(f"[Pipeline] 이미지를 찾을 수 없습니다: {image_id}")
            return
        
        # 2. 이미지 분석
        print(f"[Pipeline] 분석 시작: {image_id}")
        analysis_result = await analyzer.analyze_image(image_path)
        
        if analysis_result.get("success"):
            # 메타데이터 업데이트
            storage.update_metadata(image_id, {
                "analyzed": True,
                "analyzed_time": datetime.now().isoformat(),
                "keywords": analysis_result.get("keywords", []),
                "description": analysis_result.get("description", ""),
                "mood": analysis_result.get("mood", ""),
                "colors": analysis_result.get("colors", [])
            })
            print(f"[Pipeline] 분석 완료: {image_id}")
        else:
            print(f"[Pipeline] 분석 실패: {analysis_result.get('error')}")
            return
        
        # 3. 이미지 생성
        print(f"[Pipeline] 생성 시작: {image_id}")
        generation_result = await generator.generate_image(
            keywords=analysis_result.get("keywords", []),
            description=analysis_result.get("description", ""),
            mood=analysis_result.get("mood", ""),
            style="artistic"
        )
        
        if generation_result.get("success"):
            # 생성된 이미지 저장
            await storage.save_generated(
                image_data=generation_result["image_data"],
                image_id=image_id,
                prompt_used=generation_result.get("prompt_used", "")
            )
            print(f"[Pipeline] 생성 완료: {image_id}")
        else:
            print(f"[Pipeline] 생성 실패: {generation_result.get('error')}")
            
    except Exception as e:
        print(f"[Pipeline] 파이프라인 오류: {e}")


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> UploadResponse:
    """
    이미지 업로드 엔드포인트
    
    라즈베리파이에서 촬영한 이미지를 업로드합니다.
    업로드 후 백그라운드에서 분석 및 생성 파이프라인이 실행됩니다.
    
    Args:
        file: 업로드할 이미지 파일
        background_tasks: FastAPI 백그라운드 태스크
        
    Returns:
        업로드 결과
    """
    # 파일 타입 검증
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="이미지 파일만 업로드 가능합니다."
        )
    
    # 파일 크기 제한 (10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail="파일 크기는 10MB 이하여야 합니다."
        )
    
    # 이미지 저장
    result = await storage.save_upload(
        image_data=contents,
        original_filename=file.filename or "unknown.jpg"
    )
    
    # 백그라운드에서 분석/생성 파이프라인 실행
    background_tasks.add_task(process_image_pipeline, result["image_id"])
    
    return UploadResponse(
        success=True,
        image_id=result["image_id"],
        message="업로드 성공. 백그라운드에서 AI 처리가 진행됩니다.",
        filename=result["filename"],
        created_at=datetime.now()
    )

