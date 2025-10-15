"""
最簡化的測試 API - 確保 Railway 部署成功
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Forum Autoposter API",
    description="測試版 API 服務",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路徑"""
    logger.info("收到根路徑請求")
    return {
        "message": "Forum Autoposter API is running",
        "status": "healthy",
        "port": os.getenv("PORT", "unknown"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    logger.info("收到健康檢查請求")
    return {
        "status": "healthy",
        "message": "API is running successfully",
        "port": os.getenv("PORT", "unknown"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/after_hours_limit_up")
async def after_hours_limit_up(limit: int = 1000):
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
async def after_hours_limit_down(limit: int = 1000):
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

@app.get("/intraday-trigger/execute")
async def get_intraday_trigger_stocks(endpoint: str = "", processing: str = ""):
    """獲取盤中觸發器股票列表"""
    logger.info(f"收到盤中觸發器請求: endpoint={endpoint}, processing={processing}")
    
    # 模擬盤中觸發器股票數據
    result = {
        "success": True,
        "stocks": ["2330", "2454", "2317", "2412"],
        "data": [
            {"stock_code": "2330", "stock_name": "台積電", "change_percent": 5.2, "volume": 15000000},
            {"stock_code": "2454", "stock_name": "聯發科", "change_percent": 3.8, "volume": 8000000},
            {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 2.1, "volume": 12000000},
            {"stock_code": "2412", "stock_name": "中華電", "change_percent": 1.5, "volume": 5000000}
        ],
        "message": "盤中觸發器股票列表獲取成功",
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回盤中觸發器股票列表: {len(result['stocks'])} 支股票")
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)