#!/usr/bin/env python3
"""
創建新的 Google Sheets 並更新配置
"""

import os
import asyncio
from dotenv import load_dotenv
from src.clients.google.sheets_client import GoogleSheetsClient

# 載入環境變數
load_dotenv()

async def create_new_sheets():
    """創建新的 Google Sheets"""
    try:
        print("🔄 創建新的 Google Sheets...")
        
        # 創建 Google Sheets 客戶端（不指定 spreadsheet_id，會創建新的）
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json'
        )
        
        # 創建新的 Google Sheets
        spreadsheet_id = sheets_client.create_spreadsheet("AIGC 工作記錄 - 新版本")
        print(f"✅ 成功創建新的 Google Sheets")
        print(f"📋 Sheets ID: {spreadsheet_id}")
        print(f"🔗 連結: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        
        # 創建「貼文紀錄表」分頁
        sheets_client.create_sheet("貼文紀錄表")
        print("✅ 成功創建「貼文紀錄表」分頁")
        
        # 創建「KOL 角色紀錄表」分頁
        sheets_client.create_sheet("KOL 角色紀錄表")
        print("✅ 成功創建「KOL 角色紀錄表」分頁")
        
        print()
        print("📝 請更新以下配置：")
        print(f"1. 更新 .env 文件中的 GOOGLE_SHEETS_ID: {spreadsheet_id}")
        print("2. 更新 src/core/main_workflow_engine.py 中的 new_sheets_id")
        print("3. 更新其他相關文件中的 Google Sheets ID")
        
        return spreadsheet_id
        
    except Exception as e:
        print(f"❌ 創建失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(create_new_sheets())
