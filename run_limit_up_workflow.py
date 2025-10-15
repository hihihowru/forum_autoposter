#!/usr/bin/env python3
"""
使用主流程引擎的漲停股貼文生成器
整合到統一的主流程中
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowType, WorkflowConfig
from src.utils.config_manager import ConfigManager

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """使用主流程引擎執行漲停股貼文生成"""
    try:
        logger.info("🚀 啟動第四隻觸發器 - 盤後漲停股回顧")
        
        # 初始化主流程引擎
        workflow_engine = MainWorkflowEngine()
        
        # 配置工作流程
        config = WorkflowConfig(
            workflow_type=WorkflowType.AFTER_HOURS_LIMIT_UP,
            max_posts_per_topic=15,  # 15篇漲停股分析
            enable_content_generation=True,
            enable_publishing=False,  # 先不發布，只生成內容
            enable_learning=True,
            enable_quality_check=True,
            enable_sheets_recording=True,
            retry_on_failure=True,
            max_retries=3
        )
        
        # 執行工作流程
        logger.info("📈 開始執行盤後漲停股工作流程...")
        result = await workflow_engine.execute_workflow(config)
        
        # 顯示結果
        if result.success:
            logger.info("✅ 盤後漲停股工作流程執行成功！")
            logger.info(f"📊 總共生成 {result.total_posts_generated} 篇貼文")
            logger.info(f"📊 總共發布 {result.total_posts_published} 篇貼文")
            logger.info(f"⏱️ 執行時間: {result.execution_time:.2f} 秒")
            
            if result.warnings:
                logger.warning("⚠️ 警告訊息:")
                for warning in result.warnings:
                    logger.warning(f"  - {warning}")
        else:
            logger.error("❌ 盤後漲停股工作流程執行失敗！")
            logger.error("錯誤訊息:")
            for error in result.errors:
                logger.error(f"  - {error}")
        
    except Exception as e:
        logger.error(f"主程序執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
