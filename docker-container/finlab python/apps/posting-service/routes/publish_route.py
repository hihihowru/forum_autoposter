"""
發文到 CMoney 的 API 路由
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/posts", tags=["publish"])

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

@router.post("/{post_id}/publish")
async def publish_post_to_cmoney(post_id: str):
    """發文到 CMoney 平台"""
    logger.info(f"🚀 開始發文到 CMoney - Post ID: {post_id}")
    
    try:
        # 1. 獲取貼文記錄
        post_service = get_post_record_service()
        existing_post = post_service.get_post_record(post_id)
        
        if not existing_post:
            logger.error(f"❌ 找不到貼文記錄 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail="找不到貼文記錄")
        
        if existing_post.status not in ['approved']:
            logger.error(f"❌ 貼文狀態不正確，無法發文 - Post ID: {post_id}, 狀態: {existing_post.status}")
            raise HTTPException(status_code=400, detail=f"貼文狀態為 {existing_post.status}，無法發文")
        
        logger.info(f"✅ 找到貼文記錄 - Post ID: {post_id}, 標題: {existing_post.title}")
        
        # 2. 準備發文數據
        from src.clients.cmoney.cmoney_client import CMoneyClient, ArticleData
        
        # 準備 communityTopic（使用 topic_id）
        community_topic = None
        if existing_post.topic_id:
            community_topic = existing_post.topic_id
            logger.info(f"📌 使用熱門話題標記 - Topic ID: {existing_post.topic_id}")
        
        # 準備 commodity tags
        commodity_tags = []
        if existing_post.stock_code and existing_post.stock_code != "TOPIC":
            commodity_tags.append({
                "type": "Stock",
                "key": existing_post.stock_code,
                "bullOrBear": 0  # 中性
            })
            logger.info(f"📊 添加股票標籤 - Stock Code: {existing_post.stock_code}")
        
        # 創建文章數據
        article_data_kwargs = {
            "title": existing_post.title,
            "text": existing_post.content_md or existing_post.content,
            "commodity_tags": commodity_tags
        }
        
        # 只有在有 topic_id 時才添加 communityTopic
        if community_topic:
            article_data_kwargs["communityTopic"] = {"id": community_topic}
        
        article_data = ArticleData(**article_data_kwargs)
        
        # 3. 獲取 KOL 憑證並發文
        cmoney_client = CMoneyClient()
        
        # 獲取 KOL 憑證（從 kol_service 獲取真實憑證）
        from kol_service import kol_service
        kol_creds = kol_service.get_kol_credentials(str(existing_post.kol_serial))
        
        if not kol_creds:
            logger.error(f"❌ 找不到 KOL {existing_post.kol_serial} 的憑證")
            raise HTTPException(status_code=404, detail=f"找不到KOL {existing_post.kol_serial} 的憑證")
        
        from src.clients.cmoney.cmoney_client import LoginCredentials
        kol_credentials = LoginCredentials(
            email=kol_creds['email'],
            password=kol_creds['password']
        )
        
        # 登入 CMoney
        access_token_obj = await cmoney_client.login(kol_credentials)
        if not access_token_obj:
            logger.error(f"❌ KOL {existing_post.kol_serial} 登入 CMoney 失敗")
            raise HTTPException(status_code=500, detail="KOL 登入失敗")
        
        logger.info(f"✅ KOL {existing_post.kol_serial} 登入成功")
        
        # 發文到 CMoney
        publish_result = await cmoney_client.publish_article(access_token_obj.token, article_data)
        
        if not publish_result.success:
            logger.error(f"❌ 發文到 CMoney 失敗 - Post ID: {post_id}, 錯誤: {publish_result.error_message}")
            raise HTTPException(status_code=500, detail=f"發文失敗: {publish_result.error_message}")
        
        logger.info(f"✅ 發文到 CMoney 成功 - Post ID: {post_id}, Article ID: {publish_result.post_id}")
        
        # 4. 更新貼文記錄
        update_data = {
            'status': 'published',
            'published_at': datetime.now(),
            'cmoney_post_id': publish_result.post_id,
            'cmoney_post_url': publish_result.post_url
        }
        
        updated_post = post_service.update_post_record(post_id, update_data)
        
        if updated_post:
            logger.info(f"✅ 貼文記錄更新成功 - Post ID: {post_id}")
            
            return {
                "success": True,
                "message": "貼文發佈成功",
                "post_id": publish_result.post_id,
                "post_url": publish_result.post_url,
                "published_at": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文記錄失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="更新貼文記錄失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 發文時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"發文失敗: {str(e)}")
