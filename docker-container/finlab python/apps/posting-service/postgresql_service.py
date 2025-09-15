"""
PostgreSQL 貼文記錄服務
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import logging
from sqlalchemy.orm import Session
from database import PostRecord, get_db, create_tables
import json

logger = logging.getLogger(__name__)

class PostgreSQLPostRecordService:
    """PostgreSQL 貼文記錄服務"""
    
    def __init__(self):
        """初始化服務"""
        logger.info("🚀 初始化 PostgreSQL 貼文記錄服務")
        # 創建數據庫表
        create_tables()
        logger.info("✅ PostgreSQL 貼文記錄服務初始化完成")
    
    def create_post_record(self, post_data: dict) -> PostRecord:
        """創建貼文記錄"""
        try:
            post_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # 創建貼文記錄
            post_record = PostRecord(
                post_id=post_id,
                created_at=now,
                updated_at=now,
                session_id=post_data.get('session_id'),
                kol_serial=post_data.get('kol_serial'),
                kol_nickname=post_data.get('kol_nickname'),
                kol_persona=post_data.get('kol_persona'),
                stock_code=post_data.get('stock_code'),
                stock_name=post_data.get('stock_name'),
                title=post_data.get('title'),
                content=post_data.get('content'),
                content_md=post_data.get('content_md'),
                status=post_data.get('status', 'draft'),
                reviewer_notes=post_data.get('reviewer_notes'),
                approved_by=post_data.get('approved_by'),
                approved_at=post_data.get('approved_at'),
                published_at=post_data.get('published_at'),
                cmoney_post_id=post_data.get('cmoney_post_id'),
                cmoney_post_url=post_data.get('cmoney_post_url'),
                views=post_data.get('views', 0),
                likes=post_data.get('likes', 0),
                comments=post_data.get('comments', 0),
                shares=post_data.get('shares', 0),
                topic_id=post_data.get('topic_id'),
                topic_title=post_data.get('topic_title'),
                technical_analysis=post_data.get('technical_analysis'),
                serper_data=post_data.get('serper_data'),
                quality_score=post_data.get('quality_score'),
                ai_detection_score=post_data.get('ai_detection_score'),
                risk_level=post_data.get('risk_level'),
                generation_params=post_data.get('generation_params'),
                commodity_tags=post_data.get('commodity_tags')
            )
            
            # 保存到數據庫
            db = next(get_db())
            db.add(post_record)
            db.commit()
            db.refresh(post_record)
            db.close()
            
            logger.info(f"✅ 貼文記錄創建成功 - Post ID: {post_id}")
            return post_record
            
        except Exception as e:
            logger.error(f"❌ 創建貼文記錄失敗: {e}")
            raise
    
    def get_post_record(self, post_id: str) -> Optional[PostRecord]:
        """獲取特定貼文記錄"""
        try:
            db = next(get_db())
            post_record = db.query(PostRecord).filter(PostRecord.post_id == post_id).first()
            db.close()
            
            if post_record:
                logger.info(f"✅ 找到貼文記錄 - Post ID: {post_id}")
            else:
                logger.warning(f"❌ 貼文記錄不存在 - Post ID: {post_id}")
            
            return post_record
            
        except Exception as e:
            logger.error(f"❌ 獲取貼文記錄失敗: {e}")
            return None
    
    def update_post_record(self, post_id: str, update_data: dict) -> Optional[PostRecord]:
        """更新貼文記錄"""
        try:
            db = next(get_db())
            post_record = db.query(PostRecord).filter(PostRecord.post_id == post_id).first()
            
            if post_record:
                # 更新字段
                for key, value in update_data.items():
                    if hasattr(post_record, key) and value is not None:
                        setattr(post_record, key, value)
                
                post_record.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(post_record)
                db.close()
                
                logger.info(f"✅ 貼文記錄更新成功 - Post ID: {post_id}")
                return post_record
            else:
                logger.warning(f"❌ 貼文記錄不存在 - Post ID: {post_id}")
                db.close()
                return None
                
        except Exception as e:
            logger.error(f"❌ 更新貼文記錄失敗: {e}")
            return None
    
    def get_all_posts(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[PostRecord]:
        """獲取所有貼文記錄"""
        try:
            db = next(get_db())
            query = db.query(PostRecord)
            
            if status:
                query = query.filter(PostRecord.status == status)
            
            posts = query.offset(skip).limit(limit).all()
            db.close()
            
            logger.info(f"✅ 獲取貼文記錄成功 - 總數: {len(posts)}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ 獲取貼文記錄失敗: {e}")
            return []
    
    def get_session_posts(self, session_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[PostRecord]:
        """獲取特定session的貼文記錄"""
        try:
            db = next(get_db())
            query = db.query(PostRecord).filter(PostRecord.session_id == session_id)
            
            # 如果有狀態過濾條件，添加狀態過濾
            if status:
                query = query.filter(PostRecord.status == status)
            
            posts = query.offset(skip).limit(limit).all()
            db.close()
            
            logger.info(f"✅ 獲取session {session_id} 貼文記錄成功 - 總數: {len(posts)} (狀態過濾: {status})")
            return posts
            
        except Exception as e:
            logger.error(f"❌ 獲取session貼文記錄失敗: {e}")
            return []
    
    def delete_post_record(self, post_id: str) -> bool:
        """刪除貼文記錄"""
        try:
            db = next(get_db())
            post_record = db.query(PostRecord).filter(PostRecord.post_id == post_id).first()
            
            if post_record:
                db.delete(post_record)
                db.commit()
                db.close()
                logger.info(f"✅ 貼文記錄刪除成功 - Post ID: {post_id}")
                return True
            else:
                logger.warning(f"❌ 貼文記錄不存在 - Post ID: {post_id}")
                db.close()
                return False
                
        except Exception as e:
            logger.error(f"❌ 刪除貼文記錄失敗: {e}")
            return False
    
    def get_posts_count(self, status: Optional[str] = None) -> int:
        """獲取貼文記錄總數"""
        try:
            db = next(get_db())
            query = db.query(PostRecord)
            
            if status:
                query = query.filter(PostRecord.status == status)
            
            count = query.count()
            db.close()
            
            logger.info(f"✅ 獲取貼文記錄總數成功 - 總數: {count}")
            return count
            
        except Exception as e:
            logger.error(f"❌ 獲取貼文記錄總數失敗: {e}")
            return 0
    
    def create_post_record_simple(self, stock_code: str, stock_name: str, kol_serial: str, kol_nickname: str, session_id: int = None) -> PostRecord:
        """創建簡化版貼文記錄（繞過 CommodityTag 問題）"""
        try:
            # 生成簡單的 post_id (1, 2, 3, 4...)
            db = next(get_db())
            max_id = db.query(PostRecord).count()
            post_id = str(max_id + 1)
            db.close()
            
            now = datetime.utcnow()
            
            # 創建簡化的貼文記錄
            post_record = PostRecord(
                post_id=post_id,
                created_at=now,
                updated_at=now,
                session_id=session_id,
                kol_serial=kol_serial,
                kol_nickname=kol_nickname,
                stock_code=stock_code,
                stock_name=stock_name,
                title=f"【{kol_nickname}】{stock_name}({stock_code}) 盤後分析",
                content=f"這是 {kol_nickname} 針對 {stock_name}({stock_code}) 的簡化版貼文內容。",
                content_md=f"# {stock_name}({stock_code}) 分析\n\n這是 {kol_nickname} 的簡化版貼文內容。",
                status='draft',
                generation_params=json.dumps({
                    "method": "simple",
                    "bypass_commodity_tag": True,
                    "created_at": now.isoformat()
                })
            )
            
            # 保存到數據庫
            db = next(get_db())
            db.add(post_record)
            db.commit()
            db.refresh(post_record)
            db.close()
            
            logger.info(f"✅ 簡化版貼文記錄創建成功 - Post ID: {post_id}")
            return post_record
            
        except Exception as e:
            logger.error(f"❌ 創建簡化版貼文記錄失敗: {e}")
            raise