"""
發文管理系統資料庫模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class PostStatus(str, Enum):
    """發文狀態"""
    DRAFT = "draft"           # 草稿
    PENDING_REVIEW = "pending_review"  # 待審核
    APPROVED = "approved"     # 已審核
    PUBLISHED = "published"   # 已發布
    REJECTED = "rejected"     # 已拒絕
    FAILED = "failed"         # 發布失敗

class TriggerType(str, Enum):
    """觸發器類型"""
    TRENDING_TOPIC = "trending_topic"
    LIMIT_UP_AFTER_HOURS = "limit_up_after_hours"
    INTRADAY_LIMIT_UP = "intraday_limit_up"
    CUSTOM_STOCKS = "custom_stocks"
    STOCK_CODE_LIST = "stock_code_list"  # 新增：股票代號列表
    NEWS_EVENT = "news_event"
    EARNINGS_REPORT = "earnings_report"

class PostMode(str, Enum):
    """發文模式"""
    ONE_TO_ONE = "one_to_one"      # 一對一
    ONE_TO_MANY = "one_to_many"    # 一對多

class AssignmentMode(str, Enum):
    """KOL分配模式"""
    FIXED = "fixed"           # 固定指派
    DYNAMIC = "dynamic"       # 動態派發

class PostingTemplate(Base):
    """發文模板"""
    __tablename__ = "posting_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50), nullable=False)
    data_sources = Column(JSON)  # 數據源配置
    explainability_config = Column(JSON)  # 可解釋層配置
    news_config = Column(JSON)  # 新聞配置
    kol_config = Column(JSON)  # KOL配置
    generation_settings = Column(JSON)  # 生成設定
    tag_settings = Column(JSON)  # 標籤設定
    batch_mode_config = Column(JSON)  # 批量模式配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PostingSession(Base):
    """發文會話"""
    __tablename__ = "posting_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(100), nullable=False)
    trigger_type = Column(String(50), nullable=False)
    trigger_data = Column(JSON)  # 觸發器數據
    template_id = Column(Integer, ForeignKey("posting_templates.id"))
    config = Column(JSON)  # 完整配置
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    template = relationship("PostingTemplate")
    posts = relationship("Post", back_populates="session")

class Post(Base):
    """發文記錄 - 對應Google Sheets和發文生成系統數據結構"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("posting_sessions.id"))
    
    # ==================== 基本發文資訊 ====================
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default=PostStatus.DRAFT)
    
    # ==================== KOL資訊 (對應Google Sheets) ====================
    kol_serial = Column(Integer, nullable=False)
    kol_nickname = Column(String(50), nullable=False)
    kol_name = Column(String(100))  # KOL真實姓名
    kol_persona = Column(String(100))  # KOL人設
    kol_style = Column(String(50))  # KOL風格
    kol_expertise = Column(JSON)  # KOL專業領域
    kol_question_ratio = Column(Float)  # 問題比例
    kol_content_length = Column(String(20))  # 內容長度偏好
    
    # ==================== 股票資訊 (對應Google Sheets) ====================
    stock_codes = Column(JSON)  # 股票代碼列表
    stock_names = Column(JSON)  # 股票名稱列表
    stock_data = Column(JSON)  # 股票數據 (價格、漲跌幅等)
    stock_analysis_angle = Column(String(100))  # 分析角度
    stock_technical_signals = Column(JSON)  # 技術訊號
    
    # ==================== 觸發器資訊 ====================
    trigger_type = Column(String(50))  # 觸發器類型
    trigger_data = Column(JSON)  # 觸發器數據
    topic_title = Column(String(200))  # 話題標題
    topic_keywords = Column(JSON)  # 話題關鍵字
    
    # ==================== 生成配置 (發文生成系統各階段) ====================
    generation_config = Column(JSON)  # 完整生成配置
    
    # 數據源配置
    data_sources = Column(JSON)  # 使用的數據源
    explainability_config = Column(JSON)  # 可解釋層配置
    news_config = Column(JSON)  # 新聞配置
    news_links = Column(JSON)  # 新聞連結列表
    
    # Prompting配置
    prompt_template = Column(Text)  # 使用的prompt模板
    prompt_template_id = Column(Integer)  # Prompt模板ID
    technical_indicators = Column(JSON)  # 技術指標
    custom_prompt = Column(Text)  # 自定義prompt
    
    # 生成設定
    post_mode = Column(String(20))  # 發文模式 (one_to_one, one_to_many)
    content_length = Column(String(20))  # 內容長度
    content_style = Column(String(50))  # 內容風格
    max_words = Column(Integer)  # 最大字數
    include_analysis_depth = Column(Boolean)  # 包含分析深度
    include_charts = Column(Boolean)  # 包含圖表
    include_risk_warning = Column(Boolean)  # 包含風險警告
    
    # 標籤設定
    tag_settings = Column(JSON)  # 標籤配置
    stock_tags = Column(JSON)  # 股票標籤
    topic_tags = Column(JSON)  # 話題標籤
    
    # ==================== 品質檢查 (對應Google Sheets) ====================
    quality_score = Column(Float)  # 品質分數
    ai_detection_score = Column(Float)  # AI檢測分數
    ai_detection_result = Column(String(20))  # AI檢測結果 (passed, warning, failed)
    risk_level = Column(String(20))  # 風險等級 (low, medium, high)
    content_quality_issues = Column(JSON)  # 內容品質問題
    
    # ==================== 審核資訊 (對應Google Sheets) ====================
    reviewer_notes = Column(Text)  # 審核備註
    reviewer_suggestions = Column(Text)  # 審核建議
    approved_by = Column(String(50))  # 審核人
    approved_at = Column(DateTime)  # 審核時間
    review_status = Column(String(20))  # 審核狀態
    
    # ==================== 發布資訊 (對應Google Sheets) ====================
    published_at = Column(DateTime)  # 發布時間
    cmoney_post_id = Column(String(50))  # CMoney發文ID
    cmoney_url = Column(String(200))  # CMoney發文連結
    publish_error = Column(Text)  # 發布錯誤訊息
    publish_attempts = Column(Integer, default=0)  # 發布嘗試次數
    
    # ==================== 互動數據 (對應Google Sheets) ====================
    views = Column(Integer, default=0)  # 瀏覽數
    likes = Column(Integer, default=0)  # 讚數
    comments = Column(Integer, default=0)  # 留言數
    shares = Column(Integer, default=0)  # 分享數
    engagement_rate = Column(Float)  # 互動率
    interaction_data = Column(JSON)  # 詳細互動數據
    
    # ==================== 學習機制數據 ====================
    performance_score = Column(Float)  # 表現分數
    learning_feedback = Column(JSON)  # 學習反饋
    improvement_suggestions = Column(JSON)  # 改進建議
    
    # ==================== 時間戳 ====================
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_at = Column(DateTime)  # 生成時間
    scheduled_at = Column(DateTime)  # 排程時間
    
    # ==================== 關聯 ====================
    session = relationship("PostingSession", back_populates="posts")

class PromptTemplate(Base):
    """Prompt模板"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    data_source = Column(String(50), nullable=False)  # 適用數據源
    template = Column(Text, nullable=False)  # prompt模板
    variables = Column(JSON)  # 變數列表
    technical_indicators = Column(JSON)  # 技術指標
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KOLProfile(Base):
    """KOL檔案"""
    __tablename__ = "kol_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    serial = Column(Integer, unique=True, nullable=False)
    nickname = Column(String(50), nullable=False)
    name = Column(String(100))
    persona = Column(String(100))
    style_preference = Column(String(50))
    expertise_areas = Column(JSON)  # 專業領域
    activity_level = Column(String(20))
    question_ratio = Column(Float, default=0.5)
    content_length = Column(String(20), default="medium")
    interaction_starters = Column(JSON)  # 互動開場詞
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PostingAnalytics(Base):
    """發文分析"""
    __tablename__ = "posting_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    date = Column(DateTime, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float)  # 互動率
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    post = relationship("Post")

class SystemConfig(Base):
    """系統配置"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
