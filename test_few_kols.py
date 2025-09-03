#!/usr/bin/env python3
"""
測試前幾個 KOL 的登入
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.publish.publish_service import PublishService
from src.clients.google.sheets_client import GoogleSheetsClient

async def test_few_kols():
    """測試前幾個 KOL 的登入"""
    
    print("=== 測試前幾個 KOL 登入 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    publish_service = PublishService(sheets_client)
    
    # 測試前3個 KOL
    test_kols = [
        {"serial": 200, "email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
        {"serial": 201, "email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
        {"serial": 202, "email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"}
    ]
    
    success_count = 0
    
    for kol in test_kols:
        print(f"測試 KOL {kol['serial']} ({kol['email']})...")
        try:
            success = await publish_service.login_kol(kol['serial'], kol['email'], kol['password'])
            if success:
                print(f"✅ KOL {kol['serial']} 登入成功")
                success_count += 1
            else:
                print(f"❌ KOL {kol['serial']} 登入失敗")
        except Exception as e:
            print(f"❌ KOL {kol['serial']} 登入異常: {e}")
        print()
    
    print(f"登入結果: {success_count}/{len(test_kols)} 成功")
    
    if success_count > 0:
        print("\n✅ 有 KOL 登入成功，可以繼續發文測試")
    else:
        print("\n❌ 沒有 KOL 登入成功")

if __name__ == "__main__":
    asyncio.run(test_few_kols())
