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

# 微服務配置 - 基於你的 Railway 部署
SERVICES = {
    "ohlc": {
        "host": os.getenv("OHLC_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("OHLC_SERVICE_PORT", "8005")),
        "prefixes": ["/after_hours_limit_up", "/after_hours_limit_down", "/industries", "/stocks_by_industry", "/get_ohlc"]
    },
    "posting": {
        "host": os.getenv("POSTING_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("POSTING_SERVICE_PORT", "8001")),
        "prefixes": ["/posts", "/api/posting", "/api/schedule", "/intraday-trigger"]
    },
    "trending": {
        "host": os.getenv("TRENDING_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("TRENDING_SERVICE_PORT", "8004")),
        "prefixes": ["/trending", "/extract-keywords", "/search-stocks-by-keywords", "/analyze-topic", "/generate-content"]
    },
    "analyze": {
        "host": os.getenv("ANALYZE_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("ANALYZE_SERVICE_PORT", "8002")),
        "prefixes": ["/analyze"]
    },
    "summary": {
        "host": os.getenv("SUMMARY_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("SUMMARY_SERVICE_PORT", "8003")),
        "prefixes": ["/summary"]
    },
    "dashboard": {
        "host": os.getenv("DASHBOARD_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("DASHBOARD_SERVICE_PORT", "8012")),
        "prefixes": ["/dashboard", "/health"]
    },
    "financial": {
        "host": os.getenv("FINANCIAL_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("FINANCIAL_SERVICE_PORT", "8006")),
        "prefixes": ["/financial"]
    },
    "revenue": {
        "host": os.getenv("REVENUE_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("REVENUE_SERVICE_PORT", "8008")),
        "prefixes": ["/revenue"]
    },
    "monthly-revenue": {
        "host": os.getenv("MONTHLY_REVENUE_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("MONTHLY_REVENUE_SERVICE_PORT", "8009")),
        "prefixes": ["/monthly-revenue"]
    },
    "fundamental": {
        "host": os.getenv("FUNDAMENTAL_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("FUNDAMENTAL_SERVICE_PORT", "8010")),
        "prefixes": ["/fundamental"]
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

# 添加服務狀態檢查端點
@app.get("/services/status")
async def services_status():
    """檢查所有微服務的狀態"""
    import asyncio
    
    status = {}
    for service_name, config in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"http://{config['host']}:{config['port']}/health")
                status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": f"http://{config['host']}:{config['port']}",
                    "response_code": response.status_code
                }
        except Exception as e:
            status[service_name] = {
                "status": "unreachable",
                "url": f"http://{config['host']}:{config['port']}",
                "error": str(e)
            }
    
    return {
        "gateway": "running",
        "services": status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
