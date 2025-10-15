"""
統一的 API 服務 - 完整版本
Railway 部署時使用此服務作為唯一的 API 入口
"""

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
import json

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Forum Autoposter Unified API",
    description="統一的 API 服務，整合所有微服務功能",
    version="1.0.0"
)

# 配置 CORS - 允許 Vercel 域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://forum-autoposter-dz27.vercel.app",
        "https://forum-autoposter-dz27-*.vercel.app",  # 允許所有 preview 域名
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_origin_regex=r"^https:\/\/forum-autoposter-dz27.*\.vercel\.app$",  # 正則匹配所有 preview 域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ==================== 健康檢查 ====================

@app.get("/")
async def root():
    """根路徑"""
    logger.info("收到根路徑請求")
    return {
        "message": "Forum Autoposter Unified API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    logger.info("收到健康檢查請求")
    return {
        "status": "healthy",
        "message": "Unified API is running successfully",
        "timestamp": datetime.now().isoformat()
    }

# ==================== OHLC API 功能 ====================

@app.get("/after_hours_limit_up")
async def after_hours_limit_up(
    limit: int = Query(1000, description="限制返回數量"),
    changeThreshold: Optional[float] = Query(None, description="漲跌幅閾值"),
    sortBy: Optional[str] = Query(None, description="排序條件")
):
    """盤後漲停股票數據"""
    logger.info(f"收到 after_hours_limit_up 請求: limit={limit}, changeThreshold={changeThreshold}, sortBy={sortBy}")
    
    # 模擬 OHLC 數據
    mock_ohlc = [
        {
            "stock_id": "2330",
            "stock_name": "台積電",
            "close_price": 580.0,
            "change_percent": 9.8,
            "volume": 15000000,
            "market_cap": 1500000000000,
            "industry": "半導體"
        },
        {
            "stock_id": "2454",
            "stock_name": "聯發科",
            "close_price": 920.0,
            "change_percent": 9.9,
            "volume": 8000000,
            "market_cap": 150000000000,
            "industry": "半導體"
        },
        {
            "stock_id": "2317",
            "stock_name": "鴻海",
            "close_price": 105.5,
            "change_percent": 8.5,
            "volume": 12000000,
            "market_cap": 150000000000,
            "industry": "電子製造"
        },
        {
            "stock_id": "2412",
            "stock_name": "中華電",
            "close_price": 125.0,
            "change_percent": 7.2,
            "volume": 5000000,
            "market_cap": 100000000000,
            "industry": "電信"
        }
    ]
    
    # 應用篩選條件
    filtered_data = mock_ohlc
    if changeThreshold:
        filtered_data = [stock for stock in filtered_data if stock["change_percent"] >= changeThreshold]
    
    # 應用排序
    if sortBy:
        sort_fields = sortBy.split(',')
        for field in reversed(sort_fields):  # 從最後一個字段開始排序
            if field == "volume":
                filtered_data.sort(key=lambda x: x["volume"], reverse=True)
            elif field == "change_percent":
                filtered_data.sort(key=lambda x: x["change_percent"], reverse=True)
            elif field == "market_cap":
                filtered_data.sort(key=lambda x: x["market_cap"], reverse=True)
    
    result = {
        "success": True,
        "message": "API Gateway is working - this is a mock response",
        "data": filtered_data[:limit],
        "count": len(filtered_data[:limit]),
        "limit": limit,
        "filters_applied": {
            "changeThreshold": changeThreshold,
            "sortBy": sortBy
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 after_hours_limit_up 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/after_hours_limit_down")
async def after_hours_limit_down(
    limit: int = Query(1000, description="限制返回數量"),
    changeThreshold: Optional[float] = Query(None, description="漲跌幅閾值"),
    sortBy: Optional[str] = Query(None, description="排序條件")
):
    """盤後跌停股票數據"""
    logger.info(f"收到 after_hours_limit_down 請求: limit={limit}, changeThreshold={changeThreshold}, sortBy={sortBy}")
    
    # 模擬跌停數據
    mock_ohlc = [
        {
            "stock_id": "1303",
            "stock_name": "南亞",
            "close_price": 45.2,
            "change_percent": -9.8,
            "volume": 5000000,
            "market_cap": 50000000000,
            "industry": "塑膠"
        },
        {
            "stock_id": "2002",
            "stock_name": "中鋼",
            "close_price": 28.5,
            "change_percent": -9.5,
            "volume": 8000000,
            "market_cap": 45000000000,
            "industry": "鋼鐵"
        }
    ]
    
    # 應用篩選條件
    filtered_data = mock_ohlc
    if changeThreshold:
        filtered_data = [stock for stock in filtered_data if stock["change_percent"] <= changeThreshold]
    
    result = {
        "success": True,
        "message": "API Gateway is working - this is a mock response",
        "data": filtered_data[:limit],
        "count": len(filtered_data[:limit]),
        "limit": limit,
        "filters_applied": {
            "changeThreshold": changeThreshold,
            "sortBy": sortBy
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 after_hours_limit_down 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/industries")
async def get_industries():
    """獲取所有產業類別"""
    logger.info("收到 industries 請求")
    
    industries = [
        {"id": "electronics", "name": "電子業", "count": 150, "description": "半導體、電子製造等"},
        {"id": "finance", "name": "金融業", "count": 45, "description": "銀行、保險、證券等"},
        {"id": "traditional", "name": "傳產", "count": 200, "description": "鋼鐵、塑膠、紡織等"},
        {"id": "biotech", "name": "生技醫療", "count": 80, "description": "製藥、醫療器材等"},
        {"id": "telecom", "name": "電信", "count": 15, "description": "電信服務、網路等"}
    ]
    
    result = {
        "success": True,
        "data": industries,
        "count": len(industries),
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 industries 數據: {len(result['data'])} 條記錄")
    return result

@app.get("/stocks_by_industry")
async def get_stocks_by_industry(industry: str = Query(..., description="產業類別")):
    """根據產業獲取股票列表"""
    logger.info(f"收到 stocks_by_industry 請求: industry={industry}")
    
    # 模擬不同產業的股票數據
    industry_stocks = {
        "electronics": [
            {"stock_id": "2330", "stock_name": "台積電", "industry": "半導體"},
            {"stock_id": "2454", "stock_name": "聯發科", "industry": "半導體"},
            {"stock_id": "2317", "stock_name": "鴻海", "industry": "電子製造"}
        ],
        "finance": [
            {"stock_id": "2881", "stock_name": "富邦金", "industry": "銀行"},
            {"stock_id": "2882", "stock_name": "國泰金", "industry": "銀行"},
            {"stock_id": "2886", "stock_name": "兆豐金", "industry": "銀行"}
        ],
        "traditional": [
            {"stock_id": "1303", "stock_name": "南亞", "industry": "塑膠"},
            {"stock_id": "2002", "stock_name": "中鋼", "industry": "鋼鐵"}
        ]
    }
    
    stocks = industry_stocks.get(industry, [])
    
    result = {
        "success": True,
        "data": stocks,
        "count": len(stocks),
        "industry": industry,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 {industry} 產業股票: {len(result['data'])} 支")
    return result

@app.get("/get_ohlc")
async def get_ohlc(stock_id: str = Query(..., description="股票代碼")):
    """獲取特定股票的 OHLC 數據"""
    logger.info(f"收到 get_ohlc 請求: stock_id={stock_id}")
    
    # 模擬 OHLC 數據
    mock_ohlc = {
        "stock_id": stock_id,
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
        "data": mock_ohlc,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回 {stock_id} 的 OHLC 數據")
    return result

# ==================== 盤中觸發器功能 ====================

@app.get("/intraday-trigger/execute")
async def get_intraday_trigger_stocks(
    endpoint: str = Query(..., description="數據源端點"), 
    processing: str = Query("", description="處理配置")
):
    """獲取盤中觸發器股票列表"""
    logger.info(f"收到盤中觸發器請求: endpoint={endpoint}, processing={processing}")
    
    # 解析處理配置
    processing_config = []
    if processing:
        try:
            processing_config = json.loads(processing) if isinstance(processing, str) else processing
        except:
            processing_config = []
    
    # 模擬盤中觸發器股票數據
    result = {
        "success": True,
        "stocks": ["2330", "2454", "2317", "2412"],
        "data": [
            {
                "stock_code": "2330", 
                "stock_name": "台積電", 
                "change_percent": 5.2, 
                "volume": 15000000,
                "current_price": 580.0,
                "intraday_high": 585.0,
                "intraday_low": 575.0
            },
            {
                "stock_code": "2454", 
                "stock_name": "聯發科", 
                "change_percent": 3.8, 
                "volume": 8000000,
                "current_price": 920.0,
                "intraday_high": 925.0,
                "intraday_low": 915.0
            },
            {
                "stock_code": "2317", 
                "stock_name": "鴻海", 
                "change_percent": 2.1, 
                "volume": 12000000,
                "current_price": 105.5,
                "intraday_high": 106.0,
                "intraday_low": 104.0
            },
            {
                "stock_code": "2412", 
                "stock_name": "中華電", 
                "change_percent": 1.5, 
                "volume": 5000000,
                "current_price": 125.0,
                "intraday_high": 126.0,
                "intraday_low": 124.0
            }
        ],
        "message": "盤中觸發器股票列表獲取成功",
        "endpoint": endpoint,
        "processing_config": processing_config,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"返回盤中觸發器股票列表: {len(result['stocks'])} 支股票")
    return result

# ==================== Posting Service 功能 ====================

@app.post("/api/posting")
async def create_posting(request: Request):
    """創建貼文"""
    logger.info("收到 create_posting 請求")
    
    try:
        body = await request.json()
        logger.info(f"貼文內容: {body}")
        
        result = {
            "success": True,
            "message": "貼文創建成功",
            "post_id": "post_12345",
            "data": body,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("貼文創建成功")
        return result
        
    except Exception as e:
        logger.error(f"貼文創建失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"貼文創建失敗: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/api/manual-posting")
async def manual_posting(request: Request):
    """手動貼文"""
    logger.info("收到 manual_posting 請求")
    
    try:
        body = await request.json()
        logger.info(f"手動貼文內容: {body}")
        
        result = {
            "success": True,
            "message": "手動貼文成功",
            "post_id": "manual_post_67890",
            "data": body,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("手動貼文成功")
        return result
        
    except Exception as e:
        logger.error(f"手動貼文失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"手動貼文失敗: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

# ==================== Dashboard API 功能 ====================

@app.get("/dashboard/system-monitoring")
async def get_system_monitoring():
    """獲取系統監控數據"""
    logger.info("收到 system-monitoring 請求")
    
    result = {
        "success": True,
        "data": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "active_connections": 156,
            "uptime": "5 days, 12 hours",
            "last_restart": "2025-10-10T08:30:00Z"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info("返回系統監控數據")
    return result

@app.get("/dashboard/content-management")
async def get_content_management():
    """獲取內容管理數據"""
    logger.info("收到 content-management 請求")
    
    result = {
        "success": True,
        "data": {
            "total_posts": 1250,
            "published_posts": 1180,
            "draft_posts": 70,
            "scheduled_posts": 45,
            "failed_posts": 5
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info("返回內容管理數據")
    return result

@app.get("/dashboard/interaction-analysis")
async def get_interaction_analysis():
    """獲取互動分析數據"""
    logger.info("收到 interaction-analysis 請求")
    
    result = {
        "success": True,
        "data": {
            "total_interactions": 15680,
            "likes": 8920,
            "comments": 2340,
            "shares": 4420,
            "engagement_rate": 12.5,
            "top_performing_posts": [
                {"post_id": "post_001", "interactions": 1250},
                {"post_id": "post_002", "interactions": 980},
                {"post_id": "post_003", "interactions": 750}
            ]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info("返回互動分析數據")
    return result

# ==================== Trending API 功能 ====================

@app.get("/trending")
async def get_trending_topics():
    """獲取熱門話題"""
    logger.info("收到 trending 請求")
    
    result = {
        "success": True,
        "data": [
            {"topic": "AI人工智慧", "trend_score": 95.5, "posts_count": 1250},
            {"topic": "電動車", "trend_score": 88.2, "posts_count": 980},
            {"topic": "半導體", "trend_score": 82.1, "posts_count": 750},
            {"topic": "新能源", "trend_score": 76.8, "posts_count": 650}
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info("返回熱門話題數據")
    return result

@app.get("/extract-keywords")
async def extract_keywords(text: str = Query(..., description="要提取關鍵字的文本")):
    """提取關鍵字"""
    logger.info(f"收到 extract-keywords 請求: text={text[:50]}...")
    
    # 模擬關鍵字提取
    keywords = ["AI", "人工智慧", "科技", "創新", "發展"]
    
    result = {
        "success": True,
        "data": {
            "keywords": keywords,
            "confidence_scores": [0.95, 0.88, 0.82, 0.76, 0.65],
            "original_text": text
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"提取到 {len(keywords)} 個關鍵字")
    return result

@app.get("/search-stocks-by-keywords")
async def search_stocks_by_keywords(keywords: str = Query(..., description="關鍵字")):
    """根據關鍵字搜索股票"""
    logger.info(f"收到 search-stocks-by-keywords 請求: keywords={keywords}")
    
    # 模擬股票搜索結果
    stocks = [
        {"stock_id": "2330", "stock_name": "台積電", "relevance_score": 0.95},
        {"stock_id": "2454", "stock_name": "聯發科", "relevance_score": 0.88},
        {"stock_id": "2317", "stock_name": "鴻海", "relevance_score": 0.82}
    ]
    
    result = {
        "success": True,
        "data": {
            "stocks": stocks,
            "keywords": keywords,
            "total_found": len(stocks)
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"找到 {len(stocks)} 支相關股票")
    return result

@app.get("/analyze-topic")
async def analyze_topic(topic: str = Query(..., description="要分析的話題")):
    """分析話題"""
    logger.info(f"收到 analyze-topic 請求: topic={topic}")
    
    result = {
        "success": True,
        "data": {
            "topic": topic,
            "sentiment": "positive",
            "sentiment_score": 0.75,
            "key_points": [
                "技術創新持續推進",
                "市場需求穩定增長",
                "政策支持力度加大"
            ],
            "related_stocks": ["2330", "2454", "2317"]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"完成話題分析: {topic}")
    return result

@app.get("/generate-content")
async def generate_content(
    topic: str = Query(..., description="話題"),
    style: str = Query("professional", description="內容風格")
):
    """生成內容"""
    logger.info(f"收到 generate-content 請求: topic={topic}, style={style}")
    
    result = {
        "success": True,
        "data": {
            "content": f"關於{topic}的專業分析：市場趨勢顯示該領域具有強勁的成長潛力，建議投資人密切關注相關標的。",
            "topic": topic,
            "style": style,
            "word_count": 45,
            "generated_at": datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"生成內容完成: {topic}")
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)