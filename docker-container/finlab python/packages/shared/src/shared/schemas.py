from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class OHLCItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class MACDValue(BaseModel):
    macd: Optional[float] = None
    signal: Optional[float] = None
    hist: Optional[float] = None

class AnalyzeOutput(BaseModel):
    stock_id: str
    as_of: str
    indicators: Dict[str, Any]
    signals: List[Dict[str, Any]]

class Action(BaseModel):
    action: str  # buy | hold | sell
    confidence: float = Field(ge=0, le=1)
    rationale: str
    risk: List[str] = []
    horizon_days: int
    invalidations: List[str] = []
    stops_targets: Dict[str, float] = {}

class SummaryOutput(BaseModel):
    actions: List[Action]
    post_md: str
    telemetry: Dict[str, Any]

class Persona(BaseModel):
    name: str
    style: str

# 虛擬 KOL 相關 schemas
class KOLPersona(BaseModel):
    """虛擬 KOL 人格特質"""
    id: str
    name: str
    style: Literal["technical", "fundamental", "news_driven", "quantitative", "educational"]
    personality: Dict[str, Any]  # 人格特質
    expertise: List[str]  # 專長領域
    content_preferences: List[str]  # 內容偏好
    interaction_style: str  # 互動風格

class ContentRequest(BaseModel):
    """內容生成請求"""
    stock_id: str
    kol_persona: str
    content_style: Literal["chart_analysis", "earnings_review", "news_commentary", "technical_breakdown", "educational"]
    target_audience: Literal["active_traders", "long_term_investors", "beginners", "professionals"]
    content_length: Literal["short", "medium", "long"] = "medium"
    include_charts: bool = True
    include_backtest: bool = False

class KOLContent(BaseModel):
    """虛擬 KOL 生成的內容"""
    kol_id: str
    kol_name: str
    stock_id: str
    content_type: str
    title: str
    content_md: str
    key_points: List[str]
    investment_advice: Dict[str, Any]
    charts_data: Optional[Dict[str, Any]] = None
    backtest_results: Optional[Dict[str, Any]] = None
    engagement_prediction: float = Field(ge=0, le=1)
    created_at: datetime
    metadata: Dict[str, Any] = {}

class InteractionMetrics(BaseModel):
    """互動數據"""
    content_id: str
    kol_id: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    sentiment_score: float = 0.0
    timestamp: datetime

class KOLPerformance(BaseModel):
    """KOL 表現追蹤"""
    kol_id: str
    total_posts: int
    avg_engagement_rate: float
    top_performing_content_types: List[str]
    audience_preferences: Dict[str, float]
    learning_metrics: Dict[str, Any]