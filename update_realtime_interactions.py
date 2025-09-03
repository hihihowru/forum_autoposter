#!/usr/bin/env python3
"""
更新即時互動數據腳本
從貼文記錄表讀取有 Article ID 的貼文，抓取即時互動數據並更新到「aigc 自我學習機制」分頁
"""

import asyncio
import logging
from datetime import datetime
from src.clients.google.sheets_client import GoogleSheetsClient
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealtimeInteractionUpdater:
    """即時互動數據更新器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        self.cmoney_client = CMoneyClient()
        # 初始化 token 快取
        self.cmoney_client._tokens = {}
        
    async def get_posts_with_article_id(self):
        """獲取有 Article ID 的貼文"""
        try:
            # 讀取貼文記錄表
            data = self.sheets_client.read_sheet('貼文記錄表', 'A:Y')
            
            posts_with_article_id = []
            
            for i, row in enumerate(data[1:], start=2):
                if len(row) >= 16:
                    post_id = row[0] if row[0] else ''
                    kol_serial = row[1] if len(row) > 1 else ''
                    kol_nickname = row[2] if len(row) > 2 else ''
                    kol_id = row[3] if len(row) > 3 else ''
                    persona = row[4] if len(row) > 4 else ''
                    topic_id = row[7] if len(row) > 7 else ''
                    title = row[8] if len(row) > 8 else ''
                    content = row[10] if len(row) > 10 else ''
                    status = row[11] if len(row) > 11 else ''
                    post_time = row[13] if len(row) > 13 else ''
                    article_id = row[15] if len(row) > 15 else ''
                    article_url = row[16] if len(row) > 16 else ''
                    trending_topic_title = row[17] if len(row) > 17 else ''
                    
                    if article_id and article_id.strip():
                        posts_with_article_id.append({
                            'row_num': i,
                            'post_id': post_id,
                            'kol_serial': kol_serial,
                            'kol_nickname': kol_nickname,
                            'kol_id': kol_id,
                            'persona': persona,
                            'topic_id': topic_id,
                            'title': title,
                            'content': content,
                            'status': status,
                            'post_time': post_time,
                            'article_id': article_id,
                            'article_url': article_url,
                            'trending_topic_title': trending_topic_title
                        })
            
            logger.info(f"找到 {len(posts_with_article_id)} 篇有 Article ID 的貼文")
            return posts_with_article_id
            
        except Exception as e:
            logger.error(f"獲取貼文記錄失敗: {e}")
            return []
    
    async def get_article_interactions(self, article_id: str, kol_credentials: dict):
        """獲取文章互動數據"""
        try:
            # 登入 KOL
            login_creds = LoginCredentials(
                email=kol_credentials['email'],
                password=kol_credentials['password']
            )
            
            access_token = await self.cmoney_client.login(login_creds)
            
            # 獲取互動數據
            interaction_data = await self.cmoney_client.get_article_interactions(
                access_token.token, 
                article_id
            )
            
            return interaction_data
            
        except Exception as e:
            logger.error(f"獲取文章 {article_id} 互動數據失敗: {e}")
            return None
    
    async def get_kol_credentials(self, kol_serial: str):
        """獲取 KOL 登入憑證"""
        try:
            # 讀取同學會帳號管理
            data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            for row in data[1:]:  # 跳過標題行
                if len(row) > 6 and str(row[0]) == str(kol_serial):
                    return {
                        'email': row[5] if len(row) > 5 else '',
                        'password': row[6] if len(row) > 6 else ''
                    }
            
            logger.warning(f"找不到 KOL {kol_serial} 的登入憑證")
            return None
            
        except Exception as e:
            logger.error(f"獲取 KOL 憑證失敗: {e}")
            return None
    
    async def update_interaction_data(self, posts_data):
        """更新互動數據到「aigc 自我學習機制」分頁"""
        try:
            # 準備要寫入的數據
            rows_to_write = []
            
            for post in posts_data:
                # 獲取 KOL 憑證
                kol_credentials = await self.get_kol_credentials(post['kol_serial'])
                if not kol_credentials:
                    continue
                
                # 獲取互動數據
                interaction_data = await self.get_article_interactions(
                    post['article_id'], 
                    kol_credentials
                )
                
                if interaction_data:
                    # 計算互動率
                    total_interactions = interaction_data.likes + interaction_data.comments
                    engagement_rate = (total_interactions / max(interaction_data.views, 1)) * 100 if interaction_data.views > 0 else 0
                    
                    # 準備行數據
                    row_data = [
                        post['article_id'],  # article_id
                        post['kol_id'],      # member_id
                        post['kol_nickname'], # nickname
                        post['title'],       # title
                        post['content'],     # content
                        post['topic_id'],    # topic_id
                        'TRUE',              # is_trending_topic
                        post['post_time'],   # post_time
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # last_update_time
                        str(interaction_data.likes),      # likes_count
                        str(interaction_data.comments),   # comments_count
                        str(total_interactions),                # total_interactions
                        f"{engagement_rate:.2f}%",              # engagement_rate
                        "0.00%",                               # growth_rate (暫時設為0)
                        ""                                     # collection_error
                    ]
                    
                    rows_to_write.append(row_data)
                    logger.info(f"準備更新 {post['kol_nickname']} 的互動數據: {total_interactions} 次互動")
                else:
                    logger.warning(f"無法獲取 {post['kol_nickname']} 的互動數據")
            
            # 寫入到「互動回饋_1hr」分頁（作為即時互動數據展示）
            if rows_to_write:
                # 先寫入標題行
                headers = [
                    'article_id',
                    'member_id', 
                    'nickname',
                    'title',
                    'content',
                    'topic_id',
                    'is_trending_topic',
                    'post_time',
                    'last_update_time',
                    'likes_count',
                    'comments_count',
                    'total_interactions',
                    'engagement_rate',
                    'growth_rate',
                    'collection_error'
                ]
                
                # 寫入標題行
                self.sheets_client.write_sheet('互動回饋_1hr', [headers], 'A1:O1')
                
                # 寫入數據行
                range_name = f'A2:O{len(rows_to_write) + 1}'
                self.sheets_client.write_sheet('互動回饋_1hr', rows_to_write, range_name)
                
                logger.info(f"✅ 成功更新 {len(rows_to_write)} 筆即時互動數據到「互動回饋_1hr」分頁")
            else:
                logger.warning("沒有數據需要更新")
                
        except Exception as e:
            logger.error(f"更新互動數據失敗: {e}")
    
    async def run(self):
        """執行更新流程"""
        logger.info("🚀 開始更新即時互動數據")
        
        # 獲取有 Article ID 的貼文
        posts = await self.get_posts_with_article_id()
        
        if not posts:
            logger.warning("沒有找到有 Article ID 的貼文")
            return
        
        # 更新互動數據
        await self.update_interaction_data(posts)
        
        logger.info("✅ 即時互動數據更新完成")

async def main():
    """主函數"""
    updater = RealtimeInteractionUpdater()
    await updater.run()

if __name__ == "__main__":
    asyncio.run(main())
