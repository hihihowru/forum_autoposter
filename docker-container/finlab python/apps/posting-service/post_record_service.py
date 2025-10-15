"""
簡化的貼文記錄服務 - 避免相對導入問題
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import logging
import json
import os
import psycopg2

# 配置日誌
logger = logging.getLogger(__name__)

# 簡化的數據模型
class PostStatus(str):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"

class CommodityTag:
    def __init__(self, type: str, key: str, bullOrBear: int):
        self.type = type
        self.key = key
        self.bullOrBear = bullOrBear
    
    def model_dump(self):
        return {
            "type": self.type,
            "key": self.key,
            "bullOrBear": self.bullOrBear
        }

class CommunityTopic:
    def __init__(self, id: str, title: Optional[str] = None):
        self.id = id
        self.title = title
    
    def model_dump(self):
        return {
            "id": self.id,
            "title": self.title
        }

class GenerationParams:
    def __init__(self, kol_persona: str, content_style: str, target_audience: str, 
                 batch_mode: bool, session_id: Optional[int] = None, 
                 technical_indicators: List[str] = None, data_sources: List[str] = None,
                 # 新增：百分比配置參數
                 article_type_distribution: Optional[Dict[str, int]] = None,
                 content_length_distribution: Optional[Dict[str, int]] = None,
                 content_style_distribution: Optional[Dict[str, int]] = None,
                 analysis_depth_distribution: Optional[Dict[str, int]] = None,
                 max_words: Optional[int] = None,
                 include_charts: Optional[bool] = None,
                 include_risk_warning: Optional[bool] = None,
                 # 新增：觸發器類型
                 trigger_type: Optional[str] = None):
        self.kol_persona = kol_persona
        self.content_style = content_style
        self.target_audience = target_audience
        self.batch_mode = batch_mode
        self.session_id = session_id
        self.technical_indicators = technical_indicators or []
        self.data_sources = data_sources or []
        # 新增：百分比配置參數
        self.article_type_distribution = article_type_distribution
        self.content_length_distribution = content_length_distribution
        self.content_style_distribution = content_style_distribution
        self.analysis_depth_distribution = analysis_depth_distribution
        self.max_words = max_words
        self.include_charts = include_charts
        self.include_risk_warning = include_risk_warning
        # 新增：觸發器類型
        self.trigger_type = trigger_type
    
    def model_dump(self):
        return {
            "kol_persona": self.kol_persona,
            "content_style": self.content_style,
            "target_audience": self.target_audience,
            "batch_mode": self.batch_mode,
            "session_id": self.session_id,
            "technical_indicators": self.technical_indicators,
            "data_sources": self.data_sources,
            # 新增：百分比配置參數
            "article_type_distribution": self.article_type_distribution,
            "content_length_distribution": self.content_length_distribution,
            "content_style_distribution": self.content_style_distribution,
            "analysis_depth_distribution": self.analysis_depth_distribution,
            "max_words": self.max_words,
            "include_charts": self.include_charts,
            "include_risk_warning": self.include_risk_warning,
            # 新增：觸發器類型
            "trigger_type": self.trigger_type
        }

class PostRecordCreate:
    def __init__(self, session_id: int, kol_serial: int, kol_nickname: str, 
                 kol_persona: str, stock_code: Optional[str] = None, 
                 stock_name: Optional[str] = None, title: str = "", 
                 content: str = "", content_md: Optional[str] = None,
                 commodity_tags: List[CommodityTag] = None, 
                 community_topic: Optional[CommunityTopic] = None,
                 status: str = PostStatus.PENDING_REVIEW,
                 generation_params: Optional[GenerationParams] = None,
                 quality_score: Optional[float] = None,
                 ai_detection_score: Optional[float] = None,
                 risk_level: Optional[str] = None,
                 reviewer_notes: Optional[str] = None,
                 approved_by: Optional[str] = None,
                 approved_at: Optional[datetime] = None,
                 scheduled_at: Optional[datetime] = None,
                 published_at: Optional[datetime] = None,
                 cmoney_post_id: Optional[str] = None,
                 cmoney_post_url: Optional[str] = None,
                 publish_error: Optional[str] = None,
                 views: int = 0, likes: int = 0, comments: int = 0, shares: int = 0,
                 topic_id: Optional[str] = None, topic_title: Optional[str] = None,
                 technical_analysis: Optional[Dict] = None,
                 serper_data: Optional[Dict] = None,
                 alternative_versions: Optional[List[Dict]] = None):
        self.session_id = session_id
        self.kol_serial = kol_serial
        self.kol_nickname = kol_nickname
        self.kol_persona = kol_persona
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.title = title
        self.content = content
        self.content_md = content_md
        self.commodity_tags = commodity_tags or []
        self.community_topic = community_topic
        self.status = status
        self.generation_params = generation_params
        self.quality_score = quality_score
        self.ai_detection_score = ai_detection_score
        self.risk_level = risk_level
        self.reviewer_notes = reviewer_notes
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.scheduled_at = scheduled_at
        self.published_at = published_at
        self.cmoney_post_id = cmoney_post_id
        self.cmoney_post_url = cmoney_post_url
        self.publish_error = publish_error
        self.views = views
        self.likes = likes
        self.comments = comments
        self.shares = shares
        self.topic_id = topic_id
        self.topic_title = topic_title
        self.technical_analysis = technical_analysis
        self.serper_data = serper_data
        self.alternative_versions = alternative_versions or []

class PostRecordInDB(PostRecordCreate):
    def __init__(self, post_id: str, created_at: datetime, updated_at: datetime, **kwargs):
        super().__init__(**kwargs)
        self.post_id = post_id
        self.created_at = created_at
        self.updated_at = updated_at

class PostRecordUpdate:
    def __init__(self, status: str = None, reviewer_notes: str = None, approved_by: str = None, 
                 approved_at: datetime = None, published_at: datetime = None, 
                 cmoney_post_id: str = None, cmoney_post_url: str = None):
        self.status = status
        self.reviewer_notes = reviewer_notes
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.published_at = published_at
        self.cmoney_post_id = cmoney_post_id
        self.cmoney_post_url = cmoney_post_url

class PostRecordService:
    """
    貼文記錄服務，負責與數據庫（目前為內存模擬）交互
    """
    def __init__(self):
        self.db_file = "/app/post_records/post_records.json"
        self.db: Dict[str, PostRecordInDB] = self.load_from_file()
    
    def load_from_file(self) -> Dict[str, PostRecordInDB]:
        """從文件載入數據"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 轉換回 PostRecordInDB 對象
                    result = {}
                    for post_id, post_data in data.items():
                        # 重建對象
                        post_record = PostRecordInDB(
                            post_id=post_id,
                            created_at=datetime.fromisoformat(post_data['created_at']),
                            updated_at=datetime.fromisoformat(post_data['updated_at']),
                            session_id=post_data.get('session_id'),
                            kol_serial=post_data.get('kol_serial'),
                            kol_nickname=post_data.get('kol_nickname'),
                            kol_persona=post_data.get('kol_persona'),
                            stock_code=post_data.get('stock_code'),
                            stock_name=post_data.get('stock_name'),
                            title=post_data.get('title'),
                            content=post_data.get('content'),
                            content_md=post_data.get('content_md'),
                            status=post_data.get('status', 'pending_review'),
                            reviewer_notes=post_data.get('reviewer_notes'),
                            approved_by=post_data.get('approved_by'),
                            approved_at=datetime.fromisoformat(post_data['approved_at']) if post_data.get('approved_at') else None,
                            published_at=datetime.fromisoformat(post_data['published_at']) if post_data.get('published_at') else None,
                            cmoney_post_id=post_data.get('cmoney_post_id'),
                            cmoney_post_url=post_data.get('cmoney_post_url'),
                            views=post_data.get('views', 0),
                            likes=post_data.get('likes', 0),
                            comments=post_data.get('comments', 0),
                            shares=post_data.get('shares', 0),
                            topic_id=post_data.get('topic_id'),
                            topic_title=post_data.get('topic_title'),
                            technical_analysis=post_data.get('technical_analysis'),
                            serper_data=post_data.get('serper_data'),
                            quality_score=post_data.get('quality_score'),
                            ai_detection_score=post_data.get('ai_detection_score'),
                            risk_level=post_data.get('risk_level')
                        )
                        result[post_id] = post_record
                    logger.info(f"📁 從文件載入 {len(result)} 筆貼文記錄")
                    return result
        except Exception as e:
            logger.error(f"❌ 載入文件失敗: {e}")
        return {}
    
    def save_to_file(self):
        """保存數據到文件"""
        try:
            data = {}
            for post_id, post_record in self.db.items():
                data[post_id] = {
                    'post_id': post_record.post_id,
                    'created_at': post_record.created_at.isoformat(),
                    'updated_at': post_record.updated_at.isoformat(),
                    'session_id': post_record.session_id,
                    'kol_serial': post_record.kol_serial,
                    'kol_nickname': post_record.kol_nickname,
                    'kol_persona': post_record.kol_persona,
                    'stock_code': post_record.stock_code,
                    'stock_name': post_record.stock_name,
                    'title': post_record.title,
                    'content': post_record.content,
                    'content_md': post_record.content_md,
                    'status': post_record.status,
                    'reviewer_notes': post_record.reviewer_notes,
                    'approved_by': post_record.approved_by,
                    'approved_at': post_record.approved_at.isoformat() if post_record.approved_at else None,
                    'published_at': post_record.published_at.isoformat() if post_record.published_at else None,
                    'cmoney_post_id': post_record.cmoney_post_id,
                    'cmoney_post_url': post_record.cmoney_post_url,
                    'views': post_record.views,
                    'likes': post_record.likes,
                    'comments': post_record.comments,
                    'shares': post_record.shares,
                    'topic_id': post_record.topic_id,
                    'topic_title': post_record.topic_title,
                    'technical_analysis': post_record.technical_analysis,
                    'serper_data': post_record.serper_data,
                    'quality_score': post_record.quality_score,
                    'ai_detection_score': post_record.ai_detection_score,
                    'risk_level': post_record.risk_level
                }
            
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 保存 {len(self.db)} 筆貼文記錄到文件")
        except Exception as e:
            logger.error(f"❌ 保存文件失敗: {e}")

    def create_post_record(self, post_data: PostRecordCreate) -> PostRecordInDB:
        post_id = str(uuid.uuid4())
        from timezone_utils import get_taiwan_utcnow
        now = get_taiwan_utcnow()
        
        # 調試：檢查post_data的屬性
        print(f"🔍 PostRecordCreate屬性: {post_data.__dict__}")
        print(f"🔍 status值: {getattr(post_data, 'status', 'NOT_FOUND')}")
        
        post_record = PostRecordInDB(
            post_id=post_id,
            created_at=now,
            updated_at=now,
            **post_data.__dict__
        )
        
        # 調試：檢查創建後的記錄
        print(f"🔍 PostRecordInDB status: {getattr(post_record, 'status', 'NOT_FOUND')}")
        
        # 1. 保存到內存
        self.db[post_id] = post_record
        
        # 2. 立即保存到 PostgreSQL 數據庫
        try:
            self.save_to_postgresql(post_record)
            logger.info(f"✅ 貼文記錄已保存到 PostgreSQL 數據庫 - Post ID: {post_id}")
        except Exception as e:
            logger.error(f"❌ 保存到 PostgreSQL 失敗: {e}")
            # 即使 PostgreSQL 失敗，也要保存到文件作為備份
            self.save_to_file()
        
        logger.info(f"✅ 貼文記錄創建並保存成功 - Post ID: {post_id}")
        return post_record

    def get_post_record(self, post_id: str) -> Optional[PostRecordInDB]:
        """獲取特定貼文記錄"""
        logger.info(f"🔍 查詢貼文記錄 - Post ID: {post_id}")
        post_record = self.db.get(post_id)
        if post_record:
            logger.info(f"✅ 找到貼文記錄 - Post ID: {post_id}, 狀態: {post_record.status}")
        else:
            logger.warning(f"❌ 貼文記錄不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {len(self.db)}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: {list(self.db.keys())}")
        return post_record

    def update_post_record(self, post_id: str, update_data: PostRecordUpdate) -> Optional[PostRecordInDB]:
        """更新貼文記錄"""
        logger.info(f"🔄 開始更新貼文記錄 - Post ID: {post_id}")
        logger.info(f"📝 更新資料: status={update_data.status}, reviewer_notes={update_data.reviewer_notes}, approved_by={update_data.approved_by}")
        
        post_record = self.db.get(post_id)
        if post_record:
            logger.info(f"✅ 找到要更新的貼文記錄 - Post ID: {post_id}, 當前狀態: {post_record.status}")
            
            # 更新字段
            if update_data.status is not None:
                old_status = post_record.status
                post_record.status = update_data.status
                logger.info(f"📝 更新狀態: {old_status} -> {update_data.status}")
            if update_data.reviewer_notes is not None:
                post_record.reviewer_notes = update_data.reviewer_notes
                logger.info(f"📝 更新審核備註: {update_data.reviewer_notes}")
            if update_data.approved_by is not None:
                post_record.approved_by = update_data.approved_by
                logger.info(f"📝 更新審核者: {update_data.approved_by}")
            if update_data.approved_at is not None:
                post_record.approved_at = update_data.approved_at
                logger.info(f"📝 更新審核時間: {update_data.approved_at}")
            if update_data.published_at is not None:
                post_record.published_at = update_data.published_at
                logger.info(f"📝 更新發布時間: {update_data.published_at}")
            if update_data.cmoney_post_id is not None:
                post_record.cmoney_post_id = update_data.cmoney_post_id
                logger.info(f"📝 更新CMoney貼文ID: {update_data.cmoney_post_id}")
            if update_data.cmoney_post_url is not None:
                post_record.cmoney_post_url = update_data.cmoney_post_url
                logger.info(f"📝 更新CMoney貼文URL: {update_data.cmoney_post_url}")
            
            post_record.updated_at = datetime.now()
            self.db[post_id] = post_record
            # 保存到文件
            self.save_to_file()
            logger.info(f"✅ 貼文記錄更新並保存成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            return post_record
        else:
            logger.error(f"❌ 找不到要更新的貼文記錄 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {len(self.db)}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: {list(self.db.keys())}")
        return None

    def get_pending_review_posts(self) -> List[PostRecordInDB]:
        return [post for post in self.db.values() if post.status == "pending_review"]

    def get_session_posts(self, session_id: int, status: Optional[str] = None) -> List[PostRecordInDB]:
        if status:
            return [post for post in self.db.values() if post.session_id == session_id and post.status == status]
        return [post for post in self.db.values() if post.session_id == session_id]
    
    def get_all_posts(self) -> List[PostRecordInDB]:
        """獲取所有貼文"""
        return list(self.db.values())

    def save_to_postgresql(self, post_record: PostRecordInDB):
        """保存貼文記錄到 PostgreSQL 數據庫"""
        try:
            import os
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'postgres-db'),
                port=int(os.getenv('POSTGRES_PORT', '5432')),
                database=os.getenv('POSTGRES_DB', 'posting_management'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'password')
            )
            cursor = conn.cursor()
            
            # 插入數據到 PostgreSQL (使用正確的表名 post_records)
            cursor.execute('''
                INSERT INTO post_records (
                    session_id, title, content, status, kol_serial, kol_nickname, kol_persona,
                    stock_codes, stock_names, topic_id, topic_title, cmoney_post_id, cmoney_url,
                    views, likes, comments, shares, reviewer_notes, approved_by, quality_score,
                    ai_detection_score, risk_level, publish_error, technical_analysis, serper_data,
                    generation_params, commodity_tags, created_at, updated_at, approved_at,
                    scheduled_at, published_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            ''', (
                post_record.session_id,
                post_record.title,
                post_record.content,
                post_record.status,
                post_record.kol_serial,
                post_record.kol_nickname,
                post_record.kol_persona,
                json.dumps([post_record.stock_code]) if post_record.stock_code else None,
                json.dumps([post_record.stock_name]) if post_record.stock_name else None,
                post_record.topic_id,
                post_record.topic_title,
                post_record.cmoney_post_id,
                post_record.cmoney_post_url,
                post_record.views,
                post_record.likes,
                post_record.comments,
                post_record.shares,
                post_record.reviewer_notes,
                post_record.approved_by,
                post_record.quality_score,
                post_record.ai_detection_score,
                post_record.risk_level,
                post_record.publish_error,
                json.dumps(post_record.technical_analysis) if post_record.technical_analysis else None,
                json.dumps(post_record.serper_data) if post_record.serper_data else None,
                post_record.generation_params if isinstance(post_record.generation_params, str) else json.dumps(post_record.generation_params),
                json.dumps(post_record.commodity_tags) if post_record.commodity_tags else None,
                post_record.created_at,
                post_record.updated_at,
                post_record.approved_at,
                post_record.scheduled_at,
                post_record.published_at
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 貼文記錄已保存到 PostgreSQL - Post ID: {post_record.post_id}")
            
        except Exception as e:
            logger.error(f"❌ 保存到 PostgreSQL 失敗: {e}")
            raise e

    def delete_post_record(self, post_id: str) -> bool:
        if post_id in self.db:
            del self.db[post_id]
            return True
        return False

# 添加 get_post_record_service 函數以修復導入錯誤
def get_post_record_service():
    """獲取PostgreSQL服務實例（延遲初始化）"""
    from postgresql_service import PostgreSQLPostRecordService
    return PostgreSQLPostRecordService()
