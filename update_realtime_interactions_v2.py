#!/usr/bin/env python3
"""
更新即時互動數據到「互動回饋即時總表」
從貼文紀錄表讀取所有有 article_id 的貼文，透過 CM API 獲取詳細互動數據
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealtimeInteractionUpdaterV2:
    """即時互動數據更新器 V2"""
    
    def __init__(self):
        """初始化"""
        self.cmoney_client = CMoneyClient()
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
        )
        
        # 初始化 token 快取
        self.cmoney_client._tokens = {}
        
    async def get_posts_with_article_id(self) -> List[Dict[str, Any]]:
        """獲取有 Article ID 的貼文"""
        try:
            logger.info("📖 讀取貼文記錄表...")
            
            # 讀取貼文記錄表
            data = self.sheets_client.read_sheet('貼文記錄表', 'A:Z')
            
            if not data or len(data) < 2:
                logger.warning("貼文記錄表為空或格式錯誤")
                return []
            
            headers = data[0]
            rows = data[1:]
            
            # 找到關鍵欄位的索引
            field_indices = {}
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if 'platform_post_id' in header_lower or '貼文id' in header_lower:
                    field_indices['platform_post_id'] = i
                elif 'kol_serial' in header_lower or 'kol serial' in header_lower:
                    field_indices['kol_serial'] = i
                elif 'kol_nickname' in header_lower or 'kol 暱稱' in header_lower:
                    field_indices['kol_nickname'] = i
                elif 'kol_id' in header_lower or 'kol id' in header_lower:
                    field_indices['kol_id'] = i
                elif 'topic_id' in header_lower or 'topicid' in header_lower:
                    field_indices['topic_id'] = i
                elif 'topic_title' in header_lower or 'topictitle' in header_lower:
                    field_indices['topic_title'] = i
                elif 'generated_content' in header_lower or '生成內容' in header_lower:
                    field_indices['generated_content'] = i
                elif 'post_timestamp' in header_lower or '發文時間戳記' in header_lower:
                    field_indices['post_timestamp'] = i
                elif 'trending_topic_title' in header_lower or '熱門話題標題' in header_lower:
                    field_indices['trending_topic_title'] = i
            
            posts_with_article_id = []
            
            for i, row in enumerate(rows, 1):
                if len(row) > 0:
                    # 獲取 platform_post_id
                    platform_post_id_idx = field_indices.get('platform_post_id')
                    if platform_post_id_idx is None or len(row) <= platform_post_id_idx:
                        continue
                    
                    article_id = row[platform_post_id_idx].strip() if row[platform_post_id_idx] else ''
                    
                    if article_id:  # 只處理有 article_id 的貼文
                        post_data = {
                            'row_index': i,
                            'article_id': article_id,
                            'kol_serial': row[field_indices.get('kol_serial', 1)] if len(row) > field_indices.get('kol_serial', 1) else '',
                            'kol_nickname': row[field_indices.get('kol_nickname', 2)] if len(row) > field_indices.get('kol_nickname', 2) else '',
                            'kol_id': row[field_indices.get('kol_id', 3)] if len(row) > field_indices.get('kol_id', 3) else '',
                            'topic_id': row[field_indices.get('topic_id', 7)] if len(row) > field_indices.get('topic_id', 7) else '',
                            'topic_title': row[field_indices.get('topic_title', 8)] if len(row) > field_indices.get('topic_title', 8) else '',
                            'generated_content': row[field_indices.get('generated_content', 10)] if len(row) > field_indices.get('generated_content', 10) else '',
                            'post_timestamp': row[field_indices.get('post_timestamp', 13)] if len(row) > field_indices.get('post_timestamp', 13) else '',
                            'trending_topic_title': row[field_indices.get('trending_topic_title', 17)] if len(row) > field_indices.get('trending_topic_title', 17) else '',
                            'full_row': row
                        }
                        posts_with_article_id.append(post_data)
            
            logger.info(f"✅ 找到 {len(posts_with_article_id)} 個有 Article ID 的貼文")
            return posts_with_article_id
            
        except Exception as e:
            logger.error(f"❌ 獲取有 Article ID 的貼文失敗: {e}")
            return []
    
    async def get_interaction_data(self, article_id: str) -> Optional[Dict[str, Any]]:
        """透過 CM API 獲取互動數據"""
        try:
            # 使用川川哥的憑證登入
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password=os.getenv('CMONEY_PASSWORD')
            )
            
            # 登入獲取 token
            login_result = await self.cmoney_client.login(credentials)
            
            if not login_result or login_result.is_expired:
                logger.error(f"❌ 登入失敗或 Token 已過期")
                return None
            
            # 獲取互動數據
            interaction_data = await self.cmoney_client.get_article_interactions(
                login_result.token, 
                article_id
            )
            
            if interaction_data:
                # 解析表情數據
                emoji_details = {}
                emoji_total = 0
                
                if hasattr(interaction_data, 'raw_data') and interaction_data.raw_data:
                    emoji_count = interaction_data.raw_data.get('emojiCount', {})
                    if isinstance(emoji_count, dict):
                        emoji_details = emoji_count
                        emoji_total = sum(emoji_count.values())
                
                # 計算總互動數
                total_interactions = (interaction_data.likes + 
                                    interaction_data.comments + 
                                    interaction_data.shares + 
                                    emoji_total)
                
                # 計算互動率 (假設瀏覽數為 1000)
                engagement_rate = round(total_interactions / 1000.0, 3) if total_interactions > 0 else 0.0
                
                return {
                    'likes': interaction_data.likes,
                    'comments': interaction_data.comments,
                    'shares': interaction_data.shares,
                    'views': interaction_data.views,
                    'engagement_rate': interaction_data.engagement_rate,
                    'emoji_details': emoji_details,
                    'emoji_total': emoji_total,
                    'total_interactions': total_interactions,
                    'calculated_engagement_rate': engagement_rate,
                    'raw_data': interaction_data.raw_data
                }
            else:
                logger.warning(f"⚠️ 無法獲取 Article {article_id} 的互動數據")
                return None
                
        except Exception as e:
            logger.error(f"❌ 獲取 Article {article_id} 互動數據失敗: {e}")
            return None
    
    async def update_interaction_data(self, posts_data: List[Dict[str, Any]]):
        """更新互動數據到「互動回饋即時總表」"""
        try:
            logger.info("🔄 開始更新互動數據...")
            
            # 準備要寫入的數據
            rows_to_write = []
            current_time = datetime.now().isoformat()
            
            for post in posts_data:
                logger.info(f"📝 處理 {post['kol_nickname']} 的貼文 {post['article_id']}...")
                
                # 獲取互動數據
                interaction_data = await self.get_interaction_data(post['article_id'])
                
                if interaction_data:
                    # 準備行數據
                    row_data = [
                        post['article_id'],                    # A: article_id
                        post['kol_id'],                         # B: member_id
                        post['kol_nickname'],                   # C: nickname
                        f"貼文 {post['article_id']}",           # D: title
                        post['generated_content'][:100] if post['generated_content'] else '',  # E: content (截取前100字)
                        post['topic_id'],                       # F: topic_id
                        'TRUE' if post['trending_topic_title'] else 'FALSE',  # G: is_trending_topic
                        post['post_timestamp'],                 # H: post_time
                        current_time,                          # I: last_update_time
                        interaction_data['likes'],             # J: likes_count
                        interaction_data['comments'],          # K: comments_count
                        interaction_data['total_interactions'], # L: total_interactions
                        interaction_data['calculated_engagement_rate'],  # M: engagement_rate
                        0.0,                                   # N: growth_rate (暫時設為0)
                        '',                                    # O: collection_error
                        interaction_data.get('shares', 0),     # P: donation_count (用shares代替)
                        0.0,                                   # Q: donation_amount
                        '👍' if interaction_data['emoji_total'] > 0 else '',  # R: emoji_type
                        str(interaction_data['emoji_details']), # S: emoji_counts
                        interaction_data['emoji_total']         # T: total_emoji_count
                    ]
                    
                    rows_to_write.append(row_data)
                    logger.info(f"✅ {post['kol_nickname']} 的互動數據: {interaction_data['total_interactions']} 次互動")
                else:
                    # 如果無法獲取互動數據，也要記錄錯誤
                    error_row_data = [
                        post['article_id'],                    # A: article_id
                        post['kol_id'],                        # B: member_id
                        post['kol_nickname'],                  # C: nickname
                        f"貼文 {post['article_id']}",          # D: title
                        post['generated_content'][:100] if post['generated_content'] else '',  # E: content
                        post['topic_id'],                      # F: topic_id
                        'TRUE' if post['trending_topic_title'] else 'FALSE',  # G: is_trending_topic
                        post['post_timestamp'],                # H: post_time
                        current_time,                          # I: last_update_time
                        0,                                     # J: likes_count
                        0,                                     # K: comments_count
                        0,                                     # L: total_interactions
                        0.0,                                   # M: engagement_rate
                        0.0,                                   # N: growth_rate
                        '無法獲取互動數據',                      # O: collection_error
                        0,                                     # P: donation_count
                        0.0,                                   # Q: donation_amount
                        '',                                    # R: emoji_type
                        '{}',                                  # S: emoji_counts
                        0                                      # T: total_emoji_count
                    ]
                    rows_to_write.append(error_row_data)
                    logger.warning(f"⚠️ {post['kol_nickname']} 的互動數據獲取失敗")
            
            # 寫入到「互動回饋即時總表」
            if rows_to_write:
                # 先清空現有數據（保留標題行）
                logger.info("🗑️ 清空現有數據...")
                self.sheets_client.clear_sheet('互動回饋即時總表', 'A2:T1000')
                
                # 寫入新數據
                logger.info(f"📊 寫入 {len(rows_to_write)} 筆數據...")
                range_name = f'A2:T{len(rows_to_write) + 1}'
                self.sheets_client.write_sheet('互動回饋即時總表', rows_to_write, range_name)
                
                logger.info(f"✅ 成功更新 {len(rows_to_write)} 筆即時互動數據到「互動回饋即時總表」")
            else:
                logger.warning("⚠️ 沒有數據需要更新")
                
        except Exception as e:
            logger.error(f"❌ 更新互動數據失敗: {e}")
    
    async def run(self):
        """執行更新流程"""
        try:
            logger.info("🚀 開始更新即時互動數據...")
            logger.info("=" * 60)
            
            # 1. 獲取有 Article ID 的貼文
            posts_data = await self.get_posts_with_article_id()
            
            if not posts_data:
                logger.warning("⚠️ 沒有找到有 Article ID 的貼文")
                return
            
            # 2. 更新互動數據
            await self.update_interaction_data(posts_data)
            
            logger.info("✅ 即時互動數據更新完成！")
            
        except Exception as e:
            logger.error(f"❌ 更新流程失敗: {e}")

async def main():
    """主函數"""
    updater = RealtimeInteractionUpdaterV2()
    await updater.run()

if __name__ == "__main__":
    asyncio.run(main())
