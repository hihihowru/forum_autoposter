#!/usr/bin/env python3
"""
重新生成26檔盤中急漲股貼文 - 使用正確的成交金額和張數數據
"""

import os
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 26檔盤中急漲股票數據 (2025/09/05) - 使用新的數據
SURGE_STOCKS = [
    "2344", "2642", "5508", "2408", "6789", "4989", "2323", "3323", "5234", "5345",
    "8034", "8358", "5309", "2740", "3543", "6510", "3535", "3059", "4577", "6781",
    "4166", "6727", "6223", "6515", "2509", "5314"
]

async def regenerate_corrected_posts():
    """重新生成26檔盤中急漲股貼文 - 使用正確的成交金額和張數數據"""
    print("🚀 開始重新生成26檔盤中急漲股貼文...")
    print("📊 使用2025/09/05最新真實數據")
    print("📈 成交量單位: 張")
    print("💰 成交金額單位: 億")
    print("🔍 包含Serper API漲停原因分析")
    print("🎯 修復標題問題:")
    print("   - 使用客製化標題而非通用標題")
    print("   - 移除內文重複標題")
    print("✅ 修復數據問題:")
    print("   - 成交量: 使用張數 (如220,989張)")
    print("   - 成交金額: 使用億元 (如48.5109億)")
    
    try:
        from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
        
        # 初始化工作流程引擎
        engine = MainWorkflowEngine()
        
        # 設定手動股票代號（26檔）
        os.environ['MANUAL_STOCK_IDS'] = ','.join(SURGE_STOCKS)
        
        print(f"📋 使用股票代號: {len(SURGE_STOCKS)}檔")
        print("📊 數據來源: 2025/09/05漲幅排行最新圖片")
        
        # 創建工作流程配置
        config = WorkflowConfig(
            workflow_type=WorkflowType.INTRADAY_SURGE_STOCKS,
            max_posts_per_topic=26
        )
        
        # 執行完整工作流程
        print("🎯 開始執行完整工作流程...")
        result = await engine.execute_workflow(config)
        
        print(f"✅ 工作流程完成！")
        print(f"📊 生成貼文數量: {result.total_posts_generated}")
        print(f"📊 發佈貼文數量: {result.total_posts_published}")
        
        if result.generated_posts:
            print(f"\n📝 生成的貼文摘要:")
            for i, post in enumerate(result.generated_posts, 1):
                print(f"  {i:2d}. {post['post_id']}")
                print(f"      股票: {post['stock_name']} ({post['stock_id']})")
                print(f"      KOL: {post['kol_id']}")
                print(f"      內容長度: {len(post['content'])} 字")
                print(f"      內容預覽: {post['content'][:100]}...")
                print()
        
        print("🎉 26檔盤中急漲股貼文重新生成完成！")
        print("✅ 已修復:")
        print("   - 數據準確性: 使用2025/09/05最新真實數據")
        print("   - 成交量單位: 正確使用張數 (如220,989張)")
        print("   - 成交金額單位: 正確使用億元 (如48.5109億)")
        print("   - 標題客製化: 使用多樣化標題模板")
        print("   - 移除內文重複標題: 直接開始內容")
        print("   - Serper API: 漲停原因分析和新聞連結")
        print("   - 邏輯統一: 與盤後漲停股邏輯一致")
        
    except Exception as e:
        print(f"❌ 生成失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(regenerate_corrected_posts())


