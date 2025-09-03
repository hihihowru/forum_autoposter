#!/usr/bin/env python3
"""
刪除所有測試貼文
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

async def delete_test_posts():
    """刪除所有測試貼文"""
    
    print("=== 刪除所有測試貼文 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    cmoney_client = CMoneyClient()
    
    try:
        # 步驟1: 讀取貼文記錄表，找到所有測試貼文
        print("步驟1: 讀取貼文記錄表...")
        data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not data:
            print("❌ 無法讀取貼文記錄表")
            return
        
        # 找到所有測試貼文
        test_posts = []
        for row in data[1:]:  # 跳過標題行
            if len(row) >= 16:
                post_id = row[0] if row[0] else ""
                platform_post_id = row[15] if len(row) > 15 and row[15] else ""
                status = row[11] if len(row) > 11 and row[11] else ""
                kol_serial = row[1] if row[1] else ""
                kol_nickname = row[2] if len(row) > 2 and row[2] else ""
                
                # 檢查是否為測試貼文且已發佈
                if (post_id.startswith(('debug_', 'test_', 'improved_test_', 'general_test_')) and 
                    status == "posted" and platform_post_id):
                    test_posts.append({
                        'post_id': post_id,
                        'platform_post_id': platform_post_id,
                        'kol_serial': kol_serial,
                        'kol_nickname': kol_nickname
                    })
        
        print(f"✅ 找到 {len(test_posts)} 篇測試貼文需要刪除")
        
        if not test_posts:
            print("✅ 沒有找到需要刪除的測試貼文")
            return
        
        # 顯示測試貼文列表
        for i, post in enumerate(test_posts, 1):
            print(f"  {i}. {post['kol_nickname']} (Serial: {post['kol_serial']})")
            print(f"     貼文ID: {post['post_id']}")
            print(f"     平台發文ID: {post['platform_post_id']}")
            print()
        
        # 步驟2: 登入 KOL 並刪除貼文
        print("步驟2: 登入 KOL 並刪除貼文...")
        
        # 獲取需要登入的 KOL
        kol_serials = list(set([post['kol_serial'] for post in test_posts]))
        
        # KOL 帳號密碼對應
        kol_credentials = {
            "200": {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
            "201": {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
            "202": {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"},
            "203": {"email": "forum_203@cmoney.com.tw", "password": "y7O3cL9k"},
            "204": {"email": "forum_204@cmoney.com.tw", "password": "f4E9sC8w"},
            "205": {"email": "forum_205@cmoney.com.tw", "password": "Z5u6dL9o"}
        }
        
        # 登入 KOL 並刪除貼文
        kol_tokens = {}
        for kol_serial in kol_serials:
            if kol_serial in kol_credentials:
                print(f"登入 KOL {kol_serial}...")
                credentials = LoginCredentials(
                    email=kol_credentials[kol_serial]["email"],
                    password=kol_credentials[kol_serial]["password"]
                )
                
                try:
                    token = await cmoney_client.login(credentials)
                    kol_tokens[kol_serial] = token
                    print(f"✅ KOL {kol_serial} 登入成功")
                except Exception as e:
                    print(f"❌ KOL {kol_serial} 登入失敗: {e}")
        
        # 刪除貼文
        deleted_count = 0
        for post in test_posts:
            kol_serial = post['kol_serial']
            platform_post_id = post['platform_post_id']
            
            if kol_serial in kol_tokens:
                print(f"刪除貼文 {post['post_id']} (平台ID: {platform_post_id})...")
                try:
                    success = await cmoney_client.delete_article(
                        kol_tokens[kol_serial].token, 
                        platform_post_id
                    )
                    if success:
                        print(f"✅ 成功刪除貼文 {post['post_id']}")
                        deleted_count += 1
                    else:
                        print(f"❌ 刪除貼文 {post['post_id']} 失敗")
                except Exception as e:
                    print(f"❌ 刪除貼文 {post['post_id']} 異常: {e}")
            else:
                print(f"❌ KOL {kol_serial} 未登入，跳過貼文 {post['post_id']}")
        
        print(f"\n✅ 刪除完成！成功刪除 {deleted_count}/{len(test_posts)} 篇測試貼文")
        
    except Exception as e:
        print(f"❌ 刪除測試貼文失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(delete_test_posts())
