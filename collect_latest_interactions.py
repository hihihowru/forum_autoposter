#!/usr/bin/env python3
"""
更新最新互動成效數據到 Google Sheets
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

class LatestInteractionCollector:
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
        
    async def collect_latest_interactions(self, article_ids):
        """搜集最新互動成效"""
        latest_data = []
        
        for article_id in article_ids:
            print(f"正在搜集貼文 {article_id} 的互動數據...")
            
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
                
                if interaction_data:
                    # 格式化數據以符合現有表格結構
                    formatted_data = {
                        "article_id": article_id,
                        "member_id": kol_serial,
                        "nickname": kol_nickname,
                        "title": f"貼文 {article_id}",
                        "content": "",
                        "topic_id": "",
                        "is_trending_topic": "FALSE",
                        "post_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "last_update_time": datetime.now().isoformat(),
                        "likes_count": interaction_data.likes,
                        "comments_count": interaction_data.comments,
                        "total_interactions": interaction_data.likes + interaction_data.comments,
                        "engagement_rate": interaction_data.engagement_rate,
                        "growth_rate": 0.0,
                        "collection_error": ""
                    }
                    
                    latest_data.append(formatted_data)
                    print(f"✅ 成功搜集貼文 {article_id} 的數據")
                else:
                    print(f"❌ 無法獲取貼文 {article_id} 的數據")
                    
            except Exception as e:
                print(f"❌ 搜集貼文 {article_id} 時發生錯誤: {str(e)}")
                error_data = {
                    "article_id": article_id,
                    "member_id": "",
                    "nickname": "",
                    "title": "",
                    "content": "",
                    "topic_id": "",
                    "is_trending_topic": "FALSE",
                    "post_time": "",
                    "last_update_time": datetime.now().isoformat(),
                    "likes_count": 0,
                    "comments_count": 0,
                    "total_interactions": 0,
                    "engagement_rate": 0.0,
                    "growth_rate": 0.0,
                    "collection_error": str(e)
                }
                latest_data.append(error_data)
            
            # 避免請求過於頻繁
            await asyncio.sleep(1)
        
        return latest_data
    
    def update_google_sheets(self, latest_data):
        """更新 Google Sheets 的最新狀態表"""
        try:
            # 使用 append_sheet 方法添加到現有工作表
            sheet_name = "aigc 自我學習機制"
            
            # 轉換數據為表格格式
            rows = []
            for data in latest_data:
                row = [
                    data.get("article_id", ""),
                    data.get("member_id", ""),
                    data.get("nickname", ""),
                    data.get("title", ""),
                    data.get("content", ""),
                    data.get("topic_id", ""),
                    data.get("is_trending_topic", ""),
                    data.get("post_time", ""),
                    data.get("last_update_time", ""),
                    data.get("likes_count", 0),
                    data.get("comments_count", 0),
                    data.get("total_interactions", 0),
                    data.get("engagement_rate", 0.0),
                    data.get("growth_rate", 0.0),
                    data.get("collection_error", "")
                ]
                rows.append(row)
            
            # 追加數據到工作表
            self.sheets_client.append_sheet(sheet_name, rows)
            print(f"✅ 成功更新 Google Sheets 的「{sheet_name}」表")
            
        except Exception as e:
            print(f"❌ 更新 Google Sheets 時發生錯誤: {str(e)}")
    
    async def run(self, article_ids):
        """執行完整的搜集流程"""
        print("🚀 開始搜集最新互動成效數據...")
        print(f"📝 目標貼文: {article_ids}")
        
        # 搜集數據
        latest_data = await self.collect_latest_interactions(article_ids)
        
        if latest_data:
            # 更新 Google Sheets
            self.update_google_sheets(latest_data)
            
            # 顯示結果摘要
            print("\n📊 搜集結果摘要:")
            for data in latest_data:
                print(f"  貼文 {data['article_id']}: {data['total_interactions']} 互動 "
                      f"({data['likes_count']} 讚, {data['comments_count']} 留言)")
        else:
            print("❌ 沒有搜集到任何數據")

async def main():
    # 最新的兩個貼文 ID
    latest_article_ids = ["173477844", "173477845"]
    
    collector = LatestInteractionCollector()
    await collector.run(latest_article_ids)

if __name__ == "__main__":
    asyncio.run(main())
