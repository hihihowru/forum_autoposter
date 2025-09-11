"""
簡化的貼文記錄服務 - 避免相對導入問題
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import logging

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
                 technical_indicators: List[str] = None, data_sources: List[str] = None):
        self.kol_persona = kol_persona
        self.content_style = content_style
        self.target_audience = target_audience
        self.batch_mode = batch_mode
        self.session_id = session_id
        self.technical_indicators = technical_indicators or []
        self.data_sources = data_sources or []
    
    def model_dump(self):
        return {
            "kol_persona": self.kol_persona,
            "content_style": self.content_style,
            "target_audience": self.target_audience,
            "batch_mode": self.batch_mode,
            "session_id": self.session_id,
            "technical_indicators": self.technical_indicators,
            "data_sources": self.data_sources
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
                 serper_data: Optional[Dict] = None):
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
        self.db: Dict[str, PostRecordInDB] = {} # 模擬數據庫

    def create_post_record(self, post_data: PostRecordCreate) -> PostRecordInDB:
        post_id = str(uuid.uuid4())
        now = datetime.now()
        
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
        
        self.db[post_id] = post_record
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
            logger.info(f"✅ 貼文記錄更新成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
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

    def delete_post_record(self, post_id: str) -> bool:
        if post_id in self.db:
            del self.db[post_id]
            return True
        return False
