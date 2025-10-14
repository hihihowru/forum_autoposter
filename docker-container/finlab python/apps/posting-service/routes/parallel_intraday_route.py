"""
並行盤中觸發器路由 - 解決 API 塞車問題
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from parallel_processor import trigger_processor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intraday/parallel", tags=["parallel-intraday-trigger"])

@router.post("/execute-multiple")
async def execute_multiple_triggers_parallel(trigger_configs: List[Dict[str, Any]]):
    """
    並行執行多個盤中觸發器
    
    Args:
        trigger_configs: 觸發器配置列表
        
    Returns:
        執行結果列表
    """
    try:
        logger.info(f"🚀 開始並行執行 {len(trigger_configs)} 個盤中觸發器")
        
        # 定義進度回調函數
        async def progress_callback(completed: int, total: int, result: Dict[str, Any]):
            """進度回調函數"""
            percentage = round(completed / total * 100, 1)
            if result.get("success"):
                logger.info(f"✅ 進度: {completed}/{total} ({percentage}%) - 觸發器執行成功")
            else:
                logger.warning(f"⚠️ 進度: {completed}/{total} ({percentage}%) - 觸發器執行失敗: {result.get('error', 'Unknown error')}")
        
        # 並行執行所有觸發器
        results = await trigger_processor.execute_triggers_parallel(
            trigger_configs,
            progress_callback=progress_callback
        )
        
        # 統計結果
        successful_triggers = sum(1 for r in results if r.get("success"))
        failed_triggers = len(results) - successful_triggers
        
        logger.info(f"🎉 並行觸發器執行完成: 成功 {successful_triggers} 個，失敗 {failed_triggers} 個")
        
        return {
            "success": True,
            "total_triggers": len(trigger_configs),
            "successful_triggers": successful_triggers,
            "failed_triggers": failed_triggers,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 並行觸發器執行失敗: {e}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"並行觸發器執行失敗: {str(e)}")

@router.post("/execute-with-timeout")
async def execute_triggers_with_timeout(
    trigger_configs: List[Dict[str, Any]],
    timeout_seconds: int = 30,
    max_concurrent: int = 3
):
    """
    帶超時控制的並行觸發器執行
    
    Args:
        trigger_configs: 觸發器配置列表
        timeout_seconds: 總超時時間（秒）
        max_concurrent: 最大並發數
        
    Returns:
        執行結果列表
    """
    try:
        logger.info(f"🚀 開始帶超時控制的並行觸發器執行: {len(trigger_configs)} 個觸發器，超時: {timeout_seconds}秒，並發數: {max_concurrent}")
        
        # 創建帶超時控制的並行處理器
        from parallel_processor import IntradayTriggerProcessor
        timeout_processor = IntradayTriggerProcessor(
            max_concurrent=max_concurrent,
            timeout=timeout_seconds
        )
        
        # 使用 asyncio.wait_for 來控制總超時時間
        try:
            results = await asyncio.wait_for(
                timeout_processor.execute_triggers_parallel(trigger_configs),
                timeout=timeout_seconds
            )
            
            # 統計結果
            successful_triggers = sum(1 for r in results if r.get("success"))
            failed_triggers = len(results) - successful_triggers
            
            logger.info(f"🎉 帶超時控制的並行觸發器執行完成: 成功 {successful_triggers} 個，失敗 {failed_triggers} 個")
            
            return {
                "success": True,
                "total_triggers": len(trigger_configs),
                "successful_triggers": successful_triggers,
                "failed_triggers": failed_triggers,
                "results": results,
                "timeout_seconds": timeout_seconds,
                "max_concurrent": max_concurrent,
                "timestamp": datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"❌ 觸發器執行超時: {timeout_seconds}秒")
            raise HTTPException(
                status_code=408,
                detail=f"觸發器執行超時: {timeout_seconds}秒"
            )
        
    except Exception as e:
        logger.error(f"❌ 帶超時控制的並行觸發器執行失敗: {e}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"帶超時控制的並行觸發器執行失敗: {str(e)}")

@router.post("/execute-with-circuit-breaker")
async def execute_triggers_with_circuit_breaker(
    trigger_configs: List[Dict[str, Any]],
    failure_threshold: int = 3,
    recovery_timeout: int = 60
):
    """
    帶熔斷器的並行觸發器執行
    
    Args:
        trigger_configs: 觸發器配置列表
        failure_threshold: 失敗閾值
        recovery_timeout: 恢復超時時間（秒）
        
    Returns:
        執行結果列表
    """
    try:
        logger.info(f"🚀 開始帶熔斷器的並行觸發器執行: {len(trigger_configs)} 個觸發器，失敗閾值: {failure_threshold}，恢復超時: {recovery_timeout}秒")
        
        # 簡單的熔斷器實現
        class SimpleCircuitBreaker:
            def __init__(self, failure_threshold: int, recovery_timeout: int):
                self.failure_threshold = failure_threshold
                self.recovery_timeout = recovery_timeout
                self.failure_count = 0
                self.last_failure_time = None
                self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
            
            def can_execute(self) -> bool:
                if self.state == "CLOSED":
                    return True
                elif self.state == "OPEN":
                    if self.last_failure_time and (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        return True
                    return False
                else:  # HALF_OPEN
                    return True
            
            def record_success(self):
                self.failure_count = 0
                self.state = "CLOSED"
            
            def record_failure(self):
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
        
        circuit_breaker = SimpleCircuitBreaker(failure_threshold, recovery_timeout)
        
        # 檢查熔斷器狀態
        if not circuit_breaker.can_execute():
            logger.warning(f"⚠️ 熔斷器處於 OPEN 狀態，拒絕執行觸發器")
            raise HTTPException(
                status_code=503,
                detail=f"熔斷器處於 OPEN 狀態，請等待 {recovery_timeout} 秒後重試"
            )
        
        # 執行觸發器
        results = await trigger_processor.execute_triggers_parallel(trigger_configs)
        
        # 統計結果並更新熔斷器狀態
        successful_triggers = sum(1 for r in results if r.get("success"))
        failed_triggers = len(results) - successful_triggers
        
        if failed_triggers > 0:
            circuit_breaker.record_failure()
        else:
            circuit_breaker.record_success()
        
        logger.info(f"🎉 帶熔斷器的並行觸發器執行完成: 成功 {successful_triggers} 個，失敗 {failed_triggers} 個，熔斷器狀態: {circuit_breaker.state}")
        
        return {
            "success": True,
            "total_triggers": len(trigger_configs),
            "successful_triggers": successful_triggers,
            "failed_triggers": failed_triggers,
            "results": results,
            "circuit_breaker_state": circuit_breaker.state,
            "failure_threshold": failure_threshold,
            "recovery_timeout": recovery_timeout,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 帶熔斷器的並行觸發器執行失敗: {e}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"帶熔斷器的並行觸發器執行失敗: {str(e)}")

@router.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "ok",
        "service": "parallel-intraday-trigger",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stats")
async def get_parallel_stats():
    """獲取並行處理統計信息"""
    return {
        "max_concurrent": trigger_processor.max_concurrent,
        "timeout": trigger_processor.timeout,
        "max_retries": trigger_processor.max_retries,
        "timestamp": datetime.now().isoformat()
    }


