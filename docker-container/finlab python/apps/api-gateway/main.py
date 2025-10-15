"""
API 網關 - 統一處理所有微服務的路由
Railway 部署時使用此網關來路由請求到不同的微服務
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from typing import Dict, Any
import logging
from datetime import datetime

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Forum Autoposter API Gateway",
    description="統一 API 網關，路由請求到不同的微服務",
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

# 微服務配置
SERVICES = {
    "ohlc": {
        "host": os.getenv("OHLC_SERVICE_HOST", "ohlc-api"),
        "port": int(os.getenv("OHLC_SERVICE_PORT", "8000")),
        "prefixes": ["/after_hours_limit_up", "/after_hours_limit_down", "/industries", "/stocks_by_industry", "/get_ohlc"]
    },
    "posting": {
        "host": os.getenv("POSTING_SERVICE_HOST", "posting-service"),
        "port": int(os.getenv("POSTING_SERVICE_PORT", "8000")),
        "prefixes": ["/posts", "/api/posting", "/api/schedule", "/intraday-trigger"]
    },
    "trending": {
        "host": os.getenv("TRENDING_SERVICE_HOST", "trending-api"),
        "port": int(os.getenv("TRENDING_SERVICE_PORT", "8000")),
        "prefixes": ["/trending", "/extract-keywords", "/search-stocks-by-keywords", "/analyze-topic", "/generate-content"]
    },
    "analyze": {
        "host": os.getenv("ANALYZE_SERVICE_HOST", "analyze-api"),
        "port": int(os.getenv("ANALYZE_SERVICE_PORT", "8000")),
        "prefixes": ["/analyze"]
    },
    "summary": {
        "host": os.getenv("SUMMARY_SERVICE_HOST", "summary-api"),
        "port": int(os.getenv("SUMMARY_SERVICE_PORT", "8000")),
        "prefixes": ["/summary"]
    },
    "dashboard": {
        "host": os.getenv("DASHBOARD_SERVICE_HOST", "dashboard-api"),
        "port": int(os.getenv("DASHBOARD_SERVICE_PORT", "8000")),
        "prefixes": ["/dashboard", "/health"]
    }
}

def get_service_for_path(path: str) -> Dict[str, Any]:
    """根據路徑確定應該路由到哪個服務"""
    for service_name, config in SERVICES.items():
        for prefix in config["prefixes"]:
            if path.startswith(prefix):
                return {
                    "name": service_name,
                    "host": config["host"],
                    "port": config["port"],
                    "url": f"http://{config['host']}:{config['port']}"
                }
    
    # 默認路由到 posting-service
    return {
        "name": "posting",
        "host": SERVICES["posting"]["host"],
        "port": SERVICES["posting"]["port"],
        "url": f"http://{SERVICES['posting']['host']}:{SERVICES['posting']['port']}"
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_request(path: str, request: Request):
    """代理請求到對應的微服務"""
    
    # 獲取目標服務
    service = get_service_for_path(f"/{path}")
    target_url = f"{service['url']}/{path}"
    
    # 添加查詢參數
    if request.url.query:
        target_url += f"?{request.url.query}"
    
    logger.info(f"🔄 路由請求: {request.method} /{path} -> {service['name']} ({target_url})")
    
    try:
        # 準備請求頭
        headers = dict(request.headers)
        # 移除可能導致問題的頭部
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # 準備請求體
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # 發送請求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body
            )
            
            # 返回響應
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        logger.error(f"⏰ 請求超時: {target_url}")
        raise HTTPException(status_code=504, detail="Gateway Timeout")
    except httpx.ConnectError:
        logger.error(f"🔌 連接失敗: {target_url}")
        raise HTTPException(status_code=502, detail="Bad Gateway - Service Unavailable")
    except Exception as e:
        logger.error(f"❌ 代理請求失敗: {target_url}, 錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/")
async def root():
    """根路徑 - 健康檢查"""
    return {
        "message": "Forum Autoposter API Gateway",
        "status": "healthy",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "gateway": "running",
        "message": "API Gateway is running successfully",
        "timestamp": datetime.now().isoformat(),
        "services": {name: f"{config['host']}:{config['port']}" for name, config in SERVICES.items()}
    }

# 添加一些基本的 API 端點，避免依賴其他微服務
@app.get("/after_hours_limit_up")
async def after_hours_limit_up(limit: int = 1000):
    """模擬 after_hours_limit_up 端點"""
    return {
        "success": True,
        "message": "API Gateway is working - this is a mock response",
        "data": [],
        "count": 0,
        "limit": limit
    }

@app.get("/after_hours_limit_down")
async def after_hours_limit_down(limit: int = 1000):
    """模擬 after_hours_limit_down 端點"""
    return {
        "success": True,
        "message": "API Gateway is working - this is a mock response",
        "data": [],
        "count": 0,
        "limit": limit
    }

@app.get("/industries")
async def get_industries():
    """模擬 industries 端點"""
    return {
        "success": True,
        "message": "API Gateway is working - this is a mock response",
        "data": ["電子業", "金融業", "傳產", "生技醫療"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
