#!/usr/bin/env python3
"""
獲取完整的 Google Sheets 欄位列表（包括所有欄位）
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.utils.config_manager import ConfigManager

def get_all_headers():
    """獲取完整的欄位列表（包括所有欄位）"""
    try:
        # 載入環境變數
        load_dotenv()
        
        # 創建 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="crested-timer-468207-k1-ea6b44e04eff.json",
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        # 讀取貼文紀錄表的完整標題行（使用更大的範圍）
        data = sheets_client.read_sheet('貼文紀錄表', 'A1:ZZ1')
        if data and len(data) > 0:
            headers = data[0]
            print("完整的貼文紀錄表欄位列表（所有欄位）:")
            print("headers = [")
            for i, header in enumerate(headers):
                print(f"    '{header}',")
            print("]")
            print(f"\n總共 {len(headers)} 個欄位")
            
            # 檢查空欄位
            empty_headers = [i for i, header in enumerate(headers) if not header or header.strip() == '']
            if empty_headers:
                print(f"空欄位位置: {empty_headers}")
            
            return headers
        else:
            print("無法讀取標題行")
            return None
            
    except Exception as e:
        print(f"❌ 獲取欄位列表失敗: {e}")
        return None

if __name__ == "__main__":
    get_all_headers()


