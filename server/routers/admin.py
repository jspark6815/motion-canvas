"""
관리자 라우터
관리자 로그인 및 이미지 관리 기능을 제공합니다.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from server.services.auth import (
    authenticate_admin,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from server.services.storage import storage

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


# 스키마
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class DeleteImageRequest(BaseModel):
    image_id: str


class DeleteImageResponse(BaseModel):
    success: bool
    message: str
    deleted_files: list[str]


# 의존성: 현재 관리자 확인
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """현재 로그인한 관리자 확인"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    return {"username": username}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    관리자 로그인
    
    환경변수 ADMIN_USERNAME과 ADMIN_PASSWORD로 인증합니다.
    """
    if not authenticate_admin(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me")
async def get_current_user_info(
    current_admin: dict = Depends(get_current_admin)
) -> dict:
    """현재 로그인한 관리자 정보"""
    return {
        "username": current_admin["username"],
        "is_admin": True
    }


@router.delete("/images/{image_id}", response_model=DeleteImageResponse)
async def delete_image(
    image_id: str,
    current_admin: dict = Depends(get_current_admin)
) -> DeleteImageResponse:
    """
    이미지 삭제 (관리자 전용)
    
    원본 이미지, 생성된 이미지, 메타데이터를 S3에서 모두 삭제합니다.
    """
    # S3에서 이미지 삭제
    result = storage.delete_image(image_id)
    
    if not result["success"] and "Image not found" in result.get("message", ""):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return DeleteImageResponse(
        success=result["success"],
        message=result["message"],
        deleted_files=result["deleted_keys"]
    )


@router.get("/stats")
async def get_admin_stats(
    current_admin: dict = Depends(get_current_admin)
) -> dict:
    """관리자 통계 정보"""
    total_images = storage.count_images()
    generated_images = storage.count_images(generated_only=True)
    
    return {
        "total_images": total_images,
        "generated_images": generated_images,
        "pending_images": total_images - generated_images
    }

