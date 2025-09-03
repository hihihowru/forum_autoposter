#!/usr/bin/env python3
"""
測試統一流程管理器
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

async def test_unified_flow_manager():
    """測試統一流程管理器"""
    
    print("🚀 測試統一流程管理器")
    print("=" * 60)
    
    try:
        # 1. 初始化 Google Sheets 客戶端
        print("📋 初始化 Google Sheets 客戶端...")
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 2. 創建統一流程管理器
        print("🔧 創建統一流程管理器...")
        flow_manager = create_unified_flow_manager(sheets_client)
        
        # 3. 測試熱門話題流程
        print("\n🔥 測試熱門話題流程...")
        trending_config = FlowConfig(
            flow_type="trending_topic",
            max_assignments_per_topic=2,
            enable_stock_analysis=True,
            enable_content_generation=True,
            enable_sheets_recording=True,
            enable_publishing=False
        )
        
        trending_result = await flow_manager.execute_trending_topic_flow(trending_config)
        
        print(f"✅ 熱門話題流程執行結果:")
        print(f"   成功: {trending_result.success}")
        print(f"   處理話題數: {trending_result.processed_topics}")
        print(f"   生成貼文數: {trending_result.generated_posts}")
        print(f"   執行時間: {trending_result.execution_time:.2f}秒")
        print(f"   錯誤數: {len(trending_result.errors)}")
        
        if trending_result.errors:
            print("   錯誤詳情:")
            for error in trending_result.errors:
                print(f"     - {error}")
        
        # 4. 測試漲停股流程（目前是空的實現）
        print("\n📈 測試漲停股流程...")
        limit_up_config = FlowConfig(
            flow_type="limit_up_stock",
            max_assignments_per_topic=2,
            enable_stock_analysis=True,
            enable_content_generation=True,
            enable_sheets_recording=True,
            enable_publishing=False
        )
        
        limit_up_result = await flow_manager.execute_limit_up_stock_flow(limit_up_config)
        
        print(f"✅ 漲停股流程執行結果:")
        print(f"   成功: {limit_up_result.success}")
        print(f"   處理話題數: {limit_up_result.processed_topics}")
        print(f"   生成貼文數: {limit_up_result.generated_posts}")
        print(f"   執行時間: {limit_up_result.execution_time:.2f}秒")
        print(f"   錯誤數: {len(limit_up_result.errors)}")
        
        if limit_up_result.errors:
            print("   錯誤詳情:")
            for error in limit_up_result.errors:
                print(f"     - {error}")
        
        # 5. 測試盤中漲停股流程
        print("\n🚀 測試盤中漲停股流程...")
        test_stock_ids = ["2330", "2317", "2454"]  # 測試股票代號
        intraday_config = FlowConfig(
            flow_type="intraday_limit_up",
            max_assignments_per_topic=2,
            enable_stock_analysis=True,
            enable_content_generation=True,
            enable_sheets_recording=True,
            enable_publishing=False
        )
        
        intraday_result = await flow_manager.execute_intraday_limit_up_flow(test_stock_ids, intraday_config)
        
        print(f"✅ 盤中漲停股流程執行結果:")
        print(f"   成功: {intraday_result.success}")
        print(f"   處理話題數: {intraday_result.processed_topics}")
        print(f"   生成貼文數: {intraday_result.generated_posts}")
        print(f"   執行時間: {intraday_result.execution_time:.2f}秒")
        print(f"   錯誤數: {len(intraday_result.errors)}")
        
        if intraday_result.errors:
            print("   錯誤詳情:")
            for error in intraday_result.errors:
                print(f"     - {error}")
        
        print("\n" + "=" * 60)
        print("🎉 統一流程管理器測試完成！")
        
        # 總結
        print("\n📊 測試總結:")
        print(f"   熱門話題流程: {'✅ 成功' if trending_result.success else '❌ 失敗'}")
        print(f"   漲停股流程: {'✅ 成功' if limit_up_result.success else '❌ 失敗'}")
        print(f"   盤中漲停股流程: {'✅ 成功' if intraday_result.success else '❌ 失敗'}")
        print(f"   總生成貼文: {trending_result.generated_posts + limit_up_result.generated_posts + intraday_result.generated_posts}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_unified_flow_manager())
