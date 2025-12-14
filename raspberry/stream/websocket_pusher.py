"""
WebSocket 스트림 푸셔
카메라 프레임을 EC2 서버로 푸시합니다.
"""
import asyncio
import threading
import time
from typing import Optional

try:
    import websockets
    from websockets.exceptions import ConnectionClosed
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    print("[WebSocketPusher] websockets 미설치. pip install websockets")

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("[WebSocketPusher] OpenCV 미설치.")

from raspberry.config import StreamConfig, stream_config


class WebSocketStreamPusher:
    """WebSocket을 통해 EC2 서버로 스트림 푸시"""
    
    def __init__(
        self,
        camera_source,  # PiCameraSource 인스턴스
        server_url: str,  # ws://ec2-server:8000/stream/push
        secret: str,  # 인증 키
        config: StreamConfig = stream_config
    ) -> None:
        self.camera = camera_source
        self.server_url = server_url
        self.secret = secret
        self.config = config
        
        self._thread: Optional[threading.Thread] = None
        self._running: bool = False
        self._connected: bool = False
        self._reconnect_delay: float = 5.0
    
    @property
    def is_connected(self) -> bool:
        """서버 연결 상태"""
        return self._connected
    
    def start(self) -> bool:
        """백그라운드 스레드에서 푸셔 시작"""
        if not self.config.enabled:
            print("[WebSocketPusher] 스트림 비활성화됨")
            return False
        
        if not HAS_WEBSOCKETS:
            print("[WebSocketPusher] websockets 필요. pip install websockets")
            return False
        
        if not HAS_CV2:
            print("[WebSocketPusher] OpenCV 필요")
            return False
        
        if self._running:
            print("[WebSocketPusher] 이미 실행 중")
            return True
        
        self._running = True
        self._thread = threading.Thread(target=self._run_pusher, daemon=True)
        self._thread.start()
        print(f"[WebSocketPusher] 푸셔 시작: {self.server_url}")
        return True
    
    def stop(self) -> None:
        """푸셔 중지"""
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=3)
        
        print("[WebSocketPusher] 푸셔 중지")
    
    def _run_pusher(self) -> None:
        """푸셔 실행 (스레드에서 호출)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._push_loop())
        except Exception as e:
            print(f"[WebSocketPusher] 오류: {e}")
        finally:
            loop.close()
    
    async def _push_loop(self) -> None:
        """WebSocket 연결 및 푸시 루프"""
        while self._running:
            try:
                await self._connect_and_push()
            except ConnectionClosed as e:
                print(f"[WebSocketPusher] 연결 끊김: {e}")
            except Exception as e:
                print(f"[WebSocketPusher] 연결 오류: {e}")
            
            self._connected = False
            
            if self._running:
                print(f"[WebSocketPusher] {self._reconnect_delay}초 후 재연결...")
                await asyncio.sleep(self._reconnect_delay)
    
    async def _connect_and_push(self) -> None:
        """서버에 연결하고 프레임 푸시"""
        url = f"{self.server_url}?secret={self.secret}"
        
        print(f"[WebSocketPusher] 서버 연결 시도: {self.server_url}")
        
        async with websockets.connect(
            url,
            ping_interval=20,
            ping_timeout=10,
            max_size=10 * 1024 * 1024,  # 10MB
        ) as ws:
            self._connected = True
            print("[WebSocketPusher] 서버 연결 성공!")
            
            frame_interval = 1.0 / self.config.fps
            
            while self._running:
                try:
                    # 프레임 캡처
                    frame = self.camera.get_latest_frame()
                    
                    if frame is None:
                        frame = self.camera.capture()
                    
                    if frame is None:
                        await asyncio.sleep(frame_interval)
                        continue
                    
                    # RGB → BGR 변환 (Picamera2는 RGB, OpenCV는 BGR 사용)
                    if len(frame.shape) == 3 and frame.shape[2] == 3:
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # JPEG 인코딩
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.quality]
                    ret, jpg = cv2.imencode(".jpg", frame, encode_param)
                    
                    if not ret:
                        await asyncio.sleep(frame_interval)
                        continue
                    
                    # 서버로 전송
                    await ws.send(jpg.tobytes())
                    
                    await asyncio.sleep(frame_interval)
                    
                except ConnectionClosed:
                    raise
                except Exception as e:
                    print(f"[WebSocketPusher] 프레임 전송 오류: {e}")
                    await asyncio.sleep(frame_interval)

