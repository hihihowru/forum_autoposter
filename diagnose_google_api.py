#!/usr/bin/env python3
"""
Google API 認證問題診斷工具
"""

import os
import sys
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def diagnose_google_api_issue():
    """診斷 Google API 認證問題"""
    print("🔍 Google API 認證問題診斷")
    print("=" * 60)
    
    # 1. 檢查憑證檔案
    print("1. 檢查憑證檔案...")
    credentials_file = "./credentials/google-service-account.json"
    
    if not os.path.exists(credentials_file):
        print("❌ 憑證檔案不存在")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            cred_data = json.load(f)
        
        print("✅ 憑證檔案存在且格式正確")
        print(f"   Project ID: {cred_data.get('project_id')}")
        print(f"   Client Email: {cred_data.get('client_email')}")
        print(f"   Private Key 長度: {len(cred_data.get('private_key', ''))}")
        
        # 檢查必要欄位
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if not cred_data.get(field)]
        
        if missing_fields:
            print(f"❌ 缺少必要欄位: {missing_fields}")
            return False
        else:
            print("✅ 所有必要欄位都存在")
            
    except json.JSONDecodeError as e:
        print(f"❌ 憑證檔案 JSON 格式錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 讀取憑證檔案失敗: {e}")
        return False
    
    # 2. 測試認證
    print("\n2. 測試認證...")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print("✅ Service Account 認證創建成功")
        
        # 3. 測試 API 連接
        print("\n3. 測試 API 連接...")
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Google Sheets API 服務創建成功")
        
        # 4. 測試讀取權限
        print("\n4. 測試讀取權限...")
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        try:
            # 先測試獲取文件資訊
            result = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            print("✅ 成功獲取 Google Sheets 文件資訊")
            print(f"   文件標題: {result.get('properties', {}).get('title', 'Unknown')}")
            print(f"   工作表數量: {len(result.get('sheets', []))}")
            
            # 列出工作表
            sheets = result.get('sheets', [])
            print("   工作表列表:")
            for sheet in sheets:
                sheet_title = sheet.get('properties', {}).get('title', 'Unknown')
                print(f"     - {sheet_title}")
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else {}
            print(f"❌ 讀取 Google Sheets 失敗: {e}")
            print(f"   錯誤詳情: {error_details}")
            
            # 分析錯誤類型
            if "notFound" in str(e):
                print("   💡 可能原因: Google Sheets 文件 ID 不正確或文件不存在")
            elif "forbidden" in str(e):
                print("   💡 可能原因: Service Account 沒有存取權限")
            elif "invalid_grant" in str(e):
                print("   💡 可能原因: 憑證過期或權限不足")
            
            return False
        
        # 5. 測試讀取特定工作表
        print("\n5. 測試讀取特定工作表...")
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='同學會帳號管理!A1:Z1'
            ).execute()
            
            values = result.get('values', [])
            if values:
                print("✅ 成功讀取「同學會帳號管理」工作表")
                print(f"   標題行欄位數: {len(values[0])}")
            else:
                print("⚠️ 工作表為空")
                
        except HttpError as e:
            print(f"❌ 讀取「同學會帳號管理」工作表失敗: {e}")
            return False
        
        print("\n✅ 所有測試通過！Google API 認證正常")
        return True
        
    except Exception as e:
        print(f"❌ 認證測試失敗: {e}")
        return False

def provide_solutions():
    """提供解決方案"""
    print("\n" + "=" * 60)
    print("🔧 Google API 認證問題解決方案")
    print("=" * 60)
    
    print("\n1. 重新生成 Service Account 憑證:")
    print("   a) 前往 Google Cloud Console")
    print("   b) 選擇專案: crested-timer-468207-k1")
    print("   c) 前往 IAM & Admin > Service Accounts")
    print("   d) 找到: n8n-migration-service@crested-timer-468207-k1.iam.gserviceaccount.com")
    print("   e) 點擊 > Keys > Add Key > Create new key > JSON")
    print("   f) 下載並替換 credentials/google-service-account.json")
    
    print("\n2. 檢查 Google Sheets 權限:")
    sheets_id = os.getenv('GOOGLE_SHEETS_ID', 'YOUR_SHEETS_ID')
    print(f"   a) 打開 Google Sheets: https://docs.google.com/spreadsheets/d/{sheets_id}/edit")
    print("   b) 點擊右上角「共用」按鈕")
    print("   c) 添加 Service Account email: n8n-migration-service@crested-timer-468207-k1.iam.gserviceaccount.com")
    print("   d) 設置權限為「編輯者」")
    
    print("\n3. 檢查 Google Cloud 專案設定:")
    print("   a) 確保 Google Sheets API 已啟用")
    print("   b) 檢查 Service Account 是否有適當的角色")
    print("   c) 確認專案計費狀態正常")
    
    print("\n4. 替代解決方案:")
    print("   a) 使用 OAuth 2.0 用戶端憑證（需要用戶授權）")
    print("   b) 使用 API Key（僅限讀取權限）")
    print("   c) 手動更新數據（當前使用的方法）")

if __name__ == "__main__":
    success = diagnose_google_api_issue()
    if not success:
        provide_solutions()


