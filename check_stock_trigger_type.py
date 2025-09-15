#!/usr/bin/env python3
"""
檢查stock_trigger_type欄位
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_stock_trigger_type():
    """檢查stock_trigger_type欄位"""
    print("🔍 檢查stock_trigger_type欄位...")
    
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
        
        # 檢查最後20行的stock_trigger_type欄位
        print(f"\n📋 最後20行的stock_trigger_type欄位:")
        for i, row in enumerate(posts_data[-20:], len(posts_data)-19):
            print(f"\n第 {i} 行:")
            if len(row) > 31:
                print(f"  stock_id: {row[20] if len(row) > 20 else ''}")
                print(f"  stock_name: {row[21] if len(row) > 21 else ''}")
                print(f"  stock_trigger_type: {row[31] if len(row) > 31 else ''}")
                print(f"  status: {row[4] if len(row) > 4 else ''}")
                print(f"  title: {row[32] if len(row) > 32 else ''}")
        
        # 查找stock_trigger_type為limit_up_stock_smart的行
        print(f"\n🔍 查找stock_trigger_type為limit_up_stock_smart的行:")
        limit_up_posts = []
        for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
            if len(row) > 31:
                stock_trigger_type = row[31] if len(row) > 31 else ""
                status = row[4] if len(row) > 4 else ""
                if stock_trigger_type == "limit_up_stock_smart":
                    limit_up_posts.append((i, row))
                    print(f"  第 {i} 行: status={status}, stock_trigger_type={stock_trigger_type}")
        
        print(f"\n📊 找到 {len(limit_up_posts)} 行stock_trigger_type為limit_up_stock_smart的貼文")
        
        # 檢查這些貼文的狀態
        ready_posts = []
        for row_index, row in limit_up_posts:
            status = row[4] if len(row) > 4 else ""
            if status == "ready_to_post":
                ready_posts.append((row_index, row))
        
        print(f"\n📊 其中 {len(ready_posts)} 行狀態為ready_to_post")
        
        if ready_posts:
            print(f"\n📋 ready_to_post的貼文:")
            for row_index, row in ready_posts:
                print(f"  第 {row_index} 行: {row[21] if len(row) > 21 else ''}({row[20] if len(row) > 20 else ''}) - {row[8] if len(row) > 8 else ''}")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_stock_trigger_type()


