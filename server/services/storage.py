"""
이미지 저장 서비스
파일 시스템 기반 이미지 저장 및 관리를 담당합니다.
"""
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class ImageStorage:
    """이미지 저장소 관리 클래스"""
    
    def __init__(self, base_path: str = "static") -> None:
        self.base_path = Path(base_path)
        self.uploads_path = self.base_path / "uploads"
        self.generated_path = self.base_path / "generated"
        self.metadata_path = self.base_path / "metadata"
        
        # 디렉토리 생성
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """필요한 디렉토리 생성"""
        self.uploads_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
    
    def generate_id(self) -> str:
        """고유 이미지 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}_{short_uuid}"
    
    async def save_upload(
        self, 
        image_data: bytes, 
        original_filename: str
    ) -> Dict[str, Any]:
        """
        업로드된 이미지 저장
        
        Args:
            image_data: 이미지 바이트 데이터
            original_filename: 원본 파일명
            
        Returns:
            저장 정보 딕셔너리
        """
        image_id = self.generate_id()
        extension = Path(original_filename).suffix or ".jpg"
        filename = f"{image_id}{extension}"
        
        # 이미지 파일 저장
        file_path = self.uploads_path / filename
        file_path.write_bytes(image_data)
        
        # 메타데이터 생성 및 저장
        metadata = {
            "image_id": image_id,
            "original_filename": original_filename,
            "stored_filename": filename,
            "upload_time": datetime.now().isoformat(),
            "file_size": len(image_data),
            "analyzed": False,
            "keywords": [],
            "description": "",
            "mood": "",
            "colors": [],
            "generated": False,
            "generated_image_path": None,
            "prompt_used": None
        }
        
        self._save_metadata(image_id, metadata)
        
        return {
            "image_id": image_id,
            "filename": filename,
            "path": str(file_path),
            "url": f"/static/uploads/{filename}"
        }
    
    async def save_generated(
        self, 
        image_data: bytes, 
        image_id: str,
        prompt_used: str = ""
    ) -> Dict[str, Any]:
        """
        생성된 이미지 저장
        
        Args:
            image_data: 생성된 이미지 바이트 데이터
            image_id: 원본 이미지 ID
            prompt_used: 사용된 프롬프트
            
        Returns:
            저장 정보 딕셔너리
        """
        generated_id = f"{image_id}_gen"
        filename = f"{generated_id}.png"
        
        # 이미지 파일 저장
        file_path = self.generated_path / filename
        file_path.write_bytes(image_data)
        
        # 메타데이터 업데이트
        metadata = self._load_metadata(image_id)
        if metadata:
            metadata["generated"] = True
            metadata["generated_image_path"] = str(file_path)
            metadata["generated_time"] = datetime.now().isoformat()
            metadata["prompt_used"] = prompt_used
            self._save_metadata(image_id, metadata)
        
        return {
            "generated_id": generated_id,
            "filename": filename,
            "path": str(file_path),
            "url": f"/static/generated/{filename}"
        }
    
    def _save_metadata(self, image_id: str, metadata: Dict[str, Any]) -> None:
        """메타데이터 저장"""
        metadata_file = self.metadata_path / f"{image_id}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self, image_id: str) -> Optional[Dict[str, Any]]:
        """메타데이터 로드"""
        metadata_file = self.metadata_path / f"{image_id}.json"
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
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
        """업로드된 이미지 경로 반환"""
        metadata = self._load_metadata(image_id)
        if not metadata:
            return None
        
        filename = metadata.get("stored_filename")
        if not filename:
            return None
        
        return self.uploads_path / filename
    
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
        
        for metadata_file in self.metadata_path.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
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
        for metadata_file in self.metadata_path.glob("*.json"):
            if generated_only:
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        if metadata.get("generated"):
                            count += 1
                except Exception:
                    continue
            else:
                count += 1
        return count


# 싱글톤 인스턴스
storage = ImageStorage()

