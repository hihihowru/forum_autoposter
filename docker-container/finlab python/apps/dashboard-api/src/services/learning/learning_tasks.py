"""
學習任務
整合到現有的Celery調度系統中
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from celery import Celery
from dotenv import load_dotenv

from .learning_orchestrator import LearningOrchestrator

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

# 創建Celery應用
app = Celery('learning_tasks')
app.config_from_object('celery_config')

# 初始化學習協調器
learning_orchestrator = LearningOrchestrator()

@app.task(bind=True, max_retries=3)
def process_interaction_learning(self, interaction_data: Dict[str, Any]):
    """
    處理互動學習任務
    
    Args:
        interaction_data: 互動數據
    """
    try:
        logger.info(f"開始處理互動學習任務: {interaction_data.get('content_id', 'unknown')}")
        
        # 開始學習會話
        session_id = await learning_orchestrator.start_learning_session(
            interaction_data.get('kol_id', ''),
            interaction_data.get('content_id', '')
        )
        
        # 處理互動數據
        results = await learning_orchestrator.process_interaction_data(session_id, interaction_data)
        
        logger.info(f"互動學習任務完成: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"互動學習任務失敗: {e}")
        # 重試機制
        if self.request.retries < self.max_retries:
            logger.info(f"重試互動學習任務，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            return {
                "status": "failed",
                "error": str(e)
            }

@app.task(bind=True, max_retries=3)
def daily_learning_report(self, kol_id: str, days: int = 1):
    """
    每日學習報告任務
    
    Args:
        kol_id: KOL ID
        days: 報告天數
    """
    try:
        logger.info(f"開始生成每日學習報告: {kol_id}")
        
        # 生成學習報告
        report = await learning_orchestrator.generate_learning_report(kol_id, days)
        
        # 檢查關鍵指標
        alerts = []
        if report.avg_ai_detection_score > 0.4:
            alerts.append({
                "type": "ai_detection_risk",
                "message": f"AI偵測風險過高: {report.avg_ai_detection_score:.3f}",
                "severity": "high"
            })
        
        if report.avg_engagement_score < 0.03:
            alerts.append({
                "type": "low_engagement",
                "message": f"互動率過低: {report.avg_engagement_score:.3f}",
                "severity": "medium"
            })
        
        logger.info(f"每日學習報告完成: {kol_id}")
        return {
            "status": "success",
            "report": {
                "report_id": report.report_id,
                "kol_id": report.kol_id,
                "total_posts": report.total_posts,
                "avg_engagement_score": report.avg_engagement_score,
                "avg_ai_detection_score": report.avg_ai_detection_score,
                "insights_count": len(report.insights),
                "alerts": alerts
            }
        }
        
    except Exception as e:
        logger.error(f"每日學習報告失敗: {e}")
        if self.request.retries < self.max_retries:
            logger.info(f"重試每日學習報告，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            return {
                "status": "failed",
                "error": str(e)
            }

@app.task(bind=True, max_retries=3)
def batch_learning_analysis(self, historical_data: List[Dict[str, Any]]):
    """
    批量學習分析任務
    
    Args:
        historical_data: 歷史數據列表
    """
    try:
        logger.info(f"開始批量學習分析，數據量: {len(historical_data)}")
        
        # 批量處理歷史數據
        results = await learning_orchestrator.batch_process_historical_data(historical_data)
        
        logger.info("批量學習分析完成")
        return {
            "status": "success",
            "processed_kols": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量學習分析失敗: {e}")
        if self.request.retries < self.max_retries:
            logger.info(f"重試批量學習分析，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            return {
                "status": "failed",
                "error": str(e)
            }

@app.task(bind=True, max_retries=3)
def train_learning_models(self, training_data: List[Dict[str, Any]]):
    """
    訓練學習模型任務
    
    Args:
        training_data: 訓練數據列表
    """
    try:
        logger.info(f"開始訓練學習模型，數據量: {len(training_data)}")
        
        # 訓練模型
        training_result = await learning_orchestrator.train_models(training_data)
        
        logger.info("學習模型訓練完成")
        return {
            "status": "success",
            "training_result": training_result
        }
        
    except Exception as e:
        logger.error(f"學習模型訓練失敗: {e}")
        if self.request.retries < self.max_retries:
            logger.info(f"重試學習模型訓練，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            return {
                "status": "failed",
                "error": str(e)
            }

@app.task
def scheduled_learning_analysis():
    """
    定時學習分析任務
    每日執行，分析所有KOL的學習狀態
    """
    try:
        logger.info("開始定時學習分析")
        
        # 獲取所有KOL列表（這裡需要根據實際系統調整）
        kol_ids = ["kol_001", "kol_002", "kol_003"]  # 從數據庫或配置獲取
        
        results = []
        for kol_id in kol_ids:
            try:
                # 生成每日學習報告
                report = await learning_orchestrator.generate_learning_report(kol_id, days=1)
                
                # 檢查是否需要警報
                alerts = []
                if report.avg_ai_detection_score > 0.4:
                    alerts.append("AI偵測風險過高")
                
                if report.avg_engagement_score < 0.03:
                    alerts.append("互動率過低")
                
                results.append({
                    "kol_id": kol_id,
                    "total_posts": report.total_posts,
                    "avg_engagement_score": report.avg_engagement_score,
                    "avg_ai_detection_score": report.avg_ai_detection_score,
                    "insights_count": len(report.insights),
                    "alerts": alerts
                })
                
            except Exception as e:
                logger.error(f"KOL {kol_id} 學習分析失敗: {e}")
                results.append({
                    "kol_id": kol_id,
                    "error": str(e)
                })
        
        logger.info("定時學習分析完成")
        return {
            "status": "success",
            "analyzed_kols": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"定時學習分析失敗: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

@app.task
def weekly_model_retraining():
    """
    每週模型重訓練任務
    使用過去一週的數據重新訓練模型
    """
    try:
        logger.info("開始每週模型重訓練")
        
        # 獲取過去一週的訓練數據（這裡需要根據實際系統調整）
        # 從數據庫或文件系統獲取歷史數據
        training_data = []  # 實際實現中需要從數據源獲取
        
        if not training_data:
            logger.warning("沒有足夠的訓練數據，跳過模型重訓練")
            return {
                "status": "skipped",
                "reason": "insufficient_training_data"
            }
        
        # 訓練模型
        training_result = await learning_orchestrator.train_models(training_data)
        
        logger.info("每週模型重訓練完成")
        return {
            "status": "success",
            "training_result": training_result
        }
        
    except Exception as e:
        logger.error(f"每週模型重訓練失敗: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

# 定時任務配置
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-learning-analysis': {
        'task': 'learning_tasks.scheduled_learning_analysis',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2點執行
    },
    'weekly-model-retraining': {
        'task': 'learning_tasks.weekly_model_retraining',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # 每週一凌晨3點執行
    },
}

app.conf.timezone = 'Asia/Taipei'

if __name__ == '__main__':
    app.start()

