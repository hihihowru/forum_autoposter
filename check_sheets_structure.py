#!/usr/bin/env python3
"""
檢查Google Sheets中的貼文記錄結構
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_sheets_structure():
    """檢查Google Sheets中的貼文記錄結構"""
    print("🔍 檢查Google Sheets中的貼文記錄結構...")
    
    try:
        from src.clients.google.sheets_client import GoogleSheetsClient
        
        # 初始化Google Sheets客戶端
        credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "./credentials/google-service-account.json")
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取貼文紀錄表
        posts_data = sheets_client.read_sheet("貼文紀錄表")
        
        if not posts_data:
            print("❌ 無法獲取貼文記錄")
            return
        
        print(f"📊 總共 {len(posts_data)} 行數據")
        
        # 顯示標題行
        if len(posts_data) > 0:
            print("\n📋 標題行:")
            headers = posts_data[0]
            for i, header in enumerate(headers):
                print(f"  {i:2d}. {header}")
        
        # 顯示前幾行數據
        print(f"\n📋 前5行數據:")
        for i, row in enumerate(posts_data[:6]):  # 標題行 + 前5行數據
            print(f"\n第 {i} 行:")
            for j, cell in enumerate(row[:10]):  # 只顯示前10個欄位
                print(f"  {j:2d}. {cell}")
        
        # 查找trigger_type為limit_up_stock_smart的行
        print(f"\n🔍 查找trigger_type為limit_up_stock_smart的行:")
        limit_up_posts = []
        for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
            if len(row) > 5:
                trigger_type = row[5] if len(row) > 5 else ""
                status = row[4] if len(row) > 4 else ""
                if trigger_type == "limit_up_stock_smart":
                    limit_up_posts.append((i, row))
                    print(f"  第 {i} 行: status={status}, trigger_type={trigger_type}")
        
        print(f"\n📊 找到 {len(limit_up_posts)} 行limit_up_stock_smart貼文")
        
        # 查找status為ready_to_post的行
        print(f"\n🔍 查找status為ready_to_post的行:")
        ready_posts = []
        for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
            if len(row) > 4:
                status = row[4] if len(row) > 4 else ""
                trigger_type = row[5] if len(row) > 5 else ""
                if status == "ready_to_post":
                    ready_posts.append((i, row))
                    print(f"  第 {i} 行: status={status}, trigger_type={trigger_type}")
        
        print(f"\n📊 找到 {len(ready_posts)} 行ready_to_post貼文")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sheets_structure()