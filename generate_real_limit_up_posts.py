#!/usr/bin/env python3
"""
使用真實漲停股票數據生成貼文
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowType, WorkflowConfig

# 真實漲停股票數據
REAL_LIMIT_UP_STOCKS = [
    {"id": "2642", "name": "宅配通", "price": 29.15, "change": 2.65, "change_percent": 10.00},
    {"id": "5508", "name": "永信建", "price": 89.20, "change": 8.10, "change_percent": 9.99},
    {"id": "4989", "name": "榮科", "price": 31.50, "change": 2.85, "change_percent": 9.95},
    {"id": "2323", "name": "中環", "price": 9.41, "change": 0.85, "change_percent": 9.93},
    {"id": "6895", "name": "宏碩系統", "price": 332.50, "change": 30.00, "change_percent": 9.92},
    {"id": "5345", "name": "馥鴻", "price": 25.50, "change": 2.30, "change_percent": 9.91},
    {"id": "8034", "name": "榮群", "price": 24.40, "change": 2.20, "change_percent": 9.91},
    {"id": "2740", "name": "天蔥", "price": 27.25, "change": 2.45, "change_percent": 9.88},
    {"id": "3543", "name": "州巧", "price": 32.80, "change": 2.95, "change_percent": 9.88},
    {"id": "6510", "name": "精測", "price": 1390.00, "change": 125.00, "change_percent": 9.88},
    {"id": "3535", "name": "晶彩科", "price": 73.50, "change": 6.60, "change_percent": 9.87},
    {"id": "3059", "name": "華晶科", "price": 59.10, "change": 5.30, "change_percent": 9.85},
    {"id": "6781", "name": "AES-KY", "price": 1340.00, "change": 120.00, "change_percent": 9.84},
    {"id": "4166", "name": "友霖", "price": 25.70, "change": 2.30, "change_percent": 9.83},
    {"id": "6727", "name": "亞泰金屬", "price": 224.00, "change": 20.00, "change_percent": 9.80},
    {"id": "2408", "name": "南亞科", "price": 52.90, "change": 4.70, "change_percent": 9.75},
    {"id": "6223", "name": "旺矽", "price": 1520.00, "change": 135.00, "change_percent": 9.75},
    {"id": "6515", "name": "穎崴", "price": 1745.00, "change": 155.00, "change_percent": 9.75},
    {"id": "2509", "name": "全坤建", "price": 17.50, "change": 1.55, "change_percent": 9.72}
]

async def generate_real_limit_up_posts():
    """使用真實漲停股票數據生成貼文"""
    print("🚀 開始使用真實漲停股票數據生成貼文...")
    
    try:
        # 初始化工作流程引擎
        engine = MainWorkflowEngine()
        
        # 設定手動股票代號（前10檔）
        stock_ids = [stock["id"] for stock in REAL_LIMIT_UP_STOCKS[:10]]
        os.environ['MANUAL_STOCK_IDS'] = ','.join(stock_ids)
        
        print(f"📋 使用股票代號: {stock_ids}")
        
        # 創建工作流程配置
        config = WorkflowConfig(
            workflow_type=WorkflowType.INTRADAY_SURGE_STOCKS,
            max_posts_per_topic=10
        )
        
        # 執行工作流程
        result = await engine.execute_workflow(config)
        
        # 顯示結果
        print(f"\n🎉 貼文生成完成！")
        print(f"📊 總貼文數: {result.total_posts_generated}")
        print(f"✅ 發布數: {result.total_posts_published}")
        print(f"❌ 錯誤數: {len(result.errors)}")
        
        if result.generated_posts:
            print(f"\n📝 生成的貼文:")
            for i, post in enumerate(result.generated_posts, 1):
                print(f"{i}. {post['stock_id']} - {post['post_id']}")
                print(f"   KOL: {post['kol_id']}")
                print(f"   內容預覽: {post['content'][:100]}...")
                print()
        
        return result
        
    except Exception as e:
        print(f"❌ 生成貼文失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(generate_real_limit_up_posts())


