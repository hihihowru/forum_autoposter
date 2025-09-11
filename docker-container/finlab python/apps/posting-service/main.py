import os
import requests
import json
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import sys
import json
from dotenv import load_dotenv
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 開始載入模組...")

# 導入改進的內容生成器
from improved_content_generator import generate_improved_kol_content
# 導入GPT內容生成器
from gpt_content_generator import gpt_generator

# 載入環境變數
print("📝 載入環境變數...")
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))
print("✅ 環境變數載入完成")

# 使用本地的post_record_service
print("📦 導入post_record_service...")
from post_record_service import PostRecordCreate, CommodityTag, CommunityTopic, GenerationParams, PostRecordService, PostRecordUpdate
print("✅ post_record_service導入完成")

print("🏗️ 創建FastAPI應用...")
app = FastAPI(title="Posting Service", description="虛擬KOL自動發文服務")
print("✅ FastAPI應用創建完成")

# 添加 CORS 中間件
print("🌐 添加CORS中間件...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("✅ CORS中間件添加完成")

# API 端點配置
print("⚙️ 配置API端點...")
TRENDING_API_URL = os.getenv("TRENDING_API_URL", "http://localhost:8004")
SUMMARY_API_URL = os.getenv("SUMMARY_API_URL", "http://summary-api:8003")
OHLC_API_URL = os.getenv("OHLC_API_URL", "http://ohlc-api:8001")
print("✅ API端點配置完成")

# 初始化數據庫服務
print("💾 初始化數據庫服務...")
post_record_service = PostRecordService()
print("✅ 數據庫服務初始化完成")

class PostingRequest(BaseModel):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    kol_serial: Optional[str] = None
    kol_persona: str = "technical"
    content_style: str = "chart_analysis"
    target_audience: str = "active_traders"
    auto_post: bool = True
    post_to_thread: Optional[str] = None
    batch_mode: bool = False
    session_id: Optional[int] = None
    # 內容長度設定
    content_length: str = "medium"
    max_words: int = 200
    # 新增數據源相關欄位
    data_sources: Optional[Dict[str, Any]] = None
    explainability_config: Optional[Dict[str, Any]] = None
    news_config: Optional[Dict[str, Any]] = None

class PostingResult(BaseModel):
    success: bool
    post_id: Optional[str] = None
    content: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: datetime

class BatchPostRequest(BaseModel):
    session_id: int
    posts: List[Dict[str, Any]]
    batch_config: Dict[str, Any]
    data_sources: Optional[Dict[str, Any]] = None
    explainability_config: Optional[Dict[str, Any]] = None
    news_config: Optional[Dict[str, Any]] = None

class BatchPostResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    content: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str
    progress: Optional[Dict[str, Any]] = None

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
    
    print(f"🚀 開始手動發文生成 - 請求參數: {request}")
    print(f"📝 內容長度設定: content_length={request.content_length}, max_words={request.max_words}")
    
    try:
        # 如果前端指定了股票代號，使用指定的股票
        if request.stock_code:
            stock_id = request.stock_code
            stock_name = request.stock_name or f"股票{stock_id}"
            print(f"📊 使用指定股票: {stock_name}({stock_id})")
        else:
            # 否則獲取熱門股票
            print("📈 獲取熱門股票...")
            try:
                trending_stocks_response = requests.get(f"{TRENDING_API_URL}/trending/stocks", params={"limit": 10})
                trending_stocks_response.raise_for_status()
                trending_stocks = trending_stocks_response.json()
                
                if not trending_stocks.get("stocks"):
                    print("⚠️ 沒有找到熱門股票")
                    return PostingResult(
                        success=False,
                        error="沒有找到熱門股票",
                        timestamp=datetime.now()
                    )
                
                # 選擇第一個熱門股票
                stock = trending_stocks["stocks"][0]
                stock_id = stock["stock_id"]
                stock_name = stock.get("stock_name", f"股票{stock_id}")
                print(f"📈 選擇熱門股票: {stock_name}({stock_id})")
            except Exception as e:
                print(f"⚠️ 獲取熱門股票失敗: {e}")
                stock_id = "2330"
                stock_name = "台積電"
                print(f"📈 使用預設股票: {stock_name}({stock_id})")
        
        print(f"✅ 股票確定: {stock_name}({stock_id})")
        
        # 導入新的服務
        print("🔧 導入服務模組...")
        try:
            from serper_integration import serper_service
            from smart_data_source_assigner import smart_assigner, KOLProfile, StockProfile
            from publish_service import publish_service
            print("✅ 服務模組導入成功")
        except Exception as e:
            print(f"❌ 服務模組導入失敗: {e}")
            raise
        
        # 1. 智能數據源分配
        print(f"🎯 開始智能數據源分配: {stock_id}, {request.kol_persona}")
        
        # 檢查是否有前端傳來的數據源配置
        if request.data_sources:
            print(f"📊 使用前端數據源配置: {request.data_sources}")
            # 使用前端配置的數據源
            primary_sources = []
            if request.data_sources.get('stock_price_api'):
                primary_sources.append('ohlc_api')
            if request.data_sources.get('monthly_revenue_api'):
                primary_sources.append('revenue_api')
            if request.data_sources.get('financial_report_api'):
                primary_sources.append('financial_api')
            if request.data_sources.get('news_sources', []):
                primary_sources.append('serper_api')
            
            # 創建模擬的數據源分配結果
            from smart_data_source_assigner import DataSourceAssignment, DataSourceType
            data_source_assignment = DataSourceAssignment(
                primary_sources=[DataSourceType(source) for source in primary_sources if hasattr(DataSourceType, source)],
                secondary_sources=[],
                excluded_sources=[],
                assignment_reason=f"基於前端配置: {', '.join(primary_sources)}",
                confidence_score=0.9
            )
        else:
            # 使用智能分配邏輯
            kol_profile = KOLProfile(
                serial=int(request.kol_serial) if request.kol_serial else 1,
                nickname=f"KOL-{request.kol_serial or '1'}",
                persona=request.kol_persona,
                expertise_areas=[request.kol_persona],
                content_style=request.content_style,
                target_audience=request.target_audience
            )
            
            stock_profile = StockProfile(
                stock_code=stock_id,
                stock_name=stock_name,
                industry="科技",  # 可以從API獲取
                market_cap="medium",  # 可以從API獲取
                volatility="medium",  # 可以從API獲取
                news_frequency="medium"  # 可以從API獲取
            )
            
            # 分配數據源
            data_source_assignment = smart_assigner.assign_data_sources(kol_profile, stock_profile)
        
        print(f"✅ 數據源分配完成: {data_source_assignment.assignment_reason}")
        print(f"📊 主要數據源: {[s.value for s in data_source_assignment.primary_sources]}")
        
        # 2. 獲取Serper新聞數據 - 使用前端配置的關鍵字
        print(f"🔍 開始獲取Serper新聞數據: {stock_id}")
        try:
            # 提取新聞搜尋關鍵字配置
            search_keywords = None
            if request.news_config and request.news_config.get('search_keywords'):
                search_keywords = request.news_config.get('search_keywords')
                print(f"📝 使用前端新聞關鍵字配置: {len(search_keywords)} 個關鍵字")
                for kw in search_keywords:
                    print(f"   - {kw.get('type', 'custom')}: {kw.get('keyword', '')}")
            else:
                print("📝 使用預設新聞搜尋關鍵字")
            
            serper_analysis = serper_service.get_comprehensive_stock_analysis(
                stock_id, 
                stock_name, 
                search_keywords=search_keywords
            )
            news_items = serper_analysis.get('news_items', [])
            limit_up_analysis = serper_analysis.get('limit_up_analysis', {})
            print(f"✅ Serper分析完成: 找到 {len(news_items)} 則新聞")
        except Exception as e:
            print(f"⚠️ Serper分析失敗: {e}")
            serper_analysis = {'news_items': [], 'limit_up_analysis': {}}
            news_items = []
            limit_up_analysis = {}
        
        # 3. 生成KOL內容 - 強制使用新聞分析Agent
        print(f"✍️ 開始生成KOL內容: {stock_id}, {request.kol_persona}")
        
        try:
            # 強制使用新聞分析Agent
            if news_items:
                print(f"🤖 強制使用新聞分析Agent分析 {len(news_items)} 則新聞")
                from news_analysis_agent import NewsAnalysisAgent
                # 創建新的實例以確保API Key正確載入
                news_agent = NewsAnalysisAgent()
                kol_content = news_agent.analyze_stock_news(
                    stock_id, stock_name, news_items, request.kol_persona, 
                    request.content_length, request.max_words
                )
                print(f"✅ Agent內容生成完成: {len(kol_content.get('content', ''))} 字")
            else:
                print("⚠️ 沒有新聞數據，使用GPT生成器")
                kol_content = gpt_generator.generate_stock_analysis(
                    stock_id=stock_id,
                    stock_name=stock_name,
                    kol_persona=request.kol_persona,
                    serper_analysis=serper_analysis,
                    data_sources=[source.value for source in data_source_assignment.primary_sources],
                    content_length=request.content_length,
                    max_words=request.max_words
                )
                print(f"✅ GPT內容生成完成: {len(kol_content.get('content', ''))} 字")
        except Exception as e:
            print(f"❌ Agent內容生成失敗: {e}")
            # 回退到改進的內容生成器
            kol_content = generate_improved_kol_content(
                stock_id=stock_id,
                stock_name=stock_name,
                kol_persona=request.kol_persona,
                content_style=request.content_style,
                target_audience=request.target_audience,
                serper_analysis=serper_analysis,
                data_sources=[source.value for source in data_source_assignment.primary_sources]
            )
            print(f"✅ 回退內容生成完成: {len(kol_content.get('content', ''))} 字")
        
        # 4. 整合新聞素材和數據源資訊
        print("🔗 整合新聞素材和數據源資訊...")
        try:
            enhanced_content = enhance_content_with_serper_data(
                kol_content, 
                serper_analysis, 
                data_source_assignment
            )
            print("✅ 內容整合完成")
        except Exception as e:
            print(f"⚠️ 內容整合失敗: {e}")
            enhanced_content = kol_content
        
        # 添加額外的欄位以符合前端期望
        enhanced_content.update({
            "stock_code": stock_id,
            "stock_name": stock_name,
            "kol_serial": request.kol_serial or "1",
            "session_id": request.session_id,
            "batch_mode": request.batch_mode
        })
        
        # 準備商品標籤
        print("🏷️ 準備商品標籤...")
        commodity_tags = []
        if stock_id:
            commodity_tag = CommodityTag(
                type="Stock",
                key=stock_id,
                bullOrBear=0  # 中性，可根據技術分析調整
            )
            commodity_tags.append(commodity_tag.model_dump())
        
        print(f"✅ 生成的商品標籤: {commodity_tags}")
        print(f"📊 股票代號: {stock_id}, 股票名稱: {stock_name}")
        print(f"👤 KOL序號: {request.kol_serial}")
        
        # 準備社群話題
        community_topic = None
        if request.post_to_thread:
            community_topic = CommunityTopic(id=request.post_to_thread)
            print(f"💬 社群話題: {request.post_to_thread}")
        
        # 準備生成參數 - 整合數據源資訊
        print("⚙️ 準備生成參數...")
        generation_params = GenerationParams(
            kol_persona=request.kol_persona,
            content_style=request.content_style,
            target_audience=request.target_audience,
            batch_mode=request.batch_mode,
            data_sources=[source.value for source in data_source_assignment.primary_sources],
            session_id=request.session_id,
            technical_indicators=[]
        )
        print("✅ 生成參數準備完成")
        
        # 創建貼文記錄
        print("💾 開始保存貼文記錄到資料庫...")
        try:
            # 轉換 commodity_tags 為 Pydantic 模型列表
            commodity_tag_models = []
            for tag_dict in commodity_tags:
                commodity_tag_models.append(CommodityTag(**tag_dict))
            
            post_record_data = PostRecordCreate(
                session_id=request.session_id or 0,
                kol_serial=int(request.kol_serial or "1"),
                kol_nickname=f"KOL-{request.kol_serial or '1'}",
                kol_persona=request.kol_persona,
                stock_code=stock_id,
                stock_name=stock_name,
                title=enhanced_content.get("title", f"{stock_name}分析"),
                content=enhanced_content.get("content_md", enhanced_content.get("content", "")),
                content_md=enhanced_content.get("content_md"),
                commodity_tags=commodity_tag_models,
                community_topic=community_topic,
                status="pending_review",  # 添加狀態
                generation_params=generation_params,
                topic_id=None,
                topic_title=None
            )
            
            print(f"📝 貼文記錄數據準備完成: {post_record_data.title}")
            print(f"🔍 貼文記錄數據詳情: session_id={post_record_data.session_id}, stock_code={post_record_data.stock_code}")
            
            # 保存到數據庫
            post_record = post_record_service.create_post_record(post_record_data)
            print(f"✅ 貼文記錄保存成功: {post_record.post_id}")
            print(f"🔍 數據庫中貼文總數: {len(post_record_service.db)}")
            
            # 更新enhanced_content包含post_id
            enhanced_content["post_id"] = post_record.post_id
            enhanced_content["status"] = "pending_review"
            
        except Exception as e:
            print(f"❌ 保存貼文記錄失敗: {e}")
            # 即使保存失敗也繼續返回結果
            enhanced_content["post_id"] = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            enhanced_content["status"] = "error"
        
        # 發文
        if request.auto_post:
            print("🚀 準備自動發文...")
            background_tasks = BackgroundTasks()
            background_tasks.add_task(post_to_platform, enhanced_content, {"id": request.post_to_thread})
            print("✅ 自動發文任務已加入背景任務")
        
        print(f"🎉 發文生成完成: {enhanced_content.get('post_id')}")
        
        return PostingResult(
            success=True,
            post_id=enhanced_content.get("post_id", f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            content=enhanced_content,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return PostingResult(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )

def generate_kol_content_direct(stock_id: str, stock_name: str, kol_persona: str, content_style: str, target_audience: str) -> Dict:
    """直接生成KOL內容 - 基於原本的盤後漲停腳本架構"""
    
    # KOL人設配置
    kol_personas = {
        "technical": {
            "name": "技術大師",
            "style": "專業且自信",
            "focus": "圖表分析、技術指標",
            "language": "技術術語豐富，數據導向"
        },
        "fundamental": {
            "name": "價值投資大師", 
            "style": "穩重且深思熟慮",
            "focus": "基本面分析、財報解讀",
            "language": "邏輯清晰，重視數據"
        },
        "news_driven": {
            "name": "新聞獵人",
            "style": "敏銳且即時", 
            "focus": "新聞影響、政策變化",
            "language": "生動活潑，時事導向"
        }
    }
    
    persona = kol_personas.get(kol_persona, kol_personas["technical"])
    
    # 生成標題 - 純文字格式
    title = f"{stock_name}({stock_id}) {persona['name']}觀點 - 技術面深度解析"
    
    # 生成內容 - 純文字格式
    content_md = f"""{stock_name}({stock_id}) 技術面分析報告

核心觀點
{stock_name} 目前處於強勢突破狀態，技術指標顯示多頭訊號確認。

關鍵技術指標
- MA5/MA20: 黃金交叉確認多頭趨勢
- RSI14: 中性偏多，仍有上漲空間
- MACD柱狀體: 多頭訊號持續

技術訊號分析
- 價漲量增：買盤力道強勁，後市看好
- 突破壓力：成功突破關鍵阻力位
- 趨勢確認：多頭排列完整

投資建議
基於技術分析，建議逢低布局，目標價位可期待10-15%漲幅。

風險提醒
- 注意大盤環境變化
- 設好停損點位
- 分批進場降低風險

操作策略
1. 進場時機: 回測支撐時分批買進
2. 停損設定: 跌破關鍵支撐位
3. 目標價位: 技術目標價位
4. 持股比例: 建議控制在總資產10%以內

以上分析僅供參考，投資有風險，請謹慎評估

數據來源
本分析整合了: 技術指標數據, 市場摘要分析, 熱門話題數據
"""
    
    return {
        "kol_id": f"kol_{persona['name']}",
        "kol_name": persona['name'],
        "stock_id": stock_id,
        "content_type": content_style,
        "title": title,
        "content_md": content_md,
        "key_points": [
            "技術面強勢突破",
            "多頭訊號確認", 
            "價漲量增格局",
            "逢低布局策略"
        ],
        "investment_advice": {
            "recommendation": "buy",
            "confidence": 0.8,
            "target_price": "技術目標價",
            "stop_loss": "關鍵支撐位"
        },
        "engagement_prediction": 0.75,
        "created_at": datetime.now().isoformat()
    }

def enhance_content_with_news(kol_content: Dict, topic: Dict, news_items: List[Dict]) -> Dict:
    """整合新聞素材到KOL內容中"""
    
    enhanced_content = kol_content.copy()
    
    # 確保 content_md 存在
    if "content_md" not in enhanced_content:
        enhanced_content["content_md"] = ""
    
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
        if "key_points" in enhanced_content:
            enhanced_content["key_points"].append("整合最新新聞素材")
        else:
            enhanced_content["key_points"] = ["整合最新新聞素材"]
    
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

# ==================== KOL憑證管理 ====================

class KOLCredentialManager:
    """KOL憑證管理器"""
    
    def __init__(self):
        # KOL憑證配置 (實際使用時應該從環境變量或數據庫讀取)
        self.kol_credentials = {
            "150": {"email": "forum_150@cmoney.com.tw", "password": "N9t1kY3x", "member_id": "150"},
            "151": {"email": "forum_151@cmoney.com.tw", "password": "m7C1lR4t", "member_id": "151"},
            "152": {"email": "forum_152@cmoney.com.tw", "password": "x2U9nW5p", "member_id": "152"},
            "153": {"email": "forum_153@cmoney.com.tw", "password": "y7O3cL9k", "member_id": "153"},
            "154": {"email": "forum_154@cmoney.com.tw", "password": "f4E9sC8w", "member_id": "154"},
            "155": {"email": "forum_155@cmoney.com.tw", "password": "Z5u6dL9o", "member_id": "155"},
            "156": {"email": "forum_156@cmoney.com.tw", "password": "T1t7kS9j", "member_id": "156"},
            "157": {"email": "forum_157@cmoney.com.tw", "password": "w2B3cF6l", "member_id": "157"},
            "158": {"email": "forum_158@cmoney.com.tw", "password": "q4N8eC7h", "member_id": "158"},
            "159": {"email": "forum_159@cmoney.com.tw", "password": "V5n6hK0f", "member_id": "159"},
            "160": {"email": "forum_160@cmoney.com.tw", "password": "D8k9mN2p", "member_id": "160"}
        }
        
        # Token快取
        self.kol_tokens = {}
        
        print("🔐 KOL憑證管理器初始化完成")
    
    def get_kol_credentials(self, kol_serial: str) -> Optional[Dict[str, str]]:
        """獲取KOL憑證"""
        return self.kol_credentials.get(str(kol_serial))
    
    async def login_kol(self, kol_serial: str) -> Optional[str]:
        """登入KOL並返回access token"""
        try:
            # 檢查是否已有有效token
            if kol_serial in self.kol_tokens:
                token_data = self.kol_tokens[kol_serial]
                if token_data.get('expires_at') and datetime.now() < token_data['expires_at']:
                    print(f"✅ 使用快取的KOL {kol_serial} token")
                    return token_data['token']
            
            # 獲取憑證
            creds = self.get_kol_credentials(kol_serial)
            if not creds:
                print(f"❌ 找不到KOL {kol_serial} 的憑證")
                return None
            
            print(f"🔐 開始登入KOL {kol_serial}...")
            
            # 使用CMoney Client登入
            from serper_integration import serper_service
            if hasattr(serper_service, 'cmoney_client'):
                cmoney_client = serper_service.cmoney_client
            else:
                # 如果沒有CMoney client，創建一個
                from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
                cmoney_client = CMoneyClient()
            
            from src.clients.cmoney.cmoney_client import LoginCredentials
            credentials = LoginCredentials(
                email=creds['email'],
                password=creds['password']
            )
            
            access_token = await cmoney_client.login(credentials)
            
            if access_token and access_token.token:
                # 快取token
                self.kol_tokens[kol_serial] = {
                    'token': access_token.token,
                    'expires_at': access_token.expires_at
                }
                print(f"✅ KOL {kol_serial} 登入成功")
                return access_token.token
            else:
                print(f"❌ KOL {kol_serial} 登入失敗")
                return None
                
        except Exception as e:
            print(f"❌ KOL {kol_serial} 登入異常: {e}")
            return None

# 全域KOL憑證管理器
kol_credential_manager = KOLCredentialManager()


@app.get("/posts")
async def get_all_posts(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """獲取所有貼文"""
    try:
        posts = post_record_service.get_all_posts()
        
        # 根據狀態篩選
        if status:
            posts = [post for post in posts if post.status == status]
        
        # 分頁
        total = len(posts)
        posts = posts[skip:skip + limit]
        
        return {
            "posts": posts,
            "count": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        print(f"獲取貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取貼文失敗: {str(e)}")

@app.get("/posts/pending-review")
async def get_pending_review_posts():
    """獲取待審核的貼文列表"""
    try:
        posts = post_record_service.get_pending_review_posts()
        print(f"找到 {len(posts)} 篇待審核貼文")
        for post in posts:
            print(f"  - {post.post_id}: {post.title} (狀態: {post.status})")
        
        return {
            "success": True,
            "posts": posts,
            "count": len(posts),
            "timestamp": datetime.now()
        }
    except Exception as e:
        print(f"獲取待審核貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/serper/test")
async def test_serper_api():
    """測試Serper API連接"""
    try:
        print("🔍 測試Serper API連接...")
        
        # 檢查環境變數
        serper_api_key = os.getenv('SERPER_API_KEY')
        print(f"🔑 SERPER_API_KEY 狀態: {'已設定' if serper_api_key else '未設定'}")
        
        if not serper_api_key:
            return {
                "success": False,
                "error": "SERPER_API_KEY 環境變數未設定",
                "timestamp": datetime.now().isoformat()
            }
        
        # 測試API連接
        from serper_integration import serper_service
        
        # 測試搜尋功能
        test_result = serper_service.search_stock_news("2330", "台積電", limit=2)
        
        return {
            "success": True,
            "api_key_configured": True,
            "test_query": "台積電 2330 新聞 最新",
            "results_count": len(test_result),
            "sample_results": test_result[:2] if test_result else [],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Serper API測試失敗: {e}")
        return {
            "success": False,
            "error": str(e),
            "api_key_configured": bool(os.getenv('SERPER_API_KEY')),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/posts/debug")
async def debug_posts():
    """調試端點：檢查所有貼文"""
    try:
        # 獲取所有貼文
        all_posts = post_record_service.get_all_posts()
        print(f"資料庫中共有 {len(all_posts)} 篇貼文")
        
        # 按狀態分組
        status_groups = {}
        for post in all_posts:
            status = str(post.status)  # 直接轉換為字符串
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(post)
        
        print("按狀態分組:")
        for status, posts in status_groups.items():
            print(f"  {status}: {len(posts)} 篇")
            for post in posts[:3]:  # 只顯示前3篇
                print(f"    - {post.post_id}: {post.title}")
        
        return {
            "success": True,
            "total_posts": len(all_posts),
            "posts_by_status": {status: len(posts) for status, posts in status_groups.items()},
            "posts": all_posts,
            "timestamp": datetime.now()
        }
    except Exception as e:
        print(f"調試貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/data-source-assignment")
async def debug_data_source_assignment():
    """調試數據源分配功能"""
    try:
        from smart_data_source_assigner import smart_assigner, KOLProfile, StockProfile
        
        # 測試KOL配置
        test_kol = KOLProfile(
            serial=150,
            nickname="測試KOL",
            persona="technical",
            expertise_areas=["技術分析"],
            content_style="chart_analysis",
            target_audience="active_traders"
        )
        
        # 測試股票配置
        test_stock = StockProfile(
            stock_code="2208",
            stock_name="台船",
            industry="航運",
            market_cap="medium",
            volatility="high",
            news_frequency="high"
        )
        
        # 執行數據源分配
        assignment = smart_assigner.assign_data_sources(
            kol_profile=test_kol,
            stock_profile=test_stock,
            batch_context={'trigger_type': 'after_hours_limit_up'}
        )
        
        return {
            "success": True,
            "kol_profile": {
                "serial": test_kol.serial,
                "nickname": test_kol.nickname,
                "persona": test_kol.persona
            },
            "stock_profile": {
                "stock_code": test_stock.stock_code,
                "stock_name": test_stock.stock_name,
                "market_cap": test_stock.market_cap,
                "volatility": test_stock.volatility
            },
            "data_source_assignment": {
                "primary_sources": [source.value for source in assignment.primary_sources],
                "secondary_sources": [source.value for source in assignment.secondary_sources],
                "excluded_sources": [source.value for source in assignment.excluded_sources],
                "assignment_reason": assignment.assignment_reason,
                "confidence_score": assignment.confidence_score
            }
        }
        
    except Exception as e:
        print(f"❌ 數據源分配調試失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/debug/data-source-usage")
async def debug_data_source_usage():
    """調試數據源實際使用情況"""
    try:
        # 獲取最近的貼文
        all_posts = post_record_service.get_all_posts()
        recent_posts = sorted(all_posts, key=lambda x: x.created_at, reverse=True)[:5]
        
        usage_analysis = []
        
        for post in recent_posts:
            # 解析生成參數
            generation_params = post.generation_params or {}
            if hasattr(generation_params, '__dict__'):
                generation_params = generation_params.__dict__
            
            data_sources = generation_params.get('data_sources', {})
            smart_assigned = generation_params.get('smart_assigned', [])
            assignment_reason = generation_params.get('assignment_reason', '')
            
            usage_analysis.append({
                "post_id": post.post_id,
                "title": post.title,
                "stock_code": post.stock_code,
                "kol_serial": post.kol_serial,
                "generation_params": {
                    "data_sources": data_sources,
                    "smart_assigned": smart_assigned,
                    "assignment_reason": assignment_reason
                },
                "content_preview": post.content[:200] + "..." if len(post.content) > 200 else post.content
            })
        
        return {
            "success": True,
            "total_posts": len(all_posts),
            "recent_posts_analysis": usage_analysis,
            "data_source_summary": {
                "smart_assignment_used": sum(1 for post in recent_posts 
                                           if post.generation_params and 
                                           hasattr(post.generation_params, 'smart_assigned')),
                "batch_data_sources_used": sum(1 for post in recent_posts 
                                              if post.generation_params and 
                                              hasattr(post.generation_params, 'data_sources')),
                "assignment_reasons_count": len(set(getattr(post.generation_params, 'assignment_reason', '') 
                                                   for post in recent_posts 
                                                   if post.generation_params))
            }
        }
        
    except Exception as e:
        print(f"❌ 數據源使用情況調試失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/posts/session/{session_id}")
async def get_session_posts(session_id: int, status: Optional[str] = None):
    """獲取會話的所有貼文"""
    try:
        print(f"🔍 獲取會話貼文: session_id={session_id}, status={status}")
        posts = post_record_service.get_session_posts(session_id, status)
        print(f"✅ 找到 {len(posts)} 篇貼文")
        return {
            "success": True,
            "posts": posts,
            "count": len(posts),
            "timestamp": datetime.now()
        }
    except Exception as e:
        print(f"❌ 獲取會話貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post/batch-generate-stream")
async def batch_generate_posts_stream(request: BatchPostRequest):
    """
    批量生成貼文 - 使用Server-Sent Events一則一則回傳
    """
    print(f"🚀 開始批量發文生成 - 會話ID: {request.session_id}, 貼文數量: {len(request.posts)}")
    
    async def generate_posts():
        total_posts = len(request.posts)
        successful_posts = 0
        failed_posts = 0
        
        print(f"📊 批量生成統計: 總數={total_posts}, 成功={successful_posts}, 失敗={failed_posts}")
        
        # 發送開始事件
        yield f"data: {json.dumps({'type': 'batch_start', 'total': total_posts, 'session_id': request.session_id})}\n\n"
        
        for index, post_data in enumerate(request.posts):
            try:
                print(f"📝 開始生成第 {index + 1}/{total_posts} 篇貼文...")
                
                # 發送進度事件
                progress = {
                    'type': 'progress',
                    'current': index + 1,
                    'total': total_posts,
                    'percentage': round((index + 1) / total_posts * 100, 1),
                    'successful': successful_posts,
                    'failed': failed_posts
                }
                yield f"data: {json.dumps(progress)}\n\n"
                
                # 為每個貼文智能分配數據源
                print(f"🧠 為第 {index + 1} 篇貼文智能分配數據源...")
                
                # 創建KOL和股票配置
                kol_profile = KOLProfile(
                    serial=int(post_data.get('kol_serial', 150)),
                    nickname=f"KOL-{post_data.get('kol_serial', 150)}",
                    persona=request.batch_config.get('kol_persona', 'technical'),
                    expertise_areas=[],
                    content_style=request.batch_config.get('content_style', 'chart_analysis'),
                    target_audience=request.batch_config.get('target_audience', 'active_traders')
                )
                
                stock_profile = StockProfile(
                    stock_code=post_data.get('stock_code'),
                    stock_name=post_data.get('stock_name'),
                    industry='unknown',
                    market_cap='medium',  # 預設中等市值
                    volatility='medium',  # 預設中等波動
                    news_frequency='medium'  # 預設中等新聞頻率
                )
                
                # 智能分配數據源
                data_source_assignment = smart_assigner.assign_data_sources(
                    kol_profile=kol_profile,
                    stock_profile=stock_profile,
                    batch_context={'trigger_type': 'manual_batch'}
                )
                
                # 合併智能分配的數據源和批次配置的數據源
                smart_sources = [source.value for source in data_source_assignment.primary_sources]
                batch_sources = request.data_sources or {}
                
                # 創建混合數據源配置 - 優先使用智能分配的數據源
                hybrid_data_sources = {
                    **batch_sources,  # 批次配置的數據源
                    'smart_assigned': smart_sources,  # 智能分配的數據源
                    'assignment_reason': data_source_assignment.assignment_reason,
                    'confidence_score': data_source_assignment.confidence_score
                }
                
                # 如果智能分配有數據源，優先使用智能分配的
                if smart_sources:
                    # 將智能分配的數據源設為主要數據源
                    for source in smart_sources:
                        if source == 'ohlc_api':
                            hybrid_data_sources['stock_price_api'] = True
                        elif source == 'revenue_api':
                            hybrid_data_sources['monthly_revenue_api'] = True
                        elif source == 'fundamental_api':
                            hybrid_data_sources['fundamental_data'] = ['財報']
                        elif source == 'serper_api':
                            hybrid_data_sources['news_sources'] = ['工商時報', '經濟日報', '中央社']
                        elif source == 'summary_api':
                            hybrid_data_sources['technical_indicators'] = ['MACD', 'RSI', '移動平均線']
                
                print(f"📊 數據源分配: 智能={smart_sources}, 批次={list(batch_sources.keys())}")
                
                # 生成單個貼文
                post_request = PostingRequest(
                    stock_code=post_data.get('stock_code'),
                    stock_name=post_data.get('stock_name'),
                    kol_serial=post_data.get('kol_serial'),
                    kol_persona=request.batch_config.get('kol_persona', 'technical'),
                    content_style=request.batch_config.get('content_style', 'chart_analysis'),
                    target_audience=request.batch_config.get('target_audience', 'active_traders'),
                    batch_mode=True,
                    session_id=request.session_id,
                    data_sources=hybrid_data_sources,  # 使用混合數據源
                    explainability_config=request.explainability_config,
                    news_config=request.news_config
                )
                
                print(f"⚙️ 調用單個貼文生成API...")
                result = await manual_post_content(post_request)
                print(f"✅ 第 {index + 1} 篇貼文生成完成: {result.success}")
                
                # 發送貼文生成完成事件
                post_response = {
                    'type': 'post_generated',
                    'success': result.success,
                    'post_id': result.post_id,
                    'content': result.content,
                    'error': result.error,
                    'timestamp': result.timestamp.isoformat(),
                    'progress': {
                        'current': index + 1,
                        'total': total_posts,
                        'percentage': round((index + 1) / total_posts * 100, 1)
                    }
                }
                
                if result.success:
                    successful_posts += 1
                    print(f"✅ 第 {index + 1} 篇貼文生成成功: {result.post_id}")
                else:
                    failed_posts += 1
                    print(f"❌ 第 {index + 1} 篇貼文生成失敗: {result.error}")
                
                yield f"data: {json.dumps(post_response)}\n\n"
                
                # 添加延遲，避免過於頻繁的請求
                await asyncio.sleep(0.5)
                
            except Exception as e:
                failed_posts += 1
                print(f"❌ 第 {index + 1} 篇貼文生成異常: {e}")
                error_response = {
                    'type': 'post_error',
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'progress': {
                        'current': index + 1,
                        'total': total_posts,
                        'percentage': round((index + 1) / total_posts * 100, 1)
                    }
                }
                yield f"data: {json.dumps(error_response)}\n\n"
        
        # 發送完成事件
        print(f"🎉 批量生成完成: 總數={total_posts}, 成功={successful_posts}, 失敗={failed_posts}")
        final_result = {
            'type': 'batch_complete',
            'total': total_posts,
            'successful': successful_posts,
            'failed': failed_posts,
            'session_id': request.session_id,
            'timestamp': datetime.now().isoformat()
        }
        yield f"data: {json.dumps(final_result)}\n\n"
    
    return StreamingResponse(
        generate_posts(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/posts/{post_id}/approve")
async def approve_post(post_id: str, request: Request):
    """審核通過貼文"""
    logger.info(f"🔍 開始處理貼文審核請求 - Post ID: {post_id}")
    
    try:
        # 記錄請求詳情
        logger.info(f"📝 審核請求詳情 - Post ID: {post_id}")
        
        # 檢查貼文是否存在
        existing_post = post_record_service.get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {len(post_record_service.db)}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: {list(post_record_service.db.keys())}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 解析請求內容
        body = await request.json()
        reviewer_notes = body.get("reviewer_notes")
        approved_by = body.get("approved_by", "system")
        
        logger.info(f"📝 審核參數 - 審核者: {approved_by}, 備註: {reviewer_notes}")
        
        # 創建更新資料
        update_data = PostRecordUpdate(
            status="approved",
            reviewer_notes=reviewer_notes,
            approved_by=approved_by,
            approved_at=datetime.now()
        )
        
        logger.info(f"🔄 開始更新貼文狀態 - Post ID: {post_id}")
        
        # 更新貼文記錄
        post_record = post_record_service.update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文審核成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            logger.info(f"📊 更新後資料庫狀態 - 總貼文數: {len(post_record_service.db)}")
            
            return {
                "success": True,
                "message": "貼文審核通過",
                "post": {
                    "post_id": post_record.post_id,
                    "status": post_record.status,
                    "approved_by": post_record.approved_by,
                    "approved_at": post_record.approved_at.isoformat() if post_record.approved_at else None,
                    "reviewer_notes": post_record.reviewer_notes
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新貼文失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}, 詳情: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ 審核貼文時發生未預期錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        logger.error(f"🔍 錯誤類型: {type(e).__name__}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"審核失敗: {str(e)}")

@app.post("/posts/{post_id}/reject")
async def reject_post(post_id: str, request: Request):
    """拒絕貼文"""
    logger.info(f"🔍 開始處理貼文拒絕請求 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = post_record_service.get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {len(post_record_service.db)}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: {list(post_record_service.db.keys())}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 解析請求內容
        body = await request.json()
        reviewer_notes = body.get("reviewer_notes", "拒絕")
        
        logger.info(f"📝 拒絕參數 - 備註: {reviewer_notes}")
        
        # 創建更新資料
        update_data = PostRecordUpdate(
            status="rejected",
            reviewer_notes=reviewer_notes,
            approved_by="system"
        )
        
        logger.info(f"🔄 開始更新貼文狀態為拒絕 - Post ID: {post_id}")
        
        # 更新貼文記錄
        post_record = post_record_service.update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文拒絕成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            return {
                "success": True,
                "message": "貼文已拒絕",
                "post": {
                    "post_id": post_record.post_id,
                    "status": post_record.status,
                    "reviewer_notes": post_record.reviewer_notes
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新貼文失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}, 詳情: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ 拒絕貼文時發生未預期錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"拒絕失敗: {str(e)}")

@app.post("/posts/{post_id}/publish")
async def publish_post_to_cmoney(post_id: str, cmoney_config: Optional[Dict[str, Any]] = None):
    """發布貼文到CMoney"""
    try:
        # 獲取貼文記錄
        post_record = post_record_service.get_post_record(post_id)
        if not post_record:
            raise HTTPException(status_code=404, detail="貼文不存在")
        
        if post_record.status != "approved":
            raise HTTPException(status_code=400, detail="只有已審核的貼文才能發布")
        
        # 使用發佈服務發佈貼文
        from publish_service import publish_service
        publish_result = await publish_service.publish_post(post_record)
        
        # 更新貼文狀態為published
        update_data = PostRecordUpdate(
            status="published",
            published_at=datetime.now(),
            cmoney_post_id=publish_result["post_id"],
            cmoney_post_url=publish_result["post_url"]
        )
        
        updated_post = post_record_service.update_post_record(post_id, update_data)
        
        return publish_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"發布失敗: {e}")
        return {
            "success": False,
            "error": str(e),
            "post_id": post_id,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    """獲取單個貼文詳情"""
    logger.info(f"🔍 獲取貼文請求 - Post ID: {post_id}")
    
    try:
        post_record = post_record_service.get_post_record(post_id)
        if post_record:
            logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 狀態: {post_record.status}")
            
            # 將貼文記錄轉換為可序列化的字典
            post_data = {
                "post_id": post_record.post_id,
                "session_id": post_record.session_id,
                "kol_serial": post_record.kol_serial,
                "kol_nickname": post_record.kol_nickname,
                "kol_persona": post_record.kol_persona,
                "stock_code": post_record.stock_code,
                "stock_name": post_record.stock_name,
                "title": post_record.title,
                "content": post_record.content,
                "content_md": post_record.content_md,
                "status": post_record.status,
                "quality_score": post_record.quality_score,
                "ai_detection_score": post_record.ai_detection_score,
                "risk_level": post_record.risk_level,
                "reviewer_notes": post_record.reviewer_notes,
                "approved_by": post_record.approved_by,
                "approved_at": post_record.approved_at.isoformat() if post_record.approved_at else None,
                "scheduled_at": post_record.scheduled_at.isoformat() if post_record.scheduled_at else None,
                "published_at": post_record.published_at.isoformat() if post_record.published_at else None,
                "cmoney_post_id": post_record.cmoney_post_id,
                "cmoney_post_url": post_record.cmoney_post_url,
                "publish_error": post_record.publish_error,
                "views": post_record.views,
                "likes": post_record.likes,
                "comments": post_record.comments,
                "shares": post_record.shares,
                "topic_id": post_record.topic_id,
                "topic_title": post_record.topic_title,
                "created_at": post_record.created_at.isoformat() if post_record.created_at else None,
                "updated_at": post_record.updated_at.isoformat() if post_record.updated_at else None
            }
            
            return {
                "success": True,
                "post": post_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 獲取貼文時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"獲取貼文失敗: {str(e)}")

# ==================== 新增的內容生成函數 ====================

def generate_kol_content_with_serper(stock_id: str, stock_name: str, kol_persona: str, 
                                    content_style: str, target_audience: str,
                                    serper_analysis: Dict[str, Any],
                                    data_sources: List[str]) -> Dict[str, Any]:
    """使用Serper數據生成KOL內容"""
    
    try:
        # 提取Serper數據
        news_items = serper_analysis.get('news_items', [])
        limit_up_analysis = serper_analysis.get('limit_up_analysis', {})
        limit_up_reasons = limit_up_analysis.get('limit_up_reasons', [])
        key_events = limit_up_analysis.get('key_events', [])
        market_sentiment = limit_up_analysis.get('market_sentiment', 'neutral')
        
        # 構建增強版Prompt
        prompt_parts = []
        
        # 1. 基本分析框架 - 純文字格式
        prompt_parts.append(f"{stock_name}({stock_id}) 深度分析報告")
        prompt_parts.append("")
        prompt_parts.append("核心觀點")
        prompt_parts.append("")
        
        # 2. 整合漲停原因分析
        if limit_up_reasons:
            prompt_parts.append(f"基於最新市場資訊，{stock_name} 目前處於強勢上漲狀態：")
            for reason in limit_up_reasons[:2]:  # 取前2個原因
                prompt_parts.append(f"- {reason['title']}: {reason['snippet'][:150]}")
        else:
            prompt_parts.append(f"{stock_name} 目前處於技術面強勢狀態，多項指標顯示上漲動能。")
        
        prompt_parts.append("")
        
        # 3. 技術分析部分
        if 'ohlc_api' in data_sources:
            prompt_parts.append("技術面分析")
            prompt_parts.append("- MA5/MA20: 黃金交叉確認多頭趨勢")
            prompt_parts.append("- RSI14: 中性偏多，仍有上漲空間")
            prompt_parts.append("- MACD柱狀體: 多頭訊號持續")
            prompt_parts.append("")
        
        # 4. 基本面分析部分
        if 'fundamental_api' in data_sources:
            prompt_parts.append("基本面分析")
            if key_events:
                prompt_parts.append("關鍵事件分析:")
                for event in key_events[:2]:
                    prompt_parts.append(f"- {event['event']}: {event['description'][:100]}")
            else:
                prompt_parts.append("- 財務指標穩健，營收成長動能強勁")
                prompt_parts.append("- 產業前景看好，長期投資價值顯現")
            prompt_parts.append("")
        
        # 5. 新聞整合部分
        if news_items and 'serper_api' in data_sources:
            prompt_parts.append("市場動態")
            prompt_parts.append("最新市場資訊:")
            for news in news_items[:2]:  # 取前2則新聞
                prompt_parts.append(f"- {news['title']}: {news['snippet'][:150]}")
            prompt_parts.append("")
        
        # 6. 投資建議
        prompt_parts.append("投資建議")
        if market_sentiment == 'positive':
            prompt_parts.append("基於技術面和基本面分析，建議積極布局，目標價位可期待15-20%漲幅。")
        elif market_sentiment == 'negative':
            prompt_parts.append("雖然技術面強勢，但需注意基本面風險，建議謹慎操作，設好停損點位。")
        else:
            prompt_parts.append("基於綜合分析，建議逢低布局，目標價位可期待10-15%漲幅。")
        prompt_parts.append("")
        
        # 7. 風險提醒
        prompt_parts.append("風險提醒")
        prompt_parts.append("- 注意大盤環境變化")
        prompt_parts.append("- 設好停損點位")
        prompt_parts.append("- 分批進場降低風險")
        prompt_parts.append("")
        
        # 8. 操作策略
        prompt_parts.append("操作策略")
        prompt_parts.append("1. 進場時機: 回測支撐時分批買進")
        prompt_parts.append("2. 停損設定: 跌破關鍵支撐位")
        prompt_parts.append("3. 目標價位: 技術目標價位")
        prompt_parts.append("4. 持股比例: 建議控制在總資產10%以內")
        
        # 9. 免責聲明
        prompt_parts.append("")
        prompt_parts.append("以上分析僅供參考，投資有風險，請謹慎評估")
        prompt_parts.append("")
        
        # 10. 數據來源標註
        prompt_parts.append("數據來源")
        data_source_names = {
            'ohlc_api': '技術指標數據',
            'serper_api': '最新新聞資訊',
            'fundamental_api': '基本面數據',
            'summary_api': '市場摘要分析',
            'revenue_api': '營收數據',
            'financial_api': '財務數據'
        }
        used_sources = [data_source_names.get(source, source) for source in data_sources]
        prompt_parts.append(f"本分析整合了: {', '.join(used_sources)}")
        
        # 組合完整內容
        content_md = "\n".join(prompt_parts)
        
        # 生成標題 - 純文字格式
        title = f"{stock_name}({stock_id}) {kol_persona.title()}觀點 - 深度市場解析"
        
        return {
            "title": title,
            "content": content_md,
            "content_md": content_md,
            "stock_id": stock_id,
            "stock_name": stock_name,
            "kol_persona": kol_persona,
            "content_style": content_style,
            "target_audience": target_audience,
            "data_sources": data_sources,
            "serper_integration": True,
            "news_count": len(news_items),
            "market_sentiment": market_sentiment,
            "generation_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Serper內容生成失敗: {e}")
        # 回退到基本內容生成
        return generate_kol_content_direct(stock_id, stock_name, kol_persona, content_style, target_audience)

def enhance_content_with_serper_data(kol_content: Dict[str, Any], 
                                   serper_analysis: Dict[str, Any],
                                   data_source_assignment) -> Dict[str, Any]:
    """使用Serper數據增強內容"""
    
    try:
        enhanced_content = kol_content.copy()
        
        # 獲取新聞數據
        news_items = serper_analysis.get('news_items', [])
        limit_up_analysis = serper_analysis.get('limit_up_analysis', {})
        
        # 如果有新聞數據，整合到內容中
        if news_items:
            print(f"🔗 整合 {len(news_items)} 則新聞到內容中")
            
            # 提取新聞摘要和連結
            news_summary = []
            for i, news in enumerate(news_items[:3]):  # 只取前3則新聞
                title = news.get('title', '')
                snippet = news.get('snippet', '')
                link = news.get('link', '')
                if title and snippet:
                    if link:
                        news_summary.append(f"📰 {title}: {snippet[:100]}...\n   [閱讀更多]({link})")
                    else:
                        news_summary.append(f"📰 {title}: {snippet[:100]}...")
            
            # 整合新聞到內容中
            original_content = enhanced_content.get('content', '')
            original_content_md = enhanced_content.get('content_md', '')
            
            # 添加新聞資訊到內容開頭
            news_section = ""
            if news_summary:
                news_section = "📰 **最新消息**\n\n" + "\n".join(news_summary) + "\n\n"
            
            # 如果有漲停分析，也加入
            if limit_up_analysis:
                analysis_section = ""
                if limit_up_analysis.get('market_sentiment'):
                    sentiment = limit_up_analysis.get('market_sentiment', 'neutral')
                    analysis_section += f"📊 **市場情緒**: {sentiment}\n\n"
                
                if limit_up_analysis.get('key_factors'):
                    factors = limit_up_analysis.get('key_factors', [])
                    if factors:
                        analysis_section += f"🔍 **關鍵因素**: {', '.join(factors[:3])}\n\n"
                
                news_section += analysis_section
            
            # 更新內容
            enhanced_content['content'] = news_section + original_content
            enhanced_content['content_md'] = news_section + original_content_md
            
            print(f"✅ 新聞整合完成，內容長度: {len(enhanced_content['content'])} 字")
        
        # 添加Serper數據到內容中
        enhanced_content.update({
            "serper_data": serper_analysis,
            "data_source_assignment": {
                "primary_sources": [source.value for source in data_source_assignment.primary_sources],
                "secondary_sources": [source.value for source in data_source_assignment.secondary_sources],
                "assignment_reason": data_source_assignment.assignment_reason,
                "confidence_score": data_source_assignment.confidence_score
            },
            "news_integration": True,
            "limit_up_analysis": limit_up_analysis,
            "market_sentiment": limit_up_analysis.get('market_sentiment', 'neutral')
        })
        
        return enhanced_content
        
    except Exception as e:
        print(f"Serper數據增強失敗: {e}")
        return kol_content

print("🎉 所有模組載入完成！")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

