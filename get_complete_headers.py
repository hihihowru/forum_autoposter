#!/usr/bin/env python3
"""
獲取完整的 Google Sheets 欄位列表
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.utils.config_manager import ConfigManager

def get_complete_headers():
    """獲取完整的欄位列表"""
    try:
        # 載入環境變數
        load_dotenv()
        
        # 創建 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="crested-timer-468207-k1-ea6b44e04eff.json",
            spreadsheet_id="1R_nBesf62hX5dQEr_SDjHrGefAC9nsOo1Kbih79EHKw"
        )
        
        # 讀取貼文紀錄表的完整標題行
        data = sheets_client.read_sheet('貼文紀錄表', 'A1:BZ1')
        if data and len(data) > 0:
            headers = data[0]
            print("完整的貼文紀錄表欄位列表:")
            print("headers = [")
            for i, header in enumerate(headers):
                print(f"    '{header}',")
            print("]")
            print(f"\n總共 {len(headers)} 個欄位")
            return headers
        else:
            print("無法讀取標題行")
            return None
            
    except Exception as e:
        print(f"❌ 獲取欄位列表失敗: {e}")
        return None

if __name__ == "__main__":
    get_complete_headers()


