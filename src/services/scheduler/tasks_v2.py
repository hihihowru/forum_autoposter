"""
Celery 任務定義 V2
基於發文時間的動態互動數據收集任務
"""

import sys
import os
import logging
import asyncio
from celery import current_task
from datetime import datetime, timedelta

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.scheduler.celery_app_v2 import app
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
def check_and_collect_interactions(self):
    """
    主要任務：檢查所有已發布貼文，根據發文時間判斷是否需要收集互動數據
    """
    try:
        logger.info("開始檢查基於發文時間的互動數據收集")
        
        sheets_client, _ = get_clients()
        current_time = datetime.now()
        
        # 讀取所有貼文記錄 (包含新增的收集狀態欄位)
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:W')  # 擴展到W欄包含新增欄位
        headers = post_data[0] if post_data else []
        rows = post_data[1:] if len(post_data) > 1 else []
        
        if not headers:
            logger.warning("無法讀取貼文記錄表表頭")
            return {"status": "error", "message": "無法讀取表頭"}
        
        logger.info(f"讀取到 {len(rows)} 筆貼文記錄")
        
        # 找到相關欄位的索引
        column_indices = {}
        required_columns = [
            '貼文ID', '發文狀態', '發文時間戳記', '平台發文ID',
            '1小時後收集狀態', '1日後收集狀態', '7日後收集狀態'
        ]
        
        for col in required_columns:
            try:
                column_indices[col] = headers.index(col)
            except ValueError:
                logger.warning(f"欄位 '{col}' 不存在於表頭中")
                column_indices[col] = -1
        
        # 收集需要處理的任務
        collection_tasks = []
        
        for i, row in enumerate(rows):
            if len(row) <= max(column_indices.values()):
                continue  # 跳過不完整的行
            
            # 檢查是否為已發布的貼文
            status_idx = column_indices.get('發文狀態', -1)
            if status_idx == -1 or len(row) <= status_idx or row[status_idx] != 'published':
                continue
            
            # 獲取發文時間
            timestamp_idx = column_indices.get('發文時間戳記', -1)
            if timestamp_idx == -1 or len(row) <= timestamp_idx or not row[timestamp_idx]:
                continue
            
            try:
                post_time = datetime.fromisoformat(row[timestamp_idx].replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"無法解析發文時間: {row[timestamp_idx]}")
                continue
            
            # 獲取貼文基本資訊
            post_id_idx = column_indices.get('貼文ID', -1)
            platform_id_idx = column_indices.get('平台發文ID', -1)
            
            post_id = row[post_id_idx] if post_id_idx != -1 and len(row) > post_id_idx else ''
            platform_post_id = row[platform_id_idx] if platform_id_idx != -1 and len(row) > platform_id_idx else ''
            
            if not post_id or not platform_post_id:
                continue  # 跳過沒有ID的貼文
            
            # 檢查各個時間點的收集需求
            time_checks = [
                {
                    'type': '1h',
                    'delta': timedelta(hours=1),
                    'status_col': '1小時後收集狀態',
                    'tolerance': timedelta(minutes=5)
                },
                {
                    'type': '1d', 
                    'delta': timedelta(days=1),
                    'status_col': '1日後收集狀態',
                    'tolerance': timedelta(minutes=10)
                },
                {
                    'type': '7d',
                    'delta': timedelta(days=7),
                    'status_col': '7日後收集狀態',
                    'tolerance': timedelta(minutes=30)
                }
            ]
            
            for check in time_checks:
                # 計算應該收集的時間
                target_time = post_time + check['delta']
                time_diff = abs(current_time - target_time)
                
                # 檢查是否在容錯範圍內且還未收集
                if time_diff <= check['tolerance']:
                    status_idx = column_indices.get(check['status_col'], -1)
                    if status_idx != -1 and len(row) > status_idx:
                        current_status = row[status_idx] if row[status_idx] else 'pending'
                        
                        if current_status == 'pending':
                            collection_tasks.append({
                                'post_id': post_id,
                                'platform_post_id': platform_post_id,
                                'collection_type': check['type'],
                                'row_index': i + 2,  # Google Sheets 行號 (1-based + header)
                                'post_time': post_time,
                                'target_time': target_time
                            })
                            
                            logger.info(f"發現需要收集的任務: {post_id} - {check['type']} (目標時間: {target_time})")
        
        # 執行收集任務
        logger.info(f"準備執行 {len(collection_tasks)} 個收集任務")
        
        for task in collection_tasks:
            try:
                # 觸發具體的收集任務
                collect_specific_interaction.delay(
                    post_id=task['post_id'],
                    platform_post_id=task['platform_post_id'],
                    collection_type=task['collection_type'],
                    row_index=task['row_index']
                )
                
                logger.info(f"已觸發收集任務: {task['post_id']} - {task['collection_type']}")
                
            except Exception as e:
                logger.error(f"觸發收集任務失敗: {task['post_id']} - {e}")
        
        result_msg = f"檢查完成，觸發了 {len(collection_tasks)} 個收集任務"
        logger.info(result_msg)
        
        return {
            "status": "success", 
            "message": result_msg,
            "tasks_triggered": len(collection_tasks)
        }
        
    except Exception as e:
        logger.error(f"check_and_collect_interactions 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 check_and_collect_interactions，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=300 * (self.request.retries + 1))  # 5分鐘、10分鐘、15分鐘後重試
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def collect_specific_interaction(self, post_id, platform_post_id, collection_type, row_index):
    """
    收集特定貼文在特定時間點的互動數據
    
    Args:
        post_id: 貼文ID
        platform_post_id: 平台貼文ID 
        collection_type: 收集類型 ('1h', '1d', '7d')
        row_index: 在 Google Sheets 中的行號
    """
    try:
        logger.info(f"開始收集互動數據: {post_id} - {collection_type}")
        
        sheets_client, cmoney_client = get_clients()
        current_time = datetime.now()
        
        # 更新收集狀態為 'collecting'
        status_column_map = {
            '1h': 'R',   # 1小時後收集狀態
            '1d': 'S',   # 1日後收集狀態  
            '7d': 'T'    # 7日後收集狀態
        }
        
        time_column_map = {
            '1h': 'U',   # 1小時後收集時間
            '1d': 'V',   # 1日後收集時間
            '7d': 'W'    # 7日後收集時間
        }
        
        status_col = status_column_map.get(collection_type)
        time_col = time_column_map.get(collection_type)
        
        if not status_col or not time_col:
            raise ValueError(f"無效的收集類型: {collection_type}")
        
        # 更新狀態為 'collecting'
        status_range = f'{status_col}{row_index}'
        sheets_client.write_sheet('貼文記錄表', [['collecting']], status_range)
        
        # 收集互動數據
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 使用川川哥的憑證 (實際應該根據 KOL ID 動態選擇)
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password='N9t1kY3x'
            )
            
            token = loop.run_until_complete(cmoney_client.login(credentials))
            interaction_data = loop.run_until_complete(
                cmoney_client.get_article_interactions(token.token, platform_post_id)
            )
            
            if interaction_data and hasattr(interaction_data, 'likes'):
                # 收集成功，準備數據
                collection_time = current_time.isoformat()
                
                # 計算表情數據
                emoji_total = 0
                emoji_details = "{}"
                
                if hasattr(interaction_data, 'raw_data') and interaction_data.raw_data:
                    emoji_count = interaction_data.raw_data.get('emojiCount', {})
                    if isinstance(emoji_count, dict):
                        emoji_total = sum(emoji_count.values())
                        import json
                        emoji_details = json.dumps(emoji_count, ensure_ascii=False)
                
                # 計算總互動數
                total_interactions = (interaction_data.likes + 
                                    interaction_data.comments + 
                                    interaction_data.shares + 
                                    emoji_total)
                
                # 準備要寫入互動數據表的數據
                table_name_map = {
                    '1h': '互動回饋_1hr',
                    '1d': '互動回饋_1day', 
                    '7d': '互動回饋_7days'
                }
                
                target_table = table_name_map.get(collection_type)
                
                if target_table:
                    # 讀取原始貼文資料
                    original_data = sheets_client.read_sheet('貼文記錄表', f'A{row_index}:Q{row_index}')
                    if original_data and len(original_data[0]) >= 17:
                        base_row = original_data[0]
                        
                        # 組合完整的互動數據記錄
                        interaction_record = base_row + [
                            collection_time,                     # 數據收集時間
                            collection_type.replace('h', '小時後').replace('d', '日後'),  # 發文經過時間
                            str(interaction_data.likes),         # 讚數
                            str(interaction_data.comments),      # 留言數
                            str(interaction_data.shares),        # 收藏數
                            str(emoji_total),                    # 表情符號總數
                            emoji_details,                       # 表情符號明細
                            str(total_interactions),            # 總互動數
                            "0.0",                              # 互動成長率 (暫時)
                            "0.0",                              # 每小時平均互動 (暫時)
                            "0.0",                              # 互動率 (暫時)
                            "success",                          # API呼叫狀態
                            "",                                 # 錯誤訊息
                            json.dumps(interaction_data.raw_data, ensure_ascii=False) if hasattr(interaction_data, 'raw_data') else "{}"  # 原始API回應
                        ]
                        
                        # 寫入互動數據表
                        try:
                            sheets_client.append_sheet(target_table, [interaction_record])
                            logger.info(f"成功寫入互動數據到 {target_table}")
                        except Exception as e:
                            logger.warning(f"寫入 {target_table} 失敗，可能表格不存在: {e}")
                
                # 更新貼文記錄表的收集狀態和時間
                status_time_range = f'{status_col}{row_index}:{time_col}{row_index}'
                sheets_client.write_sheet('貼文記錄表', [['collected', collection_time]], status_time_range)
                
                logger.info(f"互動數據收集完成: {post_id} - {collection_type} (讚={interaction_data.likes}, 留言={interaction_data.comments}, 收藏={interaction_data.shares})")
                
                return {
                    "status": "success",
                    "message": f"成功收集 {collection_type} 互動數據",
                    "data": {
                        "likes": interaction_data.likes,
                        "comments": interaction_data.comments,
                        "shares": interaction_data.shares,
                        "total": total_interactions
                    }
                }
                
            else:
                raise Exception("API 回應異常或無數據")
                
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"收集互動數據失敗: {post_id} - {collection_type} - {e}")
        
        # 更新狀態為 'failed'
        try:
            sheets_client, _ = get_clients()
            status_col = status_column_map.get(collection_type)
            if status_col:
                status_range = f'{status_col}{row_index}'
                sheets_client.write_sheet('貼文記錄表', [['failed']], status_range)
        except:
            pass
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試收集任務，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=180 * (self.request.retries + 1))
        
        return {"status": "error", "message": str(e)}

@app.task(bind=True, max_retries=3)
def generate_content_for_ready_tasks(self):
    """為 ready_to_gen 狀態的任務生成內容"""
    try:
        # 使用 asyncio 運行異步函數
        import asyncio
        return asyncio.run(_generate_content_for_ready_tasks_async())
    except Exception as e:
        logger.error(f"generate_content_for_ready_tasks 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 generate_content_for_ready_tasks，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=120 * (self.request.retries + 1))
        
        return {"status": "error", "message": str(e)}

# 其他現有任務保持不變
async def _generate_content_for_ready_tasks_async():
    """異步版本的內容生成任務"""
    try:
        logger.info("開始執行 generate_content_for_ready_tasks 任務")
        
        sheets_client, _ = get_clients()
        content_generator = create_content_generator()
        
        # 讀取待生成內容的任務
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Y')
        headers = post_data[0]
        rows = post_data[1:]
        
        processed_count = 0
        
        for i, row in enumerate(rows):
            if len(row) > 11 and row[11] == 'ready_to_gen':  # 發文狀態
                try:
                    # 獲取股票資訊 (第19欄，索引18)
                    stock_info = row[18] if len(row) > 18 else ''
                    market_data = {}
                    
                    if stock_info:
                        # 解析股票資訊格式: "台積電(2330)"
                        if '(' in stock_info and ')' in stock_info:
                            stock_name = stock_info.split('(')[0]
                            stock_id = stock_info.split('(')[1].split(')')[0]
                            market_data = {
                                'stock_id': stock_id,
                                'stock_name': stock_name,
                                'has_stock': True
                            }
                            logger.info(f"任務 {row[0]} 有股票資訊: {stock_name}({stock_id})")
                            
                            # 如果有股票資訊，獲取個股數據
                            try:
                                from services.stock.stock_data_service import create_stock_data_service
                                stock_data_service = create_stock_data_service()
                                stock_data = await stock_data_service.get_comprehensive_stock_data(stock_id)
                                market_data['stock_data'] = stock_data
                                logger.info(f"任務 {row[0]} 獲取個股數據成功: {stock_data['has_ohlc']} OHLC, {stock_data['has_analysis']} 分析, {stock_data['has_financial']} 財務")
                            except Exception as e:
                                logger.warning(f"任務 {row[0]} 獲取個股數據失敗: {e}")
                                market_data['stock_data'] = None
                        else:
                            market_data = {'has_stock': False}
                    else:
                        market_data = {'has_stock': False}
                        logger.info(f"任務 {row[0]} 沒有股票資訊")
                    
                    # 創建內容生成請求
                    request = ContentRequest(
                        topic_title=row[8] if len(row) > 8 else '',
                        topic_keywords=row[9] if len(row) > 9 else '',
                        kol_persona=row[4] if len(row) > 4 else '',
                        kol_nickname=row[2] if len(row) > 2 else '',
                        content_type=row[5] if len(row) > 5 else '',
                        market_data=market_data
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
    """發布 ready_to_post 狀態的貼文，並設置收集狀態為 pending"""
    try:
        logger.info("開始執行 publish_ready_posts 任務")
        
        sheets_client, cmoney_client = get_clients()
        
        # 讀取待發布的任務
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:W')
        headers = post_data[0]
        rows = post_data[1:]
        
        published_count = 0
        
        for i, row in enumerate(rows):
            if len(row) > 11 and row[11] == 'ready_to_post':  # 發文狀態
                try:
                    # 暫時跳過實際發文，只更新狀態
                    logger.info(f"模擬發布任務 {row[0]} (實際發文功能待實作)")
                    
                    # 更新狀態和收集狀態
                    row_index = i + 2
                    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
                    
                    # 更新發文狀態 (L欄)、發文時間戳記 (N欄) 和三個收集狀態 (R, S, T欄)
                    status_range = f'L{row_index}:T{row_index}'
                    update_values = [[
                        'published',        # 發文狀態
                        '',                # 上次排程時間 (M欄)
                        current_time,      # 發文時間戳記 (N欄)
                        '',                # 最近錯誤訊息 (O欄)
                        '',                # 平台發文ID (P欄) - 實際發文時會填入
                        '',                # 平台發文URL (Q欄) - 實際發文時會填入
                        'pending',         # 1小時後收集狀態 (R欄)
                        'pending',         # 1日後收集狀態 (S欄)
                        'pending'          # 7日後收集狀態 (T欄)
                    ]]
                    
                    sheets_client.write_sheet('貼文記錄表', update_values, status_range)
                    
                    published_count += 1
                    logger.info(f"任務 {row[0]} 狀態已更新為 published，收集狀態設為 pending")
                    
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
    """獲取熱門話題並分配給 KOL，整合股票查詢功能"""
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
            
            # 使用新的話題處理器處理話題（包含股票查詢）
            if topics:
                from services.assign.topic_processor import create_topic_processor
                
                # 創建話題處理器
                topic_processor = create_topic_processor(sheets_client)
                
                # 轉換話題格式
                topic_data_list = []
                for topic in topics:
                    topic_data_list.append({
                        'id': topic.id,
                        'title': topic.title,
                        'content': topic.name  # 使用 name 作為內容
                    })
                
                # 處理話題（包含股票查詢和分配）
                processed_topics = loop.run_until_complete(topic_processor.process_topics(topic_data_list))
                
                logger.info(f"成功處理 {len(processed_topics)} 個話題，包含股票查詢和分配")
                
                # 統計股票分配情況
                total_assignments = 0
                stock_assignments = 0
                for processed_topic in processed_topics:
                    total_assignments += len(processed_topic.assignments)
                    if processed_topic.stock_assignments:
                        stock_assignments += sum(1 for stock in processed_topic.stock_assignments.values() if stock is not None)
                
                logger.info(f"總分配任務: {total_assignments}, 股票相關任務: {stock_assignments}")
                
                return {
                    "status": "success",
                    "message": f"成功處理 {len(processed_topics)} 個話題",
                    "total_assignments": total_assignments,
                    "stock_assignments": stock_assignments,
                    "processed_topics": len(processed_topics)
                }
            else:
                logger.info("沒有獲取到熱門話題")
                return {
                    "status": "success",
                    "message": "沒有獲取到熱門話題",
                    "total_assignments": 0,
                    "stock_assignments": 0,
                    "processed_topics": 0
                }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"fetch_and_assign_topics 任務失敗: {e}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"重試 fetch_and_assign_topics，第 {self.request.retries + 1} 次")
            raise self.retry(countdown=300 * (self.request.retries + 1))
        
        return {"status": "error", "message": str(e)}

# 測試任務
@app.task
def test_task():
    """測試任務"""
    logger.info("執行測試任務")
    return {"status": "success", "message": "測試任務執行成功", "timestamp": datetime.now().isoformat()}
