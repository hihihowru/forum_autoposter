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
from .interaction_batch_routes import router as interaction_batch_router
# from .interaction_analysis_routes import router as interaction_analysis_router
# from .kol_personalization_routes import router as kol_personalization_router
from .schedule_routes_simple import router as schedule_router
from .intraday_trigger_route import router as intraday_trigger_router
from .parallel_intraday_route import router as parallel_intraday_router

# 創建主路由器
main_router = APIRouter()

# 包含子路由
main_router.include_router(post_router)
main_router.include_router(kol_router)
main_router.include_router(kol_api_router)
main_router.include_router(restore_router)
main_router.include_router(publish_router)
main_router.include_router(interaction_router)
main_router.include_router(interaction_batch_router)
# main_router.include_router(interaction_analysis_router)
# main_router.include_router(kol_personalization_router)
main_router.include_router(schedule_router)
main_router.include_router(intraday_trigger_router)
main_router.include_router(parallel_intraday_router)
