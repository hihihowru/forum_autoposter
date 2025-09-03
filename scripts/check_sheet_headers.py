#!/usr/bin/env python3
"""
檢查Google Sheets的欄位名稱
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient
import os

def main():
    """檢查Google Sheets的欄位名稱"""
    
    try:
        # 初始化Google Sheets客戶端
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取貼文記錄表
        sheet_name = "貼文記錄表"
        existing_data = sheets_client.read_sheet(sheet_name)
        
        if not existing_data:
            print("❌ 無法讀取Google Sheets")
            return
        
        # 獲取標題行
        headers = existing_data[0] if existing_data else []
        if not headers:
            print("❌ 無法獲取標題行")
            return
        
        print(f"📋 檢測到 {len(headers)} 個欄位:")
        print("-" * 50)
        
        for i, header in enumerate(headers, 1):
            print(f"{i:2d}. {header}")
        
        print("-" * 50)
        print(f"總共 {len(headers)} 個欄位")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
