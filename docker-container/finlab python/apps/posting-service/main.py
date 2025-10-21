import os
import requests
import json
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import sys
import json
from dotenv import load_dotenv
import logging
import pytz

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 設置日誌 - 允許 INFO 級別以顯示排程啟動日誌
# 強制覆蓋環境變數 LOG_LEVEL=INFO
import os
os.environ['LOG_LEVEL'] = 'INFO'

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

# 強制關閉 SQLAlchemy 的 SQL 查詢日誌
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.orm').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

# 強制設置根日誌級別
logging.getLogger().setLevel(logging.WARNING)

# 導入改進的內容生成器
from improved_content_generator import generate_improved_kol_content
# 導入GPT內容生成器
from gpt_content_generator import gpt_generator
# 導入互動內容生成器
# from interaction_content_generator import generate_interaction_content  # 暫時註解，模組不存在

# 載入環境變數
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

# 使用PostgreSQL服務
from postgresql_service import PostgreSQLPostRecordService
# 導入數據模型 (CommodityTag 將在需要時動態導入)
try:
    from post_record_service import CommunityTopic, GenerationParams, PostRecordCreate, PostRecordUpdate
except ImportError as e:
    print(f"❌ 數據模型導入失敗: {e}")

# 導入 asyncio 模組
import asyncio

app = FastAPI(
    title="Posting Service", 
    description="虛擬KOL自動發文服務"
)

# 🔥 使用舊版本的啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    print("🚀🚀🚀 STARTUP 事件被調用！🚀🚀🚀")
    print("🚀🚀🚀 FastAPI 應用開始啟用 🚀🚀🚀")
    
    # 啟動時的邏輯
    logger.info("🚀🚀🚀 FastAPI 應用開始啟用 🚀🚀🚀")
    logger.info("📋 正在初始化各項服務...")
    print("📋 正在初始化各項服務...")
    
    # 🔥 TEMPORARILY DISABLED: posting-service background scheduler
    # TODO: Fix time check logic before re-enabling
    # The background scheduler was executing all active schedules continuously
    # Disabled to prevent infinite loop execution
    logger.warning("⚠️  排程服務背景任務已暫時停用 - 需修復時間檢查邏輯")
    print("⚠️  排程服務背景任務已暫時停用 - 需修復時間檢查邏輯")

    # try:
    #     # 🔥 重新啟用排程服務
    #     logger.info("🚀🚀🚀 開始啟動排程服務背景任務 🚀🚀🚀")
    #     logger.info("📋 正在導入排程服務模組...")
    #     print("🚀🚀🚀 開始啟動排程服務背景任務 🚀🚀🚀")
    #
    #     try:
    #         from schedule_service import schedule_service
    #         logger.info("✅ 排程服務模組導入成功")
    #         print("✅ 排程服務模組導入成功")
    #
    #         logger.info("🔄 正在創建背景排程任務...")
    #         print("🔄 正在創建背景排程任務...")
    #         background_task = asyncio.create_task(schedule_service.start_background_scheduler())
    #         app.state.background_scheduler_task = background_task
    #         logger.info("✅ 背景排程任務創建成功")
    #         print("✅ 背景排程任務創建成功")
    #
    #         logger.info("✅ ✅ ✅ 排程服務已啟動，API 服務已啟動 ✅ ✅ ✅")
    #         print("✅ ✅ ✅ 排程服務已啟動，API 服務已啟動 ✅ ✅ ✅")
    #
    #     except Exception as import_error:
    #         logger.error(f"❌ 排程服務模組導入或啟動失敗: {import_error}")
    #         logger.error(f"🔍 導入錯誤詳情: {str(import_error)}")
    #         print(f"❌ 排程服務模組導入或啟動失敗: {import_error}")
    #         import traceback
    #         logger.error(f"🔍 導入錯誤堆疊:\n{traceback.format_exc()}")
    #         print(f"🔍 導入錯誤堆疊:\n{traceback.format_exc()}")
    #         raise
    #
    # except Exception as e:
    #     logger.error(f"❌ 排程服務啟動失敗: {e}")
    #     logger.error(f"🔍 錯誤詳情: {str(e)}")
    #     print(f"❌ 排程服務啟動失敗: {e}")
    #     import traceback
    #     traceback.print_exc()

    logger.info("🎉 所有服務初始化完成！應用開始運行...")
    print("🎉 所有服務初始化完成！應用開始運行...")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    print("🛑 應用正在關閉...")
    logger.info("🛑 應用正在關閉...")
    try:
        # 清理背景任務
        if hasattr(app.state, 'background_scheduler_task'):
            logger.info("🔄 正在停止背景排程器...")
            print("🔄 正在停止背景排程器...")
            app.state.background_scheduler_task.cancel()
            try:
                await app.state.background_scheduler_task
            except asyncio.CancelledError:
                logger.info("✅ 背景排程器已停止")
                print("✅ 背景排程器已停止")
    except Exception as e:
        logger.error(f"❌ 關閉服務時發生錯誤: {e}")
        print(f"❌ 關閉服務時發生錯誤: {e}")
    
    logger.info("🏁 應用關閉完成")
    print("🏁 應用關閉完成")

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由模組
from routes import main_router
from routes.schedule_routes_simple import router as schedule_router
app.include_router(main_router)
app.include_router(schedule_router, prefix="/api/schedule")

# API 端點配置
TRENDING_API_URL = os.getenv("TRENDING_API_URL", "http://localhost:8004")
SUMMARY_API_URL = os.getenv("SUMMARY_API_URL", "http://summary-api:8003")
OHLC_API_URL = os.getenv("OHLC_API_URL", "http://ohlc-api:8001")

# 初始化PostgreSQL數據庫服務
# 延遲初始化，避免啟動時連接數據庫
post_record_service = None

def get_post_record_service():
    """獲取PostgreSQL服務實例（延遲初始化）"""
    global post_record_service
    if post_record_service is None:
        post_record_service = PostgreSQLPostRecordService()
    return post_record_service

def _extract_stock_from_keywords(keywords: str) -> dict:
    """從關鍵詞中提取股票信息"""
    if not keywords:
        return None
    
    # 股票名稱到代碼的映射
    stock_mapping = {
        "正達": "3149",
        "茂矽": "2342", 
        "環球晶": "6488",
        "中美晶": "5483",
        "合晶": "6182",
        "嘉晶": "3016",
        "漢磊": "3707",
        "世界": "5347",
        "力積電": "6770",
        "南亞科": "2408",
        "華邦電": "2344",
        "旺宏": "2337",
        "群聯": "8299",
        "慧榮": "2379",
        "瑞昱": "2379",
        "聯詠": "3034",
        "矽力": "6415",
        "譜瑞": "4966",
        "祥碩": "5269",
        "信驊": "5274",
        "創意": "3443",
        "世芯": "3661",
        "智原": "3035",
        "力旺": "3529",
        "台勝科": "3532",
        "台積電": "2330",
        "聯發科": "2454", 
        "鴻海": "2317",
        "中華電": "2412",
        "台塑": "1301",
        "中鋼": "2002",
        "長榮": "2603",
        "陽明": "2609",
        "萬海": "2615",
        "富邦金": "2881"
    }
    
    # 檢查關鍵詞中是否包含股票名稱
    for stock_name, stock_code in stock_mapping.items():
        if stock_name in keywords:
            logger.info(f"🎯 在關鍵詞中找到股票: {stock_name}({stock_code})")
            return {
                "name": stock_name,
                "code": stock_code
            }
    
    logger.info(f"⚠️ 在關鍵詞中未找到已知股票: {keywords}")
    return None

class PostingRequest(BaseModel):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    
    @validator('stock_name', pre=True)
    def validate_stock_name(cls, v):
        """驗證 stock_name 字段，如果是對象則提取 company_name"""
        if isinstance(v, dict):
            # 如果是對象，提取 company_name 字段
            company_name = v.get('company_name')
            if company_name:
                return company_name
            # 如果沒有 company_name，嘗試其他可能的字段
            return v.get('name', v.get('stock_name', str(v)))
        return v
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
    max_words: int = 1000
    # 新增數據源相關欄位
    data_sources: Optional[Dict[str, Any]] = None
    # 新聞時間範圍設定
    news_time_range: Optional[str] = "d2"
    explainability_config: Optional[Dict[str, Any]] = None
    news_config: Optional[Dict[str, Any]] = None
    # 新增話題相關欄位
    topic_title: Optional[str] = None
    topic_keywords: Optional[str] = None
    kol_nickname: Optional[str] = None
    # 標籤配置
    tags_config: Optional[Dict[str, Any]] = None
    # 共享 commodity tags (用於批量生成)
    shared_commodity_tags: Optional[List[Dict[str, Any]]] = None
    # 熱門話題相關欄位
    topic_id: Optional[str] = None
    topic_title: Optional[str] = None
    # 發文類型
    posting_type: Optional[str] = 'analysis'  # analysis/interaction
    # 觸發器類型
    trigger_type: Optional[str] = None
    
    # 新增：百分比配置欄位
    article_type_distribution: Optional[Dict[str, int]] = None
    content_length_distribution: Optional[Dict[str, int]] = None
    content_style_distribution: Optional[Dict[str, int]] = None
    analysis_depth_distribution: Optional[Dict[str, int]] = None
    include_charts: Optional[bool] = None
    include_risk_warning: Optional[bool] = None
    
    # 新增：生成模式和廢文情感傾向
    generation_mode: Optional[str] = "high_quality"
    trash_sentiment: Optional[str] = "positive"
    
    # 新增：新聞連結配置
    enable_news_links: Optional[bool] = True
    news_max_links: Optional[int] = 5
    # 新增：發文類型 (analysis/interaction)
    posting_type: Optional[str] = 'analysis'

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
    tags_config: Optional[Dict[str, Any]] = None  # 新增：標籤配置
    posting_type: Optional[str] = 'analysis'  # 新增：發文類型 (analysis/interaction)

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

@app.post("/api/simple-mode/generate-batch")
async def simple_mode_generate_batch(request: dict):
    """簡易模式/廢文模式批次生成"""
    try:
        print(f"🎲 簡易模式批次生成開始: {request}")
        
        stock_codes = request.get('stock_codes', [])
        stock_names = request.get('stock_names', [])
        session_id = request.get('session_id')
        use_random_kol = request.get('use_random_kol', False)
        trash_mode = request.get('trash_mode', False)
        trash_sentiment = request.get('trash_sentiment', 'positive')
        
        if not stock_codes:
            return {"success": False, "error": "沒有股票代碼"}
        
        results = []
        
        for i, stock_code in enumerate(stock_codes):
            stock_name = stock_names[i] if i < len(stock_names) else stock_code
            
            # 隨機選擇KOL
            if use_random_kol:
                kol_serial = random.choice(['200', '201', '202', '203', '204', '205', '206', '207', '208'])
            else:
                kol_serial = '200'  # 預設KOL
            
            # 生成內容
            if trash_mode:
                # 廢文模式
                title = f"{stock_name} {random.choice(['爆了', '噴了', '崩了', '穩了'])}！"
                content = f"{stock_name}今天{random.choice(['超強', '超弱', '超穩', '超猛'])}，{random.choice(['買爆', '賣爆', '觀望', '加碼'])}就對了！"
            else:
                # 簡易模式
                title = f"{stock_name} 技術分析"
                content = f"{stock_name}近期表現{random.choice(['強勢', '弱勢', '穩定'])}，技術面顯示{random.choice(['突破', '回調', '整理'])}，建議{random.choice(['逢低布局', '觀望', '減碼'])}。"
            
            results.append({
                "stock_code": stock_code,
                "stock_name": stock_name,
                "kol_serial": kol_serial,
                "title": title,
                "content": content,
                "session_id": session_id
            })
        
        return {
            "success": True,
            "data": {
                "posts": results,
                "total_count": len(results),
                "mode": "trash" if trash_mode else "simple"
            }
        }
        
    except Exception as e:
        print(f"❌ 簡易模式批次生成失敗: {e}")
        return {"success": False, "error": str(e)}

@app.post("/post/simple")
async def simple_post_content(request: PostingRequest):
    """簡化版貼文生成，使用修復後的 ContentGenerator"""
    try:
        logger.info(f"🚀 簡化模式：開始生成貼文")
        logger.info(f"📝 請求參數: topic_title={request.topic_title}, topic_keywords={request.topic_keywords}, kol_serial={request.kol_serial}")
        
        # 基本參數
        stock_id = request.stock_code or "2330"
        stock_name = request.stock_name or "台積電"
        kol_serial = int(request.kol_serial) if request.kol_serial else 200
        session_id = request.session_id or 1  # 使用簡單數字 1, 2, 3...
        
        logger.info(f"📊 基本參數: stock_id={stock_id}, stock_name={stock_name}, kol_serial={kol_serial}")
        
        # 使用修復後的 ContentGenerator
        try:
            logger.info(f"🔧 嘗試導入 ContentGenerator...")
            from src.services.content.content_generator import ContentGenerator, ContentRequest
            logger.info(f"✅ ContentGenerator 導入成功")
            
            # 創建內容生成器
            logger.info(f"🔧 創建 ContentGenerator 實例...")
            content_generator = ContentGenerator()
            logger.info(f"✅ ContentGenerator 實例創建成功")
            
            # 🔍 檢查KOL個人化管理器是否載入
            if hasattr(content_generator, 'kol_personalization_manager') and content_generator.kol_personalization_manager:
                logger.info(f"✅ KOL個人化管理器已載入")
                # 測試KOL個人化管理器
                try:
                    test_nickname = content_generator.kol_personalization_manager.get_kol_nickname(str(kol_serial))
                    test_persona = content_generator.kol_personalization_manager.get_kol_persona(str(kol_serial))
                    logger.info(f"🎯 KOL {kol_serial} 真實資料: 暱稱={test_nickname}, 人設={test_persona}")
                except Exception as e:
                    logger.warning(f"⚠️ KOL個人化管理器測試失敗: {e}")
            else:
                logger.warning(f"❌ KOL個人化管理器未載入或不可用")
            
            # 從 topic_keywords 中提取股票信息
            extracted_stock_info = _extract_stock_from_keywords(request.topic_keywords)
            if extracted_stock_info:
                stock_name = extracted_stock_info['name']
                stock_id = extracted_stock_info['code']
                logger.info(f"🎯 從關鍵詞提取股票信息: {stock_name}({stock_id})")
            
            # 創建內容請求
            content_request = ContentRequest(
                topic_title=request.topic_title or f"{stock_name}盤後分析",
                topic_keywords=request.topic_keywords or f"{stock_name}, 技術分析",
                kol_persona=request.kol_persona or "技術派",
                kol_nickname=request.kol_nickname or f"KOL-{kol_serial}",
                content_type=request.content_style or "investment",
                target_audience=request.target_audience or "active_traders"
            )
            
            logger.info(f"📝 內容請求: topic_title={content_request.topic_title}, topic_keywords={content_request.topic_keywords}")
            
            # 生成內容
            logger.info(f"🔄 開始生成內容...")
            generated_content = content_generator.generate_complete_content(content_request)
            
            if generated_content.success:
                simple_content = {
                    "title": generated_content.title,
                    "content": generated_content.content,
                    "stock_code": stock_id,
                    "stock_name": stock_name,
                    "kol_serial": kol_serial,
                    "session_id": session_id,
                    "post_id": f"simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "status": "draft",
                    "created_at": datetime.now().isoformat()
                }
                logger.info(f"✅ 使用 ContentGenerator 生成內容成功")
                logger.info(f"📝 生成標題: {generated_content.title}")
            else:
                raise Exception(f"ContentGenerator 生成失敗: {generated_content.error_message}")
                
        except Exception as gen_error:
            logger.warning(f"⚠️ ContentGenerator 失敗，使用簡化邏輯: {gen_error}")
            logger.error(f"❌ ContentGenerator 錯誤詳情: {str(gen_error)}")
            import traceback
            logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
            
            # Fallback 到簡化邏輯
            simple_content = {
                "title": f"{stock_name}({stock_id}) - 技術分析",
                "content": f"今日{stock_name}表現如何？讓我們來看看技術面的狀況...",
                "stock_code": stock_id,
                "stock_name": stock_name,
                "kol_serial": kol_serial,
                "session_id": session_id,
                "post_id": f"simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "pending_review",
                "created_at": datetime.now().isoformat()
            }
            logger.info(f"🔄 使用簡化邏輯生成內容")
        
        # 嘗試保存到數據庫（不使用 CommodityTag）
        try:
            logger.info(f"💾 開始保存到數據庫...")
            from postgresql_service import PostgreSQLPostRecordService
            post_service = PostgreSQLPostRecordService()
            
            # 獲取 KOL 暱稱
            kol_nickname = f"KOL-{kol_serial}"  # 默認名稱
            try:
                from kol_service import kol_service
                kol_data = kol_service.get_kol_info(str(kol_serial))
                if kol_data and 'nickname' in kol_data:
                    kol_nickname = kol_data['nickname']
                    logger.info(f"👤 獲取 KOL 暱稱: {kol_nickname}")
            except Exception as kol_error:
                logger.warning(f"⚠️ 獲取 KOL 信息失敗，使用默認名稱: {kol_error}")
            
            # 創建簡化的貼文記錄，不包含 commodity_tags
            logger.info(f"📝 創建貼文記錄: stock_code={stock_id}, stock_name={stock_name}, kol_serial={kol_serial}")
            post_record = post_service.create_post_record_simple(
                stock_code=stock_id,
                stock_name=stock_name,
                kol_serial=str(kol_serial),
                kol_nickname=kol_nickname,
                session_id=session_id
            )
            
            simple_content["database_saved"] = True
            simple_content["database_post_id"] = post_record.id if post_record else None
            logger.info(f"✅ 簡化貼文已保存到數據庫: {simple_content['database_post_id']}")
            
        except Exception as db_error:
            logger.error(f"⚠️ 數據庫保存失敗，但內容生成成功: {db_error}")
            logger.error(f"❌ 數據庫錯誤詳情: {str(db_error)}")
            import traceback
            logger.error(f"📋 數據庫錯誤堆疊: {traceback.format_exc()}")
            simple_content["database_saved"] = False
            simple_content["database_error"] = str(db_error)
        
        logger.info(f"✅ 簡化貼文生成完成")
        logger.info(f"📊 最終結果: title={simple_content.get('title', 'N/A')}, stock_name={simple_content.get('stock_name', 'N/A')}")
        
        return {
            "success": True,
            "post_id": simple_content["post_id"],
            "content": simple_content,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        import traceback
        logger.error(f"❌ 簡化模式錯誤: {e}")
        logger.error(f"❌ 錯誤詳情: {str(e)}")
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@app.post("/post/manual", response_model=PostingResult)
async def manual_post_content(request: PostingRequest):
    """手動發文 - 指定股票和KOL風格"""
    print("🚀🚀🚀 manual_post_content 函數被調用！")
    print(f"🚀🚀🚀 請求參數: stock_code={request.stock_code}, kol_serial={request.kol_serial}")
    print(f"🚀🚀🚀 請求時間: {datetime.now()}")
    
    # 初始化 topic_id 和 topic_title 變量
    topic_id = request.topic_id or None
    topic_title = request.topic_title or None
    
    print(f"🚀 開始手動發文生成 - 請求參數: {request}")
    print(f"📝 內容長度設定: content_length={request.content_length}, max_words={request.max_words}")
    
    # 添加調試信息
    print(f"🔍 後端調試 - 接收到的參數:")
    print(f"  - tags_config: {request.tags_config}")
    print(f"  - topic_tags: {request.tags_config.get('topic_tags', {}) if request.tags_config else {}}")
    print(f"  - mixed_mode: {request.tags_config.get('topic_tags', {}).get('mixed_mode', False) if request.tags_config else False}")
    print(f"  - topic_id: {topic_id}")
    print(f"  - topic_title: {topic_title}")
    
    try:
        # 如果前端指定了股票代號，使用指定的股票
        if request.stock_code:
            stock_id = request.stock_code
            # 使用前端傳遞的股票名稱，如果沒有則使用默認格式
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
        
        # print(f"✅ 股票確定: {stock_name}({stock_id})")
        
        # 導入新的服務
        print("🔧 導入服務模組...")
        try:
            from serper_integration import serper_service
            from smart_data_source_assigner import smart_assigner, KOLProfile, StockProfile
            from publish_service import publish_service
            # print("✅ 服務模組導入成功")
        except Exception as e:
            print(f"❌ 服務模組導入失敗: {e}")
            raise
        
        # 1. 智能數據源分配
        # print(f"🎯 開始智能數據源分配: {stock_id}, {request.kol_persona}")
        
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
        
        # print(f"✅ 數據源分配完成: {data_source_assignment.assignment_reason}")
        print(f"📊 主要數據源: {[s.value for s in data_source_assignment.primary_sources]}")
        
        # 2. 獲取即時股價數據和驗證觸發器類型
        print(f"🔍 開始獲取即時股價數據: {stock_id}")
        actual_price_data = None
        
        try:
            # 🔥 使用盤中觸發器獲取即時股價數據
            print(f"📊 調用盤中觸發器獲取即時股價數據...")
            
            # 構建盤中觸發器請求 - 使用正確的 StockCalculation endpoint
            trigger_config = {
                "endpoint": "https://asterisk-chipsapi.cmoney.tw/AdditionInformationRevisit/api/GetAll/StockCalculation",
                "processing": [
                    {"ParameterJson": f'{{"TargetPropertyNamePath": ["CommKey"], "Value": "{stock_id}"}}', "ProcessType": "EqualValueFilter"},
                    {"ProcessType": "TakeCount", "ParameterJson": "{\"Count\":1}"}
                ]
            }
            
            # 直接調用 CMoney API 獲取即時股價數據
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://asterisk-chipsapi.cmoney.tw/AdditionInformationRevisit/api/GetAll/StockCalculation",
                    json=trigger_config
                )
                
                if response.status_code == 200:
                    trigger_data = response.json()
                    if trigger_data and len(trigger_data) > 0:
                        # 解析即時股價數據
                        price_data = trigger_data
                        if price_data and len(price_data) > 0:
                            # 數據格式: [交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價]
                            stock_data = price_data[0]  # 取第一筆數據
                            
                            actual_price_data = {
                                'current_price': float(stock_data[3]) if len(stock_data) > 3 else 0,  # 即時成交價
                                'change_amount': float(stock_data[8]) if len(stock_data) > 8 else 0,  # 漲跌
                                'change_percentage': float(stock_data[9]) if len(stock_data) > 9 else 0,  # 漲跌幅
                                'current_volume': int(stock_data[4]) if len(stock_data) > 4 else 0,  # 即時成交量
                                'total_volume': int(stock_data[11]) if len(stock_data) > 11 else 0,  # 累計成交量
                                'high_price': float(stock_data[5]) if len(stock_data) > 5 else 0,  # 最高價
                                'low_price': float(stock_data[6]) if len(stock_data) > 6 else 0,  # 最低價
                                'open_price': float(stock_data[12]) if len(stock_data) > 12 else 0,  # 開盤價
                                'is_limit_up': abs(float(stock_data[9])) >= 9.5 and float(stock_data[9]) > 0 if len(stock_data) > 9 else False,
                                'is_limit_down': abs(float(stock_data[9])) >= 9.5 and float(stock_data[9]) < 0 if len(stock_data) > 9 else False,
                                'volume_ratio': 1.0,  # 需要計算
                                'raw_data': stock_data,  # 🔥 保存原始 JSON 數據
                                'column_names': ['交易時間', '傳輸序號', '內外盤旗標', '即時成交價', '即時成交量', '最低價', '最高價', '標的', '漲跌', '漲跌幅', '累計成交總額', '累計成交量', '開盤價'],  # 新增：column names
                                'avg_volume': 0  # 需要從其他API獲取
                            }
                            
                            print(f"✅ 獲取即時股價數據成功:")
                            print(f"   - 當前價格: {actual_price_data['current_price']}")
                            print(f"   - 漲跌: {actual_price_data['change_amount']}")
                            print(f"   - 漲跌幅: {actual_price_data['change_percentage']}%")
                            print(f"   - 是否漲停: {actual_price_data['is_limit_up']}")
                            print(f"   - 是否跌停: {actual_price_data['is_limit_down']}")
                        else:
                            print(f"⚠️ CMoney API 返回空數據")
                    else:
                        print(f"⚠️ CMoney API 請求失敗: {trigger_data}")
                else:
                    print(f"⚠️ CMoney API 調用失敗: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"⚠️ 獲取即時股價數據失敗: {e}")
            import traceback
            print(f"📋 錯誤堆疊: {traceback.format_exc()}")
        
        # 3. 股價驗證和新聞關鍵字修正
        corrected_keywords = None
        if actual_price_data:
            try:
                # 導入股價驗證器
                from stock_price_validator import stock_price_validator
                
                # 驗證觸發器類型
                trigger_type = getattr(request, 'trigger_type', 'intraday_limit_up')
                is_valid, validation_message, suggested_trigger = stock_price_validator.validate_trigger_type(
                    stock_code=stock_id,
                    stock_name=stock_name,
                    trigger_type=trigger_type,
                    actual_price_data=actual_price_data
                )
                
                print(f"🔍 觸發器驗證結果: {validation_message}")
                if not is_valid and suggested_trigger:
                    print(f"⚠️ 建議使用觸發器類型: {suggested_trigger}")
                    # 可以選擇是否自動修正觸發器類型
                    # trigger_type = suggested_trigger
                
                # 根據實際股價表現獲取正確的新聞關鍵字
                corrected_keywords = stock_price_validator.get_corrected_news_keywords(
                    stock_code=stock_id,
                    stock_name=stock_name,
                    trigger_type=trigger_type,
                    actual_price_data=actual_price_data
                )
                
            except Exception as e:
                print(f"⚠️ 股價驗證失敗，使用預設設定: {e}")
                corrected_keywords = None
        else:
            print(f"⚠️ 無法獲取即時股價數據，跳過驗證")
        
        # 4. 獲取Serper新聞數據 - 使用修正後的關鍵字
        print(f"🔍 開始獲取Serper新聞數據: {stock_id}")
        try:
            # 提取新聞搜尋關鍵字配置
            search_keywords = None
            time_range = "d2"  # 預設時間範圍
            
            # 優先使用修正後的關鍵字
            if corrected_keywords:
                search_keywords = corrected_keywords
                print(f"📝 使用修正後的新聞關鍵字: {len(search_keywords)} 個關鍵字")
                for kw in search_keywords:
                    print(f"   - {kw.get('type', 'custom')}: {kw.get('keyword', '')}")
            elif request.news_config:
                # 提取搜尋關鍵字
                if request.news_config.get('search_keywords'):
                    search_keywords = request.news_config.get('search_keywords')
                    print(f"📝 使用前端新聞關鍵字配置: {len(search_keywords)} 個關鍵字")
                    for kw in search_keywords:
                        print(f"   - {kw.get('type', 'custom')}: {kw.get('keyword', '')}")
                
                # 提取時間範圍設定
                if request.news_config.get('time_range'):
                    time_range = request.news_config.get('time_range')
                    print(f"⏰ 使用前端時間範圍設定: {time_range}")
                elif request.news_time_range:
                    time_range = request.news_time_range
                    print(f"⏰ 使用請求時間範圍設定: {time_range}")
                
                # 🔥 修復：提取新聞連結設定
                if 'enable_news_links' in request.news_config:
                    request.enable_news_links = request.news_config.get('enable_news_links', True)
                    print(f"🔗 使用前端新聞連結設定: {request.enable_news_links}")
                
                # 🔥 修復：提取新聞數量設定
                if 'max_links' in request.news_config:
                    request.news_max_links = request.news_config.get('max_links', 5)
                    print(f"📊 使用前端新聞數量設定: {request.news_max_links}")
            else:
                print("📝 使用預設新聞搜尋關鍵字")
            
            serper_analysis = serper_service.get_comprehensive_stock_analysis(
                stock_id, 
                stock_name, 
                search_keywords=search_keywords,
                time_range=time_range,
                trigger_type=request.trigger_type
            )
            news_items = serper_analysis.get('news_items', [])
            limit_up_analysis = serper_analysis.get('limit_up_analysis', {})
            # print(f"✅ Serper分析完成: 找到 {len(news_items)} 則新聞")
        except Exception as e:
            print(f"⚠️ Serper分析失敗: {e}")
            serper_analysis = {'news_items': [], 'limit_up_analysis': {}}
            news_items = []
            limit_up_analysis = {}
        
        # 3. 生成KOL內容 - 檢查發文類型
        print(f"✍️ 開始生成KOL內容: {stock_id}, {request.kol_persona}")
        
        # 檢查是否為互動發問類型
        posting_type = getattr(request, 'posting_type', 'analysis')
        print(f"📝 發文類型: {posting_type}")
        
        if posting_type == 'interaction':
            print("🎯 使用互動發問捷徑生成內容（跳過個人化模組）")
            
            # 使用互動內容生成器
            kol_content = generate_interaction_content(
                stock_id=stock_id,
                stock_name=stock_name,
                include_questions=True,
                include_emoji=True,
                include_hashtag=True
            )
            
            print(f"✅ 互動發問內容生成完成: {kol_content['title']} - {kol_content['content']}")
            print(f"📊 內容長度: {kol_content['content_length']} 字")
            print(f"🚫 跳過個人化模組: {kol_content['skipped_personalization']}")
            
        else:
            print("📊 使用正常分析流程生成內容")
            
            try:
                # 強制使用新聞分析Agent
                if news_items:
                    print(f"🤖 強制使用新聞分析Agent分析 {len(news_items)} 則新聞")
                from news_analysis_agent import NewsAnalysisAgent
                
                # 獲取KOL配置信息
                kol_nickname = f"KOL-{request.kol_serial}" if request.kol_serial else "分析師"
                kol_persona = request.kol_persona or "technical"  # 初始化 kol_persona
                kol_config = {}
                
                # 嘗試從KOL服務獲取詳細配置
                try:
                    print(f"🔍 開始獲取KOL配置: serial={request.kol_serial}")
                    from kol_service import kol_service
                    kol_data = kol_service.get_kol_info(str(request.kol_serial)) if request.kol_serial else None
                    print(f"🔍 KOL數據查詢結果: {kol_data is not None}")
                    if kol_data:
                        print(f"🔍 KOL數據內容: {list(kol_data.keys())}")
                        kol_nickname = kol_data.get('nickname', kol_nickname)
                        # 構建KOL配置字典
                        kol_config = {
                            'tone_style': kol_data.get('tone_style', '專業友善'),
                            'common_words': kol_data.get('common_terms', ''),
                            'casual_words': kol_data.get('colloquial_terms', ''),
                            'typing_habit': kol_data.get('typing_habit', '正常標點'),
                            'background_story': kol_data.get('backstory', ''),
                            'expertise': kol_data.get('expertise', ''),
                            'ending_style': kol_data.get('signature', '感謝閱讀，歡迎討論')
                        }
                        print(f"👤 獲取KOL配置: {kol_nickname}")
                        print(f"👤 KOL配置內容: {kol_config}")
                        print(f"👤 KOL配置詳細: tone_style={kol_config.get('tone_style')}, common_words={kol_config.get('common_words')}, casual_words={kol_config.get('casual_words')}")
                    else:
                        print(f"⚠️ 未找到KOL數據: serial={request.kol_serial}")
                except Exception as kol_error:
                    print(f"⚠️ 獲取KOL配置失敗，使用默認設定: {kol_error}")
                    import traceback
                    print(f"📋 錯誤堆疊: {traceback.format_exc()}")
                
                # 創建新的實例以確保API Key正確載入
                news_agent = NewsAnalysisAgent()
                
                # 根據生成模式選擇不同的內容生成邏輯
                # 🔥 修復：強制使用高品質模式，忽略前端的錯誤參數
                generation_mode = 'high_quality'  # 強制使用高品質模式
                print(f"🎯 強制使用高品質模式，忽略前端參數: {request.generation_mode}")
                
                if generation_mode == 'trash':
                    # 廢文模式 - 使用簡易內容生成器
                    print("🗑️ 使用廢文模式生成內容")
                    from simple_content_generator import SimpleContentGenerator
                    simple_generator = SimpleContentGenerator()
                    
                    kol_content = simple_generator.generate_content(
                        stock_codes=[stock_id],
                        stock_names=[stock_name],
                        kol_nickname=kol_nickname,
                        kol_persona=request.kol_persona,
                        session_id=request.session_id,
                        trash_mode=True,
                        trash_sentiment=request.trash_sentiment or 'positive'
                    )
                    # print(f"✅ 廢文模式生成完成: {len(kol_content.get('content', ''))} 字")
                    
                elif generation_mode == 'simple':
                    # 簡易模式 - 使用修復後的ContentGenerator（與高品質模式相同）
                    print("🎲 使用簡易模式生成內容（使用ContentGenerator）")
                    
                    # 🔧 使用修復後的ContentGenerator
                    try:
                        print("🔧 嘗試使用修復後的ContentGenerator...")
                        from src.services.content.content_generator import ContentGenerator, ContentRequest
                        content_generator = ContentGenerator()
                        
                        # 🔍 檢查KOL個人化管理器
                        if hasattr(content_generator, 'kol_personalization_manager') and content_generator.kol_personalization_manager:
                            # print("✅ KOL個人化管理器已載入")
                            # 獲取真實KOL資料
                            real_nickname = content_generator.kol_personalization_manager.get_kol_nickname(str(kol_serial))
                            real_persona = content_generator.kol_personalization_manager.get_kol_persona(str(kol_serial))
                            # print(f"🎯 KOL {kol_serial} 真實資料: 暱稱={real_nickname}, 人設={real_persona}")
                            
                            # 使用真實KOL資料
                            kol_nickname = real_nickname
                            if real_persona:
                                request.kol_persona = real_persona
                        else:
                            print("⚠️ KOL個人化管理器未載入，使用預設資料")
                        
                        # 構建ContentRequest
                        content_request = ContentRequest(
                            stock_code=stock_id,
                            stock_name=stock_name,
                            kol_serial=kol_serial,
                            kol_nickname=kol_nickname,
                            kol_persona=request.kol_persona,
                            content_style=request.content_style,
                            target_audience=request.target_audience,
                            content_length=request.content_length,
                            max_words=request.max_words,
                            data_sources=request.data_sources,
                            serper_analysis=serper_analysis,
                            trigger_type=request.trigger_type
                        )
                        
                        # 生成內容
                        generated_content = content_generator.generate_content(content_request)
                        
                        if generated_content.success:
                            kol_content = {
                                "title": generated_content.title,
                                "content": generated_content.content,
                                "content_md": generated_content.content_md,
                                "commodity_tags": generated_content.commodity_tags,
                                "community_topic": generated_content.community_topic
                            }
                            print(f"✅ 簡易模式生成完成: {len(kol_content.get('content', ''))} 字")
                        else:
                            raise Exception(f"ContentGenerator生成失敗: {generated_content.error}")
                            
                    except Exception as e:
                        print(f"❌ ContentGenerator失敗: {e}")
                        # Fallback 到基本內容
                        kol_content = {
                            "title": f"{stock_name} 分析",
                            "content": f"關於 {stock_name} 的技術分析，建議謹慎操作。",
                            "content_md": f"關於 {stock_name} 的技術分析，建議謹慎操作。",
                            "commodity_tags": [{"type": "Stock", "key": stock_id, "bullOrBear": 0}],
                            "community_topic": None
                        }
                    
                else:
                    # 高品質模式 - 使用修復後的ContentGenerator
                    print("✨ 使用高品質模式生成內容")
                    
                    # 🔧 使用修復後的ContentGenerator
                    try:
                        print("🔧 嘗試使用修復後的ContentGenerator...")
                        from src.services.content.content_generator import ContentGenerator, ContentRequest
                        content_generator = ContentGenerator()
                        
                        # 🔍 檢查KOL個人化管理器
                        if hasattr(content_generator, 'kol_personalization_manager') and content_generator.kol_personalization_manager:
                            # print("✅ KOL個人化管理器已載入")
                            # 獲取真實KOL資料
                            real_nickname = content_generator.kol_personalization_manager.get_kol_nickname(str(kol_serial))
                            real_persona = content_generator.kol_personalization_manager.get_kol_persona(str(kol_serial))
                            # print(f"🎯 KOL {kol_serial} 真實資料: 暱稱={real_nickname}, 人設={real_persona}")
                            
                            # 使用真實KOL資料
                            kol_nickname = real_nickname
                            kol_persona = real_persona
                        else:
                            print("⚠️ KOL個人化管理器未載入，使用預設資料")
                        
                        # 創建內容請求
                        content_request = ContentRequest(
                            topic_title=request.topic_title or f"{stock_name}盤後分析",
                            topic_keywords=request.topic_keywords or f"{stock_name}, 技術分析",
                            kol_persona=kol_persona,
                            kol_nickname=kol_nickname,
                            content_type=request.content_style or "investment",
                            target_audience=request.target_audience or "active_traders"
                        )
                        
                        # 生成內容 - 整合新聞數據
                        generated_content = content_generator.generate_complete_content(
                            content_request,
                            serper_analysis=serper_analysis,
                            data_sources=[source.value for source in data_source_assignment.primary_sources] if data_source_assignment else None
                        )
                        
                        if generated_content.success:
                            kol_content = {
                                "title": generated_content.title,
                                "content": generated_content.content,
                                "stock_code": stock_id,
                                "stock_name": stock_name,
                                "kol_serial": kol_serial,
                                "kol_nickname": kol_nickname,
                                "kol_persona": kol_persona
                            }
                            # print(f"✅ ContentGenerator生成成功: {len(generated_content.content)} 字")
                        else:
                            raise Exception(f"ContentGenerator生成失敗: {generated_content.error_message}")
                            
                    except Exception as e:
                        print(f"⚠️ ContentGenerator失敗，回退到原有邏輯: {e}")
                        # 回退到原有邏輯
                        # 檢查是否為熱門話題
                        if topic_id and topic_title:
                            print(f"🔥 檢測到熱門話題，使用專用分析方法: {topic_title}")
                        # 獲取話題內容
                        topic_content = ""
                        try:
                            from src.services.triggers.trending_topic_trigger_system import get_trending_topic_trigger_system
                            trending_system = get_trending_topic_trigger_system()
                            topic_data = trending_system.get_topic_details(topic_id)
                            if topic_data:
                                topic_content = topic_data.get("content", "")
                                print(f"📝 獲取話題內容: {len(topic_content)} 字")
                        except Exception as e:
                            print(f"⚠️ 獲取話題內容失敗: {e}")
                        
                        kol_content = news_agent.analyze_stock_news(
                            stock_code=stock_id,
                            stock_name=stock_name,
                            news_items=news_items,
                            kol_persona=request.kol_persona,
                            content_length=request.content_length,
                            max_words=request.max_words
                        )
                        # print(f"✅ 熱門話題分析完成: {len(kol_content.get('content', ''))} 字")
                    else:
                        # 根據觸發器類型選擇不同的分析方法
                        trigger_type = request.trigger_type or 'default'
                        print(f"📈 使用股票分析方法: {stock_name}({stock_id}), 觸發器類型: {trigger_type}")
                        print(f"🔍 DEBUG: request.trigger_type = {request.trigger_type}")
                        print(f"🔍 DEBUG: trigger_type = {trigger_type}")
                        
                        if trigger_type == 'volume_low':
                            # 成交量低迷觸發器 - 使用下跌分析
                            kol_content = news_agent.analyze_volume_low_stock(
                                stock_id, stock_name, news_items, request.kol_persona, 
                                kol_nickname, kol_config, request.content_length, request.max_words
                            )
                            # print(f"✅ 成交量低迷分析完成: {len(kol_content.get('content', ''))} 字")
                        elif trigger_type == 'limit_down_after_hours':
                            # 盤後下跌觸發器 - 使用下跌分析
                            kol_content = news_agent.analyze_limit_down_stock(
                                stock_id, stock_name, news_items, request.kol_persona, 
                                kol_nickname, kol_config, request.content_length, request.max_words
                            )
                            # print(f"✅ 盤後下跌分析完成: {len(kol_content.get('content', ''))} 字")
                        else:
                            # 默認使用通用股票分析
                            kol_content = news_agent.analyze_stock_news(
                                stock_id, stock_name, news_items, request.kol_persona, 
                                kol_nickname, kol_config, request.content_length, request.max_words, trigger_type
                            )
                            # print(f"✅ 通用股票分析完成: {len(kol_content.get('content', ''))} 字")
                        
                        # 如果沒有新聞數據，使用GPT生成器
                        if not news_items:
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
                            # print(f"✅ GPT內容生成完成: {len(kol_content.get('content', ''))} 字")
                    
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
                # print(f"✅ 回退內容生成完成: {len(kol_content.get('content', ''))} 字")
        
        # 4. 整合新聞素材和數據源資訊
        print("🔗 整合新聞素材和數據源資訊...")
        try:
            enhanced_content = enhance_content_with_serper_data(
                kol_content, 
                serper_analysis, 
                data_source_assignment
            )
            # print("✅ 內容整合完成")
        except Exception as e:
            print(f"⚠️ 內容整合失敗: {e}")
            enhanced_content = kol_content
        
        # 定義百分比配置變數（避免語法錯誤）
        article_type_distribution = getattr(request, 'article_type_distribution', None)
        content_length_distribution = getattr(request, 'content_length_distribution', None)
        content_style_distribution = getattr(request, 'content_style_distribution', None)
        analysis_depth_distribution = getattr(request, 'analysis_depth_distribution', None)
        max_words = getattr(request, 'max_words', None)
        include_charts = getattr(request, 'include_charts', None)
        include_risk_warning = getattr(request, 'include_risk_warning', None)
        
        # 🎯 個人化步驟 - 在內容整合完成後，保存到數據庫前
        print("🎯 開始個人化處理...")
        
        # 檢查是否為互動發問類型，如果是則跳過個人化處理
        if posting_type == 'interaction':
            print("🚫 互動發問類型跳過個人化處理")
            enhanced_content = kol_content  # 直接使用互動內容
        else:
            print("🎯 正常類型進行個人化處理")
        
        # 🔔 排程生成檢測標記
        batch_mode = getattr(request, 'batch_mode', False)
        session_id = getattr(request, 'session_id', None)
        schedule_task_id = os.environ.get('CURRENT_SCHEDULE_TASK_ID', None)
        
        # 🔥 修復：只有當CURRENT_SCHEDULE_TASK_ID存在時才是真正的排程模式
        if schedule_task_id:
            print(f"🔔🔔🔔 檢測到排程生成模式！這是排程系統自動觸發的貼文！🔔🔔🔔")
            print(f"🔔 Task ID: {schedule_task_id}, Stock: {request.stock_code}, KOL: KOL-{request.kol_serial}")
        elif batch_mode:
            print("📦📦📦 檢測到手動批次模式！這是用戶手動觸發的批次貼文！📦📦📦")
            print(f"📦 Stock: {request.stock_code}, Session: {session_id}")
        else:
            print("👤👤👤 檢測到手動單篇模式！這是用戶手動觸發的單篇貼文！👤👤👤")
            print(f"👤 Stock: {request.stock_code}, Session: {session_id}")
        
        print(f"🔍 調試：enhanced_content keys: {list(enhanced_content.keys()) if enhanced_content else 'None'}")
        print(f"🔍 調試：enhanced_content title: {enhanced_content.get('title', 'None') if enhanced_content else 'None'}")
        print(f"🔍 調試：enhanced_content content length: {len(enhanced_content.get('content', '')) if enhanced_content else 0}")
        
        # 定義 kol_serial 變數 - 如果沒有指定則隨機選擇
        if request.kol_serial:
            kol_serial = request.kol_serial
            print(f"🎯 使用指定的KOL序列號: {kol_serial}")
        else:
            # 隨機選擇KOL - 從資料庫動態獲取所有可用KOL
            import random
            import time
            try:
                # 從資料庫獲取所有可用的KOL
                from kol_database_service import KOLDatabaseService
                kol_service = KOLDatabaseService()
                all_kols = kol_service.get_all_kols()
                available_kols = [str(kol.serial) for kol in all_kols if kol.status == 'active']
                
                if not available_kols:
                    # 如果資料庫沒有KOL，使用預設的9個
                    available_kols = ['200', '201', '202', '203', '204', '205', '206', '207', '208']
                    print(f"⚠️ 資料庫沒有可用KOL，使用預設池子: {len(available_kols)} 個")
                else:
                    print(f"📊 從資料庫獲取到 {len(available_kols)} 個可用KOL")
                
                # 使用當前時間作為隨機種子的一部分，增加隨機性
                random.seed(int(time.time() * 1000) % 1000000)
                # 打亂順序後選擇
                random.shuffle(available_kols)
                kol_serial = random.choice(available_kols)
                print(f"🎲 隨機選擇KOL序列號: {kol_serial} (從 {len(available_kols)} 個KOL中選擇)")
                
            except Exception as e:
                print(f"❌ 獲取KOL列表失敗: {e}，使用預設KOL")
                # 回退到預設的9個KOL
                available_kols = ['200', '201', '202', '203', '204', '205', '206', '207', '208']
                random.seed(int(time.time() * 1000) % 1000000)
                random.shuffle(available_kols)
                kol_serial = random.choice(available_kols)
                print(f"🎲 隨機選擇KOL序列號: {kol_serial} (從預設池子中選擇)")
        print(f"🎯 請求中的 kol_persona: {request.kol_persona}")
        
        # 🎯 舊版個人化模組已移除，使用增強版個人化模組
        print("🎯 跳過舊版個人化模組，等待增強版個人化處理...")
        
        # 5. 內容檢查和修復（在新聞整合後進行）
        print("🔍 開始內容檢查和修復...")
        print("⚠️ 暫時禁用 ContentChecker 以測試個人化功能")
        # try:
        #     from content_checker import ContentChecker
        #     content_checker = ContentChecker()
        #     
        #     # 檢查並修復內容（檢查 content_md 字段）
        #     content_to_check = enhanced_content.get('content_md', enhanced_content.get('content', ''))
        #     check_result = content_checker.check_and_fix_content(
        #         content_to_check,
        #         stock_name,
        #         stock_id,
        #         request.kol_persona,
        #         request.kol_serial,
        #         # 新增：傳遞百分比配置
        #         article_type_distribution=article_type_distribution,
        #         content_length_distribution=content_length_distribution,
        #         content_style_distribution=content_style_distribution,
        #         analysis_depth_distribution=analysis_depth_distribution,
        #         max_words=max_words,
        #         include_charts=include_charts,
        #         include_risk_warning=include_risk_warning,
        #         # 新增：傳遞觸發器類型
        #         trigger_type=request.trigger_type
        #     )
        #     
        #     if check_result['success']:
        #         print(f"✅ 內容檢查完成: {check_result['fix_method']} 修復")
        #         if check_result['issues_found']:
        #             print(f"🔧 發現問題: {', '.join(check_result['issues_found'])}")
        #         
        #         # 使用修復後的內容，但保留個人化標籤和新聞來源
        #         # 檢查是否有個人化標籤需要保留
        #         personalization_tag = ""
        #         if enhanced_content['content'].startswith(f"【{real_nickname}】"):
        #             personalization_tag = f"【{real_nickname}】"
        #             print(f"🔍 保留個人化標籤: {personalization_tag}")
        #         
        #         # 檢查是否有新聞來源需要保留
        #         news_sources_section = ""
        #         if "新聞來源:" in enhanced_content['content']:
        #             news_sources_start = enhanced_content['content'].find("新聞來源:")
        #             news_sources_section = enhanced_content['content'][news_sources_start:]
        #             print(f"🔍 保留新聞來源: {len(news_sources_section)} 字")
        #         
        #         # 應用修復後的內容
        #         enhanced_content['content'] = check_result['fixed_content']
        #         enhanced_content['content_md'] = check_result['fixed_content']
        #         
        #         # 重新添加個人化標籤
        #         if personalization_tag:
        #             enhanced_content['content'] = personalization_tag + enhanced_content['content']
        #             enhanced_content['content_md'] = personalization_tag + enhanced_content['content_md']
        #             print(f"✅ 個人化標籤已重新添加: {personalization_tag}")
        #         
        #         # 重新添加新聞來源
        #         if news_sources_section:
        #             enhanced_content['content'] += "\n\n" + news_sources_section
        #             enhanced_content['content_md'] += "\n\n" + news_sources_section
        #             print(f"✅ 新聞來源已重新添加: {len(news_sources_section)} 字")
        #         
        #         enhanced_content['content_check'] = check_result
        #     else:
        #         print(f"⚠️ 內容檢查失敗: {check_result.get('error', '未知錯誤')}")
        #         
        # except Exception as e:
        #     print(f"⚠️ 內容檢查器初始化失敗: {e}")
        
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
        
        # 處理 commodity tags
        commodity_tags = []
        
        # 默認添加 TWA00 標籤（台股大盤）
        commodity_tags.append({
            "type": "Market",
            "key": "TWA00",
            "bullOrBear": 0  # 預設中性
        })
        print(f"🏷️ 添加默認 TWA00 標籤")
        
        # 如果有共享的 commodity tags（來自批量生成），優先使用
        if request.shared_commodity_tags:
            commodity_tags.extend(request.shared_commodity_tags)
            print(f"🏷️ 使用共享 commodity tags: {len(request.shared_commodity_tags)} 個")
            for tag in request.shared_commodity_tags:
                print(f"  - {tag.get('type')}: {tag.get('key')}")
        else:
            # 檢查是否為熱門話題
            if topic_id and topic_title:
                # 熱門話題生成專用標籤 - 使用 topic_id 作為 key
                commodity_tags.append({
                    "type": "TrendingTopic",
                    "key": topic_id,  # 使用 topic_id (UUID) 而不是 topic_title
                    "bullOrBear": 0  # 預設中性，後續可以根據內容分析調整
                })
                print(f"🏷️ 生成熱門話題 commodity tag: {topic_id} - {topic_title}")
            else:
                # 否則根據股票信息生成 commodity tags
                commodity_tags.append({
                    "type": "Stock",
                    "key": stock_id,
                    "bullOrBear": 0  # 預設中性
                })
                print(f"🏷️ 生成單個股票 commodity tag: {stock_id}")
        
        print(f"✅ 最終 commodity tags: {len(commodity_tags)} 個")
        print(f"📊 股票代號: {stock_id}, 股票名稱: {stock_name}")
        print(f"👤 KOL序號: {request.kol_serial}")
        
        # 準備社群話題
        community_topic = None
        if request.post_to_thread:
            community_topic = CommunityTopic(id=request.post_to_thread, title=request.post_to_thread)
            print(f"💬 社群話題: {request.post_to_thread}")
        elif topic_id and topic_title:
            # 如果是熱門話題，使用 topic_id 作為社群話題 ID
            community_topic = CommunityTopic(id=topic_id, title=topic_title)
            print(f"💬 熱門話題社群話題: {topic_id} - {topic_title}")
        
        # 準備生成參數 - 整合數據源資訊
        print("⚙️ 準備生成參數...")
        
        generation_params = GenerationParams(
            kol_persona=request.kol_persona,
            content_style=request.content_style,
            target_audience=request.target_audience,
            batch_mode=request.batch_mode,
            data_sources=[source.value for source in data_source_assignment.primary_sources],
            session_id=request.session_id,
            technical_indicators=[],
            # 新增：百分比配置參數
            article_type_distribution=article_type_distribution,
            content_length_distribution=content_length_distribution,
            content_style_distribution=content_style_distribution,
            analysis_depth_distribution=analysis_depth_distribution,
            max_words=max_words,
            include_charts=include_charts,
            include_risk_warning=include_risk_warning
        )
        print("✅ 生成參數準備完成")
        
        # 創建貼文記錄
        print("💾 開始保存貼文記錄到資料庫...")
        try:
            # 處理 commodity tags 模型轉換
            commodity_tag_models = []
            if commodity_tags:
                try:
                    # 動態導入 CommodityTag 模型
                    from post_record_service import CommodityTag
                    for tag_data in commodity_tags:
                        commodity_tag_models.append(CommodityTag(
                            type=tag_data.get("type", "Stock"),
                            key=tag_data.get("key", ""),
                            bullOrBear=tag_data.get("bullOrBear", 0)
                        ))
                    print(f"✅ 成功轉換 {len(commodity_tag_models)} 個 commodity tags")
                except ImportError as e:
                    print(f"⚠️ CommodityTag 模型導入失敗，跳過 commodity tags: {e}")
                    commodity_tag_models = []
            else:
                print("ℹ️ 沒有 commodity tags 需要處理")
            
            # 確保使用存在的 KOL
            from kol_service import kol_service
            available_kol_ids = list(kol_service.kol_credentials.keys())
            if request.kol_serial and str(request.kol_serial) in available_kol_ids:
                kol_serial = int(request.kol_serial)
            else:
                # 使用第一個可用的 KOL
                kol_serial = int(available_kol_ids[0])
                print(f"⚠️ KOL {request.kol_serial} 不存在，使用 KOL {kol_serial}")
            
            # 準備貼文記錄數據
            print(f"📝 準備貼文記錄數據: {enhanced_content.get('title', '未命名貼文')}")
            print(f"🔍 貼文記錄數據詳情: session_id={request.session_id}, stock_code={stock_id}")
            
        except Exception as e:
            print(f"❌ 準備貼文記錄數據失敗: {e}")
            # 不設置 error 狀態，繼續嘗試保存到數據庫
        
        # 處理熱門話題 ID（混和模式）- 在保存到數據庫之前執行
        print("🔍 開始處理熱門話題 ID（混和模式）")
        # 調試日誌
        print(f"🔍 調試標籤模式條件:")
        print(f"  - topic_id: {topic_id}")
        print(f"  - topic_title: {topic_title}")
        print(f"  - tags_config: {request.tags_config}")
        print(f"  - tag_mode: {request.tags_config.get('tag_mode', 'stock_tags') if request.tags_config else 'stock_tags'}")
        print(f"  - topic_tags: {request.tags_config.get('topic_tags', {}) if request.tags_config else {}}")
        print(f"  - mixed_mode: {request.tags_config.get('topic_tags', {}).get('mixed_mode', False) if request.tags_config else False}")
        
        # 檢查標籤模式條件
        tag_mode = request.tags_config.get('tag_mode', 'stock_tags') if request.tags_config else 'stock_tags'
        mixed_mode_enabled = request.tags_config and request.tags_config.get('topic_tags', {}).get('mixed_mode', False)
        topic_tags_enabled = request.tags_config and request.tags_config.get('topic_tags', {}).get('enabled', False)
        
        print(f"🔍 標籤模式條件檢查:")
        print(f"  - request.tags_config 存在: {bool(request.tags_config)}")
        print(f"  - tag_mode: {tag_mode}")
        print(f"  - mixed_mode_enabled: {mixed_mode_enabled}")
        print(f"  - topic_id 為空: {not topic_id}")
        
        # 判斷是否需要自動獲取熱門話題
        should_auto_fetch_topic = (
            (not topic_id or topic_id == 'auto_fetch') and  # 沒有提供 topic_id 或明確要求自動獲取
            (
                tag_mode == 'topic_tags' or  # 純熱門話題模式
                tag_mode == 'both' or  # 混合模式
                mixed_mode_enabled or  # 或者啟用了混和模式
                topic_id == 'auto_fetch'  # 或者明確要求自動獲取
            )
        )
        
        print(f"  - 應該自動獲取熱門話題: {should_auto_fetch_topic}")
        
        # 如果沒有提供 topic_id 但需要熱門話題標籤，自動從 trending API 獲取
        if should_auto_fetch_topic:
            try:
                print("🔄 自動獲取熱門話題（基於標籤模式）...")
                print(f"🔍 調用 trending API: {TRENDING_API_URL}/trending")
                trending_response = requests.get(f"{TRENDING_API_URL}/trending", params={"limit": 1})
                print(f"🔍 trending API 響應狀態: {trending_response.status_code}")
                trending_response.raise_for_status()
                trending_data = trending_response.json()
                print(f"🔍 trending API 響應數據: {trending_data}")
                
                if trending_data.get("topics") and len(trending_data["topics"]) > 0:
                    trending_topic = trending_data["topics"][0]
                    topic_id = trending_topic.get("id")
                    topic_title = trending_topic.get("title")
                    print(f"✅ 自動獲取到熱門話題 - ID: {topic_id}, 標題: {topic_title}")
                    print(f"🔍 完整話題數據: {trending_topic}")
                else:
                    print("⚠️ 未獲取到熱門話題數據")
                    print(f"🔍 響應數據結構: {trending_data}")
                    # 確保變量有默認值
                    if not topic_id:
                        topic_id = None
                    if not topic_title:
                        topic_title = None
            except Exception as e:
                print(f"❌ 獲取熱門話題失敗: {e}")
                import traceback
                print(f"🔍 錯誤堆疊: {traceback.format_exc()}")
                # 確保變量有默認值
                if not topic_id:
                    topic_id = None
                if not topic_title:
                    topic_title = None
        
        # 🎯 增強版個人化節點 - 在保存到數據庫之前進行個人化處理
        print("🎯 開始增強版個人化節點處理...")
        try:
            from personalization_module import enhanced_personalization_processor
            
            # 獲取KOL序號 - 使用之前確定的kol_serial
            print(f"🎯 使用增強版個人化處理器 - KOL: {kol_serial}")
            
            # 準備個人化參數
            original_title = enhanced_content.get('title', f"{stock_name} 分析")
            original_content = enhanced_content.get('content', '')
            batch_config = {}  # 可以從request中獲取
            serper_analysis = enhanced_content.get('serper_data', {})
            trigger_type = request.trigger_type or 'manual'
            
            print(f"🎯 個人化輸入 - 標題: {original_title}")
            print(f"🎯 個人化輸入 - 內容長度: {len(original_content)} 字")
            print(f"🎯 個人化輸入 - 觸發器類型: {trigger_type}")
            
            # 將新聞連結配置添加到 serper_analysis 中
            if serper_analysis:
                serper_analysis['enable_news_links'] = getattr(request, 'enable_news_links', True)
                serper_analysis['news_max_links'] = getattr(request, 'news_max_links', 5) if getattr(request, 'enable_news_links', True) else 0
            
            # 使用增強版個人化處理器 - 整合隨機化生成
            try:
                personalized_title, personalized_content, random_metadata = enhanced_personalization_processor.personalize_content(
                    standard_title=original_title,
                    standard_content=original_content,
                    kol_serial=kol_serial,
                    batch_config=batch_config,
                    serper_analysis=serper_analysis,
                    trigger_type=trigger_type,
                    real_time_price_data=actual_price_data or {},  # 🔥 新增：傳入即時股價數據，如果為 None 則傳入空字典
                    posting_type=posting_type  # 🎲 新增：傳入發文類型
                )
                
                # 🎲 新增：處理隨機化元數據
                if random_metadata:
                    alternative_versions = random_metadata.get('alternative_versions', [])
                    generation_metadata = random_metadata.get('generation_metadata', {})
                    
                    print(f"🎲 隨機化生成完成 - 選中版本: {generation_metadata.get('selected_index', 'Unknown') + 1}")
                    print(f"📝 其他版本數量: {len(alternative_versions)}")
                    
                    # 詳細記錄每個 alternative_versions 的內容
                    for i, version in enumerate(alternative_versions):
                        print(f"📝 版本 {i+1}: {version.get('title', 'No title')}")
                        print(f"   角度: {version.get('angle', 'No angle')}")
                        print(f"   內容長度: {len(version.get('content', ''))} 字符")
                    
                    # 將其他版本存儲到 enhanced_content 中，稍後保存到數據庫
                    enhanced_content['alternative_versions'] = alternative_versions
                    enhanced_content['generation_metadata'] = generation_metadata
                    
                    print(f"💾 alternative_versions 已存儲到 enhanced_content，數量: {len(enhanced_content.get('alternative_versions', []))}")
                    
            except Exception as e:
                print(f"⚠️ 增強版個人化節點失敗: {e}")
                # 回退到基本個人化處理
                personalized_title = original_title
                personalized_content = original_content
                enhanced_content['alternative_versions'] = []
                enhanced_content['generation_metadata'] = {}
            
            # 移除Markdown格式（用於社交媒體發布）
            import re
            def remove_markdown(text):
                """移除Markdown格式符號"""
                # 移除標題符號 ##
                text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
                # 移除粗體 **text**
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
                # 移除斜體 *text*
                text = re.sub(r'\*(.*?)\*', r'\1', text)
                # 移除程式碼區塊 ```
                text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
                # 移除行內程式碼 `code`
                text = re.sub(r'`([^`]*)`', r'\1', text)
                # 移除水平分隔線 ---
                text = re.sub(r'^[\-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
                # 移除連結 [text](url) 但保留文字
                text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
                # 移除圖片 ![alt](url)
                text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
                # 清理多餘的空行（最多保留兩個）
                text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
                return text.strip()
            
            # 更新enhanced_content
            personalized_content_no_md = remove_markdown(personalized_content)
            enhanced_content['title'] = personalized_title
            enhanced_content['content'] = personalized_content_no_md
            enhanced_content['content_md'] = personalized_content_no_md
            
            print(f"✅ 增強版個人化完成")
            print(f"✅ 個人化標題: {original_title} → {personalized_title}")
            print(f"✅ 個人化內容長度: {len(original_content)} → {len(personalized_content_no_md)} 字")
            print(f"✅ Markdown格式已移除")
            print(f"✅ 個人化內容前100字: {personalized_content_no_md[:100]}...")
            
        except Exception as e:
            print(f"⚠️ 增強版個人化節點失敗: {e}")
            # 如果個人化失敗，使用原始內容

        # 保存到數據庫 - 使用個人化後的 enhanced_content
        try:
            post_service = get_post_record_service()
            
            # 準備完整的貼文數據
            print(f"🔍 準備保存到數據庫的 topic_id: {topic_id}")
            print(f"🔍 準備保存到數據庫的 topic_title: {topic_title}")
            
            # 安全處理 kol_serial
            # 使用之前確定的kol_serial
            try:
                kol_serial_int = int(kol_serial)
                kol_nickname = f"KOL-{kol_serial}"
            except (ValueError, TypeError):
                kol_serial_int = 200
                kol_nickname = "KOL-200"
            
            # 獲取正確的 KOL persona
            actual_kol_persona = request.kol_persona
            try:
                # 嘗試從 KOL 服務獲取正確的 persona
                from kol_service import KOLService
                kol_service = KOLService()
                kol_profile = kol_service.get_kol_info(str(kol_serial_int))
                if kol_profile and kol_profile.get('persona'):
                    actual_kol_persona = kol_profile['persona']
                    print(f"🎯 使用 KOL 數據庫中的 persona: {actual_kol_persona}")
                else:
                    print(f"⚠️ 無法獲取 KOL {kol_serial_int} 的 persona，使用預設值: {actual_kol_persona}")
            except Exception as e:
                print(f"⚠️ 獲取 KOL persona 失敗: {e}，使用預設值: {actual_kol_persona}")
            
            post_data = {
                'session_id': request.session_id or 1,
                'kol_serial': kol_serial_int,
                'kol_nickname': kol_nickname,
                'kol_persona': actual_kol_persona,
                'stock_code': request.stock_code or "2330",
                'stock_name': stock_name,  # 使用從 stock_mapping 獲取的正確名稱
                'title': enhanced_content.get("title", f"【{kol_nickname}】{request.stock_name or '台積電'}({request.stock_code or '2330'}) 盤後分析"),
                'content': enhanced_content.get("content", ""),
                'content_md': enhanced_content.get("content_md", ""),
                'status': 'draft',
                'technical_analysis': enhanced_content.get("technical_analysis"),
                'serper_data': enhanced_content.get("serper_data"),
                'quality_score': enhanced_content.get("quality_score"),
                'ai_detection_score': enhanced_content.get("ai_detection_score"),
                'risk_level': enhanced_content.get("risk_level"),
                'topic_id': topic_id,  # 使用處理後的 topic_id
                'topic_title': topic_title,  # 使用處理後的 topic_title
                'trigger_type': request.trigger_type or 'manual',  # 添加觸發器類型
                'commodity_tags': [tag.model_dump() for tag in commodity_tag_models] if commodity_tag_models else [],
                'generation_params': json.dumps({
                    "method": "manual",  # 手動發文生成（步驟1-9）
                    "kol_persona": request.kol_persona,
                    "content_style": request.content_style,
                    "target_audience": request.target_audience,
                    "topic_id": topic_id,
                    "topic_title": topic_title,
                    "tag_mode": tag_mode,
                    "topic_tags_enabled": topic_tags_enabled,
                    "mixed_mode": mixed_mode_enabled,
                    "shared_commodity_tags": len(commodity_tags) if request.shared_commodity_tags else 0,
                    "trigger_type": request.trigger_type or 'manual',  # 在 generation_params 中也添加
                    "posting_type": posting_type,  # 🎲 新增：發文類型
                    "created_at": datetime.now(pytz.timezone('Asia/Taipei')).replace(tzinfo=None).isoformat()
                }),
                'alternative_versions': json.dumps(enhanced_content.get('alternative_versions', []))  # 🎲 新增：其他版本
            }
            
            print(f"🔍 完整的 post_data: {post_data}")
            print(f"💾 準備保存到數據庫的 alternative_versions: {len(enhanced_content.get('alternative_versions', []))} 個版本")
            
            # 創建完整的貼文記錄
            post_record = post_service.create_post_record(post_data)
            
            print(f"✅ 貼文記錄保存成功: {post_record.post_id}")
            enhanced_content["post_id"] = post_record.post_id
            enhanced_content["status"] = "draft"  # 設置為 draft 狀態，等待審核
            
            # 將 topic_id 和 topic_title 添加到 enhanced_content 中
            if topic_id:
                enhanced_content["topic_id"] = topic_id
                enhanced_content["topic_title"] = topic_title
                print(f"✅ 已更新 enhanced_content 中的話題信息: {topic_id} - {topic_title}")
            
        except Exception as db_error:
            print(f"❌ 保存貼文記錄失敗: {db_error}")
            enhanced_content["post_id"] = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            enhanced_content["status"] = "error"
            # 如果數據庫保存失敗，返回錯誤
            return PostingResult(
                success=False,
                error=f"數據庫保存失敗: {str(db_error)}",
                timestamp=datetime.now()
            )
        
        # 發文
        if request.auto_post:
            print("🚀 準備自動發文...")
            background_tasks = BackgroundTasks()
            background_tasks.add_task(post_to_platform, enhanced_content, {"id": request.post_to_thread})
            print("✅ 自動發文任務已加入背景任務")
        
        print(f"🎉 發文生成完成: {enhanced_content.get('post_id')}")
        
        # 將 commodity_tags 和 community_topic 添加到 enhanced_content 中
        enhanced_content["commodity_tags"] = [tag.model_dump() for tag in commodity_tag_models] if commodity_tag_models else []
        enhanced_content["community_topic"] = community_topic.model_dump() if community_topic else None
        
        print(f"✅ 已添加 commodity_tags: {len(enhanced_content['commodity_tags'])} 個")
        print(f"✅ 已添加 community_topic: {enhanced_content['community_topic']}")
        
        
        return PostingResult(
            success=True,
            post_id=enhanced_content.get("post_id", f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            content=enhanced_content,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        import traceback
        print(f"❌ manual_post_content 函數發生錯誤: {e}")
        print(f"❌ 錯誤詳情: {str(e)}")
        print(f"📋 錯誤堆疊: {traceback.format_exc()}")
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
    title = f"{stock_name} {persona['name']}觀點"
    
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
        news_section = "\n\n相關新聞素材\n"
        news_sources = []
        for i, news in enumerate(news_items[:5], 1):  # 取前5則新聞
            news_section += f"{news['title']}: {news['summary'][:100]}...\n\n"
            news_sources.append(f"{i}. {news['title']}\n   [閱讀更多]({news['url']})")
        
        # 在內容末尾加入新聞素材
        enhanced_content["content_md"] += news_section
        
        # 添加新聞來源到最後 - 避免重複添加
        if news_sources:
            # 檢查是否已經有新聞來源
            if "新聞來源:" not in enhanced_content["content_md"]:
                sources_section = "\n\n新聞來源:\n" + "\n".join(news_sources)
                enhanced_content["content_md"] += sources_section
            else:
                print("⚠️ 內容中已包含新聞來源，跳過重複添加")
        
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
        # 使用 KOL 服務載入憑證
        self.kol_credentials = {}
        self.kol_tokens = {}
        self._load_kol_credentials()
        
        print("🔐 KOL憑證管理器初始化完成")
    
    def _load_kol_credentials(self):
        """從 KOL 服務載入憑證"""
        try:
            from kol_service import kol_service
            
            # 獲取所有 KOL 憑證
            for serial in kol_service.get_all_kol_serials():
                creds = kol_service.get_kol_credentials(serial)
                if creds:
                    self.kol_credentials[str(serial)] = {
                        "email": creds["email"],
                        "password": creds["password"],
                        "member_id": creds["member_id"]
                    }
                    print(f"載入KOL憑證: {serial} - {creds['email']}")
            
            print(f"✅ 成功載入 {len(self.kol_credentials)} 個KOL憑證")
            
        except Exception as e:
            print(f"❌ 從KOL服務載入憑證失敗: {e}")
            # 使用預設憑證作為備用
            self.kol_credentials = {
                "200": {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x", "member_id": "9505546"},
                "201": {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t", "member_id": "9505547"},
                "202": {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p", "member_id": "9505548"},
                "203": {"email": "forum_203@cmoney.com.tw", "password": "D8k9mN2p", "member_id": "9505549"},
                "204": {"email": "forum_204@cmoney.com.tw", "password": "D8k9mN2p", "member_id": "9505550"},
                "205": {"email": "forum_205@cmoney.com.tw", "password": "Z5u6dL9o", "member_id": "9505551"},
                "206": {"email": "forum_206@cmoney.com.tw", "password": "T1t7kS9j", "member_id": "9505552"},
                "207": {"email": "forum_207@cmoney.com.tw", "password": "w2B3cF6l", "member_id": "9505553"},
                "208": {"email": "forum_208@cmoney.com.tw", "password": "q4N8eC7h", "member_id": "9505554"}
            }
            print("使用預設KOL憑證配置")
    
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
            from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
            cmoney_client = CMoneyClient()
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
async def get_all_posts(skip: int = 0, limit: int = 1000, status: Optional[str] = None):
    """獲取所有貼文"""
    try:
        posts = get_post_record_service().get_all_posts()
        
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
        posts = get_post_record_service().get_pending_review_posts()
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

@app.get("/posts/review-sidebar")
async def get_review_sidebar_data():
    """獲取發文審核 sidebar 頁面所需的數據"""
    try:
        # 獲取所有待審核貼文
        pending_posts = get_post_record_service().get_pending_review_posts()
        
        # 按 session 分組
        session_groups = {}
        for post in pending_posts:
            session_id = post.session_id
            if session_id not in session_groups:
                session_groups[session_id] = []
            session_groups[session_id].append(post)
        
        # 統計數據
        stats = {
            "total_pending": len(pending_posts),
            "sessions_count": len(session_groups),
            "latest_session": max(session_groups.keys()) if session_groups else None,
            "oldest_pending": min([post.created_at for post in pending_posts]) if pending_posts else None
        }
        
        # 準備 sidebar 數據
        sidebar_data = {
            "sessions": []
        }
        
        for session_id, posts in session_groups.items():
            session_info = {
                "session_id": session_id,
                "posts_count": len(posts),
                "latest_post": max([post.created_at for post in posts]),
                "kol_personas": list(set([post.kol_persona for post in posts])),
                "stock_codes": list(set([post.stock_code for post in posts if post.stock_code])),
                "posts": posts
            }
            sidebar_data["sessions"].append(session_info)
        
        # 按最新貼文時間排序
        sidebar_data["sessions"].sort(key=lambda x: x["latest_post"], reverse=True)
        
        return {
            "success": True,
            "stats": stats,
            "sidebar_data": sidebar_data,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        print(f"獲取審核 sidebar 數據失敗: {e}")
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
        test_result = serper_service.search_stock_news("2330", "台積電", limit=2, time_range="d2")
        
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
        all_posts = get_post_record_service().get_all_posts()
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
        all_posts = get_post_record_service().get_all_posts()
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
        posts = get_post_record_service().get_session_posts(session_id, status)
        print(f"✅ 找到 {len(posts)} 篇貼文")
        
        # 將 PostRecord 對象轉換為可序列化的字典
        posts_data = []
        for post in posts:
            post_data = {
                "post_id": post.post_id,
                "session_id": post.session_id,
                "kol_serial": post.kol_serial,
                "kol_nickname": post.kol_nickname,
                "kol_persona": post.kol_persona,
                "stock_code": post.stock_code,
                "stock_name": post.stock_name,
                "title": post.title,
                "content": post.content,
                "content_md": post.content_md,
                "status": post.status,
                "quality_score": post.quality_score,
                "ai_detection_score": post.ai_detection_score,
                "risk_level": post.risk_level,
                "reviewer_notes": post.reviewer_notes,
                "approved_by": post.approved_by,
                "approved_at": post.approved_at.isoformat() if post.approved_at else None,
                "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "cmoney_post_id": post.cmoney_post_id,
                "cmoney_post_url": post.cmoney_post_url,
                "publish_error": post.publish_error,
                "views": post.views,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "topic_id": post.topic_id,
                "topic_title": post.topic_title,
                "alternative_versions": post.alternative_versions,  # 新增：其他版本
                "generation_params": post.generation_params,  # 🔥 新增：生成參數
                "trigger_type": post.generation_params.get('trigger_type') if post.generation_params else None,  # 🔥 新增：觸發器類型
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None
            }
            posts_data.append(post_data)
        
        return {
            "success": True,
            "posts": posts_data,
            "count": len(posts_data),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
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
    
    # 導入必要的模組
    try:
        from smart_data_source_assigner import smart_assigner, KOLProfile, StockProfile
    except ImportError as e:
        print(f"❌ 導入模組失敗: {e}")
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'error': f'導入模組失敗: {e}'})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/plain")
    
    async def generate_posts():
        total_posts = len(request.posts)
        successful_posts = 0
        failed_posts = 0
        
        print(f"📊 批量生成統計: 總數={total_posts}, 成功={successful_posts}, 失敗={failed_posts}")
        
        # 生成 batch 級別的共享 commodity tags
        batch_commodity_tags = []
        
        # 檢查是否啟用「全貼同群股標」
        should_use_shared_tags = False
        
        # 優先檢查 tags_config 中的 batch_shared_tags 設定
        if request.tags_config and request.tags_config.get('stock_tags', {}).get('batch_shared_tags', False):
            should_use_shared_tags = True
            print("🏷️ 根據前端標籤配置啟用全貼同群股標")
        # 其次檢查 batch_config 中的 shared_commodity_tags 設定
        elif request.batch_config.get('shared_commodity_tags', True):
            should_use_shared_tags = True
            print("🏷️ 根據批量配置啟用共享標籤")
        
        if should_use_shared_tags:
            print("🏷️ 生成 batch 級別的共享 commodity tags...")
            unique_stocks = set()
            for post_data in request.posts:
                stock_code = post_data.get('stock_code')
                if stock_code:
                    unique_stocks.add(stock_code)
            
            # 為所有股票生成 commodity tags
            for stock_code in unique_stocks:
                batch_commodity_tags.append({
                    "type": "Stock",
                    "key": stock_code,
                    "bullOrBear": 0  # 預設中性
                })
            
            print(f"✅ 生成 {len(batch_commodity_tags)} 個共享 commodity tags: {[tag['key'] for tag in batch_commodity_tags]}")
        else:
            print("🏷️ 未啟用共享標籤，每個貼文將使用獨立標籤")
        
        # 發送開始事件
        yield f"data: {json.dumps({'type': 'batch_start', 'total': total_posts, 'session_id': request.session_id, 'shared_tags_count': len(batch_commodity_tags)})}\n\n"
        
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
                
                # 為熱門話題觸發器動態調整搜索關鍵字
                news_config = request.news_config.copy() if request.news_config else {}
                
                # 檢查是否為熱門話題觸發器且有具體話題
                topic_id = post_data.get('topic_id')
                topic_title = post_data.get('topic_title')
                
                if topic_id and topic_title:
                    print(f"🎯 為貼文動態調整搜索關鍵字 - 話題: {topic_title}")
                    
                    # 為這個特定話題生成搜索關鍵字
                    topic_keywords = [
                        {
                            "id": "1",
                            "keyword": "{stock_name}",
                            "type": "stock_name",
                            "description": "股票名稱"
                        },
                        {
                            "id": f"topic_{topic_id}",
                            "keyword": topic_title,
                            "type": "trigger_keyword",
                            "description": f"熱門話題關鍵字: {topic_title}"
                        }
                    ]
                    
                    news_config['search_keywords'] = topic_keywords
                    print(f"✅ 更新後的搜索關鍵字: {topic_keywords}")
                
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
                    news_config=news_config,  # 使用動態調整後的 news_config
                    tags_config=request.tags_config,  # 傳遞標籤配置
                    shared_commodity_tags=batch_commodity_tags  # 傳遞共享的 commodity tags
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
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {get_post_record_service().get_posts_count()}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: 無法獲取（PostgreSQL 模式）")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 解析請求內容
        body = await request.json()
        reviewer_notes = body.get("reviewer_notes")
        approved_by = body.get("approved_by", "system")
        
        logger.info(f"📝 審核參數 - 審核者: {approved_by}, 備註: {reviewer_notes}")
        
        # 創建更新資料
        update_data = {
            "status": "approved",
            "reviewer_notes": reviewer_notes,
            "approved_by": approved_by,
            "approved_at": datetime.now()
        }
        
        logger.info(f"🔄 開始更新貼文狀態 - Post ID: {post_id}")
        
        # 更新貼文記錄
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文審核成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            logger.info(f"📊 更新後資料庫狀態 - 總貼文數: {get_post_record_service().get_posts_count()}")
            
            return {
                "success": True,
                "message": "貼文審核通過",
                "post": {
                    "post_id": post_record.id,
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
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {get_post_record_service().get_posts_count()}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: 無法獲取（PostgreSQL 模式）")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 解析請求內容
        body = await request.json()
        reviewer_notes = body.get("reviewer_notes", "拒絕")
        
        logger.info(f"📝 拒絕參數 - 備註: {reviewer_notes}")
        
        # 創建更新資料
        update_data = {
            "status": "rejected",
            "reviewer_notes": reviewer_notes,
            "approved_by": "system"
        }
        
        logger.info(f"🔄 開始更新貼文狀態為拒絕 - Post ID: {post_id}")
        
        # 更新貼文記錄
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文拒絕成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            return {
                "success": True,
                "message": "貼文已拒絕",
                "post": {
                    "post_id": post_record.id,
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
        post_record = get_post_record_service().get_post_record(post_id)
        if not post_record:
            raise HTTPException(status_code=404, detail="貼文不存在")
        
        if post_record.status not in ["approved", "draft"]:
            raise HTTPException(status_code=400, detail=f"貼文狀態為 {post_record.status}，無法發文。只有已審核或草稿狀態的貼文才能發布")
        
        # 使用發佈服務發佈貼文
        from publish_service import publish_service
        publish_result = await publish_service.publish_post(post_record)
        
        # 更新貼文狀態為published
        update_data = {
            "status": "published",
            "published_at": datetime.now(),
            "cmoney_post_id": publish_result["post_id"],
            "cmoney_post_url": publish_result["post_url"]
        }
        
        updated_post = get_post_record_service().update_post_record(post_id, update_data)
        
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
        post_record = get_post_record_service().get_post_record(post_id)
        if post_record:
            logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 狀態: {post_record.status}")
            
            # 將貼文記錄轉換為可序列化的字典
            post_data = {
                "post_id": post_record.id,
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

@app.put("/posts/{post_id}/content")
async def update_post_content(post_id: str, content_data: dict):
    """更新貼文內容（用於版本選擇）"""
    logger.info(f"🔄 更新貼文內容請求 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前標題: {existing_post.title}")
        
        # 準備更新數據
        update_data = {
            'updated_at': datetime.now()
        }
        
        # 更新標題
        if 'title' in content_data:
            update_data['title'] = content_data['title']
            logger.info(f"📝 更新標題: {content_data['title']}")
        
        # 更新內容
        if 'content' in content_data:
            update_data['content'] = content_data['content']
            logger.info(f"📝 更新內容: {len(content_data['content'])} 字符")
        
        # 更新 Markdown 內容
        if 'content_md' in content_data:
            update_data['content_md'] = content_data['content_md']
        elif 'content' in content_data:
            # 如果沒有提供 content_md，使用 content 作為 content_md
            update_data['content_md'] = content_data['content']
        
        # 更新貼文記錄
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文內容更新成功 - Post ID: {post_id}")
            return {
                "success": True,
                "message": "貼文內容更新成功",
                "post_id": post_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 貼文內容更新失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新貼文內容失敗 - Post ID: {post_id}, 錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"更新失敗: {str(e)}")

@app.get("/posts/{post_id}/self-learning-data")
async def get_post_self_learning_data(post_id: str):
    """獲取貼文的自我學習數據 - 用於重建相同內容"""
    logger.info(f"🧠 獲取自我學習數據 - Post ID: {post_id}")
    
    try:
        post_record = get_post_record_service().get_post_record(post_id)
        if not post_record:
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        # 準備自我學習數據
        self_learning_data = {
            "post_id": post_record.id,
            "session_id": post_record.session_id,
            "kol_serial": post_record.kol_serial,
            "kol_nickname": post_record.kol_nickname,
            "kol_persona": post_record.kol_persona,
            "stock_code": post_record.stock_code,
            "stock_name": post_record.stock_name,
            
            # 生成參數 - 用於重建相同內容
            "generation_params": post_record.generation_params.model_dump() if post_record.generation_params else {},
            
            # 技術分析數據
            "technical_analysis": post_record.technical_analysis,
            
            # Serper 新聞數據
            "serper_data": post_record.serper_data,
            
            # 商品標籤
            "commodity_tags": [tag.model_dump() for tag in post_record.commodity_tags] if post_record.commodity_tags else [],
            
            # 社群話題
            "community_topic": post_record.community_topic.model_dump() if post_record.community_topic else None,
            
            # 品質評估數據
            "quality_score": post_record.quality_score,
            "ai_detection_score": post_record.ai_detection_score,
            "risk_level": post_record.risk_level,
            
            # 時間戳記
            "created_at": post_record.created_at.isoformat() if post_record.created_at else None,
            
            # 重建所需的其他參數
            "content_length": post_record.generation_params.content_style if post_record.generation_params else "chart_analysis",
            "target_audience": post_record.generation_params.target_audience if post_record.generation_params else "active_traders",
            "data_sources": post_record.generation_params.data_sources if post_record.generation_params else [],
            "technical_indicators": post_record.generation_params.technical_indicators if post_record.generation_params else []
        }
        
        logger.info(f"✅ 自我學習數據準備完成 - Post ID: {post_id}")
        logger.info(f"📊 數據包含: generation_params={bool(self_learning_data['generation_params'])}, "
                   f"technical_analysis={bool(self_learning_data['technical_analysis'])}, "
                   f"serper_data={bool(self_learning_data['serper_data'])}")
        
        return {
            "success": True,
            "self_learning_data": self_learning_data,
            "reconstruction_ready": bool(
                self_learning_data['generation_params'] and 
                self_learning_data['stock_code'] and 
                self_learning_data['kol_persona']
            ),
            
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 獲取自我學習數據時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"獲取自我學習數據失敗: {str(e)}")

@app.post("/test/kol-login/{kol_serial}")
async def test_kol_login(kol_serial: str):
    """測試 KOL 登入功能"""
    logger.info(f"🔐 測試 KOL 登入 - Serial: {kol_serial}")
    
    try:
        # 使用發佈服務測試登入
        from publish_service import publish_service
        
        # 測試登入
        access_token = await publish_service.login_kol(kol_serial)
        
        if access_token:
            logger.info(f"✅ KOL {kol_serial} 登入測試成功")
            return {
                "success": True,
                "message": f"KOL {kol_serial} 登入成功",
                "has_token": bool(access_token),
                "token_preview": access_token[:20] + "..." if access_token else None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ KOL {kol_serial} 登入測試失敗")
            return {
                "success": False,
                "message": f"KOL {kol_serial} 登入失敗",
                "error": "無法獲取 access token",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ KOL 登入測試異常: {e}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"KOL {kol_serial} 登入測試異常",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Delete API 已移至 routes/cmoney_routes.py

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
        title = f"{stock_name} 深度分析"
        
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
            # 從 serper_analysis 獲取新聞連結配置，如果沒有則使用預設值
            news_max_links = serper_analysis.get('news_max_links', 5)
            enable_news_links = serper_analysis.get('enable_news_links', True)
            
            if not enable_news_links:
                print("⚠️ 新聞連結已停用，跳過新聞來源整合")
                return enhanced_content
            
            print(f"🔗 整合 {len(news_items)} 則新聞到內容中 (最多 {news_max_links} 則)")
            
            # 提取新聞摘要和連結
            news_summary = []
            news_sources = []
            print(f"🔍 處理 {len(news_items)} 則新聞...")
            for i, news in enumerate(news_items[:news_max_links]):  # 根據配置取新聞數量
                title = news.get('title', '')
                snippet = news.get('snippet', '')
                link = news.get('link', '')
                print(f"  新聞 {i+1}: title='{title[:30]}...', snippet='{snippet[:30]}...', link='{link[:30]}...'")
                if title and snippet:
                    # 新聞摘要（簡化版，不包含emoji和markdown）
                    news_summary.append(f"{title}: {snippet[:100]}...")
                    # 新聞來源（用於最後的來源列表）
                    if link:
                        news_sources.append(f"{i+1}. {title}\n   連結: {link}")
                        print(f"    ✅ 添加新聞來源 {i+1} (有連結): {link}")
                    else:
                        news_sources.append(f"{i+1}. {title}")
                        print(f"    ✅ 添加新聞來源 {i+1} (無連結)")
                else:
                    print(f"    ❌ 跳過新聞 {i+1} (標題或摘要為空)")
            
            # 整合新聞到內容中
            original_content = enhanced_content.get('content', '')
            original_content_md = enhanced_content.get('content_md', '')
            
            # 不添加新聞摘要到內容開頭，只保留原始內容
            enhanced_content['content'] = original_content
            enhanced_content['content_md'] = original_content_md
            
            # 在內容最後添加新聞來源
            print(f"🔍 新聞來源列表: {len(news_sources)} 個")
            for i, source in enumerate(news_sources):
                print(f"   {i+1}. {source[:50]}...")
            
            if news_sources:
                # 檢查是否已經有新聞來源，避免重複添加
                if "新聞來源:" not in enhanced_content['content']:
                    sources_section = "\n\n新聞來源:\n" + "\n".join(news_sources)
                    enhanced_content['content'] += sources_section
                    enhanced_content['content_md'] += sources_section
                    print(f"✅ 新聞來源已添加: {len(sources_section)} 字")
                else:
                    print("⚠️ 內容中已包含新聞來源，跳過重複添加")
            else:
                print("⚠️ 沒有新聞來源可添加")
            
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

@app.post("/api/test-stock-filter")
async def test_stock_filter(trigger_type: str = "limit_up_after_hours", max_stocks: int = 5):
    """測試股票篩選服務"""
    try:
        from stock_filter_service import stock_filter_service
        
        stocks = await stock_filter_service.filter_stocks_by_trigger(
            trigger_type=trigger_type,
            max_stocks=max_stocks
        )
        
        return {
            "success": True,
            "trigger_type": trigger_type,
            "max_stocks": max_stocks,
            "stocks_count": len(stocks),
            "stocks": stocks
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

print("🎉 所有模組載入完成！")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

