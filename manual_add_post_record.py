#!/usr/bin/env python3
"""
手動添加貼文記錄到貼文記錄表
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
    print("🚀 手動添加貼文記錄...")
    
    try:
        print("📋 步驟 1: 初始化服務...")
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
        )
        print("✅ Google Sheets 客戶端初始化成功")
        
        print("📋 步驟 2: 添加測試記錄...")
        # 添加一筆測試記錄到貼文記錄表
        test_row = [
            f"test_limit_up_2419_{datetime.now().strftime('%Y%m%d_%H%M%S')}",  # 貼文ID
            '200',    # KOL Serial
            '川川哥',  # KOL 暱稱
            '仲琦',   # 股票名稱
            '2419',   # 股票代號
            'test_intraday_limit_up_2419',  # 話題ID
            '173501944',  # 平台發文ID
            'https://www.cmoney.tw/forum/article/173501944',  # 平台發文URL
            '仲琦盤中漲停...籌碼面爆發...這波要噴啦...',  # 生成標題
            '仲琦盤中漲停...籌碼面爆發...這波要噴啦...\n\n仲琦今天盤中漲停，這根K棒真的讓我想起當初我抓到台積電的感覺...成交量暴增，籌碼面太香了啦！基本面有沒有跟上？這裡是不是要進場？大家覺得會不會有假突破？',  # 生成內容
            '[{"type": "Stock", "key": "2419", "bullOrBear": 0}]',  # commodity_tags
            'published'  # 發文狀態
        ]
        
        print(f"🔄 寫入數據: {test_row[0]}")
        print(f"數據長度: {len(test_row)}")
        
        sheets_client.append_sheet(
            sheet_name="貼文記錄表",
            values=[test_row]
        )
        print("✅ 測試記錄已添加")
        
        # 驗證記錄
        print("📋 步驟 3: 驗證記錄...")
        data = sheets_client.read_sheet('貼文記錄表', 'A1:Z30')
        latest = data[-1]
        print(f"最新記錄: {latest[0]} - {latest[2]} - {latest[3]}({latest[4]}) - 文章ID={latest[6]}")
        
        print("✅ 測試完成！")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


