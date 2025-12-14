"""
스트림 라우터
라즈베리파이에서 WebSocket으로 스트림을 수신하고, 클라이언트에게 MJPEG로 중계합니다.
"""
import asyncio
import os
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import StreamingResponse

from server.services.stream_relay import stream_relay

router = APIRouter(prefix="/stream", tags=["stream"])

# 스트림 인증 키 (환경변수로 설정)
STREAM_SECRET = os.getenv("STREAM_SECRET", "raspberry-pi-secret")


@router.websocket("/push")
async def websocket_stream_push(
    websocket: WebSocket,
    secret: str = Query(...)
) -> None:
    """
    라즈베리파이에서 스트림을 푸시하는 WebSocket 엔드포인트
    
    라즈베리파이는 이 엔드포인트에 연결하여 JPEG 프레임을 전송합니다.
    
    Query Parameters:
        secret: 인증 키 (STREAM_SECRET 환경변수와 일치해야 함)
    """
    # 인증 확인
    if secret != STREAM_SECRET:
        await websocket.close(code=4001, reason="Invalid secret")
        return
    
    await websocket.accept()
    
    # 소스 ID 생성
    source_id = f"pi-{id(websocket)}"
    
    # 소스 연결 시도
    if not stream_relay.connect_source(source_id):
        await websocket.close(code=4002, reason="Another source already connected")
        return
    
    print(f"[Stream] 라즈베리파이 연결됨: {source_id}")
    
    try:
        while True:
            # 바이너리 데이터(JPEG) 수신
            data = await websocket.receive_bytes()
            
            if data:
                stream_relay.push_frame(data)
                
    except WebSocketDisconnect:
        print(f"[Stream] 라즈베리파이 연결 종료: {source_id}")
    except Exception as e:
        print(f"[Stream] 오류: {e}")
    finally:
        stream_relay.disconnect_source(source_id)


@router.get("/live.mjpg")
async def mjpeg_stream() -> StreamingResponse:
    """
    MJPEG 스트림 엔드포인트
    
    클라이언트(브라우저)가 이 URL로 접속하면 실시간 스트림을 볼 수 있습니다.
    
    Returns:
        MJPEG 스트림 응답
    """
    if not stream_relay.is_source_connected:
        raise HTTPException(
            status_code=503,
            detail="스트림 소스가 연결되지 않았습니다. 라즈베리파이 연결을 확인하세요."
        )
    
    async def generate():
        boundary = "frame"
        queue = await stream_relay.subscribe()
        
        try:
            while True:
                try:
                    # 프레임 대기 (타임아웃 5초)
                    frame_data = await asyncio.wait_for(
                        queue.get(),
                        timeout=5.0
                    )
                    
                    # MJPEG 프레임 생성
                    yield (
                        f"--{boundary}\r\n"
                        f"Content-Type: image/jpeg\r\n"
                        f"Content-Length: {len(frame_data)}\r\n\r\n"
                    ).encode() + frame_data + b"\r\n"
                    
                except asyncio.TimeoutError:
                    # 타임아웃 시 연결 상태 확인
                    if not stream_relay.is_source_connected:
                        break
                    continue
                    
        finally:
            stream_relay.unsubscribe(queue)
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/snapshot.jpg")
async def stream_snapshot() -> StreamingResponse:
    """
    현재 프레임 스냅샷 엔드포인트
    
    Returns:
        최신 JPEG 이미지
    """
    frame = stream_relay.get_latest_frame()
    
    if not frame:
        raise HTTPException(
            status_code=503,
            detail="스트림 프레임이 없습니다."
        )
    
    return StreamingResponse(
        iter([frame]),
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache",
        }
    )


@router.get("/status")
async def stream_status() -> dict:
    """
    스트림 상태 조회 엔드포인트
    
    Returns:
        스트림 연결 상태 정보
    """
    return stream_relay.get_status()

