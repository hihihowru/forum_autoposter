"""
KOL 數據庫 API 端點
提供完整的 KOL 管理 API
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/kol", tags=["KOL管理"])

# Pydantic 模型
class KOLCreateRequest(BaseModel):
    """KOL 創建請求"""
    serial: str
    nickname: str
    member_id: str
    persona: str
    email: str
    password: str
    status: str = "active"
    owner: str = "威廉用"
    notes: Optional[str] = None
    post_times: Optional[str] = None
    target_audience: Optional[str] = None
    interaction_threshold: float = 0.6
    content_types: Optional[List[str]] = None
    common_terms: Optional[str] = None
    colloquial_terms: Optional[str] = None
    tone_style: Optional[str] = None
    typing_habit: Optional[str] = None
    backstory: Optional[str] = None
    expertise: Optional[str] = None
    data_source: Optional[str] = None
    prompt_persona: Optional[str] = None
    prompt_style: Optional[str] = None
    prompt_guardrails: Optional[str] = None
    prompt_skeleton: Optional[str] = None
    prompt_cta: Optional[str] = None
    prompt_hashtags: Optional[str] = None
    signature: Optional[str] = None
    emoji_pack: Optional[str] = None
    model_id: str = "gpt-4o-mini"
    template_variant: str = "default"
    model_temp: float = 0.5
    max_tokens: int = 700
    title_openers: Optional[List[str]] = None
    title_signature_patterns: Optional[List[str]] = None
    title_tail_word: Optional[str] = None
    title_banned_words: Optional[List[str]] = None
    title_style_examples: Optional[List[str]] = None
    title_retry_max: int = 3
    tone_formal: int = 5
    tone_emotion: int = 5
    tone_confidence: int = 7
    tone_urgency: int = 4
    tone_interaction: int = 6
    question_ratio: float = 0.5
    content_length: str = "medium"
    interaction_starters: Optional[List[str]] = None
    require_finlab_api: bool = True
    allow_hashtags: bool = True

class KOLUpdateRequest(BaseModel):
    """KOL 更新請求"""
    nickname: Optional[str] = None
    persona: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None
    post_times: Optional[str] = None
    target_audience: Optional[str] = None
    interaction_threshold: Optional[float] = None
    content_types: Optional[List[str]] = None
    common_terms: Optional[str] = None
    colloquial_terms: Optional[str] = None
    tone_style: Optional[str] = None
    typing_habit: Optional[str] = None
    backstory: Optional[str] = None
    expertise: Optional[str] = None
    data_source: Optional[str] = None
    prompt_persona: Optional[str] = None
    prompt_style: Optional[str] = None
    prompt_guardrails: Optional[str] = None
    prompt_skeleton: Optional[str] = None
    prompt_cta: Optional[str] = None
    prompt_hashtags: Optional[str] = None
    signature: Optional[str] = None
    emoji_pack: Optional[str] = None
    model_id: Optional[str] = None
    template_variant: Optional[str] = None
    model_temp: Optional[float] = None
    max_tokens: Optional[int] = None
    title_openers: Optional[List[str]] = None
    title_signature_patterns: Optional[List[str]] = None
    title_tail_word: Optional[str] = None
    title_banned_words: Optional[List[str]] = None
    title_style_examples: Optional[List[str]] = None
    title_retry_max: Optional[int] = None
    tone_formal: Optional[int] = None
    tone_emotion: Optional[int] = None
    tone_confidence: Optional[int] = None
    tone_urgency: Optional[int] = None
    tone_interaction: Optional[int] = None
    question_ratio: Optional[float] = None
    content_length: Optional[str] = None
    interaction_starters: Optional[List[str]] = None
    require_finlab_api: Optional[bool] = None
    allow_hashtags: Optional[bool] = None

class KOLResponse(BaseModel):
    """KOL 回應模型"""
    serial: str
    nickname: str
    member_id: str
    persona: str
    status: str
    owner: str
    email: str
    whitelist: bool
    notes: Optional[str]
    post_times: Optional[str]
    target_audience: Optional[str]
    interaction_threshold: float
    content_types: Optional[List[str]]
    common_terms: Optional[str]
    colloquial_terms: Optional[str]
    tone_style: Optional[str]
    typing_habit: Optional[str]
    backstory: Optional[str]
    expertise: Optional[str]
    data_source: Optional[str]
    prompt_persona: Optional[str]
    prompt_style: Optional[str]
    prompt_guardrails: Optional[str]
    prompt_skeleton: Optional[str]
    prompt_cta: Optional[str]
    prompt_hashtags: Optional[str]
    signature: Optional[str]
    emoji_pack: Optional[str]
    model_id: Optional[str] = "gpt-4o-mini"
    template_variant: Optional[str] = "default"
    model_temp: Optional[float] = 0.5
    max_tokens: Optional[int] = 700
    title_openers: Optional[List[str]] = None
    title_signature_patterns: Optional[List[str]] = None
    title_tail_word: Optional[str] = None
    title_banned_words: Optional[List[str]] = None
    title_style_examples: Optional[List[str]] = None
    title_retry_max: Optional[int] = 3
    tone_formal: Optional[int] = 5
    tone_emotion: Optional[int] = 5
    tone_confidence: Optional[int] = 7
    tone_urgency: Optional[int] = 4
    tone_interaction: Optional[int] = 6
    question_ratio: Optional[float] = 0.5
    content_length: Optional[str] = "medium"
    interaction_starters: Optional[List[str]] = None
    require_finlab_api: Optional[bool] = True
    allow_hashtags: Optional[bool] = True
    created_time: datetime
    last_updated: datetime
    total_posts: int
    published_posts: int
    avg_interaction_rate: float
    best_performing_post: Optional[str]

class KOLListResponse(BaseModel):
    """KOL 列表回應模型"""
    success: bool
    data: List[Dict[str, Any]]
    count: int
    timestamp: str

# 依賴注入
def get_kol_db_service():
    """獲取 KOL 數據庫服務"""
    from kol_database_service import kol_db_service
    return kol_db_service

# API 端點
@router.get("/list", response_model=KOLListResponse)
async def get_kol_list(kol_db_service = Depends(get_kol_db_service)):
    """獲取所有 KOL 列表"""
    try:
        kol_list = kol_db_service.get_kol_list_for_selection()
        return KOLListResponse(
            success=True,
            data=kol_list,
            count=len(kol_list),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"獲取 KOL 列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 列表失敗: {str(e)}")

@router.get("/{serial}", response_model=KOLResponse)
async def get_kol_by_serial(serial: str, kol_db_service = Depends(get_kol_db_service)):
    """根據序號獲取 KOL 詳情"""
    try:
        kol = kol_db_service.get_kol_by_serial(serial)
        if not kol:
            raise HTTPException(status_code=404, detail=f"找不到 KOL {serial}")
        
        return KOLResponse(
            serial=kol.serial,
            nickname=kol.nickname,
            member_id=kol.member_id,
            persona=kol.persona,
            status=kol.status,
            owner=kol.owner,
            email=kol.email,
            whitelist=kol.whitelist,
            notes=kol.notes,
            post_times=kol.post_times,
            target_audience=kol.target_audience,
            interaction_threshold=kol.interaction_threshold,
            content_types=kol.content_types,
            common_terms=kol.common_terms,
            colloquial_terms=kol.colloquial_terms,
            tone_style=kol.tone_style,
            typing_habit=kol.typing_habit,
            backstory=kol.backstory,
            expertise=kol.expertise,
            data_source=kol.data_source,
            prompt_persona=kol.prompt_persona,
            prompt_style=kol.prompt_style,
            prompt_guardrails=kol.prompt_guardrails,
            prompt_skeleton=kol.prompt_skeleton,
            prompt_cta=kol.prompt_cta,
            prompt_hashtags=kol.prompt_hashtags,
            signature=kol.signature,
            emoji_pack=kol.emoji_pack,
            model_id=kol.model_id,
            template_variant=kol.template_variant,
            model_temp=kol.model_temp,
            max_tokens=kol.max_tokens,
            title_openers=kol.title_openers,
            title_signature_patterns=kol.title_signature_patterns,
            title_tail_word=kol.title_tail_word,
            title_banned_words=kol.title_banned_words,
            title_style_examples=kol.title_style_examples,
            title_retry_max=kol.title_retry_max,
            tone_formal=kol.tone_formal,
            tone_emotion=kol.tone_emotion,
            tone_confidence=kol.tone_confidence,
            tone_urgency=kol.tone_urgency,
            tone_interaction=kol.tone_interaction,
            question_ratio=kol.question_ratio,
            content_length=kol.content_length,
            interaction_starters=kol.interaction_starters,
            require_finlab_api=kol.require_finlab_api,
            allow_hashtags=kol.allow_hashtags,
            created_time=kol.created_time,
            last_updated=kol.last_updated,
            total_posts=kol.total_posts,
            published_posts=kol.published_posts,
            avg_interaction_rate=kol.avg_interaction_rate,
            best_performing_post=kol.best_performing_post
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取 KOL {serial} 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 失敗: {str(e)}")

@router.post("/create", response_model=KOLResponse)
async def create_kol(request: KOLCreateRequest, kol_db_service = Depends(get_kol_db_service)):
    """創建新 KOL"""
    try:
        # 檢查是否已存在
        existing_kol = kol_db_service.get_kol_by_serial(request.serial)
        if existing_kol:
            raise HTTPException(status_code=400, detail=f"KOL {request.serial} 已存在")
        
        # 創建 KOL
        kol_data = request.dict()
        kol = kol_db_service.create_kol(kol_data)
        
        if not kol:
            raise HTTPException(status_code=500, detail="創建 KOL 失敗")
        
        return KOLResponse(
            serial=kol.serial,
            nickname=kol.nickname,
            member_id=kol.member_id,
            persona=kol.persona,
            status=kol.status,
            owner=kol.owner,
            email=kol.email,
            whitelist=kol.whitelist,
            notes=kol.notes,
            post_times=kol.post_times,
            target_audience=kol.target_audience,
            interaction_threshold=kol.interaction_threshold,
            content_types=kol.content_types,
            common_terms=kol.common_terms,
            colloquial_terms=kol.colloquial_terms,
            tone_style=kol.tone_style,
            typing_habit=kol.typing_habit,
            backstory=kol.backstory,
            expertise=kol.expertise,
            data_source=kol.data_source,
            prompt_persona=kol.prompt_persona,
            prompt_style=kol.prompt_style,
            prompt_guardrails=kol.prompt_guardrails,
            prompt_skeleton=kol.prompt_skeleton,
            prompt_cta=kol.prompt_cta,
            prompt_hashtags=kol.prompt_hashtags,
            signature=kol.signature,
            emoji_pack=kol.emoji_pack,
            model_id=kol.model_id,
            template_variant=kol.template_variant,
            model_temp=kol.model_temp,
            max_tokens=kol.max_tokens,
            title_openers=kol.title_openers,
            title_signature_patterns=kol.title_signature_patterns,
            title_tail_word=kol.title_tail_word,
            title_banned_words=kol.title_banned_words,
            title_style_examples=kol.title_style_examples,
            title_retry_max=kol.title_retry_max,
            tone_formal=kol.tone_formal,
            tone_emotion=kol.tone_emotion,
            tone_confidence=kol.tone_confidence,
            tone_urgency=kol.tone_urgency,
            tone_interaction=kol.tone_interaction,
            question_ratio=kol.question_ratio,
            content_length=kol.content_length,
            interaction_starters=kol.interaction_starters,
            require_finlab_api=kol.require_finlab_api,
            allow_hashtags=kol.allow_hashtags,
            created_time=kol.created_time,
            last_updated=kol.last_updated,
            total_posts=kol.total_posts,
            published_posts=kol.published_posts,
            avg_interaction_rate=kol.avg_interaction_rate,
            best_performing_post=kol.best_performing_post
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"創建 KOL 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"創建 KOL 失敗: {str(e)}")

@router.put("/{serial}", response_model=KOLResponse)
async def update_kol(serial: str, request: KOLUpdateRequest, kol_db_service = Depends(get_kol_db_service)):
    """更新 KOL"""
    try:
        # 過濾掉 None 值
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        kol = kol_db_service.update_kol(serial, update_data)
        if not kol:
            raise HTTPException(status_code=404, detail=f"找不到 KOL {serial}")
        
        return KOLResponse(
            serial=kol.serial,
            nickname=kol.nickname,
            member_id=kol.member_id,
            persona=kol.persona,
            status=kol.status,
            owner=kol.owner,
            email=kol.email,
            whitelist=kol.whitelist,
            notes=kol.notes,
            post_times=kol.post_times,
            target_audience=kol.target_audience,
            interaction_threshold=kol.interaction_threshold,
            content_types=kol.content_types,
            common_terms=kol.common_terms,
            colloquial_terms=kol.colloquial_terms,
            tone_style=kol.tone_style,
            typing_habit=kol.typing_habit,
            backstory=kol.backstory,
            expertise=kol.expertise,
            data_source=kol.data_source,
            prompt_persona=kol.prompt_persona,
            prompt_style=kol.prompt_style,
            prompt_guardrails=kol.prompt_guardrails,
            prompt_skeleton=kol.prompt_skeleton,
            prompt_cta=kol.prompt_cta,
            prompt_hashtags=kol.prompt_hashtags,
            signature=kol.signature,
            emoji_pack=kol.emoji_pack,
            model_id=kol.model_id,
            template_variant=kol.template_variant,
            model_temp=kol.model_temp,
            max_tokens=kol.max_tokens,
            title_openers=kol.title_openers,
            title_signature_patterns=kol.title_signature_patterns,
            title_tail_word=kol.title_tail_word,
            title_banned_words=kol.title_banned_words,
            title_style_examples=kol.title_style_examples,
            title_retry_max=kol.title_retry_max,
            tone_formal=kol.tone_formal,
            tone_emotion=kol.tone_emotion,
            tone_confidence=kol.tone_confidence,
            tone_urgency=kol.tone_urgency,
            tone_interaction=kol.tone_interaction,
            question_ratio=kol.question_ratio,
            content_length=kol.content_length,
            interaction_starters=kol.interaction_starters,
            require_finlab_api=kol.require_finlab_api,
            allow_hashtags=kol.allow_hashtags,
            created_time=kol.created_time,
            last_updated=kol.last_updated,
            total_posts=kol.total_posts,
            published_posts=kol.published_posts,
            avg_interaction_rate=kol.avg_interaction_rate,
            best_performing_post=kol.best_performing_post
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新 KOL {serial} 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"更新 KOL 失敗: {str(e)}")

@router.delete("/{serial}")
async def delete_kol(serial: str, kol_db_service = Depends(get_kol_db_service)):
    """刪除 KOL"""
    try:
        success = kol_db_service.delete_kol(serial)
        if not success:
            raise HTTPException(status_code=404, detail=f"找不到 KOL {serial}")
        
        return {
            "success": True,
            "message": f"KOL {serial} 刪除成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除 KOL {serial} 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"刪除 KOL 失敗: {str(e)}")

@router.post("/sync")
async def sync_kols_from_data_manager(kol_db_service = Depends(get_kol_db_service)):
    """從 KOL 數據管理器同步數據到數據庫"""
    try:
        success = kol_db_service.sync_kols_from_data_manager()
        if success:
            return {
                "success": True,
                "message": "KOL 數據同步成功",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="KOL 數據同步失敗")
    except Exception as e:
        logger.error(f"同步 KOL 數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"同步 KOL 數據失敗: {str(e)}")

@router.get("/credentials/{serial}")
async def get_kol_credentials(serial: str, kol_db_service = Depends(get_kol_db_service)):
    """獲取 KOL 登入憑證"""
    try:
        credentials = kol_db_service.get_kol_credentials(serial)
        if not credentials:
            raise HTTPException(status_code=404, detail=f"找不到 KOL {serial} 的憑證")
        
        return {
            "success": True,
            "data": credentials,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取 KOL {serial} 憑證失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 憑證失敗: {str(e)}")


