"""
MJPEG 스트림 서버 모듈
카메라 프레임을 MJPEG로 스트리밍합니다.
"""
import asyncio
import threading
from typing import Optional

try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    print("[MJPEGStreamServer] aiohttp 미설치. pip install aiohttp 실행하세요.")

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("[MJPEGStreamServer] OpenCV 미설치. 스트림이 동작하지 않습니다.")

from raspberry.config import StreamConfig, stream_config


class MJPEGStreamServer:
    """MJPEG 스트림 서버 (백그라운드 스레드)"""
    
    def __init__(
        self, 
        camera_source,  # PiCameraSource 인스턴스
        config: StreamConfig = stream_config
    ) -> None:
        self.camera = camera_source
        self.config = config
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._runner: Optional[web.AppRunner] = None
        self._running: bool = False
    
    def start(self) -> bool:
        """백그라운드 스레드에서 스트림 서버 시작"""
        if not self.config.enabled:
            print("[MJPEGStreamServer] 스트림 비활성화됨")
            return False
        
        if not HAS_AIOHTTP:
            print("[MJPEGStreamServer] aiohttp 필요. pip install aiohttp")
            return False
        
        if not HAS_CV2:
            print("[MJPEGStreamServer] OpenCV 필요")
            return False
        
        if self._running:
            print("[MJPEGStreamServer] 이미 실행 중")
            return True
        
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        self._running = True
        print(f"[MJPEGStreamServer] 스트림 서버 시작: http://{self.config.host}:{self.config.port}/stream.mjpg")
        return True
    
    def stop(self) -> None:
        """스트림 서버 중지"""
        if not self._running:
            return
        
        self._running = False
        
        if self._loop and self._runner:
            # 이벤트 루프에서 정리 실행
            asyncio.run_coroutine_threadsafe(self._cleanup(), self._loop)
        
        if self._thread:
            self._thread.join(timeout=2)
        
        print("[MJPEGStreamServer] 스트림 서버 중지")
    
    async def _cleanup(self) -> None:
        """aiohttp 정리"""
        if self._runner:
            await self._runner.cleanup()
    
    def _run_server(self) -> None:
        """서버 실행 (스레드에서 호출)"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._start_web_server())
            self._loop.run_forever()
        except Exception as e:
            print(f"[MJPEGStreamServer] 오류: {e}")
        finally:
            self._loop.close()
    
    async def _start_web_server(self) -> None:
        """aiohttp 웹 서버 시작"""
        app = web.Application()
        app.router.add_get("/stream.mjpg", self._mjpeg_handler)
        app.router.add_get("/", self._index_handler)
        
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        
        site = web.TCPSite(self._runner, self.config.host, self.config.port)
        await site.start()
    
    async def _index_handler(self, request: web.Request) -> web.Response:
        """인덱스 페이지"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pi Camera Stream</title>
            <style>
                body {{ 
                    background: #1a1a1f; 
                    color: white; 
                    font-family: system-ui; 
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                }}
                h1 {{ color: #7b97f8; }}
                img {{ 
                    max-width: 90vw; 
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                }}
            </style>
        </head>
        <body>
            <h1>Pi Camera Stream</h1>
            <img src="/stream.mjpg" alt="Live Stream" />
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")
    
    async def _mjpeg_handler(self, request: web.Request) -> web.StreamResponse:
        """MJPEG 스트림 핸들러"""
        boundary = "frame"
        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": f"multipart/x-mixed-replace; boundary=--{boundary}",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Access-Control-Allow-Origin": "*",
            },
        )
        await response.prepare(request)
        
        frame_interval = 1.0 / self.config.fps
        
        while self._running:
            try:
                # 최신 프레임 가져오기
                frame = self.camera.get_latest_frame()
                
                if frame is None:
                    # 프레임 없으면 직접 캡처 시도
                    frame = self.camera.capture()
                
                if frame is None:
                    await asyncio.sleep(frame_interval)
                    continue
                
                # Picamera2 RGB888 → 로컬 스트림에서는 변환 없이 사용
                # (로컬 MJPEG 스트림은 RGB 그대로 인코딩해도 정상 표시됨)
                bgr_frame = frame
                
                # JPEG 인코딩
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.quality]
                ret, jpg = cv2.imencode(".jpg", bgr_frame, encode_param)
                
                if not ret:
                    await asyncio.sleep(frame_interval)
                    continue
                
                data = jpg.tobytes()
                
                # MJPEG 프레임 전송
                await response.write(
                    f"--{boundary}\r\n".encode()
                    + b"Content-Type: image/jpeg\r\n"
                    + f"Content-Length: {len(data)}\r\n\r\n".encode()
                    + data
                    + b"\r\n"
                )
                
                await asyncio.sleep(frame_interval)
                
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[MJPEGStreamServer] 스트림 오류: {e}")
                break
        
        return response

