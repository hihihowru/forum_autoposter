"""
Celery 排程應用程式
用於定時執行互動數據收集任務
"""

import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 創建 Celery 應用程式
app = Celery('n8n_migration_scheduler')

# Redis 配置
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Celery 配置
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Taipei',
    enable_utc=True,
    
    # 任務配置
    task_routes={
        'scheduler.tasks.collect_hourly_interactions': {'queue': 'interactions'},
        'scheduler.tasks.collect_daily_interactions': {'queue': 'interactions'},
        'scheduler.tasks.collect_weekly_interactions': {'queue': 'interactions'},
        'scheduler.tasks.generate_content_for_ready_tasks': {'queue': 'content'},
        'scheduler.tasks.publish_ready_posts': {'queue': 'publishing'},
    },
    
    # 工作者配置
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # 錯誤處理
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    result_expires=3600,  # 結果保存1小時
)

# 定義定時任務
app.conf.beat_schedule = {
    # 每小時收集互動數據 (發文後1小時)
    'collect-hourly-interactions': {
        'task': 'scheduler.tasks.collect_hourly_interactions',
        'schedule': crontab(minute=5),  # 每小時的第5分鐘執行
        'options': {'queue': 'interactions'}
    },
    
    # 每日收集互動數據 (發文後1日)
    'collect-daily-interactions': {
        'task': 'scheduler.tasks.collect_daily_interactions', 
        'schedule': crontab(hour=1, minute=10),  # 每天凌晨1:10執行
        'options': {'queue': 'interactions'}
    },
    
    # 每週收集互動數據 (發文後1週)
    'collect-weekly-interactions': {
        'task': 'scheduler.tasks.collect_weekly_interactions',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # 每週一凌晨2:00執行
        'options': {'queue': 'interactions'}
    },
    
    # 每15分鐘處理 ready_to_gen 任務
    'generate-content-for-ready-tasks': {
        'task': 'scheduler.tasks.generate_content_for_ready_tasks',
        'schedule': crontab(minute='*/15'),  # 每15分鐘執行
        'options': {'queue': 'content'}
    },
    
    # 每30分鐘處理 ready_to_post 任務
    'publish-ready-posts': {
        'task': 'scheduler.tasks.publish_ready_posts',
        'schedule': crontab(minute='*/30'),  # 每30分鐘執行
        'options': {'queue': 'publishing'}
    },
    
    # 每4小時獲取新的熱門話題
    'fetch-trending-topics': {
        'task': 'scheduler.tasks.fetch_and_assign_topics',
        'schedule': crontab(minute=0, hour='*/4'),  # 每4小時執行
        'options': {'queue': 'content'}
    },
}

if __name__ == '__main__':
    app.start()
