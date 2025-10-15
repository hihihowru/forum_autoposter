#!/usr/bin/env python3
"""
盤中漲停機器人 - 模擬版本
使用真實的股票列表生成模擬貼文並記錄到 Google Sheets
"""

import asyncio
import sys
import os
from datetime import datetime
import random

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

async def main():
    """主執行函數"""
    print("🚀 啟動盤中漲停機器人（模擬版本）...")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file="./credentials/google-service-account.json",
        spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
    )
    
    # 從用戶提供的數據中提取股票代號和詳細資訊
    stock_data = '''1 仲琦 2419.TW 25.30 2.30 10.00% 25.30 23.20 2.10 3,274 0.8149
2 精成科 6191.TW 148.50 13.50 10.00% 148.50 130.50 18.00 55,427 78.3840
3 越峰 8121.TWO 25.30 2.30 10.00% 25.30 23.40 1.90 1,524 0.3820
4 昇佳電子 6732.TWO 198.50 18.00 9.97% 198.50 188.00 10.50 344 0.6774
5 東友 5438.TWO 28.15 2.55 9.96% 28.15 26.10 2.05 10,555 2.8943
6 如興 4414.TW 11.60 1.05 9.95% 11.60 11.60 0.00 179 0.0208
7 江興鍛 4528.TWO 21.00 1.90 9.95% 21.00 20.10 0.90 277 0.0578
8 應廣 6716.TWO 48.60 4.40 9.95% 48.60 44.25 4.35 170 0.0811
9 立積 4968.TW 160.50 14.50 9.93% 160.50 149.50 11.00 7,179 11.2361
10 偉詮電 2436.TW 53.20 4.80 9.92% 53.20 49.30 3.90 4,457 2.3222
11 錦明 3230.TWO 56.50 5.10 9.92% 56.50 51.70 4.80 2,447 1.3690
12 德宏 5475.TWO 46.55 4.20 9.92% 46.55 41.30 5.25 4,591 2.0676
13 詠昇 6418.TWO 39.90 3.60 9.92% 39.90 36.85 3.05 2,742 1.0686
14 欣普羅 6560.TWO 48.20 4.35 9.92% 48.20 43.15 5.05 1,110 0.5201
15 微程式 7721.TW 66.50 6.00 9.92% 66.50 64.30 2.20 225 0.1490
16 漢磊 3707.TWO 49.35 4.45 9.91% 49.35 46.20 3.15 11,964 5.8080
17 晟田 4541.TWO 63.20 5.70 9.91% 63.20 57.10 6.10 22,102 13.3864
18 世紀* 5314.TWO 88.80 8.00 9.90% 88.80 80.40 8.40 28,761 24.6965
19 沛亨 6291.TWO 172.00 15.50 9.90% 172.00 157.00 15.00 2,245 3.7349
20 佳凌 4976.TW 53.90 4.80 9.89% 53.90 48.70 5.20 15,101 7.8597
21 南茂 8150.TW 26.10 2.35 9.89% 26.10 25.10 1.00 10,210 2.6519
22 台船 2208.TW 20.60 1.85 9.87% 20.60 20.50 0.10 10,846 2.2343
23 宏碩系統 6895.TWO 306.00 27.50 9.87% 306.00 272.00 34.00 621 1.8240
24 攸泰科技 6928.TW 76.80 6.90 9.87% 76.80 69.60 7.20 3,994 3.0160
25 安克 4188.TWO 16.75 1.50 9.84% 16.75 16.00 0.75 424 0.0706
26 訊舟 3047.TW 22.35 2.00 9.83% 22.35 20.40 1.95 6,118 1.3454
27 連宇 2482.TW 21.80 1.95 9.82% 21.80 19.85 1.95 867 0.1867
28 利勤 4426.TW 11.20 1.00 9.80% 11.20 10.30 0.90 992 0.1099
29 銘旺科 2429.TW 105.50 9.40 9.78% 105.50 95.90 9.60 3,369 3.4691
30 為升 2231.TW 118.00 10.50 9.77% 118.00 107.50 10.50 4,005 4.6137
31 御嵿 3522.TWO 14.05 1.25 9.77% 14.05 12.80 1.25 429 0.0598
32 鮮活果汁-KY 1256.TW 157.50 14.00 9.76% 157.50 157.50 0.00 108 0.1701
33 融程電 3416.TW 197.00 17.50 9.75% 197.00 180.00 17.00 4,065 7.8604
34 斐成 3313.TWO 14.10 1.25 9.73% 14.10 13.00 1.10 1,113 0.1532
35 昇陽半導體 8028.TW 175.00 15.50 9.72% 175.00 158.00 17.00 28,972 48.9364
36 穩得 6761.TWO 169.50 15.00 9.71% 169.50 159.00 10.50 6,882 11.3126
37 朋程 8255.TWO 147.00 13.00 9.70% 147.00 135.00 12.00 5,266 7.5773
38 龍德造船 6753.TW 158.50 14.00 9.69% 158.50 155.00 3.50 2,569 4.0455
39 昶瑞機電 7642.TWO 124.50 11.00 9.69% 124.50 114.00 10.50 722 0.8829
40 亞航 2630.TW 72.50 6.40 9.68% 72.60 66.50 6.10 5,613 3.9420
41 中光電 5371.TWO 131.00 11.50 9.62% 131.00 118.00 13.00 70,315 88.4578'''

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
    
    print(f"📊 解析到 {len(stocks_info)} 檔漲停股票")
    print("前5檔股票:", [f"{s['stock_id']}({s['stock_name']})" for s in stocks_info[:5]])
    
    # KOL 角色列表
    kol_roles = ['籌碼派', '基本面派', '消息派', '綜合派']
    
    # 生成模擬貼文
    generated_posts = []
    
    try:
        print("🔄 開始生成模擬貼文...")
        
        # 為前20檔股票生成貼文
        for i, stock in enumerate(stocks_info[:20]):
            kol_role = random.choice(kol_roles)
            
            # 根據角色生成不同風格的標題和內容
            if kol_role == '籌碼派':
                title = f"📈 {stock['stock_name']} 籌碼面分析：成交量暴增{stock['volume']//1000}K張，主力進場明顯！"
                content = f"""
{stock['stock_name']} 今日強勢漲停，漲幅達 {stock['change_percent']:.1f}%！

📊 籌碼面分析：
• 成交量：{stock['volume']:,} 張（較前日暴增）
• 成交金額：{stock['turnover']:.2f} 億元
• 價差：{stock['price_diff']:.2f} 元
• 最高價：{stock['high_price']} 元

💡 投資建議：
從籌碼面來看，{stock['stock_name']} 今日成交量明顯放大，顯示有主力資金進場。建議投資人密切關注後續走勢，但也要注意風險控制。

#籌碼分析 #{stock['stock_id']} #{stock['stock_name']} #漲停股
                """.strip()
                
            elif kol_role == '基本面派':
                title = f"📋 {stock['stock_name']} 基本面分析：營收成長動能強勁，投資價值浮現"
                content = f"""
{stock['stock_name']} 今日漲停，讓我們從基本面角度分析：

📈 技術面表現：
• 漲幅：{stock['change_percent']:.1f}%
• 現價：{stock['current_price']} 元
• 成交量：{stock['volume']:,} 張

🔍 基本面觀察：
根據最新財報顯示，{stock['stock_name']} 營收成長動能強勁，毛利率維持穩定。公司基本面穩健，長期投資價值浮現。

⚠️ 風險提醒：
雖然基本面良好，但投資人仍需注意市場波動風險，建議分批布局。

#基本面分析 #{stock['stock_id']} #{stock['stock_name']} #投資分析
                """.strip()
                
            elif kol_role == '消息派':
                title = f"🔥 {stock['stock_name']} 最新消息：重大利多發酵，股價強勢表態！"
                content = f"""
{stock['stock_name']} 今日強勢漲停！重大利多消息發酵中！

🚀 最新消息：
據可靠消息指出，{stock['stock_name']} 近期有重大利多消息即將公布，市場資金提前卡位，今日股價強勢表態。

📊 盤面表現：
• 漲幅：{stock['change_percent']:.1f}%
• 成交量：{stock['volume']:,} 張
• 成交金額：{stock['turnover']:.2f} 億元

💡 操作建議：
消息面利多發酵，建議投資人密切關注後續發展，但也要注意消息確認度。

#最新消息 #{stock['stock_id']} #{stock['stock_name']} #利多發酵
                """.strip()
                
            else:  # 綜合派
                title = f"🎯 {stock['stock_name']} 綜合分析：技術面、基本面、籌碼面全面解析"
                content = f"""
{stock['stock_name']} 今日漲停，讓我們從多個角度進行分析：

📊 技術面：
• 漲幅：{stock['change_percent']:.1f}%
• 現價：{stock['current_price']} 元
• 價差：{stock['price_diff']:.2f} 元

💰 籌碼面：
• 成交量：{stock['volume']:,} 張
• 成交金額：{stock['turnover']:.2f} 億元

📈 基本面：
公司營運穩健，營收成長動能強勁，長期投資價值浮現。

🎯 綜合建議：
技術面、基本面、籌碼面三方面都表現良好，建議投資人可適度關注，但要注意風險控制。

#綜合分析 #{stock['stock_id']} #{stock['stock_name']} #投資分析
                """.strip()
            
            post = {
                'kol_name': f"AI_{kol_role}_分析師",
                'stock_id': stock['stock_id'],
                'stock_name': stock['stock_name'],
                'title': title,
                'content': content,
                'kol_role': kol_role,
                'generated_at': datetime.now().isoformat(),
                'topic_id': f"intraday_limit_up_{stock['stock_id']}",
                'topic_title': f"{stock['stock_name']} 盤中漲停！漲幅 {stock['change_percent']:.1f}%"
            }
            
            generated_posts.append(post)
        
        print(f"✅ 貼文生成完成！")
        print(f"📈 總共處理 {len(stocks_info)} 檔股票")
        print(f"📝 生成 {len(generated_posts)} 篇貼文")
        
        # 記錄到 Google Sheets
        print("📝 開始記錄到 Google Sheets...")
        
        # 讀取現有的貼文記錄
        try:
            existing_records = await sheets_client.read_sheet("貼文記錄表", "A:Y")
            print(f"📋 現有記錄數: {len(existing_records) if existing_records else 0}")
        except Exception as e:
            print(f"⚠️ 讀取現有記錄失敗: {e}")
            existing_records = []
        
        # 準備新記錄
        new_records = []
        for post in generated_posts:
            record = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 生成時間
                post['kol_name'],  # KOL名稱
                post['stock_id'],  # 股票代號
                post['stock_name'],  # 股票名稱
                post['title'],  # 標題
                post['content'],  # 內容
                post['kol_role'],  # KOL角色
                "盤中漲停",  # 話題類型
                post['topic_id'],  # 話題ID
                post['topic_title'],  # 話題標題
                "已生成",  # 狀態
                "",  # 發布時間
                "",  # 發布平台
                "",  # 互動數據
                "",  # 備註
                "",  # 審核狀態
                "",  # 審核意見
                "",  # 修改記錄
                "",  # 標籤
                "",  # 分類
                "",  # 優先級
                "",  # 預計發布時間
                "",  # 實際發布時間
                "",  # 發布後數據
                ""   # 7日後收集時間
            ]
            new_records.append(record)
        
        # 寫入 Google Sheets
        if new_records:
            try:
                await sheets_client.write_sheet("貼文記錄表", "A:Y", new_records)
                print(f"✅ 成功記錄 {len(new_records)} 篇貼文到 Google Sheets")
            except Exception as e:
                print(f"❌ 記錄到 Google Sheets 失敗: {e}")
        
        # 顯示生成的貼文摘要
        print("\n📋 生成的貼文摘要:")
        for i, post in enumerate(generated_posts[:5], 1):
            print(f"{i}. {post['kol_name']} - {post['stock_id']} - {post['title'][:50]}...")
        
        if len(generated_posts) > 5:
            print(f"... 還有 {len(generated_posts) - 5} 篇貼文")
        
        print(f"\n📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 盤中漲停機器人（模擬版本）執行完成！")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


