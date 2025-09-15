#!/usr/bin/env python3
"""
自動更新互動數據到 Google Sheets
從貼文記錄表讀取 article_id，通過 CMoney API 獲取互動數據，並更新到互動回饋即時總表
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class InteractionData:
    """互動數據結構"""
    article_id: str
    member_id: str
    nickname: str
    title: str
    content: str
    topic_id: str
    is_trending_topic: bool
    post_time: str
    last_update_time: str
    likes_count: int
    comments_count: int
    total_interactions: int
    engagement_rate: float
    growth_rate: float
    collection_error: str
    donation_count: int
    donation_amount: float
    emoji_type: str
    emoji_counts: Dict[str, int]
    total_emoji_count: int

class GoogleSheetsManager:
    """Google Sheets 管理器"""
    
    def __init__(self):
        self.credentials_file = 'credentials/google-service-account.json'
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """初始化 Google Sheets 服務"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets 服務初始化成功")
        except Exception as e:
            logger.error(f"❌ Google Sheets 服務初始化失敗: {e}")
            raise
    
    def read_post_records(self) -> List[Dict]:
        """讀取貼文記錄表"""
        try:
            range_name = '貼文記錄表!A2:Z1000'  # 讀取前1000行
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ 貼文記錄表為空")
                return []
            
            # 根據實際貼文記錄表結構定義欄位名稱
            headers = [
                'post_id', 'kol_serial', 'kol_nickname', 'stock_name', 'stock_code',
                'topic_id', 'platform_post_id', 'platform_post_url', 'title', 'content',
                'commodity_tags', 'status'
            ]
            
            posts = []
            for row in values:
                if len(row) >= 1 and row[0]:  # 確保有 post_id
                    post_data = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            post_data[header] = row[i]
                        else:
                            post_data[header] = ''
                    posts.append(post_data)
            
            logger.info(f"📖 成功讀取 {len(posts)} 筆貼文記錄")
            return posts
            
        except Exception as e:
            logger.error(f"❌ 讀取貼文記錄失敗: {e}")
            return []
    
    def update_interaction_data(self, interaction_data: List[InteractionData]):
        """更新互動數據到互動回饋即時總表"""
        try:
            # 準備更新數據
            update_values = []
            for data in interaction_data:
                row = [
                    data.article_id,
                    data.member_id,
                    data.nickname,
                    data.title,
                    data.content,
                    data.topic_id,
                    data.is_trending_topic,
                    data.post_time,
                    data.last_update_time,
                    data.likes_count,
                    data.comments_count,
                    data.total_interactions,
                    data.engagement_rate,
                    data.growth_rate,
                    data.collection_error,
                    data.donation_count,
                    data.donation_amount,
                    data.emoji_type,
                    json.dumps(data.emoji_counts, ensure_ascii=False),
                    data.total_emoji_count
                ]
                update_values.append(row)
            
            # 清空現有數據（保留標題行）
            range_name = '互動回饋即時總表!A2:Z1000'
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            # 寫入新數據
            body = {
                'values': update_values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='互動回饋即時總表!A2',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"✅ 成功更新 {len(interaction_data)} 筆互動數據到互動回饋即時總表")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新互動數據失敗: {e}")
            return False

class CMoneyAPIManager:
    """CMoney API 管理器"""
    
    def __init__(self):
        self.cmoney_client = CMoneyClient()
        # 使用預設的 KOL 帳號
        self.default_credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password=os.getenv('CMONEY_PASSWORD')
        )
        self.access_token = None
    
    async def login(self):
        """登入 CMoney"""
        try:
            self.access_token = await self.cmoney_client.login(self.default_credentials)
            logger.info("✅ CMoney 登入成功")
        except Exception as e:
            logger.error(f"❌ CMoney 登入失敗: {e}")
            raise
    
    async def get_article_interactions(self, article_id: str) -> Optional[Dict]:
        """獲取文章互動數據"""
        try:
            if not self.access_token:
                await self.login()
            
            interaction_data = await self.cmoney_client.get_article_interactions(
                self.access_token.token, 
                article_id
            )
            
            if interaction_data:
                # 轉換為字典格式
                result = {
                    'likes_count': interaction_data.likes,
                    'comments_count': interaction_data.comments,
                    'total_interactions': interaction_data.total_interactions,
                    'engagement_rate': interaction_data.engagement_rate,
                    'donation_count': interaction_data.donations,
                    'donation_amount': 0.0,  # CMoney API 沒有提供金額
                    'emoji_type': '👍',  # 預設表情
                    'emoji_counts': {
                        '👍': interaction_data.likes,
                        '👎': interaction_data.dislikes,
                        '😂': interaction_data.laughs,
                        '💰': interaction_data.money,
                        '😱': interaction_data.shock,
                        '😢': interaction_data.cry,
                        '🤔': interaction_data.think,
                        '😠': interaction_data.angry
                    },
                    'total_emoji_count': interaction_data.total_emojis
                }
                
                logger.info(f"✅ 成功獲取文章 {article_id} 的互動數據")
                return result
            else:
                logger.warning(f"⚠️ 無法獲取文章 {article_id} 的互動數據")
                return None
                
        except Exception as e:
            logger.error(f"❌ 獲取文章 {article_id} 互動數據時發生錯誤: {e}")
            return None

class InteractionDataProcessor:
    """互動數據處理器"""
    
    def __init__(self, cmoney_api: CMoneyAPIManager):
        self.cmoney_api = cmoney_api
    
    async def process_post_data(self, post_data: Dict) -> Optional[InteractionData]:
        """處理單筆貼文數據"""
        try:
            # 使用 platform_post_id 作為 article_id
            article_id = post_data.get('platform_post_id', '')
            if not article_id:
                logger.warning("⚠️ 貼文數據缺少 platform_post_id")
                return None
            
            # 獲取互動數據
            interaction_data = await self.cmoney_api.get_article_interactions(article_id)
            if not interaction_data:
                logger.warning(f"⚠️ 無法獲取文章 {article_id} 的互動數據")
                return None
            
            # 整合數據
            interaction = InteractionData(
                article_id=article_id,
                member_id=post_data.get('kol_serial', ''),
                nickname=post_data.get('kol_nickname', ''),
                title=post_data.get('title', ''),
                content=post_data.get('content', ''),
                topic_id=post_data.get('topic_id', ''),
                is_trending_topic=False,  # 暫時設為 False
                post_time=post_data.get('platform_post_url', ''),  # 使用 URL 作為 post_time
                last_update_time=datetime.now().isoformat(),
                likes_count=interaction_data.get('likes_count', 0),
                comments_count=interaction_data.get('comments_count', 0),
                total_interactions=interaction_data.get('total_interactions', 0),
                engagement_rate=interaction_data.get('engagement_rate', 0.0),
                growth_rate=0.0,  # 暫時設為 0
                collection_error='',
                donation_count=interaction_data.get('donation_count', 0),
                donation_amount=interaction_data.get('donation_amount', 0.0),
                emoji_type=interaction_data.get('emoji_type', ''),
                emoji_counts=interaction_data.get('emoji_counts', {}),
                total_emoji_count=interaction_data.get('total_emoji_count', 0)
            )
            
            logger.info(f"✅ 成功處理文章 {article_id} 的互動數據")
            return interaction
            
        except Exception as e:
            logger.error(f"❌ 處理貼文數據時發生錯誤: {e}")
            return None
    
    async def process_all_posts(self, posts: List[Dict]) -> List[InteractionData]:
        """處理所有貼文數據"""
        tasks = []
        for post in posts:
            task = self.process_post_data(post)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        interaction_data = []
        for result in results:
            if isinstance(result, InteractionData):
                interaction_data.append(result)
            elif isinstance(result, Exception):
                logger.error(f"❌ 處理貼文時發生錯誤: {result}")
        
        return interaction_data

async def main():
    """主函數"""
    try:
        logger.info("🚀 開始自動更新互動數據")
        
        # 初始化管理器
        sheets_manager = GoogleSheetsManager()
        cmoney_api = CMoneyAPIManager()
        processor = InteractionDataProcessor(cmoney_api)
        
        # 讀取貼文記錄
        posts = sheets_manager.read_post_records()
        if not posts:
            logger.warning("⚠️ 沒有找到貼文記錄")
            return
        
        logger.info(f"📖 找到 {len(posts)} 筆貼文記錄")
        
        # 處理所有貼文數據
        interaction_data = await processor.process_all_posts(posts)
        if not interaction_data:
            logger.warning("⚠️ 沒有成功處理任何互動數據")
            return
        
        logger.info(f"✅ 成功處理 {len(interaction_data)} 筆互動數據")
        
        # 更新到 Google Sheets
        success = sheets_manager.update_interaction_data(interaction_data)
        if success:
            logger.info("🎉 互動數據更新完成！")
        else:
            logger.error("❌ 更新到 Google Sheets 失敗")
        
    except Exception as e:
        logger.error(f"❌ 主程序執行失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
