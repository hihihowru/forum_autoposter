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
        # KOL憑證配置 - 從Google Sheets讀取
        self.kol_credentials = {}
        self._load_kol_credentials()
        
        # Token快取
        self.kol_tokens = {}
        
        logger.info("🔐 貼文發佈服務初始化完成")
    
    def _load_kol_credentials(self):
        """從KOL服務載入KOL憑證"""
        try:
            # 使用新的 KOL 服務
            from kol_service import kol_service
            
            # 獲取所有 KOL 憑證
            for serial in kol_service.get_all_kol_serials():
                creds = kol_service.get_kol_credentials(serial)
                if creds:
                    self.kol_credentials[serial] = {
                        "email": creds["email"],
                        "password": creds["password"],
                        "member_id": serial
                    }
                    logger.info(f"載入KOL憑證: {serial} - {creds['email']}")
            
            logger.info(f"✅ 成功載入 {len(self.kol_credentials)} 個KOL憑證")
            
        except Exception as e:
            logger.error(f"❌ 從KOL服務載入KOL憑證失敗: {e}")
            logger.info("使用預設配置")
            self._load_default_credentials()
    
    def _load_default_credentials(self):
        """載入預設KOL憑證（備用方案）"""
        self.kol_credentials = {
            "186": {"email": "forum_186@cmoney.com.tw", "password": "t7L9uY0f", "member_id": "186"},
            "187": {"email": "forum_187@cmoney.com.tw", "password": "a4E9jV8t", "member_id": "187"},
            "188": {"email": "forum_188@cmoney.com.tw", "password": "z6G5wN2m", "member_id": "188"},
            "189": {"email": "forum_189@cmoney.com.tw", "password": "c8L5nO3q", "member_id": "189"},
            "190": {"email": "forum_190@cmoney.com.tw", "password": "W4x6hU0r", "member_id": "190"},
            "191": {"email": "forum_191@cmoney.com.tw", "password": "H7u4rE2j", "member_id": "191"},
            "192": {"email": "forum_192@cmoney.com.tw", "password": "S3c6oJ9h", "member_id": "192"},
            "193": {"email": "forum_193@cmoney.com.tw", "password": "X2t1vU7l", "member_id": "193"},
            "194": {"email": "forum_194@cmoney.com.tw", "password": "j3H5dM7p", "member_id": "194"},
            "195": {"email": "forum_195@cmoney.com.tw", "password": "P9n1fT3x", "member_id": "195"},
            "196": {"email": "forum_196@cmoney.com.tw", "password": "b4C1pL3r", "member_id": "196"},
            "197": {"email": "forum_197@cmoney.com.tw", "password": "O8a3pF4c", "member_id": "197"},
            "198": {"email": "forum_198@cmoney.com.tw", "password": "i0L5fC3s", "member_id": "198"}
        }
        logger.info("使用預設KOL憑證配置")
    
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
            # 添加正確的路徑 - src 目錄現在掛載在 /app/src
            src_path = '/app/src'
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
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
            # 添加正確的路徑 - src 目錄現在掛載在 /app/src
            src_path = '/app/src'
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            from src.clients.cmoney.cmoney_client import ArticleData, CMoneyClient
            
            # 構建商品標籤
            commodity_tags = []
            if post_record.stock_code:
                commodity_tags.append({
                    "type": "Stock",
                    "key": post_record.stock_code,
                    "bullOrBear": 0  # 預設為0，可以根據內容分析調整
                })
            
            # 構建社區話題標籤
            communityTopic = None
            if hasattr(post_record, 'topic_id') and post_record.topic_id:
                communityTopic = {"id": post_record.topic_id}
                logger.info(f"🏷️ 設置社區話題標籤: {post_record.topic_id}")
            
            # 構建文章數據
            article_data = ArticleData(
                title=post_record.title,
                text=post_record.content,
                commodity_tags=commodity_tags,
                communityTopic=communityTopic
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
