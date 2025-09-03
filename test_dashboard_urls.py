#!/usr/bin/env python3
"""
測試 Dashboard URL 連結功能
驗證 KOL 和貼文的 URL 是否正確
"""

import asyncio
from src.clients.google.sheets_client import GoogleSheetsClient

async def test_dashboard_urls():
    """測試 Dashboard URL 連結"""
    sheets_client = GoogleSheetsClient(
        credentials_file='credentials/google-service-account.json',
        spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
    )
    
    print("=" * 60)
    print("🔗 Dashboard URL 連結測試")
    print("=" * 60)
    
    # 讀取 KOL 數據
    print("\n📋 KOL 會員主頁連結:")
    print("-" * 40)
    
    try:
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        for i, row in enumerate(kol_data[1:], start=2):  # 跳過標題行
            if len(row) > 4 and row[1] and row[4]:  # 確保有暱稱和 member_id
                nickname = row[1]
                member_id = row[4]
                status = row[9] if len(row) > 9 else '未知'
                
                if status == '啟用':
                    url = f"https://www.cmoney.tw/forum/user/{member_id}"
                    print(f"✅ {nickname} (ID: {member_id})")
                    print(f"   🔗 {url}")
                    print()
    except Exception as e:
        print(f"❌ 讀取 KOL 數據失敗: {e}")
    
    # 讀取貼文數據
    print("\n📝 貼文文章連結:")
    print("-" * 40)
    
    try:
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Y')
        for i, row in enumerate(post_data[1:], start=2):  # 跳過標題行
            if len(row) > 16 and row[2] and row[15]:  # 確保有 KOL 暱稱和 article_id
                kol_nickname = row[2]
                post_id = row[0]
                article_id = row[15]
                status = row[11] if len(row) > 11 else '未知'
                
                if article_id and status == 'posted':
                    url = f"https://www.cmoney.tw/forum/article/{article_id}"
                    print(f"✅ {kol_nickname} - {post_id}")
                    print(f"   📄 Article ID: {article_id}")
                    print(f"   🔗 {url}")
                    print()
    except Exception as e:
        print(f"❌ 讀取貼文數據失敗: {e}")
    
    # 讀取即時互動數據
    print("\n📊 即時互動數據連結:")
    print("-" * 40)
    
    try:
        interaction_data = sheets_client.read_sheet('互動回饋_1hr', 'A:O')
        for i, row in enumerate(interaction_data[1:], start=2):  # 跳過標題行
            if len(row) > 10 and row[0] and row[1]:  # 確保有 article_id 和 member_id
                article_id = row[0]
                member_id = row[1]
                nickname = row[2]
                likes = row[9] if len(row) > 9 else '0'
                comments = row[10] if len(row) > 10 else '0'
                
                article_url = f"https://www.cmoney.tw/forum/article/{article_id}"
                member_url = f"https://www.cmoney.tw/forum/user/{member_id}"
                
                print(f"✅ {nickname} - 互動數據")
                print(f"   📄 文章: {article_url}")
                print(f"   👤 會員: {member_url}")
                print(f"   👍 讚數: {likes} | 💬 留言: {comments}")
                print()
    except Exception as e:
        print(f"❌ 讀取互動數據失敗: {e}")
    
    print("=" * 60)
    print("✅ URL 連結測試完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_dashboard_urls())
