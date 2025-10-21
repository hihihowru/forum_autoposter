"""
排程服務 - 整合資料庫持久化
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import pytz

from schedule_database import schedule_db_service
from timezone_utils import get_taiwan_utcnow

logger = logging.getLogger(__name__)

class ScheduleTask:
    """排程任務"""
    def __init__(self, task_id: str, session_id: int, post_ids: List[str], 
                 schedule_type: str, interval_seconds: int = 30, 
                 batch_duration_hours: Optional[int] = None,
                 schedule_name: Optional[str] = None,
                 schedule_description: Optional[str] = None,
                 daily_execution_time: Optional[str] = None,
                 weekdays_only: bool = True,
                 max_posts_per_hour: int = 2,
                 timezone: str = 'Asia/Taipei',
                 generation_config: Optional[Dict[str, Any]] = None,
                 batch_info: Optional[Dict[str, Any]] = None):
        self.task_id = task_id
        self.session_id = session_id
        self.post_ids = post_ids
        self.schedule_type = schedule_type
        self.interval_seconds = interval_seconds
        self.batch_duration_hours = batch_duration_hours
        self.schedule_name = schedule_name
        self.schedule_description = schedule_description
        self.daily_execution_time = daily_execution_time
        self.weekdays_only = weekdays_only
        self.max_posts_per_hour = max_posts_per_hour
        self.timezone = timezone
        self.generation_config = generation_config or {}
        self.batch_info = batch_info or {}
        self.status = 'pending'
        self.created_at = get_taiwan_utcnow()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0

class ScheduleService:
    """排程服務 - 整合資料庫持久化"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduleTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.db_service = schedule_db_service
        self.background_scheduler_running = False
    
    async def create_schedule_task(self, session_id: int, post_ids: List[str],
                                 schedule_type: str, interval_seconds: int = 30,
                                 batch_duration_hours: Optional[int] = None,
                                 schedule_name: Optional[str] = None,
                                 schedule_description: Optional[str] = None,
                                 daily_execution_time: Optional[str] = None,
                                 weekdays_only: bool = True,
                                 max_posts_per_hour: int = 2,
                                 timezone: str = 'Asia/Taipei',
                                 generation_config: Optional[Dict[str, Any]] = None,
                                 batch_info: Optional[Dict[str, Any]] = None,
                                 # 🔥 FIX: Add trigger_config and schedule_config parameters
                                 trigger_config: Optional[Dict[str, Any]] = None,
                                 schedule_config: Optional[Dict[str, Any]] = None,
                                 auto_posting: bool = False,
                                 # 來源追蹤參數
                                 source_type: Optional[str] = None,
                                 source_batch_id: Optional[str] = None,
                                 source_experiment_id: Optional[str] = None,
                                 source_feature_name: Optional[str] = None,
                                 created_by: str = 'system') -> str:
        """創建排程任務 - 持久化到資料庫"""
        
        # 🔥 添加詳細的創建日誌記錄
        print(f"🚀🚀🚀 開始創建排程任務 🚀🚀🚀")
        print(f"📋 創建參數:")
        print(f"   📊 Session ID: {session_id}")
        print(f"   📝 排程名稱: {schedule_name}")
        print(f"   📝 排程描述: {schedule_description}")
        print(f"   🕐 排程類型: {schedule_type}")
        print(f"   ⏰ 執行時間: {daily_execution_time}")
        print(f"   📅 僅工作日: {weekdays_only}")
        print(f"   🤖 自動發文: {auto_posting}")
        print(f"   ⏱️ 間隔秒數: {interval_seconds}")
        print(f"   📈 每小時最大發文數: {max_posts_per_hour}")
        print(f"   🌍 時區: {timezone}")
        print(f"   📦 批次資訊: {batch_info}")
        print(f"   🎯 生成配置: {generation_config}")
        
        # 🔥 詳細分析生成配置
        if generation_config:
            print(f"🔍 生成配置詳情:")
            print(f"   🎯 觸發器類型: {generation_config.get('trigger_type', 'N/A')}")
            print(f"   📝 發文類型: {generation_config.get('posting_type', 'N/A')}")
            print(f"   📊 股票排序: {generation_config.get('stock_sorting', 'N/A')}")
            print(f"   📈 最大股票數: {generation_config.get('max_stocks', 'N/A')}")
            print(f"   👥 KOL分配: {generation_config.get('kol_assignment', 'N/A')}")
            print(f"   🎨 內容風格: {generation_config.get('content_style', 'N/A')}")
            print(f"   📏 內容長度: {generation_config.get('content_length', 'N/A')}")
            print(f"   📰 新聞連結: {generation_config.get('enable_news_links', 'N/A')}")
            print(f"   🔧 生成模式: {generation_config.get('generation_mode', 'N/A')}")
        else:
            print(f"⚠️ 沒有提供生成配置")
        # 生成預設排程名稱
        if not schedule_name:
            # 使用台灣時區生成時間戳
            tz = pytz.timezone('Asia/Taipei')
            taiwan_time = datetime.now(tz)
            timestamp = taiwan_time.strftime('%Y%m%d_%H%M%S')
            
            # 根據觸發器類型和股票排序生成名稱
            if generation_config:
                trigger_type = generation_config.get('trigger_type', 'unknown')
                stock_sorting = generation_config.get('stock_sorting', 'unknown')
                
                # 觸發器類型映射
                trigger_map = {
                    'limit_up_after_hours': '盤後漲',
                    'limit_down_after_hours': '盤後跌',
                    'intraday_limit_up': '盤中漲',
                    'intraday_limit_down': '盤中跌',
                    'custom_stocks': '自選股',
                    'news_hot': '熱門新聞'
                }
                
                # 股票排序映射
                sorting_map = {
                    'five_day_change_desc': '五日漲幅',
                    'change_percent_desc': '漲跌幅',
                    'volume_desc': '成交量',
                    'current_price_desc': '股價',
                    'market_cap_desc': '市值'
                }
                
                trigger_name = trigger_map.get(trigger_type, '未知觸發')
                sorting_name = sorting_map.get(stock_sorting, '未知排序')
                
                schedule_name = f"{trigger_name}_{sorting_name}_{timestamp}"
            else:
                # 根據排程類型生成更友好的名稱
                if schedule_type == 'weekday_daily':
                    schedule_name = f"工作日排程_{timestamp}"
                elif schedule_type == '24hour_batch':
                    schedule_name = f"24小時批次_{timestamp}"
                elif schedule_type == '5min_batch':
                    schedule_name = f"5分鐘批次_{timestamp}"
                elif schedule_type == 'immediate':
                    schedule_name = f"立即執行_{timestamp}"
                else:
                    schedule_name = f"排程任務_{timestamp}"
        
        # 創建資料庫記錄
        schedule_id = await self.db_service.create_schedule_task(
            schedule_name=schedule_name,
            schedule_description=schedule_description,
            session_id=session_id,
            schedule_type=schedule_type,
            interval_seconds=interval_seconds,
            batch_duration_hours=batch_duration_hours,
            daily_execution_time=daily_execution_time,
            weekdays_only=weekdays_only,
            max_posts_per_hour=max_posts_per_hour,
            timezone=timezone,
            generation_config=generation_config,
            batch_info=batch_info,
            # 🔥 FIX: Pass trigger_config and schedule_config to database
            trigger_config=trigger_config,
            schedule_config=schedule_config,
            auto_posting=auto_posting,
            # 來源追蹤參數
            source_type=source_type,
            source_batch_id=source_batch_id,
            source_experiment_id=source_experiment_id,
            source_feature_name=source_feature_name,
            created_by=created_by
        )
        
        # 創建記憶體中的任務對象（向後兼容）
        task = ScheduleTask(
            task_id=schedule_id,
            session_id=session_id,
            post_ids=post_ids,
            schedule_type=schedule_type,
            interval_seconds=interval_seconds,
            batch_duration_hours=batch_duration_hours,
            schedule_name=schedule_name,
            schedule_description=schedule_description,
            daily_execution_time=daily_execution_time,
            weekdays_only=weekdays_only,
            max_posts_per_hour=max_posts_per_hour,
            timezone=timezone,
            generation_config=generation_config,
            batch_info=batch_info
        )
        
        self.tasks[schedule_id] = task
        logger.info(f"✅ 排程任務創建成功 - Schedule ID: {schedule_id}, Session ID: {session_id}")
        logger.info(f"📋 排程類型: {schedule_type}, 工作日執行: {weekdays_only}")
        if daily_execution_time:
            logger.info(f"⏰ 每日執行時間: {daily_execution_time}")
        
        return schedule_id
    
    async def start_background_scheduler(self):
        """啟動背景排程器，自動啟動所有 active 排程"""
        logger.info("🚀🚀🚀 開始啟動背景排程器 🚀🚀🚀")
        
        if self.background_scheduler_running:
            logger.warning("⚠️ 背景排程器已在運行中，跳過啟動")
            return
        
        self.background_scheduler_running = True
        logger.info("🔄 啟動背景排程器狀態: STARTING")
        
        try:
            # 獲取所有 active 排程任務
            logger.info("📊 正在獲取所有 active 排程任務...")
            active_tasks = await self.db_service.get_active_schedule_tasks()
            logger.info(f"📋 資料庫中發現 {len(active_tasks)} 個 active 排程任務")
            
            if len(active_tasks) == 0:
                logger.info("✅ 沒有 active 排程任務，背景排程器空轉等待")
                # 持續等待，每小時檢查一次
                while self.background_scheduler_running:
                    await asyncio.sleep(3600)  # 等待 1 小時
                    active_tasks = await self.db_service.get_active_schedule_tasks()
                    if len(active_tasks) > 0:
                        logger.info(f"📋 發現新的 active 排程任務: {len(active_tasks)} 個")
                        break
                return
            
            # 啟動所有 active 排程
            success_count = 0
            failure_count = 0
            
            for idx, task in enumerate(active_tasks, 1):
                task_id = task['schedule_id']
                schedule_name = task.get('schedule_name', 'Unknown')
                schedule_type = task.get('schedule_type', 'Unknown')
                daily_execution_time = task.get('daily_execution_time', 'Not Set')
                
                logger.info(f"🔍 處理排程任務 {idx}/{len(active_tasks)}:")
                logger.info(f"   📋 Task ID: {task_id}")
                logger.info(f"   📝 排程名稱: {schedule_name}")
                logger.info(f"   🕐 排程類型: {schedule_type}")
                logger.info(f"   ⏰ 執行時間: {daily_execution_time}")
                logger.info(f"   🔄 狀態: {task.get('status', 'Unknown')}")
                logger.info(f"   📊 Session ID: {task.get('session_id', 'N/A')}")
                logger.info(f"   🌍 時區: {task.get('timezone', 'N/A')}")
                logger.info(f"   📅 僅工作日: {task.get('weekdays_only', 'N/A')}")
                logger.info(f"   🤖 自動發文: {task.get('auto_posting', 'N/A')}")
                logger.info(f"   ⏱️ 間隔秒數: {task.get('interval_seconds', 'N/A')}")
                logger.info(f"   📈 每小時最大發文數: {task.get('max_posts_per_hour', 'N/A')}")
                logger.info(f"   🏃 執行次數: {task.get('run_count', 0)}")
                logger.info(f"   ✅ 成功次數: {task.get('success_count', 0)}")
                logger.info(f"   ❌ 失敗次數: {task.get('failure_count', 0)}")
                logger.info(f"   📈 成功率: {task.get('success_rate', 0)}%")
                logger.info(f"   📝 下次執行: {task.get('next_run', 'Not Set')}")
                logger.info(f"   📝 最後執行: {task.get('last_run', 'Never')}")
                
                # 🔥 計算並顯示預計執行時間
                try:
                    next_run_time = await self._calculate_next_run_time(task)
                    if next_run_time:
                        tz_next_run = next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                        logger.info(f"   🎯 預計下次執行時間: {tz_next_run}")
                        
                        # 計算距離執行還有多久
                        now = datetime.now(pytz.timezone(task.get('timezone', 'Asia/Taipei')))
                        time_diff = next_run_time - now
                        if time_diff.total_seconds() > 0:
                            hours = int(time_diff.total_seconds() // 3600)
                            minutes = int((time_diff.total_seconds() % 3600) // 60)
                            logger.info(f"   ⏳ 距離執行還有: {hours}小時{minutes}分鐘")
                        else:
                            logger.info(f"   ⚠️ 執行時間已過，將重新計算")
                    else:
                        logger.warning(f"   ⚠️ 無法計算預計執行時間")
                except Exception as calc_error:
                    logger.error(f"   ❌ 計算預計執行時間失敗: {calc_error}")
                
                # 🔥 顯示觸發器配置
                trigger_config = task.get('trigger_config', {})
                if trigger_config:
                    logger.info(f"   🎯 觸發器配置:")
                    logger.info(f"      🎯 觸發器類型: {trigger_config.get('trigger_type', 'N/A')}")
                    logger.info(f"      📊 最大股票數: {trigger_config.get('max_stocks', 'N/A')}")
                    logger.info(f"      👥 KOL分配: {trigger_config.get('kol_assignment', 'N/A')}")
                    logger.info(f"      📈 股票排序: {trigger_config.get('stock_sorting', 'N/A')}")
                
                # 🔥 顯示生成配置
                generation_config = task.get('generation_config', {})
                if generation_config:
                    logger.info(f"   🎨 生成配置:")
                    logger.info(f"      📝 發文類型: {generation_config.get('posting_type', 'N/A')}")
                    logger.info(f"      📏 內容長度: {generation_config.get('content_length', 'N/A')}")
                    logger.info(f"      🎨 內容風格: {generation_config.get('content_style', 'N/A')}")
                    logger.info(f"      📰 新聞連結: {generation_config.get('enable_news_links', 'N/A')}")
                
                # 🔥 顯示批次資訊
                batch_info = task.get('batch_info', {})
                if batch_info:
                    logger.info(f"   📦 批次資訊:")
                    logger.info(f"      📊 總發文數: {batch_info.get('total_posts', 'N/A')}")
                    logger.info(f"      ✅ 已發布數: {batch_info.get('published_posts', 'N/A')}")
                    logger.info(f"      📈 成功率: {batch_info.get('success_rate', 'N/A')}%")
                    logger.info(f"      🏢 股票代碼: {batch_info.get('stock_codes', 'N/A')}")
                    logger.info(f"      👥 KOL名稱: {batch_info.get('kol_names', 'N/A')}")
                
                # 檢查是否有執行時間設定
                if not daily_execution_time or daily_execution_time == 'Not Set':
                    logger.warning(f"⚠️ 排程沒有設定執行時間，跳過執行 - Task ID: {task_id}")
                    failure_count += 1
                    continue
                status = task.get('status', 'unknown')
                
                logger.info(f"🚀 [{idx}/{len(active_tasks)}] 正在準備啟動排程任務:")
                logger.info(f"   📋 Task ID: {task_id}")
                logger.info(f"   📝 排程名稱: {schedule_name}")
                logger.info(f"   🕐 排程類型: {schedule_type}")
                logger.info(f"   ⏰ 執行時間: {daily_execution_time}")
                logger.info(f"   🔄 當前狀態: {status}")
                
                try:
                    # 檢查是否已有運行中的任務
                    if task_id in self.running_tasks:
                        existing_task = self.running_tasks[task_id]
                        if not existing_task.done():
                            logger.warning(f"⚠️ 排程任務已在運行 - Task ID: {task_id}")
                            success_count += 1
                            continue
                        else:
                            logger.info(f"🔄 清理已完成的任務: {task_id}")
                            del self.running_tasks[task_id]
                    
                    # 啟動新的排程任務
                    logger.info(f"🎯 創建排程任務協程 - Task ID: {task_id}")
                    running_task = asyncio.create_task(self._execute_schedule_task(task_id))
                    self.running_tasks[task_id] = running_task
                    
                    # 等待一小段時間確保任務啟動成功
                    await asyncio.sleep(0.1)
                    
                    if not running_task.done():
                        success_count += 1
                        logger.info(f"✅ 排程任務啟動成功 - Task ID: {task_id}")
                    else:
                        failure_count += 1
                        logger.error(f"❌ 排程任務立即完成（可能失敗）- Task ID: {task_id}")
                        
                except Exception as e:
                    failure_count += 1
                    logger.error(f"❌ 排程任務啟動失敗 - Task ID: {task_id}")
                    logger.error(f"🔍 錯誤類型: {type(e).__name__}")
                    logger.error(f"🔍 錯誤詳情: {str(e)}")
                    import traceback
                    logger.error(f"🔍 錯誤堆疊:\n{traceback.format_exc()}")
            
            # 啟動總結
            logger.info("📊 背景排程器啟動總結:")
            logger.info(f"   ✅ 成功啟動: {success_count} 個任務")
            logger.info(f"   ❌ 啟動失敗: {failure_count} 個任務")
            logger.info(f"   🔄 總運行中: {len(self.running_tasks)} 個任務")
            
            if success_count > 0:
                logger.info("✅ 背景排程器啟動完成 - 開始監控執行")
                self.background_scheduler_running = True
                
                # 持續監控運行中的任務
                while self.background_scheduler_running:
                    try:
                        # 檢查是否有任務需要重啟
                        active_tasks = await self.db_service.get_active_schedule_tasks()
                        current_running_task_ids = set(self.running_tasks.keys())
                        active_task_ids = {task['schedule_id'] for task in active_tasks}
                        
                        # 啟動新的 active 任務
                        for task in active_tasks:
                            task_id = task['schedule_id']
                            if task_id not in current_running_task_ids:
                                logger.info(f"🔄 發現新的 active 任務，正在啟動: {task_id}")
                                try:
                                    task_obj = asyncio.create_task(self._execute_schedule_task(task_id))
                                    self.running_tasks[task_id] = task_obj
                                    logger.info(f"✅ 新任務啟動成功: {task_id}")
                                except Exception as e:
                                    logger.error(f"❌ 新任務啟動失敗: {task_id}, Error: {e}")
                        
                        # 清理已停止的任務
                        for task_id in list(current_running_task_ids):
                            if task_id not in active_task_ids:
                                logger.info(f"🛑 任務已停止，清理: {task_id}")
                                if task_id in self.running_tasks:
                                    self.running_tasks[task_id].cancel()
                                    del self.running_tasks[task_id]
                        
                        # 等待 5 分鐘後再次檢查
                        await asyncio.sleep(300)
                        
                    except Exception as e:
                        logger.error(f"❌ 背景排程器監控錯誤: {e}")
                        await asyncio.sleep(60)  # 錯誤時等待 1 分鐘
            else:
                logger.warning("⚠️ 沒有成功啟動任何排程任務")
                
        except Exception as e:
            logger.error(f"❌ 背景排程器啟動失敗: {e}")
            logger.error(f"🔍 錯誤類型: {type(e).__name__}")
            import traceback
            logger.error(f"🔍 錯誤堆疊:\n{traceback.format_exc()}")
            self.background_scheduler_running = False
    
    async def start_schedule_task(self, task_id: str) -> bool:
        """啟動排程任務"""
        logger.info(f"🎯 準備啟動單一排程任務 - Task ID: {task_id}")
        
        # 先從資料庫獲取任務資訊
        logger.info(f"📊 正在從資料庫獲取任務資訊...")
        db_task = await self.db_service.get_schedule_task(task_id)
        
        if not db_task:
            logger.error(f"❌ 排程任務不存在於資料庫中 - Task ID: {task_id}")
            return False
        
        schedule_name = db_task.get('schedule_name', 'Unknown')
        schedule_type = db_task.get('schedule_type', 'Unknown')
        current_status = db_task.get('status', 'unknown')
        daily_execution_time = db_task.get('daily_execution_time', 'Not Set')
        
        logger.info(f"📋 任務資訊確認:")
        logger.info(f"   📋 Task ID: {task_id}")
        logger.info(f"   📝 排程名稱: {schedule_name}")
        logger.info(f"   🕐 排程類型: {schedule_type}")
        logger.info(f"   🔄 當前狀態: {current_status}")
        logger.info(f"   ⏰ 執行時間: {daily_execution_time}")
        
        # 詳細的排程設定資訊
        logger.info(f"🔧 詳細排程設定:")
        logger.info(f"   📊 Session ID: {db_task.get('session_id', 'N/A')}")
        logger.info(f"   📝 描述: {db_task.get('schedule_description', 'N/A')}")
        logger.info(f"   ⏱️ 間隔秒數: {db_task.get('interval_seconds', 'N/A')}")
        logger.info(f"   🌍 時區: {db_task.get('timezone', 'N/A')}")
        logger.info(f"   📅 僅工作日: {db_task.get('weekdays_only', 'N/A')}")
        logger.info(f"   📈 每小時最大發文數: {db_task.get('max_posts_per_hour', 'N/A')}")
        logger.info(f"   🤖 自動發文: {db_task.get('auto_posting', 'N/A')}")
        
        # 觸發器配置
        trigger_config = db_task.get('trigger_config', {})
        if trigger_config:
            logger.info(f"🎯 觸發器配置:")
            logger.info(f"   🎯 觸發器類型: {trigger_config.get('trigger_type', 'N/A')}")
            logger.info(f"   📊 最大股票數: {trigger_config.get('max_stocks', 'N/A')}")
            logger.info(f"   👥 KOL分配: {trigger_config.get('kol_assignment', 'N/A')}")
            logger.info(f"   📈 股票排序: {trigger_config.get('stock_sorting', 'N/A')}")
        
        # 生成配置
        generation_config = db_task.get('generation_config', {})
        if generation_config:
            logger.info(f"🎨 生成配置:")
            logger.info(f"   📝 發文類型: {generation_config.get('posting_type', 'N/A')}")
            logger.info(f"   📏 內容長度: {generation_config.get('content_length', 'N/A')}")
            logger.info(f"   🎨 內容風格: {generation_config.get('content_style', 'N/A')}")
            logger.info(f"   📰 新聞連結: {generation_config.get('enable_news_links', 'N/A')}")
        
        # 批次資訊
        batch_info = db_task.get('batch_info', {})
        if batch_info:
            logger.info(f"📦 批次資訊:")
            logger.info(f"   📊 總發文數: {batch_info.get('total_posts', 'N/A')}")
            logger.info(f"   ✅ 已發布數: {batch_info.get('published_posts', 'N/A')}")
            logger.info(f"   📈 成功率: {batch_info.get('success_rate', 'N/A')}%")
            logger.info(f"   🏢 股票代碼: {batch_info.get('stock_codes', 'N/A')}")
            logger.info(f"   👥 KOL名稱: {batch_info.get('kol_names', 'N/A')}")
        
        if current_status not in ['pending', 'cancelled', 'active']:
            logger.error(f"❌ 排程任務狀態不正確 - Task ID: {task_id}, 期望: pending, cancelled 或 active, 實際: {current_status}")
            return False
        
        if current_status == 'active':
            logger.info(f"ℹ️ 排程任務已經是 active 狀態，直接啟動執行循環 - Task ID: {task_id}")
            # 直接啟動執行循環，不改變狀態
        else:
            logger.info(f"✅ 任務狀態檢查通過，狀態有效")
        
        logger.info(f"✅ 任務狀態檢查通過，狀態有效")
        
        try:
            logger.info(f"⏰ 正在計算初始執行時間...")
            # 計算初始的下次執行時間
            next_run_time = await self._calculate_next_run_time(db_task)
            
            if next_run_time:
                tz_next_run = next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                logger.info(f"✅ 計算成功 - 下次執行時間: {tz_next_run}")
            else:
                logger.warning(f"⚠️ 無法計算下次執行時間，將使用安全默認值")
            
            logger.info(f"💾 正在更新資料庫狀態為 active...")
            # 更新資料庫狀態和下次執行時間
            await self.db_service.update_schedule_status(
                task_id, 'active', started_at=datetime.utcnow()
            )
            logger.info(f"✅ 資料庫狀態更新成功")
            
            if next_run_time:
                logger.info(f"💾 正在更新下次執行時間...")
                await self.db_service.update_schedule_next_run(task_id, next_run_time)
                logger.info(f"✅ 下次執行時間更新成功")
            
            # 更新記憶體中的任務狀態
            if task_id in self.tasks:
                logger.info(f"🔄 正在更新記憶體中的任務狀態...")
                task = self.tasks[task_id]
                task.status = 'active'
                task.started_at = datetime.utcnow()
                logger.info(f"✅ 記憶體狀態更新成功")
            
            logger.info(f"🚀 正在創建異步任務協程...")
            # 創建異步任務
            running_task = asyncio.create_task(self._execute_schedule_task(task_id))
            self.running_tasks[task_id] = running_task
            
            # 檢查任務是否成功啟動
            await asyncio.sleep(0.05)  # 短暫等待
            
            if not running_task.done():
                logger.info(f"✅ 異步任務成功啟動並運行中")
                logger.info(f"🎉 排程任務啟動完全成功 - Task ID: {task_id}")
                logger.info(f"📊 當前運行中任務總數: {len(self.running_tasks)}")
                return True
            else:
                logger.error(f"❌ 異步任務立即完成（可能啟動失敗）")
                return False
            
        except Exception as e:
            logger.error(f"❌ 啟動排程任務失敗 - Task ID: {task_id}")
            logger.error(f"🔍 錯誤類型: {type(e).__name__}")
            logger.error(f"🔍 錯誤詳情: {str(e)}")
            import traceback
            logger.error(f"🔍 錯誤堆疊:\n{traceback.format_exc()}")
            
            # 嘗試更新資料庫狀態為 failed
            try:
                await self.db_service.update_schedule_status(
                    task_id, 'failed', error_message=str(e)
                )
                logger.info(f"💾 已將任務狀態更新為 failed")
            except Exception as db_error:
                logger.error(f"❌ 更新資料庫狀態失敗: {db_error}")
            
            return False
    
    async def execute_task_immediately(self, task_id: str) -> bool:
        """立即執行排程任務（測試用）- 不影響排程狀態"""
        logger.info(f"🔔🔔🔔 排程系統立即執行測試開始 - Task ID: {task_id} 🔔🔔🔔")
        logger.info(f"🎯 開始立即執行排程任務測試 - Task ID: {task_id}")
        
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"⏰ 當前執行時間: {current_time}")
            
            # 從資料庫獲取任務資訊
            logger.info(f"📊 正在獲取任務詳細資訊...")
            db_task = await self.db_service.get_schedule_task(task_id)
            
            if not db_task:
                logger.error(f"❌ 排程任務不存在於資料庫中 - Task ID: {task_id}")
                return False
            
            schedule_name = db_task.get('schedule_name', 'Unknown')
            schedule_type = db_task.get('schedule_type', 'weekday_daily')
            current_status = db_task.get('status', 'unknown')
            generation_config = db_task.get('generation_config', {})
            
            logger.info(f"📋 立即執行任務資訊:")
            logger.info(f"   📋 Task ID: {task_id}")
            logger.info(f"   📝 排程名稱: {schedule_name}")
            logger.info(f"   🕐 排程類型: {schedule_type}")
            logger.info(f"   🔄 當前狀態: {current_status}")
            logger.info(f"   ⚙️ 生成配置: {generation_config}")
            
            # 根據排程類型執行對應的邏輯
            logger.info(f"🚀 準備執行排程邏輯...")
            
            if schedule_type == 'weekday_daily' or not schedule_type:
                logger.info(f"✅ 排程類型確認: weekday_daily，開始執行...")
                # 執行工作日每日排程
                result = await self._execute_weekday_daily_schedule(task_id, db_task)
                
                if result:
                    logger.info(f"✅ 工作日每日排程執行完成 - Task ID: {task_id}")
                else:
                    logger.error(f"❌ 工作日每日排程執行失敗 - Task ID: {task_id}")
                    return False
            else:
                logger.warning(f"⚠️ 不支持的排程類型: {schedule_type}")
                logger.info(f"💡 當前支持的排程類型: weekday_daily")
                return False
            
            # 記錄執行完成時間
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            duration = (datetime.now() - datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')).total_seconds()
            
            logger.info(f"🎉 立即執行測試完全成功 - Task ID: {task_id}")
            logger.info(f"⏱️ 執行完成時間: {completion_time}")
            logger.info(f"⏱️ 執行耗時: {duration:.2f} 秒")
            logger.info(f"🔔🔔🔔 排程系統立即執行測試結束 - Task ID: {task_id} 🔔🔔🔔")
            
            return True
            
        except Exception as e:
            error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.error(f"❌ 立即執行測試失敗 - Task ID: {task_id}")
            logger.error(f"⏰ 失敗時間: {error_time}")
            logger.error(f"🔍 錯誤類型: {type(e).__name__}")
            logger.error(f"🔍 錯誤詳情: {str(e)}")
            import traceback
            logger.error(f"🔍 錯誤堆疊:\n{traceback.format_exc()}")
            return False
    
    async def _execute_schedule_task(self, task_id: str):
        """執行排程任務 - 持續運行模式"""
        try:
            logger.info(f"🚀 開始執行排程任務 - Task ID: {task_id}")
            
            # 從資料庫獲取任務資訊
            db_task = await self.db_service.get_schedule_task(task_id)
            if not db_task:
                raise Exception(f"排程任務不存在: {task_id}")
            
            # 持續運行循環
            while True:
                try:
                    # 檢查任務是否仍為 active 狀態
                    current_task = await self.db_service.get_schedule_task(task_id)
                    if not current_task or current_task['status'] != 'active':
                        logger.info(f"🛑 排程任務已停止 - Task ID: {task_id}")
                        break
                    
                    # 檢查是否應該執行
                    should_execute = await self._should_execute_now(current_task)
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if not should_execute:
                        logger.debug(f"⏰ 排程未到執行時間 - Task ID: {task_id}, 時間: {current_time}")
                        # 等待 1 分鐘後再檢查，確保不會錯過執行時間
                        await asyncio.sleep(60)
                        continue
                    
                    # 🔥 關鍵修復：檢查今日是否已執行過，避免重複執行
                    last_run = current_task.get('last_run')
                    if last_run:
                        tz = pytz.timezone('Asia/Taipei')
                        
                        # 處理 last_run 可能是字符串的情況
                        if isinstance(last_run, str):
                            # 如果是字符串，解析為 datetime
                            try:
                                if 'T' in last_run:
                                    # ISO 格式
                                    last_run_dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                                else:
                                    # 其他格式
                                    last_run_dt = datetime.strptime(last_run, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                logger.warning(f"⚠️ 無法解析 last_run 時間格式: {last_run}")
                                continue
                        else:
                            # 已經是 datetime 對象
                            last_run_dt = last_run
                        
                        # 確保時區處理正確
                        if last_run_dt.tzinfo is None:
                            # 沒有時區信息，假設為 UTC 然後轉換
                            last_run_tz = pytz.UTC.localize(last_run_dt).astimezone(tz)
                        else:
                            # 有時區信息，直接轉換
                            last_run_tz = last_run_dt.astimezone(tz)
                        
                        now_tz = datetime.now(tz)
                        
                        # 如果今日已執行過，跳過本次執行
                        if last_run_tz.date() == now_tz.date():
                            logger.info(f"⏰ 今日已執行過，跳過重複執行 - Task ID: {task_id}, 上次執行: {last_run_tz.strftime('%Y-%m-%d %H:%M:%S')}")
                            # 等待到明天再執行
                            tomorrow = now_tz.date() + timedelta(days=1)
                            tomorrow_execution_time = current_task.get('daily_execution_time', '16:30')
                            try:
                                exec_time = datetime.strptime(tomorrow_execution_time.split('T')[1].split('.')[0], '%H:%M:%S').time() if 'T' in tomorrow_execution_time else datetime.strptime(tomorrow_execution_time.strip(), '%H:%M').time()
                                next_execution = tz.localize(datetime.combine(tomorrow, exec_time))
                                sleep_seconds = (next_execution - now_tz).total_seconds()
                                await asyncio.sleep(max(sleep_seconds, 3600))  # 至少等待 1 小時
                            except:
                                await asyncio.sleep(86400)  # 等待 24 小時
                            continue
                    
                    logger.info(f"⏰ 🚀 觸發排程執行 - Task ID: {task_id}, 時間: {current_time}")
                    logger.info(f"📋 排程名稱: {current_task.get('schedule_name', 'Unknown')}")
                    logger.info(f"🕐 排程類型: {current_task.get('schedule_type', 'Unknown')}")
                    
                    # 更新最後執行時間
                    await self.db_service.update_schedule_status(
                        task_id, 'active', last_run=datetime.utcnow()
                    )
                    
                    # 執行排程邏輯
                    if current_task['schedule_type'] == 'immediate':
                        # 立即執行所有貼文
                        if current_task.get('auto_posting'):
                            await self._publish_posts_immediately(task_id, current_task.get('post_ids', []))
                        else:
                            logger.info("🛑 自動發文關閉，跳過立即發布")
                    elif current_task['schedule_type'] == '24hour_batch':
                        # 24小時內分批發文
                        if current_task.get('auto_posting'):
                            await self._publish_posts_with_interval(task_id, current_task.get('post_ids', []), current_task['interval_seconds'])
                        else:
                            logger.info("🛑 自動發文關閉，跳過分批發布")
                    elif current_task['schedule_type'] == '5min_batch':
                        # 5分鐘內分批發文
                        if current_task.get('auto_posting'):
                            await self._publish_posts_with_interval(task_id, current_task.get('post_ids', []), current_task['interval_seconds'])
                        else:
                            logger.info("🛑 自動發文關閉，跳過分批發布")
                    elif current_task['schedule_type'] == 'weekday_daily':
                        # 工作日每日執行批次腳本
                        await self._execute_weekday_daily_schedule(task_id, current_task)
                    
                    # 🔥 注意：統計數據已在具體執行方法中更新，這裡不需要重複更新
                    # await self.db_service.increment_schedule_stats(
                    #     task_id, run_count=1, success_count=1
                    # )
                    
                    # 計算下次執行時間
                    next_run_time = await self._calculate_next_run_time(current_task)
                    if next_run_time:
                        # 更新資料庫中的下次執行時間
                        await self.db_service.update_schedule_next_run(task_id, next_run_time)
                        logger.info(f"⏰ 下次執行時間: {next_run_time}")

                        # 等待到下次執行時間
                        tz = pytz.timezone('Asia/Taipei')
                        now = datetime.now(tz)
                        # 確保兩個時間都是 aware 的
                        if next_run_time.tzinfo is None:
                            next_run_time = tz.localize(next_run_time)
                        elif next_run_time.tzinfo != tz:
                            # 如果時區不同，轉換到台北時區
                            next_run_time = next_run_time.astimezone(tz)
                        if now.tzinfo is None:
                            now = tz.localize(now)
                        sleep_seconds = (next_run_time - now).total_seconds()
                        
                        if sleep_seconds and sleep_seconds > 0:
                            logger.info(f"😴 等待 {sleep_seconds/3600:.1f} 小時後執行")
                            await asyncio.sleep(sleep_seconds)
                        else:
                            logger.warning("⚠️ 下次執行時間已過，立即執行")
                    else:
                        # 如果無法計算下次執行時間，設定為明天的同一個時間 + 15分鐘
                        logger.warning("⚠️ 無法計算下次執行時間，設定為明天 16:30 (安全默認值)")
                        try:
                            # 安全默認：明天 16:30 執行
                            tz = pytz.timezone('Asia/Taipei')
                            now = datetime.now(tz)
                            tomorrow = now.date() + timedelta(days=1)
                            fallback_time = tz.localize(datetime.combine(tomorrow, datetime.strptime('16:30', '%H:%M').time()))
                            await self.db_service.update_schedule_next_run(task_id, fallback_time)
                            logger.info(f"✅ 設定安全默認執行時間: {fallback_time}")
                            
                            # 計算等待時間
                            sleep_seconds = (fallback_time - now).total_seconds()
                            if sleep_seconds > 0:
                                logger.info(f"😴 等待 {sleep_seconds/3600:.1f} 小時後執行")
                                await asyncio.sleep(min(sleep_seconds, 86400))  # 最多等待 24 小時
                        except Exception as fallback_error:
                            logger.error(f"❌ 設定默認執行時間失敗: {fallback_error}")
                            # 最後的安全措施：等待 4 小時
                            await asyncio.sleep(14400)
                    
                except Exception as e:
                    logger.error(f"❌ 排程任務執行失敗 - Task ID: {task_id}, Error: {e}")
                    
                    # 更新失敗統計
                    try:
                        await self.db_service.increment_schedule_stats(
                            task_id, run_count=1, failure_count=1
                        )
                    except Exception as db_error:
                        logger.error(f"❌ 更新失敗統計失敗: {db_error}")
                    
                    # 計算下次執行時間（即使失敗也要等到明天）
                    try:
                        current_task = await self.db_service.get_schedule_task(task_id)
                        if current_task:
                            next_run_time = await self._calculate_next_run_time(current_task)
                            if next_run_time:
                                await self.db_service.update_schedule_next_run(task_id, next_run_time)
                                tz = pytz.timezone('Asia/Taipei')
                                now = datetime.now(tz)
                                if next_run_time.tzinfo is None:
                                    next_run_time = tz.localize(next_run_time)
                                elif next_run_time.tzinfo != tz:
                                    # 如果時區不同，轉換到台北時區
                                    next_run_time = next_run_time.astimezone(tz)
                                if now.tzinfo is None:
                                    now = tz.localize(now)
                                sleep_seconds = (next_run_time - now).total_seconds()
                                if sleep_seconds and sleep_seconds > 0:
                                    logger.info(f"⚠️ 執行失敗，等待 {sleep_seconds/3600:.1f} 小時後重試")
                                    await asyncio.sleep(sleep_seconds)
                                else:
                                    logger.warning("⚠️ 執行失敗，等待 1 小時後重試")
                                    await asyncio.sleep(3600)
                            else:
                                logger.warning("⚠️ 無法計算下次執行時間，等待 1 小時後重試")
                                await asyncio.sleep(3600)
                        else:
                            logger.warning("⚠️ 無法獲取任務資訊，等待 1 小時後重試")
                            await asyncio.sleep(3600)
                    except Exception as calc_error:
                        logger.error(f"❌ 計算下次執行時間失敗: {calc_error}, 等待 1 小時")
                        await asyncio.sleep(3600)
            
            logger.info(f"✅ 排程任務結束 - Task ID: {task_id}")
            
        except Exception as e:
            logger.error(f"❌ 排程任務執行失敗 - Task ID: {task_id}, Error: {e}")
            
            # 更新失敗狀態
            await self.db_service.update_schedule_status(
                task_id, 'failed', error_message=str(e)
            )
            
            # 更新記憶體中的任務狀態
            if task_id in self.tasks:
                self.tasks[task_id].status = 'failed'
                self.tasks[task_id].error_message = str(e)
    
    async def _publish_posts_immediately(self, task_id: str, post_ids: List[str]):
        """立即發布所有貼文"""
        logger.info(f"📝 立即發布 {len(post_ids)} 篇貼文")
        
        success_count = 0
        for post_id in post_ids:
            try:
                logger.info(f"📝 發布貼文 - Post ID: {post_id}")
                
                # 調用實際的發布服務
                from publish_service import publish_service
                from main import get_post_record_service
                
                # 獲取貼文記錄
                post_service = get_post_record_service()
                post_record = post_service.get_post_record(post_id)
                
                if not post_record:
                    logger.error(f"❌ 找不到貼文記錄 - Post ID: {post_id}")
                    continue
                
                if post_record.status not in ["approved", "draft"]:
                    logger.error(f"❌ 貼文狀態不正確，無法發文 - Post ID: {post_id}, 狀態: {post_record.status}")
                    continue
                
                # 實際發布到 CMoney
                publish_result = await publish_service.publish_post(post_record)
                
                if publish_result.get("success"):
                    logger.info(f"✅ 貼文發布成功 - Post ID: {post_id}")
                    success_count += 1
                else:
                    logger.error(f"❌ 貼文發布失敗 - Post ID: {post_id}, 錯誤: {publish_result.get('error')}")
                
                # 記錄貼文與排程的關聯
                await self.db_service.add_generated_post(task_id, post_id)
                
            except Exception as e:
                logger.error(f"❌ 發布貼文異常 - Post ID: {post_id}, 錯誤: {e}")
        
        # 更新統計數據
        await self.db_service.increment_schedule_stats(
            task_id, posts_generated=len(post_ids), success_count=success_count
        )
        
        logger.info(f"📊 發布完成 - 成功: {success_count}/{len(post_ids)}")
    
    async def _publish_posts_with_interval(self, task_id: str, post_ids: List[str], interval_seconds: int):
        """按間隔發布貼文"""
        logger.info(f"📝 按間隔 {interval_seconds} 秒發布 {len(post_ids)} 篇貼文")
        
        success_count = 0
        for i, post_id in enumerate(post_ids):
            try:
                logger.info(f"📝 發布貼文 {i+1}/{len(post_ids)} - Post ID: {post_id}")
                
                # 調用實際的發布服務
                from publish_service import publish_service
                from main import get_post_record_service
                
                # 獲取貼文記錄
                post_service = get_post_record_service()
                post_record = post_service.get_post_record(post_id)
                
                if not post_record:
                    logger.error(f"❌ 找不到貼文記錄 - Post ID: {post_id}")
                    continue
                
                if post_record.status not in ["approved", "draft"]:
                    logger.error(f"❌ 貼文狀態不正確，無法發文 - Post ID: {post_id}, 狀態: {post_record.status}")
                    continue
                
                # 實際發布到 CMoney
                publish_result = await publish_service.publish_post(post_record)
                
                if publish_result.get("success"):
                    logger.info(f"✅ 貼文發布成功 - Post ID: {post_id}")
                    success_count += 1
                else:
                    logger.error(f"❌ 貼文發布失敗 - Post ID: {post_id}, 錯誤: {publish_result.get('error')}")
                
                # 記錄貼文與排程的關聯
                await self.db_service.add_generated_post(task_id, post_id)
                
                if i < len(post_ids) - 1:  # 不是最後一篇
                    logger.info(f"⏳ 等待 {interval_seconds} 秒後發布下一篇...")
                    await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ 發布貼文異常 - Post ID: {post_id}, 錯誤: {e}")
        
        # 更新統計數據
        await self.db_service.increment_schedule_stats(
            task_id, posts_generated=len(post_ids), success_count=success_count
        )
        
        logger.info(f"📊 間隔發布完成 - 成功: {success_count}/{len(post_ids)}")
    
    async def _execute_weekday_daily_schedule(self, task_id: str, db_task: Dict[str, Any]):
        """執行工作日每日排程"""
        try:
            logger.info(f"🚀 開始執行工作日排程 - Task ID: {task_id}")
            logger.info(f"📋 排程設定: {db_task['schedule_name']}")
            logger.info(f"⚙️ 生成配置: {db_task['generation_config']}")
            
            # 詳細記錄執行參數
            trigger_type = db_task['generation_config'].get('trigger_type', 'unknown')
            stock_sorting = db_task['generation_config'].get('stock_sorting', 'unknown')
            max_stocks = db_task['generation_config'].get('max_stocks', 10)
            kol_assignment = db_task['generation_config'].get('kol_assignment', 'unknown')
            
            logger.info(f"🔍 執行參數詳情:")
            logger.info(f"   📈 觸發器類型: {trigger_type}")
            logger.info(f"   📊 股票排序: {stock_sorting}")
            logger.info(f"   🎯 最大股票數: {max_stocks}")
            logger.info(f"   👥 KOL分配方式: {kol_assignment}")
            
            # 1. 根據觸發器類型篩選股票
            logger.info(f"🔍 開始篩選股票（觸發器: {trigger_type}）...")
            stocks = await self._filter_stocks_by_trigger(db_task['generation_config'])
            logger.info(f"📊 篩選結果: 共 {len(stocks)} 檔股票")
            
            # 詳細記錄篩選到的股票
            if stocks:
                logger.info(f"📋 篩選到的股票:")
                for i, stock in enumerate(stocks, 1):
                    stock_code = stock.get('stock_code', 'N/A')
                    stock_name = stock.get('stock_name', 'N/A')
                    change_percent = stock.get('change_percent', 0)
                    logger.info(f"   {i}. {stock_code} {stock_name} ({change_percent:.2f}%)")
            
            # 檢查是否篩選到股票
            if not stocks or len(stocks) == 0:
                logger.warning(f"⚠️ 未篩選到股票，本次排程跳過執行 - Task ID: {task_id}")
                # 更新統計：算作失敗
                await self.db_service.increment_schedule_stats(
                    task_id, run_count=1, failure_count=1
                )
                return False  # 直接返回失敗，不拋出異常
            
            # 2. 根據KOL分配方式分配KOL
            logger.info(f"👥 開始KOL分配（方式: {kol_assignment}）...")
            kol_assignments = await self._assign_kols_to_stocks(stocks, db_task['generation_config'])
            logger.info(f"👥 KOL分配完成: {len(kol_assignments)} 個分配")
            
            # 詳細記錄KOL分配結果
            if kol_assignments:
                logger.info(f"👥 分配詳情:")
                for i, assignment in enumerate(kol_assignments, 1):
                    stock_code = assignment.get('stock_code', 'N/A')
                    stock_name = assignment.get('stock_name', 'N/A')
                    kol_serial = assignment.get('kol_serial', 'N/A')
                    kol_nickname = assignment.get('kol_nickname', 'N/A')
                    logger.info(f"   {i}. {stock_code} {stock_name} → KOL-{kol_serial} ({kol_nickname})")
            
            if not kol_assignments or len(kol_assignments) == 0:
                logger.warning(f"⚠️ KOL分配失敗，本次排程跳過執行 - Task ID: {task_id}")
                await self.db_service.increment_schedule_stats(
                    task_id, run_count=1, failure_count=1
                )
                return False
            
            # 3. 生成貼文內容
            logger.info(f"📝 開始生成貼文內容...")
            posts = await self._generate_posts_with_config(kol_assignments, db_task['generation_config'], task_id)
            logger.info(f"📝 貼文生成完成: 共 {len(posts)} 篇貼文")
            
            if not posts or len(posts) == 0:
                logger.warning(f"⚠️ 未生成任何貼文，本次排程跳過執行 - Task ID: {task_id}")
                await self.db_service.increment_schedule_stats(
                    task_id, run_count=1, failure_count=1
                )
                return False
            
            # 詳細記錄生成的貼文
            logger.info(f"📋 生成的貼文詳情:")
            for i, post in enumerate(posts, 1):
                post_id = post.get('post_id', 'N/A')
                stock_code = post.get('stock_code', 'N/A')
                stock_name = post.get('stock_name', 'N/A')
                kol_serial = post.get('kol_serial', 'N/A')
                title = post.get('title', 'N/A')
                logger.info(f"   {i}. {post_id}: {stock_code} {stock_name} (KOL-{kol_serial})")
                logger.info(f"      📝 標題: {title[:50]}..." if len(title) > 50 else f"      📝 標題: {title}")
            
            # 4. 按間隔發布貼文（受 auto_posting 控制）
            auto_posting_value = db_task.get('auto_posting')
            logger.info(f"🔍 調試 auto_posting 值: {auto_posting_value} (類型: {type(auto_posting_value)})")
            
            if auto_posting_value:
                logger.info(f"🚀 開始按間隔發布貼文 (間隔: {db_task['interval_seconds']} 秒)...")
                await self._publish_posts_with_interval(task_id, [post['post_id'] for post in posts], db_task['interval_seconds'])
                logger.info(f"🚀 貼文發布完成")
            else:
                logger.info("🛑 自動發文關閉，僅生成貼文不發布")
            
            # 🔥 更新統計數據 - 記錄生成的貼文數量
            await self.db_service.increment_schedule_stats(
                task_id, run_count=1, success_count=1, posts_generated=len(posts)
            )
            logger.info(f"📊 已更新排程統計: 生成 {len(posts)} 篇貼文")
            
            # 記錄執行成功
            logger.info(f"✅ 工作日排程執行成功完成 - Task ID: {task_id}")
            logger.info(f"📊 執行摘要:")
            logger.info(f"   🎯 觸發器: {trigger_type}")
            logger.info(f"   📈 篩選股票: {len(stocks)} 檔")
            logger.info(f"   👥 KOL分配: {len(kol_assignments)} 個")
            logger.info(f"   📝 生成貼文: {len(posts)} 篇")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 工作日排程執行失敗 - Task ID: {task_id}, Error: {e}")
            logger.error(f"🔍 錯誤類型: {type(e).__name__}")
            logger.error(f"🔍 錯誤詳情: {str(e)}")
            import traceback
            logger.error(f"🔍 錯誤堆疊:\n{traceback.format_exc()}")
            
            # 嘗試更新失敗統計
            try:
                await self.db_service.increment_schedule_stats(
                    task_id, run_count=1, failure_count=1
                )
                logger.info(f"💾 已更新失敗統計")
            except Exception as stats_error:
                logger.error(f"❌ 更新失敗統計失敗: {stats_error}")
            
            return False
    
    async def _filter_stocks_by_trigger(self, generation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根據觸發器類型篩選股票"""
        trigger_type = generation_config.get('trigger_type', 'limit_up_after_hours')
        stock_sorting = generation_config.get('stock_sorting', 'five_day_change_desc')
        max_stocks = generation_config.get('max_stocks', 10)
        
        logger.info(f"🔍 篩選股票 - 觸發器: {trigger_type}, 排序: {stock_sorting}, 最大檔數: {max_stocks}")
        
        try:
            # 導入股票篩選服務
            from stock_filter_service import stock_filter_service
            
            # 調用實際的股票篩選服務
            stocks = await stock_filter_service.filter_stocks_by_trigger(
                trigger_type=trigger_type,
                stock_sorting=stock_sorting,
                max_stocks=max_stocks,
                additional_filters=generation_config.get('additional_filters')
            )
            
            logger.info(f"✅ 股票篩選完成，共 {len(stocks)} 檔股票")
            return stocks
            
        except Exception as e:
            logger.error(f"❌ 股票篩選服務調用失敗: {e}")
            # 返回模擬數據作為備用
            mock_stocks = [
                {"stock_code": "841", "stock_name": "大江", "change_percent": 9.8},
                {"stock_code": "2330", "stock_name": "台積電", "change_percent": 5.2},
                {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 3.8},
                {"stock_code": "2454", "stock_name": "聯發科", "change_percent": 4.1},
            ]
            return mock_stocks[:max_stocks]
    
    async def _assign_kols_to_stocks(self, stocks: List[Dict[str, Any]], generation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根據KOL分配方式分配KOL"""
        import random
        
        kol_assignment = generation_config.get('kol_assignment', 'random')
        
        logger.info(f"👥 KOL分配 - 方式: {kol_assignment}")
        
        # 模擬KOL列表 - 使用實際的KOL名稱和序號
        available_kols = [
            {"name": "川川哥", "serial": "200", "persona": "技術派"},
            {"name": "小道爆料王", "serial": "201", "persona": "消息派"},
            {"name": "長線韭韭", "serial": "202", "persona": "總經+價值派"},
            {"name": "信號宅神", "serial": "203", "persona": "量化派"},
            {"name": "梅川褲子", "serial": "204", "persona": "新聞派"},
            {"name": "韭割哥", "serial": "205", "persona": "總經派"},
            {"name": "龜狗一日散戶", "serial": "206", "persona": "籌碼派"},
            {"name": "技術分析師", "serial": "207", "persona": "技術派"},
            {"name": "基本面達人", "serial": "208", "persona": "價值派"}
        ]
        
        assignments = []
        for i, stock in enumerate(stocks):
            if kol_assignment == 'random':
                # 🔥 真正的隨機分配
                selected_kol = random.choice(available_kols)
                kol_name = selected_kol["name"]
                kol_serial = selected_kol["serial"]
            else:
                # 固定指派第一個KOL
                selected_kol = available_kols[0]
                kol_name = selected_kol["name"]
                kol_serial = selected_kol["serial"]
            
            assignments.append({
                "stock_code": stock["stock_code"],
                "stock_name": stock["stock_name"],
                "kol_nickname": kol_name,
                "kol_serial": kol_serial
            })
            
            logger.info(f"📊 股票 {stock['stock_code']} 分配給 KOL: {kol_name} (序號: {kol_serial})")
        
        return assignments
    
    async def _generate_posts_with_config(self, kol_assignments: List[Dict[str, Any]], generation_config: Dict[str, Any], task_id: str) -> List[Dict[str, Any]]:
        """使用生成配置生成貼文"""
        content_style = generation_config.get('content_style', 'technical')
        content_length = generation_config.get('content_length', 'medium')
        max_words = generation_config.get('max_words', 1000)
        enable_news_links = generation_config.get('enable_news_links', True)  # 新增：新聞連結開關
        news_max_links = generation_config.get('news_max_links', 5) if enable_news_links else 0  # 只有啟用時才設定數量
        
        logger.info(f"📝 生成貼文 - 風格: {content_style}, 長度: {content_length}, 字數: {max_words}, 新聞連結: {'啟用' if enable_news_links else '停用'}({news_max_links}則)")
        
        posts = []
        for assignment in kol_assignments:
            try:
                # 調用實際的內容生成服務
                post = await self._generate_single_post(assignment, generation_config, task_id)
                posts.append(post)
            except Exception as e:
                logger.error(f"❌ 生成貼文失敗 - 股票: {assignment['stock_code']}, 錯誤: {e}")
                # 使用模擬數據作為備用
                post = {
                    "post_id": f"schedule_{assignment['stock_code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "stock_code": assignment["stock_code"],
                    "stock_name": assignment["stock_name"],
                    "kol_nickname": assignment["kol_nickname"],
                    "kol_serial": assignment["kol_serial"],
                    "title": f"{assignment['stock_name']} 技術分析",
                    "content": f"這是 {assignment['stock_name']} 的技術分析內容...",
                    "generation_config": generation_config
                }
                posts.append(post)
        
        return posts
    
    async def _generate_single_post(self, assignment: Dict[str, Any], generation_config: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """生成單個貼文 - 調用實際的內容生成服務"""
        try:
            # 導入必要的服務
            from main import manual_post_content
            from main import PostingRequest
            
            # 獲取排程任務的 auto_posting 設定
            db_task = await self.db_service.get_schedule_task(task_id)
            auto_posting = db_task.get('auto_posting', False) if db_task else False
            
            # 構建 PostingRequest
            posting_request = PostingRequest(
                stock_code=assignment["stock_code"],
                stock_name=assignment["stock_name"],
                kol_serial=assignment["kol_serial"],
                kol_persona=generation_config.get('kol_persona', 'technical'),
                content_style=generation_config.get('content_style', 'chart_analysis'),
                target_audience=generation_config.get('target_audience', 'active_traders'),
                content_length=generation_config.get('content_length', 'medium'),
                max_words=generation_config.get('max_words', 1000),
                auto_post=auto_posting,  # 根據排程任務的 auto_posting 設定決定是否自動發文
                batch_mode=True,
                session_id=0,  # 排程系統使用 0 作為 session_id
                trigger_type=generation_config.get('trigger_type', 'limit_up_after_hours'),
                # 新增：新聞連結配置
                enable_news_links=generation_config.get('enable_news_links', True),
                news_max_links=generation_config.get('news_max_links', 5) if generation_config.get('enable_news_links', True) else 0
            )
            
            logger.info(f"🎯 調用內容生成服務 - Task ID: {task_id}, 股票: {assignment['stock_code']}, KOL: {assignment['kol_serial']}")
            
            # 設置當前task_id，供manual_post_content使用
            import os
            os.environ['CURRENT_SCHEDULE_TASK_ID'] = task_id
            
            # 調用內容生成服務
            result = await manual_post_content(posting_request)
            
            # 🔥 修復：排程完成後清除環境變數，避免影響後續手動操作
            if 'CURRENT_SCHEDULE_TASK_ID' in os.environ:
                del os.environ['CURRENT_SCHEDULE_TASK_ID']
            
            if result.success:
                logger.info(f"✅ 內容生成成功 - Post ID: {result.post_id}")
                return {
                    "post_id": result.post_id,
                    "stock_code": assignment["stock_code"],
                    "stock_name": assignment["stock_name"],
                    "kol_nickname": assignment["kol_nickname"],
                    "kol_serial": assignment["kol_serial"],
                    "title": result.content.get('title', f"{assignment['stock_name']} 分析"),
                    "content": result.content.get('content', ''),
                    "generation_config": generation_config
                }
            else:
                raise Exception(f"內容生成失敗: {result.error}")
                
        except Exception as e:
            logger.error(f"❌ 單個貼文生成失敗: {e}")
            raise e
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """獲取任務狀態 - 從資料庫獲取"""
        db_task = await self.db_service.get_schedule_task(task_id)
        if not db_task:
            return None
        
        # 獲取生成的貼文列表
        generated_posts = await self.db_service.get_schedule_posts(task_id)
        
        # 確保所有時間欄位都正確序列化
        created_at_str = db_task['created_at'].isoformat() if db_task.get('created_at') else None
        last_run_str = db_task['last_run'].isoformat() if db_task.get('last_run') else None
        next_run_str = db_task['next_run'].isoformat() if db_task.get('next_run') else None
        started_at_str = db_task['started_at'].isoformat() if db_task.get('started_at') else None
        completed_at_str = db_task['completed_at'].isoformat() if db_task.get('completed_at') else None

        # 確保所有數值欄位都是數字，不是 None
        run_count = db_task.get('run_count') or 0
        success_count = db_task.get('success_count') or 0
        failure_count = db_task.get('failure_count') or 0
        total_posts_generated = db_task.get('total_posts_generated') or 0
        interval_seconds = db_task.get('interval_seconds') or 30

        # 計算成功率，確保不會除以零
        success_rate = (success_count / max(run_count, 1)) * 100 if run_count > 0 else 0.0

        return {
            'task_id': db_task['schedule_id'],
            'name': db_task.get('schedule_name') or 'Unnamed Schedule',
            'description': db_task.get('schedule_description') or f"基於批次 {db_task.get('session_id', 'N/A')} 的排程",
            'session_id': db_task.get('session_id') or 0,
            'post_ids': generated_posts,  # 從關聯表獲取
            'schedule_type': db_task.get('schedule_type') or 'weekday_daily',
            'status': db_task.get('status') or 'pending',
            'auto_posting': bool(db_task.get('auto_posting', False)),  # 確保是布林值
            'created_at': created_at_str,
            'last_run': last_run_str,
            'next_run': next_run_str,
            'run_count': run_count,
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': round(success_rate, 2),
            'started_at': started_at_str,
            'completed_at': completed_at_str,
            'error_message': db_task.get('error_message'),
            'total_posts_generated': total_posts_generated,
            'interval_seconds': interval_seconds,
            'schedule_config': {
                'enabled': db_task.get('status') == 'active',
                'posting_time_slots': [db_task['daily_execution_time']] if db_task.get('daily_execution_time') else [],
                'timezone': db_task.get('timezone') or 'Asia/Taipei',
                'auto_posting': bool(db_task.get('auto_posting', False))
            },
            'trigger_config': {
                'trigger_type': (db_task.get('generation_config') or {}).get('trigger_type', 'limit_up_after_hours'),
                'stock_codes': [],  # 不顯示具體股票代碼
                'kol_assignment': (db_task.get('generation_config') or {}).get('kol_assignment', 'random'),
                'max_stocks': (db_task.get('generation_config') or {}).get('max_stocks', 10) or 10,
                'stock_sorting': {
                    'primary_sort': (db_task.get('generation_config') or {}).get('stock_sorting', 'five_day_change_desc')
                }
            },
            'batch_info': db_task.get('batch_info') or {},
            'generation_config': db_task.get('generation_config') or {}
        }
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """獲取所有任務 - 從資料庫獲取"""
        db_tasks = await self.db_service.get_all_schedule_tasks()
        result = []
        for task in db_tasks:
            task_status = await self.get_task_status(task['schedule_id'])
            if task_status:
                result.append(task_status)
        return result
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任務"""
        # 取消正在運行的任務
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        # 更新資料庫狀態
        success = await self.db_service.cancel_schedule_task(task_id)
        if success:
            # 更新記憶體中的任務狀態
            if task_id in self.tasks:
                self.tasks[task_id].status = 'cancelled'
            logger.info(f"✅ 排程任務已取消 - Task ID: {task_id}")
        
        return success
    
    async def _should_execute_now(self, task: Dict[str, Any]) -> bool:
        """檢查是否應該現在執行排程"""
        try:
            schedule_type = task['schedule_type']
            daily_execution_time = task.get('daily_execution_time')
            weekdays_only = task.get('weekdays_only', True)
            timezone = task.get('timezone', 'Asia/Taipei')
            
            logger.info(f"🔍 檢查執行時間 - Task ID: {task.get('schedule_id')}")
            logger.info(f"   📅 daily_execution_time: {repr(daily_execution_time)}")
            logger.info(f"   🌍 timezone: {timezone}")
            
            # 獲取當前時間
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            
            # 檢查是否為工作日
            if weekdays_only and now.weekday() >= 5:  # 0-4 是週一到週五，5-6 是週末
                logger.info(f"📅 今天是週末，跳過執行 - Task ID: {task['schedule_id']}")
                return False
            
            # 檢查執行時間
            if daily_execution_time:
                try:
                    # 解析執行時間 (格式: "09:00" 或 "09:00-18:00" 或 ISO 格式)
                    # 先處理 ISO 格式時間 (2025-09-30T20:04:00.000Z)
                    if 'T' in daily_execution_time:
                        time_part = daily_execution_time.split('T')[1].split('.')[0]
                        execution_time = datetime.strptime(time_part, '%H:%M:%S').time()
                        current_time = now.time()
                        
                        # 嚴格按照設定時間執行，不允許提前執行
                        current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
                        execution_seconds = execution_time.hour * 3600 + execution_time.minute * 60 + execution_time.second
                        
                        # 只允許在設定時間之後的 2 分鐘內執行（不允許提前）
                        if current_seconds >= execution_seconds and current_seconds <= execution_seconds + 120:
                            return True
                    elif '-' in daily_execution_time and ':' in daily_execution_time:
                        # 時間範圍格式 (09:00-18:00)
                        parts = daily_execution_time.split('-')
                        if len(parts) == 2:
                            start_time_str = parts[0].strip()
                            end_time_str = parts[1].strip()
                            start_time = datetime.strptime(start_time_str, '%H:%M').time()
                            end_time = datetime.strptime(end_time_str, '%H:%M').time()
                            
                            # 檢查是否在執行時間範圍內
                            current_time = now.time()
                            if start_time <= current_time <= end_time:
                                return True
                    else:
                        # 單一時間點
                        logger.info(f"   🕐 解析單一時間點: {daily_execution_time}")
                        execution_time = datetime.strptime(daily_execution_time.strip(), '%H:%M').time()
                        current_time = now.time()
                        
                        logger.info(f"   🕐 執行時間: {execution_time}")
                        logger.info(f"   🕐 當前時間: {current_time}")
                        
                        # 嚴格按照設定時間執行，不允許提前執行
                        current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
                        execution_seconds = execution_time.hour * 3600 + execution_time.minute * 60
                        
                        logger.info(f"   🕐 當前秒數: {current_seconds}")
                        logger.info(f"   🕐 執行秒數: {execution_seconds}")
                        
                        # 只允許在設定時間之後的 1 分鐘內執行（不允許提前）
                        if current_seconds >= execution_seconds and current_seconds <= execution_seconds + 60:
                            logger.info(f"   ✅ 時間檢查通過，應該執行")
                            return True
                        else:
                            logger.info(f"   ❌ 時間檢查失敗，不執行")
                            return False
                except ValueError as e:
                    logger.error(f"❌ 解析執行時間失敗: {daily_execution_time}, Error: {e}")
                    logger.error(f"❌ 當前時間: {now}, 時區: {timezone}")
                    return False
            
            # 如果沒有設定執行時間，則不執行（等待設定）
            logger.warning(f"⚠️ 排程沒有設定執行時間，跳過執行 - Task ID: {task['schedule_id']}")
            return False
            
        except Exception as e:
            logger.error(f"❌ 檢查執行時間失敗: {e}")
            return False
    
    async def _calculate_next_run_time(self, task: Dict[str, Any]) -> Optional[datetime]:
        """計算下次執行時間 - 時區固定台北時間，明天同一時間執行"""
        try:
            daily_execution_time = task.get('daily_execution_time')
            task_id = task.get('schedule_id', 'Unknown')
            
            logger.info(f"⏰ 開始計算下次執行時間 - Task ID: {task_id}")
            logger.info(f"   📝 執行時間設定: {daily_execution_time}")
            
            if not daily_execution_time:
                logger.error(f"❌ 沒有設定執行時間 - Task ID: {task_id}")
                return None
            
            if not daily_execution_time:
                # 如果沒有設定執行時間，返回 None（會等待 1 小時）
                return None
            
            # 固定使用台北時區
            tz = pytz.timezone('Asia/Taipei')
            now = datetime.now(tz)
            
            try:
                # 處理 ISO 格式時間 (2025-09-30T20:04:00.000Z)
                if 'T' in daily_execution_time:
                    # ISO 格式，提取時間部分
                    time_part_with_tz = daily_execution_time.split('T')[1]  # 20:04:00.000Z
                    time_part_only = time_part_with_tz.split('.')[0]  # 20:04:00
                    execution_time = datetime.strptime(time_part_only, '%H:%M:%S').time()
                elif ',' in daily_execution_time:
                    # 多個時間範圍 (例如: 09:00-12:00,14:00-18:00)
                    first_range = daily_execution_time.split(',')[0]
                    if '-' in first_range:
                        parts = first_range.split('-')
                        start_time_str = parts[0].strip()
                        execution_time = datetime.strptime(start_time_str, '%H:%M').time()
                    else:
                        execution_time = datetime.strptime(first_range.strip(), '%H:%M').time()
                elif '-' in daily_execution_time and ':' in daily_execution_time:
                    # 時間範圍，計算明天的開始時間 (例如: 09:00-12:00)
                    parts = daily_execution_time.split('-')
                    start_time_str = parts[0].strip()
                    execution_time = datetime.strptime(start_time_str, '%H:%M').time()
                else:
                    # 單一時間點
                    execution_time = datetime.strptime(daily_execution_time.strip(), '%H:%M').time()
                
                # 計算下次執行時間：先檢查今天是否已過執行時間
                today_execution = tz.localize(datetime.combine(now.date(), execution_time))
                
                if now < today_execution:
                    # 今天的執行時間還沒到，使用今天
                    next_run = today_execution
                    logger.info(f"⏰ 計算下次執行時間: {next_run} (今天，台北時間)")
                else:
                    # 今天的執行時間已過，使用明天
                    tomorrow = now.date() + timedelta(days=1)
                    next_run = tz.localize(datetime.combine(tomorrow, execution_time))
                    logger.info(f"⏰ 計算下次執行時間: {next_run} (明天，台北時間)")
                
                return next_run
                
            except ValueError as e:
                logger.error(f"❌ 解析執行時間失敗: {daily_execution_time}, Error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 計算下次執行時間失敗: {e}")
            return None

# 全局排程服務實例
schedule_service = ScheduleService()