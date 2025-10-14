"""
貼文相關的 API 路由
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from post_record_service import PostRecordUpdate

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/posts", tags=["posts"])

# 導入全局服務實例 - 避免循環導入
post_record_service = None

def get_post_record_service():
    global post_record_service
    if post_record_service is None:
        try:
            from postgresql_service import PostgreSQLPostRecordService
            post_record_service = PostgreSQLPostRecordService()
            print(f"✅ PostgreSQL 服務初始化成功: {post_record_service}")
        except Exception as e:
            print(f"❌ PostgreSQL 服務初始化失敗: {e}")
            return None
    return post_record_service

@router.get("/")
async def get_all_posts(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """獲取所有貼文"""
    try:
        posts = get_post_record_service().get_all_posts()
        
        # 根據狀態篩選
        if status:
            posts = [post for post in posts if post.status == status]
        
        # 分頁
        total = len(posts)
        posts = posts[skip:skip + limit]
        
        # 轉換為可序列化的格式
        posts_data = []
        for post in posts:
            post_data = {
                "post_id": post.post_id,
                "session_id": post.session_id,
                "kol_serial": post.kol_serial,
                "kol_nickname": post.kol_nickname,
                "kol_persona": post.kol_persona,
                "stock_code": post.stock_code,
                "stock_name": post.stock_name,
                "title": post.title,
                "content": post.content,
                "content_md": post.content_md,
                "status": post.status,
                "quality_score": post.quality_score,
                "ai_detection_score": post.ai_detection_score,
                "risk_level": post.risk_level,
                "reviewer_notes": post.reviewer_notes,
                "approved_by": post.approved_by,
                "approved_at": post.approved_at.isoformat() if post.approved_at else None,
                "scheduled_at": None,  # PostRecord 模型沒有此字段
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "cmoney_post_id": post.cmoney_post_id,
                "cmoney_post_url": post.cmoney_post_url,
                "publish_error": getattr(post, 'publish_error', None),
                "views": post.views,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "topic_id": post.topic_id,
                "topic_title": post.topic_title,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None
            }
            posts_data.append(post_data)
        
        return {
            "posts": posts_data,
            "count": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"獲取貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取貼文失敗: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_posts(session_id: int, status: Optional[str] = None):
    """獲取特定會話的貼文"""
    logger.info(f"🔍 獲取會話貼文請求 - Session ID: {session_id}")
    
    try:
        # 直接導入並創建服務實例
        from postgresql_service import PostgreSQLPostRecordService
        service = PostgreSQLPostRecordService()
        posts = service.get_session_posts(session_id, status)
        
        # 轉換為可序列化的格式
        posts_data = []
        for post in posts:
            post_data = {
                "post_id": post.post_id,
                "session_id": post.session_id,
                "kol_serial": post.kol_serial,
                "kol_nickname": post.kol_nickname,
                "kol_persona": post.kol_persona,
                "stock_code": post.stock_code,
                "stock_name": post.stock_name,
                "title": post.title,
                "content": post.content,
                "content_md": post.content_md,
                "status": post.status,
                "quality_score": post.quality_score,
                "ai_detection_score": post.ai_detection_score,
                "risk_level": post.risk_level,
                "reviewer_notes": post.reviewer_notes,
                "approved_by": post.approved_by,
                "approved_at": post.approved_at.isoformat() if post.approved_at else None,
                "scheduled_at": None,  # PostRecord 模型沒有此字段
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "cmoney_post_id": post.cmoney_post_id,
                "cmoney_post_url": post.cmoney_post_url,
                "publish_error": getattr(post, 'publish_error', None),
                "views": post.views,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "topic_id": post.topic_id,
                "topic_title": post.topic_title,
                "alternative_versions": post.alternative_versions,  # 新增：其他版本
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None
            }
            posts_data.append(post_data)
        
        logger.info(f"✅ 找到 {len(posts_data)} 篇會話貼文 - Session ID: {session_id}")
        
        return {
            "success": True,
            "posts": posts_data,
            "count": len(posts_data),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取會話貼文失敗 - Session ID: {session_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"獲取會話貼文失敗: {str(e)}")

@router.post("/create-test")
async def create_test_post():
    """創建測試貼文"""
    try:
        test_post_data = {
            'session_id': 1,
            'kol_serial': 200,
            'kol_nickname': '測試KOL',
            'kol_persona': 'technical',
            'stock_code': '2330',
            'stock_name': '台積電',
            'title': '測試貼文標題',
            'content': '這是一個測試貼文的內容，用於驗證數據庫是否正常工作。',
            'content_md': '這是一個測試貼文的內容，用於驗證數據庫是否正常工作。',
            'status': 'draft'
        }
        
        post_record = get_post_record_service().create_post_record(test_post_data)
        
        return {
            "success": True,
            "post_id": post_record.post_id,
            "message": "測試貼文創建成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"創建測試貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"創建測試貼文失敗: {str(e)}")

@router.get("/kol-list")
async def get_kols():
    """獲取所有 KOL 列表"""
    try:
        from kol_service import kol_service
        
        # 獲取所有 KOL 序號
        kol_serials = kol_service.get_all_kol_serials()
        
        # 構建 KOL 列表
        kols = []
        for serial in kol_serials:
            kol_info = kol_service.get_kol_info(serial)
            if kol_info:
                kols.append(kol_info)
        
        logger.info(f"📊 返回 {len(kols)} 個 KOL")
        return kols
        
    except Exception as e:
        logger.error(f"❌ 獲取 KOL 列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 列表失敗: {str(e)}")

def _get_trigger_type_from_params(generation_params):
    """從 generation_params 中提取 trigger_type"""
    if not generation_params:
        return None
    
    try:
        # 如果是字符串，嘗試解析為 JSON
        if isinstance(generation_params, str):
            import json
            params = json.loads(generation_params)
        else:
            params = generation_params
        
        return params.get('trigger_type') if isinstance(params, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None

@router.get("/history-stats")
async def get_history_stats():
    """獲取歷史生成資料統計"""
    try:
        all_posts = get_post_record_service().get_all_posts()
        
        # 按狀態分組統計
        status_stats = {}
        session_stats = {}
        kol_stats = {}
        stock_stats = {}
        
        for post in all_posts:
            # 狀態統計
            status = post.status
            status_stats[status] = status_stats.get(status, 0) + 1
            
            # Session 統計
            session_id = post.session_id
            if session_id not in session_stats:
                session_stats[session_id] = {
                    'count': 0,
                    'statuses': {},
                    'kols': set(),
                    'stocks': set()
                }
            session_stats[session_id]['count'] += 1
            session_stats[session_id]['statuses'][status] = session_stats[session_id]['statuses'].get(status, 0) + 1
            session_stats[session_id]['kols'].add(post.kol_serial)
            session_stats[session_id]['stocks'].add(post.stock_code)
            
            # KOL 統計
            kol_serial = post.kol_serial
            if kol_serial not in kol_stats:
                kol_stats[kol_serial] = {
                    'count': 0,
                    'statuses': {},
                    'sessions': set()
                }
            kol_stats[kol_serial]['count'] += 1
            kol_stats[kol_serial]['statuses'][status] = kol_stats[kol_serial]['statuses'].get(status, 0) + 1
            kol_stats[kol_serial]['sessions'].add(session_id)
            
            # 股票統計
            stock_code = post.stock_code
            if stock_code not in stock_stats:
                stock_stats[stock_code] = {
                    'count': 0,
                    'statuses': {},
                    'sessions': set()
                }
            stock_stats[stock_code]['count'] += 1
            stock_stats[stock_code]['statuses'][status] = stock_stats[stock_code]['statuses'].get(status, 0) + 1
            stock_stats[stock_code]['sessions'].add(session_id)
        
        # 轉換 set 為 list 以便 JSON 序列化
        for session_id in session_stats:
            session_stats[session_id]['kols'] = list(session_stats[session_id]['kols'])
            session_stats[session_id]['stocks'] = list(session_stats[session_id]['stocks'])
        
        for kol_serial in kol_stats:
            kol_stats[kol_serial]['sessions'] = list(kol_stats[kol_serial]['sessions'])
        
        for stock_code in stock_stats:
            stock_stats[stock_code]['sessions'] = list(stock_stats[stock_code]['sessions'])
        
        return {
            "success": True,
            "status_stats": status_stats,
            "session_stats": session_stats,
            "kol_stats": kol_stats,
            "stock_stats": stock_stats,
            "all_posts": [
                {
                    "post_id": post.post_id,
                    "session_id": post.session_id,
                    "kol_serial": post.kol_serial,
                    "stock_code": post.stock_code,
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "trigger_type": _get_trigger_type_from_params(post.generation_params)
                }
                for post in all_posts
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"獲取歷史統計失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{post_id}")
async def get_post(post_id: str):
    """獲取單個貼文詳情"""
    logger.info(f"🔍 獲取貼文請求 - Post ID: {post_id}")
    
    try:
        post_record = get_post_record_service().get_post_record(post_id)
        if post_record:
            logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 狀態: {post_record.status}")
            
            # 將貼文記錄轉換為可序列化的字典
            post_data = {
                "post_id": post_record.post_id,
                "session_id": post_record.session_id,
                "kol_serial": post_record.kol_serial,
                "kol_nickname": post_record.kol_nickname,
                "kol_persona": post_record.kol_persona,
                "stock_code": post_record.stock_code,
                "stock_name": post_record.stock_name,
                "title": post_record.title,
                "content": post_record.content,
                "content_md": post_record.content_md,
                "status": post_record.status,
                "quality_score": post_record.quality_score,
                "ai_detection_score": post_record.ai_detection_score,
                "risk_level": post_record.risk_level,
                "reviewer_notes": post_record.reviewer_notes,
                "approved_by": post_record.approved_by,
                "approved_at": post_record.approved_at.isoformat() if post_record.approved_at else None,
                "scheduled_at": None,  # PostRecord 模型沒有此字段
                "published_at": post_record.published_at.isoformat() if post_record.published_at else None,
                "cmoney_post_id": post_record.cmoney_post_id,
                "cmoney_post_url": post_record.cmoney_post_url,
                "publish_error": post_record.publish_error,
                "views": post_record.views,
                "likes": post_record.likes,
                "comments": post_record.comments,
                "shares": post_record.shares,
                "topic_id": post_record.topic_id,
                "topic_title": post_record.topic_title,
                "created_at": post_record.created_at.isoformat() if post_record.created_at else None,
                "updated_at": post_record.updated_at.isoformat() if post_record.updated_at else None
            }
            
            return {
                "success": True,
                "post": post_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 獲取貼文時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"獲取貼文失敗: {str(e)}")

@router.post("/{post_id}/approve")
async def approve_post(post_id: str, request: Request):
    """審核通過貼文"""
    logger.info(f"🔍 開始處理貼文審核請求 - Post ID: {post_id}")
    
    try:
        # 記錄請求詳情
        logger.info(f"📝 審核請求詳情 - Post ID: {post_id}")
        
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {get_post_record_service().get_posts_count()}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: 無法獲取（PostgreSQL 模式）")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 解析請求內容
        body = await request.json()
        reviewer_notes = body.get("reviewer_notes")
        approved_by = body.get("approved_by", "system")
        
        # 獲取編輯後的內容
        edited_title = body.get("edited_title")
        edited_content = body.get("edited_content")
        
        logger.info(f"📝 審核參數 - 審核者: {approved_by}, 備註: {reviewer_notes}")
        logger.info(f"📝 編輯內容 - 標題: {'有編輯' if edited_title else '無編輯'}, 內容: {'有編輯' if edited_content else '無編輯'}")
        
        # 如果有編輯內容，直接更新數據庫中的記錄
        if edited_title or edited_content:
            existing_post.status = "approved"
            existing_post.reviewer_notes = reviewer_notes
            existing_post.approved_by = approved_by
            existing_post.approved_at = datetime.now()
            
            if edited_title:
                existing_post.title = edited_title
                logger.info(f"📝 更新標題: {edited_title}")
            
            if edited_content:
                existing_post.content = edited_content
                logger.info(f"📝 更新內容: {len(edited_content)} 字符")
            
            existing_post.updated_at = datetime.now()
            
            # 使用 PostgreSQL 服務更新記錄
            update_data = {
                'status': 'approved',
                'reviewer_notes': reviewer_notes,
                'approved_by': approved_by,
                'approved_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            if edited_title:
                update_data['title'] = edited_title
            if edited_content:
                update_data['content'] = edited_content
            
            post_record = get_post_record_service().update_post_record(post_id, update_data)
        else:
            # 創建更新資料
            update_data = {
                'status': 'approved',
                'reviewer_notes': reviewer_notes,
                'approved_by': approved_by,
                'approved_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文審核成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            logger.info(f"📊 更新後資料庫狀態 - 總貼文數: {get_post_record_service().get_posts_count()}")
            
            return {
                "success": True,
                "message": "貼文審核通過",
                "post": {
                    "post_id": post_record.post_id,
                    "title": post_record.title,
                    "content": post_record.content,
                    "status": post_record.status,
                    "approved_by": post_record.approved_by,
                    "approved_at": post_record.approved_at.isoformat() if post_record.approved_at else None,
                    "reviewer_notes": post_record.reviewer_notes
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新貼文失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}, 詳情: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ 審核貼文時發生未預期錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        logger.error(f"🔍 錯誤類型: {type(e).__name__}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"審核失敗: {str(e)}")

@router.post("/{post_id}/reject")
async def reject_post(post_id: str, request: Request):
    """拒絕貼文"""
    logger.info(f"🔍 開始處理貼文拒絕請求 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            logger.info(f"📊 目前資料庫中的貼文數量: {get_post_record_service().get_posts_count()}")
            logger.info(f"📋 資料庫中的貼文 ID 列表: 無法獲取（PostgreSQL 模式）")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 解析請求內容
        body = await request.json()
        reviewer_notes = body.get("reviewer_notes", "拒絕")
        
        logger.info(f"📝 拒絕參數 - 備註: {reviewer_notes}")
        
        # 創建更新資料
        update_data = {
            'status': 'rejected',
            'reviewer_notes': reviewer_notes,
            'approved_by': 'system',
            'updated_at': datetime.now()
        }
        
        logger.info(f"🔄 開始更新貼文狀態為拒絕 - Post ID: {post_id}")
        
        # 更新貼文記錄
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文拒絕成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            return {
                "success": True,
                "message": "貼文已拒絕",
                "post": {
                    "post_id": post_record.post_id,
                    "status": post_record.status,
                    "reviewer_notes": post_record.reviewer_notes
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新貼文失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}, 詳情: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ 拒絕貼文時發生未預期錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"拒絕失敗: {str(e)}")

@router.delete("/cmoney/{article_id}")
async def delete_cmoney_article(article_id: str, kol_serial: Optional[str] = None):
    """刪除CMoney平台上的文章"""
    logger.info(f"🗑️ 開始刪除CMoney文章 - Article ID: {article_id}")
    
    try:
        # 如果沒有指定KOL序號，嘗試從資料庫中找到對應的KOL
        if not kol_serial:
            logger.info(f"🔍 搜尋文章 {article_id} 對應的KOL...")
            
            # 從所有貼文中找到對應的KOL
            all_posts = get_post_record_service().get_all_posts()
            for post in all_posts:
                if post.cmoney_post_id == article_id:
                    kol_serial = str(post.kol_serial)
                    logger.info(f"✅ 找到對應KOL: {kol_serial}")
                    break
            
            if not kol_serial:
                logger.error(f"❌ 找不到文章 {article_id} 對應的KOL")
                raise HTTPException(status_code=404, detail=f"找不到文章 {article_id} 對應的KOL")
        
        # 獲取KOL憑證
        from main import kol_credential_manager
        kol_creds = kol_credential_manager.get_kol_credentials(kol_serial)
        if not kol_creds:
            logger.error(f"❌ 找不到KOL {kol_serial} 的憑證")
            raise HTTPException(status_code=404, detail=f"找不到KOL {kol_serial} 的憑證")
        
        logger.info(f"🔐 使用KOL {kol_serial} 憑證登入...")
        
        # 登入KOL
        access_token = await kol_credential_manager.login_kol(kol_serial)
        if not access_token:
            logger.error(f"❌ KOL {kol_serial} 登入失敗")
            raise HTTPException(status_code=401, detail=f"KOL {kol_serial} 登入失敗")
        
        logger.info(f"✅ KOL {kol_serial} 登入成功")
        
        # 使用CMoney Client刪除文章
        from src.clients.cmoney.cmoney_client import CMoneyClient
        cmoney_client = CMoneyClient()
        
        logger.info(f"🗑️ 開始刪除文章 {article_id}...")
        delete_success = await cmoney_client.delete_article(access_token, article_id)
        
        if delete_success:
            logger.info(f"✅ 成功刪除文章 {article_id}")
            
            # 更新資料庫中的貼文狀態
            all_posts = get_post_record_service().get_all_posts()
            for post in all_posts:
                if post.cmoney_post_id == article_id:
                    update_data = {
                        "status": "deleted",
                        "reviewer_notes": f"已刪除CMoney文章 {article_id}",
                        "approved_by": "system"
                    }
                    get_post_record_service().update_post_record(post.post_id, update_data)
                    logger.info(f"✅ 更新資料庫貼文狀態: {post.post_id}")
                    break
            
            return {
                "success": True,
                "message": f"成功刪除文章 {article_id}",
                "article_id": article_id,
                "kol_serial": kol_serial,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 刪除文章 {article_id} 失敗")
            raise HTTPException(status_code=500, detail=f"刪除文章 {article_id} 失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Article ID: {article_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 刪除文章時發生錯誤 - Article ID: {article_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"刪除文章失敗: {str(e)}")


@router.delete("/{post_id}/delete")
async def delete_post_from_cmoney(post_id: str):
    """通過 post_id 刪除 CMoney 平台上的文章"""
    logger.info(f"🗑️ 開始刪除貼文 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        # 檢查是否已發布到 CMoney
        if not existing_post.cmoney_post_id:
            logger.error(f"❌ 貼文尚未發布到 CMoney - Post ID: {post_id}")
            raise HTTPException(status_code=400, detail=f"貼文尚未發布到 CMoney: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, CMoney Article ID: {existing_post.cmoney_post_id}")
        
        # 獲取KOL憑證
        from main import kol_credential_manager
        kol_serial = str(existing_post.kol_serial)
        kol_creds = kol_credential_manager.get_kol_credentials(kol_serial)
        if not kol_creds:
            logger.error(f"❌ 找不到KOL {kol_serial} 的憑證")
            raise HTTPException(status_code=404, detail=f"找不到KOL {kol_serial} 的憑證")
        
        logger.info(f"🔐 使用KOL {kol_serial} 憑證登入...")
        
        # 登入KOL
        access_token = await kol_credential_manager.login_kol(kol_serial)
        if not access_token:
            logger.error(f"❌ KOL {kol_serial} 登入失敗")
            raise HTTPException(status_code=401, detail=f"KOL {kol_serial} 登入失敗")
        
        logger.info(f"✅ KOL {kol_serial} 登入成功")
        
        # 使用CMoney Client刪除文章
        from src.clients.cmoney.cmoney_client import CMoneyClient
        cmoney_client = CMoneyClient()
        
        article_id = existing_post.cmoney_post_id
        logger.info(f"🗑️ 開始刪除文章 {article_id}...")
        delete_success = await cmoney_client.delete_article(access_token, article_id)
        
        if delete_success:
            logger.info(f"✅ 成功刪除文章 {article_id}")
            
            # 更新資料庫中的貼文狀態
            update_data = {
                "status": "deleted",
                "reviewer_notes": f"已刪除CMoney文章 {article_id}",
                "approved_by": "system"
            }
            get_post_record_service().update_post_record(post_id, update_data)
            logger.info(f"✅ 更新資料庫貼文狀態: {post_id}")
            
            return {
                "success": True,
                "message": f"成功刪除文章 {article_id}",
                "post_id": post_id,
                "article_id": article_id,
                "kol_serial": kol_serial,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 刪除文章 {article_id} 失敗")
            raise HTTPException(status_code=500, detail=f"刪除文章 {article_id} 失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 刪除貼文時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"刪除貼文失敗: {str(e)}")

@router.delete("/{post_id}")
async def delete_post(post_id: str):
    """刪除貼文（軟刪除）"""
    logger.info(f"🗑️ 開始刪除貼文 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 如果貼文已經發布到 CMoney，先從 CMoney 刪除
        if existing_post.cmoney_post_id and existing_post.status == 'published':
            logger.info(f"🔄 貼文已發布到 CMoney，先從平台刪除 - Article ID: {existing_post.cmoney_post_id}")
            
            try:
                # 獲取KOL憑證
                from main import kol_credential_manager
                kol_serial = str(existing_post.kol_serial)
                kol_creds = kol_credential_manager.get_kol_credentials(kol_serial)
                if kol_creds:
                    # 登入KOL
                    access_token = await kol_credential_manager.login_kol(kol_serial)
                    if access_token:
                        # 使用CMoney Client刪除文章
                        from src.clients.cmoney.cmoney_client import CMoneyClient
                        cmoney_client = CMoneyClient()
                        
                        article_id = existing_post.cmoney_post_id
                        delete_success = await cmoney_client.delete_article(access_token, article_id)
                        
                        if delete_success:
                            logger.info(f"✅ 成功從 CMoney 刪除文章 {article_id}")
                        else:
                            logger.warning(f"⚠️ 從 CMoney 刪除文章 {article_id} 失敗，但繼續執行軟刪除")
                    else:
                        logger.warning(f"⚠️ KOL {kol_serial} 登入失敗，但繼續執行軟刪除")
                else:
                    logger.warning(f"⚠️ 找不到KOL {kol_serial} 的憑證，但繼續執行軟刪除")
            except Exception as e:
                logger.warning(f"⚠️ 從 CMoney 刪除文章時發生錯誤: {str(e)}，但繼續執行軟刪除")
        
        # 執行軟刪除：更新貼文狀態為 deleted
        update_data = {
            "status": "deleted",
            "reviewer_notes": f"貼文已刪除 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "approved_by": "system",
            "updated_at": datetime.now()
        }
        
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文軟刪除成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            
            return {
                "success": True,
                "message": f"貼文已刪除",
                "post_id": post_id,
                "status": post_record.status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文狀態失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="刪除貼文失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 刪除貼文時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"刪除貼文失敗: {str(e)}")