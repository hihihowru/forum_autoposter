#!/usr/bin/env python3
"""
檢查最新的貼文記錄
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_latest_posts():
    """檢查最新的貼文記錄"""
    print("🔍 檢查最新的貼文記錄...")
    
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
        
        # 檢查最後20行數據
        print(f"\n📋 最後20行數據:")
        for i, row in enumerate(posts_data[-20:], len(posts_data)-19):
            print(f"\n第 {i} 行:")
            if len(row) > 10:
                print(f"  test_post_id: {row[0] if len(row) > 0 else ''}")
                print(f"  status: {row[4] if len(row) > 4 else ''}")
                print(f"  trigger_type: {row[5] if len(row) > 5 else ''}")
                print(f"  kol_serial: {row[7] if len(row) > 7 else ''}")
                print(f"  kol_nickname: {row[8] if len(row) > 8 else ''}")
                print(f"  stock_id: {row[22] if len(row) > 22 else ''}")
                print(f"  stock_name: {row[23] if len(row) > 23 else ''}")
                print(f"  title: {row[36] if len(row) > 36 else ''}")
        
        # 查找包含我們股票代號的行
        target_stocks = ["2344", "2642", "3211", "2408", "6789", "4989", "2323", "8088", "3323", "5234", "6895", "5345", "8034", "3006", "8358", "5309", "8299"]
        
        print(f"\n🔍 查找包含目標股票代號的行:")
        found_posts = []
        for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
            if len(row) > 22:
                stock_id = row[22] if len(row) > 22 else ""
                if stock_id in target_stocks:
                    found_posts.append((i, row))
                    print(f"  第 {i} 行: stock_id={stock_id}, status={row[4] if len(row) > 4 else ''}, trigger_type={row[5] if len(row) > 5 else ''}")
        
        print(f"\n📊 找到 {len(found_posts)} 行包含目標股票代號的貼文")
        
        # 檢查這些貼文的狀態
        ready_posts = []
        for row_index, row in found_posts:
            status = row[4] if len(row) > 4 else ""
            if status == "ready_to_post":
                ready_posts.append((row_index, row))
        
        print(f"\n📊 其中 {len(ready_posts)} 行狀態為ready_to_post")
        
        if ready_posts:
            print(f"\n📋 ready_to_post的貼文:")
            for row_index, row in ready_posts:
                print(f"  第 {row_index} 行: {row[23] if len(row) > 23 else ''}({row[22] if len(row) > 22 else ''}) - {row[8] if len(row) > 8 else ''}")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_latest_posts()