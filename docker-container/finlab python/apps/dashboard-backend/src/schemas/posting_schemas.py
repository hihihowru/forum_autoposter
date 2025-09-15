"""
發文管理系統的Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# ==================== 枚舉類型 ====================

class PostStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    FAILED = "failed"

class TriggerType(str, Enum):
    TRENDING_TOPIC = "trending_topic"
    LIMIT_UP_AFTER_HOURS = "limit_up_after_hours"
    INTRADAY_LIMIT_UP = "intraday_limit_up"
    CUSTOM_STOCKS = "custom_stocks"
    STOCK_CODE_LIST = "stock_code_list"
    NEWS_EVENT = "news_event"
    EARNINGS_REPORT = "earnings_report"

class PostMode(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"

class AssignmentMode(str, Enum):
    FIXED = "fixed"
    DYNAMIC = "dynamic"

# ==================== 基礎模型 ====================

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# ==================== 模板相關 ====================

class PostingTemplateBase(BaseSchema):
    name: str = Field(..., description="模板名稱")
    description: Optional[str] = Field(None, description="模板描述")
    trigger_type: TriggerType = Field(..., description="觸發器類型")
    data_sources: Dict[str, Any] = Field(default_factory=dict, description="數據源配置")
    explainability_config: Dict[str, Any] = Field(default_factory=dict, description="可解釋層配置")
    news_config: Dict[str, Any] = Field(default_factory=dict, description="新聞配置")
    kol_config: Dict[str, Any] = Field(default_factory=dict, description="KOL配置")
    generation_settings: Dict[str, Any] = Field(default_factory=dict, description="生成設定")
    tag_settings: Dict[str, Any] = Field(default_factory=dict, description="標籤設定")
    batch_mode_config: Dict[str, Any] = Field(default_factory=dict, description="批量模式配置")

class PostingTemplateCreate(PostingTemplateBase):
    pass

class PostingTemplateUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    data_sources: Optional[Dict[str, Any]] = None
    explainability_config: Optional[Dict[str, Any]] = None
    news_config: Optional[Dict[str, Any]] = None
    kol_config: Optional[Dict[str, Any]] = None
    generation_settings: Optional[Dict[str, Any]] = None
    tag_settings: Optional[Dict[str, Any]] = None
    batch_mode_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PostingTemplateResponse(PostingTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# ==================== 發文會話相關 ====================

class PostingSessionBase(BaseSchema):
    session_name: str = Field(..., description="會話名稱")
    trigger_type: TriggerType = Field(..., description="觸發器類型")
    trigger_data: Dict[str, Any] = Field(default_factory=dict, description="觸發器數據")
    template_id: Optional[int] = Field(None, description="模板ID")
    config: Dict[str, Any] = Field(default_factory=dict, description="完整配置")

class PostingSessionCreate(PostingSessionBase):
    pass

class PostingSessionResponse(PostingSessionBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

# ==================== 發文相關 ====================

class PostBase(BaseSchema):
    title: str = Field(..., description="標題")
    content: str = Field(..., description="內容")
    kol_serial: int = Field(..., description="KOL序號")
    kol_nickname: str = Field(..., description="KOL暱稱")
    kol_persona: Optional[str] = Field(None, description="KOL人設")
    stock_codes: Optional[List[str]] = Field(default_factory=list, description="股票代碼")
    stock_names: Optional[List[str]] = Field(default_factory=list, description="股票名稱")
    stock_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="股票數據")
    generation_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="生成配置")
    prompt_template: Optional[str] = Field(None, description="Prompt模板")
    technical_indicators: Optional[List[str]] = Field(default_factory=list, description="技術指標")

class PostCreate(PostBase):
    session_id: int = Field(..., description="會話ID")

class PostUpdate(BaseSchema):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[PostStatus] = None
    reviewer_notes: Optional[str] = None
    quality_score: Optional[float] = None
    ai_detection_score: Optional[float] = None
    risk_level: Optional[str] = None

class PostResponse(PostBase):
    id: int
    session_id: int
    status: PostStatus
    quality_score: Optional[float] = None
    ai_detection_score: Optional[float] = None
    risk_level: Optional[str] = None
    reviewer_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    cmoney_post_id: Optional[str] = None
    publish_error: Optional[str] = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    created_at: datetime
    updated_at: datetime

# ==================== Prompt模板相關 ====================

class PromptTemplateBase(BaseSchema):
    name: str = Field(..., description="模板名稱")
    description: Optional[str] = Field(None, description="模板描述")
    data_source: str = Field(..., description="適用數據源")
    template: str = Field(..., description="Prompt模板")
    variables: Optional[List[str]] = Field(default_factory=list, description="變數列表")
    technical_indicators: Optional[List[str]] = Field(default_factory=list, description="技術指標")

class PromptTemplateCreate(PromptTemplateBase):
    pass

class PromptTemplateResponse(PromptTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# ==================== KOL相關 ====================

class KOLProfileResponse(BaseSchema):
    id: int
    serial: int
    nickname: str
    name: Optional[str] = None
    persona: Optional[str] = None
    style_preference: Optional[str] = None
    expertise_areas: Optional[List[str]] = None
    activity_level: Optional[str] = None
    question_ratio: Optional[float] = None
    content_length: Optional[str] = None
    interaction_starters: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

# ==================== 分析相關 ====================

class PostingAnalyticsResponse(BaseSchema):
    id: int
    post_id: int
    date: datetime
    views: int
    likes: int
    comments: int
    shares: int
    engagement_rate: Optional[float] = None
    created_at: datetime

class AnalyticsSummary(BaseSchema):
    total_posts: int
    published_posts: int
    pending_review: int
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    avg_engagement_rate: float
    top_performing_kols: List[Dict[str, Any]]
    top_performing_posts: List[Dict[str, Any]]

# ==================== 請求/響應模型 ====================

class GeneratePostsRequest(BaseSchema):
    session_id: int
    max_posts: Optional[int] = Field(10, description="最大發文數量")
    force_regenerate: Optional[bool] = Field(False, description="強制重新生成")

class GeneratePostsResponse(BaseSchema):
    success: bool
    generated_count: int
    failed_count: int
    posts: List[PostResponse]
    errors: List[str]

class BatchOperationRequest(BaseSchema):
    post_ids: List[int]
    operation: str = Field(..., description="操作類型: approve, reject, publish")
    notes: Optional[str] = None

class BatchOperationResponse(BaseSchema):
    success: bool
    processed_count: int
    failed_count: int
    errors: List[str]
