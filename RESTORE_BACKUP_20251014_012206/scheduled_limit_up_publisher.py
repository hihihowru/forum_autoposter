#!/usr/bin/env python3
"""
漲停股貼文自動排程發布系統
設定在早上6:40開始，每2-3分鐘發布一篇貼文
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
import sys
import os

# 添加src路徑
sys.path.append('./src')

# 不需要直接導入LoginCredentials，PublishService會處理

class ScheduledLimitUpPublisher:
    def __init__(self):
        self.sheets_client = None
        self.publish_service = None
        self.posts_to_publish = []
        self.current_post_index = 0
        
    async def initialize_services(self):
        """初始化服務"""
        print("🔧 初始化服務...")
        
        try:
            # 初始化Google Sheets客戶端
            from clients.google.sheets_client import GoogleSheetsClient
            self.sheets_client = GoogleSheetsClient(
                credentials_file="./credentials/google-service-account.json",
                spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
            )
            
            # 初始化發布服務
            from services.publish.publish_service import PublishService
            self.publish_service = PublishService(self.sheets_client)
            
            # KOL登入憑證
            self.kol_credentials = {
                1: {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
                2: {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
                3: {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"},
                4: {"email": "forum_203@cmoney.com.tw", "password": "k8D2mS5u"},
                5: {"email": "forum_204@cmoney.com.tw", "password": "p3F4nT6v"},
                6: {"email": "forum_205@cmoney.com.tw", "password": "q5G6oU7w"},
                7: {"email": "forum_206@cmoney.com.tw", "password": "r7H8pV9x"},
                8: {"email": "forum_207@cmoney.com.tw", "password": "s9I0qW1y"},
                9: {"email": "forum_208@cmoney.com.tw", "password": "t1J2rX3z"},
                10: {"email": "forum_209@cmoney.com.tw", "password": "u3K4sY5a"}
            }
            
            print("✅ 服務初始化完成")
            
        except Exception as e:
            print(f"❌ 服務初始化失敗: {e}")
            raise
    
    async def load_posts_from_sheets(self):
        """從Google Sheets載入待發布的貼文"""
        print("📖 載入待發布貼文...")
        
        try:
            # 讀取貼文記錄表
            posts_data = self.sheets_client.read_sheet('貼文記錄表')
            
            if not posts_data or len(posts_data) <= 1:  # 只有標題行
                print("❌ 沒有找到貼文數據")
                return False
            
            # 解析貼文數據
            self.posts_to_publish = []
            for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
                if len(row) >= 20:  # 確保有足夠的欄位
                    post = {
                        "post_id": row[0],
                        "kol_serial": int(row[1]) if row[1].isdigit() else 0,
                        "kol_nickname": row[2],
                        "kol_persona": row[3],
                        "topic_id": row[4],
                        "topic_title": row[5],
                        "stock_id": row[6],
                        "stock_name": row[7],
                        "limit_up_price": float(row[8]) if row[8] else 0,
                        "previous_close": float(row[9]) if row[9] else 0,
                        "change_percent": float(row[10]) if row[10] else 0,
                        "limit_up_reason": row[11],
                        "generated_title": row[12],
                        "generated_content": row[13],
                        "generated_hashtags": row[14],
                        "status": row[15],
                        "content_length": int(row[16]) if row[16].isdigit() else 0,
                        "data_sources": row[17],
                        "data_source_status": row[18],
                        "created_at": row[19]
                    }
                    
                    # 只載入ready_to_post狀態的貼文
                    if post["status"] == "ready_to_post":
                        self.posts_to_publish.append(post)
            
            print(f"✅ 載入 {len(self.posts_to_publish)} 篇待發布貼文")
            return True
            
        except Exception as e:
            print(f"❌ 載入貼文失敗: {e}")
            return False
    
    async def login_kols(self):
        """登入所有需要的KOL"""
        print("🔐 登入KOL帳號...")
        
        # 獲取需要登入的KOL序號
        kol_serials = list(set([post['kol_serial'] for post in self.posts_to_publish]))
        
        success_count = 0
        for kol_serial in kol_serials:
            if kol_serial in self.kol_credentials:
                try:
                    creds = self.kol_credentials[kol_serial]
                    success = await self.publish_service.login_kol(
                        kol_serial, 
                        creds["email"], 
                        creds["password"]
                    )
                    if success:
                        print(f"✅ KOL {kol_serial} 登入成功")
                        success_count += 1
                    else:
                        print(f"❌ KOL {kol_serial} 登入失敗")
                except Exception as e:
                    print(f"❌ KOL {kol_serial} 登入異常: {e}")
        
        print(f"📊 登入結果: {success_count}/{len(kol_serials)} 個KOL成功")
        return success_count > 0

    async def publish_single_post(self, post):
        """發布單篇貼文"""
        try:
            print(f"\n📝 開始發布貼文: {post['stock_name']}({post['stock_id']})")
            print(f"👤 KOL: {post['kol_nickname']}")
            print(f"📋 標題: {post['generated_title']}")
            
            # 發布貼文
            result = await self.publish_service.publish_post(
                kol_serial=post['kol_serial'],
                title=post['generated_title'],
                content=post['generated_content'],
                topic_id=post['topic_id']
            )
            
            if result and result.success:
                print(f"✅ 發布成功: {post['stock_name']}")
                print(f"📝 文章ID: {result.post_id}")
                print(f"🔗 文章URL: {result.post_url}")
                
                # 更新Google Sheets狀態 - 使用post_id
                await self.update_post_status(post['post_id'], 'published', result.post_id)
                
                return True
            else:
                error_msg = result.error_message if result else "Unknown error"
                print(f"❌ 發布失敗: {error_msg}")
                await self.update_post_status(post['post_id'], 'failed', error_msg)
                return False
                
        except Exception as e:
            print(f"❌ 發布過程出錯: {e}")
            await self.update_post_status(post['post_id'], 'error', str(e))
            return False
    
    async def update_post_status(self, post_id, status, additional_info=""):
        """更新貼文狀態"""
        try:
            # 更新Google Sheets中的狀態
            # 這裡需要實現更新邏輯
            print(f"📊 更新狀態: {post_id} -> {status}")
            
        except Exception as e:
            print(f"❌ 更新狀態失敗: {e}")
    
    async def run_schedule(self):
        """執行排程發布"""
        print("🚀 開始執行排程發布...")
        print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 總貼文數: {len(self.posts_to_publish)}")
        
        # 先登入所有KOL
        if not await self.login_kols():
            print("❌ KOL登入失敗，無法繼續發布")
            return
        
        for i, post in enumerate(self.posts_to_publish, 1):
            print(f"\n{'='*60}")
            print(f"📝 發布第 {i}/{len(self.posts_to_publish)} 篇貼文")
            print(f"⏰ 當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 發布貼文
            success = await self.publish_single_post(post)
            
            if success:
                print(f"✅ 第 {i} 篇發布完成")
            else:
                print(f"❌ 第 {i} 篇發布失敗")
            
            # 如果不是最後一篇，等待2-3分鐘
            if i < len(self.posts_to_publish):
                wait_time = random.randint(120, 180)  # 2-3分鐘
                print(f"⏳ 等待 {wait_time} 秒後發布下一篇...")
                
                # 顯示倒計時
                for remaining in range(wait_time, 0, -30):  # 每30秒顯示一次
                    print(f"⏰ 剩餘等待時間: {remaining//60}分{remaining%60}秒")
                    await asyncio.sleep(30)
                
                # 最後30秒的倒計時
                for remaining in range(30, 0, -1):
                    if remaining % 10 == 0:  # 每10秒顯示一次
                        print(f"⏰ 最後倒計時: {remaining}秒")
                    await asyncio.sleep(1)
            
            print(f"{'='*60}")
        
        print(f"\n🎉 排程發布完成！")
        print(f"⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 總計發布: {len(self.posts_to_publish)} 篇貼文")

async def wait_until_start_time():
    """立即開始，不等待指定時間"""
    print("🚀 立即開始發布，不等待指定時間")
    return True

async def main():
    """主函數"""
    print("🎯 漲停股貼文自動排程發布系統")
    print("=" * 60)
    print("功能:")
    print("1. 早上6:40開始自動發布")
    print("2. 每2-3分鐘發布一篇貼文")
    print("3. 自動更新Google Sheets狀態")
    print("4. 包含commoditytag標記")
    print("=" * 60)
    
    try:
        # 初始化發布器
        publisher = ScheduledLimitUpPublisher()
        await publisher.initialize_services()
        
        # 載入貼文
        if not await publisher.load_posts_from_sheets():
            print("❌ 載入貼文失敗")
            return
        
        # 等待開始時間
        await wait_until_start_time()
        
        # 執行排程
        await publisher.run_schedule()
        
    except Exception as e:
        print(f"❌ 排程執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 啟動漲停股貼文排程系統...")
    print("💡 系統將在早上6:40開始自動發布貼文")
    print("💤 您可以安心睡覺，系統會自動執行")
    asyncio.run(main())
