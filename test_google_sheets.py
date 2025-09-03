#!/usr/bin/env python3
"""
Google Sheets API 連接測試腳本
"""
import os
import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.google.sheets_client import test_connection

if __name__ == "__main__":
    print("開始測試 Google Sheets API 連接...")
    print("=" * 50)
    
    # 檢查憑證檔案是否存在
    credentials_file = "./credentials/google-service-account.json"
    if not os.path.exists(credentials_file):
        print(f"❌ 憑證檔案不存在: {credentials_file}")
        print("請按照以下步驟設置 Google Sheets API 權限:")
        print("1. 前往 Google Cloud Console")
        print("2. 創建 Service Account")
        print("3. 下載 JSON 憑證檔案")
        print("4. 將檔案放到 credentials/ 目錄")
        print("5. 將 Service Account email 加入 Google Sheets 編輯權限")
        sys.exit(1)
    
    # 測試連接
    success = test_connection()
    
    if success:
        print("=" * 50)
        print("✅ Google Sheets API 連接測試成功！")
        print("可以開始使用 Google Sheets 整合功能")
    else:
        print("=" * 50)
        print("❌ Google Sheets API 連接測試失敗！")
        print("請檢查:")
        print("1. 憑證檔案是否正確")
        print("2. Service Account 是否有 Google Sheets 編輯權限")
        print("3. Google Sheets 文件 ID 是否正確")
        sys.exit(1)
