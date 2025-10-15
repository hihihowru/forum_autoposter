#!/usr/bin/env python3
"""
檢查 Google Sheets 狀態
"""

import os
import asyncio
from dotenv import load_dotenv
from src.clients.google.sheets_client import GoogleSheetsClient

# 載入環境變數
load_dotenv()

async def check_google_sheets_status():
    """檢查 Google Sheets 狀態"""
    try:
        # 使用新的 Google Sheets ID
        sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # 創建 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id=sheets_id
        )
        
        print("🔍 檢查 Google Sheets 狀態...")
        print(f"📋 Sheets ID: {sheets_id}")
        print()
        
        # 檢查工作表資訊
        try:
            sheet_info = sheets_client.get_sheet_info()
            print("✅ 成功獲取工作表資訊")
            print(f"📄 工作表名稱: {sheet_info.get('properties', {}).get('title', 'Unknown')}")
            
            # 列出所有工作表
            sheets = sheet_info.get('sheets', [])
            print(f"📊 工作表數量: {len(sheets)}")
            for sheet in sheets:
                sheet_name = sheet.get('properties', {}).get('title', 'Unknown')
                print(f"   - {sheet_name}")
            
        except Exception as e:
            print(f"❌ 獲取工作表資訊失敗: {e}")
        
        print()
        
        # 檢查「貼文紀錄表」分頁
        try:
            data = sheets_client.read_sheet('貼文紀錄表')
            print("✅ 成功讀取「貼文紀錄表」")
            print(f"📊 數據行數: {len(data)}")
            
            if len(data) > 0:
                print(f"📋 第一行欄位數: {len(data[0])}")
                print(f"📋 第一行內容: {data[0][:5]}...")  # 只顯示前5個欄位
                
                if len(data) > 1:
                    print(f"📋 第二行欄位數: {len(data[1])}")
                    print(f"📋 第二行內容: {data[1][:5]}...")  # 只顯示前5個欄位
            else:
                print("📋 工作表為空")
                
        except Exception as e:
            print(f"❌ 讀取「貼文紀錄表」失敗: {e}")
        
        print()
        
        # 嘗試寫入測試數據
        try:
            test_headers = ['test_post_id', 'test_time', 'test_status']
            test_data = ['test_001', '2025-09-04T10:20:00', 'test']
            
            print("🧪 測試寫入數據...")
            sheets_client.write_sheet('貼文紀錄表', [test_headers], 'A1')
            print("✅ 測試標題寫入成功")
            
            sheets_client.append_sheet('貼文紀錄表', [test_data])
            print("✅ 測試數據追加成功")
            
        except Exception as e:
            print(f"❌ 測試寫入失敗: {e}")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_google_sheets_status())
