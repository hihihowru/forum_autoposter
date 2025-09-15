"""
路由模組初始化
"""
from fastapi import APIRouter
from .post_routes import router as post_router
from .kol_routes import router as kol_router
from .kol_api_routes import router as kol_api_router
from .restore_post import router as restore_router
from .publish_route import router as publish_router
from .interaction_routes import router as interaction_router

# 創建主路由器
main_router = APIRouter()

# 包含子路由
main_router.include_router(post_router)
main_router.include_router(kol_router)
main_router.include_router(kol_api_router)
main_router.include_router(restore_router)
main_router.include_router(publish_router)
main_router.include_router(interaction_router)
