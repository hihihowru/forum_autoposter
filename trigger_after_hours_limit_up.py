#!/usr/bin/env python3
"""
觸發AFTER_HOURS_LIMIT_UP工作流程
生成兩個支線共15檔股票的個人化內容
確認Finlab數據是今日的
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_finlab_data():
    """測試Finlab數據是否為今日的"""
    
    print("🔍 檢查Finlab數據是否為今日的...")
    
    try:
        # 初始化主工作流程引擎
        engine = MainWorkflowEngine()
        
        # 獲取今日漲停股票數據
        limit_up_stocks = await engine._get_today_limit_up_stocks()
        
        if limit_up_stocks:
            print(f"✅ 成功獲取今日漲停股票數據: {len(limit_up_stocks)} 檔")
            print(f"📅 數據日期: {datetime.now().strftime('%Y-%m-%d')}")
            
            # 顯示前5檔股票
            print("\n📊 前5檔漲停股票:")
            for i, stock in enumerate(limit_up_stocks[:5], 1):
                print(f"{i}. {stock.stock_name}({stock.stock_id}) - 漲幅: {stock.change_percent:.2f}% - 成交金額: {stock.volume_amount:.4f}億")
            
            # 分離有量和無量
            high_volume = [s for s in limit_up_stocks if s.volume_amount >= 1.0]
            low_volume = [s for s in limit_up_stocks if s.volume_amount < 1.0]
            
            print(f"\n📈 高量股票(≥1億): {len(high_volume)} 檔")
            print(f"📉 低量股票(<1億): {len(low_volume)} 檔")
            
            return True
        else:
            print("⚠️ 無法獲取今日漲停股票數據，將使用樣本數據")
            return False
            
    except Exception as e:
        print(f"❌ 檢查Finlab數據失敗: {e}")
        return False

async def trigger_after_hours_limit_up():
    """觸發AFTER_HOURS_LIMIT_UP工作流程"""
    
    print("🚀 觸發AFTER_HOURS_LIMIT_UP工作流程")
    print("=" * 60)
    
    try:
        # 初始化主工作流程引擎
        engine = MainWorkflowEngine()
        
        # 配置工作流程
        config = WorkflowConfig(
            workflow_type=WorkflowType.AFTER_HOURS_LIMIT_UP,
            max_posts_per_topic=15,  # 兩個支線共15檔
            enable_content_generation=True,
            enable_publishing=False,  # 先不發布，只生成內容
            enable_learning=True,
            enable_quality_check=True,
            enable_sheets_recording=True,
            retry_on_failure=True,
            max_retries=3
        )
        
        print(f"📋 工作流程配置:")
        print(f"   類型: {config.workflow_type.value}")
        print(f"   最大貼文數: {config.max_posts_per_topic}")
        print(f"   內容生成: {config.enable_content_generation}")
        print(f"   發布: {config.enable_publishing}")
        print(f"   品質檢查: {config.enable_quality_check}")
        print(f"   Sheets記錄: {config.enable_sheets_recording}")
        
        # 執行工作流程
        print(f"\n⏰ 開始執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result = await engine.execute_workflow(config)
        
        print(f"\n⏰ 結束執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.success:
            print(f"\n✅ 工作流程執行成功!")
            print(f"📊 生成貼文: {result.total_posts_generated}")
            print(f"⏱️ 執行時間: {result.execution_time:.2f}秒")
            
            # 顯示生成結果摘要
            if result.generated_posts:
                print(f"\n📝 生成內容摘要:")
                print(f"   總計: {len(result.generated_posts)} 篇貼文")
                
                # 統計高量和低量
                high_volume_count = 0
                low_volume_count = 0
                
                for post in result.generated_posts:
                    if post.get('is_high_volume', False):
                        high_volume_count += 1
                    else:
                        low_volume_count += 1
                
                print(f"   高量股票: {high_volume_count} 篇")
                print(f"   低量股票: {low_volume_count} 篇")
                
                # 顯示前3篇貼文預覽
                print(f"\n📄 前3篇貼文預覽:")
                for i, post in enumerate(result.generated_posts[:3], 1):
                    stock = post.get('stock', {})
                    content = post.get('content', '')
                    print(f"{i}. {stock.get('stock_name', 'Unknown')}({stock.get('stock_id', 'Unknown')})")
                    print(f"   標題: {post.get('title', '無標題')}")
                    print(f"   內容預覽: {content[:100]}..." if content else "   內容: 無內容")
                    print()
        else:
            print(f"\n❌ 工作流程執行失敗")
            if result.errors:
                print(f"錯誤列表:")
                for error in result.errors:
                    print(f"  - {error}")
            if result.warnings:
                print(f"警告列表:")
                for warning in result.warnings:
                    print(f"  - {warning}")
    
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主執行函數"""
    
    print("🎯 AFTER_HOURS_LIMIT_UP 工作流程觸發器")
    print("=" * 60)
    
    # 1. 檢查Finlab數據
    finlab_available = await test_finlab_data()
    
    if not finlab_available:
        print("\n⚠️ 注意: 將使用樣本數據進行測試")
    
    print("\n" + "=" * 60)
    
    # 2. 觸發工作流程
    await trigger_after_hours_limit_up()
    
    print("\n🎉 執行完成!")

if __name__ == "__main__":
    asyncio.run(main())


