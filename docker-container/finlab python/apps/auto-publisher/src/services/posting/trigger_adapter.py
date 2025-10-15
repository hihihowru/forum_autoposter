#!/usr/bin/env python3
"""
觸發器適配器
將現有觸發器轉換為發文生成系統格式
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.services.flow.trigger_manager import TriggerManager, TriggerType, TriggerConfig
from src.services.flow.unified_flow_manager import UnifiedFlowManager
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.posting.kol_integration_service import KOLIntegrationService, KOLProfile

logger = logging.getLogger(__name__)

class PostingSystemTriggerType(Enum):
    """發文生成系統觸發器類型"""
    AFTER_HOURS_LIMIT_UP = "after_hours_limit_up"
    INTRADAY_LIMIT_UP = "intraday_limit_up"
    TRENDING_TOPIC = "trending_topic"
    CUSTOM_STOCKS = "custom_stocks"
    STOCK_CODE_LIST = "stock_code_list"

@dataclass
class PostingSystemConfig:
    """發文生成系統配置"""
    trigger_type: PostingSystemTriggerType
    stock_codes: Optional[List[str]] = None
    max_posts: int = 10
    enable_publishing: bool = False
    enable_learning: bool = True
    data_sources: Dict[str, bool] = None
    kol_assignment_mode: str = "dynamic"  # "fixed" | "dynamic"
    content_mode: str = "one_to_one"  # "one_to_one" | "one_to_many"
    
    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = {
                "stock_price_api": True,
                "monthly_revenue_api": True,
                "financial_report_api": True,
                "news_sources": True
            }

class TriggerAdapter:
    """觸發器適配器"""
    
    def __init__(self, sheets_client: GoogleSheetsClient):
        self.sheets_client = sheets_client
        self.trigger_manager = TriggerManager(None)  # 將被 UnifiedFlowManager 替換
        self.unified_flow_manager = UnifiedFlowManager(sheets_client)
        self.kol_service = KOLIntegrationService()
        self.logger = logging.getLogger(__name__)
    
    async def execute_posting_system_trigger(self, config: PostingSystemConfig) -> Dict[str, Any]:
        """執行發文生成系統觸發器"""
        try:
            self.logger.info(f"執行發文生成系統觸發器: {config.trigger_type.value}")
            
            # 根據觸發器類型選擇處理方式
            if config.trigger_type == PostingSystemTriggerType.AFTER_HOURS_LIMIT_UP:
                return await self._handle_after_hours_limit_up(config)
            elif config.trigger_type == PostingSystemTriggerType.INTRADAY_LIMIT_UP:
                return await self._handle_intraday_limit_up(config)
            elif config.trigger_type == PostingSystemTriggerType.TRENDING_TOPIC:
                return await self._handle_trending_topic(config)
            elif config.trigger_type == PostingSystemTriggerType.CUSTOM_STOCKS:
                return await self._handle_custom_stocks(config)
            elif config.trigger_type == PostingSystemTriggerType.STOCK_CODE_LIST:
                return await self._handle_stock_code_list(config)
            else:
                raise ValueError(f"不支援的觸發器類型: {config.trigger_type}")
                
        except Exception as e:
            self.logger.error(f"執行發文生成系統觸發器失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_posts": 0,
                "execution_time": 0
            }
    
    async def _handle_after_hours_limit_up(self, config: PostingSystemConfig) -> Dict[str, Any]:
        """處理盤後漲停觸發器"""
        try:
            self.logger.info("開始處理盤後漲停觸發器")
            
            # 1. 轉換為現有觸發器配置
            trigger_config = TriggerConfig(
                trigger_type=TriggerType.LIMIT_UP_AFTER_HOURS,
                max_posts=config.max_posts,
                enable_publishing=config.enable_publishing,
                enable_learning=config.enable_learning
            )
            
            # 2. 執行現有流程
            result = await self.unified_flow_manager.execute_limit_up_stock_flow(
                trigger_config
            )
            
            # 3. 轉換為發文生成系統格式
            return {
                "success": result.success,
                "trigger_type": "after_hours_limit_up",
                "generated_posts": result.generated_posts,
                "processed_items": result.processed_topics,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "details": {
                    "flow_type": "limit_up_stock",
                    "data_sources_used": config.data_sources,
                    "kol_assignment_mode": config.kol_assignment_mode,
                    "content_mode": config.content_mode
                }
            }
            
        except Exception as e:
            self.logger.error(f"處理盤後漲停觸發器失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_posts": 0,
                "execution_time": 0
            }
    
    async def _handle_intraday_limit_up(self, config: PostingSystemConfig) -> Dict[str, Any]:
        """處理盤中漲停觸發器"""
        try:
            self.logger.info("開始處理盤中漲停觸發器")
            
            if not config.stock_codes:
                raise ValueError("盤中漲停觸發器需要提供股票代號列表")
            
            # 1. 轉換為現有觸發器配置
            trigger_config = TriggerConfig(
                trigger_type=TriggerType.INTRADAY_LIMIT_UP,
                max_posts=config.max_posts,
                enable_publishing=config.enable_publishing,
                enable_learning=config.enable_learning
            )
            
            # 2. 執行現有流程
            result = await self.unified_flow_manager.execute_intraday_limit_up_flow(
                config.stock_codes, trigger_config
            )
            
            # 3. 轉換為發文生成系統格式
            return {
                "success": result.success,
                "trigger_type": "intraday_limit_up",
                "generated_posts": result.generated_posts,
                "processed_items": result.processed_topics,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "details": {
                    "flow_type": "intraday_limit_up",
                    "stock_codes": config.stock_codes,
                    "data_sources_used": config.data_sources,
                    "kol_assignment_mode": config.kol_assignment_mode,
                    "content_mode": config.content_mode
                }
            }
            
        except Exception as e:
            self.logger.error(f"處理盤中漲停觸發器失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_posts": 0,
                "execution_time": 0
            }
    
    async def _handle_trending_topic(self, config: PostingSystemConfig) -> Dict[str, Any]:
        """處理熱門話題觸發器"""
        try:
            self.logger.info("開始處理熱門話題觸發器")
            
            # 1. 轉換為現有觸發器配置
            trigger_config = TriggerConfig(
                trigger_type=TriggerType.TRENDING_TOPIC,
                max_posts=config.max_posts,
                enable_publishing=config.enable_publishing,
                enable_learning=config.enable_learning
            )
            
            # 2. 執行現有流程
            result = await self.unified_flow_manager.execute_trending_topic_flow(
                trigger_config
            )
            
            # 3. 轉換為發文生成系統格式
            return {
                "success": result.success,
                "trigger_type": "trending_topic",
                "generated_posts": result.generated_posts,
                "processed_items": result.processed_topics,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "details": {
                    "flow_type": "trending_topic",
                    "data_sources_used": config.data_sources,
                    "kol_assignment_mode": config.kol_assignment_mode,
                    "content_mode": config.content_mode
                }
            }
            
        except Exception as e:
            self.logger.error(f"處理熱門話題觸發器失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_posts": 0,
                "execution_time": 0
            }
    
    async def _handle_custom_stocks(self, config: PostingSystemConfig) -> Dict[str, Any]:
        """處理自定義股票觸發器"""
        try:
            self.logger.info("開始處理自定義股票觸發器")
            
            if not config.stock_codes:
                raise ValueError("自定義股票觸發器需要提供股票代號列表")
            
            # 1. 轉換為現有觸發器配置
            trigger_config = TriggerConfig(
                trigger_type=TriggerType.CUSTOM_STOCKS,
                max_posts=config.max_posts,
                enable_publishing=config.enable_publishing,
                enable_learning=config.enable_learning
            )
            
            # 2. 執行現有流程（使用盤中漲停流程處理自定義股票）
            result = await self.unified_flow_manager.execute_intraday_limit_up_flow(
                config.stock_codes, trigger_config
            )
            
            # 3. 轉換為發文生成系統格式
            return {
                "success": result.success,
                "trigger_type": "custom_stocks",
                "generated_posts": result.generated_posts,
                "processed_items": result.processed_topics,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "details": {
                    "flow_type": "custom_stocks",
                    "stock_codes": config.stock_codes,
                    "data_sources_used": config.data_sources,
                    "kol_assignment_mode": config.kol_assignment_mode,
                    "content_mode": config.content_mode
                }
            }
            
        except Exception as e:
            self.logger.error(f"處理自定義股票觸發器失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_posts": 0,
                "execution_time": 0
            }
    
    async def _handle_stock_code_list(self, config: PostingSystemConfig) -> Dict[str, Any]:
        """處理股票代號列表觸發器"""
        try:
            self.logger.info("開始處理股票代號列表觸發器")
            
            if not config.stock_codes:
                raise ValueError("股票代號列表觸發器需要提供股票代號列表")
            
            # 1. 轉換為現有觸發器配置
            trigger_config = TriggerConfig(
                trigger_type=TriggerType.CUSTOM_STOCKS,  # 使用自定義股票類型
                max_posts=config.max_posts,
                enable_publishing=config.enable_publishing,
                enable_learning=config.enable_learning
            )
            
            # 2. 執行現有流程
            result = await self.unified_flow_manager.execute_intraday_limit_up_flow(
                config.stock_codes, trigger_config
            )
            
            # 3. 轉換為發文生成系統格式
            return {
                "success": result.success,
                "trigger_type": "stock_code_list",
                "generated_posts": result.generated_posts,
                "processed_items": result.processed_topics,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "details": {
                    "flow_type": "stock_code_list",
                    "stock_codes": config.stock_codes,
                    "data_sources_used": config.data_sources,
                    "kol_assignment_mode": config.kol_assignment_mode,
                    "content_mode": config.content_mode
                }
            }
            
        except Exception as e:
            self.logger.error(f"處理股票代號列表觸發器失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_posts": 0,
                "execution_time": 0
            }

# 工廠函數
def create_trigger_adapter(sheets_client: GoogleSheetsClient) -> TriggerAdapter:
    """創建觸發器適配器實例"""
    return TriggerAdapter(sheets_client)

# 使用範例
async def example_usage():
    """使用範例"""
    from src.clients.google.sheets_client import GoogleSheetsClient
    
    # 初始化
    sheets_client = GoogleSheetsClient()
    adapter = create_trigger_adapter(sheets_client)
    
    # 配置盤後漲停觸發器
    config = PostingSystemConfig(
        trigger_type=PostingSystemTriggerType.AFTER_HOURS_LIMIT_UP,
        max_posts=10,
        enable_publishing=False,
        enable_learning=True,
        data_sources={
            "stock_price_api": True,
            "monthly_revenue_api": True,
            "financial_report_api": True,
            "news_sources": True
        },
        kol_assignment_mode="dynamic",
        content_mode="one_to_one"
    )
    
    # 執行觸發器
    result = await adapter.execute_posting_system_trigger(config)
    
    print(f"執行結果: {result}")

if __name__ == "__main__":
    asyncio.run(example_usage())
