"""
貼文記錄數據庫服務
整合原本主架構的數據存儲邏輯
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..models.post_record import PostRecord, PostRecordCreate, PostRecordUpdate, PostStatus

logger = logging.getLogger(__name__)

Base = declarative_base()

class PostRecordDB(Base):
    """貼文記錄數據庫模型"""
    __tablename__ = "post_records"
    
    # 基礎信息
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), unique=True, index=True, nullable=False)
    session_id = Column(Integer, nullable=False)
    
    # KOL信息
    kol_serial = Column(Integer, nullable=False)
    kol_nickname = Column(String(100), nullable=False)
    kol_persona = Column(String(50), nullable=False)
    
    # 股票信息
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(100), nullable=False)
    
    # 話題信息
    topic_id = Column(String(255), nullable=True)
    topic_title = Column(String(500), nullable=True)
    
    # 內容信息
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_md = Column(Text, nullable=True)
    
    # 標籤和話題 (JSON格式存儲)
    commodity_tags = Column(JSON, nullable=True)
    community_topic = Column(JSON, nullable=True)
    
    # 狀態管理
    status = Column(String(50), default=PostStatus.PENDING_REVIEW)
    quality_score = Column(Float, nullable=True)
    ai_detection_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    
    # 審核信息
    reviewer_notes = Column(Text, nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # 發布信息
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    cmoney_post_id = Column(String(100), nullable=True)
    cmoney_post_url = Column(String(500), nullable=True)
    publish_error = Column(Text, nullable=True)
    
    # 生成參數 (JSON格式存儲)
    generation_params = Column(JSON, nullable=False)
    technical_analysis = Column(JSON, nullable=True)
    
    # 互動數據
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class PostRecordService:
    """貼文記錄服務"""
    
    def __init__(self, database_url: str = None):
        """初始化數據庫連接"""
        if database_url is None:
            # 使用共享的資料庫檔案
            import os
            database_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "post_records.db")
            database_url = f"sqlite:///{database_path}"
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
        
        logger.info("貼文記錄服務初始化完成")
    
    def _db_to_model(self, db_record: PostRecordDB) -> PostRecord:
        """將數據庫記錄轉換為模型"""
        return PostRecord(
            post_id=db_record.post_id,
            session_id=db_record.session_id,
            kol_serial=db_record.kol_serial,
            kol_nickname=db_record.kol_nickname,
            kol_persona=db_record.kol_persona,
            stock_code=db_record.stock_code,
            stock_name=db_record.stock_name,
            topic_id=db_record.topic_id,
            topic_title=db_record.topic_title,
            title=db_record.title,
            content=db_record.content,
            content_md=db_record.content_md,
            commodity_tags=db_record.commodity_tags or [],
            community_topic=db_record.community_topic,
            status=PostStatus(db_record.status),
            quality_score=db_record.quality_score,
            ai_detection_score=db_record.ai_detection_score,
            risk_level=db_record.risk_level,
            reviewer_notes=db_record.reviewer_notes,
            approved_by=db_record.approved_by,
            approved_at=db_record.approved_at,
            scheduled_at=db_record.scheduled_at,
            published_at=db_record.published_at,
            cmoney_post_id=db_record.cmoney_post_id,
            cmoney_post_url=db_record.cmoney_post_url,
            publish_error=db_record.publish_error,
            generation_params=db_record.generation_params,
            technical_analysis=db_record.technical_analysis,
            views=db_record.views,
            likes=db_record.likes,
            comments=db_record.comments,
            shares=db_record.shares,
            created_at=db_record.created_at,
            updated_at=db_record.updated_at
        )
    
    def _model_to_db(self, post_record: PostRecord) -> PostRecordDB:
        """將模型轉換為數據庫記錄"""
        return PostRecordDB(
            post_id=post_record.post_id,
            session_id=post_record.session_id,
            kol_serial=post_record.kol_serial,
            kol_nickname=post_record.kol_nickname,
            kol_persona=post_record.kol_persona,
            stock_code=post_record.stock_code,
            stock_name=post_record.stock_name,
            topic_id=post_record.topic_id,
            topic_title=post_record.topic_title,
            title=post_record.title,
            content=post_record.content,
            content_md=post_record.content_md,
            commodity_tags=post_record.commodity_tags,
            community_topic=post_record.community_topic,
            status=post_record.status.value,
            quality_score=post_record.quality_score,
            ai_detection_score=post_record.ai_detection_score,
            risk_level=post_record.risk_level,
            reviewer_notes=post_record.reviewer_notes,
            approved_by=post_record.approved_by,
            approved_at=post_record.approved_at,
            scheduled_at=post_record.scheduled_at,
            published_at=post_record.published_at,
            cmoney_post_id=post_record.cmoney_post_id,
            cmoney_post_url=post_record.cmoney_post_url,
            publish_error=post_record.publish_error,
            generation_params=post_record.generation_params,
            technical_analysis=post_record.technical_analysis,
            views=post_record.views,
            likes=post_record.likes,
            comments=post_record.comments,
            shares=post_record.shares,
            created_at=post_record.created_at,
            updated_at=post_record.updated_at
        )
    
    def create_post_record(self, post_data: PostRecordCreate) -> PostRecord:
        """創建貼文記錄"""
        try:
            # 生成唯一post_id
            post_id = f"{post_data.session_id}_{post_data.kol_serial}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 創建PostRecord對象
            post_record = PostRecord(
                post_id=post_id,
                session_id=post_data.session_id,
                kol_serial=post_data.kol_serial,
                kol_nickname=post_data.kol_nickname,
                kol_persona=post_data.kol_persona,
                stock_code=post_data.stock_code,
                stock_name=post_data.stock_name,
                topic_id=post_data.topic_id,
                topic_title=post_data.topic_title,
                title=post_data.title,
                content=post_data.content,
                content_md=post_data.content_md,
                commodity_tags=post_data.commodity_tags,
                community_topic=post_data.community_topic,
                generation_params=post_data.generation_params,
                technical_analysis=post_data.technical_analysis,
                status=PostStatus.PENDING_REVIEW
            )
            
            # 轉換為數據庫記錄並保存
            db_record = self._model_to_db(post_record)
            self.db.add(db_record)
            self.db.commit()
            self.db.refresh(db_record)
            
            logger.info(f"創建貼文記錄成功: {post_id}")
            return self._db_to_model(db_record)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"創建貼文記錄失敗: {e}")
            raise
    
    def get_post_record(self, post_id: str) -> Optional[PostRecord]:
        """獲取貼文記錄"""
        try:
            db_record = self.db.query(PostRecordDB).filter(PostRecordDB.post_id == post_id).first()
            if db_record:
                return self._db_to_model(db_record)
            return None
        except Exception as e:
            logger.error(f"獲取貼文記錄失敗: {e}")
            raise
    
    def get_session_posts(self, session_id: int, status: Optional[PostStatus] = None) -> List[PostRecord]:
        """獲取會話的所有貼文"""
        try:
            query = self.db.query(PostRecordDB).filter(PostRecordDB.session_id == session_id)
            if status:
                query = query.filter(PostRecordDB.status == status.value)
            
            db_records = query.all()
            return [self._db_to_model(record) for record in db_records]
        except Exception as e:
            logger.error(f"獲取會話貼文失敗: {e}")
            raise
    
    def update_post_record(self, post_id: str, update_data: PostRecordUpdate) -> Optional[PostRecord]:
        """更新貼文記錄"""
        try:
            db_record = self.db.query(PostRecordDB).filter(PostRecordDB.post_id == post_id).first()
            if not db_record:
                return None
            
            # 更新字段
            if update_data.status:
                db_record.status = update_data.status.value
            if update_data.reviewer_notes is not None:
                db_record.reviewer_notes = update_data.reviewer_notes
            if update_data.approved_by:
                db_record.approved_by = update_data.approved_by
                db_record.approved_at = datetime.now()
            if update_data.scheduled_at:
                db_record.scheduled_at = update_data.scheduled_at
            if update_data.quality_score is not None:
                db_record.quality_score = update_data.quality_score
            if update_data.ai_detection_score is not None:
                db_record.ai_detection_score = update_data.ai_detection_score
            if update_data.risk_level:
                db_record.risk_level = update_data.risk_level
            
            db_record.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(db_record)
            
            logger.info(f"更新貼文記錄成功: {post_id}")
            return self._db_to_model(db_record)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新貼文記錄失敗: {e}")
            raise
    
    def get_all_posts(self) -> List[PostRecord]:
        """獲取所有貼文"""
        try:
            db_records = self.db.query(PostRecordDB).all()
            return [self._db_to_model(record) for record in db_records]
        except Exception as e:
            logger.error(f"獲取所有貼文失敗: {e}")
            raise
    
    def get_pending_review_posts(self) -> List[PostRecord]:
        """獲取待審核的貼文"""
        try:
            db_records = self.db.query(PostRecordDB).filter(
                PostRecordDB.status == PostStatus.PENDING_REVIEW.value
            ).all()
            return [self._db_to_model(record) for record in db_records]
        except Exception as e:
            logger.error(f"獲取待審核貼文失敗: {e}")
            raise
    
    def get_approved_posts(self) -> List[PostRecord]:
        """獲取已審核的貼文"""
        try:
            db_records = self.db.query(PostRecordDB).filter(
                PostRecordDB.status == PostStatus.APPROVED.value
            ).all()
            return [self._db_to_model(record) for record in db_records]
        except Exception as e:
            logger.error(f"獲取已審核貼文失敗: {e}")
            raise
    
    def batch_create_posts(self, posts_data: List[PostRecordCreate]) -> List[PostRecord]:
        """批量創建貼文記錄"""
        try:
            created_posts = []
            for post_data in posts_data:
                post_record = self.create_post_record(post_data)
                created_posts.append(post_record)
            
            logger.info(f"批量創建貼文記錄成功: {len(created_posts)} 篇")
            return created_posts
            
        except Exception as e:
            logger.error(f"批量創建貼文記錄失敗: {e}")
            raise
    
    def delete_post_record(self, post_id: str) -> bool:
        """刪除貼文記錄"""
        try:
            db_record = self.db.query(PostRecordDB).filter(PostRecordDB.post_id == post_id).first()
            if db_record:
                self.db.delete(db_record)
                self.db.commit()
                logger.info(f"刪除貼文記錄成功: {post_id}")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"刪除貼文記錄失敗: {e}")
            raise

