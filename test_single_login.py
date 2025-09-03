#!/usr/bin/env python3
"""
測試單個 KOL 登入
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

async def test_single_login():
    """測試單個 KOL 登入"""
    
    print("=== 測試單個 KOL 登入 ===\n")
    
    # 初始化 CMoney 客戶端
    cmoney_client = CMoneyClient()
    
    # 測試川川哥的登入
    test_credentials = LoginCredentials(
        email="forum_200@cmoney.com.tw",
        password="N9t1kY3x"
    )
    
    print(f"測試登入: {test_credentials.email}")
    print(f"密碼: {test_credentials.password}")
    
    try:
        result = await cmoney_client.login(test_credentials)
        
        print(f"✅ 登入成功!")
        print(f"Access Token: {result.token[:20]}...")
        print(f"Expires At: {result.expires_at}")
        print(f"Is Expired: {result.is_expired}")
            
    except Exception as e:
        print(f"❌ 登入失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_login())
