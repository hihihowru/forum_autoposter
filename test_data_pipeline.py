#!/usr/bin/env python3
"""
測試數據調用支線
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.flow.unified_flow_manager import create_unified_flow_manager, FlowConfig
from src.utils.limit_up_data_parser import LimitUpDataParser

async def test_data_pipeline():
    """測試數據調用支線"""
    
    print("🧪 測試數據調用支線")
    print("=" * 60)
    
    try:
        # 1. 初始化服務
        print("🔧 初始化服務...")
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        flow_manager = create_unified_flow_manager(sheets_client)
        
        # 2. 測試漲停資料解析
        print("\n📊 測試漲停資料解析...")
        limit_up_parser = LimitUpDataParser()
        
        # 你提供的漲停資料（簡化版）
        test_data = """
漲幅排行
資料時間：2025/09/03
名次
股名/股號
股價
漲跌
漲跌幅(%)
最高
最低
價差
成交量(張)
成交金額(億)
1
仲琦
2419.TW
25.30
2.30
10.00%
25.30
23.20
2.10
3,149
0.7833
2
越峰
8121.TWO
25.30
2.30
10.00%
25.30
23.40
1.90
1,471
0.3685
3
昇佳電子
6732.TWO
198.50
18.00
9.97%
198.50
188.00
10.50
250
0.4908
"""
        
        stock_data_list = limit_up_parser.parse_limit_up_data(test_data)
        print(f"✅ 解析完成，共 {len(stock_data_list)} 檔股票")
        
        for stock_data in stock_data_list:
            print(f"  {stock_data['stock_name']} ({stock_data['stock_id']}) - 漲幅 {stock_data['change_percent']}%")
        
        # 3. 測試數據調用支線
        print("\n🔗 測試數據調用支線...")
        test_stock_ids = ["2419", "8121", "6732"]
        
        for stock_id in test_stock_ids:
            print(f"\n📈 測試股票: {stock_id}")
            
            # 測試各個數據支線
            revenue_data = await flow_manager._fetch_revenue_data(stock_id)
            print(f"  營收數據: {'✅' if revenue_data.get('success') else '❌'}")
            
            technical_data = await flow_manager._fetch_technical_data(stock_id)
            print(f"  技術數據: {'✅' if technical_data.get('success') else '❌'}")
            
            financial_data = await flow_manager._fetch_financial_data(stock_id)
            print(f"  財報數據: {'✅' if financial_data.get('success') else '❌'}")
            
            market_data = await flow_manager._fetch_market_data(stock_id)
            print(f"  市場數據: {'✅' if market_data.get('success') else '❌'}")
        
        # 4. 測試完整流程（不生成內容）
        print("\n🚀 測試完整流程...")
        config = FlowConfig(
            flow_type="intraday_limit_up",
            max_assignments_per_topic=1,
            enable_stock_analysis=True,
            enable_content_generation=False,  # 不生成內容
            enable_sheets_recording=False,    # 不記錄到 Google Sheets
            enable_publishing=False
        )
        
        # 將解析器載入到流程管理器
        flow_manager.limit_up_parser = limit_up_parser
        
        result = await flow_manager.execute_intraday_limit_up_flow(test_stock_ids, config)
        
        print(f"\n📊 完整流程測試結果:")
        print(f"   成功: {'✅' if result.success else '❌'}")
        print(f"   處理話題數: {result.processed_topics}")
        print(f"   執行時間: {result.execution_time:.2f}秒")
        print(f"   錯誤數: {len(result.errors)}")
        
        if result.errors:
            print(f"\n❌ 錯誤詳情:")
            for error in result.errors:
                print(f"   - {error}")
        
        print("\n" + "=" * 60)
        print("🎉 數據調用支線測試完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_data_pipeline())
