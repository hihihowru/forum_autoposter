"""
互動數據收集服務
定時收集 CMoney 平台的貼文互動數據
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class InteractionRecord:
    """互動數據記錄"""
    # 基礎貼文資訊 (從貼文記錄表複製)
    task_id: str
    kol_serial: str
    kol_nickname: str
    kol_id: str
    persona: str
    content_type: str
    topic_index: str
    topic_id: str
    topic_title: str
    topic_keywords: str
    generated_content: str
    post_status: str
    last_scheduled: str
    post_timestamp: str
    error_message: str
    platform_post_id: str
    platform_post_url: str
    
    # 互動數據欄位 (新增)
    collection_time: str = ""        # 收集時間
    interested_count: int = 0        # 讚數
    comment_count: int = 0           # 留言數
    collected_count: int = 0         # 收藏數
    emoji_total: int = 0             # 表情總數
    total_interactions: int = 0      # 總互動數
    growth_rate: float = 0.0         # 互動成長率
    hourly_avg_interactions: float = 0.0  # 每小時平均互動
    emoji_details: str = ""          # 表情明細 (JSON)
    data_source: str = "CMoney_API"  # 數據來源
    collection_error: str = ""       # 收集錯誤訊息

class InteractionCollector:
    """互動數據收集器"""
    
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
        
        logger.info("互動數據收集器初始化完成")
    
    async def get_published_posts(self, hours_ago: int = 1) -> List[Dict[str, str]]:
        """
        獲取指定時間前發布的貼文
        
        Args:
            hours_ago: 幾小時前發布的貼文
            
        Returns:
            符合條件的貼文列表
        """
        try:
            # 讀取貼文記錄表
            post_data = self.sheets_client.read_sheet('貼文記錄表', 'A:Q')
            headers = post_data[0]
            rows = post_data[1:]
            
            published_posts = []
            target_time = datetime.now() - timedelta(hours=hours_ago)
            
            for row in rows:
                if len(row) > 11 and row[11] == 'published':  # 發文狀態 = published
                    # 檢查發文時間
                    if len(row) > 13 and row[13]:  # 發文時間戳記
                        try:
                            post_time = datetime.fromisoformat(row[13].replace('Z', '+00:00'))
                            
                            # 如果是指定時間前發布的貼文
                            time_diff = abs((post_time - target_time).total_seconds())
                            if time_diff <= 3600:  # 允許1小時誤差
                                post_record = {
                                    'task_id': row[0] if len(row) > 0 else '',
                                    'kol_serial': row[1] if len(row) > 1 else '',
                                    'kol_nickname': row[2] if len(row) > 2 else '',
                                    'kol_id': row[3] if len(row) > 3 else '',
                                    'platform_post_id': row[15] if len(row) > 15 else '',
                                    'post_timestamp': row[13] if len(row) > 13 else '',
                                    'full_row': row
                                }
                                
                                if post_record['platform_post_id']:
                                    published_posts.append(post_record)
                                    
                        except ValueError as e:
                            logger.warning(f"無法解析發文時間: {row[13]}, 錯誤: {e}")
                            continue
            
            logger.info(f"找到 {len(published_posts)} 個 {hours_ago} 小時前發布的貼文")
            return published_posts
            
        except Exception as e:
            logger.error(f"獲取已發布貼文失敗: {e}")
            return []
    
    async def collect_interaction_data(self, post_record: Dict[str, str]) -> Optional[InteractionRecord]:
        """
        收集單個貼文的互動數據
        
        Args:
            post_record: 貼文記錄
            
        Returns:
            互動數據記錄
        """
        try:
            platform_post_id = post_record['platform_post_id']
            kol_id = post_record['kol_id']
            
            if not platform_post_id:
                logger.warning(f"貼文 {post_record['task_id']} 缺少平台貼文ID")
                return None
            
            # 使用 KOL 的登入憑證獲取 token
            from clients.cmoney.cmoney_client import LoginCredentials
            
            # 這裡需要根據 KOL ID 獲取對應的登入憑證
            # 暫時使用川川哥的憑證做測試
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
            
            # 計算額外指標
            collection_time = datetime.now().isoformat()
            
            # 解析表情數據
            emoji_details = {}
            if hasattr(interaction_data, 'raw_data') and interaction_data.raw_data:
                emoji_count = interaction_data.raw_data.get('emojiCount', {})
                if isinstance(emoji_count, dict):
                    emoji_details = emoji_count
            
            emoji_total = sum(emoji_details.values()) if emoji_details else 0
            total_interactions = (interaction_data.likes + 
                                interaction_data.comments + 
                                interaction_data.shares + 
                                emoji_total)
            
            # 計算每小時平均互動 (基於發文時間)
            try:
                post_time = datetime.fromisoformat(post_record['post_timestamp'].replace('Z', '+00:00'))
                hours_since_post = (datetime.now() - post_time).total_seconds() / 3600
                hourly_avg = total_interactions / max(hours_since_post, 0.1)
            except:
                hourly_avg = 0.0
            
            # 創建互動記錄
            full_row = post_record['full_row']
            
            interaction_record = InteractionRecord(
                # 基礎資訊 (從原始記錄複製)
                task_id=full_row[0] if len(full_row) > 0 else '',
                kol_serial=full_row[1] if len(full_row) > 1 else '',
                kol_nickname=full_row[2] if len(full_row) > 2 else '',
                kol_id=full_row[3] if len(full_row) > 3 else '',
                persona=full_row[4] if len(full_row) > 4 else '',
                content_type=full_row[5] if len(full_row) > 5 else '',
                topic_index=full_row[6] if len(full_row) > 6 else '',
                topic_id=full_row[7] if len(full_row) > 7 else '',
                topic_title=full_row[8] if len(full_row) > 8 else '',
                topic_keywords=full_row[9] if len(full_row) > 9 else '',
                generated_content=full_row[10] if len(full_row) > 10 else '',
                post_status=full_row[11] if len(full_row) > 11 else '',
                last_scheduled=full_row[12] if len(full_row) > 12 else '',
                post_timestamp=full_row[13] if len(full_row) > 13 else '',
                error_message=full_row[14] if len(full_row) > 14 else '',
                platform_post_id=full_row[15] if len(full_row) > 15 else '',
                platform_post_url=full_row[16] if len(full_row) > 16 else '',
                
                # 互動數據
                collection_time=collection_time,
                interested_count=interaction_data.likes,
                comment_count=interaction_data.comments,
                collected_count=interaction_data.shares,
                emoji_total=emoji_total,
                total_interactions=total_interactions,
                growth_rate=0.0,  # 需要與之前的數據比較
                hourly_avg_interactions=hourly_avg,
                emoji_details=json.dumps(emoji_details, ensure_ascii=False),
                data_source="CMoney_API",
                collection_error=""
            )
            
            logger.info(f"成功收集貼文 {platform_post_id} 的互動數據: 讚={interaction_data.likes}, 留言={interaction_data.comments}, 收藏={interaction_data.shares}")
            
            return interaction_record
            
        except Exception as e:
            logger.error(f"收集貼文 {post_record.get('task_id', 'unknown')} 互動數據失敗: {e}")
            
            # 返回錯誤記錄
            full_row = post_record.get('full_row', [])
            error_record = InteractionRecord(
                task_id=full_row[0] if len(full_row) > 0 else post_record.get('task_id', ''),
                kol_serial=full_row[1] if len(full_row) > 1 else post_record.get('kol_serial', ''),
                kol_nickname=full_row[2] if len(full_row) > 2 else post_record.get('kol_nickname', ''),
                kol_id=full_row[3] if len(full_row) > 3 else post_record.get('kol_id', ''),
                persona=full_row[4] if len(full_row) > 4 else '',
                content_type=full_row[5] if len(full_row) > 5 else '',
                topic_index=full_row[6] if len(full_row) > 6 else '',
                topic_id=full_row[7] if len(full_row) > 7 else '',
                topic_title=full_row[8] if len(full_row) > 8 else '',
                topic_keywords=full_row[9] if len(full_row) > 9 else '',
                generated_content=full_row[10] if len(full_row) > 10 else '',
                post_status=full_row[11] if len(full_row) > 11 else '',
                last_scheduled=full_row[12] if len(full_row) > 12 else '',
                post_timestamp=full_row[13] if len(full_row) > 13 else '',
                error_message=full_row[14] if len(full_row) > 14 else '',
                platform_post_id=full_row[15] if len(full_row) > 15 else '',
                platform_post_url=full_row[16] if len(full_row) > 16 else '',
                collection_time=datetime.now().isoformat(),
                collection_error=str(e)
            )
            
            return error_record
    
    async def save_interaction_data(self, records: List[InteractionRecord], table_name: str):
        """
        保存互動數據到 Google Sheets
        
        Args:
            records: 互動數據記錄列表
            table_name: 目標表格名稱
        """
        try:
            if not records:
                logger.info(f"沒有數據需要保存到 {table_name}")
                return
            
            # 將記錄轉換為表格數據
            rows_to_append = []
            
            for record in records:
                # 轉換為列表格式 (按照 28 個欄位的順序)
                row_data = [
                    record.task_id,
                    record.kol_serial,
                    record.kol_nickname,
                    record.kol_id,
                    record.persona,
                    record.content_type,
                    record.topic_index,
                    record.topic_id,
                    record.topic_title,
                    record.topic_keywords,
                    record.generated_content,
                    record.post_status,
                    record.last_scheduled,
                    record.post_timestamp,
                    record.error_message,
                    record.platform_post_id,
                    record.platform_post_url,
                    record.collection_time,
                    str(record.interested_count),
                    str(record.comment_count),
                    str(record.collected_count),
                    str(record.emoji_total),
                    str(record.total_interactions),
                    str(record.growth_rate),
                    str(record.hourly_avg_interactions),
                    record.emoji_details,
                    record.data_source,
                    record.collection_error
                ]
                
                rows_to_append.append(row_data)
            
            # 寫入 Google Sheets
            self.sheets_client.append_sheet(table_name, rows_to_append)
            
            logger.info(f"成功保存 {len(records)} 筆互動數據到 {table_name}")
            
        except Exception as e:
            logger.error(f"保存互動數據到 {table_name} 失敗: {e}")
            raise
    
    async def collect_hourly_interactions(self):
        """收集1小時後的互動數據"""
        logger.info("開始收集1小時後的互動數據")
        
        try:
            # 獲取1小時前發布的貼文
            published_posts = await self.get_published_posts(hours_ago=1)
            
            if not published_posts:
                logger.info("沒有1小時前發布的貼文需要收集互動數據")
                return
            
            # 收集互動數據
            interaction_records = []
            
            for post in published_posts:
                record = await self.collect_interaction_data(post)
                if record:
                    interaction_records.append(record)
                    
                # 避免 API 調用過於頻繁
                await asyncio.sleep(1)
            
            # 保存到 Google Sheets
            await self.save_interaction_data(interaction_records, '互動回饋_1hr')
            
            logger.info(f"1小時後互動數據收集完成，處理了 {len(interaction_records)} 筆記錄")
            
        except Exception as e:
            logger.error(f"收集1小時後互動數據失敗: {e}")
            raise
    
    async def collect_daily_interactions(self):
        """收集1日後的互動數據"""
        logger.info("開始收集1日後的互動數據")
        
        try:
            published_posts = await self.get_published_posts(hours_ago=24)
            
            if not published_posts:
                logger.info("沒有1日前發布的貼文需要收集互動數據")
                return
            
            interaction_records = []
            
            for post in published_posts:
                record = await self.collect_interaction_data(post)
                if record:
                    # 計算成長率 (與1小時後的數據比較)
                    try:
                        hourly_data = self.get_previous_interaction_data(record.task_id, '互動回饋_1hr')
                        if hourly_data:
                            previous_total = hourly_data.get('total_interactions', 0)
                            if previous_total > 0:
                                record.growth_rate = ((record.total_interactions - previous_total) / previous_total) * 100
                    except:
                        pass
                        
                    interaction_records.append(record)
                    
                await asyncio.sleep(1)
            
            await self.save_interaction_data(interaction_records, '互動回饋_1day')
            
            logger.info(f"1日後互動數據收集完成，處理了 {len(interaction_records)} 筆記錄")
            
        except Exception as e:
            logger.error(f"收集1日後互動數據失敗: {e}")
            raise
    
    async def collect_weekly_interactions(self):
        """收集1週後的互動數據"""
        logger.info("開始收集1週後的互動數據")
        
        try:
            published_posts = await self.get_published_posts(hours_ago=168)  # 7 * 24 = 168 hours
            
            if not published_posts:
                logger.info("沒有1週前發布的貼文需要收集互動數據")
                return
            
            interaction_records = []
            
            for post in published_posts:
                record = await self.collect_interaction_data(post)
                if record:
                    # 計算成長率 (與1日後的數據比較)
                    try:
                        daily_data = self.get_previous_interaction_data(record.task_id, '互動回饋_1day')
                        if daily_data:
                            previous_total = daily_data.get('total_interactions', 0)
                            if previous_total > 0:
                                record.growth_rate = ((record.total_interactions - previous_total) / previous_total) * 100
                    except:
                        pass
                        
                    interaction_records.append(record)
                    
                await asyncio.sleep(1)
            
            await self.save_interaction_data(interaction_records, '互動回饋_7days')
            
            logger.info(f"1週後互動數據收集完成，處理了 {len(interaction_records)} 筆記錄")
            
        except Exception as e:
            logger.error(f"收集1週後互動數據失敗: {e}")
            raise
    
    def get_previous_interaction_data(self, task_id: str, table_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取之前收集的互動數據 (用於計算成長率)
        
        Args:
            task_id: 任務ID
            table_name: 表格名稱
            
        Returns:
            之前的互動數據
        """
        try:
            data = self.sheets_client.read_sheet(table_name, 'A:AB')
            headers = data[0] if data else []
            rows = data[1:] if len(data) > 1 else []
            
            for row in rows:
                if len(row) > 0 and row[0] == task_id:
                    # 返回找到的數據
                    result = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            if header == 'total_interactions':
                                try:
                                    result[header] = int(row[i])
                                except:
                                    result[header] = 0
                            else:
                                result[header] = row[i]
                    return result
            
            return None
            
        except Exception as e:
            logger.warning(f"獲取之前的互動數據失敗: {e}")
            return None

# 工廠函數
def create_interaction_collector() -> InteractionCollector:
    """創建互動數據收集器實例"""
    return InteractionCollector()
