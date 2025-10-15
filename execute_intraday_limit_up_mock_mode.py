#!/usr/bin/env python3
"""
盤中漲停機器人 - 模擬模式版本
暫時跳過 OpenAI API 調用，使用預設內容
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

async def main():
    """主執行函數"""
    print("🚀 啟動盤中漲停機器人 (模擬模式)...")
    
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
    
    print(f"📊 解析到 {len(stocks_info)} 檔漲停股票")
    print("前5檔股票:", [f"{s['stock_id']}({s['stock_name']})" for s in stocks_info[:5]])
    
    # 生成模擬貼文
    generated_posts = []
    kol_profiles = [
        {"serial": 200, "nickname": "川川哥", "persona": "技術派"},
        {"serial": 201, "nickname": "韭割哥", "persona": "總經派"},
        {"serial": 202, "nickname": "消息哥", "persona": "消息派"}
    ]
    
    for i, stock in enumerate(stocks_info):
        kol = kol_profiles[i % len(kol_profiles)]
        
        # 根據 KOL 角色生成不同風格的貼文
        if kol["persona"] == "技術派":
            title = f"📈 {stock['stock_name']} 技術面強勢突破！"
            content = f"""
{stock['stock_name']} 今日強勢漲停！📈

🔍 技術分析：
• 漲幅：{stock['change_percent']:.1f}%
• 成交量：{stock['volume']:,} 張
• 價差：{stock['price_diff']:.2f} 元

💡 技術指標顯示：
• 突破重要壓力位
• 成交量放大
• 均線多頭排列

#技術分析 #漲停 #台股
"""
        elif kol["persona"] == "總經派":
            title = f"📊 {stock['stock_name']} 基本面支撐強勁"
            content = f"""
{stock['stock_name']} 基本面支撐下強勢上漲！📊

📈 市場表現：
• 漲幅：{stock['change_percent']:.1f}%
• 成交金額：{stock['turnover']:.2f} 億
• 價格區間：{stock['low_price']:.2f} - {stock['high_price']:.2f}

💼 基本面分析：
• 產業前景看好
• 營收成長動能強
• 估值具吸引力

#基本面 #投資 #台股
"""
        else:  # 消息派
            title = f"🔥 {stock['stock_name']} 重大利多消息！"
            content = f"""
{stock['stock_name']} 重大利多消息發酵！🔥

🚀 市場反應：
• 漲幅：{stock['change_percent']:.1f}%
• 成交量暴增：{stock['volume']:,} 張
• 價格突破：{stock['current_price']:.2f} 元

📰 消息面：
• 重大利多消息
• 市場資金追捧
• 後續動能可期

#利多 #消息面 #台股
"""
        
        post = {
            'task_id': f"limit_up_{stock['stock_id']}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'kol_serial': kol["serial"],
            'kol_nickname': kol["nickname"],
            'stock_id': stock['stock_id'],
            'stock_name': stock['stock_name'],
            'title': title,
            'content': content,
            'status': 'ready_to_gen',
            'created_at': datetime.now().isoformat()
        }
        generated_posts.append(post)
    
    # 記錄到 Google Sheets
    try:
        for post in generated_posts:
            record = [
                post['task_id'],           # 貼文ID
                str(post['kol_serial']),   # KOL Serial
                post['kol_nickname'],      # KOL 暱稱
                "",                        # KOL ID
                "",                        # Persona
                "investment",              # Content Type
                "1",                       # 已派發TopicIndex
                f"limit_up_{post['stock_id']}",  # 已派發TopicID
                f"{post['stock_name']} 盤中漲停",  # 已派發TopicTitle
                f"{post['stock_name']}, 漲停, 台股",  # 已派發TopicKeywords
                post['content'],           # 生成內容
                post['status'],            # 發文狀態
                post['created_at'],        # 上次排程時間
                "",                        # 發文時間戳記
                "",                        # 最近錯誤訊息
                "",                        # 平台發文ID
                "",                        # 平台發文URL
                f"{post['stock_id']}({post['stock_name']})"  # 分配股票資訊
            ]
            
            sheets_client.append_sheet('貼文記錄表', [record])
            print(f"✅ 記錄貼文: {post['task_id']} - {post['stock_name']}")
        
        print(f"✅ 模擬模式執行完成！")
        print(f"📈 總共處理 {len(stocks_info)} 檔股票")
        print(f"📝 生成 {len(generated_posts)} 篇貼文")
        print(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 記錄到 Google Sheets 失敗: {e}")
        print("但貼文已生成完成")

if __name__ == "__main__":
    asyncio.run(main())


