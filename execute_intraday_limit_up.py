#!/usr/bin/env python3
"""
執行盤中漲停股流程，生成貼文並更新到貼文紀錄
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

async def execute_intraday_limit_up_flow():
    """執行盤中漲停股流程"""
    
    print("🚀 執行盤中漲停股流程")
    print("=" * 60)
    
    try:
        # 1. 初始化服務
        print("🔧 初始化服務...")
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
        )
        flow_manager = create_unified_flow_manager(sheets_client)
        
        # 2. 載入漲停資料解析器
        print("\n📊 載入漲停資料解析器...")
        limit_up_parser = LimitUpDataParser()
        flow_manager.limit_up_parser = limit_up_parser
        
        # 3. 你提供的漲停資料
        print("\n📈 解析漲停資料...")
        limit_up_data = """
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
4
東友
5438.TWO
28.15
2.55
9.96%
28.15
26.10
2.05
10,423
2.8571
5
如興
4414.TW
11.60
1.05
9.95%
11.60
11.60
0.00
168
0.0195
6
江興鍛
4528.TWO
21.00
1.90
9.95%
21.00
20.10
0.90
271
0.0565
7
應廣
6716.TWO
48.60
4.40
9.95%
48.60
44.25
4.35
150
0.0714
8
立積
4968.TW
160.50
14.50
9.93%
160.50
149.50
11.00
7,027
10.9921
9
偉詮電
2436.TW
53.20
4.80
9.92%
53.20
49.30
3.90
4,264
2.2195
10
錦明
3230.TWO
56.50
5.10
9.92%
56.50
51.70
4.80
2,403
1.3441
11
德宏
5475.TWO
46.55
4.20
9.92%
46.55
41.30
5.25
4,447
2.0006
12
詠昇
6418.TWO
39.90
3.60
9.92%
39.90
36.85
3.05
2,710
1.0558
13
微程式
7721.TW
66.50
6.00
9.92%
66.50
64.30
2.20
221
0.1464
14
漢磊
3707.TWO
49.35
4.45
9.91%
49.35
46.20
3.15
11,717
5.6861
15
晟田
4541.TWO
63.20
5.70
9.91%
63.20
57.10
6.10
21,654
13.1033
16
世紀*
5314.TWO
88.80
8.00
9.90%
88.80
80.40
8.40
28,191
24.1904
17
沛亨
6291.TWO
172.00
15.50
9.90%
172.00
157.00
15.00
2,189
3.6386
18
懷特
4108.TW
15.55
1.40
9.89%
15.55
14.20
1.35
1,039
0.1587
19
佳凌
4976.TW
53.90
4.80
9.89%
53.90
48.70
5.20
14,905
7.7541
20
南茂
8150.TW
26.10
2.35
9.89%
26.10
25.10
1.00
9,946
2.5830
21
台船
2208.TW
20.60
1.85
9.87%
20.60
20.50
0.10
10,190
2.0991
22
攸泰科技
6928.TW
76.80
6.90
9.87%
76.80
69.60
7.20
3,868
2.9193
23
安克
4188.TWO
16.75
1.50
9.84%
16.75
16.00
0.75
414
0.0689
24
訊舟
3047.TW
22.35
2.00
9.83%
22.35
20.40
1.95
4,392
0.9596
25
連宇
2482.TW
21.80
1.95
9.82%
21.80
19.85
1.95
795
0.1710
26
利勤
4426.TW
11.20
1.00
9.80%
11.20
10.30
0.90
900
0.0996
27
銘旺科
2429.TW
105.50
9.40
9.78%
105.50
95.90
9.60
3,280
3.3752
28
為升
2231.TW
118.00
10.50
9.77%
118.00
107.50
10.50
3,280
3.3752
"""
        
        # 4. 解析漲停資料
        stock_data_list = limit_up_parser.parse_limit_up_data(limit_up_data)
        print(f"✅ 解析完成，共 {len(stock_data_list)} 檔股票")
        
        # 顯示前10檔股票
        for i, stock_data in enumerate(stock_data_list[:10]):
            print(f"   {i+1}. {stock_data['stock_name']} ({stock_data['stock_id']}) - 漲幅 {stock_data['change_percent']}%")
        
        # 5. 配置流程
        print("\n⚙️ 配置流程...")
        config = FlowConfig(
            flow_type="intraday_limit_up",
            max_assignments_per_topic=3,  # 每個話題最多分派給3個KOL
            enable_stock_analysis=True,
            enable_content_generation=True,  # 啟用內容生成
            enable_sheets_recording=True,    # 啟用Google Sheets記錄
            enable_publishing=False          # 不實際發文
        )
        
        # 6. 提取股票代號
        stock_ids = [stock['stock_id'] for stock in stock_data_list]
        print(f"📊 準備處理 {len(stock_ids)} 檔股票")
        
        # 7. 執行盤中漲停流程
        print("\n🚀 開始執行盤中漲停流程...")
        result = await flow_manager.execute_intraday_limit_up_flow(stock_ids, config)
        
        # 8. 顯示結果
        print(f"\n{'='*60}")
        print(f"🎯 盤中漲停流程執行結果")
        print(f"{'='*60}")
        print(f"✅ 成功: {'是' if result.success else '否'}")
        print(f"📊 處理話題數: {result.processed_topics}")
        print(f"📝 生成貼文數: {result.generated_posts}")
        print(f"⏱️  執行時間: {result.execution_time:.2f}秒")
        
        if result.errors:
            print(f"\n❌ 錯誤:")
            for error in result.errors:
                print(f"   - {error}")
        
        # 9. 預估貼文數量
        print(f"\n📈 預估貼文數量:")
        print(f"   股票數量: {len(stock_ids)}")
        print(f"   每個話題分派給: {config.max_assignments_per_topic} 個KOL")
        print(f"   預估總貼文數: {len(stock_ids) * config.max_assignments_per_topic}")
        print(f"   實際生成貼文數: {result.generated_posts}")
        
        print(f"\n{'='*60}")
        print("🎉 盤中漲停流程執行完成！")
        print("📝 貼文已更新到 Google Sheets 的貼文記錄表")
        
        return result
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(execute_intraday_limit_up_flow())


