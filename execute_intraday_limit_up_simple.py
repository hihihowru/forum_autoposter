#!/usr/bin/env python3
"""
盤中漲停機器人 - 簡化版本
跳過內容生成，只測試基本流程
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
from src.services.flow.flow_config import FlowConfig

async def main():
    """主執行函數"""
    print("🚀 啟動盤中漲停機器人 (簡化版本)...")
    
    try:
        print("📋 步驟 1: 初始化服務...")
        # 初始化服務
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
        )
        print("✅ Google Sheets 客戶端初始化成功")
        
        print("📋 步驟 2: 解析股票數據...")
        # 從用戶提供的數據中提取股票代號和詳細資訊
        stock_data = '''1 仲琦 2419.TW 25.30 2.30 10.00% 25.30 23.20 2.10 3,274 0.8149
2 精成科 6191.TW 148.50 13.50 10.00% 148.50 130.50 18.00 55,427 78.3840
3 越峰 8121.TWO 25.30 2.30 10.00% 25.30 23.40 1.90 1,524 0.3820
4 昇佳電子 6732.TWO 198.50 18.00 9.97% 198.50 188.00 10.50 344 0.6774
5 東友 5438.TWO 28.15 2.55 9.96% 28.15 26.10 2.05 10,555 2.8943'''

        # 解析股票詳細資訊
        stocks_info = []
        for line in stock_data.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 10:
                rank = int(parts[0])
                stock_name = parts[1]
                stock_code = parts[2].split('.')[0]  # 提取數字部分
                current_price = float(parts[3])
                change_amount = float(parts[4])
                change_percent = float(parts[5].replace('%', ''))
                high_price = float(parts[6])
                low_price = float(parts[7])
                price_diff = float(parts[8])
                volume = int(parts[9].replace(',', ''))
                turnover = float(parts[10]) if len(parts) > 10 else 0
                
                stock_info = {
                    'rank': rank,
                    'stock_name': stock_name,
                    'stock_id': stock_code,
                    'current_price': current_price,
                    'change_amount': change_amount,
                    'change_percent': change_percent,
                    'high_price': high_price,
                    'low_price': low_price,
                    'price_diff': price_diff,
                    'volume': volume,
                    'turnover': turnover,
                    'limit_up_time': datetime.now().isoformat()
                }
                stocks_info.append(stock_info)
        
        print(f"✅ 解析到 {len(stocks_info)} 檔漲停股票")
        print("前5檔股票:", [f"{s['stock_id']}({s['stock_name']})" for s in stocks_info[:5]])
        
        print("📋 步驟 3: 配置流程...")
        # 配置流程 - 禁用內容生成
        config = FlowConfig(
            enable_content_generation=False,  # 禁用內容生成
            enable_sheets_recording=True,
            max_posts_per_kol=3,
            content_style="analysis"
        )
        print("✅ 流程配置完成")
        
        print("📋 步驟 4: 創建話題數據...")
        # 直接使用股票資訊創建話題
        topics = []
        for stock in stocks_info:
            topic = {
                'id': f"intraday_limit_up_{stock['stock_id']}",
                'title': f"{stock['stock_name']} 盤中漲停！漲幅 {stock['change_percent']:.1f}%",
                'content': f"{stock['stock_name']} 盤中強勢漲停，漲幅達 {stock['change_percent']:.1f}%，成交量 {stock['volume']:,} 張",
                'stock_data': {
                    'has_stocks': True,
                    'stocks': [{
                        'stock_id': stock['stock_id'],
                        'stock_name': stock['stock_name'],
                        'current_price': stock['current_price'],
                        'change_amount': stock['change_amount'],
                        'change_percent': stock['change_percent'],
                        'high_price': stock['high_price'],
                        'low_price': stock['low_price'],
                        'volume': stock['volume'],
                        'turnover': stock['turnover'],
                        'rank': stock['rank'],
                        'limit_up_time': stock['limit_up_time']
                    }]
                },
                'intraday_data': {
                    'is_intraday': True,
                    'limit_up_time': stock['limit_up_time'],
                    'change_percent': stock['change_percent'],
                    'volume': stock['volume']
                }
            }
            topics.append(topic)
        
        print(f"✅ 創建了 {len(topics)} 個話題")
        
        print("📋 步驟 5: 模擬貼文生成...")
        # 模擬生成貼文
        mock_posts = []
        for i, stock in enumerate(stocks_info[:3]):  # 只生成前3檔的貼文
            post = {
                'task_id': f"limit_up_{stock['stock_id']}_TWO_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'topic_id': f"intraday_limit_up_{stock['stock_id']}",
                'kol_serial': 200 + i,
                'kol_nickname': f"測試KOL{i+1}",
                'title': f"{stock['stock_name']} 盤中漲停！漲幅 {stock['change_percent']:.1f}%",
                'content': f"{stock['stock_name']} 盤中強勢漲停，漲幅達 {stock['change_percent']:.1f}%，成交量 {stock['volume']:,} 張。技術面強勢，建議關注後續走勢。",
                'hashtags': f"#{stock['stock_name']} #盤中漲停 #技術分析",
                'stock_info': f"{stock['stock_id']}({stock['stock_name']})",
                'generated_at': datetime.now().isoformat(),
                'status': 'ready'
            }
            mock_posts.append(post)
        
        print(f"✅ 模擬生成 {len(mock_posts)} 篇貼文")
        
        print("📋 步驟 6: 記錄到 Google Sheets...")
        try:
            # 記錄到貼文記錄表
            for post in mock_posts:
                row_data = [
                    post['task_id'],
                    post['topic_id'],
                    post['kol_serial'],
                    post['kol_nickname'],
                    post['title'],
                    post['content'],
                    post['hashtags'],
                    post['stock_info'],
                    post['generated_at'],
                    post['status']
                ]
                
                # 寫入貼文記錄表
                sheets_client.append_sheet(
                    sheet_name="貼文記錄表",
                    values=[row_data]
                )
                print(f"✅ 記錄貼文: {post['title'][:30]}...")
            
            print("✅ 所有貼文已記錄到 Google Sheets")
            
        except Exception as e:
            print(f"❌ 記錄到 Google Sheets 失敗: {e}")
        
        print("✅ 流程執行完成！")
        print(f"📈 總共處理 {len(stocks_info)} 檔股票")
        print(f"📝 生成 {len(mock_posts)} 篇貼文")
        print(f"👥 處理話題數: {len(topics)}")
        
        print(f"\n📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 盤中漲停機器人執行完成！")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
