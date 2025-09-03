#!/usr/bin/env python3
"""
更新今天刪除文章的狀態
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def update_today_deleted_status():
    """更新今天刪除文章的狀態"""
    
    print("=== 更新今天刪除文章的狀態 ===\n")
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    try:
        # 讀取貼文記錄表
        data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not data:
            print("❌ 無法讀取貼文記錄表")
            return
        
        # 獲取今天的日期
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"今天日期: {today}")
        
        # 今天刪除的文章ID
        today_deleted_ids = [
            '2330-202',
            '2330-200', 
            '2454-200',
            '2454-202'
        ]
        
        updated_count = 0
        
        # 更新狀態
        for i, row in enumerate(data[1:], 1):  # 跳過標題行
            if len(row) >= 12:
                post_id = row[0] if row[0] else ""
                
                if post_id in today_deleted_ids:
                    # 更新狀態為 "deleted"
                    row[11] = "deleted"  # 發文狀態列
                    row[14] = "已刪除今天發佈的文章"  # 最近錯誤訊息列
                    updated_count += 1
                    print(f"更新文章 {post_id} 狀態為 deleted")
        
        if updated_count > 0:
            # 寫回 Google Sheets
            sheets_client.write_sheet('貼文記錄表', data, 'A:R')
            print(f"\n✅ 成功更新 {updated_count} 篇今天刪除文章的狀態")
        else:
            print("✅ 沒有找到需要更新的文章")
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_today_deleted_status()
