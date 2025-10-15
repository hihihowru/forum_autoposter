"""
時區工具函數
統一處理 UTC+8 時區
"""

import pytz
from datetime import datetime

# 台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣時間 (UTC+8)"""
    return datetime.now(TAIWAN_TZ)

def get_taiwan_utcnow():
    """獲取台灣時間 (UTC+8)，但返回 naive datetime（用於數據庫存儲）"""
    taiwan_now = datetime.now(TAIWAN_TZ)
    # 轉換為 naive datetime（移除時區信息）
    return taiwan_now.replace(tzinfo=None)

def convert_utc_to_taiwan(utc_datetime):
    """將 UTC 時間轉換為台灣時間"""
    if utc_datetime is None:
        return None
    
    if utc_datetime.tzinfo is None:
        # 假設是 UTC 時間
        utc_dt = pytz.UTC.localize(utc_datetime)
    else:
        utc_dt = utc_datetime
    
    return utc_dt.astimezone(TAIWAN_TZ)

def convert_taiwan_to_utc(taiwan_datetime):
    """將台灣時間轉換為 UTC 時間"""
    if taiwan_datetime is None:
        return None
    
    if taiwan_datetime.tzinfo is None:
        # 假設是台灣時間
        taiwan_dt = TAIWAN_TZ.localize(taiwan_datetime)
    else:
        taiwan_dt = taiwan_datetime
    
    return taiwan_dt.astimezone(pytz.UTC)
