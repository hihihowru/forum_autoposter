#!/usr/bin/env python3
"""
從 CMoney API 獲取真實的互動數據並更新到 Google Sheets
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

class RealInteractionDataCollector:
    def __init__(self):
        self.cmoney_client = CMoneyClient()
        self.sheets_client = GoogleSheetsClient(
            credentials_file="credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
    
    async def get_kol_credentials(self, kol_nickname: str) -> dict:
        """從 Google Sheets 獲取 KOL 登入憑證"""
        try:
            # 讀取同學會帳號管理表
            data = self.sheets_client.read_sheet("同學會帳號管理", "A1:Z100")
            if not data or len(data) < 2:
                raise Exception("無法讀取同學會帳號管理表")
            
            headers = data[0]
            for row in data[1:]:
                if len(row) > 2:
                    # 使用模糊匹配找到暱稱欄位
                    nickname_col = None
                    for i, header in enumerate(headers):
                        if '暱稱' in header or 'nickname' in header.lower():
                            nickname_col = i
                            break
                    
                    if nickname_col is not None and row[nickname_col] == kol_nickname:
                        # 找到對應的 email 和 password
                        email_col = None
                        password_col = None
                        for i, header in enumerate(headers):
                            if 'email' in header.lower() or '帳號' in header:
                                email_col = i
                            elif 'password' in header.lower() or '密碼' in header:
                                password_col = i
                        
                        if email_col is not None and password_col is not None:
                            return {
                                'email': row[email_col],
                                'password': row[password_col],
                                'nickname': kol_nickname
                            }
            
            raise Exception(f"找不到 KOL {kol_nickname} 的登入憑證")
            
        except Exception as e:
            print(f"❌ 獲取 KOL 憑證失敗: {e}")
            return None
    
    async def get_real_interaction_data(self, article_id: str, kol_nickname: str) -> dict:
        """從 CMoney API 獲取真實的互動數據"""
        try:
            # 獲取 KOL 登入憑證
            credentials = await self.get_kol_credentials(kol_nickname)
            if not credentials:
                return None
            
            # 登入 CMoney
            login_creds = LoginCredentials(
                email=credentials['email'],
                password=credentials['password']
            )
            
            access_token = await self.cmoney_client.login(login_creds)
            
            # 獲取互動數據
            interaction_data = await self.cmoney_client.get_article_interactions(
                access_token.token, 
                article_id
            )
            
            if not interaction_data or not interaction_data.raw_data:
                print(f"⚠️ 文章 {article_id} 沒有互動數據")
                return None
            
            # 解析 emoji 數據
            emoji_count = interaction_data.raw_data.get("emojiCount", {})
            
            # 準備 emoji 類型和數量
            emoji_types = []
            emoji_counts = {}
            
            emoji_mapping = {
                'like': '👍',
                'dislike': '👎', 
                'laugh': '😄',
                'money': '💰',
                'shock': '😱',
                'cry': '😢',
                'think': '🤔',
                'angry': '😠'
            }
            
            for emoji_key, emoji_symbol in emoji_mapping.items():
                count = emoji_count.get(emoji_key, 0)
                if count > 0:
                    emoji_types.append(emoji_symbol)
                    emoji_counts[emoji_symbol] = count
            
            return {
                'article_id': article_id,
                'member_id': interaction_data.member_id,
                'nickname': kol_nickname,
                'likes_count': interaction_data.likes,
                'comments_count': interaction_data.comments,
                'total_interactions': interaction_data.total_interactions,
                'engagement_rate': interaction_data.engagement_rate,
                'donation_count': interaction_data.donations,
                'donation_amount': 0.0,  # CMoney API 沒有提供金額
                'emoji_type': ','.join(emoji_types),
                'emoji_counts': str(emoji_counts),
                'total_emoji_count': interaction_data.total_emojis,
                'raw_data': interaction_data.raw_data
            }
            
        except Exception as e:
            print(f"❌ 獲取文章 {article_id} 互動數據失敗: {e}")
            return None
    
    async def update_interaction_sheets(self):
        """更新所有互動回饋工作表"""
        print("📊 開始收集真實互動數據...")
        print("-----------------------------------------")
        
        try:
            # 讀取貼文記錄表
            posts_data = self.sheets_client.read_sheet("貼文記錄表", "A1:Z100")
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
            
            # 為每個工作表收集數據
            sheets_to_update = [
                "互動回饋_1hr",
                "互動回饋_1day", 
                "互動回饋_7days"
            ]
            
            for sheet_name in sheets_to_update:
                print(f"\n📋 更新 {sheet_name} 工作表...")
                
                # 清空現有數據（保留標題）
                current_data = self.sheets_client.read_sheet(sheet_name, "A1:T10")
                if current_data and len(current_data) > 0:
                    headers = current_data[0]
                    # 清空工作表，只保留標題
                    self.sheets_client.write_sheet(sheet_name, [headers], "A1:T1000")
                
                # 收集每篇貼文的真實互動數據
                new_data = []
                
                for post in posts:
                    print(f"📝 收集文章 {post['article_id']} ({post['nickname']}) 的互動數據...")
                    
                    interaction_data = await self.get_real_interaction_data(
                        post['article_id'], 
                        post['nickname']
                    )
                    
                    if interaction_data:
                        # 準備記錄
                        record = [
                            interaction_data['article_id'],
                            interaction_data['member_id'],
                            interaction_data['nickname'],
                            f"貼文 {interaction_data['article_id']}",
                            "",  # content
                            "",  # topic_id
                            "FALSE",  # is_trending_topic
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # post_time
                            datetime.now().isoformat(),  # last_update_time
                            str(interaction_data['likes_count']),
                            str(interaction_data['comments_count']),
                            str(interaction_data['total_interactions']),
                            str(interaction_data['engagement_rate']),
                            "0.0",  # growth_rate
                            "",  # collection_error
                            str(interaction_data['donation_count']),
                            str(interaction_data['donation_amount']),
                            interaction_data['emoji_type'],
                            interaction_data['emoji_counts'],
                            str(interaction_data['total_emoji_count'])
                        ]
                        
                        new_data.append(record)
                        print(f"✅ 已收集: 讚={interaction_data['likes_count']}, 留言={interaction_data['comments_count']}, 總互動={interaction_data['total_interactions']}")
                    else:
                        print(f"⚠️ 無法獲取文章 {post['article_id']} 的互動數據")
                
                # 寫入數據
                if len(new_data) > 0:
                    # 使用 append_sheet 來添加數據
                    self.sheets_client.append_sheet(sheet_name, new_data)
                    print(f"✅ 已寫入 {len(new_data)} 條記錄到 {sheet_name}")
                else:
                    print(f"⚠️ {sheet_name} 沒有數據可寫入")
            
            print("\n🎉 真實互動數據收集完成！")
            
        except Exception as e:
            print(f"❌ 更新失敗: {e}")

async def main():
    collector = RealInteractionDataCollector()
    await collector.update_interaction_sheets()

if __name__ == "__main__":
    asyncio.run(main())
