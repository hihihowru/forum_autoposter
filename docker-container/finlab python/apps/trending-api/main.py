import os
import requests
import json
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
import sys
sys.path.append('/app')

# 導入 CMoney 客戶端
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

# 導入智能 Agent
from src.agents.intelligent_topic_analyzer import IntelligentTopicAnalyzer
from src.agents.multi_level_search_strategy import MultiLevelSearchStrategy
from src.agents.smart_content_generator import SmartContentGenerator

app = FastAPI(title="Trending API", description="熱門話題和新聞素材API")

# 配置
CMONEY_API_KEY = os.getenv("CMONEY_API_KEY", "demo_key")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo_key")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "demo_key")

# 初始化智能 Agent
topic_analyzer = IntelligentTopicAnalyzer()
search_strategy = MultiLevelSearchStrategy(topic_analyzer)
content_generator = SmartContentGenerator()

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
    
    try:
        # 使用真實的 CMoney API
        cmoney_client = CMoneyClient()
        
        # 使用川川哥的憑證
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        # 登入並獲取熱門話題
        token = await cmoney_client.login(credentials)
        cmoney_topics = await cmoney_client.get_trending_topics(token.token)
        
        # 轉換為 API 格式
        trending_topics = []
        print(f"🔥 開始處理 {len(cmoney_topics)} 個 CMoney 熱門話題")
        
        for topic in cmoney_topics[:limit]:
            print(f"📝 處理話題 - Topic ID: {topic.id}, 標題: {topic.title}")
            
            # 獲取話題詳細資訊（包含股票資訊）
            try:
                topic_detail = await cmoney_client.get_topic_detail(token.token, topic.id)
                
                # 提取股票標籤
                stock_ids = []
                if 'relatedStockSymbols' in topic_detail:
                    stock_symbols = topic_detail['relatedStockSymbols']
                    stock_ids = [stock['key'] for stock in stock_symbols if stock.get('type') == 'Stock']
                
                # 提取話題描述
                description = topic_detail.get('description', topic.name)
                
                trending_topic = {
                    "id": topic.id,
                    "title": topic.title,
                    "content": description,
                    "stock_ids": stock_ids,
                    "category": "trending",
                    "created_at": datetime.now() - timedelta(hours=1),
                    "engagement_score": 0.8  # 可以根據實際數據計算
                }
                trending_topics.append(trending_topic)
                
                print(f"✅ 話題處理完成 - Topic ID: {topic.id}, 股票IDs: {stock_ids}")
                
            except Exception as detail_error:
                print(f"獲取話題 {topic.id} 詳細資訊失敗: {detail_error}")
                # 如果獲取詳細資訊失敗，使用基本資訊
                trending_topic = {
                    "id": topic.id,
                    "title": topic.title,
                    "content": topic.name,
                    "stock_ids": [],
                    "category": "trending",
                    "created_at": datetime.now() - timedelta(hours=1),
                    "engagement_score": 0.8
                }
                trending_topics.append(trending_topic)
        
        # 檢查是否有話題，如果沒有則使用 fallback
        if not trending_topics:
            print("CMoney API 返回空話題列表，使用模擬數據作為 fallback")
            print("🔥 開始使用模擬熱門話題數據")
            trending_topics = [
                {
                    "id": "mock_topic_001",
                    "title": "台股高檔震盪，開高走平背後的真相？",
                    "content": "台股今日開高後走平，市場關注後續走勢。從技術面來看，大盤在關鍵阻力位附近震盪，投資人需密切關注成交量變化。",
                    "stock_ids": ["2330", "2454", "2317"],
                    "category": "market_analysis",
                    "created_at": datetime.now() - timedelta(hours=1),
                    "engagement_score": 0.85
                },
                {
                    "id": "mock_topic_002",
                    "title": "AI概念股強勢，台積電領軍上攻",
                    "content": "AI概念股表現強勢，台積電領軍科技股上攻。隨著AI應用需求持續增長，相關供應鏈公司股價表現亮眼。",
                    "stock_ids": ["2330", "2454", "2379"],
                    "category": "technology",
                    "created_at": datetime.now() - timedelta(hours=2),
                    "engagement_score": 0.92
                },
                {
                    "id": "mock_topic_003",
                    "title": "通膨數據出爐，央行政策走向引關注",
                    "content": "最新通膨數據公布，市場關注央行政策動向。通膨壓力是否會影響利率政策，成為投資人關注焦點。",
                    "stock_ids": ["2881", "2882", "2886"],
                    "category": "macro_economics",
                    "created_at": datetime.now() - timedelta(hours=3),
                    "engagement_score": 0.78
                },
                {
                    "id": "mock_topic_004",
                    "title": "生技股異軍突起，減重藥題材發酵",
                    "content": "生技股異軍突起，減重藥題材持續發酵。隨著減重藥市場需求增長，相關生技公司股價表現強勢。",
                    "stock_ids": ["6919", "4743", "6547"],
                    "category": "biotech",
                    "created_at": datetime.now() - timedelta(hours=4),
                    "engagement_score": 0.88
                },
                {
                    "id": "mock_topic_005",
                    "title": "電動車概念股回溫，充電樁建設加速",
                    "content": "電動車概念股回溫，充電樁建設加速進行。隨著電動車普及率提升，充電基礎設施需求持續增長。",
                    "stock_ids": ["3661", "2308", "2377"],
                    "category": "green_energy",
                    "created_at": datetime.now() - timedelta(hours=5),
                    "engagement_score": 0.82
                }
            ]
        
        # 根據分類篩選
        if category:
            trending_topics = [t for t in trending_topics if t["category"] == category]
        
        return TrendingResponse(
            topics=trending_topics,
            timestamp=datetime.now(),
            total_count=len(trending_topics)
        )
        
    except Exception as e:
        # 如果真實 API 失敗，回退到模擬數據
        print(f"CMoney API 錯誤: {e}")
        
        # 模擬數據作為備用
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

@app.get("/extract-keywords")
async def extract_keywords_from_topic(
    topic_id: str = Query(..., description="熱門話題ID"),
    max_keywords: int = Query(5, description="最大關鍵字數量")
):
    """從熱門話題中提取關鍵字"""
    try:
        cmoney_client = CMoneyClient()
        credentials = LoginCredentials(email='forum_200@cmoney.com.tw', password='N9t1kY3x')
        token = await cmoney_client.login(credentials)
        
        # 獲取話題詳細資訊
        topic_detail = await cmoney_client.get_topic_detail(token.token, topic_id)
        
        # 提取關鍵字的邏輯 - 返回完整話題內容
        keywords = []
        
        # 組合標題和內容作為完整的話題描述
        title = topic_detail.get('title', '')
        content = topic_detail.get('description', '')
        
        # 將標題和內容組合成完整的話題描述
        full_topic_content = f"{title} {content}".strip()
        
        if full_topic_content:
            # 清理並截取內容
            cleaned_content = extract_keywords_from_text(full_topic_content)
            keywords.extend(cleaned_content)
        
        # 確保至少有一個關鍵字
        if not keywords:
            keywords = [title if title else "熱門話題內容"]
        
        return {
            "topic_id": topic_id,
            "title": title,
            "keywords": keywords,
            "extraction_method": "complete_topic_content",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"提取關鍵字失敗: {e}")
        return {"error": f"提取關鍵字失敗: {str(e)}"}

def extract_keywords_from_text(text: str) -> list:
    """從文本中提取關鍵字 - 返回完整內容而不是拆分"""
    import re
    
    # 清理文本，但保持完整性
    cleaned_text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    
    # 移除多餘空格
    cleaned_text = ' '.join(cleaned_text.split())
    
    # 如果文本太長，截取前100個字符
    if len(cleaned_text) > 100:
        cleaned_text = cleaned_text[:100] + '...'
    
    # 返回完整內容作為一個關鍵字
    return [cleaned_text] if cleaned_text.strip() else []

@app.get("/search-stocks-by-keywords")
async def search_stocks_by_keywords(
    keywords: str = Query(..., description="關鍵字列表，用逗號分隔"),
    limit: int = Query(10, description="回傳股票數量限制")
):
    """使用關鍵字搜尋相關股票"""
    try:
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        
        # 這裡可以整合股票搜尋邏輯
        # 目前先回傳模擬數據，後續可以整合 FinLab API 或其他股票搜尋服務
        matched_stocks = []
        
        for keyword in keyword_list:
            # 模擬股票搜尋結果
            # 實際實現時，這裡會調用股票搜尋 API
            if '台積電' in keyword or 'TSMC' in keyword or '半導體' in keyword:
                matched_stocks.append({
                    "code": "2330",
                    "name": "台積電",
                    "industry": "半導體業",
                    "match_keyword": keyword,
                    "match_score": 0.9
                })
            elif '鴻海' in keyword or 'Foxconn' in keyword or '電子' in keyword:
                matched_stocks.append({
                    "code": "2317", 
                    "name": "鴻海",
                    "industry": "其他電子業",
                    "match_keyword": keyword,
                    "match_score": 0.8
                })
            elif '聯發科' in keyword or 'MTK' in keyword or 'IC設計' in keyword:
                matched_stocks.append({
                    "code": "2454",
                    "name": "聯發科", 
                    "industry": "半導體業",
                    "match_keyword": keyword,
                    "match_score": 0.85
                })
            elif '台指' in keyword or '大盤' in keyword or '指數' in keyword:
                matched_stocks.append({
                    "code": "TWA00",
                    "name": "台指期",
                    "industry": "期貨",
                    "match_keyword": keyword,
                    "match_score": 0.95
                })
        
        # 去重並按匹配分數排序
        unique_stocks = {}
        for stock in matched_stocks:
            if stock["code"] not in unique_stocks or stock["match_score"] > unique_stocks[stock["code"]]["match_score"]:
                unique_stocks[stock["code"]] = stock
        
        sorted_stocks = sorted(unique_stocks.values(), key=lambda x: x["match_score"], reverse=True)[:limit]
        
        return {
            "keywords": keyword_list,
            "matched_stocks": sorted_stocks,
            "total_matches": len(sorted_stocks),
            "search_method": "keyword_matching",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"關鍵字搜尋股票失敗: {e}")
        return {"error": f"關鍵字搜尋股票失敗: {str(e)}"}

@app.get("/extract-and-search")
async def extract_keywords_and_search_stocks(
    topic_id: str = Query(..., description="熱門話題ID"),
    max_keywords: int = Query(5, description="最大關鍵字數量"),
    stock_limit: int = Query(10, description="回傳股票數量限制")
):
    """從熱門話題提取關鍵字並搜尋相關股票"""
    try:
        # 步驟1：提取關鍵字
        keywords_result = await extract_keywords_from_topic(topic_id, max_keywords)
        
        if "error" in keywords_result:
            return keywords_result
        
        keywords = keywords_result["keywords"]
        
        # 步驟2：使用關鍵字搜尋股票
        keywords_str = ",".join(keywords)
        stocks_result = await search_stocks_by_keywords(keywords_str, stock_limit)
        
        if "error" in stocks_result:
            return stocks_result
        
        # 整合結果
        return {
            "topic_id": topic_id,
            "topic_title": keywords_result["title"],
            "extracted_keywords": keywords,
            "matched_stocks": stocks_result["matched_stocks"],
            "total_matches": stocks_result["total_matches"],
            "extraction_method": keywords_result["extraction_method"],
            "search_method": stocks_result["search_method"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"提取關鍵字並搜尋股票失敗: {e}")
        return {"error": f"提取關鍵字並搜尋股票失敗: {str(e)}"}

# ==================== 智能 Agent 端點 ====================

@app.get("/analyze-topic")
async def analyze_topic_intelligently(
    topic_id: str = Query(..., description="熱門話題ID")
):
    """智能分析熱門話題"""
    try:
        # 獲取話題詳情
        cmoney_client = CMoneyClient()
        credentials = LoginCredentials(email='forum_200@cmoney.com.tw', password='N9t1kY3x')
        token = await cmoney_client.login(credentials)
        
        topic_detail = await cmoney_client.get_topic_detail(token.token, topic_id)
        
        if not topic_detail:
            return {"error": "無法獲取話題詳情"}
        
        # 智能分析話題
        topic_analysis = await topic_analyzer.analyze_topic(topic_detail)
        
        return {
            "topic_id": topic_id,
            "topic_title": topic_detail.get('title', ''),
            "analysis": {
                "topic_type": topic_analysis.topic_type,
                "sentiment": topic_analysis.sentiment,
                "market_impact": topic_analysis.market_impact,
                "confidence": topic_analysis.confidence,
                "entities": [
                    {
                        "text": entity.text,
                        "type": entity.type,
                        "confidence": entity.confidence
                    } for entity in topic_analysis.entities
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"智能分析話題失敗: {e}")
        return {"error": f"智能分析話題失敗: {str(e)}"}

@app.get("/generate-search-strategy")
async def generate_intelligent_search_strategy(
    topic_id: str = Query(..., description="熱門話題ID"),
    stock_code: str = Query(..., description="股票代號")
):
    """為特定股票生成智能搜尋策略"""
    try:
        # 獲取話題詳情
        cmoney_client = CMoneyClient()
        credentials = LoginCredentials(email='forum_200@cmoney.com.tw', password='N9t1kY3x')
        token = await cmoney_client.login(credentials)
        
        topic_detail = await cmoney_client.get_topic_detail(token.token, topic_id)
        
        if not topic_detail:
            return {"error": "無法獲取話題詳情"}
        
        # 生成搜尋策略
        search_strategy_result = await search_strategy.generate_search_strategy(topic_detail, stock_code)
        
        return {
            "topic_id": topic_id,
            "stock_code": stock_code,
            "search_strategy": {
                "recommended_strategy": search_strategy_result.recommended_strategy,
                "overall_confidence": search_strategy_result.overall_confidence,
                "queries": [
                    {
                        "level": query.level,
                        "query": query.query,
                        "priority": query.priority,
                        "weight": query.weight,
                        "strategy": query.strategy,
                        "confidence": query.confidence
                    } for query in search_strategy_result.queries
                ]
            },
            "news_search_keywords": search_strategy.get_search_keywords_for_news(search_strategy_result),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"生成搜尋策略失敗: {e}")
        return {"error": f"生成搜尋策略失敗: {str(e)}"}

@app.post("/generate-content")
async def generate_intelligent_content(
    topic_id: str = Query(..., description="熱門話題ID"),
    stock_code: str = Query(..., description="股票代號"),
    stock_data: dict = None,
    news_results: list = None
):
    """生成智能內容"""
    try:
        # 獲取話題詳情
        cmoney_client = CMoneyClient()
        credentials = LoginCredentials(email='forum_200@cmoney.com.tw', password='N9t1kY3x')
        token = await cmoney_client.login(credentials)
        
        topic_detail = await cmoney_client.get_topic_detail(token.token, topic_id)
        
        if not topic_detail:
            return {"error": "無法獲取話題詳情"}
        
        # 分析話題
        topic_analysis = await topic_analyzer.analyze_topic(topic_detail)
        
        # 生成搜尋策略
        search_strategy_result = await search_strategy.generate_search_strategy(topic_detail, stock_code)
        
        # 準備內容上下文
        from src.agents.smart_content_generator import ContentContext
        context = ContentContext(
            topic=topic_detail,
            stock_data=stock_data or {},
            news_results=news_results or [],
            topic_analysis=topic_analysis,
            search_strategy=search_strategy_result,
            timestamp=datetime.now()
        )
        
        # 生成內容
        generated_content = await content_generator.generate_contextual_content(context)
        
        return {
            "topic_id": topic_id,
            "stock_code": stock_code,
            "generated_content": {
                "content": generated_content.content,
                "style": generated_content.style,
                "confidence": generated_content.confidence,
                "data_sources": generated_content.data_sources,
                "news_sources": generated_content.news_sources,
                "metadata": generated_content.metadata
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"生成智能內容失敗: {e}")
        return {"error": f"生成智能內容失敗: {str(e)}"}

@app.get("/intelligent-extract-keywords")
async def intelligent_extract_keywords(
    topic_id: str = Query(..., description="熱門話題ID"),
    stock_code: str = Query(None, description="股票代號（可選）")
):
    """智能提取關鍵字（整合所有 Agent）"""
    try:
        # 獲取話題詳情
        cmoney_client = CMoneyClient()
        credentials = LoginCredentials(email='forum_200@cmoney.com.tw', password='N9t1kY3x')
        token = await cmoney_client.login(credentials)
        
        topic_detail = await cmoney_client.get_topic_detail(token.token, topic_id)
        
        if not topic_detail:
            return {"error": "無法獲取話題詳情"}
        
        # 智能分析話題
        topic_analysis = await topic_analyzer.analyze_topic(topic_detail)
        
        # 如果有股票代號，生成搜尋策略
        search_keywords = []
        if stock_code:
            search_strategy_result = await search_strategy.generate_search_strategy(topic_detail, stock_code)
            search_keywords = search_strategy.get_search_keywords_for_news(search_strategy_result)
        
        # 提取傳統關鍵字（保持向後兼容）
        traditional_keywords = extract_keywords_from_text(f"{topic_detail.get('title', '')} {topic_detail.get('description', '')}")
        
        return {
            "topic_id": topic_id,
            "topic_title": topic_detail.get('title', ''),
            "intelligent_analysis": {
                "topic_type": topic_analysis.topic_type,
                "sentiment": topic_analysis.sentiment,
                "market_impact": topic_analysis.market_impact,
                "confidence": topic_analysis.confidence
            },
            "keywords": {
                "traditional": traditional_keywords,
                "intelligent_search": search_keywords,
                "recommended": search_keywords if search_keywords else traditional_keywords
            },
            "extraction_method": "intelligent_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"智能提取關鍵字失敗: {e}")
        return {"error": f"智能提取關鍵字失敗: {str(e)}"}

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

