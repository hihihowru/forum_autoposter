#!/usr/bin/env python3
"""
清空互動回饋工作表的模擬數據
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("🧹 清空互動回饋工作表的模擬數據:")
    print("-----------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    # 要清空的工作表列表
    sheets_to_clear = [
        "互動回饋_1hr",
        "互動回饋_1day", 
        "互動回饋_7days"
    ]
    
    try:
        for sheet_name in sheets_to_clear:
            print(f"📋 清空 {sheet_name} 工作表...")
            
            # 讀取標題行
            headers = sheets_client.read_sheet(sheet_name, 'A1:O1')
            if headers and len(headers) > 0:
                # 清空除標題行外的所有數據
                sheets_client.write_sheet(sheet_name, headers, f"A1:O1000")
                print(f"✅ {sheet_name} 已清空，保留標題行")
            else:
                print(f"⚠️ {sheet_name} 沒有找到標題行")
        
        print("\n🎉 所有互動回饋工作表已清空完成！")
        
    except Exception as e:
        print(f"❌ 清空失敗: {e}")

if __name__ == "__main__":
    main()










