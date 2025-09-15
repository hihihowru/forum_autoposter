#!/usr/bin/env python3
"""
檢查更新後的KOL角色紀錄表
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient

load_dotenv()

def check_updated_sheet():
    """檢查更新後的KOL角色紀錄表"""
    try:
        sheets_client = GoogleSheetsClient(
            credentials_file='./credentials/google-service-account.json',
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        print("📋 檢查更新後的KOL角色紀錄表...")
        
        # 讀取表頭
        data = sheets_client.read_sheet('KOL 角色紀錄表', 'A1:Z1')
        if data and len(data) > 0:
            headers = data[0]
            print(f"欄位數: {len(headers)}")
            print(f"欄位: {headers}")
            
            # 檢查股票提及欄位
            stock_mention_columns = ['股票提及主要格式', '股票提及次要格式', '股票提及頻率權重', '股票提及上下文修飾']
            for col in stock_mention_columns:
                if col in headers:
                    index = headers.index(col)
                    print(f"✅ {col} 在位置 {index}")
                else:
                    print(f"❌ {col} 不存在")
        else:
            print("❌ 無法讀取表頭")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    check_updated_sheet()
