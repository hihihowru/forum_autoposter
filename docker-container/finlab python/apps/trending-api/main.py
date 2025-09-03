import os
import requests
import json
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

app = FastAPI(title="Trending API", description="熱門話題和新聞素材API")

# 配置
CMONEY_API_KEY = os.getenv("CMONEY_API_KEY", "demo_key")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo_key")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "demo_key")

class TrendingTopic(BaseModel):
    id: str
    title: str
    content: str
    stock_ids: List[str]
    category: str
    created_at: datetime
    engagement_score: float

class NewsItem(BaseModel):
    title: str
    summary: str
    url: str
    published_at: datetime
    relevance_score: float
    stock_ids: List[str]

class TrendingResponse(BaseModel):
    topics: List[TrendingTopic]
    timestamp: datetime
    total_count: int

class NewsResponse(BaseModel):
    news: List[NewsItem]
    query: str
    timestamp: datetime

@app.get("/trending", response_model=TrendingResponse)
async def get_trending_topics(
    limit: int = Query(10, description="獲取話題數量"),
    category: str = Query(None, description="話題分類")
):
    """獲取 Cmoney 熱門話題"""
    
    # 模擬 Cmoney API 回應 (實際整合時替換)
    trending_topics = [
        {
            "id": "topic_001",
            "title": "台積電法說會亮眼，AI需求強勁",
            "content": "台積電最新法說會顯示AI需求持續強勁，營收展望樂觀...",
            "stock_ids": ["2330", "2454", "3034"],
            "category": "earnings",
            "created_at": datetime.now() - timedelta(hours=2),
            "engagement_score": 0.85
        },
        {
            "id": "topic_002", 
            "title": "聯發科5G晶片市占率提升",
            "content": "聯發科在5G晶片市場表現亮眼，市占率持續提升...",
            "stock_ids": ["2454", "2379"],
            "category": "technology",
            "created_at": datetime.now() - timedelta(hours=4),
            "engagement_score": 0.72
        },
        {
            "id": "topic_003",
            "title": "鴻海電動車布局加速",
            "content": "鴻海在電動車領域布局加速，與多家車廠合作...",
            "stock_ids": ["2317", "2354"],
            "category": "automotive",
            "created_at": datetime.now() - timedelta(hours=6),
            "engagement_score": 0.68
        }
    ]
    
    # 根據分類篩選
    if category:
        trending_topics = [t for t in trending_topics if t["category"] == category]
    
    # 限制數量
    trending_topics = trending_topics[:limit]
    
    return TrendingResponse(
        topics=trending_topics,
        timestamp=datetime.now(),
        total_count=len(trending_topics)
    )

@app.get("/news/search", response_model=NewsResponse)
async def search_news(
    query: str = Query(..., description="搜尋關鍵字"),
    stock_id: str = Query(None, description="股票代號"),
    limit: int = Query(10, description="新聞數量")
):
    """搜尋相關新聞素材"""
    
    # 模擬新聞API回應 (實際整合時替換)
    news_items = [
        {
            "title": f"{query}相關新聞標題1",
            "summary": f"這是關於{query}的新聞摘要，包含重要資訊...",
            "url": "https://example.com/news1",
            "published_at": datetime.now() - timedelta(hours=1),
            "relevance_score": 0.92,
            "stock_ids": [stock_id] if stock_id else []
        },
        {
            "title": f"{query}產業分析報告",
            "summary": f"深入分析{query}產業發展趨勢和投資機會...",
            "url": "https://example.com/news2", 
            "published_at": datetime.now() - timedelta(hours=3),
            "relevance_score": 0.87,
            "stock_ids": [stock_id] if stock_id else []
        }
    ]
    
    # 限制數量
    news_items = news_items[:limit]
    
    return NewsResponse(
        news=news_items,
        query=query,
        timestamp=datetime.now()
    )

@app.get("/news/stock/{stock_id}", response_model=NewsResponse)
async def get_stock_news(
    stock_id: str,
    limit: int = Query(10, description="新聞數量"),
    days_back: int = Query(7, description="回溯天數")
):
    """根據股票代號獲取相關新聞"""
    
    # 模擬股票相關新聞 (實際整合時替換)
    stock_news = [
        {
            "title": f"{stock_id}最新財報分析",
            "summary": f"{stock_id}發布最新財報，營收成長表現亮眼...",
            "url": f"https://example.com/stock/{stock_id}/earnings",
            "published_at": datetime.now() - timedelta(hours=2),
            "relevance_score": 0.95,
            "stock_ids": [stock_id]
        },
        {
            "title": f"{stock_id}產業趨勢分析",
            "summary": f"分析{stock_id}所屬產業的發展趨勢和投資機會...",
            "url": f"https://example.com/stock/{stock_id}/industry",
            "published_at": datetime.now() - timedelta(hours=6),
            "relevance_score": 0.88,
            "stock_ids": [stock_id]
        }
    ]
    
    # 限制數量和時間範圍
    cutoff_date = datetime.now() - timedelta(days=days_back)
    stock_news = [n for n in stock_news if n["published_at"] >= cutoff_date]
    stock_news = stock_news[:limit]
    
    return NewsResponse(
        news=stock_news,
        query=f"stock:{stock_id}",
        timestamp=datetime.now()
    )

@app.get("/trending/stocks")
async def get_trending_stocks(
    limit: int = Query(20, description="股票數量")
):
    """獲取熱門股票列表"""
    
    # 模擬熱門股票數據 (實際整合時替換)
    trending_stocks = [
        {"stock_id": "2330", "name": "台積電", "trend_score": 0.95, "volume_change": 0.15},
        {"stock_id": "2454", "name": "聯發科", "trend_score": 0.87, "volume_change": 0.12},
        {"stock_id": "2317", "name": "鴻海", "trend_score": 0.82, "volume_change": 0.08},
        {"stock_id": "3008", "name": "大立光", "trend_score": 0.78, "volume_change": 0.06},
        {"stock_id": "2412", "name": "中華電", "trend_score": 0.75, "volume_change": 0.05}
    ]
    
    # 按熱門度排序
    trending_stocks.sort(key=lambda x: x["trend_score"], reverse=True)
    
    return {
        "stocks": trending_stocks[:limit],
        "timestamp": datetime.now(),
        "total_count": len(trending_stocks)
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "cmoney_api": "connected" if CMONEY_API_KEY != "demo_key" else "demo_mode",
            "news_api": "connected" if ALPHA_VANTAGE_API_KEY != "demo_key" else "demo_mode"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

