#!/usr/bin/env python3
"""
修正的批量生成今天盤中漲停文章並收集互動數據
確保同時記錄到貼文記錄表和互動回饋表
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
    print("🚀 修正的批量生成今天盤中漲停文章...")
    
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
        
        print("📋 步驟 3: 準備股票數據...")
        # 今天的盤中漲停股票（前5檔）
        stocks_data = [
            {'stock_id': '2419', 'stock_name': '仲琦', 'current_price': 25.30, 'change_percent': 10.0, 'volume': 3274},
            {'stock_id': '6191', 'stock_name': '精成科', 'current_price': 148.50, 'change_percent': 10.0, 'volume': 55427},
            {'stock_id': '8121', 'stock_name': '越峰', 'current_price': 25.30, 'change_percent': 10.0, 'volume': 1524},
            {'stock_id': '6732', 'stock_name': '昇佳電子', 'current_price': 198.50, 'change_percent': 9.97, 'volume': 344},
            {'stock_id': '5438', 'stock_name': '東友', 'current_price': 28.15, 'change_percent': 9.96, 'volume': 10555}
        ]
        
        print(f"✅ 準備處理 {len(stocks_data)} 檔股票")
        
        print("📋 步驟 4: 批量生成和發文...")
        published_posts = []
        
        for i, stock in enumerate(stocks_data):
            print(f"\n🔄 處理第 {i+1} 檔股票: {stock['stock_name']}...")
            
            try:
                # 生成內容
                content_request = ContentRequest(
                    topic_title=f"{stock['stock_name']} 盤中漲停！漲幅 {stock['change_percent']:.1f}%",
                    topic_keywords="盤中漲停, 技術分析, 籌碼面, 基本面",
                    kol_persona="技術分析專家",
                    kol_nickname="川川哥",
                    content_type="investment",
                    target_audience="active_traders",
                    market_data={
                        'has_stock': True,
                        'stock_id': stock['stock_id'],
                        'stock_name': stock['stock_name'],
                        'current_price': stock['current_price'],
                        'change_percent': stock['change_percent'],
                        'volume': stock['volume']
                    }
                )
                
                result = content_generator.generate_complete_content(content_request)
                
                if not result.success:
                    print(f"❌ {stock['stock_name']} 內容生成失敗: {result.error_message}")
                    continue
                
                print(f"✅ {stock['stock_name']} 內容生成成功")
                
                # 發文
                article_data = ArticleData(
                    title=result.title,
                    text=result.content,
                    commodity_tags=[{"type": "Stock", "key": stock['stock_id'], "bullOrBear": 0}]
                )
                
                publish_result = await cmoney_client.publish_article(token.token, article_data)
                
                if not publish_result.success:
                    print(f"❌ {stock['stock_name']} 發文失敗: {publish_result.error_message}")
                    continue
                
                print(f"✅ {stock['stock_name']} 發文成功: {publish_result.post_id}")
                
                # 等待一下讓數據更新
                await asyncio.sleep(3)
                
                # 收集互動數據
                interaction_data = await cmoney_client.get_article_interactions(token.token, publish_result.post_id)
                
                if interaction_data:
                    likes_count = interaction_data.likes
                    comments_count = interaction_data.comments
                    collections_count = interaction_data.collections
                    total_interactions = interaction_data.total_interactions
                    
                    print(f"📊 {stock['stock_name']} 互動數據: 讚={likes_count}, 留言={comments_count}, 收藏={collections_count}")
                    
                    # 記錄到貼文記錄表 (12列)
                    post_id = f"limit_up_{stock['stock_id']}_BATCH_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    post_row = [
                        post_id,  # 貼文ID
                        '200',    # KOL Serial
                        '川川哥',  # KOL 暱稱
                        stock['stock_name'],  # 股票名稱
                        stock['stock_id'],    # 股票代號
                        f'intraday_limit_up_{stock["stock_id"]}',  # 話題ID
                        publish_result.post_id,  # 平台發文ID
                        publish_result.post_url,  # 平台發文URL
                        result.title,  # 生成標題
                        result.content,  # 生成內容
                        f'[{{"type": "Stock", "key": "{stock["stock_id"]}", "bullOrBear": 0}}]',  # commodity_tags
                        'published'  # 發文狀態
                    ]
                    
                    sheets_client.append_sheet(
                        sheet_name="貼文記錄表",
                        values=[post_row]
                    )
                    print(f"✅ {stock['stock_name']} 貼文記錄已更新")
                    
                    # 記錄到互動回饋表
                    interaction_row = [
                        publish_result.post_id,  # Article ID
                        '9505546',              # Member ID
                        '川川哥',               # 暱稱
                        result.title,           # 標題
                        result.content,         # 生成內文
                        f'intraday_limit_up_{stock["stock_id"]}',  # Topic ID
                        'TRUE',                 # 是否為熱門話題
                        datetime.now().isoformat(),  # 發文時間
                        datetime.now().isoformat(),  # 最後更新時間
                        likes_count,            # 按讚數
                        comments_count,         # 留言數
                        ''                      # 收集錯誤訊息
                    ]
                    
                    sheets_client.append_sheet(
                        sheet_name="互動回饋_1hr",
                        values=[interaction_row]
                    )
                    print(f"✅ {stock['stock_name']} 互動回饋記錄已更新")
                    
                    published_posts.append({
                        'stock_name': stock['stock_name'],
                        'stock_id': stock['stock_id'],
                        'post_id': publish_result.post_id,
                        'post_url': publish_result.post_url,
                        'title': result.title,
                        'likes': likes_count,
                        'comments': comments_count,
                        'collections': collections_count,
                        'total_interactions': total_interactions
                    })
                    
                else:
                    print(f"⚠️ {stock['stock_name']} 無法獲取互動數據")
                
                # 等待一下再處理下一檔
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ {stock['stock_name']} 處理失敗: {e}")
                continue
        
        print("\n✅ 批量處理完成！")
        print(f"📈 總共成功發文 {len(published_posts)} 篇")
        
        print("\n📋 發文摘要:")
        for post in published_posts:
            print(f"  {post['stock_name']}({post['stock_id']}): {post['title'][:30]}...")
            print(f"    文章ID: {post['post_id']}, 讚: {post['likes']}, 留言: {post['comments']}")
        
        print(f"\n📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 批量盤中漲停文章生成完成！")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


