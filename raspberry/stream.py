"""
간단한 MJPEG 스트림 서버 (라즈베리파이 전용)
- Picamera2로 프레임을 캡처해 /stream.mjpg 엔드포인트로 송출합니다.
- 카메라 리소스를 점유하므로 main.py와 동시에 실행하지 않는 것을 권장합니다.
"""
import asyncio
import os
from aiohttp import web
from picamera2 import Picamera2
import cv2

# 환경변수로 해상도 설정
WIDTH = int(os.getenv("STREAM_WIDTH", "640"))
HEIGHT = int(os.getenv("STREAM_HEIGHT", "480"))
FPS = int(os.getenv("STREAM_FPS", "15"))
PORT = int(os.getenv("STREAM_PORT", "8080"))
HOST = os.getenv("STREAM_HOST", "0.0.0.0")


async def mjpeg_handler(request):
    boundary = "frame"
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": f"multipart/x-mixed-replace; boundary=--{boundary}",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    await response.prepare(request)

    try:
        while True:
            frame = request.app["picam2"].capture_array()
            # RGB -> BGR 후 JPEG 인코딩
            ret, jpg = cv2.imencode(
                ".jpg",
                cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                [int(cv2.IMWRITE_JPEG_QUALITY), 80],
            )
            if not ret:
                continue

            data = jpg.tobytes()
            await response.write(
                b"--" + boundary.encode() + b"\r\n"
                + b"Content-Type: image/jpeg\r\n"
                + f"Content-Length: {len(data)}\r\n\r\n".encode()
                + data + b"\r\n"
            )
            await asyncio.sleep(1 / FPS)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[stream] error: {e}")
    finally:
        await response.write_eof()
    return response


async def on_startup(app):
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "RGB888"},
        buffer_count=2,
    )
    picam2.configure(config)
    picam2.start()
    app["picam2"] = picam2
    print(f"[stream] started at http://{HOST}:{PORT}/stream.mjpg ({WIDTH}x{HEIGHT}@{FPS}fps)")


async def on_cleanup(app):
    picam2 = app.get("picam2")
    if picam2:
        picam2.stop()
        picam2.close()
        print("[stream] camera stopped")


def main():
    app = web.Application()
    app.router.add_get("/stream.mjpg", mjpeg_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()

