#!/usr/bin/env python3
"""
詳細測試發文過程
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

async def test_detailed_publish():
    """詳細測試發文過程"""
    
    print("=== 詳細測試發文過程 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    publish_service = PublishService(sheets_client)
    
    try:
        # 步驟1: 登入川川哥
        print("步驟1: 登入川川哥...")
        success = await publish_service.login_kol(200, "forum_200@cmoney.com.tw", "N9t1kY3x")
        if not success:
            print("❌ 川川哥登入失敗")
            return
        print("✅ 川川哥登入成功")
        
        # 步驟2: 獲取準備發文的記錄
        print("\n步驟2: 獲取準備發文的記錄...")
        ready_posts = publish_service.get_ready_to_post_records()
        
        if not ready_posts:
            print("❌ 沒有找到準備發文的記錄")
            return
        
        print(f"✅ 找到 {len(ready_posts)} 篇準備發文的記錄")
        
        # 只取川川哥的記錄
        chuan_posts = [post for post in ready_posts if post['kol_serial'] == 200]
        
        if not chuan_posts:
            print("❌ 沒有找到川川哥的準備發文記錄")
            return
        
        post = chuan_posts[0]
        print(f"川川哥的發文記錄:")
        print(f"  標題: {post['title']}")
        print(f"  內容長度: {len(post['content'])} 字")
        print(f"  內容預覽: {post['content'][:100]}...")
        
        # 步驟3: 測試發文
        print(f"\n步驟3: 測試發文...")
        result = await publish_service.publish_post(
            kol_serial=200,
            title=post['title'],
            content=post['content'],
            topic_id=post['topic_id']
        )
        
        if result:
            if result.success:
                print(f"✅ 發文成功!")
                print(f"  Post ID: {result.post_id}")
                print(f"  Post URL: {result.post_url}")
            else:
                print(f"❌ 發文失敗: {result.error_message}")
        else:
            print("❌ 發文結果為 None")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_detailed_publish())
