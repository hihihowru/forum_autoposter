#!/usr/bin/env python3
"""
檢查可用的工作表名稱
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📋 檢查可用的工作表名稱:")
    print("-----------------------------------------")
    print("---------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 獲取工作表資訊
        sheet_info = sheets_client.get_sheet_info()
        
        print(f"📊 檢測到 {len(sheet_info.get('sheets', []))} 個工作表:")
        for i, sheet in enumerate(sheet_info.get('sheets', []), 1):
            sheet_name = sheet['properties']['title']
            print(f"  {i}. {sheet_name}")
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    main()
