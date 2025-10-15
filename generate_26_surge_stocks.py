#!/usr/bin/env python3
"""
生成26檔盤中急漲股貼文
"""

import os
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 26檔盤中急漲股票數據
SURGE_STOCKS = [
    {"id": "2344", "name": "華邦電", "change_percent": 10.00},
    {"id": "2642", "name": "宅配通", "change_percent": 10.00},
    {"id": "5508", "name": "永信建", "change_percent": 9.99},
    {"id": "2408", "name": "南亞科", "change_percent": 9.96},
    {"id": "6789", "name": "采鈺", "change_percent": 9.96},
    {"id": "4989", "name": "榮科", "change_percent": 9.95},
    {"id": "2323", "name": "中環", "change_percent": 9.93},
    {"id": "3323", "name": "加百裕", "change_percent": 9.92},
    {"id": "5234", "name": "達興材料", "change_percent": 9.92},
    {"id": "5345", "name": "馥鴻", "change_percent": 9.91},
    {"id": "8034", "name": "榮群", "change_percent": 9.91},
    {"id": "8358", "name": "金居", "change_percent": 9.90},
    {"id": "5309", "name": "系統電", "change_percent": 9.89},
    {"id": "2740", "name": "天蔥", "change_percent": 9.88},
    {"id": "3543", "name": "州巧", "change_percent": 9.88},
    {"id": "6510", "name": "精測", "change_percent": 9.88},
    {"id": "3535", "name": "晶彩科", "change_percent": 9.87},
    {"id": "3059", "name": "華晶科", "change_percent": 9.85},
    {"id": "4577", "name": "達航科技", "change_percent": 9.85},
    {"id": "6781", "name": "AES-KY", "change_percent": 9.84},
    {"id": "4166", "name": "友霖", "change_percent": 9.83},
    {"id": "6727", "name": "亞泰金屬", "change_percent": 9.80},
    {"id": "6223", "name": "旺矽", "change_percent": 9.75},
    {"id": "6515", "name": "穎崴", "change_percent": 9.75},
    {"id": "2509", "name": "全坤建", "change_percent": 9.72},
    {"id": "5314", "name": "世紀", "change_percent": 9.63}
]

async def generate_26_surge_stocks():
    """生成26檔盤中急漲股貼文"""
    print("🚀 開始生成26檔盤中急漲股貼文...")
    
    try:
        from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
        
        # 初始化工作流程引擎
        engine = MainWorkflowEngine()
        
        # 設定手動股票代號（26檔）
        stock_ids = [stock["id"] for stock in SURGE_STOCKS]
        os.environ['MANUAL_STOCK_IDS'] = ','.join(stock_ids)
        
        print(f"📋 使用股票代號: {len(stock_ids)}檔")
        stock_list = [f"{s['name']}({s['id']})" for s in SURGE_STOCKS[:5]]
        print(f"📊 股票列表: {stock_list}...")
        
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
                print(f"      內容預覽: {post['content'][:80]}...")
                print()
        
        print("🎉 26檔盤中急漲股貼文生成完成！")
        
    except Exception as e:
        print(f"❌ 生成失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_26_surge_stocks())
