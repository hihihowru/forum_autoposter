"""
簡單的排程管理 API 路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from schedule_service import schedule_service, ScheduleTask

logger = logging.getLogger(__name__)

router = APIRouter(tags=["schedule"])

class CreateScheduleRequest(BaseModel):
    session_id: int
    post_ids: List[str]
    schedule_type: str  # 'immediate', '24hour_batch', '5min_batch'
    interval_seconds: int = 30
    batch_duration_hours: Optional[int] = None
    # 來源追蹤參數
    source_type: Optional[str] = None  # 'batch_history' | 'self_learning'
    source_batch_id: Optional[str] = None
    source_experiment_id: Optional[str] = None
    source_feature_name: Optional[str] = None
    created_by: str = 'system'

class ScheduleResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    message: Optional[str] = None

class ScheduleStatusResponse(BaseModel):
    success: bool
    status: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class ScheduleListResponse(BaseModel):
    success: bool
    tasks: List[Dict[str, Any]] = []
    message: Optional[str] = None

@router.get("/test")
async def test_schedule():
    """測試排程服務"""
    return {"message": "排程服務正常運行", "status": "ok"}

@router.post("/create", response_model=ScheduleResponse)
async def create_schedule_task(request: CreateScheduleRequest):
    """創建排程任務"""
    try:
        task_id = await schedule_service.create_schedule_task(
            session_id=request.session_id,
            post_ids=request.post_ids,
            schedule_type=request.schedule_type,
            interval_seconds=request.interval_seconds,
            batch_duration_hours=request.batch_duration_hours,
            # 來源追蹤參數
            source_type=request.source_type,
            source_batch_id=request.source_batch_id,
            source_experiment_id=request.source_experiment_id,
            source_feature_name=request.source_feature_name,
            created_by=request.created_by
        )
        
        return ScheduleResponse(
            success=True,
            task_id=task_id,
            message="排程任務創建成功"
        )
        
    except Exception as e:
        logger.error(f"創建排程任務失敗: {e}")
        return ScheduleResponse(
            success=False,
            message=f"創建排程任務失敗: {str(e)}"
        )

@router.post("/start/{task_id}", response_model=ScheduleResponse)
async def start_schedule_task(task_id: str, background_tasks: BackgroundTasks):
    """啟動排程任務"""
    try:
        success = await schedule_service.start_schedule_task(task_id)
        
        if success:
            return ScheduleResponse(
                success=True,
                task_id=task_id,
                message="排程任務啟動成功"
            )
        else:
            return ScheduleResponse(
                success=False,
                message="啟動排程任務失敗"
            )
            
    except Exception as e:
        logger.error(f"啟動排程任務失敗: {e}")
        return ScheduleResponse(
            success=False,
            message=f"啟動排程任務失敗: {str(e)}"
        )

@router.get("/status/{task_id}", response_model=ScheduleStatusResponse)
async def get_schedule_status(task_id: str):
    """獲取排程任務狀態"""
    try:
        status = schedule_service.get_task_status(task_id)
        
        if status:
            return ScheduleStatusResponse(
                success=True,
                status=status,
                message="獲取狀態成功"
            )
        else:
            return ScheduleStatusResponse(
                success=False,
                message="任務不存在"
            )
            
    except Exception as e:
        logger.error(f"獲取排程狀態失敗: {e}")
        return ScheduleStatusResponse(
            success=False,
            message=f"獲取排程狀態失敗: {str(e)}"
        )

@router.get("/list", response_model=ScheduleListResponse)
async def get_schedule_list():
    """獲取排程任務列表"""
    try:
        tasks = await schedule_service.get_all_tasks()
        
        return ScheduleListResponse(
            success=True,
            tasks=tasks,
            message="獲取排程列表成功"
        )
        
    except Exception as e:
        logger.error(f"獲取排程列表失敗: {e}")
        return ScheduleListResponse(
            success=False,
            message=f"獲取排程列表失敗: {str(e)}"
        )

@router.get("/tasks", response_model=ScheduleListResponse)
async def get_schedule_tasks():
    """獲取排程任務列表 (前端兼容端點)"""
    return await get_schedule_list()

@router.get("/daily-stats")
async def get_daily_stats():
    """獲取每日統計數據"""
    try:
        # 獲取所有任務
        tasks = await schedule_service.get_all_tasks()
        
        # 計算統計數據
        total_tasks = len(tasks)
        active_tasks = len([t for t in tasks if t.get('status') == 'active'])
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        failed_tasks = len([t for t in tasks if t.get('status') == 'failed'])
        
        # 按來源分類
        manual_tasks = len([t for t in tasks if t.get('source') == 'manual'])
        self_learning_tasks = len([t for t in tasks if t.get('source') == 'self_learning'])
        
        return {
            "success": True,
            "data": {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "manual_tasks": manual_tasks,
                "self_learning_tasks": self_learning_tasks,
                "success_rate": total_tasks > 0 and round((completed_tasks / total_tasks) * 100, 2) or 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取每日統計失敗: {e}")
        return {
            "success": False,
            "data": {
                "total_tasks": 0,
                "active_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "manual_tasks": 0,
                "self_learning_tasks": 0,
                "success_rate": 0
            },
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/cancel/{task_id}", response_model=ScheduleResponse)
async def cancel_schedule_task(task_id: str):
    """取消排程任務"""
    try:
        success = schedule_service.cancel_task(task_id)
        
        if success:
            return ScheduleResponse(
                success=True,
                task_id=task_id,
                message="排程任務已取消"
            )
        else:
            return ScheduleResponse(
                success=False,
                message="取消排程任務失敗"
            )
            
    except Exception as e:
        logger.error(f"取消排程任務失敗: {e}")
        return ScheduleResponse(
            success=False,
            message=f"取消排程任務失敗: {str(e)}"
        )

@router.post("/execute/{task_id}", response_model=ScheduleResponse)
async def execute_schedule_now(task_id: str):
    """立即執行排程任務（測試用）"""
    try:
        logger.info(f"🚀 收到立即執行請求 - Task ID: {task_id}")
        
        # 調用排程服務的立即執行方法
        success = await schedule_service.execute_task_immediately(task_id)
        
        if success:
            return ScheduleResponse(
                success=True,
                task_id=task_id,
                message="排程任務已觸發執行"
            )
        else:
            return ScheduleResponse(
                success=False,
                message="排程任務執行失敗"
            )
            
    except Exception as e:
        logger.error(f"立即執行排程任務失敗: {e}")
        return ScheduleResponse(
            success=False,
            message=f"立即執行失敗: {str(e)}"
        )

@router.post("/stop-all-active", response_model=ScheduleResponse)
async def stop_all_active_tasks():
    """停止所有活躍的排程任務（緊急用途）"""
    try:
        logger.warning("🛑 收到停止所有活躍排程請求")
        
        # 獲取所有活躍的排程任務
        active_tasks = await schedule_service.db_service.get_active_schedule_tasks()
        
        stopped_count = 0
        for task in active_tasks:
            task_id = task['schedule_id']
            try:
                # 停止任務
                await schedule_service.db_service.update_schedule_status(task_id, 'pending')
                stopped_count += 1
                logger.info(f"✅ 已停止排程任務: {task_id}")
            except Exception as e:
                logger.error(f"❌ 停止排程任務失敗 {task_id}: {e}")
        
        return ScheduleResponse(
            success=True,
            message=f"已停止 {stopped_count} 個活躍排程任務"
        )
        
    except Exception as e:
        logger.error(f"停止所有活躍排程失敗: {e}")
        return ScheduleResponse(
            success=False,
            message=f"停止排程失敗: {str(e)}"
        )