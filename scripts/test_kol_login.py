#!/usr/bin/env python3
"""
測試 KOL 登入和 token 獲取
"""

import sys
import os
import asyncio

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def test_kol_login():
    print("🔐 測試 KOL 登入和 token 獲取:")
    print("-----------------------------------------")
    print("---------------------------------------")
    print()
    
    # 初始化 CMoney 客戶端
    cmoney_client = CMoneyClient()
    
    try:
        # 測試梅川褲子的登入
        credentials = LoginCredentials(
            email="forum_202@cmoney.com.tw",
            password="x2U9nW5p"
        )
        
        print(f"📧 測試帳號: {credentials.email}")
        print(f"🔑 密碼: {credentials.password}")
        print()
        
        # 登入
        print("🔄 正在登入...")
        access_token_obj = await cmoney_client.login(credentials)
        
        if access_token_obj:
            print("✅ 登入成功!")
            print(f"  📝 Token: {access_token_obj.token[:20]}...")
            print(f"  ⏰ 過期時間: {access_token_obj.expires_at}")
            print(f"  🔍 Token 長度: {len(access_token_obj.token)}")
            print()
            
            # 測試發文 API（不實際發文，只測試 token 是否有效）
            print("🔄 測試發文 API 連接...")
            
            # 準備測試文章數據
            from src.clients.cmoney.cmoney_client import ArticleData
            
            test_article = ArticleData(
                title="測試標題",
                text="測試內容",
                commodity_tags=[
                    {"type": "Stock", "key": "2330", "bullOrBear": 0}
                ]
            )
            
            # 嘗試發文
            publish_result = await cmoney_client.publish_article(access_token_obj.token, test_article)
            
            if publish_result.success:
                print("✅ 發文 API 測試成功!")
                print(f"  📝 Article ID: {publish_result.post_id}")
                print(f"  🔗 URL: {publish_result.post_url}")
            else:
                print("❌ 發文 API 測試失敗:")
                print(f"  📝 錯誤: {publish_result.error_message}")
                
        else:
            print("❌ 登入失敗")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kol_login())
