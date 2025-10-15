#!/usr/bin/env python3
"""
創建新的 Google Sheets 來解決單元格限制問題
"""

import os
import sys
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils.config_manager import ConfigManager

def create_new_sheets():
    """創建新的 Google Sheets"""
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # 創建 Google Drive API 服務
        credentials = service_account.Credentials.from_service_account_file(
            config.google.credentials_file,
            scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        )
        
        drive_service = build('drive', 'v3', credentials=credentials)
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        # 創建新的 Google Sheets
        spreadsheet_name = f"貼文紀錄表_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 創建 Google Sheets 文件
        spreadsheet = {
            'properties': {
                'title': spreadsheet_name
            },
            'sheets': [
                {
                    'properties': {
                        'title': '貼文紀錄表',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26
                        }
                    }
                },
                {
                    'properties': {
                        'title': 'KOL 角色紀錄表',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26
                        }
                    }
                }
            ]
        }
        
        # 創建 spreadsheet
        created_spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        new_spreadsheet_id = created_spreadsheet['spreadsheetId']
        
        print(f"✅ 成功創建新的 Google Sheets")
        print(f"📋 名稱: {spreadsheet_name}")
        print(f"🆔 ID: {new_spreadsheet_id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}/edit")
        
        # 定義貼文紀錄表的標準欄位
        headers = [
            'test_post_id', 'test_time', 'test_status', 'trigger_type', 'status',
            'priority_level', 'batch_id', 'kol_serial', 'kol_nickname', 'kol_id',
            'persona', 'writing_style', 'tone', 'key_phrases', 'avoid_topics',
            'preferred_data_sources', 'kol_assignment_method', 'kol_weight', 'kol_version',
            'kol_learning_score', 'stock_id', 'stock_name', 'topic_category', 'analysis_type',
            'analysis_type_detail', 'topic_priority'
        ]
        
        # 寫入標題行
        body = {
            'values': [headers]
        }
        sheets_service.spreadsheets().values().update(
            spreadsheetId=new_spreadsheet_id,
            range='貼文紀錄表!A1:Z1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ 已創建貼文紀錄表並設置標題行")
        print(f"📊 欄位數量: {len(headers)}")
        
        # 定義 KOL 角色紀錄表的標準欄位
        kol_headers = [
            '序號', '暱稱', '認領人', '人設', 'MemberId', 'Email(帳號)', '密碼', '加白名單', '備註', '狀態', 
            '內容類型', '發文時間', '目標受眾', '互動閾值', '常用詞彙', '口語化用詞', '語氣風格', 
            '常用打字習慣', '前導故事', '專長領域', '數據源', '創建時間', '最後更新', '熱門話題', 
            'Topic偏好類別', '禁講類別'
        ]
        
        # 寫入標題行
        body = {
            'values': [kol_headers]
        }
        sheets_service.spreadsheets().values().update(
            spreadsheetId=new_spreadsheet_id,
            range='KOL 角色紀錄表!A1:Z1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ 已創建 KOL 角色紀錄表並設置標題行")
        print(f"📊 欄位數量: {len(kol_headers)}")
        
        # 保存新的 Google Sheets ID 到環境變數或配置文件
        print(f"\n📝 請更新以下配置：")
        print(f"1. 更新 .env 文件中的 GOOGLE_SHEETS_ID: {new_spreadsheet_id}")
        print(f"2. 更新主工作流程引擎中的 new_sheets_id: {new_spreadsheet_id}")
        
        return new_spreadsheet_id
        
    except Exception as e:
        print(f"❌ 創建新的 Google Sheets 失敗: {e}")
        return None

if __name__ == "__main__":
    create_new_sheets()
