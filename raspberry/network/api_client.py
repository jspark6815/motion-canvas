"""
서버 API 클라이언트 모듈
서버와의 HTTP 통신을 담당합니다.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException

from raspberry.config import ServerConfig, server_config


@dataclass
class UploadResponse:
    """업로드 응답 데이터"""
    success: bool
    image_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class APIClient:
    """서버 API 클라이언트"""
    
    def __init__(self, config: ServerConfig = server_config) -> None:
        self.config = config
        self._session: Optional[requests.Session] = None
    
    def _get_session(self) -> requests.Session:
        """HTTP 세션 반환 (lazy initialization)"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "Accept": "application/json"
            })
        return self._session
    
    def upload_image(
        self, 
        image_bytes: bytes, 
        filename: str = "capture.jpg",
        metadata: Optional[Dict[str, Any]] = None
    ) -> UploadResponse:
        """
        이미지를 서버에 업로드
        
        Args:
            image_bytes: 인코딩된 이미지 바이트
            filename: 파일명
            metadata: 추가 메타데이터 (선택)
            
        Returns:
            UploadResponse 객체
        """
        try:
            session = self._get_session()
            
            files = {
                "file": (filename, image_bytes, "image/jpeg")
            }
            
            data = {}
            if metadata:
                data["metadata"] = str(metadata)
            
            response = session.post(
                self.config.upload_url,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return UploadResponse(
                    success=True,
                    image_id=result.get("image_id"),
                    message=result.get("message", "업로드 성공")
                )
            else:
                return UploadResponse(
                    success=False,
                    error=f"서버 오류: {response.status_code}"
                )
                
        except RequestException as e:
            return UploadResponse(
                success=False,
                error=f"네트워크 오류: {str(e)}"
            )
        except Exception as e:
            return UploadResponse(
                success=False,
                error=f"알 수 없는 오류: {str(e)}"
            )
    
    def check_health(self) -> bool:
        """
        서버 상태 확인
        
        Returns:
            서버 정상 여부
        """
        try:
            session = self._get_session()
            response = session.get(
                f"{self.config.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def close(self) -> None:
        """세션 종료"""
        if self._session:
            self._session.close()
            self._session = None
    
    def __enter__(self) -> "APIClient":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

