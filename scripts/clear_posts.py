#!/usr/bin/env python3
"""
清理Google Sheets中的現有貼文記錄
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    """清理Google Sheets中的現有貼文記錄"""
    
    try:
        # 初始化Google Sheets客戶端
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取貼文記錄表
        sheet_name = "貼文記錄表"
        existing_data = sheets_client.read_sheet(sheet_name)
        
        if not existing_data or len(existing_data) < 2:
            print("❌ 沒有數據需要清理")
            return
        
        # 保留標題行，刪除所有數據行
        headers = existing_data[0]
        
        print(f"📋 清理現有貼文記錄:")
        print(f"  📊 將刪除 {len(existing_data) - 1} 行數據")
        
        # 清空表格（只保留標題行）
        sheets_client.write_sheet(sheet_name, [headers], "A1:AM100")
        
        print("✅ 清理完成")
        
    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
