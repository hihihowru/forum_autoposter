#!/usr/bin/env python3
"""
手動添加股票提及欄位到KOL角色紀錄表
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient

load_dotenv()

def add_stock_mention_columns_manually():
    """手動添加股票提及欄位"""
    try:
        sheets_client = GoogleSheetsClient(
            credentials_file='./credentials/google-service-account.json',
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        print("📋 手動添加股票提及欄位...")
        
        # 讀取現有數據
        data = sheets_client.read_sheet('KOL 角色紀錄表', 'A:Z')
        if not data or len(data) < 1:
            print("❌ 無法讀取數據")
            return False
        
        headers = data[0]
        rows = data[1:]
        
        print(f"當前欄位數: {len(headers)}")
        print(f"當前欄位: {headers}")
        
        # 需要添加的欄位
        new_columns = [
            '股票提及主要格式',
            '股票提及次要格式', 
            '股票提及頻率權重',
            '股票提及上下文修飾'
        ]
        
        # 檢查哪些欄位需要添加
        missing_columns = []
        for col in new_columns:
            if col not in headers:
                missing_columns.append(col)
        
        if not missing_columns:
            print("✅ 所有股票提及欄位已存在")
            return True
        
        print(f"需要添加的欄位: {missing_columns}")
        
        # 為每一行添加空欄位
        updated_data = []
        for row in rows:
            new_row = row.copy()
            for _ in missing_columns:
                new_row.append("")
            updated_data.append(new_row)
        
        # 更新表頭
        updated_headers = headers + missing_columns
        
        print(f"更新後欄位數: {len(updated_headers)}")
        print(f"更新後欄位: {updated_headers}")
        
        # 寫入表頭
        sheets_client.write_sheet('KOL 角色紀錄表', [updated_headers], 'A1:AD1')
        print("✅ 表頭寫入完成")
        
        # 寫入數據行
        if updated_data:
            sheets_client.write_sheet('KOL 角色紀錄表', updated_data, 'A2:AD' + str(len(updated_data) + 1))
            print("✅ 數據行寫入完成")
        
        print("✅ 手動添加欄位完成")
        return True
        
    except Exception as e:
        print(f"❌ 手動添加欄位失敗: {e}")
        return False

if __name__ == "__main__":
    add_stock_mention_columns_manually()
