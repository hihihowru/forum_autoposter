#!/usr/bin/env python3
"""
每分鐘發文腳本
使用統一貼文生成架構，每分鐘發一篇文
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, ArticleData
from src.clients.google.sheets_client import GoogleSheetsClient
from unified_post_generator import UnifiedPostGenerator

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinutePublisher:
    """每分鐘發文器"""
    
    def __init__(self):
        # 初始化服務
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        self.cmoney_client = CMoneyClient()
        self.post_generator = UnifiedPostGenerator()
        
        # KOL登入憑證
        self.kol_credentials = {
            "200": {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x", "member_id": "200"},
            "201": {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t", "member_id": "201"},
            "202": {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p", "member_id": "202"},
            "203": {"email": "forum_203@cmoney.com.tw", "password": "y7O3cL9k", "member_id": "203"},
            "204": {"email": "forum_204@cmoney.com.tw", "password": "f4E9sC8w", "member_id": "204"},
            "205": {"email": "forum_205@cmoney.com.tw", "password": "Z5u6dL9o", "member_id": "205"},
            "206": {"email": "forum_206@cmoney.com.tw", "password": "T1t7kS9j", "member_id": "206"},
            "207": {"email": "forum_207@cmoney.com.tw", "password": "w2B3cF6l", "member_id": "207"},
            "208": {"email": "forum_208@cmoney.com.tw", "password": "q4N8eC7h", "member_id": "208"},
            "209": {"email": "forum_209@cmoney.com.tw", "password": "V5n6hK0f", "member_id": "209"},
            "210": {"email": "forum_210@cmoney.com.tw", "password": "D8k9mN2p", "member_id": "210"}
        }
        
        # 登入token快取
        self.kol_tokens = {}
        
        logger.info("✅ 每分鐘發文器初始化完成")
    
    async def login_kol(self, kol_serial: str) -> bool:
        """登入KOL帳號"""
        try:
            if kol_serial in self.kol_tokens:
                return True
            
            kol_creds = self.kol_credentials.get(kol_serial)
            if not kol_creds:
                logger.error(f"❌ 找不到KOL {kol_serial} 的憑證")
                return False
            
            token = await self.cmoney_client.login(
                LoginCredentials(
                    email=kol_creds['email'],
                    password=kol_creds['password']
                )
            )
            
            if token and token.token:
                self.kol_tokens[kol_serial] = token.token
                logger.info(f"✅ KOL {kol_serial} 登入成功")
                return True
            else:
                logger.error(f"❌ KOL {kol_serial} 登入失敗")
                return False
                
        except Exception as e:
            logger.error(f"❌ KOL {kol_serial} 登入異常: {e}")
            return False
    
    async def publish_single_post(self, post: Dict[str, Any]) -> bool:
        """發布單篇貼文"""
        try:
            kol_serial = str(post['kol_serial'])
            
            # 登入KOL
            login_success = await self.login_kol(kol_serial)
            if not login_success:
                return False
            
            # 準備文章資料
            article_data = ArticleData(
                title=post['generated_title'],
                text=post['generated_content'],
                commodity_tags=post['commodity_tags']
            )
            
            # 發布文章
            token = self.kol_tokens[kol_serial]
            publish_result = await self.cmoney_client.publish_article(token, article_data)
            
            if publish_result and publish_result.success:
                logger.info(f"✅ 發布成功: {post['stock_name']}")
                logger.info(f"📝 文章ID: {publish_result.post_id}")
                logger.info(f"🔗 文章URL: {publish_result.post_url}")
                
                # 更新Google Sheets狀態
                await self.update_post_status(post['post_id'], 'published', {
                    'post_id': publish_result.post_id,
                    'post_url': publish_result.post_url
                })
                return True
            else:
                error_msg = publish_result.error_message if publish_result else "Unknown error"
                logger.error(f"❌ 發布失敗: {error_msg}")
                await self.update_post_status(post['post_id'], 'failed', error_msg)
                return False
                
        except Exception as e:
            logger.error(f"❌ 發布貼文異常: {e}")
            await self.update_post_status(post['post_id'], 'error', str(e))
            return False
    
    async def update_post_status(self, post_id: str, status: str, result: str = "") -> None:
        """更新Google Sheets中的貼文狀態"""
        try:
            # 讀取現有資料
            posts_data = self.sheets_client.read_sheet('貼文記錄表')
            
            # 找到對應的行並更新狀態
            for i, row in enumerate(posts_data):
                if len(row) > 0 and row[0] == post_id:
                    # 更新狀態欄位 (L欄位)
                    self.sheets_client.update_cell('貼文記錄表', f"L{i+1}", status)
                    
                    # 如果有結果，更新到G欄位（平台發文ID）和H欄位（平台發文URL）
                    if result:
                        # 解析結果，提取文章ID和URL
                        if isinstance(result, dict):
                            article_id = result.get('post_id', '')
                            article_url = result.get('post_url', '')
                        else:
                            article_id = str(result)
                            article_url = f"https://www.cmoney.tw/forum/article/{article_id}"
                        
                        self.sheets_client.update_cell('貼文記錄表', f"G{i+1}", article_id)
                        self.sheets_client.update_cell('貼文記錄表', f"H{i+1}", article_url)
                    
                    logger.info(f"✅ 更新貼文狀態: {post_id} -> {status}")
                    break
                    
        except Exception as e:
            logger.error(f"❌ 更新貼文狀態失敗: {e}")
    
    def load_pending_posts(self) -> List[Dict[str, Any]]:
        """載入待發布的貼文"""
        try:
            posts_data = self.sheets_client.read_sheet('貼文記錄表')
            pending_posts = []
            
            for row in posts_data[1:]:  # 跳過標題行
                if len(row) >= 12:
                    status = row[11] if len(row) > 11 else ''
                    
                    # 檢查是否為待發布狀態
                    if status not in ['published', 'failed', 'error'] and status.strip():
                        post = {
                            'post_id': row[0],
                            'kol_serial': row[1],
                            'kol_nickname': row[2],
                            'stock_name': row[3],
                            'stock_id': row[4],
                            'topic_id': row[5],
                            'generated_title': row[8],
                            'generated_content': row[9],
                            'commodity_tags': json.loads(row[10]) if row[10] else []
                        }
                        pending_posts.append(post)
            
            logger.info(f"📋 載入 {len(pending_posts)} 篇待發布貼文")
            return pending_posts
            
        except Exception as e:
            logger.error(f"❌ 載入待發布貼文失敗: {e}")
            return []
    
    async def run_minute_publishing(self, interval_minutes: int = 1):
        """執行每分鐘發文"""
        logger.info(f"🚀 開始每分鐘發文，間隔: {interval_minutes} 分鐘")
        
        # 載入待發布貼文
        pending_posts = self.load_pending_posts()
        
        if not pending_posts:
            logger.warning("⚠️ 沒有待發布的貼文")
            return
        
        logger.info(f"📊 總共 {len(pending_posts)} 篇貼文待發布")
        
        # 開始發文循環
        for i, post in enumerate(pending_posts):
            try:
                logger.info(f"\n📝 發布第 {i+1}/{len(pending_posts)} 篇貼文")
                logger.info(f"KOL: {post['kol_nickname']}")
                logger.info(f"股票: {post['stock_name']}({post['stock_id']})")
                logger.info(f"標題: {post['generated_title']}")
                
                # 發布貼文
                success = await self.publish_single_post(post)
                
                if success:
                    logger.info(f"✅ 第 {i+1} 篇發布成功")
                else:
                    logger.error(f"❌ 第 {i+1} 篇發布失敗")
                
                # 如果不是最後一篇，等待指定間隔
                if i < len(pending_posts) - 1:
                    logger.info(f"⏳ 等待 {interval_minutes} 分鐘後發布下一篇...")
                    await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"❌ 發布第 {i+1} 篇貼文時發生異常: {e}")
                continue
        
        logger.info("🎯 所有貼文發布完成！")

async def main():
    """主函數"""
    publisher = MinutePublisher()
    
    # 執行每分鐘發文
    await publisher.run_minute_publishing(interval_minutes=1)

if __name__ == "__main__":
    asyncio.run(main())
