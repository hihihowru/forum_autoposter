"""
還原貼文端點
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/posts", tags=["posts"])

# 導入全局服務實例 - 避免循環導入
post_record_service = None

def get_post_record_service():
    global post_record_service
    if post_record_service is None:
        from main import get_post_record_service as get_service
        post_record_service = get_service()
    return post_record_service

@router.post("/{post_id}/restore")
async def restore_post(post_id: str):
    """還原已刪除的貼文"""
    logger.info(f"🔄 開始還原貼文 - Post ID: {post_id}")
    
    try:
        # 檢查貼文是否存在
        existing_post = get_post_record_service().get_post_record(post_id)
        if not existing_post:
            logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")
        
        # 檢查貼文是否為已刪除狀態
        if existing_post.status != 'deleted':
            logger.error(f"❌ 貼文不是已刪除狀態，無法還原 - Post ID: {post_id}, 當前狀態: {existing_post.status}")
            raise HTTPException(status_code=400, detail=f"貼文不是已刪除狀態，無法還原: {post_id}")
        
        logger.info(f"✅ 找到已刪除的貼文 - Post ID: {post_id}")
        
        # 還原貼文：將狀態改為 approved（已審核）
        update_data = {
            "status": "approved",
            "reviewer_notes": f"貼文已還原 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "approved_by": "system",
            "updated_at": datetime.now()
        }
        
        post_record = get_post_record_service().update_post_record(post_id, update_data)
        
        if post_record:
            logger.info(f"✅ 貼文還原成功 - Post ID: {post_id}, 新狀態: {post_record.status}")
            
            return {
                "success": True,
                "message": f"貼文已還原",
                "post_id": post_id,
                "status": post_record.status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ 更新貼文狀態失敗 - Post ID: {post_id}")
            raise HTTPException(status_code=500, detail="還原貼文失敗")
            
    except HTTPException as e:
        logger.error(f"❌ HTTP 異常 - Post ID: {post_id}, 狀態碼: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"❌ 還原貼文時發生錯誤 - Post ID: {post_id}, 錯誤: {str(e)}")
        import traceback
        logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"還原貼文失敗: {str(e)}")
