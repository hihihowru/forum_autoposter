#!/usr/bin/env python3
"""
檢查發文結果
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def check_publish_results():
    """檢查發文結果"""
    
    print("=== 檢查發文結果 ===\n")
    
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
        
        print("貼文記錄表內容:")
        print("=" * 80)
        
        # 顯示標題行
        headers = data[0]
        print("標題行:")
        for i, header in enumerate(headers):
            print(f"  {i}: {header}")
        
        print("\n發文記錄:")
        print("-" * 80)
        
        # 顯示所有記錄
        for i, row in enumerate(data[1:], 1):
            if len(row) >= 16:  # 確保有足夠的列
                post_id = row[0] if row[0] else "N/A"
                kol_serial = row[1] if row[1] else "N/A"
                kol_nickname = row[2] if row[2] else "N/A"
                title = row[8] if len(row) > 8 and row[8] else "N/A"
                status = row[11] if len(row) > 11 and row[11] else "N/A"
                publish_time = row[13] if len(row) > 13 and row[13] else "N/A"
                platform_post_id = row[15] if len(row) > 15 and row[15] else "N/A"
                platform_url = row[16] if len(row) > 16 and row[16] else "N/A"
                
                print(f"記錄 {i}:")
                print(f"  貼文ID: {post_id}")
                print(f"  KOL: {kol_nickname} (Serial: {kol_serial})")
                print(f"  標題: {title}")
                print(f"  狀態: {status}")
                print(f"  發文時間: {publish_time}")
                print(f"  平台發文ID: {platform_post_id}")
                print(f"  平台URL: {platform_url}")
                print()
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_publish_results()
