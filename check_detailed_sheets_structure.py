#!/usr/bin/env python3
"""
詳細檢查 Google Sheets 結構
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.utils.config_manager import ConfigManager

def check_detailed_sheets_structure():
    """詳細檢查 Google Sheets 結構"""
    try:
        # 載入環境變數
        load_dotenv()
        
        # 初始化配置管理器
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # 創建 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="crested-timer-468207-k1-ea6b44e04eff.json",
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        print("📋 詳細檢查Google Sheets工作表結構...")
        print(f"Spreadsheet ID: {sheets_client.spreadsheet_id}")
        
        # 獲取工作表資訊
        sheet_info = sheets_client.get_sheet_info()
        sheets = sheet_info.get('sheets', [])
        print(f"工作表數量: {len(sheets)}")
        
        for sheet in sheets:
            sheet_properties = sheet.get('properties', {})
            sheet_title = sheet_properties.get('title', 'Unknown')
            grid_properties = sheet_properties.get('gridProperties', {})
            column_count = grid_properties.get('columnCount', 0)
            row_count = grid_properties.get('rowCount', 0)
            
            print(f"\n📊 工作表: {sheet_title}")
            print(f"欄位數: {column_count}")
            print(f"行數: {row_count}")
            
            # 讀取前幾行來查看實際欄位
            try:
                # 讀取更大的範圍來查看所有欄位
                data = sheets_client.read_sheet(sheet_title, 'A1:BZ1')
                if data and len(data) > 0:
                    headers = data[0]
                    print(f"實際欄位數: {len(headers)}")
                    print("前30個欄位:")
                    for i, header in enumerate(headers[:30]):
                        print(f"  {i+1}. {header}")
                    
                    if len(headers) > 30:
                        print(f"  ... 還有 {len(headers) - 30} 個欄位")
                        
                    # 檢查是否有空欄位
                    empty_headers = [i for i, header in enumerate(headers) if not header or header.strip() == '']
                    if empty_headers:
                        print(f"空欄位位置: {empty_headers}")
                        
                else:
                    print("無法讀取標題行")
                    
            except Exception as e:
                print(f"讀取 {sheet_title} 失敗: {e}")
                
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    check_detailed_sheets_structure()


