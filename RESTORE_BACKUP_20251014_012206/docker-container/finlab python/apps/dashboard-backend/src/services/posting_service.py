"""
發文管理服務 - 簡化版
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.posting_models import (
    PostingTemplate, PostingSession, Post, KOLProfile, 
    PromptTemplate, PostingAnalytics
)
from src.schemas.posting_schemas import (
    PostingTemplateCreate, PostingTemplateResponse,
    PostingSessionCreate, PostingSessionResponse,
    PostCreate, PostResponse,
    PromptTemplateCreate, PromptTemplateResponse,
    KOLProfileResponse, PostingAnalyticsResponse,
    GeneratePostsRequest, GeneratePostsResponse,
    AnalyticsSummary
)

logger = logging.getLogger(__name__)

class PostingService:
    """發文管理服務"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== 模板管理 ====================
    
    async def create_template(self, template_data: PostingTemplateCreate) -> PostingTemplateResponse:
        """創建發文模板"""
        try:
            template = PostingTemplate(**template_data.dict())
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return PostingTemplateResponse.from_orm(template)
        except Exception as e:
            logger.error(f"創建發文模板失敗: {e}")
            raise
    
    async def get_templates(self) -> List[PostingTemplateResponse]:
        """獲取發文模板列表"""
        try:
            templates = self.db.query(PostingTemplate).all()
            return [PostingTemplateResponse.from_orm(template) for template in templates]
        except Exception as e:
            logger.error(f"獲取發文模板列表失敗: {e}")
            raise
    
    # ==================== 會話管理 ====================
    
    async def create_session(self, session_data: PostingSessionCreate) -> PostingSessionResponse:
        """創建發文會話"""
        try:
            session = PostingSession(**session_data.dict())
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return PostingSessionResponse.from_orm(session)
        except Exception as e:
            logger.error(f"創建發文會話失敗: {e}")
            raise
    
    async def get_sessions(self) -> List[PostingSessionResponse]:
        """獲取發文會話列表"""
        try:
            sessions = self.db.query(PostingSession).all()
            return [PostingSessionResponse.from_orm(session) for session in sessions]
        except Exception as e:
            logger.error(f"獲取發文會話列表失敗: {e}")
            raise
    
    # ==================== 發文管理 ====================
    
    async def create_post(self, post_data: dict) -> dict:
        """創建發文"""
        try:
            post = Post(**post_data)
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            return {
                'id': post.id,
                'session_id': post.session_id,
                'title': post.title,
                'content': post.content,
                'status': post.status,
                'kol_serial': post.kol_serial,
                'kol_nickname': post.kol_nickname,
                'kol_persona': post.kol_persona,
                'stock_codes': post.stock_codes,
                'stock_names': post.stock_names,
                'created_at': post.created_at,
                'updated_at': post.updated_at
            }
        except Exception as e:
            logger.error(f"創建發文失敗: {e}")
            raise
    
    async def get_posts(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> dict:
        """獲取發文列表"""
        try:
            query = self.db.query(Post)
            
            if status:
                query = query.filter(Post.status == status)
            
            posts = query.offset(skip).limit(limit).all()
            total = query.count()
            
            return {
                "posts": [PostResponse.from_orm(post) for post in posts],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"獲取發文列表失敗: {e}")
            raise
    
    async def update_post_status(self, post_id: int, status: str) -> PostResponse:
        """更新發文狀態"""
        try:
            post = self.db.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise ValueError(f"發文 {post_id} 不存在")
            
            post.status = status
            self.db.commit()
            self.db.refresh(post)
            return PostResponse.from_orm(post)
        except Exception as e:
            logger.error(f"更新發文狀態失敗: {e}")
            raise
    
    async def update_post_content(self, post_id: int, title: str, content: str) -> PostResponse:
        """更新發文內容"""
        try:
            post = self.db.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise ValueError(f"發文 {post_id} 不存在")
            
            post.title = title
            post.content = content
            self.db.commit()
            self.db.refresh(post)
            return PostResponse.from_orm(post)
        except Exception as e:
            logger.error(f"更新發文內容失敗: {e}")
            raise
    
    # ==================== Prompt模板管理 ====================
    
    async def create_prompt_template(self, template_data: PromptTemplateCreate) -> PromptTemplateResponse:
        """創建Prompt模板"""
        try:
            template = PromptTemplate(**template_data.dict())
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return PromptTemplateResponse.from_orm(template)
        except Exception as e:
            logger.error(f"創建Prompt模板失敗: {e}")
            raise
    
    async def get_prompt_templates(self, data_source: Optional[str] = None) -> List[PromptTemplateResponse]:
        """獲取Prompt模板列表"""
        try:
            query = self.db.query(PromptTemplate)
            
            if data_source:
                query = query.filter(PromptTemplate.data_source == data_source)
            
            templates = query.all()
            return [PromptTemplateResponse.from_orm(template) for template in templates]
        except Exception as e:
            logger.error(f"獲取Prompt模板列表失敗: {e}")
            raise
    
    # ==================== KOL管理 ====================
    
    async def get_kols(self) -> List[dict]:
        """獲取KOL列表"""
        try:
            # 使用原生SQL查詢KOL數據
            result = self.db.execute(text("""
                SELECT id, serial, nickname, name, persona, style_preference,
                       expertise_areas, activity_level, question_ratio,
                       content_length, interaction_starters, is_active,
                       created_at, updated_at
                FROM kol_profiles 
                WHERE is_active = true
                ORDER BY serial
            """))
            
            kols = []
            for row in result:
                kol_data = {
                    'id': row.id,
                    'serial': row.serial,
                    'nickname': row.nickname,
                    'name': row.name or '',
                    'persona': row.persona or '',
                    'style_preference': row.style_preference or '',
                    'expertise_areas': row.expertise_areas or [],
                    'activity_level': row.activity_level or 'high',
                    'question_ratio': row.question_ratio or 0.5,
                    'content_length': row.content_length or 'medium',
                    'interaction_starters': row.interaction_starters or [],
                    'is_active': row.is_active,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at
                }
                kols.append(kol_data)
            
            return kols
        except Exception as e:
            logger.error(f"獲取KOL列表失敗: {e}")
            raise
    
    async def get_kol_by_serial(self, serial: int) -> dict:
        """根據序號獲取KOL信息"""
        try:
            result = self.db.execute(text("""
                SELECT id, serial, nickname, name, persona, style_preference,
                       expertise_areas, activity_level, question_ratio,
                       content_length, interaction_starters, is_active
                FROM kol_profiles 
                WHERE serial = :serial AND is_active = true
            """), {"serial": serial})
            
            row = result.fetchone()
            if row:
                return {
                    'id': row.id,
                    'serial': row.serial,
                    'nickname': row.nickname,
                    'name': row.name or '',
                    'persona': row.persona or '',
                    'style_preference': row.style_preference or '',
                    'expertise_areas': row.expertise_areas or [],
                    'activity_level': row.activity_level or 'high',
                    'question_ratio': row.question_ratio or 0.5,
                    'content_length': row.content_length or 'medium',
                    'interaction_starters': row.interaction_starters or [],
                    'is_active': row.is_active
                }
            return None
        except Exception as e:
            logger.error(f"獲取KOL {serial} 失敗: {e}")
            raise
    
    async def get_session(self, session_id: int) -> dict:
        """獲取會話信息"""
        try:
            session = self.db.query(PostingSession).filter(PostingSession.id == session_id).first()
            if session:
                return {
                    'id': session.id,
                    'name': session.session_name,
                    'trigger_type': session.trigger_type,
                    'trigger_data': session.trigger_data,
                    'config': session.config,
                    'status': session.status,
                    'created_at': session.created_at,
                    'updated_at': session.updated_at
                }
            return None
        except Exception as e:
            logger.error(f"獲取會話 {session_id} 失敗: {e}")
            raise
    
    # ==================== 分析數據 ====================
    
    async def get_post_analytics(self, post_id: int, days: int = 7) -> List[PostingAnalyticsResponse]:
        """獲取發文分析數據"""
        try:
            analytics = self.db.query(PostingAnalytics)\
                .filter(PostingAnalytics.post_id == post_id)\
                .limit(days)\
                .all()
            
            return [PostingAnalyticsResponse.from_orm(analytics_item) for analytics_item in analytics]
        except Exception as e:
            logger.error(f"獲取發文分析數據失敗: {e}")
            raise
    
    async def get_analytics_summary(self, days: int = 30) -> AnalyticsSummary:
        """獲取分析摘要"""
        try:
            # 簡化版分析摘要
            return AnalyticsSummary(
                total_posts=0,
                published_posts=0,
                pending_posts=0,
                total_interactions=0,
                avg_interaction_rate=0.0,
                top_performing_posts=[]
            )
        except Exception as e:
            logger.error(f"獲取分析摘要失敗: {e}")
            raise