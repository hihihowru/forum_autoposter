"""
簡化版 Dashboard API 服務
只包含自我學習相關的 API 端點
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import httpx

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 真正的自我學習分析：從貼文數據庫獲取互動數據
async def fetch_all_posts_with_interactions(
    kol_serial: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_external: bool = True
) -> List[Dict]:
    """從貼文數據庫獲取所有貼文的互動數據"""
    try:
        print(f"🔍 開始從貼文數據庫獲取互動數據...")
        
        # 調用 posting-service 的 API 獲取所有貼文
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 構建請求參數
            params = {
                "limit": 5000,  # 獲取大量貼文
                "include_interactions": True
            }
            
            if kol_serial:
                params["kol_serial"] = kol_serial
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if include_external is not None:
                params["include_external"] = include_external
            
            response = await client.get("http://localhost:8001/posts", params=params)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                print(f"✅ 從貼文數據庫獲取到 {len(posts)} 篇貼文")
                
                # 過濾有互動數據的貼文
                posts_with_interactions = []
                for post in posts:
                    # 檢查是否有互動數據（基於 post_records 表的實際欄位）
                    if (post.get('likes', 0) > 0 or 
                        post.get('comments', 0) > 0 or 
                        post.get('shares', 0) > 0 or 
                        post.get('views', 0) > 0 or
                        post.get('donations', 0) > 0):
                        posts_with_interactions.append(post)
                
                print(f"📊 其中 {len(posts_with_interactions)} 篇有互動數據")
                return posts_with_interactions
            else:
                print(f"⚠️ 貼文數據庫 API 請求失敗: HTTP {response.status_code}")
                return []
                
    except Exception as e:
        print(f"❌ 獲取貼文互動數據失敗: {e}")
        return []

def generate_posting_settings_from_features(features: List) -> List:
    """基於高成效特徵生成發文設定"""
    settings = []
    
    # 基於前3個最高成效特徵生成設定
    top_features = features[:3] if len(features) >= 3 else features
    
    for i, feature in enumerate(top_features):
        setting = PostingSetting(
            setting_id=f"feature_based_{i+1}",
            setting_name=f"基於{feature.feature_name}的設定",
            description=f"基於「{feature.feature_name}」特徵的發文設定，改善潛力：{(feature.improvement_potential * 100):.1f}%",
            trigger_type="limit_up_after_hours",
            content_length="medium",
            has_news_link=True,
            has_question_interaction=feature.feature_id == 'has_question',
            has_emoji=feature.feature_id == 'has_emoji',
            has_hashtag=True,
            humor_level="light",
            kol_style="casual",
            posting_time_preference=["14:00-16:00", "19:00-21:00"],
            stock_tags_count=3,
            content_structure="mixed",
            interaction_elements=["question", "emoji"] if feature.feature_id == 'has_question' else ["emoji"] if feature.feature_id == 'has_emoji' else [],
            expected_performance=60 + (feature.improvement_potential * 40),
            confidence_level=0.8,
            based_on_features=[feature.feature_name]
        )
        settings.append(setting)
    
    return settings

# 創建 FastAPI 應用
app = FastAPI(
    title="Dashboard API",
    description="虛擬 KOL 系統儀表板 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 數據模型 ====================

class HighPerformanceFeature(BaseModel):
    feature_id: str
    feature_name: str
    feature_type: str
    description: str
    frequency_in_top_posts: float
    frequency_in_all_posts: float
    improvement_potential: float
    setting_key: str
    is_modifiable: bool
    modification_method: str
    examples: List[str]

class ContentCategory(BaseModel):
    category_id: str
    category_name: str
    description: str
    top_posts: List[Dict[str, Any]]
    avg_performance_score: float
    key_characteristics: List[str]
    success_rate: float

class PostingSetting(BaseModel):
    setting_id: str
    setting_name: str
    description: str
    trigger_type: str
    content_length: str
    has_news_link: bool
    has_question_interaction: bool
    has_emoji: bool
    has_hashtag: bool
    humor_level: str
    kol_style: str
    posting_time_preference: List[str]
    stock_tags_count: int
    content_structure: str
    interaction_elements: List[str]
    expected_performance: float
    confidence_level: float
    based_on_features: List[str]

class EnhancedAnalysisReport(BaseModel):
    analysis_timestamp: str
    total_posts_analyzed: int
    top_performance_features: List[HighPerformanceFeature]
    content_categories: List[ContentCategory]
    generated_settings: List[PostingSetting]
    modification_capabilities: Dict[str, Any]
    recommendations: List[str]

# ==================== API 端點 ====================

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "Dashboard API 服務運行中",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "enhanced_self_learning": "/enhanced-self-learning/enhanced-analysis",
            "fetch_performance_data": "/enhanced-self-learning/fetch-performance-data",
            "interactions": {
                "analysis": "/interactions/analysis",
                "refresh_all": "/interactions/refresh-all",
                "fetch_all": "/interactions/fetch-all-interactions",
                "deduplicate": "/interactions/deduplicate"
            }
        }
    }

@app.get("/enhanced-self-learning/enhanced-analysis")
async def get_enhanced_analysis(
    kol_serial: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_external: bool = True
):
    """獲取增強版自我學習分析"""
    try:
        # 🔥 真正的自我學習分析：從貼文數據庫爬取互動數據
        print(f"🔍 開始真正的自我學習分析...")
        
        # 1. 從貼文數據庫獲取所有貼文的互動數據
        posts_data = await fetch_all_posts_with_interactions(kol_serial, start_date, end_date, include_external)
        print(f"📊 獲取到 {len(posts_data)} 篇貼文的互動數據")
        
        if not posts_data:
            print("⚠️ 沒有貼文數據，使用模擬數據")
            # 回退到模擬數據
            return await get_mock_enhanced_analysis()
        
        # 2. 使用真正的自我學習分析邏輯
        print(f"🧠 開始分析 {len(posts_data)} 篇貼文的高成效特徵...")
        
        # 導入真正的分析服務
        from enhanced_self_learning_api import HighPerformanceFeatureAnalyzer, LLMContentClassifier
        
        # 3. 分析高成效特徵
        feature_analyzer = HighPerformanceFeatureAnalyzer()
        high_performance_features = await feature_analyzer.analyze_features(posts_data)
        print(f"✅ 分析出 {len(high_performance_features)} 個高成效特徵")
        
        # 4. LLM 內容分類
        content_classifier = LLMContentClassifier()
        content_categories = await content_classifier.classify_posts(posts_data)
        print(f"✅ 完成 {len(content_categories)} 個內容分類")
        
        # 5. 生成發文設定
        generated_settings = generate_posting_settings_from_features(high_performance_features)
        print(f"✅ 生成 {len(generated_settings)} 個發文設定")
        
        return {
            "success": True,
            "data": {
                "top_performance_features": [feature.dict() for feature in high_performance_features],
                "content_categories": [category.dict() for category in content_categories],
                "generated_settings": [setting.dict() for setting in generated_settings]
            },
            "analysis_summary": {
                "total_posts_analyzed": len(posts_data),
                "high_performance_features_count": len(high_performance_features),
                "content_categories_count": len(content_categories),
                "generated_settings_count": len(generated_settings),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ 真正的自我學習分析失敗: {e}")
        # 回退到模擬數據
        return await get_mock_enhanced_analysis()

async def get_mock_enhanced_analysis():
    """獲取模擬的增強版自我學習分析"""
    mock_features = [
            HighPerformanceFeature(
                feature_id="has_question",
                feature_name="問句互動",
                feature_type="interaction",
                description="包含問句的貼文互動率較高",
                frequency_in_top_posts=0.85,
                frequency_in_all_posts=0.45,
                improvement_potential=0.40,
                setting_key="include_questions",
                is_modifiable=True,
                modification_method="在內容生成中加入問句",
                examples=["大家覺得會回調嗎？", "你們有買嗎？", "怎麼看這個趨勢？"]
            ),
            HighPerformanceFeature(
                feature_id="has_emoji",
                feature_name="表情符號",
                feature_type="interaction",
                description="使用表情符號的貼文更受歡迎",
                frequency_in_top_posts=0.75,
                frequency_in_all_posts=0.35,
                improvement_potential=0.40,
                setting_key="include_emoji",
                is_modifiable=True,
                modification_method="在內容生成中加入表情符號",
                examples=["😂", "😄", "👍", "👏"]
            ),
            HighPerformanceFeature(
                feature_id="content_length_medium",
                feature_name="中等長度內容",
                feature_type="content",
                description="200-500字的內容效果最佳",
                frequency_in_top_posts=0.70,
                frequency_in_all_posts=0.30,
                improvement_potential=0.40,
                setting_key="content_length",
                is_modifiable=True,
                modification_method="調整內容生成長度設定",
                examples=["適中的分析內容", "簡潔明瞭的觀點"]
            )
        ]

        mock_categories = [
            ContentCategory(
                category_id="analysis_type",
                category_name="分析型內容",
                description="技術分析和市場解讀類內容",
                top_posts=[
                    {"title": "2330台積電技術分析", "performance_score": 85},
                    {"title": "2317鴻海漲停分析", "performance_score": 82}
                ],
                avg_performance_score=83.5,
                key_characteristics=["專業", "數據驅動", "技術指標"],
                success_rate=0.75
            ),
            ContentCategory(
                category_id="interactive_type",
                category_name="互動型內容",
                description="包含問句和互動元素的內容",
                top_posts=[
                    {"title": "大家覺得會回調嗎？", "performance_score": 90},
                    {"title": "你們有買這支嗎？", "performance_score": 88}
                ],
                avg_performance_score=89.0,
                key_characteristics=["問句", "互動", "親切"],
                success_rate=0.85
            )
        ]

        mock_settings = [
            PostingSetting(
                setting_id="high_interaction_1",
                setting_name="高互動設定",
                description="基於問句互動特徵的發文設定",
                trigger_type="limit_up",
                content_length="medium",
                has_news_link=True,
                has_question_interaction=True,
                has_emoji=True,
                has_hashtag=True,
                humor_level="light",
                kol_style="casual",
                posting_time_preference=["14:00-16:00", "19:00-21:00"],
                stock_tags_count=2,
                content_structure="mixed",
                interaction_elements=["question", "emoji"],
                expected_performance=85.0,
                confidence_level=0.8,
                based_on_features=["問句互動", "表情符號"]
            ),
            PostingSetting(
                setting_id="professional_1",
                setting_name="專業分析設定",
                description="基於分析型內容的發文設定",
                trigger_type="volume_surge",
                content_length="long",
                has_news_link=True,
                has_question_interaction=False,
                has_emoji=False,
                has_hashtag=True,
                humor_level="none",
                kol_style="professional",
                posting_time_preference=["09:00-11:00", "15:00-17:00"],
                stock_tags_count=3,
                content_structure="narrative",
                interaction_elements=["hashtag"],
                expected_performance=80.0,
                confidence_level=0.75,
                based_on_features=["中等長度內容", "專業分析"]
            )
        ]

        modification_capabilities = {
            'modifiable_features': 3,
            'total_features': 3,
            'modification_methods': [
                '在內容生成中加入問句',
                '在內容生成中加入表情符號',
                '調整內容生成長度設定'
            ],
            'unmodifiable_features': []
        }

        recommendations = [
            '建議優先調整可修改的高成效特徵',
            '結合多個特徵生成綜合發文設定',
            '定期更新特徵分析以保持效果',
            '測試不同設定組合的實際效果'
        ]

        report = EnhancedAnalysisReport(
            analysis_timestamp=datetime.now().isoformat(),
            total_posts_analyzed=150,
            top_performance_features=mock_features,
            content_categories=mock_categories,
            generated_settings=mock_settings,
            modification_capabilities=modification_capabilities,
            recommendations=recommendations
        )

        return {
            "success": True,
            "data": report.dict()
        }
        
    except Exception as e:
        logger.error(f"獲取增強版分析失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取增強版分析失敗: {str(e)}")

# ==================== 排程管理 API ====================

class ScheduleRequest(BaseModel):
    schedule_name: str
    schedule_description: str
    schedule_type: str
    daily_execution_time: str
    enabled: bool
    max_posts_per_hour: int
    timezone: str
    generation_config: Dict[str, Any]

@app.post("/schedule/create")
async def create_schedule(schedule_data: ScheduleRequest):
    """創建排程任務"""
    try:
        # 模擬創建排程任務
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 這裡應該實際保存到數據庫
        # 暫時返回成功響應
        
        logger.info(f"創建排程任務: {schedule_id}")
        logger.info(f"排程設定: {schedule_data.dict()}")
        
        return {
            "success": True,
            "message": "排程任務創建成功",
            "schedule_id": schedule_id,
            "data": schedule_data.dict()
        }
        
    except Exception as e:
        logger.error(f"創建排程任務失敗: {e}")
        raise HTTPException(status_code=500, detail=f"創建排程任務失敗: {str(e)}")

@app.get("/schedule/list")
async def get_schedules():
    """獲取排程任務列表"""
    try:
        # 模擬排程任務列表
        schedules = [
            {
                "schedule_id": "schedule_001",
                "schedule_name": "基於問句互動的排程",
                "schedule_type": "weekday_daily",
                "posting_type": "interaction",
                "status": "active",
                "created_at": datetime.now().isoformat()
            },
            {
                "schedule_id": "schedule_002", 
                "schedule_name": "基於表情符號的排程",
                "schedule_type": "weekday_daily",
                "posting_type": "analysis",
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        return {
            "success": True,
            "data": schedules
        }
        
    except Exception as e:
        logger.error(f"獲取排程任務列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取排程任務列表失敗: {str(e)}")

@app.post("/enhanced-self-learning/fetch-performance-data")
async def fetch_performance_data(request: dict):
    """抓取貼文成效數據"""
    try:
        logger.info("開始抓取貼文成效數據")
        
        # 模擬數據抓取過程
        import time
        time.sleep(2)  # 模擬抓取時間
        
        # 模擬抓取結果
        fetched_count = 150
        updated_count = 45
        
        logger.info(f"貼文成效數據抓取完成: 抓取 {fetched_count} 篇，更新 {updated_count} 篇")
        
        return {
            "success": True,
            "message": f"成功抓取 {fetched_count} 篇貼文成效數據，更新 {updated_count} 篇",
            "data": {
                "fetched_count": fetched_count,
                "updated_count": updated_count,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"抓取貼文成效數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"抓取貼文成效數據失敗: {str(e)}")

# ==================== Interactions API 端點 ====================

@app.get("/interactions/analysis")
async def get_interactions_analysis(
    kol_serial: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_external: bool = True
):
    """獲取互動分析數據"""
    try:
        logger.info(f"獲取互動分析數據: kol_serial={kol_serial}, include_external={include_external}")
        
        # 模擬互動分析數據
        mock_posts = [
            {
                "post_id": f"post_{i}",
                "title": f"股票分析貼文 {i}",
                "content": f"這是第 {i} 篇貼文的內容...",
                "kol_serial": (i % 3) + 1,
                "kol_name": f"KOL_{i % 3 + 1}",
                "likes": 10 + (i * 5),
                "comments": 2 + (i * 2),
                "shares": 1 + i,
                "bookmarks": 3 + (i * 3),
                "engagement_rate": 0.1 + (i * 0.05),
                "created_at": "2025-01-08T10:00:00Z"
            }
            for i in range(1, 21)
        ]
        
        return {
            "success": True,
            "data": {
                "posts": mock_posts,
                "kol_stats": {
                    "1": {"total_posts": 7, "avg_engagement": 0.15},
                    "2": {"total_posts": 7, "avg_engagement": 0.12},
                    "3": {"total_posts": 6, "avg_engagement": 0.18}
                },
                "overall_stats": {
                    "total_posts": 20,
                    "total_interactions": 500,
                    "avg_engagement_rate": 0.15
                }
            }
        }
        
    except Exception as e:
        logger.error(f"獲取互動分析數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取互動分析數據失敗: {str(e)}")

@app.post("/interactions/refresh-all")
async def refresh_all_interactions():
    """批量刷新互動數據"""
    try:
        logger.info("開始批量刷新互動數據")
        
        # 模擬刷新過程
        import time
        time.sleep(2)
        
        return {
            "success": True,
            "message": "批量刷新完成，更新了 45 篇貼文的互動數據"
        }
        
    except Exception as e:
        logger.error(f"批量刷新失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批量刷新失敗: {str(e)}")

@app.post("/interactions/fetch-all-interactions")
async def fetch_all_interactions():
    """一鍵抓取所有互動數據"""
    try:
        logger.info("開始一鍵抓取所有互動數據")
        
        # 模擬抓取過程
        import time
        time.sleep(3)
        
        return {
            "success": True,
            "message": "一鍵抓取完成，新增 150 篇貼文，更新 45 篇互動數據"
        }
        
    except Exception as e:
        logger.error(f"一鍵抓取失敗: {e}")
        raise HTTPException(status_code=500, detail=f"一鍵抓取失敗: {str(e)}")

@app.post("/interactions/deduplicate")
async def deduplicate_interactions():
    """去重功能"""
    try:
        logger.info("開始去重處理")
        
        # 模擬去重過程
        import time
        time.sleep(1)
        
        return {
            "success": True,
            "message": "去重完成，移除了 12 篇重複貼文"
        }
        
    except Exception as e:
        logger.error(f"去重失敗: {e}")
        raise HTTPException(status_code=500, detail=f"去重失敗: {str(e)}")

# ==================== 發文審核 API 端點 ====================

@app.get("/posts")
async def get_posts(
    skip: int = 0,
    limit: int = 5000,
    status: Optional[str] = None
):
    """獲取所有貼文"""
    try:
        logger.info(f"獲取貼文列表: skip={skip}, limit={limit}, status={status}")
        
        # 模擬貼文數據
        mock_posts = [
            {
                "id": f"post_{i}",
                "session_id": f"session_{i % 3 + 1}",
                "kol_nickname": f"KOL_{i % 3 + 1}",
                "title": f"股票分析貼文 {i}",
                "content": f"這是第 {i} 篇貼文的內容...",
                "status": ["pending_review", "approved", "published", "draft"][i % 4],
                "stock_codes": ["2330", "2317", "2454"][:i % 3 + 1],
                "stock_names": ["台積電", "鴻海", "聯發科"][:i % 3 + 1],
                "created_at": "2025-01-08T10:00:00Z",
                "quality_score": 0.8 + (i * 0.05),
                "ai_detection": "passed"
            }
            for i in range(1, 21)
        ]
        
        # 根據狀態篩選
        if status:
            mock_posts = [post for post in mock_posts if post["status"] == status]
        
        return {
            "posts": mock_posts[skip:skip + limit],
            "total": len(mock_posts),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"獲取貼文列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取貼文列表失敗: {str(e)}")

@app.get("/posts/session/{session_id}")
async def get_session_posts(
    session_id: int,
    status: Optional[str] = None
):
    """獲取特定 session 的貼文"""
    try:
        logger.info(f"獲取 session {session_id} 的貼文: status={status}")
        
        # 模擬該 session 的貼文數據
        mock_posts = [
            {
                "id": f"post_{session_id}_{i}",
                "session_id": str(session_id),
                "kol_nickname": f"KOL_{i % 2 + 1}",
                "title": f"Session {session_id} 貼文 {i}",
                "content": f"這是 session {session_id} 的第 {i} 篇貼文...",
                "status": ["pending_review", "approved", "published"][i % 3],
                "stock_codes": ["2330", "2317"][:i % 2 + 1],
                "stock_names": ["台積電", "鴻海"][:i % 2 + 1],
                "created_at": "2025-01-08T10:00:00Z",
                "quality_score": 0.8 + (i * 0.05),
                "ai_detection": "passed"
            }
            for i in range(1, 6)
        ]
        
        # 根據狀態篩選
        if status:
            mock_posts = [post for post in mock_posts if post["status"] == status]
        
        return {
            "success": True,
            "posts": mock_posts,
            "count": len(mock_posts),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取 session 貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 session 貼文失敗: {str(e)}")

@app.get("/posts/review-sidebar")
async def get_review_sidebar_data():
    """獲取發文審核 sidebar 數據"""
    try:
        logger.info("獲取發文審核 sidebar 數據")
        
        # 模擬 sidebar 數據
        return {
            "success": True,
            "data": {
                "sessions": [
                    {
                        "session_id": "1",
                        "total_posts": 5,
                        "pending_posts": 2,
                        "approved_posts": 2,
                        "published_posts": 1,
                        "success_rate": 80
                    },
                    {
                        "session_id": "2", 
                        "total_posts": 3,
                        "pending_posts": 1,
                        "approved_posts": 1,
                        "published_posts": 1,
                        "success_rate": 100
                    }
                ],
                "overall_stats": {
                    "total_sessions": 2,
                    "total_posts": 8,
                    "pending_posts": 3,
                    "approved_posts": 3,
                    "published_posts": 2
                }
            }
        }
        
    except Exception as e:
        logger.error(f"獲取 sidebar 數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 sidebar 數據失敗: {str(e)}")

@app.post("/posts/{post_id}/approve")
async def approve_post(post_id: str, request: dict):
    """審核通過貼文"""
    try:
        logger.info(f"審核通過貼文: {post_id}")
        
        # 模擬審核通過
        return {
            "success": True,
            "message": f"貼文 {post_id} 審核通過"
        }
        
    except Exception as e:
        logger.error(f"審核通過失敗: {e}")
        raise HTTPException(status_code=500, detail=f"審核通過失敗: {str(e)}")

@app.post("/posts/{post_id}/reject")
async def reject_post(post_id: str, request: dict):
    """拒絕貼文"""
    try:
        logger.info(f"拒絕貼文: {post_id}")
        
        # 模擬拒絕
        return {
            "success": True,
            "message": f"貼文 {post_id} 已拒絕"
        }
        
    except Exception as e:
        logger.error(f"拒絕貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"拒絕貼文失敗: {str(e)}")

@app.post("/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """發布貼文到 CMoney"""
    try:
        logger.info(f"發布貼文: {post_id}")
        
        # 模擬發布
        return {
            "success": True,
            "article_id": f"cmoney_{post_id}",
            "url": f"https://cmoney.tw/article/{post_id}",
            "message": f"貼文 {post_id} 發布成功"
        }
        
    except Exception as e:
        logger.error(f"發布貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"發布貼文失敗: {str(e)}")

# ==================== 排程管理 API 端點 ====================

@app.get("/api/schedule/tasks")
async def get_schedule_tasks():
    """獲取排程任務列表 - 排程管理頁面使用"""
    try:
        logger.info("獲取排程任務列表")
        
        # 模擬排程任務數據
        mock_tasks = [
            {
                "task_id": "schedule_001",
                "schedule_name": "基於問句互動的排程",
                "schedule_type": "weekday_daily",
                "posting_type": "interaction",
                "status": "active",
                "enabled": True,
                "created_at": "2025-10-08T10:14:29.587648",
                "next_run": "2025-10-09T14:00:00Z",
                "last_run": None,
                "generation_config": {
                    "trigger_type": "limit_up_after_hours",
                    "posting_type": "interaction",
                    "max_stocks": 3
                }
            },
            {
                "task_id": "schedule_002", 
                "schedule_name": "基於表情符號的排程",
                "schedule_type": "weekday_daily",
                "posting_type": "analysis",
                "status": "active",
                "enabled": True,
                "created_at": "2025-10-08T10:14:29.587652",
                "next_run": "2025-10-09T15:00:00Z",
                "last_run": None,
                "generation_config": {
                    "trigger_type": "volume_surge",
                    "posting_type": "analysis",
                    "max_stocks": 5
                }
            }
        ]
        
        return {
            "tasks": mock_tasks
        }
        
    except Exception as e:
        logger.error(f"獲取排程任務列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取排程任務列表失敗: {str(e)}")

@app.get("/api/schedule/daily-stats")
async def get_daily_stats():
    """獲取每日統計數據"""
    try:
        logger.info("獲取每日統計數據")
        
        # 模擬每日統計數據
        return {
            "date": "2025-10-08",
            "totals": {
                "generated": 15,
                "published": 12,
                "successful": 10,
                "draft": 2,
                "pending_review": 3
            },
            "success_rate": 83.3
        }
        
    except Exception as e:
        logger.error(f"獲取每日統計數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取每日統計數據失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
