#!/usr/bin/env python3
"""
顯示 KOL 實際密碼（僅用於測試）
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("🔐 顯示 KOL 實際密碼:")
    print("-----------------------------------------")
    print("---------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 讀取同學會帳號管理
        kol_data = sheets_client.read_sheet("同學會帳號管理")
        
        if len(kol_data) <= 1:
            print("❌ 沒有找到 KOL 數據")
            return
        
        headers = kol_data[0]
        
        # 查找關鍵欄位
        serial_index = None
        email_index = None
        password_index = None
        nickname_index = None
        
        for i, header in enumerate(headers):
            if header == "序號":
                serial_index = i
            elif header == "Email(帳號)":
                email_index = i
            elif header == "密碼":
                password_index = i
            elif header == "暱稱":
                nickname_index = i
        
        print(f"📊 KOL 列表（顯示實際密碼）:")
        for i, row in enumerate(kol_data[1:], 1):
            if len(row) > max(serial_index or 0, email_index or 0, password_index or 0, nickname_index or 0):
                serial = row[serial_index] if serial_index is not None else "N/A"
                nickname = row[nickname_index] if nickname_index is not None else "N/A"
                email = row[email_index] if email_index is not None else "N/A"
                password = row[password_index] if password_index is not None else "N/A"
                
                print(f"  {i}. {nickname} (序號: {serial})")
                print(f"     📧 Email: {email}")
                print(f"     🔑 Password: {password}")
                print()
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    main()
























