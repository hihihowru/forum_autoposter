"""
學習服務API接口
提供RESTful API來使用學習服務
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

from .learning_orchestrator import LearningOrchestrator

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

# 創建FastAPI應用
app = FastAPI(title="智能學習服務API", version="1.0.0")

# 初始化學習協調器
learning_orchestrator = LearningOrchestrator()

# Pydantic模型
class InteractionData(BaseModel):
    content_id: str
    kol_id: str
    content_type: str
    topic_category: str
    generated_content: str
    posting_time: str
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    saves_count: int = 0
    views_count: int = 0
    comments: List[Dict[str, Any]] = []

class LearningSessionRequest(BaseModel):
    kol_id: str
    content_id: str

class BatchProcessRequest(BaseModel):
    historical_data: List[Dict[str, Any]]

class TrainingDataRequest(BaseModel):
    training_data: List[Dict[str, Any]]

# API端點
@app.post("/learning/session/start")
async def start_learning_session(request: LearningSessionRequest):
    """開始學習會話"""
    try:
        session_id = await learning_orchestrator.start_learning_session(
            request.kol_id, 
            request.content_id
        )
        return {
            "status": "success",
            "session_id": session_id,
            "message": "學習會話已開始"
        }
    except Exception as e:
        logger.error(f"開始學習會話失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/session/{session_id}/process")
async def process_interaction_data(session_id: str, interaction_data: InteractionData):
    """處理互動數據"""
    try:
        # 轉換為字典格式
        data_dict = interaction_data.dict()
        
        results = await learning_orchestrator.process_interaction_data(session_id, data_dict)
        
        return {
            "status": "success",
            "session_id": session_id,
            "results": results,
            "message": "互動數據處理完成"
        }
    except Exception as e:
        logger.error(f"處理互動數據失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/report/{kol_id}")
async def generate_learning_report(kol_id: str, days: int = 7):
    """生成學習報告"""
    try:
        report = await learning_orchestrator.generate_learning_report(kol_id, days)
        
        return {
            "status": "success",
            "report": {
                "report_id": report.report_id,
                "kol_id": report.kol_id,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "total_posts": report.total_posts,
                "avg_engagement_score": report.avg_engagement_score,
                "avg_ai_detection_score": report.avg_ai_detection_score,
                "insights": [
                    {
                        "type": insight.insight_type,
                        "description": insight.description,
                        "confidence": insight.confidence,
                        "recommendation": insight.recommended_action,
                        "expected_improvement": insight.expected_improvement
                    }
                    for insight in report.insights
                ],
                "recommendations": report.recommendations,
                "strategy_updates": report.strategy_updates,
                "generated_at": report.generated_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"生成學習報告失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/batch/process")
async def batch_process_historical_data(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """批量處理歷史數據"""
    try:
        # 在背景任務中處理，避免請求超時
        background_tasks.add_task(
            learning_orchestrator.batch_process_historical_data,
            request.historical_data
        )
        
        return {
            "status": "accepted",
            "message": "批量處理已開始，請稍後查詢結果",
            "data_count": len(request.historical_data)
        }
    except Exception as e:
        logger.error(f"批量處理失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/models/train")
async def train_models(request: TrainingDataRequest, background_tasks: BackgroundTasks):
    """訓練模型"""
    try:
        # 在背景任務中訓練，避免請求超時
        background_tasks.add_task(
            learning_orchestrator.train_models,
            request.training_data
        )
        
        return {
            "status": "accepted",
            "message": "模型訓練已開始，請稍後查詢結果",
            "training_samples": len(request.training_data)
        }
    except Exception as e:
        logger.error(f"模型訓練失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/dashboard")
async def get_learning_dashboard():
    """獲取學習儀表板"""
    try:
        dashboard = learning_orchestrator.get_learning_dashboard()
        return {
            "status": "success",
            "dashboard": dashboard
        }
    except Exception as e:
        logger.error(f"獲取儀表板失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/kol/{kol_id}/status")
async def get_kol_learning_status(kol_id: str):
    """獲取KOL學習狀態"""
    try:
        status = learning_orchestrator.get_kol_learning_status(kol_id)
        return {
            "status": "success",
            "kol_status": status
        }
    except Exception as e:
        logger.error(f"獲取KOL狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/kol/{kol_id}/strategy")
async def get_kol_strategy(kol_id: str):
    """獲取KOL策略"""
    try:
        strategy = learning_orchestrator.learning_engine.get_kol_strategy(kol_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="找不到KOL策略")
        
        return {
            "status": "success",
            "strategy": {
                "kol_id": strategy.kol_id,
                "content_type_weights": strategy.content_type_weights,
                "persona_adjustments": strategy.persona_adjustments,
                "timing_preferences": strategy.timing_preferences,
                "interaction_style": strategy.interaction_style,
                "last_updated": strategy.last_updated.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取KOL策略失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/predict/engagement")
async def predict_engagement(content_features: Dict[str, Any]):
    """預測互動潛力"""
    try:
        prediction = await learning_orchestrator.learning_engine.predict_engagement(content_features)
        return {
            "status": "success",
            "prediction": prediction,
            "message": f"預測互動潛力: {prediction:.3f}"
        }
    except Exception as e:
        logger.error(f"預測互動潛力失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/predict/ai-detection")
async def predict_ai_detection(content_features: Dict[str, Any]):
    """預測AI偵測風險"""
    try:
        prediction = await learning_orchestrator.learning_engine.predict_ai_detection(content_features)
        return {
            "status": "success",
            "prediction": prediction,
            "risk_level": "high" if prediction > 0.7 else "medium" if prediction > 0.4 else "low",
            "message": f"預測AI偵測風險: {prediction:.3f}"
        }
    except Exception as e:
        logger.error(f"預測AI偵測風險失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/health")
async def health_check():
    """健康檢查"""
    try:
        dashboard = learning_orchestrator.get_learning_dashboard()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": dashboard.get("system_health", {}),
            "active_sessions": dashboard.get("active_sessions", 0)
        }
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    logger.info("智能學習服務API啟動")
    logger.info("學習協調器已初始化")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("智能學習服務API關閉")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

