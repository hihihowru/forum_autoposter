#!/usr/bin/env python3
"""
將本地備份數據寫入 Google Sheets
"""
import asyncio
import json
import os
import glob
from src.clients.google.sheets_client import GoogleSheetsClient

async def upload_backup_to_sheets():
    """將備份數據上傳到 Google Sheets"""
    try:
        # 初始化 Google Sheets 客戶端
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        credentials_file = "./credentials/google-service-account.json"
        client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 找到所有備份文件
        backup_files = glob.glob("data/backup/post_record_*.json")
        backup_files.sort()  # 按時間排序
        
        print(f"找到 {len(backup_files)} 個備份文件")
        
        # 讀取每個備份文件並寫入 Google Sheets
        for i, file_path in enumerate(backup_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 將數據轉換為行格式
                row_data = []
                for key, value in data.items():
                    row_data.append(str(value))
                
                # 寫入 Google Sheets
                result = client.append_sheet('新貼文紀錄表', [row_data])
                
                print(f"✅ 第 {i+1}/{len(backup_files)} 個文件: {data.get('post_id', 'unknown')} -> {result}")
                
            except Exception as e:
                print(f"❌ 處理文件 {file_path} 失敗: {e}")
        
        print(f"🎉 完成！共處理 {len(backup_files)} 個文件")
        
    except Exception as e:
        print(f"❌ 上傳失敗: {e}")

if __name__ == "__main__":
    asyncio.run(upload_backup_to_sheets())



