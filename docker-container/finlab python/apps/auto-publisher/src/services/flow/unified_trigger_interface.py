#!/usr/bin/env python3
"""
統一觸發器接口
整合智能調配系統、KOL分配策略和內容生成
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.services.flow.kol_allocation_strategy import (
    KOLAllocationStrategy, TriggerConfig, AllocationStrategy, 
    DEFAULT_TRIGGER_CONFIGS, create_allocation_strategy
)
from src.services.flow.unified_flow_manager import UnifiedFlowManager, FlowConfig
from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.clients.google.sheets_client import GoogleSheetsClient
from src.clients.cmoney.cmoney_client import CMoneyClient
from smart_api_allocator import SmartAPIAllocator, StockAnalysis

logger = logging.getLogger(__name__)

@dataclass
class UnifiedTriggerResult:
    """統一觸發器執行結果"""
    success: bool
    trigger_type: str
    allocation_strategy: str
    total_topics: int
    total_assignments: int
    generated_posts: int
    execution_time: float
    errors: List[str]
    details: Dict[str, Any]

class UnifiedTriggerInterface:
    """統一觸發器接口"""
    
    def __init__(self):
        """初始化統一觸發器接口"""
        # 初始化核心組件
        self.sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        self.cmoney_client = CMoneyClient()
        self.content_generator = ContentGenerator()
        self.flow_manager = UnifiedFlowManager()
        
        # 初始化分配策略和智能調配
        self.kol_allocation = create_allocation_strategy(self.sheets_client)
        self.smart_allocator = SmartAPIAllocator()
        
        logger.info("統一觸發器接口初始化完成")
    
    async def execute_trigger(self, trigger_type: str, custom_config: Optional[TriggerConfig] = None) -> UnifiedTriggerResult:
        """
        執行統一觸發器流程
        
        Args:
            trigger_type: 觸發器類型
            custom_config: 自定義配置
            
        Returns:
            執行結果
        """
        start_time = datetime.now()
        logger.info(f"開始執行觸發器: {trigger_type}")
        
        try:
            # 1. 獲取觸發器配置
            config = custom_config or DEFAULT_TRIGGER_CONFIGS.get(trigger_type)
            if not config:
                raise ValueError(f"不支援的觸發器類型: {trigger_type}")
            
            logger.info(f"觸發器配置: {config.allocation_strategy.value}")
            
            # 2. 獲取原始數據
            raw_data = await self._fetch_trigger_data(trigger_type)
            logger.info(f"獲取到 {len(raw_data)} 個原始數據")
            
            # 3. 智能調配API資源
            allocated_data = self._allocate_api_resources(trigger_type, raw_data)
            logger.info(f"API資源調配完成")
            
            # 4. 轉換為TopicData格式
            topics = self._convert_to_topics(allocated_data, trigger_type)
            logger.info(f"轉換為 {len(topics)} 個話題")
            
            # 5. KOL分配
            assignments = self.kol_allocation.allocate_kols(config, topics)
            logger.info(f"KOL分配完成，共 {len(assignments)} 個任務")
            
            # 6. 內容生成
            generated_posts = []
            if config.enable_content_generation:
                generated_posts = await self._generate_content(assignments)
                logger.info(f"內容生成完成，共 {len(generated_posts)} 篇貼文")
            
            # 7. 記錄到Google Sheets
            if generated_posts:
                await self._record_to_sheets(generated_posts, trigger_type)
                logger.info("已記錄到Google Sheets")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return UnifiedTriggerResult(
                success=True,
                trigger_type=trigger_type,
                allocation_strategy=config.allocation_strategy.value,
                total_topics=len(topics),
                total_assignments=len(assignments),
                generated_posts=len(generated_posts),
                execution_time=execution_time,
                errors=[],
                details={
                    "api_allocation": self._get_api_allocation_summary(),
                    "kol_allocation": self.kol_allocation.get_allocation_summary(),
                    "generated_posts": generated_posts
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"觸發器執行失敗: {e}")
            
            return UnifiedTriggerResult(
                success=False,
                trigger_type=trigger_type,
                allocation_strategy="unknown",
                total_topics=0,
                total_assignments=0,
                generated_posts=0,
                execution_time=execution_time,
                errors=[str(e)],
                details={}
            )
    
    async def _fetch_trigger_data(self, trigger_type: str) -> List[Dict[str, Any]]:
        """獲取觸發器原始數據"""
        if trigger_type == "after_hours_limit_up":
            return await self._fetch_after_hours_data()
        elif trigger_type == "intraday_surge":
            return await self._fetch_intraday_surge_data()
        elif trigger_type == "trending_topics":
            return await self._fetch_trending_topics_data()
        else:
            logger.warning(f"觸發器 {trigger_type} 的數據獲取方法未實現")
            return []
    
    async def _fetch_after_hours_data(self) -> List[Dict[str, Any]]:
        """獲取盤後漲停股數據"""
        try:
            # 這裡應該調用實際的Finlab API或CMoney API
            # 暫時返回模擬數據
            sample_stocks = [
                {"stock_id": "3665", "stock_name": "股票3665", "change_percent": 9.62, "volume_amount": 86.34, "is_high_volume": True},
                {"stock_id": "3653", "stock_name": "股票3653", "change_percent": 9.93, "volume_amount": 59.44, "is_high_volume": True},
                {"stock_id": "5314", "stock_name": "股票5314", "change_percent": 9.91, "volume_amount": 31.89, "is_high_volume": True},
                {"stock_id": "5345", "stock_name": "股票5345", "change_percent": 9.95, "volume_amount": 0.016, "is_high_volume": False},
                {"stock_id": "2724", "stock_name": "股票2724", "change_percent": 9.95, "volume_amount": 0.031, "is_high_volume": False}
            ]
            
            logger.info(f"獲取到 {len(sample_stocks)} 檔盤後漲停股")
            return sample_stocks
            
        except Exception as e:
            logger.error(f"獲取盤後數據失敗: {e}")
            return []
    
    async def _fetch_intraday_surge_data(self) -> List[Dict[str, Any]]:
        """獲取盤中急漲股數據"""
        # 實現盤中急漲股數據獲取
        return []
    
    async def _fetch_trending_topics_data(self) -> List[Dict[str, Any]]:
        """獲取熱門話題數據"""
        # 實現熱門話題數據獲取
        return []
    
    def _allocate_api_resources(self, trigger_type: str, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """智能調配API資源"""
        logger.info(f"開始API資源調配，觸發器: {trigger_type}")
        
        # 根據觸發器類型選擇調配策略
        if trigger_type == "after_hours_limit_up":
            return self._allocate_for_after_hours(raw_data)
        elif trigger_type == "trending_topics":
            return self._allocate_for_trending(raw_data)
        else:
            return raw_data  # 預設不進行特殊調配
    
    def _allocate_for_after_hours(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """為盤後機器人調配API資源"""
        # 轉換為StockAnalysis格式
        stock_analyses = []
        for i, stock in enumerate(stocks):
            analysis = StockAnalysis(
                stock_id=stock["stock_id"],
                stock_name=stock["stock_name"],
                volume_rank=i + 1,
                change_percent=stock["change_percent"],
                volume_amount=stock["volume_amount"],
                rank_type="有量" if stock["is_high_volume"] else "無量"
            )
            stock_analyses.append(analysis)
        
        # 使用智能調配器分配API
        allocated_stocks = self.smart_allocator.allocate_apis_for_stocks(stock_analyses)
        
        # 轉換回原始格式並添加API分配資訊
        result = []
        for stock, analysis in zip(stocks, allocated_stocks):
            stock["assigned_apis"] = analysis.assigned_apis
            result.append(stock)
        
        return result
    
    def _allocate_for_trending(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """為熱門話題調配API資源"""
        # 熱門話題的API調配邏輯
        for topic in topics:
            topic["assigned_apis"] = ["serper", "cmoney_news"]  # 預設API
        return topics
    
    def _convert_to_topics(self, data: List[Dict[str, Any]], trigger_type: str) -> List[Any]:
        """轉換數據為TopicData格式"""
        from src.services.assign.assignment_service import TopicData
        
        topics = []
        for item in data:
            if trigger_type == "after_hours_limit_up":
                topic = TopicData(
                    topic_id=f"after_hours_{item['stock_id']}_{datetime.now().strftime('%Y%m%d')}",
                    title=f"{item['stock_name']}({item['stock_id']}) 漲停分析",
                    input_index=0,
                    persona_tags=["技術派", "籌碼派"],
                    industry_tags=["漲停股"],
                    event_tags=["盤後分析"],
                    stock_tags=[item['stock_id']]
                )
                topics.append(topic)
            # 其他觸發器類型的轉換邏輯...
        
        return topics
    
    async def _generate_content(self, assignments: List[Any]) -> List[Dict[str, Any]]:
        """生成內容"""
        generated_posts = []
        
        for assignment in assignments:
            try:
                # 獲取KOL配置
                kol_info = self.kol_allocation._get_kol_info(assignment.kol_serial)
                if not kol_info:
                    logger.warning(f"找不到KOL {assignment.kol_serial} 的配置")
                    continue
                
                # 創建內容生成請求
                content_request = ContentRequest(
                    topic_title=assignment.topic_title,
                    topic_keywords=",".join(assignment.topic_keywords),
                    kol_persona=kol_info.get('人設', '技術派'),
                    kol_nickname=kol_info.get('暱稱', 'Unknown'),
                    content_type="stock_analysis",
                    target_audience="active_traders"
                )
                
                # 生成內容
                generated = self.content_generator.generate_complete_content(content_request)
                
                if generated.success:
                    post = {
                        "kol_serial": assignment.kol_serial,
                        "kol_nickname": kol_info.get('暱稱', 'Unknown'),
                        "topic_id": assignment.topic_id,
                        "title": generated.title,
                        "content": generated.content,
                        "status": "generated",
                        "created_at": datetime.now().isoformat()
                    }
                    generated_posts.append(post)
                    logger.info(f"成功生成內容: {assignment.topic_title} -> {kol_info.get('暱稱', 'Unknown')}")
                else:
                    logger.error(f"內容生成失敗: {assignment.topic_title}")
                    
            except Exception as e:
                logger.error(f"生成內容時發生錯誤: {e}")
        
        return generated_posts
    
    async def _record_to_sheets(self, posts: List[Dict[str, Any]], trigger_type: str):
        """記錄到Google Sheets"""
        try:
            # 這裡應該實現具體的Google Sheets記錄邏輯
            logger.info(f"記錄 {len(posts)} 篇貼文到Google Sheets")
            # 實際實現會調用sheets_client的相關方法
        except Exception as e:
            logger.error(f"記錄到Google Sheets失敗: {e}")
    
    def _get_api_allocation_summary(self) -> Dict[str, Any]:
        """獲取API分配摘要"""
        return {
            "total_apis": len(self.smart_allocator.api_resources),
            "api_usage": {name: api.current_usage for name, api in self.smart_allocator.api_resources.items()}
        }
    
    def update_trigger_config(self, trigger_type: str, config: TriggerConfig):
        """更新觸發器配置"""
        DEFAULT_TRIGGER_CONFIGS[trigger_type] = config
        logger.info(f"更新觸發器配置: {trigger_type}")
    
    def get_trigger_summary(self) -> Dict[str, Any]:
        """獲取觸發器摘要"""
        return {
            "available_triggers": list(DEFAULT_TRIGGER_CONFIGS.keys()),
            "allocation_strategies": [strategy.value for strategy in AllocationStrategy],
            "kol_allocation_summary": self.kol_allocation.get_allocation_summary()
        }

# 便捷函數
async def execute_after_hours_limit_up() -> UnifiedTriggerResult:
    """執行盤後漲停股觸發器"""
    interface = UnifiedTriggerInterface()
    return await interface.execute_trigger("after_hours_limit_up")

async def execute_trending_topics() -> UnifiedTriggerResult:
    """執行熱門話題觸發器"""
    interface = UnifiedTriggerInterface()
    return await interface.execute_trigger("trending_topics")

async def execute_intraday_surge() -> UnifiedTriggerResult:
    """執行盤中急漲股觸發器"""
    interface = UnifiedTriggerInterface()
    return await interface.execute_trigger("intraday_surge")

if __name__ == "__main__":
    # 測試統一觸發器接口
    async def test_trigger():
        interface = UnifiedTriggerInterface()
        result = await interface.execute_trigger("after_hours_limit_up")
        print(f"執行結果: {result}")
    
    asyncio.run(test_trigger())








