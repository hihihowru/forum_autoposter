#!/usr/bin/env python3
"""
調試 KOL 帳號密碼
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def debug_kol_credentials():
    """調試 KOL 帳號密碼"""
    
    print("=== 調試 KOL 帳號密碼 ===\n")
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    try:
        # 讀取同學會帳號管理表
        data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        
        if not data:
            print("❌ 無法讀取同學會帳號管理表")
            return
        
        print("表頭:")
        headers = data[0]
        for i, header in enumerate(headers):
            print(f"  {i}: {header}")
        
        print(f"\n總共 {len(data)} 行數據")
        
        # 顯示前幾行數據
        print("\n前5行數據:")
        for i, row in enumerate(data[1:6], 1):
            print(f"\n第 {i} 行:")
            for j, cell in enumerate(row):
                if j < len(headers):
                    print(f"  {headers[j]}: {repr(cell)}")
        
        # 檢查特定 KOL 的帳號密碼
        print("\n檢查特定 KOL 的帳號密碼:")
        for i, row in enumerate(data[1:], 1):
            if len(row) >= 6:  # 確保有足夠的列
                serial = row[0] if row[0] else "N/A"
                nickname = row[1] if len(row) > 1 and row[1] else "N/A"
                status = row[9] if len(row) > 9 and row[9] else "N/A"
                email = row[5] if len(row) > 5 and row[5] else "N/A"
                password = row[6] if len(row) > 6 and row[6] else "N/A"
                
                if status == "active" and email and password:
                    print(f"  Serial {serial} ({nickname}):")
                    print(f"    Email: {repr(email)}")
                    print(f"    Password: {repr(password)}")
                    print(f"    Status: {status}")
                    print()
        
    except Exception as e:
        print(f"❌ 調試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_kol_credentials()
