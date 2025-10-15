#!/usr/bin/env python3
"""
發佈17檔盤中急漲股貼文並更新Google Sheets
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def publish_17_posts():
    """發佈17檔盤中急漲股貼文並更新Google Sheets"""
    print("🚀 開始發佈17檔盤中急漲股貼文...")
    
    try:
        from src.core.main_workflow_engine import MainWorkflowEngine
        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, ArticleData, PublishResult
        from src.clients.google.sheets_client import GoogleSheetsClient
        
        # 初始化客戶端
        engine = MainWorkflowEngine()
        cmoney_client = CMoneyClient()
        
        # 初始化Google Sheets客戶端
        credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "./credentials/google-service-account.json")
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        print("✅ 客戶端初始化完成")
        
        # 獲取Google Sheets中的貼文記錄
        print("📋 獲取貼文記錄...")
        posts_data = sheets_client.read_sheet("貼文紀錄表")
        
        if not posts_data:
            print("❌ 無法獲取貼文記錄")
            return
        
        # 篩選出需要發佈的貼文（status為ready_to_post且stock_trigger_type為limit_up_smart）
        posts_to_publish = []
        for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
            if len(row) > 31:  # 確保有足夠的欄位
                status = row[4] if len(row) > 4 else ""  # status欄位
                stock_trigger_type = row[31] if len(row) > 31 else ""  # stock_trigger_type欄位
                test_post_id = row[0] if len(row) > 0 else ""  # test_post_id欄位
                
                if status == "ready_to_post" and stock_trigger_type == "limit_up_smart":
                    posts_to_publish.append({
                        'row_index': i,
                        'test_post_id': test_post_id,
                        'kol_serial': row[7] if len(row) > 7 else "",  # kol_serial
                        'kol_nickname': row[8] if len(row) > 8 else "",  # kol_nickname
                        'stock_id': row[20] if len(row) > 20 else "",  # stock_id
                        'stock_name': row[21] if len(row) > 21 else "",  # stock_name
                        'title': row[32] if len(row) > 32 else "",  # title
                        'content': row[33] if len(row) > 33 else "",  # content
                        'row_data': row
                    })
        
        # 只取最後17篇貼文（倒數）
        posts_to_publish = posts_to_publish[-17:] if len(posts_to_publish) > 17 else posts_to_publish
        
        print(f"📊 找到 {len(posts_to_publish)} 篇待發佈貼文")
        
        if not posts_to_publish:
            print("❌ 沒有找到待發佈的貼文")
            return
        
        # 發佈貼文
        published_count = 0
        failed_count = 0
        
        # 從KOL角色紀錄表獲取帳號密碼
        print("📋 獲取KOL帳號密碼...")
        kol_credentials = {}
        try:
            kol_data = sheets_client.read_sheet("KOL 角色紀錄表")
            if kol_data and len(kol_data) > 1:
                for row in kol_data[1:]:  # 跳過標題行
                    if len(row) >= 7:
                        kol_serial = row[0]  # 序號
                        email = row[5]      # Email(帳號)
                        password = row[6]    # 密碼
                        kol_credentials[kol_serial] = {
                            'email': email,
                            'password': password
                        }
                print(f"✅ 成功獲取 {len(kol_credentials)} 個KOL的帳號密碼")
            else:
                print("❌ 無法獲取KOL角色紀錄表")
                return
        except Exception as e:
            print(f"❌ 獲取KOL帳號密碼失敗: {e}")
            return
        
        # 為每個KOL建立登入token快取
        kol_tokens = {}
        
        for i, post in enumerate(posts_to_publish, 1):
            print(f"\n📝 發佈第 {i} 篇貼文: {post['stock_name']}({post['stock_id']})")
            print(f"   KOL: {post['kol_nickname']} ({post['kol_serial']})")
            print(f"   標題: {post['title']}")
            
            try:
                # 檢查是否需要為此KOL登入
                kol_serial = post['kol_serial']
                if kol_serial not in kol_tokens:
                    print(f"   🔐 正在為KOL {kol_serial} 登入CMoney...")
                    
                    # 從KOL角色紀錄表獲取帳號密碼
                    if kol_serial not in kol_credentials:
                        print(f"   ❌ 找不到KOL {kol_serial} 的帳號密碼")
                        continue
                    
                    cmoney_email = kol_credentials[kol_serial]['email']
                    cmoney_password = kol_credentials[kol_serial]['password']
                    
                    credentials = LoginCredentials(
                        email=cmoney_email,
                        password=cmoney_password
                    )
                    
                    try:
                        access_token = await cmoney_client.login(credentials)
                        kol_tokens[kol_serial] = access_token
                        print(f"   ✅ KOL {kol_serial} 登入成功")
                    except Exception as e:
                        print(f"   ❌ KOL {kol_serial} 登入失敗: {e}")
                        continue
                
                # 準備文章數據
                # 構建文章數據
                article_data = ArticleData(
                    title=post['title'],
                    text=post['content'],
                    community_topic={"id": "1cc70c18-f50f-420d-aecc-8dde575f3e79"},  # 使用記憶體股話題ID
                    commodity_tags=[{
                        "type": "Stock",
                        "key": post['stock_id'],
                        "bullOrBear": 0
                    }]
                )
                
                # 發佈文章
                print("   🔄 正在發佈...")
                publish_result = await cmoney_client.publish_article(
                    access_token=kol_tokens[kol_serial].token,
                    article=article_data
                )
                
                if publish_result.success:
                    print(f"   ✅ 發佈成功!")
                    print(f"   📄 Article ID: {publish_result.post_id}")
                    print(f"   🔗 Article URL: {publish_result.post_url}")
                    
                    # 更新Google Sheets
                    print("   🔄 更新Google Sheets...")
                    row_index = post['row_index']
                    
                    # 更新狀態和文章資訊
                    sheets_client.update_cell("貼文紀錄表", f"E{row_index + 1}", "published")  # status
                    sheets_client.update_cell("貼文紀錄表", f"F{row_index + 1}", datetime.now().isoformat())  # publish_time
                    sheets_client.update_cell("貼文紀錄表", f"G{row_index + 1}", publish_result.post_id)  # articleid
                    sheets_client.update_cell("貼文紀錄表", f"H{row_index + 1}", publish_result.post_url)  # platform_post_url
                    sheets_client.update_cell("貼文紀錄表", f"I{row_index + 1}", "success")  # publish_status
                    
                    print("   ✅ Google Sheets更新完成")
                    published_count += 1
                    
                else:
                    print(f"   ❌ 發佈失敗: {publish_result.error_message}")
                    
                    # 更新失敗狀態
                    row_index = post['row_index']
                    sheets_client.update_cell("貼文紀錄表", f"E{row_index + 1}", "failed")  # status
                    sheets_client.update_cell("貼文紀錄表", f"F{row_index + 1}", datetime.now().isoformat())  # publish_time
                    sheets_client.update_cell("貼文紀錄表", f"G{row_index + 1}", "")  # articleid
                    sheets_client.update_cell("貼文紀錄表", f"H{row_index + 1}", "")  # platform_post_url
                    sheets_client.update_cell("貼文紀錄表", f"I{row_index + 1}", "failed")  # publish_status
                    
                    failed_count += 1
                
            except Exception as e:
                print(f"   ❌ 發佈過程出錯: {e}")
                failed_count += 1
        
        print(f"\n🎉 發佈完成!")
        print(f"📊 成功發佈: {published_count} 篇")
        print(f"📊 發佈失敗: {failed_count} 篇")
        print(f"📊 總計處理: {len(posts_to_publish)} 篇")
        
        if published_count > 0:
            print("✅ 所有成功發佈的文章ID和URL已更新到Google Sheets")
        
    except Exception as e:
        print(f"❌ 發佈過程失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(publish_17_posts())
