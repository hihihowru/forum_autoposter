"""
發文服務
負責處理 KOL 登入、發文和更新 Google Sheets
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.clients.cmoney.cmoney_client import CMoneyClient, ArticleData, PublishResult
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.content.content_generator import ContentGenerator
from src.services.classification.topic_classifier import TopicClassifier
from src.services.publish.tag_enhancer import TagEnhancer

logger = logging.getLogger(__name__)


class PublishService:
    """發文服務"""
    
    def __init__(self, sheets_client: GoogleSheetsClient):
        """
        初始化發文服務
        
        Args:
            sheets_client: Google Sheets 客戶端
        """
        self.sheets_client = sheets_client
        self.cmoney_client = CMoneyClient()
        self.kol_tokens: Dict[int, AccessToken] = {}  # 存儲 KOL 的 access token
        
        logger.info("發文服務初始化完成")
    
    async def login_kol(self, kol_serial: int, email: str, password: str) -> bool:
        """
        登入 KOL 帳號
        
        Args:
            kol_serial: KOL 序號
            email: 電子郵件
            password: 密碼
            
        Returns:
            登入是否成功
        """
        try:
            credentials = LoginCredentials(email=email, password=password)
            token = await self.cmoney_client.login(credentials)
            
            # 檢查 token 是否有效（未過期）
            if token and not token.is_expired:
                self.kol_tokens[kol_serial] = token
                logger.info(f"KOL {kol_serial} 登入成功")
                return True
            else:
                logger.error(f"KOL {kol_serial} 登入失敗或 token 已過期")
                return False
                
        except Exception as e:
            logger.error(f"KOL {kol_serial} 登入異常: {e}")
            return False
    
    async def publish_post(self, kol_serial: int, title: str, content: str, topic_id: str) -> Optional[PublishResult]:
        """
        發布貼文
        
        Args:
            kol_serial: KOL 序號
            title: 標題
            content: 內容
            topic_id: 話題 ID
            
        Returns:
            發文結果
        """
        try:
            # 檢查是否有有效的 token
            if kol_serial not in self.kol_tokens:
                logger.error(f"KOL {kol_serial} 未登入")
                return None
            
            token = self.kol_tokens[kol_serial]
            if token.is_expired:
                logger.error(f"KOL {kol_serial} token 已過期")
                return None
            
            # 準備文章數據（暫時不指定話題，避免 404 錯誤）
            article = ArticleData(
                title=title,
                text=content,
                community_topic=None  # 暫時不指定話題
            )
            
            # 發布文章
            result = await self.cmoney_client.publish_article(token.token, article)
            
            if result.success:
                logger.info(f"KOL {kol_serial} 發文成功: {result.post_id}")
            else:
                logger.error(f"KOL {kol_serial} 發文失敗: {result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"KOL {kol_serial} 發文異常: {e}")
            return None
    
    async def publish_posts_with_interval(self, posts: List[Dict[str, Any]], interval_minutes: int = 2) -> List[Dict[str, Any]]:
        """
        間隔發文
        
        Args:
            posts: 貼文列表，每個貼文包含 kol_serial, title, content, topic_id, post_id
            interval_minutes: 間隔分鐘數
            
        Returns:
            發文結果列表
        """
        results = []
        
        for i, post in enumerate(posts):
            try:
                logger.info(f"開始發文 {i+1}/{len(posts)}: KOL {post['kol_serial']}")
                
                # 發文
                result = await self.publish_post(
                    kol_serial=post['kol_serial'],
                    title=post['title'],
                    content=post['content'],
                    topic_id=post.get('topic_id', '')
                )
                
                # 記錄結果
                post_result = {
                    'post_id': post['post_id'],
                    'kol_serial': post['kol_serial'],
                    'success': result.success if result else False,
                    'article_id': result.post_id if result and result.success else None,
                    'article_url': result.post_url if result and result.success else None,
                    'error_message': result.error_message if result and not result.success else None
                }
                
                results.append(post_result)
                
                # 更新 Google Sheets
                await self._update_post_result(post_result)
                
                # 如果不是最後一篇，等待間隔時間
                if i < len(posts) - 1:
                    wait_seconds = interval_minutes * 60
                    logger.info(f"等待 {interval_minutes} 分鐘後發下一篇...")
                    await asyncio.sleep(wait_seconds)
                
            except Exception as e:
                logger.error(f"發文 {i+1} 異常: {e}")
                results.append({
                    'post_id': post['post_id'],
                    'kol_serial': post['kol_serial'],
                    'success': False,
                    'article_id': None,
                    'article_url': None,
                    'error_message': str(e)
                })
        
        return results
    
    async def _update_post_result(self, result: Dict[str, Any]):
        """
        更新貼文結果到 Google Sheets
        
        Args:
            result: 發文結果
        """
        try:
            # 讀取現有數據
            existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:R')
            
            # 找到對應的記錄
            found_record = False
            for i, row in enumerate(existing_data[1:], start=2):  # 跳過標題行
                if len(row) > 0 and row[0] == result['post_id']:  # 第一列是 post_id
                    found_record = True
                    # 更新發文狀態和 article ID
                    update_data = [
                        result['post_id'],  # 貼文ID
                        result['kol_serial'],  # KOL Serial
                        row[2] if len(row) > 2 else '',  # KOL 暱稱
                        row[3] if len(row) > 3 else '',  # KOL ID
                        row[4] if len(row) > 4 else '',  # Persona
                        row[5] if len(row) > 5 else '',  # Content Type
                        row[6] if len(row) > 6 else '',  # 已派發TopicIndex
                        row[7] if len(row) > 7 else '',  # 已派發TopicID
                        row[8] if len(row) > 8 else '',  # 已派發TopicTitle
                        row[9] if len(row) > 9 else '',  # 已派發TopicKeywords
                        row[10] if len(row) > 10 else '',  # 生成內容
                        "posted" if result['success'] else "post_failed",  # 發文狀態
                        row[12] if len(row) > 12 else '',  # 上次排程時間
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S") if result['success'] else '',  # 發文時間戳記
                        result['error_message'] if not result['success'] else '',  # 最近錯誤訊息
                        result['article_id'] if result['success'] else '',  # 平台發文ID
                        result['article_url'] if result['success'] else '',  # 平台發文URL
                        row[17] if len(row) > 17 else ''  # 熱門話題標題
                    ]
                    
                    # 寫入更新
                    range_name = f'A{i}:R{i}'
                    self.sheets_client.write_sheet('貼文記錄表', [update_data], range_name)
                    
                    logger.info(f"✅ 更新貼文記錄 {result['post_id']}: 狀態={update_data[11]}, Article ID={result['article_id']}")
                    break
            
            if not found_record:
                logger.error(f"❌ 找不到貼文記錄 {result['post_id']}，無法更新發文結果")
                logger.error(f"   可用的 post_id 列表: {[row[0] for row in existing_data[1:] if len(row) > 0]}")
                    
        except Exception as e:
            logger.error(f"更新貼文結果失敗: {e}")
    
    def get_ready_to_post_records(self) -> List[Dict[str, Any]]:
        """
        獲取準備發文的記錄（每個 KOL 只取一篇，確保去重）
        
        Returns:
            準備發文的記錄列表
        """
        try:
            # 讀取貼文記錄表
            data = self.sheets_client.read_sheet('貼文記錄表', 'A:R')
            
            ready_posts = []
            kol_posts = {}  # 用於去重：kol_serial -> post
            
            for row in data[1:]:  # 跳過標題行
                if len(row) >= 12 and row[11] == "ready_to_post":  # 發文狀態列
                    # 只取有內容的記錄（內容長度 > 0）
                    content = row[10] if len(row) > 10 else ""
                    post_id = row[0] if row[0] else ""
                    
                    # 排除測試貼文
                    if (content and len(content.strip()) > 0 and 
                        not post_id.startswith(('debug_', 'test_', 'improved_test_', 'general_test_'))):
                        
                        kol_serial = int(row[1]) if row[1] else 0
                        
                        # 檢查是否已經有這個 KOL 的記錄
                        if kol_serial not in kol_posts:
                            post = {
                                'post_id': post_id,
                                'kol_serial': kol_serial,
                                'kol_nickname': row[2],
                                'kol_id': row[3],
                                'title': row[8],  # 已派發TopicTitle
                                'content': content,  # 生成內容
                                'topic_id': row[7]  # 已派發TopicID
                            }
                            kol_posts[kol_serial] = post
            
            # 轉換為列表
            ready_posts = list(kol_posts.values())
            
            logger.info(f"找到 {len(ready_posts)} 篇準備發文的記錄（已去重，每個 KOL 一篇）")
            return ready_posts
            
        except Exception as e:
            logger.error(f"獲取準備發文記錄失敗: {e}")
            return []
    
    async def login_all_kols(self) -> bool:
        """
        登入所有 KOL
        
        Returns:
            是否所有 KOL 都登入成功
        """
        try:
            # 讀取 KOL 配置
            data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            if not data or len(data) < 2:
                logger.error("無法讀取 KOL 配置")
                return False
            
            headers = data[0]
            kol_data = data[1:]
            
            # 找到相關列的索引
            serial_idx = headers.index('序號') if '序號' in headers else 0
            email_idx = headers.index('Email(帳號)') if 'Email(帳號)' in headers else 5
            password_idx = headers.index('密碼') if '密碼' in headers else 6
            status_idx = headers.index('狀態') if '狀態' in headers else 9
            
            success_count = 0
            total_count = 0
            
            for row in kol_data:
                if len(row) > max(serial_idx, email_idx, password_idx, status_idx):
                    serial = int(row[serial_idx]) if row[serial_idx] else 0
                    email = row[email_idx] if row[email_idx] else ''
                    password = row[password_idx] if row[password_idx] else ''
                    status = row[status_idx] if row[status_idx] else ''
                    
                    if serial > 0 and email and password and status == 'active':
                        total_count += 1
                        success = await self.login_kol(serial, email, password)
                        if success:
                            success_count += 1
            
            logger.info(f"KOL 登入完成: {success_count}/{total_count} 成功")
            return success_count == total_count and total_count > 0
            
        except Exception as e:
            logger.error(f"登入所有 KOL 失敗: {e}")
            return False
