"""
스트림 중계 서비스
라즈베리파이에서 WebSocket으로 받은 스트림을 클라이언트에게 MJPEG로 중계합니다.
"""
import asyncio
import time
from typing import Optional, Set
from dataclasses import dataclass
from collections import deque
import threading


@dataclass
class StreamFrame:
    """스트림 프레임 데이터"""
    data: bytes
    timestamp: float


class StreamRelay:
    """스트림 중계 서비스 (싱글톤)"""
    
    def __init__(self, max_frames: int = 30) -> None:
        self._latest_frame: Optional[bytes] = None
        self._frame_timestamp: float = 0
        self._lock = threading.Lock()
        self._clients: Set[asyncio.Queue] = set()
        self._connected_source: bool = False
        self._source_id: Optional[str] = None
        
        # 프레임 버퍼 (최근 N개 프레임 유지)
        self._frame_buffer: deque = deque(maxlen=max_frames)
    
    @property
    def is_source_connected(self) -> bool:
        """스트림 소스(라즈베리파이) 연결 상태"""
        return self._connected_source
    
    @property
    def source_id(self) -> Optional[str]:
        """연결된 소스 ID"""
        return self._source_id
    
    @property
    def client_count(self) -> int:
        """연결된 클라이언트 수"""
        return len(self._clients)
    
    def connect_source(self, source_id: str) -> bool:
        """스트림 소스 연결"""
        with self._lock:
            if self._connected_source:
                print(f"[StreamRelay] 이미 소스 연결됨: {self._source_id}")
                return False
            
            self._connected_source = True
            self._source_id = source_id
            print(f"[StreamRelay] 소스 연결: {source_id}")
            return True
    
    def disconnect_source(self, source_id: str) -> None:
        """스트림 소스 연결 해제"""
        with self._lock:
            if self._source_id == source_id:
                self._connected_source = False
                self._source_id = None
                self._latest_frame = None
                print(f"[StreamRelay] 소스 연결 해제: {source_id}")
    
    def push_frame(self, frame_data: bytes) -> None:
        """프레임 수신 (라즈베리파이 → 서버)"""
        with self._lock:
            self._latest_frame = frame_data
            self._frame_timestamp = time.time()
            
            # 버퍼에 추가
            self._frame_buffer.append(StreamFrame(
                data=frame_data,
                timestamp=self._frame_timestamp
            ))
        
        # 모든 클라이언트에게 프레임 전송
        for client_queue in list(self._clients):
            try:
                # 큐가 가득 차면 오래된 프레임 버림
                if client_queue.full():
                    try:
                        client_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                client_queue.put_nowait(frame_data)
            except Exception:
                pass
    
    def get_latest_frame(self) -> Optional[bytes]:
        """최신 프레임 조회"""
        with self._lock:
            return self._latest_frame
    
    def get_frame_age(self) -> float:
        """최신 프레임 나이 (초)"""
        if self._frame_timestamp == 0:
            return float('inf')
        return time.time() - self._frame_timestamp
    
    async def subscribe(self) -> asyncio.Queue:
        """클라이언트 구독 시작"""
        queue: asyncio.Queue = asyncio.Queue(maxsize=10)
        self._clients.add(queue)
        print(f"[StreamRelay] 클라이언트 구독 시작 (총 {len(self._clients)}명)")
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """클라이언트 구독 해제"""
        self._clients.discard(queue)
        print(f"[StreamRelay] 클라이언트 구독 해제 (총 {len(self._clients)}명)")
    
    def get_status(self) -> dict:
        """상태 정보 반환"""
        return {
            "source_connected": self._connected_source,
            "source_id": self._source_id,
            "client_count": len(self._clients),
            "frame_age_seconds": self.get_frame_age() if self._latest_frame else None,
            "has_frame": self._latest_frame is not None
        }


# 싱글톤 인스턴스
stream_relay = StreamRelay()

