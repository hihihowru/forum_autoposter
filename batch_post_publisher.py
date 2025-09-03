#!/usr/bin/env python3
"""
批次漲停股貼文發文腳本
每3分鐘發一篇，使用直接CMoneyClient方式
"""

import asyncio
import json
import logging
import os
import sys
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, ArticleData

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchPostPublisher:
    """批次貼文發文器"""
    
    def __init__(self):
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 初始化 CMoney 客戶端
        self.cmoney_client = CMoneyClient()
        
        # KOL 登入資訊
        self.kol_credentials = {
            "200": {  # 川川哥
                "email": "forum_200@cmoney.com.tw",
                "password": "N9t1kY3x",
                "member_id": "9505546"
            },
            "201": {  # 韭割哥
                "email": "forum_201@cmoney.com.tw", 
                "password": "m7C1lR4t",
                "member_id": "9505547"
            },
            "202": {  # 梅川褲子
                "email": "forum_202@cmoney.com.tw",
                "password": "k8D2mN5v",
                "member_id": "9505548"
            },
            "203": {  # 信號宅神
                "email": "forum_203@cmoney.com.tw",
                "password": "p9E3nO6w",
                "member_id": "9505549"
            },
            "204": {  # 八卦護城河
                "email": "forum_204@cmoney.com.tw",
                "password": "q0F4oP7x",
                "member_id": "9505550"
            },
            "205": {  # 長線韭韭
                "email": "forum_205@cmoney.com.tw",
                "password": "r1G5pQ8y",
                "member_id": "9505551"
            },
            "206": {  # 報爆哥_209
                "email": "forum_206@cmoney.com.tw",
                "password": "s2H6qR9z",
                "member_id": "9505552"
            },
            "207": {  # 板橋大who
                "email": "forum_207@cmoney.com.tw",
                "password": "t3I7rS0a",
                "member_id": "9505553"
            },
            "208": {  # 韭割哥
                "email": "forum_208@cmoney.com.tw",
                "password": "u4J8sT1b",
                "member_id": "9505554"
            },
            "209": {  # 小道爆料王
                "email": "forum_209@cmoney.com.tw",
                "password": "v5K9tU2c",
                "member_id": "9505555"
            }
        }
        
        # 已登入的KOL tokens
        self.kol_tokens = {}
    
    async def load_pending_posts(self) -> List[Dict[str, Any]]:
        """從Google Sheets載入待發布的貼文"""
        try:
            # 讀取貼文記錄表
            posts_data = self.sheets_client.read_sheet('貼文記錄表', 'A:AH')
            
            pending_posts = []
            for row in posts_data[1:]:  # 跳過標題行
                if len(row) >= 12 and row[11] == 'pending':  # L欄位是Status
                    post = {
                        'post_id': row[0],  # A欄位
                        'kol_serial': row[1],  # B欄位
                        'kol_nickname': row[2],  # C欄位
                        'stock_name': row[3],  # D欄位
                        'stock_id': row[4],  # E欄位
                        'topic_id': row[5],  # F欄位
                        'generated_title': row[8],  # I欄位
                        'generated_content': row[9],  # J欄位
                        'commodity_tags': json.loads(row[10]) if row[10] else []  # K欄位
                    }
                    pending_posts.append(post)
            
            logger.info(f"📖 載入 {len(pending_posts)} 篇待發布貼文")
            return pending_posts
            
        except Exception as e:
            logger.error(f"載入待發布貼文失敗: {e}")
            return []
    
    async def login_all_kols(self) -> bool:
        """登入所有KOL帳號"""
        logger.info("🔐 開始登入所有KOL帳號...")
        
        success_count = 0
        for kol_serial, creds in self.kol_credentials.items():
            try:
                logger.info(f"登入 KOL {kol_serial} ({creds['email']})...")
                
                token = await self.cmoney_client.login(
                    LoginCredentials(
                        email=creds['email'],
                        password=creds['password']
                    )
                )
                
                self.kol_tokens[kol_serial] = token
                logger.info(f"✅ KOL {kol_serial} 登入成功")
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ KOL {kol_serial} 登入失敗: {e}")
        
        logger.info(f"📊 登入結果: {success_count}/{len(self.kol_credentials)} 個KOL成功")
        return success_count > 0
    
    async def publish_single_post(self, post: Dict[str, Any]) -> bool:
        """發布單篇貼文"""
        try:
            kol_serial = post['kol_serial']
            
            # 檢查KOL是否已登入
            if kol_serial not in self.kol_tokens:
                logger.error(f"❌ KOL {kol_serial} 未登入，跳過發布")
                return False
            
            token = self.kol_tokens[kol_serial]
            
            logger.info(f"📝 發布貼文: {post['stock_name']}({post['stock_id']})")
            logger.info(f"👤 KOL: {post['kol_nickname']}")
            logger.info(f"📋 標題: {post['generated_title']}")
            
            # 準備文章數據
            article_data = ArticleData(
                title=post['generated_title'],
                text=post['generated_content'],
                commodity_tags=post['commodity_tags']
            )
            
            # 發布文章
            publish_result = await self.cmoney_client.publish_article(token.token, article_data)
            
            if publish_result.success:
                logger.info(f"✅ 發布成功: {post['stock_name']}")
                logger.info(f"📝 文章ID: {publish_result.post_id}")
                logger.info(f"🔗 文章URL: {publish_result.post_url}")
                
                # 更新Google Sheets狀態
                await self.update_post_status(post['post_id'], 'published', publish_result.post_id, publish_result.post_url)
                
                return True
            else:
                logger.error(f"❌ 發布失敗: {publish_result.error_message}")
                await self.update_post_status(post['post_id'], 'failed', '', '', publish_result.error_message)
                return False
                
        except Exception as e:
            logger.error(f"❌ 發布過程出錯: {e}")
            await self.update_post_status(post['post_id'], 'error', '', '', str(e))
            return False
    
    async def update_post_status(self, post_id: str, status: str, article_id: str = '', article_url: str = '', error_msg: str = ''):
        """更新Google Sheets中的貼文狀態"""
        try:
            # 讀取貼文記錄表
            posts_data = self.sheets_client.read_sheet('貼文記錄表', 'A:AH')
            
            # 找到對應的貼文
            for i, row in enumerate(posts_data):
                if row[0] == post_id:  # A欄位是post_id
                    # 更新狀態
                    update_data = [
                        status,  # L: Status
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # M: Scheduled Time
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # N: Post Time
                        error_msg,  # O: Error Message
                        article_id,  # P: Platform Post ID
                        article_url  # Q: Platform Post URL
                    ]
                    
                    # 寫回 Google Sheets
                    range_name = f'L{i+1}:Q{i+1}'
                    self.sheets_client.write_sheet('貼文記錄表', [update_data], range_name)
                    logger.info(f"📊 更新狀態: {post_id} -> {status}")
                    break
                    
        except Exception as e:
            logger.error(f"更新Google Sheets失敗: {e}")
    
    async def run_batch_publishing(self):
        """執行批次發布"""
        logger.info("🚀 啟動批次漲停股貼文發布系統...")
        logger.info("⏰ 每3分鐘發布一篇貼文")
        
        # 載入待發布貼文
        pending_posts = await self.load_pending_posts()
        if not pending_posts:
            logger.error("❌ 沒有待發布的貼文")
            return
        
        # 登入所有KOL
        if not await self.login_all_kols():
            logger.error("❌ KOL登入失敗，無法繼續發布")
            return
        
        logger.info("🎯 開始批次發布...")
        
        for i, post in enumerate(pending_posts, 1):
            logger.info(f"============================================================")
            logger.info(f"📝 發布第 {i}/{len(pending_posts)} 篇貼文")
            logger.info(f"⏰ 當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 發布貼文
            success = await self.publish_single_post(post)
            
            if success:
                logger.info(f"✅ 第 {i} 篇發布完成")
            else:
                logger.error(f"❌ 第 {i} 篇發布失敗")
            
            # 如果不是最後一篇，等待3分鐘
            if i < len(pending_posts):
                wait_time = 180  # 3分鐘
                logger.info(f"⏳ 等待 {wait_time} 秒後發布下一篇...")
                
                # 倒計時顯示
                for remaining in range(wait_time, 0, -30):
                    logger.info(f"⏰ 剩餘等待時間: {remaining//60}分{remaining%60}秒")
                    await asyncio.sleep(30)
                
                # 最後30秒倒計時
                for remaining in range(30, 0, -10):
                    logger.info(f"⏰ 最後倒計時: {remaining}秒")
                    await asyncio.sleep(10)
        
        logger.info("🎯 批次發布完成！")

async def main():
    """主函數"""
    publisher = BatchPostPublisher()
    await publisher.run_batch_publishing()

if __name__ == "__main__":
    asyncio.run(main())
