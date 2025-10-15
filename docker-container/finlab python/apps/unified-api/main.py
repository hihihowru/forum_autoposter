"""
統一的 API 服務 - 簡化版本
Railway 部署時使用此服務作為唯一的 API 入口
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Forum Autoposter Unified API",
    description="統一的 API 服務，整合所有微服務功能",
    version="1.0.0"
)

# 配置 CORS - 明確允許 Vercel 域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://forum-autoposter-dz27.vercel.app",
        "https://forum-autoposter-dz27-git-test-will-cs-projects-2b6e293d.vercel.app",
        "https://forum-autoposter-dz27-p6dtkgkw9-will-cs-projects-2b6e293d.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ==================== 健康檢查 ====================

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "Forum Autoposter Unified API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "unified-api",
        "message": "Unified API is running successfully",
        "timestamp": datetime.now().isoformat()
    }

# ==================== OHLC API 功能 ====================

@app.get("/after_hours_limit_up")
async def after_hours_limit_up(limit: int = Query(1000, description="限制返回數量")):
    """盤後漲停股票數據"""
    logger.info(f"收到 after_hours_limit_up 請求: limit={limit}")
    
    # 簡化的模擬數據
    mock_data = [
        {
            "stock_code": "2330",
            "stock_name": "台積電",
            "close_price": 580.0,
            "change_percent": 9.8,
            "volume": 15000000
        },
        {
            "stock_code": "2454",
            "stock_name": "聯發科",
            "close_price": 920.0,
            "change_percent": 9.9,
            "volume": 8000000
        }
    ]
    
    result = {
        "success": True,
        "data": mock_data[:limit],
        "count": len(mock_data[:limit]),
        "limit": limit,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 after_hours_limit_up 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/after_hours_limit_down")
async def after_hours_limit_down(limit: int = Query(1000, description="限制返回數量")):
    """盤後跌停股票數據"""
    logger.info(f"收到 after_hours_limit_down 請求: limit={limit}")
    
    # 簡化的模擬數據
    mock_data = [
        {
            "stock_code": "1303",
            "stock_name": "南亞",
            "close_price": 45.2,
            "change_percent": -9.8,
            "volume": 5000000
        }
    ]
    
    result = {
        "success": True,
        "data": mock_data[:limit],
        "count": len(mock_data[:limit]),
        "limit": limit,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 after_hours_limit_down 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/industries")
async def get_industries():
    """獲取所有產業類別"""
    logger.info("收到 industries 請求")
    
    industries = [
        {"id": "electronics", "name": "電子業", "count": 150},
        {"id": "finance", "name": "金融業", "count": 45},
        {"id": "traditional", "name": "傳產", "count": 200},
        {"id": "biotech", "name": "生技醫療", "count": 80}
    ]
    
    result = {
        "success": True,
        "data": industries,
        "count": len(industries)
    }
    
    logger.info(f"返回 industries 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/stocks_by_industry")
async def get_stocks_by_industry(
    industries: Optional[str] = Query(None, description="產業類別，用逗號分隔"),
    limit: int = Query(100, description="限制返回數量")
):
    """根據產業獲取股票"""
    logger.info(f"收到 stocks_by_industry 請求: industries={industries}, limit={limit}")
    
    # 簡化的模擬數據
    mock_stocks = [
        {
            "stock_code": "2330",
            "stock_name": "台積電",
            "industry": "electronics",
            "price": 580.0,
            "change_percent": 2.5
        },
        {
            "stock_code": "2454",
            "stock_name": "聯發科",
            "industry": "electronics",
            "price": 920.0,
            "change_percent": 1.8
        }
    ]
    
    # 如果指定了產業，進行過濾
    if industries:
        industry_list = [i.strip() for i in industries.split(",")]
        mock_stocks = [stock for stock in mock_stocks if stock["industry"] in industry_list]
    
    result = {
        "success": True,
        "data": mock_stocks[:limit],
        "count": len(mock_stocks[:limit]),
        "industries": industries,
        "limit": limit
    }
    
    logger.info(f"返回 stocks_by_industry 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/get_ohlc")
async def get_ohlc(stock_id: str = Query(..., description="股票代碼")):
    """獲取股票 OHLC 數據"""
    logger.info(f"收到 get_ohlc 請求: stock_id={stock_id}")
    
    # 簡化的模擬 OHLC 數據
    mock_ohlc = {
        "stock_code": stock_id,
        "stock_name": f"股票{stock_id}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "open": 100.0,
        "high": 105.0,
        "low": 98.0,
        "close": 103.0,
        "volume": 1000000,
        "change_percent": 3.0
    }
    
    result = {
        "success": True,
        "data": mock_ohlc
    }
    
    logger.info(f"返回 get_ohlc 數據: {result}")
    return result

# ==================== Posting Service 功能 ====================

@app.get("/posts")
async def get_posts(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """獲取貼文列表"""
    logger.info(f"收到 posts 請求: skip={skip}, limit={limit}, status={status}")
    
    # 簡化的模擬數據
    mock_posts = [
        {
            "id": 1,
            "title": "台積電財報分析",
            "content": "台積電第三季財報表現優異",
            "status": "published",
            "created_at": "2025-10-15T16:00:00Z",
            "kol_serial": "KOL001"
        },
        {
            "id": 2,
            "title": "聯發科技術突破",
            "content": "聯發科最新晶片技術",
            "status": "draft",
            "created_at": "2025-10-15T15:00:00Z",
            "kol_serial": "KOL002"
        }
    ]
    
    # 根據狀態過濾
    if status:
        mock_posts = [post for post in mock_posts if post["status"] == status]
    
    result = {
        "success": True,
        "data": mock_posts[skip:skip+limit],
        "count": len(mock_posts),
        "skip": skip,
        "limit": limit
    }
    
    logger.info(f"返回 posts 數據: {len(result['data'])} 條記錄")
    return result

@app.post("/intraday-trigger/execute")
async def execute_intraday_trigger():
    """執行盤中觸發器"""
    logger.info("收到 intraday-trigger/execute 請求")
    
    # 模擬執行結果
    result = {
        "success": True,
        "message": "盤中觸發器執行成功",
        "session_id": "session_123",
        "posts_generated": 5,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 intraday-trigger 結果: {result}")
    return result

# ==================== Dashboard API 功能 ====================

@app.get("/dashboard/system-monitoring")
async def get_system_monitoring():
    """獲取系統監控數據"""
    logger.info("收到 dashboard/system-monitoring 請求")
    
    monitoring_data = {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 23.1,
        "active_services": 10,
        "total_requests": 15420,
        "error_rate": 0.02,
        "uptime": "5 days, 12 hours",
        "last_updated": datetime.now().isoformat()
    }
    
    result = {
        "success": True,
        "data": monitoring_data
    }
    
    logger.info(f"返回 system-monitoring 數據: {result}")
    return result

@app.get("/dashboard/content-management")
async def get_content_management():
    """獲取內容管理數據"""
    logger.info("收到 dashboard/content-management 請求")
    
    content_data = {
        "total_posts": 1250,
        "published_posts": 980,
        "draft_posts": 270,
        "total_kols": 25,
        "active_kols": 18,
        "avg_engagement_rate": 4.2,
        "last_updated": datetime.now().isoformat()
    }
    
    result = {
        "success": True,
        "data": content_data
    }
    
    logger.info(f"返回 content-management 數據: {result}")
    return result

@app.get("/dashboard/interaction-analysis")
async def get_interaction_analysis():
    """獲取互動分析數據"""
    logger.info("收到 dashboard/interaction-analysis 請求")
    
    interaction_data = {
        "total_interactions": 45620,
        "likes": 23450,
        "comments": 12340,
        "shares": 9830,
        "avg_engagement_rate": 4.2,
        "top_performing_post": {
            "id": 123,
            "title": "台積電財報分析",
            "engagement_rate": 8.5
        },
        "last_updated": datetime.now().isoformat()
    }
    
    result = {
        "success": True,
        "data": interaction_data
    }
    
    logger.info(f"返回 interaction-analysis 數據: {result}")
    return result

# ==================== 錯誤處理 ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Not Found",
            "message": f"API endpoint {request.url.path} not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": "An internal server error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)