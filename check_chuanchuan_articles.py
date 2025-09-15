#!/usr/bin/env python3
"""
檢查並清理川川哥的重複文章
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def main():
    """主執行函數"""
    print("🔍 檢查川川哥的文章狀態...")
    
    try:
        print("📋 步驟 1: 初始化CMoney客戶端...")
        cmoney_client = CMoneyClient()
        print("✅ CMoney 客戶端初始化成功")
        
        print("📋 步驟 2: 登入川川哥帳號...")
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password=os.getenv('CMONEY_PASSWORD')
        )
        
        token = await cmoney_client.login(credentials)
        print(f"✅ 川川哥登入成功: {token.token[:20]}...")
        
        print("📋 步驟 3: 檢查當前文章狀態...")
        
        # 檢查最新的文章（我們剛才發的）
        latest_article_id = '173502031'
        print(f"🔍 檢查最新文章 {latest_article_id}...")
        
        try:
            # 嘗試獲取文章詳情
            article_info = await cmoney_client.get_article_details(token.token, latest_article_id)
            if article_info:
                print(f"✅ 最新文章存在: {article_info.get('title', '無標題')}")
            else:
                print(f"❌ 最新文章不存在或無法訪問")
        except Exception as e:
            print(f"⚠️ 無法檢查文章詳情: {e}")
        
        print("\n📋 步驟 4: 總結當前狀態...")
        print("🔗 川川哥頁面: https://www.cmoney.tw/forum/user/9505546")
        print("🔗 最新文章: https://www.cmoney.tw/forum/article/173502031")
        
        print("\n📋 步驟 5: 建議的清理策略...")
        print("1. 手動檢查川川哥頁面，確認重複文章是否還在")
        print("2. 如果重複文章還在，可能需要手動刪除")
        print("3. 未來發文時，確保每個KOL使用對應的帳號")
        print("4. 建立發文前的檢查機制，避免重複發文")
        
        print(f"\n📅 檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


