#!/usr/bin/env python3
"""
Google API 認證問題修復工具
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def check_google_cloud_cli():
    """檢查是否安裝了 Google Cloud CLI"""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud CLI 已安裝")
            return True
        else:
            print("❌ Google Cloud CLI 未安裝或無法使用")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud CLI 未安裝")
        return False

def fix_google_api_issue():
    """修復 Google API 認證問題"""
    print("🔧 Google API 認證問題修復工具")
    print("=" * 60)
    
    print("\n📋 問題分析:")
    print("   - 憑證檔案格式正確")
    print("   - Service Account 認證創建成功")
    print("   - 但在實際 API 調用時出現 'Invalid JWT Signature' 錯誤")
    print("   - 這通常表示憑證已過期或權限不足")
    
    print("\n🛠️ 修復步驟:")
    
    # 步驟 1: 檢查 Google Cloud CLI
    print("\n1. 檢查 Google Cloud CLI...")
    if not check_google_cloud_cli():
        print("   請先安裝 Google Cloud CLI:")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    
    # 步驟 2: 重新生成憑證
    print("\n2. 重新生成 Service Account 憑證...")
    print("   請按照以下步驟操作:")
    print("   a) 前往 Google Cloud Console: https://console.cloud.google.com/")
    print("   b) 選擇專案: crested-timer-468207-k1")
    print("   c) 前往 IAM & Admin > Service Accounts")
    print("   d) 找到: n8n-migration-service@crested-timer-468207-k1.iam.gserviceaccount.com")
    print("   e) 點擊 > Keys > Add Key > Create new key > JSON")
    print("   f) 下載新的憑證檔案")
    print("   g) 替換 credentials/google-service-account.json")
    
    # 步驟 3: 檢查 Google Sheets 權限
    print("\n3. 檢查 Google Sheets 權限...")
    sheets_id = os.getenv('GOOGLE_SHEETS_ID', 'YOUR_SHEETS_ID')
    print(f"   a) 打開 Google Sheets: https://docs.google.com/spreadsheets/d/{sheets_id}/edit")
    print("   b) 點擊右上角「共用」按鈕")
    print("   c) 添加 Service Account email: n8n-migration-service@crested-timer-468207-k1.iam.gserviceaccount.com")
    print("   d) 設置權限為「編輯者」")
    print("   e) 點擊「完成」")
    
    # 步驟 4: 檢查 API 啟用狀態
    print("\n4. 檢查 Google Sheets API 啟用狀態...")
    print("   a) 前往 Google Cloud Console > APIs & Services > Library")
    print("   b) 搜尋「Google Sheets API」")
    print("   c) 確保已啟用（如果未啟用，點擊「啟用」）")
    
    # 步驟 5: 測試修復結果
    print("\n5. 測試修復結果...")
    print("   完成上述步驟後，運行以下命令測試:")
    print("   python3 diagnose_google_api.py")
    
    return True

def create_alternative_solution():
    """創建替代解決方案"""
    print("\n" + "=" * 60)
    print("🔄 替代解決方案")
    print("=" * 60)
    
    print("\n📝 方案 1: 使用 OAuth 2.0 用戶端憑證")
    print("   優點: 更安全，支援用戶授權")
    print("   缺點: 需要用戶手動授權")
    print("   適用: 需要用戶互動的應用")
    
    print("\n📝 方案 2: 使用 API Key")
    print("   優點: 簡單易用")
    print("   缺點: 僅限讀取權限，安全性較低")
    print("   適用: 僅需要讀取數據的場景")
    
    print("\n📝 方案 3: 手動更新（當前使用）")
    print("   優點: 不依賴 Google API，穩定可靠")
    print("   缺點: 需要手動操作")
    print("   適用: 數據量較小的場景")
    
    print("\n📝 方案 4: 使用 Google Apps Script")
    print("   優點: 直接在 Google Sheets 中運行")
    print("   缺點: 需要學習 Apps Script")
    print("   適用: 複雜的自動化需求")

def create_oauth_solution():
    """創建 OAuth 2.0 解決方案"""
    print("\n" + "=" * 60)
    print("🔐 OAuth 2.0 解決方案")
    print("=" * 60)
    
    oauth_code = '''
#!/usr/bin/env python3
"""
OAuth 2.0 Google Sheets 客戶端
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class OAuthGoogleSheetsClient:
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """OAuth 2.0 認證"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        
        # 檢查是否有已保存的憑證
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # 如果沒有有效憑證，則進行授權
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 保存憑證以供下次使用
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def read_sheet(self, sheet_name: str, range_name: str = None):
        """讀取工作表數據"""
        if range_name:
            range_str = f"{sheet_name}!{range_name}"
        else:
            range_str = sheet_name
        
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_str
        ).execute()
        
        return result.get('values', [])
    
    def write_sheet(self, sheet_name: str, values, range_name: str = None):
        """寫入工作表數據"""
        if range_name:
            range_str = f"{sheet_name}!{range_name}"
        else:
            range_str = sheet_name
        
        body = {'values': values}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_str,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return result
'''
    
    print("📄 OAuth 2.0 客戶端代碼:")
    print(oauth_code)
    
    print("\n📋 設置步驟:")
    print("1. 前往 Google Cloud Console > APIs & Services > Credentials")
    print("2. 點擊「Create Credentials」>「OAuth 2.0 Client IDs」")
    print("3. 選擇「Desktop application」")
    print("4. 下載 JSON 憑證檔案")
    print("5. 將檔案放到 credentials/oauth-client.json")
    print("6. 安裝依賴: pip install google-auth-oauthlib")
    print("7. 運行腳本，會打開瀏覽器進行授權")

if __name__ == "__main__":
    print("🔧 Google API 認證問題修復工具")
    print("=" * 60)
    
    # 執行修復
    fix_google_api_issue()
    
    # 提供替代方案
    create_alternative_solution()
    
    # 提供 OAuth 解決方案
    create_oauth_solution()
    
    print("\n" + "=" * 60)
    print("💡 建議:")
    print("1. 優先嘗試重新生成 Service Account 憑證")
    print("2. 如果問題持續，考慮使用 OAuth 2.0 方案")
    print("3. 對於簡單場景，可以繼續使用手動更新方案")
    print("=" * 60)



