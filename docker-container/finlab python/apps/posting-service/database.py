"""
PostgreSQL 數據庫配置和模型
"""
import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, Boolean, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from timezone_utils import get_taiwan_utcnow

logger = logging.getLogger(__name__)

# 數據庫連接
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres-db:5432/posting_management")

# 延遲創建引擎，避免啟動時連接數據庫
engine = None
SessionLocal = None

def get_engine():
    """獲取數據庫引擎（延遲初始化）"""
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL, echo=True)
    return engine

def get_session_local():
    """獲取會話工廠（延遲初始化）"""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal

# 基礎模型
Base = declarative_base()

class PostRecord(Base):
    """貼文記錄表"""
    __tablename__ = "post_records"
    
    post_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=get_taiwan_utcnow)
    updated_at = Column(DateTime, default=get_taiwan_utcnow, onupdate=get_taiwan_utcnow)
    session_id = Column(Integer, nullable=True)
    kol_serial = Column(Integer, nullable=False)
    kol_nickname = Column(String, nullable=False)
    kol_persona = Column(String, nullable=True)
    stock_code = Column(String, nullable=False)
    stock_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_md = Column(Text, nullable=True)
    status = Column(String, default="draft")
    reviewer_notes = Column(Text, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    cmoney_post_id = Column(String, nullable=True)
    cmoney_post_url = Column(String, nullable=True)
    publish_error = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    topic_id = Column(String, nullable=True)
    topic_title = Column(String, nullable=True)
    technical_analysis = Column(JSON, nullable=True)
    serper_data = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=True)
    ai_detection_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    generation_params = Column(JSON, nullable=True)
    commodity_tags = Column(JSON, nullable=True)
    alternative_versions = Column(JSON, nullable=True)  # 存儲其他4個版本

class InvestmentBlogSyncState(Base):
    """投資網誌同步狀態表 - 追蹤最後同步的文章ID"""
    __tablename__ = "investment_blog_sync_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(String, nullable=False, unique=True, index=True)  # e.g., "newsyoudeservetoknow"
    last_seen_article_id = Column(String, nullable=True)  # UUID of the last synced article
    last_sync_at = Column(DateTime, nullable=True)
    articles_synced_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_taiwan_utcnow)
    updated_at = Column(DateTime, default=get_taiwan_utcnow, onupdate=get_taiwan_utcnow)


class InvestmentBlogArticle(Base):
    """投資網誌文章表 - 儲存已抓取的文章"""
    __tablename__ = "investment_blog_articles"

    id = Column(String, primary_key=True)  # CMoney article UUID
    author_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # Full article content
    stock_tags = Column(JSON, nullable=True)  # List of stock codes
    preview_img_url = Column(String, nullable=True)
    total_views = Column(Integer, default=0)
    cmoney_updated_at = Column(BigInteger, nullable=True)  # CMoney timestamp
    cmoney_created_at = Column(BigInteger, nullable=True)

    # Posting status
    status = Column(String, default="pending")  # pending, posted, skipped, failed
    posted_at = Column(DateTime, nullable=True)
    posted_by = Column(String, nullable=True)  # forum_190@cmoney.com.tw
    cmoney_post_id = Column(String, nullable=True)
    cmoney_post_url = Column(String, nullable=True)
    post_error = Column(Text, nullable=True)

    fetched_at = Column(DateTime, default=get_taiwan_utcnow)
    updated_at = Column(DateTime, default=get_taiwan_utcnow, onupdate=get_taiwan_utcnow)


def create_tables():
    """創建數據庫表"""
    try:
        Base.metadata.create_all(bind=get_engine())
        logger.info("✅ PostgreSQL 數據庫表創建成功")
    except Exception as e:
        logger.error(f"❌ 創建數據庫表失敗: {e}")
        raise

def get_db():
    """獲取數據庫會話"""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
