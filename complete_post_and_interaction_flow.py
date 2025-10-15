#!/usr/bin/env python3
"""
完整的發文和互動數據收集流程
1. 生成內容
2. 發文到CMoney
3. 獲取文章ID
4. 收集互動數據
5. 更新Google Sheets
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, ArticleData
from src.services.content.content_generator import ContentGenerator, ContentRequest

async def main():
    """主執行函數"""
    print("🚀 完整的發文和互動數據收集流程...")
    
    try:
        print("📋 步驟 1: 初始化服務...")
        # 初始化服務
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
        )
        print("✅ Google Sheets 客戶端初始化成功")
        
        cmoney_client = CMoneyClient()
        print("✅ CMoney 客戶端初始化成功")
        
        content_generator = ContentGenerator()
        print("✅ 內容生成器初始化成功")
        
        print("📋 步驟 2: 登入CMoney...")
        # 登入CMoney
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password=os.getenv('CMONEY_PASSWORD')
        )
        
        token = await cmoney_client.login(credentials)
        print(f"✅ 登入成功: {token.token[:20]}...")
        
        print("📋 步驟 3: 生成內容...")
        # 生成內容
        content_request = ContentRequest(
            topic_title="仲琦 盤中漲停！漲幅 10.0%",
            topic_keywords="盤中漲停, 技術分析, 籌碼面, 基本面",
            kol_persona="技術分析專家",
            kol_nickname="川川哥",
            content_type="investment",
            target_audience="active_traders",
            market_data={
                'has_stock': True,
                'stock_id': '2419',
                'stock_name': '仲琦',
                'current_price': 25.30,
                'change_percent': 10.0,
                'volume': 3274
            }
        )
        
        result = content_generator.generate_complete_content(content_request)
        
        if not result.success:
            print(f"❌ 內容生成失敗: {result.error_message}")
            return
        
        print("✅ 內容生成成功！")
        print(f"📝 標題: {result.title}")
        print(f"📄 內容: {result.content[:100]}...")
        
        print("📋 步驟 4: 發文到CMoney...")
        # 準備發文數據
        article_data = ArticleData(
            title=result.title,
            text=result.content,
            commodity_tags=[{"type": "Stock", "key": "2419", "bullOrBear": 0}]
        )
        
        # 發文
        publish_result = await cmoney_client.publish_article(token.token, article_data)
        
        if not publish_result.success:
            print(f"❌ 發文失敗: {publish_result.error_message}")
            return
        
        print("✅ 發文成功！")
        print(f"📝 文章ID: {publish_result.post_id}")
        print(f"🔗 文章URL: {publish_result.post_url}")
        
        print("📋 步驟 5: 收集互動數據...")
        # 等待一下讓數據更新
        await asyncio.sleep(5)
        
        # 收集互動數據
        try:
            # 獲取文章互動數據
            interaction_data = await cmoney_client.get_article_interactions(token.token, publish_result.post_id)
            
            if interaction_data:
                likes_count = interaction_data.likes
                comments_count = interaction_data.comments
                collections_count = interaction_data.collections
                total_interactions = interaction_data.total_interactions
                
                print(f"✅ 互動數據收集成功:")
                print(f"   👍 按讚數: {likes_count}")
                print(f"   💬 留言數: {comments_count}")
                print(f"   📚 收藏數: {collections_count}")
                print(f"   📊 總互動數: {total_interactions}")
                
                # 更新Google Sheets
                print("📋 步驟 6: 更新Google Sheets...")
                
                # 更新Google Sheets
                print("📋 步驟 6: 更新Google Sheets...")
                
                # 更新貼文記錄表
                post_id = f"limit_up_2419_COMPLETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                row_data = [
                    post_id,  # 貼文ID
                    '200',    # KOL Serial
                    '川川哥',  # KOL 暱稱
                    '9505546', # Member ID
                    '仲琦',   # 股票名稱
                    '2419',   # 股票代號
                    'test_intraday_limit_up_2419',  # 話題ID
                    'test_intraday_limit_up_2419',  # Topic ID
                    result.title,  # 生成標題
                    '',       # 生成標籤
                    result.content,  # 生成內容
                    '[{"type": "Stock", "key": "2419", "bullOrBear": 0}]',  # commodity_tags
                    datetime.now().isoformat(),  # 生成時間
                    datetime.now().isoformat(),  # 發文時間
                    publish_result.post_id,  # 平台發文ID
                    publish_result.post_url,  # 平台發文URL
                    'published',  # 發文狀態
                    '',       # 錯誤訊息
                    likes_count,  # 按讚數
                    comments_count,  # 留言數
                    datetime.now().isoformat()  # 最後更新時間
                ]
                
                sheets_client.append_sheet(
                    sheet_name="貼文記錄表",
                    values=[row_data]
                )
                print("✅ 貼文記錄已更新")
                
                # 更新互動回饋表
                interaction_data = [
                    publish_result.post_id,  # Article ID
                    '9505546',              # Member ID
                    '川川哥',               # 暱稱
                    result.title,           # 標題
                    result.content,         # 生成內文
                    'test_intraday_limit_up_2419',  # Topic ID
                    'TRUE',                 # 是否為熱門話題
                    datetime.now().isoformat(),  # 發文時間
                    datetime.now().isoformat(),  # 最後更新時間
                    likes_count,            # 按讚數
                    comments_count,         # 留言數
                    ''                      # 收集錯誤訊息
                ]
                
                sheets_client.append_sheet(
                    sheet_name="互動回饋_1hr",
                    values=[interaction_data]
                )
                print("✅ 互動回饋記錄已更新")
                
            else:
                print("⚠️ 無法獲取文章詳情")
                
        except Exception as e:
            print(f"❌ 收集互動數據失敗: {e}")
        
        print("✅ 流程執行完成！")
        print(f"📈 文章ID: {publish_result.post_id}")
        print(f"🔗 文章URL: {publish_result.post_url}")
        print(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
