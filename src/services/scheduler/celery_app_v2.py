"""
Celery 排程應用程式 V2
基於發文時間的動態互動數據收集
"""

import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 創建 Celery 應用程式
app = Celery('n8n_migration_scheduler_v2')

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
        'scheduler.tasks_v2.check_and_collect_interactions': {'queue': 'interactions'},
        'scheduler.tasks_v2.collect_specific_interaction': {'queue': 'interactions'},
        'scheduler.tasks_v2.generate_content_for_ready_tasks': {'queue': 'content'},
        'scheduler.tasks_v2.publish_ready_posts': {'queue': 'publishing'},
        'scheduler.tasks_v2.fetch_and_assign_topics': {'queue': 'content'},
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

# 定義定時任務 - 基於發文時間的動態收集
app.conf.beat_schedule = {
    # 每10分鐘檢查是否有貼文到達收集時間點
    'check-interactions-by-post-time': {
        'task': 'scheduler.tasks_v2.check_and_collect_interactions',
        'schedule': crontab(minute='*/10'),  # 每10分鐘執行
        'options': {'queue': 'interactions'}
    },
    
    # 每15分鐘處理 ready_to_gen 任務
    'generate-content-for-ready-tasks': {
        'task': 'scheduler.tasks_v2.generate_content_for_ready_tasks',
        'schedule': crontab(minute='*/15'),  # 每15分鐘執行
        'options': {'queue': 'content'}
    },
    
    # 每30分鐘處理 ready_to_post 任務
    'publish-ready-posts': {
        'task': 'scheduler.tasks_v2.publish_ready_posts',
        'schedule': crontab(minute='*/30'),  # 每30分鐘執行
        'options': {'queue': 'publishing'}
    },
    
    # 每4小時獲取新的熱門話題
    'fetch-trending-topics': {
        'task': 'scheduler.tasks_v2.fetch_and_assign_topics',
        'schedule': crontab(minute=0, hour='*/4'),  # 每4小時執行
        'options': {'queue': 'content'}
    },
}

if __name__ == '__main__':
    app.start()
