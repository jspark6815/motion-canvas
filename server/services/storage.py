"""
이미지 저장 서비스 (AWS S3 기반)
S3를 사용한 이미지 저장 및 관리를 담당합니다.
"""
import os
import json
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))

import boto3
from botocore.exceptions import ClientError


class ImageStorage:
    """S3 기반 이미지 저장소 관리 클래스"""
    
    def __init__(self) -> None:
        # 환경변수에서 AWS 설정 로드
        self.bucket_name = os.getenv("AWS_S3_BUCKET", "motion-canvas-bucket")
        self.region = os.getenv("AWS_REGION", "ap-northeast-2")
        
        # S3 클라이언트 초기화
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # S3 키 접두사
        self.uploads_prefix = "uploads/"
        self.generated_prefix = "generated/"
        self.metadata_prefix = "metadata/"
    
    def _get_s3_url(self, key: str) -> str:
        """S3 객체의 공개 URL 반환"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
    
    def generate_id(self) -> str:
        """고유 이미지 ID 생성"""
        timestamp = datetime.now(KST).strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}_{short_uuid}"
    
    async def save_upload(
        self, 
        image_data: bytes, 
        original_filename: str
    ) -> Dict[str, Any]:
        """
        업로드된 이미지를 S3에 저장
        
        Args:
            image_data: 이미지 바이트 데이터
            original_filename: 원본 파일명
            
        Returns:
            저장 정보 딕셔너리
        """
        image_id = self.generate_id()
        extension = Path(original_filename).suffix or ".jpg"
        filename = f"{image_id}{extension}"
        s3_key = f"{self.uploads_prefix}{filename}"
        
        # Content-Type 결정
        content_type = "image/jpeg"
        if extension.lower() == ".png":
            content_type = "image/png"
        elif extension.lower() == ".gif":
            content_type = "image/gif"
        elif extension.lower() == ".webp":
            content_type = "image/webp"
        
        # S3에 업로드
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType=content_type
        )
        
        # 메타데이터 생성 및 저장
        metadata = {
            "image_id": image_id,
            "original_filename": original_filename,
            "stored_filename": filename,
            "s3_key": s3_key,
            "upload_time": datetime.now(KST).isoformat(),
            "file_size": len(image_data),
            "analyzed": False,
            "keywords": [],
            "description": "",
            "mood": "",
            "colors": [],
            "generated": False,
            "generated_s3_key": None,
            "prompt_used": None
        }
        
        self._save_metadata(image_id, metadata)
        
        return {
            "image_id": image_id,
            "filename": filename,
            "s3_key": s3_key,
            "url": self._get_s3_url(s3_key)
        }
    
    async def save_generated(
        self, 
        image_data: bytes, 
        image_id: str,
        prompt_used: str = ""
    ) -> Dict[str, Any]:
        """
        생성된 이미지를 S3에 저장
        
        Args:
            image_data: 생성된 이미지 바이트 데이터
            image_id: 원본 이미지 ID
            prompt_used: 사용된 프롬프트
            
        Returns:
            저장 정보 딕셔너리
        """
        generated_id = f"{image_id}_gen"
        filename = f"{generated_id}.png"
        s3_key = f"{self.generated_prefix}{filename}"
        
        # S3에 업로드
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType="image/png"
        )
        
        # 메타데이터 업데이트
        metadata = self._load_metadata(image_id)
        if metadata:
            metadata["generated"] = True
            metadata["generated_s3_key"] = s3_key
            metadata["generated_time"] = datetime.now(KST).isoformat()
            metadata["prompt_used"] = prompt_used
            self._save_metadata(image_id, metadata)
        
        return {
            "generated_id": generated_id,
            "filename": filename,
            "s3_key": s3_key,
            "url": self._get_s3_url(s3_key)
        }
    
    def _save_metadata(self, image_id: str, metadata: Dict[str, Any]) -> None:
        """메타데이터를 S3에 저장"""
        s3_key = f"{self.metadata_prefix}{image_id}.json"
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=json.dumps(metadata, ensure_ascii=False, indent=2),
            ContentType="application/json"
        )
    
    def _load_metadata(self, image_id: str) -> Optional[Dict[str, Any]]:
        """S3에서 메타데이터 로드"""
        s3_key = f"{self.metadata_prefix}{image_id}.json"
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise
    
    def update_metadata(
        self, 
        image_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """메타데이터 업데이트"""
        metadata = self._load_metadata(image_id)
        if not metadata:
            return None
        
        metadata.update(updates)
        self._save_metadata(image_id, metadata)
        return metadata
    
    def get_metadata(self, image_id: str) -> Optional[Dict[str, Any]]:
        """메타데이터 조회"""
        return self._load_metadata(image_id)
    
    def get_upload_path(self, image_id: str) -> Optional[Path]:
        """
        업로드된 이미지를 임시 파일로 다운로드하여 경로 반환
        (AI 분석을 위해 로컬 파일 경로가 필요한 경우)
        """
        metadata = self._load_metadata(image_id)
        if not metadata:
            return None
        
        s3_key = metadata.get("s3_key")
        if not s3_key:
            return None
        
        # 임시 파일로 다운로드
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # 확장자 추출
            extension = Path(s3_key).suffix or ".jpg"
            
            # 임시 파일 생성
            temp_file = tempfile.NamedTemporaryFile(
                suffix=extension,
                delete=False
            )
            temp_file.write(response["Body"].read())
            temp_file.close()
            
            return Path(temp_file.name)
        except ClientError:
            return None
    
    def get_upload_url(self, image_id: str) -> Optional[str]:
        """업로드된 이미지의 S3 URL 반환"""
        metadata = self._load_metadata(image_id)
        if not metadata:
            return None
        
        s3_key = metadata.get("s3_key")
        if not s3_key:
            return None
        
        return self._get_s3_url(s3_key)
    
    def get_generated_url(self, image_id: str) -> Optional[str]:
        """생성된 이미지의 S3 URL 반환"""
        metadata = self._load_metadata(image_id)
        if not metadata or not metadata.get("generated"):
            return None
        
        s3_key = metadata.get("generated_s3_key")
        if not s3_key:
            return None
        
        return self._get_s3_url(s3_key)
    
    def get_all_images(
        self, 
        page: int = 1, 
        page_size: int = 20,
        generated_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        모든 이미지 메타데이터 조회
        
        Args:
            page: 페이지 번호
            page_size: 페이지당 아이템 수
            generated_only: 생성된 이미지만 필터링
            
        Returns:
            이미지 메타데이터 리스트
        """
        all_metadata = []
        
        # S3에서 메타데이터 파일 목록 조회
        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self.bucket_name,
            Prefix=self.metadata_prefix
        )
        
        for page_result in pages:
            for obj in page_result.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".json"):
                    continue
                
                try:
                    response = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    metadata = json.loads(response["Body"].read().decode("utf-8"))
                    
                    if generated_only and not metadata.get("generated"):
                        continue
                    
                    all_metadata.append(metadata)
                except Exception:
                    continue
        
        # 업로드 시간 기준 정렬 (최신순)
        all_metadata.sort(
            key=lambda x: x.get("upload_time", ""), 
            reverse=True
        )
        
        # 페이지네이션
        start = (page - 1) * page_size
        end = start + page_size
        
        return all_metadata[start:end]
    
    def count_images(self, generated_only: bool = False) -> int:
        """이미지 총 개수"""
        count = 0
        
        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self.bucket_name,
            Prefix=self.metadata_prefix
        )
        
        for page_result in pages:
            for obj in page_result.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".json"):
                    continue
                
                if generated_only:
                    try:
                        response = self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=key
                        )
                        metadata = json.loads(response["Body"].read().decode("utf-8"))
                        if metadata.get("generated"):
                            count += 1
                    except Exception:
                        continue
                else:
                    count += 1
        
        return count
    
    def delete_image(self, image_id: str) -> Dict[str, Any]:
        """
        이미지 및 관련 파일 모두 삭제 (S3)
        
        Args:
            image_id: 삭제할 이미지 ID
            
        Returns:
            삭제 결과 딕셔너리
        """
        deleted_keys = []
        errors = []
        
        # 메타데이터 먼저 로드
        metadata = self._load_metadata(image_id)
        if not metadata:
            return {
                "success": False,
                "message": "Image not found",
                "deleted_keys": [],
                "errors": ["Metadata not found"]
            }
        
        # 1. 원본 이미지 삭제
        upload_key = metadata.get("s3_key")
        if upload_key:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=upload_key
                )
                deleted_keys.append(upload_key)
            except ClientError as e:
                errors.append(f"Failed to delete upload: {str(e)}")
        
        # 2. 생성된 이미지 삭제
        generated_key = metadata.get("generated_s3_key")
        if generated_key:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=generated_key
                )
                deleted_keys.append(generated_key)
            except ClientError as e:
                errors.append(f"Failed to delete generated: {str(e)}")
        
        # 3. 메타데이터 삭제
        metadata_key = f"{self.metadata_prefix}{image_id}.json"
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=metadata_key
            )
            deleted_keys.append(metadata_key)
        except ClientError as e:
            errors.append(f"Failed to delete metadata: {str(e)}")
        
        return {
            "success": len(errors) == 0,
            "message": f"Deleted {len(deleted_keys)} objects" if not errors else f"Partial deletion with {len(errors)} errors",
            "deleted_keys": deleted_keys,
            "errors": errors
        }


# 싱글톤 인스턴스
storage = ImageStorage()
