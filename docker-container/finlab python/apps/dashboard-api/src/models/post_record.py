"""
貼文記錄數據模型
整合原本主架構的完整數據結構
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class PostStatus(str, Enum):
    """貼文狀態枚舉"""
    PENDING_REVIEW = "pending_review"      # 待審核
    APPROVED = "approved"                  # 已審核
    PUBLISHED = "published"                # 已發布
    REJECTED = "rejected"                  # 已拒絕
    FAILED = "failed"                      # 發布失敗
    SCHEDULED = "scheduled"                # 已排程

class CommodityTag(BaseModel):
    """商品標籤"""
    type: str = Field(..., description="標籤類型，如 'Stock'")
    key: str = Field(..., description="股票代號")
    bullOrBear: int = Field(default=0, description="多空方向，0=中性，1=看多，-1=看空")

class CommunityTopic(BaseModel):
    """社群話題"""
    id: str = Field(..., description="話題ID")
    title: Optional[str] = Field(None, description="話題標題")

class GenerationParams(BaseModel):
    """生成參數"""
    kol_persona: str = Field(..., description="KOL人設")
    content_style: str = Field(..., description="內容風格")
    target_audience: str = Field(..., description="目標受眾")
    batch_mode: bool = Field(default=False, description="是否批量模式")
    session_id: Optional[int] = Field(None, description="會話ID")
    generation_strategy: Optional[str] = Field(None, description="生成策略")
    technical_indicators: List[str] = Field(default_factory=list, description="技術指標")
    data_sources: List[str] = Field(default_factory=list, description="數據來源")

class TechnicalAnalysis(BaseModel):
    """技術分析數據"""
    ma5: Optional[float] = Field(None, description="5日均線")
    ma20: Optional[float] = Field(None, description="20日均線")
    rsi14: Optional[float] = Field(None, description="14日RSI")
    macd: Optional[Dict[str, float]] = Field(None, description="MACD指標")
    signals: List[Dict[str, Any]] = Field(default_factory=list, description="技術信號")
    overall_score: Optional[float] = Field(None, description="整體評分")

class PostRecord(BaseModel):
    """貼文記錄 - 整合原本主架構的完整數據結構"""
    
    # 基礎信息
    post_id: str = Field(..., description="唯一標識符")
    session_id: int = Field(..., description="發文會話ID")
    
    # KOL信息
    kol_serial: int = Field(..., description="KOL序號")
    kol_nickname: str = Field(..., description="KOL暱稱")
    kol_persona: str = Field(..., description="KOL人設")
    
    # 股票信息
    stock_code: str = Field(..., description="股票代號")
    stock_name: str = Field(..., description="股票名稱")
    
    # 話題信息
    topic_id: Optional[str] = Field(None, description="話題ID")
    topic_title: Optional[str] = Field(None, description="話題標題")
    
    # 內容信息
    title: str = Field(..., description="生成標題")
    content: str = Field(..., description="生成內容")
    content_md: Optional[str] = Field(None, description="Markdown格式內容")
    
    # 標籤和話題
    commodity_tags: List[CommodityTag] = Field(default_factory=list, description="商品標籤")
    community_topic: Optional[CommunityTopic] = Field(None, description="社群話題")
    
    # 狀態管理
    status: PostStatus = Field(default=PostStatus.PENDING_REVIEW, description="貼文狀態")
    quality_score: Optional[float] = Field(None, description="品質分數")
    ai_detection_score: Optional[float] = Field(None, description="AI檢測分數")
    risk_level: Optional[str] = Field(None, description="風險等級")
    
    # 審核信息
    reviewer_notes: Optional[str] = Field(None, description="審核備註")
    approved_by: Optional[str] = Field(None, description="審核人")
    approved_at: Optional[datetime] = Field(None, description="審核時間")
    
    # 發布信息
    scheduled_at: Optional[datetime] = Field(None, description="預定發布時間")
    published_at: Optional[datetime] = Field(None, description="實際發布時間")
    cmoney_post_id: Optional[str] = Field(None, description="CMoney文章ID")
    cmoney_post_url: Optional[str] = Field(None, description="CMoney文章URL")
    publish_error: Optional[str] = Field(None, description="發布錯誤訊息")
    
    # 生成參數
    generation_params: GenerationParams = Field(..., description="生成參數")
    technical_analysis: Optional[TechnicalAnalysis] = Field(None, description="技術分析")
    
    # 互動數據
    views: int = Field(default=0, description="瀏覽數")
    likes: int = Field(default=0, description="按讚數")
    comments: int = Field(default=0, description="評論數")
    shares: int = Field(default=0, description="分享數")
    
    # 時間戳
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")

class PostRecordCreate(BaseModel):
    """創建貼文記錄的請求模型"""
    session_id: int
    kol_serial: int
    kol_nickname: str
    kol_persona: str
    stock_code: str
    stock_name: str
    title: str
    content: str
    content_md: Optional[str] = None
    commodity_tags: List[CommodityTag] = []
    community_topic: Optional[CommunityTopic] = None
    generation_params: GenerationParams
    technical_analysis: Optional[TechnicalAnalysis] = None
    topic_id: Optional[str] = None
    topic_title: Optional[str] = None

class PostRecordUpdate(BaseModel):
    """更新貼文記錄的請求模型"""
    status: Optional[PostStatus] = None
    reviewer_notes: Optional[str] = None
    approved_by: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    ai_detection_score: Optional[float] = None
    risk_level: Optional[str] = None

class PostRecordResponse(BaseModel):
    """貼文記錄響應模型"""
    success: bool
    data: Optional[PostRecord] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class BatchPostResponse(BaseModel):
    """批量貼文響應模型"""
    success: bool
    generated_count: int
    failed_count: int
    posts: List[PostRecord]
    errors: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)



















