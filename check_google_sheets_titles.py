#!/usr/bin/env python3
"""
檢查 Google Sheets 中的標題欄位
查看雷虎的標題為什麼顯示為 "標題"
"""

import asyncio
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def check_google_sheets_titles():
    """檢查 Google Sheets 中的標題"""
    try:
        from src.clients.google.sheets_client import GoogleSheetsClient
        
        # 讀取貼文紀錄表
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        if not spreadsheet_id:
            raise ValueError("請設定 GOOGLE_SHEETS_ID 環境變數")
        sheet_name = "貼文紀錄表"  # 使用正確的工作表名稱
        
        # 初始化 Google Sheets 客戶端
        credentials_file = "credentials/google-service-account.json"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 先列出所有工作表
        sheets = sheets_client.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        print("📊 可用的工作表:")
        for sheet in sheets['sheets']:
            print(f"   - {sheet['properties']['title']}")
        print("-" * 40)
        
        # 讀取數據
        data = sheets_client.read_sheet(sheet_name)
        
        if not data or len(data) < 2:
            print("❌ 沒有找到數據")
            return
        
        # 找到標題欄位的索引
        headers = data[0]
        title_index = None
        content_index = None
        stock_id_index = None
        
        print("📊 所有欄位標題:")
        for i, header in enumerate(headers):
            print(f"   {i}: {header}")
            if "標題" in header:
                title_index = i
            elif "內容" in header:
                content_index = i
            elif "股票代號" in header:
                stock_id_index = i
        
        print("🧪 檢查 Google Sheets 標題欄位")
        print("="*60)
        print(f"📊 標題欄位索引: {title_index}")
        print(f"📄 內容欄位索引: {content_index}")
        print(f"📈 股票代號欄位索引: {stock_id_index}")
        print("-" * 40)
        
        # 檢查最近的幾行數據
        print("📊 檢查所有包含數據的行:")
        for i, row in enumerate(data[1:], 1):
            if len(row) > 4 and row[4]:  # 有股票代號的行
                stock_id = row[4]
                title = row[8] if len(row) > 8 else ""
                content = row[9] if len(row) > 9 else ""
                
                print(f"📊 第 {i+1} 行:")
                print(f"   股票代號: {stock_id}")
                print(f"   標題: '{title}'")
                print(f"   內容長度: {len(content)} 字")
                if content:
                    print(f"   內容預覽: {content[:100]}...")
                print("-" * 20)
                
                # 只顯示前20行有數據的
                if i >= 20:
                    break
        
        # 特別檢查雷虎的數據
        print("\n🔍 特別檢查雷虎 (8033) 的數據:")
        for i, row in enumerate(data[1:], 1):
            if len(row) > (stock_id_index or 0) and stock_id_index is not None and row[stock_id_index] == "8033":
                title = row[title_index] if title_index is not None else "N/A"
                content = row[content_index] if content_index is not None else "N/A"
                print(f"📊 雷虎數據 (第 {i+1} 行):")
                print(f"   標題: '{title}'")
                print(f"   內容長度: {len(content)} 字")
                if content:
                    print(f"   內容預覽: {content[:100]}...")
                break
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    asyncio.run(check_google_sheets_titles())
