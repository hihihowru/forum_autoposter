#!/usr/bin/env python3
"""
檢查 Google Sheets 最後幾行的數據
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient

def check_last_rows():
    """檢查最後幾行的數據"""
    try:
        # 載入環境變數
        load_dotenv()
        
        # 創建 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="crested-timer-468207-k1-ea6b44e04eff.json",
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        # 讀取最後幾行數據
        data = sheets_client.read_sheet('貼文紀錄表')
        if data and len(data) > 0:
            print(f"總共 {len(data)} 行數據")
            
            # 檢查最後5行
            for i in range(min(5, len(data))):
                row = data[-(i+1)]
                print(f"\n第 {len(data)-i} 行 (共 {len(row)} 個欄位):")
                print(f"前10個欄位: {row[:10]}")
                print(f"後10個欄位: {row[-10:]}")
                
                # 檢查空欄位
                empty_count = sum(1 for cell in row if not cell or cell.strip() == '')
                print(f"空欄位數量: {empty_count}")
                
                # 檢查非空欄位
                non_empty_count = sum(1 for cell in row if cell and cell.strip() != '')
                print(f"非空欄位數量: {non_empty_count}")
                
        else:
            print("無法讀取數據")
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    check_last_rows()
