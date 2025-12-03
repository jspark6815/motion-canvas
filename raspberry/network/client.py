"""
네트워크 클라이언트 모듈
서버와의 통신을 담당합니다.
"""
import requests
import base64
import cv2
import numpy as np
from typing import Optional, Dict
import io


class ServerClient:
    """서버와 통신하는 클라이언트 클래스"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Args:
            server_url: 서버 URL (기본값: http://localhost:8000)
        """
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
    
    def encode_image(self, image: np.ndarray) -> str:
        """
        OpenCV 이미지를 base64 문자열로 인코딩합니다.
        
        Args:
            image: OpenCV 이미지 (BGR 형식)
            
        Returns:
            base64 인코딩된 문자열
        """
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def send_image_for_analysis(self, image: np.ndarray) -> Optional[Dict]:
        """
        이미지를 서버로 전송하여 분석을 요청합니다.
        
        Args:
            image: 분석할 이미지
            
        Returns:
            {
                'keywords': List[str],
                'analysis': Dict
            } 또는 None
        """
        try:
            image_base64 = self.encode_image(image)
            
            response = self.session.post(
                f"{self.server_url}/api/analyze",
                json={
                    'image': image_base64,
                    'format': 'jpg'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"분석 요청 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"이미지 분석 요청 중 오류: {e}")
            return None
    
    def request_image_generation(self, keywords: list, style: str = "artistic") -> Optional[np.ndarray]:
        """
        키워드를 기반으로 이미지 생성을 요청합니다.
        
        Args:
            keywords: 이미지 생성에 사용할 키워드 리스트
            style: 이미지 스타일 (기본값: "artistic")
            
        Returns:
            생성된 이미지 (OpenCV 형식) 또는 None
        """
        try:
            response = self.session.post(
                f"{self.server_url}/api/generate",
                json={
                    'keywords': keywords,
                    'style': style
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                image_base64 = result.get('image')
                
                if image_base64:
                    # base64 디코딩
                    image_bytes = base64.b64decode(image_base64)
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    return image
            
            print(f"이미지 생성 요청 실패: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"이미지 생성 요청 중 오류: {e}")
            return None
    
    def health_check(self) -> bool:
        """서버 연결 상태 확인"""
        try:
            response = self.session.get(
                f"{self.server_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"서버 연결 확인 실패: {e}")
            return False

