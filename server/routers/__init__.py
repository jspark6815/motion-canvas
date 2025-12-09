"""라우터 모듈"""
from server.routers.upload import router as upload_router
from server.routers.analyze import router as analyze_router
from server.routers.generate import router as generate_router
from server.routers.gallery import router as gallery_router

__all__ = ["upload_router", "analyze_router", "generate_router", "gallery_router"]

