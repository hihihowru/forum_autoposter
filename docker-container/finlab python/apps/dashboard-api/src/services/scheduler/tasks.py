"""
Celery 任務定義
定義所有的定時任務和背景任務
"""

import sys
import os
import logging
import asyncio
from celery import current_task
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.scheduler.celery_app import app
from services.interaction.interaction_collector import create_interaction_collector
from services.content.content_generator import create_content_generator, ContentRequest
from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

# 初始化客戶端 (全域)
sheets_client = None
cmoney_client = None

def get_clients():
    """獲取客戶端實例 (懶載入)"""
    global sheets_client, cmoney_client
    
    if sheets_client is None:
        sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-service-account.json'),
            spreadsheet_id=os.getenv('GOOGLE_SPREADSHEET_ID')
        )
    
    if cmoney_client is None:
        cmoney_client = CMoneyClient()
    
    return sheets_client, cmoney_client

@app.task(bind=True, max_retries=3)
def collect_hourly_interactions(self):
    """收集1小時後的互動數據任務"""
    try:
        logger.info("開始執行 collect_hourly_interactions 任務")
        
        # 創建收集器並執行
        collector = create_interaction_collector()
        
        # 在同步環境中運行異步函數
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(collector.collect_hourly_interactions())
            logger.info("collect_hourly_interactions 任務完成")
            return {"status": "success", "message": "1小時後互動數據收集完成"}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"collect_hourly_interactions 任務失敗: {e}")
        
        # 重試機制
        if self.request.retries < self.max_retries:
            logger.info(f"重試 collect_hourly_interactions，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=60 * (self.request.retries + 1))  # 1分鐘、2分鐘、3分鐘後重試
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def collect_daily_interactions(self):
    """收集1日後的互動數據任務"""
    try:
        logger.info("開始執行 collect_daily_interactions 任務")
        
        collector = create_interaction_collector()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(collector.collect_daily_interactions())
            logger.info("collect_daily_interactions 任務完成")
            return {"status": "success", "message": "1日後互動數據收集完成"}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"collect_daily_interactions 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 collect_daily_interactions，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=300 * (self.request.retries + 1))  # 5分鐘、10分鐘、15分鐘後重試
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def collect_weekly_interactions(self):
    """收集1週後的互動數據任務"""
    try:
        logger.info("開始執行 collect_weekly_interactions 任務")
        
        collector = create_interaction_collector()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(collector.collect_weekly_interactions())
            logger.info("collect_weekly_interactions 任務完成")
            return {"status": "success", "message": "1週後互動數據收集完成"}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"collect_weekly_interactions 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 collect_weekly_interactions，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=600 * (self.request.retries + 1))  # 10分鐘、20分鐘、30分鐘後重試
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def generate_content_for_ready_tasks(self):
    """為 ready_to_gen 狀態的任務生成內容"""
    try:
        logger.info("開始執行 generate_content_for_ready_tasks 任務")
        
        sheets_client, _ = get_clients()
        content_generator = create_content_generator()
        
        # 讀取待生成內容的任務
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Q')
        headers = post_data[0]
        rows = post_data[1:]
        
        processed_count = 0
        
        for i, row in enumerate(rows):
            if len(row) > 11 and row[11] == 'ready_to_gen':  # 發文狀態
                try:
                    # 創建內容生成請求
                    request = ContentRequest(
                        topic_title=row[8] if len(row) > 8 else '',
                        topic_keywords=row[9] if len(row) > 9 else '',
                        kol_persona=row[4] if len(row) > 4 else '',
                        kol_nickname=row[2] if len(row) > 2 else '',
                        content_type=row[5] if len(row) > 5 else ''
                    )
                    
                    # 生成內容
                    generated = content_generator.generate_complete_content(request)
                    
                    if generated.success:
                        # 更新 Google Sheets
                        row_index = i + 2  # Google Sheets 行號 (1-based + header)
                        current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
                        
                        # 更新生成內容 (K欄) 和狀態 (L欄)
                        content_range = f'K{row_index}:L{row_index}'
                        update_values = [[generated.content, 'ready_to_post']]
                        
                        sheets_client.write_sheet('貼文記錄表', update_values, content_range)
                        
                        processed_count += 1
                        logger.info(f"成功為任務 {row[0]} 生成內容")
                    else:
                        logger.error(f"任務 {row[0]} 內容生成失敗: {generated.error_message}")
                        
                except Exception as e:
                    logger.error(f"處理任務 {row[0] if len(row) > 0 else 'unknown'} 時出錯: {e}")
                    continue
        
        logger.info(f"generate_content_for_ready_tasks 任務完成，處理了 {processed_count} 個任務")
        return {"status": "success", "message": f"成功生成 {processed_count} 個任務的內容"}
        
    except Exception as e:
        logger.error(f"generate_content_for_ready_tasks 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 generate_content_for_ready_tasks，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=120 * (self.request.retries + 1))
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def publish_ready_posts(self):
    """發布 ready_to_post 狀態的貼文"""
    try:
        logger.info("開始執行 publish_ready_posts 任務")
        
        sheets_client, cmoney_client = get_clients()
        
        # 讀取待發布的任務
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Q')
        headers = post_data[0]
        rows = post_data[1:]
        
        published_count = 0
        
        for i, row in enumerate(rows):
            if len(row) > 11 and row[11] == 'ready_to_post':  # 發文狀態
                try:
                    # 暫時跳過實際發文，只更新狀態為 published
                    logger.info(f"模擬發布任務 {row[0]} (實際發文功能待實作)")
                    
                    # 更新狀態
                    row_index = i + 2
                    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
                    
                    # 更新發文狀態 (L欄) 和發文時間戳記 (N欄)
                    status_range = f'L{row_index}:N{row_index}'
                    update_values = [['published', current_time, '']]  # 狀態、時間戳記、錯誤訊息
                    
                    sheets_client.write_sheet('貼文記錄表', update_values, status_range)
                    
                    published_count += 1
                    logger.info(f"任務 {row[0]} 狀態已更新為 published")
                    
                except Exception as e:
                    logger.error(f"發布任務 {row[0] if len(row) > 0 else 'unknown'} 時出錯: {e}")
                    
                    # 更新錯誤訊息
                    try:
                        row_index = i + 2
                        error_range = f'O{row_index}'  # 錯誤訊息欄位
                        sheets_client.write_sheet('貼文記錄表', [[str(e)]], error_range)
                    except:
                        pass
                    
                    continue
        
        logger.info(f"publish_ready_posts 任務完成，發布了 {published_count} 個任務")
        return {"status": "success", "message": f"成功發布 {published_count} 個任務"}
        
    except Exception as e:
        logger.error(f"publish_ready_posts 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 publish_ready_posts，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=180 * (self.request.retries + 1))
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def fetch_and_assign_topics(self):
    """獲取熱門話題並分配給 KOL"""
    try:
        logger.info("開始執行 fetch_and_assign_topics 任務")
        
        sheets_client, cmoney_client = get_clients()
        
        # 使用川川哥的憑證獲取熱門話題
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 登入並獲取話題
            token = loop.run_until_complete(cmoney_client.login(credentials))
            topics = loop.run_until_complete(cmoney_client.get_trending_topics(token.token))
            
            logger.info(f"獲取到 {len(topics)} 個熱門話題")
            
            # 簡單的分配邏輯 (實際應該使用更複雜的分配服務)
            # 這裡只是示例，創建一個新任務
            if topics:
                topic = topics[0]
                current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
                task_id = f'{topic.id}::200'  # 分配給川川哥
                
                # 檢查是否已存在
                post_data = sheets_client.read_sheet('貼文記錄表', 'A:A')
                existing_ids = [row[0] for row in post_data[1:] if len(row) > 0]
                
                if task_id not in existing_ids:
                    new_record = [
                        task_id,                    # 貼文ID
                        '200',                     # KOL Serial
                        '川川哥',                   # KOL 暱稱
                        '9505546',                 # KOL ID
                        '技術分析專家',             # Persona
                        'technical,chart',         # Content Type
                        '1',                       # 已派發TopicIndex
                        topic.id,                  # 已派發TopicID
                        topic.title,               # 已派發TopicTitle
                        '技術分析,台股,投資',        # 已派發TopicKeywords
                        '',                        # 生成內容
                        'queued',                  # 發文狀態
                        current_time,              # 上次排程時間
                        '',                        # 發文時間戳記
                        '',                        # 最近錯誤訊息
                        '',                        # 平台發文ID
                        ''                         # 平台發文URL
                    ]
                    
                    sheets_client.append_sheet('貼文記錄表', [new_record])
                    logger.info(f"創建新任務: {task_id}")
                else:
                    logger.info(f"任務 {task_id} 已存在，跳過")
            
            return {"status": "success", "message": f"處理了 {len(topics)} 個熱門話題"}
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"fetch_and_assign_topics 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 fetch_and_assign_topics，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=300 * (self.request.retries + 1))
        
        return {"status": "error", "message": str(e)}

# 手動觸發任務的輔助函數
@app.task
def test_task():
    """測試任務"""
    logger.info("執行測試任務")
    return {"status": "success", "message": "測試任務執行成功", "timestamp": datetime.now().isoformat()}
