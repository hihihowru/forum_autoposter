#!/usr/bin/env python3
"""
測試獲取真實熱門話題
使用 CMoney API 獲取 trending topics
"""
import sys
import asyncio
import os
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from clients.google.sheets_client import GoogleSheetsClient


async def test_real_trending_topics():
    """測試獲取真實熱門話題"""
    print("=== 測試獲取真實熱門話題 ===")
    
    try:
        # 1. 初始化 CMoney 客戶端
        cmoney_client = CMoneyClient()
        
        # 2. 從 Google Sheets 讀取 KOL 憑證
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        print("讀取 KOL 憑證...")
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        
        if len(kol_data) < 2:
            print("❌ 沒有找到 KOL 數據")
            return False
        
        # 找到第一個有效的 KOL 憑證
        headers = kol_data[0]
        email_idx = None
        password_idx = None
        
        for i, header in enumerate(headers):
            if 'Email' in header or '帳號' in header:
                email_idx = i
            elif '密碼' in header:
                password_idx = i
        
        if email_idx is None or password_idx is None:
            print("❌ 找不到 Email 或密碼欄位")
            return False
        
        # 使用第一個 KOL 的憑證
        first_kol = kol_data[1]
        email = first_kol[email_idx] if len(first_kol) > email_idx else None
        password = first_kol[password_idx] if len(first_kol) > password_idx else None
        
        if not email or not password:
            print("❌ KOL 憑證不完整")
            return False
        
        print(f"使用 KOL 憑證: {email[:5]}***@{email.split('@')[1] if '@' in email else '***'}")
        
        # 3. 登入 CMoney
        print("登入 CMoney...")
        credentials = LoginCredentials(email=email, password=password)
        access_token = await cmoney_client.login(credentials)
        print(f"✅ 登入成功，Token: {access_token.token[:20]}...")
        
        # 4. 獲取熱門話題
        print("獲取熱門話題...")
        trending_topics = await cmoney_client.get_trending_topics(access_token.token)
        
        print(f"✅ 成功獲取 {len(trending_topics)} 個熱門話題")
        print()
        
        # 5. 顯示話題詳情
        print("=== 熱門話題列表 ===")
        for i, topic in enumerate(trending_topics[:5], 1):
            print(f"話題 {i}:")
            print(f"  ID: {topic.id}")
            print(f"  標題: {topic.title}")
            print(f"  名稱: {topic.name}")
            if topic.last_article_create_time:
                print(f"  最後文章時間: {topic.last_article_create_time}")
            print()
        
        # 6. 測試改進後的標題生成
        print("=== 測試改進後的標題生成 ===")
        from services.content.content_generator import create_content_generator, ContentRequest
        
        generator = create_content_generator()
        
        # 選擇第一個話題進行測試
        if trending_topics:
            test_topic = trending_topics[0]
            print(f"測試話題: {test_topic.title}")
            print()
            
            # 測試不同 KOL 的標題生成
            test_kols = [
                {"nickname": "川川哥", "persona": "技術派"},
                {"nickname": "梅川褲子", "persona": "新聞派"},
                {"nickname": "韭割哥", "persona": "總經派"}
            ]
            
            for kol in test_kols:
                print(f"--- {kol['nickname']} ({kol['persona']}) ---")
                
                request = ContentRequest(
                    topic_title=test_topic.title,
                    topic_keywords=f"熱門話題,{test_topic.name}",
                    kol_persona=kol['persona'],
                    kol_nickname=kol['nickname'],
                    content_type='investment',
                    target_audience='active_traders',
                    market_data={}
                )
                
                try:
                    result = generator.generate_complete_content(request)
                    if result.success:
                        print(f"標題: {result.title}")
                        print(f"內容長度: {len(result.content)} 字")
                        print()
                    else:
                        print(f"❌ 生成失敗: {result.error_message}")
                except Exception as e:
                    print(f"❌ 異常: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_real_trending_topics())
    if not success:
        sys.exit(1)
