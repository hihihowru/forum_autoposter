#!/usr/bin/env python3
"""
創建最新狀態工作表
"""

import os
import sys

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient

def create_latest_status_sheet():
    """創建最新狀態工作表"""
    try:
        # 從環境變量獲取配置
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
        
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 準備標題行
        headers = [
            "article_id", "member_id", "nickname", "title", "content", 
            "topic_id", "is_trending_topic", "post_time", "last_update_time",
            "likes_count", "comments_count", "total_interactions", 
            "engagement_rate", "growth_rate", "collection_error"
        ]
        
        # 使用現有的「aigc 自我學習機制」工作表
        sheets_client.write_sheet("aigc 自我學習機制", [headers])
        print("✅ 成功更新「aigc 自我學習機制」工作表")
        
    except Exception as e:
        print(f"❌ 更新工作表時發生錯誤: {str(e)}")

if __name__ == "__main__":
    create_latest_status_sheet()
