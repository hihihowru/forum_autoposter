"""
互動數據相關的 API 路由
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio
import os
import sys

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

# 導入 CMoney 客戶端
try:
    from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
except ImportError as e:
    logger.error(f"❌ 無法導入 CMoney 客戶端: {e}")
    # 創建一個假的類來避免錯誤
    class CMoneyClient:
        pass
    class LoginCredentials:
        def __init__(self, email: str, password: str):
            self.email = email
            self.password = password

# 創建路由器
router = APIRouter(prefix="/interactions", tags=["interactions"])

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

@router.post("/update/{post_id}")
async def update_post_interactions(post_id: str, interaction_data: Dict[str, Any]):
    """更新特定貼文的互動數據"""
    logger.info(f"🔄 開始更新貼文互動數據 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        logger.info(f"✅ 找到貼文 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
        
        # 準備更新數據
        update_data = {
            'views': interaction_data.get('views', existing_post.views),
            'likes': interaction_data.get('likes', existing_post.likes),
            'comments': interaction_data.get('comments', existing_post.comments),
            'shares': interaction_data.get('shares', existing_post.shares),
            'updated_at': datetime.now()
        }
        
        logger.info(f"📊 更新互動數據 - 瀏覽: {update_data['views']}, 讚: {update_data['likes']}, 留言: {update_data['comments']}, 分享: {update_data['shares']}")
        
        # 更新貼文記錄
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文互動數據更新成功 - Post ID: {post_id}")
            return {
                "success": True,
                "message": "互動數據更新成功",
                "post_id": post_id,
                "interaction_data": {
                    "views": post_record.views,
                    "likes": post_record.likes,
                    "comments": post_record.comments,
                    "shares": post_record.shares
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文互動數據失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新互動數據失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 更新互動數據時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"更新互動數據失敗: {str(e)}")

@router.post("/batch-update")
async def batch_update_interactions(background_tasks: BackgroundTasks):
    """批量更新所有已發布貼文的互動數據"""
    logger.info("🔄 開始批量更新互動數據")
    
    try:
        # 獲取所有已發布的貼文
        published_posts = get_post_record_service().get_all_posts(status='published')
        
        if not published_posts:
            logger.warning("❌ 沒有找到已發布的貼文")
            return {
                "success": True,
                "message": "沒有找到已發布的貼文",
                "updated_count": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"📊 找到 {len(published_posts)} 個已發布的貼文")
        
        # 在背景任務中更新互動數據
        background_tasks.add_task(update_interactions_background, published_posts)
        
        return {
            "success": True,
            "message": f"已開始批量更新 {len(published_posts)} 個貼文的互動數據",
            "total_posts": len(published_posts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 批量更新互動數據失敗: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"批量更新失敗: {str(e)}")

async def update_interactions_background(published_posts: List):
    """背景任務：更新互動數據"""
    logger.info(f"🔄 背景任務開始更新 {len(published_posts)} 個貼文的互動數據")
    
    # 定義不追蹤互動數據的 KOL 黑名單
    KOLS_TO_SKIP = [166, 210, 212]
    
    updated_count = 0
    skipped_count = 0
    
    for post in published_posts:
        try:
            # 檢查是否在黑名單中
            if post.kol_serial in KOLS_TO_SKIP:
                logger.info(f"⏭️ 跳過 KOL-{post.kol_serial} 的貼文 {post.post_id}，不在追蹤範圍內")
                skipped_count += 1
                continue
            
            # 如果沒有 CMoney 文章 ID，跳過
            if not post.cmoney_post_id:
                logger.warning(f"⚠️ 貼文 {post.post_id} 沒有 CMoney 文章 ID，跳過")
                continue
            
            # 獲取互動數據（這裡使用模擬數據，實際應該從 CMoney API 獲取）
            interaction_data = await get_cmoney_interaction_data(post.cmoney_post_id, post.kol_serial)
            
            if interaction_data:
                # 更新貼文記錄
                update_data = {
                    'views': interaction_data.get('views', 0),
                    'likes': interaction_data.get('likes', 0),
                    'comments': interaction_data.get('comments', 0),
                    'shares': interaction_data.get('shares', 0),
                    'updated_at': datetime.now()
                }
                
                post_record = get_post_record_service().update_post_record(post.post_id, update_data)
                
                if post_record:
                    updated_count += 1
                    logger.info(f"✅ 更新成功 - {post.kol_nickname} 的貼文 {post.post_id}")
                else:
                    logger.error(f"❌ 更新失敗 - 貼文 {post.post_id}")
            else:
                logger.warning(f"⚠️ 無法獲取互動數據 - 貼文 {post.post_id}")
            
            # 避免請求過於頻繁
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ 更新貼文 {post.post_id} 互動數據失敗: {str(e)}")
            continue
    
    logger.info(f"✅ 背景任務完成，成功更新 {updated_count} 個貼文的互動數據，跳過 {skipped_count} 個不在追蹤範圍內的貼文")

async def get_kol_credentials(kol_serial: int) -> Optional[LoginCredentials]:
    """根據 KOL serial 獲取對應的登入憑證"""
    try:
        # 從環境變數獲取 KOL 憑證
        import os
        kol_email = os.getenv(f'KOL_{kol_serial}_EMAIL')
        kol_password = os.getenv(f'KOL_{kol_serial}_PASSWORD')
        
        if kol_email and kol_password:
            credentials = LoginCredentials(email=kol_email, password=kol_password)
            logger.info(f"✅ 從環境變數獲取 KOL-{kol_serial} 憑證")
            return credentials
        else:
            logger.warning(f"⚠️ 環境變數中找不到 KOL-{kol_serial} 的憑證")
            # 嘗試使用預設 KOL 憑證
            default_email = os.getenv('DEFAULT_KOL_EMAIL')
            default_password = os.getenv('DEFAULT_KOL_PASSWORD')
            
            if default_email and default_password:
                return LoginCredentials(email=default_email, password=default_password)
            else:
                logger.error(f"❌ 環境變數中找不到預設 KOL 憑證")
                return None
        
            
    except Exception as e:
        logger.error(f"❌ 從環境變數獲取 KOL 憑證失敗: {e}")
        return None

async def get_kol_credentials(kol_serial: int) -> Optional[LoginCredentials]:
    """根據 KOL serial 獲取對應的登入憑證"""
    try:
        # 從環境變數獲取 KOL 憑證
        import os
        kol_email = os.getenv(f'KOL_{kol_serial}_EMAIL')
        kol_password = os.getenv(f'KOL_{kol_serial}_PASSWORD')
        
        if kol_email and kol_password:
            credentials = LoginCredentials(email=kol_email, password=kol_password)
            logger.info(f"✅ 從環境變數獲取 KOL-{kol_serial} 憑證")
            return credentials
        else:
            logger.warning(f"⚠️ 環境變數中找不到 KOL-{kol_serial} 的憑證")
            # 嘗試使用預設 KOL 憑證
            default_email = os.getenv('DEFAULT_KOL_EMAIL')
            default_password = os.getenv('DEFAULT_KOL_PASSWORD')
            
            if default_email and default_password:
                return LoginCredentials(email=default_email, password=default_password)
            else:
                logger.error(f"❌ 環境變數中找不到預設 KOL 憑證")
                return None
        
            
    except Exception as e:
        logger.error(f"❌ 從環境變數獲取 KOL 憑證失敗: {e}")
        return None

async def get_cmoney_interaction_data(article_id: str, kol_serial: int) -> Optional[Dict[str, Any]]:
    """從 CMoney API 獲取真實互動數據（使用數據庫憑證）"""
    try:
        # 定義不追蹤互動數據的 KOL 黑名單
        KOLS_TO_SKIP = [166, 210, 212]
        
        # 檢查是否在黑名單中
        if kol_serial in KOLS_TO_SKIP:
            logger.info(f"⏭️ 跳過 KOL-{kol_serial} 的互動數據獲取，不在追蹤範圍內")
            return None
        
        # 首先嘗試從數據庫獲取 KOL 憑證
        credentials = await get_kol_credentials_from_db(kol_serial)
        if not credentials:
            logger.warning(f"⚠️ 無法從數據庫獲取 KOL {kol_serial} 的憑證，使用硬編碼憑證")
            # 回退到硬編碼憑證
            credentials = await get_kol_credentials(kol_serial)
        
        # 初始化客戶端
        client = CMoneyClient()
        
        # 登入獲取 token
        login_result = await client.login(credentials)
        
        if not login_result or login_result.is_expired:
            logger.error(f"❌ KOL-{kol_serial} 登入失敗 - Article ID: {article_id}")
            return None
        
        # 獲取互動數據
        interaction_data = await client.get_article_interactions(
            login_result.token, 
            article_id
        )
        
        if interaction_data:
            # 轉換為標準格式
            result = {
                'views': interaction_data.views or 0,
                'likes': interaction_data.likes or 0,
                'comments': interaction_data.comments or 0,
                'shares': interaction_data.shares or 0,
                'engagement_rate': interaction_data.engagement_rate or 0,
                'emoji_count': interaction_data.raw_data.get('emojiCount', {}) if interaction_data.raw_data else {}
            }
            
            logger.info(f"📊 獲取真實互動數據 - Article ID: {article_id}, 數據: {result}")
            return result
        else:
            logger.warning(f"⚠️ 無法獲取互動數據 - Article ID: {article_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 獲取 CMoney 互動數據失敗: {str(e)}")
        logger.warning(f"⚠️ 無法獲取真實互動數據 - Article ID: {article_id}")
        return None

async def get_kol_credentials_from_db(kol_serial: int):
    """從 KOL SQL 數據庫獲取憑證"""
    try:
        from kol_database_service import kol_db_service
        
        kol_data = kol_db_service.get_kol_by_serial(str(kol_serial))
        
        if not kol_data:
            logger.warning(f"⚠️ 找不到 KOL-{kol_serial} 的數據")
            return None
            
        credentials = LoginCredentials(
            email=kol_data.email,
            password=kol_data.password
        )
        
        logger.info(f"✅ 從數據庫獲取 KOL-{kol_serial} 憑證: {kol_data.email}")
        return credentials
        
    except Exception as e:
        logger.error(f"❌ 從數據庫獲取 KOL-{kol_serial} 憑證失敗: {e}")
        return None

def get_mock_interaction_data() -> Dict[str, Any]:
    """生成模擬互動數據（備用方案）"""
    import random
    
    mock_data = {
        'views': random.randint(50, 500),
        'likes': random.randint(5, 50),
        'comments': random.randint(2, 20),
        'shares': random.randint(1, 10),
        'engagement_rate': random.uniform(5.0, 25.0),
        'emoji_count': {}
    }
    
    logger.info(f"📊 使用模擬互動數據: {mock_data}")
    return mock_data

@router.get("/stats")
async def get_interaction_stats():
    """獲取互動數據統計"""
    try:
        # 獲取所有已發布的貼文
        published_posts = get_post_record_service().get_all_posts(status='published')
        
        if not published_posts:
            return {
                "success": True,
                "stats": {
                    "total_posts": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "avg_engagement_rate": 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # 計算統計數據
        total_views = sum(post.views or 0 for post in published_posts)
        total_likes = sum(post.likes or 0 for post in published_posts)
        total_comments = sum(post.comments or 0 for post in published_posts)
        total_shares = sum(post.shares or 0 for post in published_posts)
        
        # 計算平均互動率
        total_interactions = total_likes + total_comments + total_shares
        avg_engagement_rate = (total_interactions / max(total_views, 1)) * 100 if total_views > 0 else 0
        
        stats = {
            "total_posts": len(published_posts),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "avg_engagement_rate": round(avg_engagement_rate, 2)
        }
        
        logger.info(f"📊 互動數據統計: {stats}")
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取互動數據統計失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取統計數據失敗: {str(e)}")
