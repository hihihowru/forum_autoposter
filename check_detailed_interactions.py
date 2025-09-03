#!/usr/bin/env python3
"""
檢查所有表情和打賞數據
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

class DetailedInteractionChecker:
    def __init__(self):
        # 從環境變量獲取配置
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
        
        self.sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        self.cmoney_client = CMoneyClient()
        
    async def get_kol_credentials(self, kol_serial: str):
        """獲取 KOL 登入憑證"""
        try:
            # 讀取同學會帳號管理
            data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            for row in data[1:]:  # 跳過標題行
                if len(row) > 6 and str(row[0]) == str(kol_serial):
                    return {
                        'email': row[5] if len(row) > 5 else '',
                        'password': row[6] if len(row) > 6 else ''
                    }
            
            print(f"找不到 KOL {kol_serial} 的登入憑證")
            return None
            
        except Exception as e:
            print(f"獲取 KOL 憑證失敗: {e}")
            return None
        
    async def check_detailed_interactions(self, article_ids):
        """檢查詳細的互動數據"""
        
        for article_id in article_ids:
            print(f"\n🔍 詳細檢查貼文 {article_id} 的互動數據...")
            
            try:
                # 從貼文記錄表獲取 KOL 資訊
                post_data = self.sheets_client.read_sheet('貼文記錄表', 'A:Z')
                kol_serial = None
                kol_nickname = ""
                
                for row in post_data[1:]:  # 跳過標題行
                    if len(row) > 15 and row[15] == article_id:  # platform_post_id
                        kol_serial = row[1] if len(row) > 1 else None  # kol_serial
                        kol_nickname = row[2] if len(row) > 2 else ""   # kol_nickname
                        break
                
                if not kol_serial:
                    print(f"❌ 找不到貼文 {article_id} 對應的 KOL 資訊")
                    continue
                
                print(f"📝 KOL 資訊: {kol_nickname} (ID: {kol_serial})")
                
                # 獲取 KOL 憑證
                kol_credentials = await self.get_kol_credentials(kol_serial)
                if not kol_credentials:
                    continue
                
                # 登入 KOL
                login_creds = LoginCredentials(
                    email=kol_credentials['email'],
                    password=kol_credentials['password']
                )
                
                access_token = await self.cmoney_client.login(login_creds)
                
                # 獲取互動數據
                interaction_data = await self.cmoney_client.get_article_interactions(
                    access_token.token, 
                    article_id
                )
                
                if interaction_data and hasattr(interaction_data, 'raw_data'):
                    raw_data = interaction_data.raw_data
                    emoji_count = raw_data.get("emojiCount", {})
                    
                    print(f"\n📊 詳細互動數據分析:")
                    print(f"  - 貼文 ID: {article_id}")
                    print(f"  - 標題: {raw_data.get('content', {}).get('title', 'N/A')}")
                    
                    print(f"\n😊 表情詳細統計:")
                    print(f"  - 讚 (like): {emoji_count.get('like', 0)}")
                    print(f"  - 倒讚 (dislike): {emoji_count.get('dislike', 0)}")
                    print(f"  - 笑 (laugh): {emoji_count.get('laugh', 0)}")
                    print(f"  - 錢 (money): {emoji_count.get('money', 0)}")
                    print(f"  - 震驚 (shock): {emoji_count.get('shock', 0)}")
                    print(f"  - 哭 (cry): {emoji_count.get('cry', 0)}")
                    print(f"  - 思考 (think): {emoji_count.get('think', 0)}")
                    print(f"  - 生氣 (angry): {emoji_count.get('angry', 0)}")
                    
                    total_emojis = sum(emoji_count.values())
                    print(f"  - 表情總數: {total_emojis}")
                    
                    print(f"\n💬 其他互動數據:")
                    print(f"  - 留言數 (commentCount): {raw_data.get('commentCount', 0)}")
                    print(f"  - 收藏數 (collectedCount): {raw_data.get('collectedCount', 0)}")
                    print(f"  - 打賞數 (donation): {raw_data.get('donation', 0)}")
                    print(f"  - 興趣數 (interestedCount): {raw_data.get('interestedCount', 0)}")
                    
                    print(f"\n📈 計算結果:")
                    print(f"  - 總互動數: {interaction_data.likes + interaction_data.comments + interaction_data.shares}")
                    print(f"  - 互動率: {interaction_data.engagement_rate}")
                    
                else:
                    print(f"❌ 無法獲取貼文 {article_id} 的數據")
                    
            except Exception as e:
                print(f"❌ 檢查貼文 {article_id} 時發生錯誤: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # 避免請求過於頻繁
            await asyncio.sleep(2)

async def main():
    # 最新的兩個貼文 ID
    latest_article_ids = ["173477844", "173477845"]
    
    checker = DetailedInteractionChecker()
    await checker.check_detailed_interactions(latest_article_ids)

if __name__ == "__main__":
    import json
    asyncio.run(main())


