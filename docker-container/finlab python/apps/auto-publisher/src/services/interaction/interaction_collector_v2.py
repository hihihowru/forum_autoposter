"""
互動數據收集服務 V2
簡化的互動數據收集，支援新的表格結構
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class SimplifiedInteractionRecord:
    """簡化的互動數據記錄"""
    # 基礎資訊
    article_id: str              # Article ID (平台文章ID)
    member_id: str               # Member ID (KOL會員ID)
    nickname: str                # 暱稱
    title: str                   # 標題
    content: str                 # 生成內文
    topic_id: str                # Topic ID
    is_trending_topic: str       # 是否為熱門話題 (TRUE/FALSE)
    
    # 時間資訊
    post_time: str               # 發文時間
    last_update_time: str        # 最後更新時間 (收集時間)
    
    # 互動數據
    likes_count: int = 0         # 按讚數
    comments_count: int = 0      # 留言數
    
    # 錯誤處理
    collection_error: str = ""   # 收集錯誤訊息

class SimplifiedInteractionCollector:
    """簡化的互動數據收集器"""
    
    def __init__(self):
        """初始化收集器"""
        from clients.google.sheets_client import GoogleSheetsClient
        from clients.cmoney.cmoney_client import CMoneyClient
        
        # 初始化客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-service-account.json'),
            spreadsheet_id=os.getenv('GOOGLE_SPREADSHEET_ID')
        )
        
        self.cmoney_client = CMoneyClient()
        self.max_retries = 3
        self.timeout = 30
        
        logger.info("簡化互動數據收集器初始化完成")
    
    async def get_post_details_from_record_table(self, post_id: str) -> Optional[Dict[str, str]]:
        """
        從貼文記錄表獲取貼文詳細資訊
        
        Args:
            post_id: 貼文ID (task_id 格式)
            
        Returns:
            貼文詳細資訊
        """
        try:
            # 讀取貼文記錄表
            post_data = self.sheets_client.read_sheet('貼文記錄表', 'A:W')
            headers = post_data[0] if post_data else []
            rows = post_data[1:] if len(post_data) > 1 else []
            
            # 查找對應的貼文記錄
            for row in rows:
                if len(row) > 0 and row[0] == post_id:  # 貼文ID匹配
                    
                    # 提取需要的欄位
                    post_details = {
                        'task_id': row[0] if len(row) > 0 else '',
                        'kol_serial': row[1] if len(row) > 1 else '',
                        'kol_nickname': row[2] if len(row) > 2 else '',
                        'member_id': row[3] if len(row) > 3 else '',
                        'topic_title': row[8] if len(row) > 8 else '',
                        'generated_content': row[10] if len(row) > 10 else '',
                        'topic_id': row[7] if len(row) > 7 else '',
                        'post_timestamp': row[13] if len(row) > 13 else '',
                        'platform_post_id': row[15] if len(row) > 15 else '',
                        'is_trending': 'TRUE'  # 目前都是熱門話題
                    }
                    
                    logger.info(f"成功從貼文記錄表獲取貼文詳情: {post_id}")
                    return post_details
            
            logger.warning(f"在貼文記錄表中未找到貼文: {post_id}")
            return None
            
        except Exception as e:
            logger.error(f"從貼文記錄表獲取貼文詳情失敗: {e}")
            return None
    
    async def collect_interaction_data_for_post(self, post_id: str, collection_type: str) -> Optional[SimplifiedInteractionRecord]:
        """
        收集單個貼文的互動數據
        
        Args:
            post_id: 貼文ID
            collection_type: 收集類型 ('1h', '1d', '7d')
            
        Returns:
            簡化的互動數據記錄
        """
        try:
            # 從貼文記錄表獲取基礎資訊
            post_details = await self.get_post_details_from_record_table(post_id)
            
            if not post_details:
                logger.error(f"無法獲取貼文 {post_id} 的基礎資訊")
                return None
            
            platform_post_id = post_details.get('platform_post_id')
            if not platform_post_id:
                logger.error(f"貼文 {post_id} 缺少平台貼文ID")
                return None
            
            # 使用 KOL 的登入憑證獲取 token
            from clients.cmoney.cmoney_client import LoginCredentials
            
            # 暫時使用川川哥的憑證 (實際應該根據 KOL ID 動態選擇)
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password='N9t1kY3x'
            )
            
            token = await self.cmoney_client.login(credentials)
            
            # 收集互動數據
            interaction_data = await self.cmoney_client.get_article_interactions(
                token.token, 
                platform_post_id
            )
            
            # 準備簡化的互動記錄
            collection_time = datetime.now().isoformat()
            
            # 創建簡化記錄
            simplified_record = SimplifiedInteractionRecord(
                # 基礎資訊
                article_id=platform_post_id,
                member_id=post_details.get('member_id', ''),
                nickname=post_details.get('kol_nickname', ''),
                title=post_details.get('topic_title', ''),
                content=post_details.get('generated_content', ''),
                topic_id=post_details.get('topic_id', ''),
                is_trending_topic=post_details.get('is_trending', 'TRUE'),
                
                # 時間資訊
                post_time=post_details.get('post_timestamp', ''),
                last_update_time=collection_time,
                
                # 互動數據
                likes_count=interaction_data.likes if interaction_data else 0,
                comments_count=interaction_data.comments if interaction_data else 0,
                
                # 錯誤處理
                collection_error=""
            )
            
            logger.info(f"成功收集貼文 {platform_post_id} 的互動數據: 讚={simplified_record.likes_count}, 留言={simplified_record.comments_count}")
            
            return simplified_record
            
        except Exception as e:
            logger.error(f"收集貼文 {post_id} 互動數據失敗: {e}")
            
            # 返回錯誤記錄
            post_details = await self.get_post_details_from_record_table(post_id)
            if post_details:
                error_record = SimplifiedInteractionRecord(
                    article_id=post_details.get('platform_post_id', ''),
                    member_id=post_details.get('member_id', ''),
                    nickname=post_details.get('kol_nickname', ''),
                    title=post_details.get('topic_title', ''),
                    content=post_details.get('generated_content', ''),
                    topic_id=post_details.get('topic_id', ''),
                    is_trending_topic=post_details.get('is_trending', 'TRUE'),
                    post_time=post_details.get('post_timestamp', ''),
                    last_update_time=datetime.now().isoformat(),
                    likes_count=0,
                    comments_count=0,
                    collection_error=str(e)
                )
                return error_record
            
            return None
    
    async def save_simplified_interaction_data(self, records: List[SimplifiedInteractionRecord], table_name: str):
        """
        保存簡化的互動數據到 Google Sheets
        
        Args:
            records: 簡化的互動數據記錄列表
            table_name: 目標表格名稱
        """
        try:
            if not records:
                logger.info(f"沒有數據需要保存到 {table_name}")
                return
            
            # 將記錄轉換為表格數據 (按照新的11個欄位順序)
            rows_to_append = []
            
            for record in records:
                row_data = [
                    record.article_id,           # Article ID
                    record.member_id,            # Member ID
                    record.nickname,             # 暱稱
                    record.title,                # 標題
                    record.content,              # 生成內文
                    record.topic_id,             # Topic ID
                    record.is_trending_topic,    # 是否為熱門話題
                    record.post_time,            # 發文時間
                    record.last_update_time,     # 最後更新時間
                    str(record.likes_count),     # 按讚數
                    str(record.comments_count)   # 留言數
                ]
                
                rows_to_append.append(row_data)
            
            # 寫入 Google Sheets
            try:
                self.sheets_client.append_sheet(table_name, rows_to_append)
                logger.info(f"成功保存 {len(records)} 筆簡化互動數據到 {table_name}")
            except Exception as e:
                logger.warning(f"保存到 {table_name} 失敗，可能表格不存在: {e}")
                # 顯示數據內容供手動創建表格參考
                logger.info(f"準備保存的數據範例:")
                if rows_to_append:
                    sample_row = rows_to_append[0]
                    headers = ['Article ID', 'Member ID', '暱稱', '標題', '生成內文', 'Topic ID', 
                              '是否為熱門話題', '發文時間', '最後更新時間', '按讚數', '留言數']
                    for i, (header, value) in enumerate(zip(headers, sample_row)):
                        display_value = value[:50] + '...' if len(str(value)) > 50 else value
                        logger.info(f"  {header}: {display_value}")
            
        except Exception as e:
            logger.error(f"保存簡化互動數據到 {table_name} 失敗: {e}")
            raise
    
    async def collect_hourly_interactions(self):
        """收集1小時後的互動數據"""
        logger.info("開始收集1小時後的簡化互動數據")
        
        try:
            # 獲取1小時前發布的貼文 (從貼文記錄表查詢)
            published_posts = await self.get_published_posts_for_collection('1h')
            
            if not published_posts:
                logger.info("沒有1小時前發布的貼文需要收集互動數據")
                return
            
            # 收集互動數據
            interaction_records = []
            
            for post_id in published_posts:
                record = await self.collect_interaction_data_for_post(post_id, '1h')
                if record:
                    interaction_records.append(record)
                    
                # 避免 API 調用過於頻繁
                await asyncio.sleep(1)
            
            # 保存到 Google Sheets
            await self.save_simplified_interaction_data(interaction_records, '互動回饋_1hr')
            
            logger.info(f"1小時後簡化互動數據收集完成，處理了 {len(interaction_records)} 筆記錄")
            
        except Exception as e:
            logger.error(f"收集1小時後簡化互動數據失敗: {e}")
            raise
    
    async def collect_daily_interactions(self):
        """收集1日後的互動數據"""
        logger.info("開始收集1日後的簡化互動數據")
        
        try:
            published_posts = await self.get_published_posts_for_collection('1d')
            
            if not published_posts:
                logger.info("沒有1日前發布的貼文需要收集互動數據")
                return
            
            interaction_records = []
            
            for post_id in published_posts:
                record = await self.collect_interaction_data_for_post(post_id, '1d')
                if record:
                    interaction_records.append(record)
                    
                await asyncio.sleep(1)
            
            await self.save_simplified_interaction_data(interaction_records, '互動回饋_1day')
            
            logger.info(f"1日後簡化互動數據收集完成，處理了 {len(interaction_records)} 筆記錄")
            
        except Exception as e:
            logger.error(f"收集1日後簡化互動數據失敗: {e}")
            raise
    
    async def collect_weekly_interactions(self):
        """收集7日後的互動數據"""
        logger.info("開始收集7日後的簡化互動數據")
        
        try:
            published_posts = await self.get_published_posts_for_collection('7d')
            
            if not published_posts:
                logger.info("沒有7日前發布的貼文需要收集互動數據")
                return
            
            interaction_records = []
            
            for post_id in published_posts:
                record = await self.collect_interaction_data_for_post(post_id, '7d')
                if record:
                    interaction_records.append(record)
                    
                await asyncio.sleep(1)
            
            await self.save_simplified_interaction_data(interaction_records, '互動回饋_7days')
            
            logger.info(f"7日後簡化互動數據收集完成，處理了 {len(interaction_records)} 筆記錄")
            
        except Exception as e:
            logger.error(f"收集7日後簡化互動數據失敗: {e}")
            raise
    
    async def get_published_posts_for_collection(self, collection_type: str) -> List[str]:
        """
        獲取需要收集互動數據的已發布貼文
        
        Args:
            collection_type: 收集類型 ('1h', '1d', '7d')
            
        Returns:
            需要收集的貼文ID列表
        """
        try:
            # 計算目標時間範圍
            current_time = datetime.now()
            
            time_deltas = {
                '1h': timedelta(hours=1),
                '1d': timedelta(days=1),
                '7d': timedelta(days=7)
            }
            
            tolerances = {
                '1h': timedelta(minutes=5),
                '1d': timedelta(minutes=10),
                '7d': timedelta(minutes=30)
            }
            
            target_delta = time_deltas.get(collection_type)
            tolerance = tolerances.get(collection_type)
            
            if not target_delta or not tolerance:
                logger.error(f"無效的收集類型: {collection_type}")
                return []
            
            # 讀取貼文記錄表
            post_data = self.sheets_client.read_sheet('貼文記錄表', 'A:W')
            headers = post_data[0] if post_data else []
            rows = post_data[1:] if len(post_data) > 1 else []
            
            posts_to_collect = []
            
            for row in rows:
                # 檢查是否為已發布的貼文
                if len(row) > 11 and row[11] == 'published':
                    
                    # 檢查是否有發文時間戳記
                    post_timestamp = row[13] if len(row) > 13 else ''
                    platform_post_id = row[15] if len(row) > 15 else ''
                    
                    if not post_timestamp or not platform_post_id:
                        continue
                    
                    try:
                        post_time = datetime.fromisoformat(post_timestamp.replace('Z', '+00:00'))
                        target_time = post_time + target_delta
                        time_diff = abs(current_time - target_time)
                        
                        # 檢查是否在收集時間範圍內
                        if time_diff <= tolerance:
                            
                            # 檢查收集狀態 (避免重複收集)
                            status_columns = {
                                '1h': 17,  # R欄 - 1小時後收集狀態
                                '1d': 18,  # S欄 - 1日後收集狀態
                                '7d': 19   # T欄 - 7日後收集狀態
                            }
                            
                            status_col_idx = status_columns.get(collection_type)
                            if status_col_idx and len(row) > status_col_idx:
                                current_status = row[status_col_idx] if row[status_col_idx] else 'pending'
                                
                                if current_status == 'pending':
                                    posts_to_collect.append(row[0])  # 貼文ID
                                    logger.info(f"發現需要收集的貼文: {row[0]} - {collection_type}")
                        
                    except ValueError:
                        logger.warning(f"無法解析發文時間: {post_timestamp}")
                        continue
            
            logger.info(f"找到 {len(posts_to_collect)} 個需要收集 {collection_type} 互動數據的貼文")
            return posts_to_collect
            
        except Exception as e:
            logger.error(f"獲取需要收集的貼文失敗: {e}")
            return []

# 工廠函數
def create_simplified_interaction_collector() -> SimplifiedInteractionCollector:
    """創建簡化的互動數據收集器實例"""
    return SimplifiedInteractionCollector()
