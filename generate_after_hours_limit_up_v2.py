#!/usr/bin/env python3
"""
盤後漲停觸發器 - 使用主流程引擎
重新生成貼文並更新到 Google Sheets
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

async def run_after_hours_limit_up_generation():
    """執行盤後漲停貼文生成"""
    try:
        print("🚀 開始執行盤後漲停貼文生成...")
        
        # 初始化主流程引擎
        engine = MainWorkflowEngine()
        
        # 配置工作流程
        config = WorkflowConfig(
            workflow_type=WorkflowType.AFTER_HOURS_LIMIT_UP,
            max_posts=13,
            enable_publishing=False,
            enable_learning=False
        )
        
        # 執行工作流程
        result = await engine.execute_workflow(config)
        
        print(f"✅ 貼文生成完成！")
        print(f"📊 生成貼文數: {result.generated_posts}")
        print(f"📤 發布貼文數: {result.published_posts}")
        print(f"⏱️ 執行時間: {result.execution_time:.2f} 秒")
        
        return result
        
    except Exception as e:
        print(f"❌ 貼文生成失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_after_hours_limit_up_generation())
