#!/usr/bin/env python3
"""
簡化的貼文成效抓取函數
可以重複調用來獲取貼文紀錄表上的互動成效
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, '..', 'src'))

from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from clients.google.sheets_client import GoogleSheetsClient

async def fetch_post_performance():
    """抓取貼文成效並更新工作表 - 可重複調用的函數"""
    print("📊 抓取貼文成效...")
    print("-----------------------------------------")
    
    try:
        # 初始化客戶端
        cmoney_client = CMoneyClient()
        sheets_client = GoogleSheetsClient(
            credentials_file="credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 讀取貼文記錄表
        posts_data = sheets_client.read_sheet("貼文記錄表", "A1:Z100")
        if not posts_data or len(posts_data) < 2:
            print("❌ 無法讀取貼文記錄表")
            return
        
        headers = posts_data[0]
        posts = []
        
        # 找到相關欄位索引
        articleid_col = None
        nickname_col = None
        status_col = None
        
        for i, header in enumerate(headers):
            if '平台發文ID' in header:
                articleid_col = i
            elif 'KOL 暱稱' in header:
                nickname_col = i
            elif '發文狀態' in header:
                status_col = i
        
        if articleid_col is None or nickname_col is None:
            print("❌ 找不到必要的欄位")
            return
        
        # 收集已發文的貼文
        for row in posts_data[1:]:
            if len(row) > max(articleid_col, nickname_col):
                article_id = row[articleid_col]
                nickname = row[nickname_col]
                status = row[status_col] if status_col is not None and len(row) > status_col else ""
                
                if article_id and nickname and status == "已發文":
                    posts.append({
                        'article_id': article_id,
                        'nickname': nickname
                    })
        
        print(f"📝 找到 {len(posts)} 篇已發文的貼文")
        
        # 抓取每篇貼文的互動成效
        performance_data = []
        
        for post in posts:
            print(f"📝 抓取文章 {post['article_id']} ({post['nickname']}) 的互動成效...")
            
            try:
                # 獲取 KOL 登入憑證
                kol_data = sheets_client.read_sheet("同學會帳號管理", "A1:Z100")
                credentials = None
                
                if kol_data and len(kol_data) > 1:
                    kol_headers = kol_data[0]
                    for kol_row in kol_data[1:]:
                        if len(kol_row) > 2:
                            # 找到暱稱欄位
                            nickname_col = None
                            for i, header in enumerate(kol_headers):
                                if '暱稱' in header or 'nickname' in header.lower():
                                    nickname_col = i
                                    break
                            
                            if nickname_col is not None and kol_row[nickname_col] == post['nickname']:
                                # 找到 email 和 password
                                email_col = None
                                password_col = None
                                for i, header in enumerate(kol_headers):
                                    if 'email' in header.lower() or '帳號' in header:
                                        email_col = i
                                    elif 'password' in header.lower() or '密碼' in header:
                                        password_col = i
                                
                                if email_col is not None and password_col is not None:
                                    credentials = {
                                        'email': kol_row[email_col],
                                        'password': kol_row[password_col]
                                    }
                                    break
                
                if not credentials:
                    print(f"⚠️ 無法獲取 {post['nickname']} 的登入憑證")
                    continue
                
                # 登入 CMoney
                login_creds = LoginCredentials(
                    email=credentials['email'],
                    password=credentials['password']
                )
                
                access_token = await cmoney_client.login(login_creds)
                
                # 獲取互動數據
                interaction_data = await cmoney_client.get_article_interactions(
                    access_token.token, 
                    post['article_id']
                )
                
                if interaction_data and interaction_data.raw_data:
                    # 解析 emoji 數據
                    emoji_count = interaction_data.raw_data.get("emojiCount", {})
                    emoji_types = []
                    emoji_counts = {}
                    
                    emoji_mapping = {
                        'like': '👍', 'dislike': '👎', 'laugh': '😄',
                        'money': '💰', 'shock': '😱', 'cry': '😢',
                        'think': '🤔', 'angry': '😠'
                    }
                    
                    for emoji_key, emoji_symbol in emoji_mapping.items():
                        count = emoji_count.get(emoji_key, 0)
                        if count > 0:
                            emoji_types.append(emoji_symbol)
                            emoji_counts[emoji_symbol] = count
                    
                    performance = {
                        'article_id': post['article_id'],
                        'member_id': interaction_data.member_id,
                        'nickname': post['nickname'],
                        'likes_count': interaction_data.likes,
                        'comments_count': interaction_data.comments,
                        'total_interactions': interaction_data.total_interactions,
                        'engagement_rate': interaction_data.engagement_rate,
                        'donation_count': interaction_data.donations,
                        'donation_amount': 0.0,
                        'emoji_type': ','.join(emoji_types),
                        'emoji_counts': str(emoji_counts),
                        'total_emoji_count': interaction_data.total_emojis,
                        'fetch_time': datetime.now().isoformat()
                    }
                    
                    performance_data.append(performance)
                    print(f"✅ 已抓取: 讚={performance['likes_count']}, 留言={performance['comments_count']}, 總互動={performance['total_interactions']}")
                else:
                    print(f"⚠️ 文章 {post['article_id']} 沒有互動數據")
                    
            except Exception as e:
                print(f"❌ 抓取文章 {post['article_id']} 失敗: {e}")
        
        if performance_data:
            # 更新互動回饋工作表
            print("\n📋 更新互動回饋工作表...")
            
            headers = ['article_id', 'member_id', 'nickname', 'title', 'content', 'topic_id', 'is_trending_topic', 'post_time', 'last_update_time', 'likes_count', 'comments_count', 'total_interactions', 'engagement_rate', 'growth_rate', 'collection_error', 'donation_count', 'donation_amount', 'emoji_type', 'emoji_counts', 'total_emoji_count']
            
            sheets_to_update = [
                "互動回饋_1hr",
                "互動回饋_1day", 
                "互動回饋_7days",
                "互動回饋即時總表"
            ]
            
            for sheet_name in sheets_to_update:
                print(f"📋 更新 {sheet_name}...")
                
                # 清空並重寫
                sheets_client.write_sheet(sheet_name, [headers], "A1:T1000")
                
                new_data = []
                for performance in performance_data:
                    record = [
                        performance['article_id'],
                        performance['member_id'],
                        performance['nickname'],
                        f"貼文 {performance['article_id']}",
                        "", "", "FALSE",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        performance['fetch_time'],
                        str(performance['likes_count']),
                        str(performance['comments_count']),
                        str(performance['total_interactions']),
                        str(performance['engagement_rate']),
                        "0.0", "",
                        str(performance['donation_count']),
                        str(performance['donation_amount']),
                        performance['emoji_type'],
                        performance['emoji_counts'],
                        str(performance['total_emoji_count'])
                    ]
                    new_data.append(record)
                
                if new_data:
                    sheets_client.append_sheet(sheet_name, new_data)
                    print(f"✅ 已寫入 {len(new_data)} 條記錄")
            
            # 顯示總結
            print("\n📊 貼文成效總結:")
            print("-----------------------------------------")
            total_likes = sum(p['likes_count'] for p in performance_data)
            total_comments = sum(p['comments_count'] for p in performance_data)
            total_interactions = sum(p['total_interactions'] for p in performance_data)
            total_donations = sum(p['donation_count'] for p in performance_data)
            
            print(f"📝 總貼文數: {len(performance_data)}")
            print(f"👍 總讚數: {total_likes}")
            print(f"💬 總留言數: {total_comments}")
            print(f"📊 總互動數: {total_interactions}")
            print(f"💰 總捐贈數: {total_donations}")
            
            for performance in performance_data:
                print(f"\n📄 {performance['nickname']} (文章 {performance['article_id']}):")
                print(f"  👍 讚數: {performance['likes_count']}")
                print(f"  💬 留言: {performance['comments_count']}")
                print(f"  📊 總互動: {performance['total_interactions']}")
                print(f"  💰 捐贈: {performance['donation_count']}")
                print(f"  😊 Emoji: {performance['emoji_type']}")
            
            print("\n🎉 貼文成效抓取完成！")
        else:
            print("❌ 沒有抓取到任何貼文成效")
            
    except Exception as e:
        print(f"❌ 抓取失敗: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_post_performance())










