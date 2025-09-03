import os
import requests
import json
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

app = FastAPI(title="Posting Service", description="虛擬KOL自動發文服務")

# API 端點配置
TRENDING_API_URL = os.getenv("TRENDING_API_URL", "http://trending-api:8000")
SUMMARY_API_URL = os.getenv("SUMMARY_API_URL", "http://summary-api:8000")
OHLC_API_URL = os.getenv("OHLC_API_URL", "http://ohlc-api:8000")

class PostingRequest(BaseModel):
    kol_persona: str = "technical"
    content_style: str = "chart_analysis"
    target_audience: str = "active_traders"
    auto_post: bool = True
    post_to_thread: Optional[str] = None

class PostingResult(BaseModel):
    success: bool
    post_id: Optional[str] = None
    content: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: datetime

class AutoPostingConfig(BaseModel):
    enabled: bool = True
    interval_minutes: int = 60
    max_posts_per_day: int = 10
    kol_personas: List[str] = ["technical", "fundamental", "news_driven"]

@app.post("/post/auto", response_model=PostingResult)
async def auto_post_content(background_tasks: BackgroundTasks, config: AutoPostingConfig):
    """自動發文 - 根據熱門話題自動生成內容並發文"""
    
    try:
        # 1. 獲取熱門話題
        trending_response = requests.get(f"{TRENDING_API_URL}/trending", params={"limit": 5})
        trending_response.raise_for_status()
        trending_topics = trending_response.json()
        
        if not trending_topics.get("topics"):
            return PostingResult(
                success=False,
                error="沒有找到熱門話題",
                timestamp=datetime.now()
            )
        
        # 2. 選擇第一個熱門話題
        topic = trending_topics["topics"][0]
        stock_id = topic["stock_ids"][0] if topic["stock_ids"] else "2330"
        
        # 3. 獲取相關新聞素材
        news_response = requests.get(f"{TRENDING_API_URL}/news/stock/{stock_id}", params={"limit": 3})
        news_items = []
        if news_response.status_code == 200:
            news_items = news_response.json().get("news", [])
        
        # 4. 生成KOL內容
        content_request = {
            "stock_id": stock_id,
            "kol_persona": config.kol_personas[0],
            "content_style": "chart_analysis",
            "target_audience": "active_traders"
        }
        
        summary_response = requests.post(f"{SUMMARY_API_URL}/generate-kol-content", json=content_request)
        summary_response.raise_for_status()
        kol_content = summary_response.json()
        
        # 5. 整合新聞素材到內容中
        enhanced_content = enhance_content_with_news(kol_content, topic, news_items)
        
        # 6. 發文到指定平台
        if config.enabled:
            background_tasks.add_task(post_to_platform, enhanced_content, topic)
        
        return PostingResult(
            success=True,
            post_id=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=enhanced_content,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return PostingResult(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )

@app.post("/post/manual", response_model=PostingResult)
async def manual_post_content(request: PostingRequest):
    """手動發文 - 指定股票和KOL風格"""
    
    try:
        # 1. 獲取熱門股票
        trending_stocks_response = requests.get(f"{TRENDING_API_URL}/trending/stocks", params={"limit": 10})
        trending_stocks_response.raise_for_status()
        trending_stocks = trending_stocks_response.json()
        
        if not trending_stocks.get("stocks"):
            return PostingResult(
                success=False,
                error="沒有找到熱門股票",
                timestamp=datetime.now()
            )
        
        # 2. 選擇第一個熱門股票
        stock = trending_stocks["stocks"][0]
        stock_id = stock["stock_id"]
        
        # 3. 獲取相關新聞
        news_response = requests.get(f"{TRENDING_API_URL}/news/stock/{stock_id}", params={"limit": 3})
        news_items = []
        if news_response.status_code == 200:
            news_items = news_response.json().get("news", [])
        
        # 4. 生成KOL內容
        content_request = {
            "stock_id": stock_id,
            "kol_persona": request.kol_persona,
            "content_style": request.content_style,
            "target_audience": request.target_audience
        }
        
        summary_response = requests.post(f"{SUMMARY_API_URL}/generate-kol-content", json=content_request)
        summary_response.raise_for_status()
        kol_content = summary_response.json()
        
        # 5. 整合新聞素材
        enhanced_content = enhance_content_with_news(kol_content, {"title": f"{stock_id}分析"}, news_items)
        
        # 6. 發文
        if request.auto_post:
            background_tasks = BackgroundTasks()
            background_tasks.add_task(post_to_platform, enhanced_content, {"id": request.post_to_thread})
        
        return PostingResult(
            success=True,
            post_id=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=enhanced_content,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return PostingResult(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )

def enhance_content_with_news(kol_content: Dict, topic: Dict, news_items: List[Dict]) -> Dict:
    """整合新聞素材到KOL內容中"""
    
    enhanced_content = kol_content.copy()
    
    # 在內容中加入新聞素材
    if news_items:
        news_section = "\n\n### 📰 相關新聞素材\n"
        for i, news in enumerate(news_items[:3], 1):
            news_section += f"{i}. **{news['title']}**\n"
            news_section += f"   {news['summary'][:100]}...\n"
            news_section += f"   [閱讀更多]({news['url']})\n\n"
        
        # 在內容末尾加入新聞素材
        enhanced_content["content_md"] += news_section
        
        # 更新關鍵點
        enhanced_content["key_points"].append("整合最新新聞素材")
    
    # 加入話題標籤
    if topic.get("title"):
        enhanced_content["content_md"] += f"\n\n---\n*回應熱門話題：{topic['title']}*"
    
    return enhanced_content

async def post_to_platform(content: Dict, topic: Dict):
    """發文到指定平台 (模擬)"""
    
    # 這裡可以整合實際的發文平台API
    # 例如：Twitter API, LinkedIn API, 或自建平台
    
    post_data = {
        "content": content["content_md"],
        "title": content["title"],
        "stock_id": content["stock_id"],
        "kol_id": content["kol_id"],
        "topic_id": topic.get("id", "unknown"),
        "timestamp": datetime.now().isoformat()
    }
    
    # 模擬發文成功
    print(f"📝 發文成功: {content['title']}")
    print(f"📊 股票: {content['stock_id']}")
    print(f"👤 KOL: {content['kol_name']}")
    print(f"🔗 話題: {topic.get('title', 'N/A')}")
    
    # 實際整合時，這裡會調用發文平台API
    # response = requests.post("https://api.twitter.com/2/tweets", json=post_data)
    
    return {"success": True, "post_id": f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "trending_api": "connected",
            "summary_api": "connected",
            "ohlc_api": "connected"
        }
    }

@app.get("/trending/preview")
async def preview_trending_content():
    """預覽熱門話題內容"""
    
    try:
        # 獲取熱門話題
        trending_response = requests.get(f"{TRENDING_API_URL}/trending", params={"limit": 3})
        trending_response.raise_for_status()
        trending_topics = trending_response.json()
        
        # 獲取熱門股票
        stocks_response = requests.get(f"{TRENDING_API_URL}/trending/stocks", params={"limit": 5})
        stocks_response.raise_for_status()
        trending_stocks = stocks_response.json()
        
        return {
            "topics": trending_topics.get("topics", []),
            "stocks": trending_stocks.get("stocks", []),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

