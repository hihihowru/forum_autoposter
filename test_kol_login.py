#!/usr/bin/env python3
"""
測試 KOL 登入
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.publish.publish_service import PublishService

async def test_kol_login():
    """測試 KOL 登入"""
    
    print("=== 測試 KOL 登入 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    publish_service = PublishService(sheets_client)
    
    try:
        # 讀取 KOL 配置
        print("讀取 KOL 配置...")
        data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        
        if not data or len(data) < 2:
            print("❌ 無法讀取 KOL 配置")
            return
        
        headers = data[0]
        kol_data = data[1:]
        
        # 找到相關列的索引
        serial_idx = headers.index('序號') if '序號' in headers else 0
        email_idx = headers.index('Email(帳號)') if 'Email(帳號)' in headers else 5
        password_idx = headers.index('密碼') if '密碼' in headers else 6
        status_idx = headers.index('狀態') if '狀態' in headers else 9
        
        print(f"欄位索引: serial={serial_idx}, email={email_idx}, password={password_idx}, status={status_idx}")
        
        # 測試前3個活躍的 KOL
        test_count = 0
        for row in kol_data:
            if test_count >= 3:
                break
                
            if len(row) > max(serial_idx, email_idx, password_idx, status_idx):
                serial = int(row[serial_idx]) if row[serial_idx] else 0
                email = row[email_idx] if row[email_idx] else ''
                password = row[password_idx] if row[password_idx] else ''
                status = row[status_idx] if row[status_idx] else ''
                
                if serial > 0 and email and password and status == 'active':
                    print(f"\n測試 KOL {serial}:")
                    print(f"  Email: {email}")
                    print(f"  Password: {password[:3]}***")
                    print(f"  Status: {status}")
                    
                    # 測試登入
                    success = await publish_service.login_kol(serial, email, password)
                    if success:
                        print(f"  ✅ 登入成功")
                    else:
                        print(f"  ❌ 登入失敗")
                    
                    test_count += 1
        
        print(f"\n✅ KOL 登入測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kol_login())
