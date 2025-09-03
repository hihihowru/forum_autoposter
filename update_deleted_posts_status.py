#!/usr/bin/env python3
"""
更新已刪除測試貼文的狀態
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def update_deleted_posts_status():
    """更新已刪除測試貼文的狀態"""
    
    print("=== 更新已刪除測試貼文的狀態 ===\n")
    
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
        
        # 找到需要更新的測試貼文
        test_post_ids = [
            'debug_test_002-200',
            'debug_test_002-201', 
            'debug_test_002-202',
            'improved_test_001-201',
            'improved_test_001-200',
            'improved_test_002-200',
            'improved_test_002-201',
            'general_test_001-200',
            'general_test_001-201'
        ]
        
        updated_count = 0
        
        # 更新狀態
        for i, row in enumerate(data[1:], 1):  # 跳過標題行
            if len(row) >= 12:
                post_id = row[0] if row[0] else ""
                
                if post_id in test_post_ids:
                    # 更新狀態為 "deleted"
                    row[11] = "deleted"  # 發文狀態列
                    row[14] = "已刪除測試貼文"  # 最近錯誤訊息列
                    updated_count += 1
                    print(f"更新貼文 {post_id} 狀態為 deleted")
        
        if updated_count > 0:
            # 寫回 Google Sheets
            sheets_client.write_sheet('貼文記錄表', data, 'A:R')
            print(f"\n✅ 成功更新 {updated_count} 篇測試貼文的狀態")
        else:
            print("✅ 沒有找到需要更新的測試貼文")
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_deleted_posts_status()
