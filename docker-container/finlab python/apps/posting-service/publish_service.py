"""
貼文發佈服務
處理KOL登入和CMoney平台發佈
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class PostPublishService:
    """貼文發佈服務"""
    
    def __init__(self):
        # KOL憑證配置
        self.kol_credentials = {
            "150": {"email": "forum_150@cmoney.com.tw", "password": "N9t1kY3x", "member_id": "150"},
            "151": {"email": "forum_151@cmoney.com.tw", "password": "m7C1lR4t", "member_id": "151"},
            "152": {"email": "forum_152@cmoney.com.tw", "password": "x2U9nW5p", "member_id": "152"},
            "153": {"email": "forum_153@cmoney.com.tw", "password": "y7O3cL9k", "member_id": "153"},
            "154": {"email": "forum_154@cmoney.com.tw", "password": "f4E9sC8w", "member_id": "154"},
            "155": {"email": "forum_155@cmoney.com.tw", "password": "Z5u6dL9o", "member_id": "155"},
            "156": {"email": "forum_156@cmoney.com.tw", "password": "T1t7kS9j", "member_id": "156"},
            "157": {"email": "forum_157@cmoney.com.tw", "password": "w2B3cF6l", "member_id": "157"},
            "158": {"email": "forum_158@cmoney.com.tw", "password": "q4N8eC7h", "member_id": "158"},
            "159": {"email": "forum_159@cmoney.com.tw", "password": "V5n6hK0f", "member_id": "159"},
            "160": {"email": "forum_160@cmoney.com.tw", "password": "D8k9mN2p", "member_id": "160"}
        }
        
        # Token快取
        self.kol_tokens = {}
        
        logger.info("🔐 貼文發佈服務初始化完成")
    
    def get_kol_credentials(self, kol_serial: str) -> Optional[Dict[str, str]]:
        """獲取KOL憑證"""
        return self.kol_credentials.get(str(kol_serial))
    
    async def login_kol(self, kol_serial: str) -> Optional[str]:
        """登入KOL並返回access token"""
        try:
            # 檢查是否已有有效token
            if kol_serial in self.kol_tokens:
                token_data = self.kol_tokens[kol_serial]
                if token_data.get('expires_at') and datetime.now() < token_data['expires_at']:
                    logger.info(f"✅ 使用快取的KOL {kol_serial} token")
                    return token_data['token']
            
            # 獲取憑證
            creds = self.get_kol_credentials(kol_serial)
            if not creds:
                logger.error(f"❌ 找不到KOL {kol_serial} 的憑證")
                return None
            
            logger.info(f"🔐 開始登入KOL {kol_serial}...")
            
            # 使用CMoney Client登入
            import sys
            import os
            # 添加正確的路徑
            project_root = os.path.join(os.path.dirname(__file__), '../../../..')
            sys.path.insert(0, project_root)
            from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
            cmoney_client = CMoneyClient()
            
            credentials = LoginCredentials(
                email=creds['email'],
                password=creds['password']
            )
            
            access_token = await cmoney_client.login(credentials)
            
            if access_token and access_token.token:
                # 快取token
                self.kol_tokens[kol_serial] = {
                    'token': access_token.token,
                    'expires_at': access_token.expires_at
                }
                logger.info(f"✅ KOL {kol_serial} 登入成功")
                return access_token.token
            else:
                logger.error(f"❌ KOL {kol_serial} 登入失敗")
                return None
                
        except Exception as e:
            logger.error(f"❌ KOL {kol_serial} 登入異常: {e}")
            return None
    
    async def publish_to_cmoney(self, post_record, access_token: str) -> Dict[str, Any]:
        """發佈貼文到CMoney平台"""
        try:
            import sys
            import os
            # 添加正確的路徑
            project_root = os.path.join(os.path.dirname(__file__), '../../../..')
            sys.path.insert(0, project_root)
            from src.clients.cmoney.cmoney_client import ArticleData, CommodityTag, CommunityTopic, CMoneyClient
            
            # 構建商品標籤
            commodity_tags = []
            if post_record.stock_code:
                commodity_tags.append(CommodityTag(
                    type="Stock",
                    key=post_record.stock_code,
                    bullOrBear=0  # 預設為0，可以根據內容分析調整
                ))
            
            # 構建文章數據
            article_data = ArticleData(
                title=post_record.title,
                text=post_record.content,
                commodity_tags=commodity_tags,
                community_topic=None  # 可以根據需要設置話題
            )
            
            logger.info(f"📤 準備發文數據: 標題={article_data.title[:50]}...")
            
            # 發佈到CMoney
            cmoney_client = CMoneyClient()
            publish_result = await cmoney_client.publish_article(access_token, article_data)
            
            if publish_result.success:
                logger.info(f"✅ 貼文發佈成功: {publish_result.post_id}")
                
                # 生成正確的CMoney貼文URL
                post_url = f"https://www.cmoney.tw/forum/article/{publish_result.post_id}"
                
                return {
                    "success": True,
                    "post_id": publish_result.post_id,
                    "article_id": publish_result.post_id,  # 添加article_id字段
                    "post_url": post_url,
                    "published_at": datetime.now()
                }
            else:
                logger.error(f"❌ 貼文發佈失敗: {publish_result.error_message}")
                return {
                    "success": False,
                    "error_message": publish_result.error_message
                }
                
        except Exception as e:
            logger.error(f"❌ 發佈到CMoney異常: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def publish_post(self, post_record) -> Dict[str, Any]:
        """完整的貼文發佈流程"""
        try:
            logger.info(f"🚀 開始發佈貼文 {post_record.post_id} 到CMoney...")
            logger.info(f"📝 貼文資訊: {post_record.title}")
            logger.info(f"👤 KOL: {post_record.kol_serial}")
            
            # 1. 登入KOL
            access_token = await self.login_kol(str(post_record.kol_serial))
            if not access_token:
                raise HTTPException(status_code=401, detail="KOL登入失敗")
            
            # 2. 發佈到CMoney
            publish_result = await self.publish_to_cmoney(post_record, access_token)
            
            if publish_result["success"]:
                return {
                    "success": True,
                    "message": "貼文發佈成功",
                    "post_id": publish_result["post_id"],
                    "post_url": publish_result["post_url"],
                    "published_at": publish_result["published_at"].isoformat()
                }
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"發佈失敗: {publish_result['error_message']}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 發佈貼文異常: {e}")
            raise HTTPException(status_code=500, detail=f"發佈異常: {str(e)}")

# 全域發佈服務實例
publish_service = PostPublishService()
