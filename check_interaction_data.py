#!/usr/bin/env python3
"""
檢查互動數據回傳內容
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

class InteractionDataChecker:
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
        
    async def check_interaction_data(self, article_ids):
        """檢查互動數據回傳內容"""
        
        for article_id in article_ids:
            print(f"\n🔍 檢查貼文 {article_id} 的互動數據...")
            
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
                
                print(f"🔑 登入憑證: {kol_credentials['email']}")
                
                # 登入 KOL
                login_creds = LoginCredentials(
                    email=kol_credentials['email'],
                    password=kol_credentials['password']
                )
                
                access_token = await self.cmoney_client.login(login_creds)
                print(f"✅ 登入成功，Token: {access_token.token[:20]}...")
                
                # 獲取互動數據
                interaction_data = await self.cmoney_client.get_article_interactions(
                    access_token.token, 
                    article_id
                )
                
                if interaction_data:
                    print(f"\n📊 互動數據詳細內容:")
                    print(f"  - 貼文 ID: {article_id}")
                    print(f"  - 讚數: {interaction_data.likes}")
                    print(f"  - 留言數: {interaction_data.comments}")
                    print(f"  - 分享數: {interaction_data.shares}")
                    print(f"  - 瀏覽數: {interaction_data.views}")
                    print(f"  - 點擊率: {interaction_data.click_rate}")
                    print(f"  - 互動率: {interaction_data.engagement_rate}")
                    print(f"  - 總互動: {interaction_data.likes + interaction_data.comments}")
                    
                    # 檢查原始數據
                    if hasattr(interaction_data, 'raw_data') and interaction_data.raw_data:
                        print(f"\n🔍 原始 API 回應數據:")
                        print(json.dumps(interaction_data.raw_data, indent=2, ensure_ascii=False))
                    else:
                        print(f"\n⚠️  沒有原始數據可顯示")
                        
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
    
    checker = InteractionDataChecker()
    await checker.check_interaction_data(latest_article_ids)

if __name__ == "__main__":
    import json
    asyncio.run(main())


