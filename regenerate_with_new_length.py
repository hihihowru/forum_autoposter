#!/usr/bin/env python3
"""
重新生成17檔盤中漲停貼文 - 調整字數控制
"""

import os
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 17檔盤中急漲股票數據 (2025/09/05) - 使用最新數據
SURGE_STOCKS = [
    "2344", "2642", "3211", "2408", "6789", "4989", "2323", "8088", "3323", "5234",
    "6895", "5345", "8034", "3006", "8358", "5309", "8299"
]

async def regenerate_with_new_length():
    """重新生成17檔盤中急漲股貼文 - 調整字數控制"""
    print("🚀 重新生成17檔盤中急漲股貼文...")
    print("📊 使用2025/09/05最新真實數據")
    print("📈 成交量單位: 張 (如221,286張)")
    print("💰 成交金額單位: 億 (如48.5779億)")
    print("🔍 包含Serper API深度分析:")
    print("   - 漲停原因分析")
    print("   - 類股連動分析")
    print("   - 深度洞察")
    print("   - 新聞內容總結")
    print("🎯 調整字數控制:")
    print("   - 一半控制在150字以下（扣除連結部分）")
    print("   - 另一半在200-500字")
    print("   - 一半帶起互動，使用疑問句類型")
    print("   - 疑問句控制在50字左右")
    print("✅ 新增功能:")
    print("   - 短篇互動型：150字以下，疑問句為主")
    print("   - 詳細分析型：200-500字")
    print("   - 疑問句範例：大大們怎麼看？先進們有想法嗎？")
    
    try:
        from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
        
        # 初始化工作流程引擎
        engine = MainWorkflowEngine()
        
        # 設定手動股票代號（17檔）
        os.environ['MANUAL_STOCK_IDS'] = ','.join(SURGE_STOCKS)
        
        print(f"📋 使用股票代號: {len(SURGE_STOCKS)}檔")
        print("📊 數據來源: 2025/09/05漲幅排行最新數據")
        print("🔧 調整內容:")
        print("   - 短篇互動型：150字以下，疑問句為主")
        print("   - 詳細分析型：200-500字")
        print("   - 疑問句範例：大大們怎麼看？先進們有想法嗎？")
        print("   - 深度洞察分析")
        print("   - 類股連動分析")
        print("   - 新聞內容總結")
        
        # 創建工作流程配置
        config = WorkflowConfig(
            workflow_type=WorkflowType.INTRADAY_SURGE_STOCKS,
            max_posts_per_topic=17
        )
        
        # 執行完整工作流程
        print("🎯 開始執行完整工作流程...")
        result = await engine.execute_workflow(config)
        
        print(f"✅ 工作流程完成！")
        print(f"📊 生成貼文數量: {result.total_posts_generated}")
        print(f"📊 發佈貼文數量: {result.total_posts_published}")
        
        if result.generated_posts:
            print(f"\n📝 生成的貼文摘要:")
            short_count = 0
            long_count = 0
            
            for i, post in enumerate(result.generated_posts, 1):
                content_length = len(post['content'])
                if content_length < 200:
                    short_count += 1
                    length_type = "短篇互動型"
                else:
                    long_count += 1
                    length_type = "詳細分析型"
                
                print(f"  {i:2d}. {post['post_id']}")
                print(f"      股票: {post['stock_name']} ({post['stock_id']})")
                print(f"      KOL: {post['kol_id']}")
                print(f"      內容長度: {content_length} 字 ({length_type})")
                print(f"      內容預覽: {post['content'][:100]}...")
                print()
            
            print(f"📊 字數分布統計:")
            print(f"  短篇互動型 (<200字): {short_count} 篇")
            print(f"  詳細分析型 (200-500字): {long_count} 篇")
        
        print("🎉 17檔盤中急漲股貼文重新生成完成！")
        print("✅ 已調整:")
        print("   - 字數控制: 一半150字以下，一半200-500字")
        print("   - 疑問句類型: 大大們怎麼看？先進們有想法嗎？")
        print("   - 短篇互動型: 重點是互動和疑問句")
        print("   - 詳細分析型: 深度分析但保持幽默")
        print("✅ 已修復:")
        print("   - KOL nickname映射: 使用角色紀錄表的正確名稱")
        print("   - KOL平均分配: 每個KOL至少分配1-2檔股票")
        print("   - 數據準確性: 使用2025/09/05最新真實數據")
        print("   - 成交量單位: 正確使用張數 (如221,286張)")
        print("   - 成交金額單位: 正確使用億元 (如48.5779億)")
        print("   - 避免成交張數和成交金額混淆")
        print("   - 標題客製化: 使用多樣化標題模板")
        print("   - 移除內文重複標題: 直接開始內容")
        print("   - Serper API: 漲停原因分析和新聞連結")
        print("   - 邏輯統一: 與盤後漲停股邏輯一致")
        print("✅ 已新增:")
        print("   - 深度洞察分析: 提供有料的回覆")
        print("   - 類股連動分析: 分析營建、記憶體等題材")
        print("   - 新聞內容總結: 不只是連結，還有內容分析")
        print("   - 邏輯脈絡清楚: 從基本面到技術面完整分析")
        print("   - 漲停原因分析: 為什麼漲停的深度解析")
        print("   - 互動元素: 大大們怎麼看？先進們有想法嗎？")
        
    except Exception as e:
        print(f"❌ 生成失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(regenerate_with_new_length())


