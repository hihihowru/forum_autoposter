#!/usr/bin/env python3
"""
統一的觸發器介面
提供簡單易用的 API 來調用不同的觸發器
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.flow.unified_flow_manager import create_unified_flow_manager
from src.services.flow.trigger_manager import TriggerManager, TriggerType, TriggerConfig, TriggerResult
from src.utils.limit_up_data_parser import LimitUpDataParser

class UnifiedTriggerInterface:
    """統一的觸發器介面"""
    
    def __init__(self):
        """初始化觸發器介面"""
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")
        )
        self.flow_manager = create_unified_flow_manager(self.sheets_client)
        self.trigger_manager = TriggerManager(self.flow_manager)
        self.limit_up_parser = LimitUpDataParser()
        
        # 將解析器載入到流程管理器
        self.flow_manager.limit_up_parser = self.limit_up_parser
    
    async def trigger_trending_topics(self, 
                                    max_assignments: int = 3,
                                    enable_content_generation: bool = True,
                                    enable_sheets_recording: bool = True,
                                    enable_publishing: bool = False) -> TriggerResult:
        """觸發熱門話題流程"""
        config = TriggerConfig(
            trigger_type=TriggerType.TRENDING_TOPIC,
            data_source="auto_fetch",  # 自動從 CMoney 獲取
            max_assignments=max_assignments,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        return await self.trigger_manager.execute_trigger(config)
    
    async def trigger_limit_up_after_hours(self,
                                         max_assignments: int = 3,
                                         enable_content_generation: bool = True,
                                         enable_sheets_recording: bool = True,
                                         enable_publishing: bool = False) -> TriggerResult:
        """觸發盤後漲停流程"""
        config = TriggerConfig(
            trigger_type=TriggerType.LIMIT_UP_AFTER_HOURS,
            data_source="auto_fetch",  # 自動從 FinLab 獲取
            max_assignments=max_assignments,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        return await self.trigger_manager.execute_trigger(config)
    
    async def trigger_intraday_limit_up(self,
                                       stock_data: Union[str, List[str]],
                                       max_assignments: int = 3,
                                       enable_content_generation: bool = True,
                                       enable_sheets_recording: bool = True,
                                       enable_publishing: bool = False) -> TriggerResult:
        """觸發盤中漲停流程"""
        config = TriggerConfig(
            trigger_type=TriggerType.INTRADAY_LIMIT_UP,
            data_source=stock_data,
            max_assignments=max_assignments,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        return await self.trigger_manager.execute_trigger(config)
    
    async def trigger_custom_stocks(self,
                                   stock_ids: List[str],
                                   max_assignments: int = 3,
                                   enable_content_generation: bool = True,
                                   enable_sheets_recording: bool = True,
                                   enable_publishing: bool = False) -> TriggerResult:
        """觸發自定義股票流程"""
        config = TriggerConfig(
            trigger_type=TriggerType.CUSTOM_STOCKS,
            data_source=stock_ids,
            max_assignments=max_assignments,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        return await self.trigger_manager.execute_trigger(config)
    
    async def trigger_news_event(self,
                                news_title: str,
                                news_content: str = "",
                                max_assignments: int = 3,
                                enable_content_generation: bool = True,
                                enable_sheets_recording: bool = True,
                                enable_publishing: bool = False) -> TriggerResult:
        """觸發新聞事件流程"""
        news_data = {
            'title': news_title,
            'content': news_content or news_title,
            'type': 'news_event'
        }
        config = TriggerConfig(
            trigger_type=TriggerType.NEWS_EVENT,
            data_source=news_data,
            max_assignments=max_assignments,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        return await self.trigger_manager.execute_trigger(config)
    
    async def trigger_earnings_report(self,
                                    company_name: str,
                                    earnings_data: str = "",
                                    max_assignments: int = 3,
                                    enable_content_generation: bool = True,
                                    enable_sheets_recording: bool = True,
                                    enable_publishing: bool = False) -> TriggerResult:
        """觸發財報發布流程"""
        earnings_info = {
            'title': f"{company_name} 財報發布",
            'content': earnings_data or f"{company_name} 發布最新財報",
            'type': 'earnings_report'
        }
        config = TriggerConfig(
            trigger_type=TriggerType.EARNINGS_REPORT,
            data_source=earnings_info,
            max_assignments=max_assignments,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        return await self.trigger_manager.execute_trigger(config)
    
    def print_result(self, result: TriggerResult):
        """打印執行結果"""
        print(f"\n{'='*60}")
        print(f"🎯 觸發器執行結果: {result.trigger_type.value}")
        print(f"{'='*60}")
        print(f"✅ 成功: {'是' if result.success else '否'}")
        print(f"📊 處理項目: {result.processed_items}")
        print(f"📝 生成內容: {result.generated_content}")
        print(f"⏱️  執行時間: {result.execution_time:.2f}秒")
        
        if result.errors:
            print(f"\n❌ 錯誤:")
            for error in result.errors:
                print(f"   - {error}")
        
        if result.details:
            print(f"\n📋 詳細資訊:")
            for key, value in result.details.items():
                print(f"   {key}: {value}")
        
        print(f"{'='*60}")

# 簡化的使用範例
async def example_usage():
    """使用範例"""
    interface = UnifiedTriggerInterface()
    
    print("🚀 統一的觸發器介面使用範例")
    print("=" * 60)
    
    # 1. 盤中漲停觸發器
    print("\n1️⃣ 盤中漲停觸發器")
    stock_data = """
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
"""
    result1 = await interface.trigger_intraday_limit_up(
        stock_data=stock_data,
        max_assignments=2,
        enable_content_generation=False,  # 不生成內容
        enable_sheets_recording=False     # 不記錄到 Google Sheets
    )
    interface.print_result(result1)
    
    # 2. 自定義股票觸發器
    print("\n2️⃣ 自定義股票觸發器")
    result2 = await interface.trigger_custom_stocks(
        stock_ids=["2330", "2454", "2317"],
        max_assignments=1,
        enable_content_generation=False,
        enable_sheets_recording=False
    )
    interface.print_result(result2)
    
    # 3. 新聞事件觸發器
    print("\n3️⃣ 新聞事件觸發器")
    result3 = await interface.trigger_news_event(
        news_title="台積電宣布擴大投資先進製程",
        news_content="台積電今日宣布將投資數百億美元擴大先進製程產能，預計將帶動相關供應鏈成長。",
        max_assignments=1,
        enable_content_generation=False,
        enable_sheets_recording=False
    )
    interface.print_result(result3)
    
    # 4. 財報發布觸發器
    print("\n4️⃣ 財報發布觸發器")
    result4 = await interface.trigger_earnings_report(
        company_name="聯發科",
        earnings_data="聯發科公布第三季財報，營收年增15%，獲利表現優於預期。",
        max_assignments=1,
        enable_content_generation=False,
        enable_sheets_recording=False
    )
    interface.print_result(result4)

if __name__ == "__main__":
    asyncio.run(example_usage())


