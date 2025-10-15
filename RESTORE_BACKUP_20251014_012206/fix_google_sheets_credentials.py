#!/usr/bin/env python3
"""
Google Sheets 憑證修復腳本
重新設置 Google Service Account 憑證
"""

import os
import json
from pathlib import Path

def create_google_credentials_guide():
    """創建 Google 憑證設置指南"""
    print("🔧 Google Sheets 憑證修復指南")
    print("=" * 60)
    
    # 檢查憑證目錄
    credentials_dir = Path("./credentials")
    if not credentials_dir.exists():
        credentials_dir.mkdir(parents=True)
        print("✅ 創建憑證目錄: ./credentials/")
    
    # 檢查憑證文件
    credentials_file = credentials_dir / "google-service-account.json"
    
    if credentials_file.exists():
        print("✅ Google Service Account 憑證文件已存在")
        return True
    else:
        print("❌ Google Service Account 憑證文件不存在")
        print()
        print("📋 請按照以下步驟設置 Google Sheets 憑證：")
        print()
        print("1. 前往 Google Cloud Console:")
        print("   https://console.cloud.google.com/iam-admin/serviceaccounts")
        print()
        print("2. 選擇或創建專案")
        print()
        print("3. 創建新的 Service Account:")
        print("   - 名稱: n8n-migration-service")
        print("   - 描述: AIGC 工作記錄系統")
        print()
        print("4. 為 Service Account 添加權限:")
        print("   - Google Sheets API")
        print("   - Google Drive API")
        print()
        print("5. 創建並下載 JSON 金鑰:")
        print("   - 點擊 Service Account")
        print("   - 前往 'Keys' 標籤")
        print("   - 點擊 'Add Key' > 'Create new key'")
        print("   - 選擇 JSON 格式")
        print("   - 下載到本地")
        print()
        print("6. 將下載的 JSON 文件重命名並移動到:")
        print(f"   {credentials_file}")
        print()
        print("7. 確保 Google Sheets 已分享給 Service Account:")
        print("   - 打開 Google Sheets: 請使用環境變數中的 GOOGLE_SHEETS_ID")
        print("   - 點擊 'Share' 按鈕")
        print("   - 添加 Service Account 的 Email (格式: n8n-migration-service@project-id.iam.gserviceaccount.com)")
        print("   - 權限設為 'Editor'")
        print()
        
        return False

def create_mock_credentials_for_testing():
    """創建測試用的模擬憑證文件"""
    print("🧪 創建測試用模擬憑證文件")
    print("=" * 40)
    
    credentials_dir = Path("./credentials")
    credentials_file = credentials_dir / "google-service-account.json"
    
    # 模擬憑證結構（僅供測試，實際使用需要真實憑證）
    mock_credentials = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY_FOR_TESTING\n-----END PRIVATE KEY-----\n",
        "client_email": "test-service@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-service%40test-project.iam.gserviceaccount.com"
    }
    
    try:
        with open(credentials_file, 'w') as f:
            json.dump(mock_credentials, f, indent=2)
        
        print(f"✅ 已創建模擬憑證文件: {credentials_file}")
        print("⚠️  注意：這是模擬憑證，僅供測試使用")
        print("   實際運行時需要真實的 Google Service Account 憑證")
        
        return True
        
    except Exception as e:
        print(f"❌ 創建模擬憑證失敗: {e}")
        return False

def test_google_sheets_connection():
    """測試 Google Sheets 連接"""
    print("🔗 測試 Google Sheets 連接")
    print("=" * 40)
    
    credentials_file = "./credentials/google-service-account.json"
    
    if not os.path.exists(credentials_file):
        print("❌ 憑證文件不存在，無法測試連接")
        return False
    
    try:
        from src.clients.google.sheets_client import GoogleSheetsClient
        
        sheets_client = GoogleSheetsClient(
            credentials_file=credentials_file,
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        # 測試讀取
        sheet_data = sheets_client.read_sheet('貼文紀錄表', 'A1:Z1')
        
        if sheet_data and len(sheet_data) > 0:
            print("✅ Google Sheets 連接成功")
            print(f"   貼文紀錄表欄位數: {len(sheet_data[0])}")
            return True
        else:
            print("❌ Google Sheets 連接失敗：無法讀取數據")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets 連接測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔧 Google Sheets 憑證修復工具")
    print("=" * 60)
    
    # 1. 檢查並創建憑證目錄
    create_google_credentials_guide()
    
    # 2. 詢問是否創建模擬憑證進行測試
    print()
    response = input("是否要創建模擬憑證進行測試？(y/n): ").strip().lower()
    
    if response == 'y':
        if create_mock_credentials_for_testing():
            print()
            print("🧪 現在可以進行測試，但實際運行時需要真實憑證")
        else:
            print("❌ 創建模擬憑證失敗")
    else:
        print("📋 請按照上述指南設置真實的 Google Service Account 憑證")
    
    print()
    print("=" * 60)
    print("📋 設置完成後，請重新運行數據檢查腳本")
    print("   python3 data_check_after_hours_limit_up.py")

if __name__ == "__main__":
    main()
