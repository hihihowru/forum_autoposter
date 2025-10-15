#!/usr/bin/env python3
"""
統一的觸發器管理器
支援多種觸發類型，提供可重用的流程介面
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# 導入自動標記服務
try:
    from src.services.auto_topic_tagging import AutoTopicTaggingService
    AUTO_TAGGING_AVAILABLE = True
except ImportError:
    logger.warning("自動標記服務不可用")
    AUTO_TAGGING_AVAILABLE = False

class TriggerType(Enum):
    """觸發器類型"""
    TRENDING_TOPIC = "trending_topic"           # 熱門話題
    LIMIT_UP_AFTER_HOURS = "limit_up_after_hours"  # 盤後漲停
    INTRADAY_LIMIT_UP = "intraday_limit_up"    # 盤中漲停
    CUSTOM_STOCKS = "custom_stocks"            # 自定義股票列表
    NEWS_EVENT = "news_event"                  # 新聞事件
    EARNINGS_REPORT = "earnings_report"        # 財報發布

@dataclass
class TriggerConfig:
    """觸發器配置"""
    trigger_type: TriggerType
    data_source: Union[str, List[str], Dict[str, Any]]  # 數據來源
    max_assignments: int = 3
    enable_content_generation: bool = True
    enable_sheets_recording: bool = True
    enable_publishing: bool = False
    custom_filters: Optional[Dict[str, Any]] = None

@dataclass
class TriggerResult:
    """觸發器執行結果"""
    success: bool
    trigger_type: TriggerType
    processed_items: int
    generated_content: int
    execution_time: float
    errors: List[str]
    details: Dict[str, Any]

class TriggerManager:
    """統一的觸發器管理器"""
    
    def __init__(self, flow_manager):
        self.flow_manager = flow_manager
        self.trigger_handlers = {
            TriggerType.TRENDING_TOPIC: self._handle_trending_topic,
            TriggerType.LIMIT_UP_AFTER_HOURS: self._handle_limit_up_after_hours,
            TriggerType.INTRADAY_LIMIT_UP: self._handle_intraday_limit_up,
            TriggerType.CUSTOM_STOCKS: self._handle_custom_stocks,
            TriggerType.NEWS_EVENT: self._handle_news_event,
            TriggerType.EARNINGS_REPORT: self._handle_earnings_report
        }
        
        # 初始化自動標記服務
        if AUTO_TAGGING_AVAILABLE:
            self.auto_tagging_service = AutoTopicTaggingService()
            logger.info("自動標記服務已啟用")
        else:
            self.auto_tagging_service = None
            logger.warning("自動標記服務未啟用")
    
    async def execute_trigger(self, config: TriggerConfig) -> TriggerResult:
        """執行觸發器"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"執行觸發器: {config.trigger_type.value}")
            
            # 獲取對應的處理器
            handler = self.trigger_handlers.get(config.trigger_type)
            if not handler:
                return TriggerResult(
                    success=False,
                    trigger_type=config.trigger_type,
                    processed_items=0,
                    generated_content=0,
                    execution_time=0,
                    errors=[f"不支援的觸發器類型: {config.trigger_type}"],
                    details={}
                )
            
            # 執行處理器
            result = await handler(config)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TriggerResult(
                success=result.get('success', False),
                trigger_type=config.trigger_type,
                processed_items=result.get('processed_items', 0),
                generated_content=result.get('generated_content', 0),
                execution_time=execution_time,
                errors=result.get('errors', []),
                details=result.get('details', {})
            )
            
        except Exception as e:
            logger.error(f"觸發器執行失敗: {e}")
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TriggerResult(
                success=False,
                trigger_type=config.trigger_type,
                processed_items=0,
                generated_content=0,
                execution_time=execution_time,
                errors=[str(e)],
                details={}
            )
    
    async def _handle_trending_topic(self, config: TriggerConfig) -> Dict[str, Any]:
        """處理熱門話題觸發器"""
        try:
            # 使用現有的熱門話題流程
            result = await self.flow_manager.execute_trending_topic_flow(config)
            
            # 自動生成熱門話題標籤
            auto_tags = []
            if self.auto_tagging_service and result.success:
                try:
                    # 從結果中提取話題和股票數據
                    topic_data = getattr(result, 'topic_data', {})
                    stock_selections = getattr(result, 'stock_selections', [])
                    
                    auto_tags = self.auto_tagging_service.generate_trending_topic_tags(
                        trigger_type="trending_topic",
                        topic_data=topic_data,
                        stock_selections=stock_selections
                    )
                    
                    logger.info(f"為熱門話題觸發器自動生成了 {len(auto_tags)} 個標籤")
                    
                except Exception as e:
                    logger.warning(f"自動標記失敗: {e}")
            
            return {
                'success': result.success,
                'processed_items': result.processed_topics,
                'generated_content': result.generated_posts,
                'errors': result.errors,
                'details': {
                    'flow_type': 'trending_topic',
                    'auto_tags': auto_tags,
                    'auto_tags_count': len(auto_tags)
                }
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    async def _handle_limit_up_after_hours(self, config: TriggerConfig) -> Dict[str, Any]:
        """處理盤後漲停觸發器"""
        try:
            # 使用現有的盤後漲停流程
            result = await self.flow_manager.execute_limit_up_stock_flow(config)
            return {
                'success': result.success,
                'processed_items': result.processed_topics,
                'generated_content': result.generated_posts,
                'errors': result.errors,
                'details': {'flow_type': 'limit_up_after_hours'}
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    async def _handle_intraday_limit_up(self, config: TriggerConfig) -> Dict[str, Any]:
        """處理盤中漲停觸發器"""
        try:
            # 解析股票代號
            stock_ids = self._parse_stock_ids(config.data_source)
            
            # 使用現有的盤中漲停流程
            result = await self.flow_manager.execute_intraday_limit_up_flow(stock_ids, config)
            return {
                'success': result.success,
                'processed_items': result.processed_topics,
                'generated_content': result.generated_posts,
                'errors': result.errors,
                'details': {'flow_type': 'intraday_limit_up', 'stock_ids': stock_ids}
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    async def _handle_custom_stocks(self, config: TriggerConfig) -> Dict[str, Any]:
        """處理自定義股票列表觸發器"""
        try:
            # 解析股票代號
            stock_ids = self._parse_stock_ids(config.data_source)
            
            # 使用盤中漲停流程（因為邏輯相似）
            result = await self.flow_manager.execute_intraday_limit_up_flow(stock_ids, config)
            return {
                'success': result.success,
                'processed_items': result.processed_topics,
                'generated_content': result.generated_posts,
                'errors': result.errors,
                'details': {'flow_type': 'custom_stocks', 'stock_ids': stock_ids}
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    async def _handle_news_event(self, config: TriggerConfig) -> Dict[str, Any]:
        """處理新聞事件觸發器"""
        try:
            # 解析新聞事件資料
            news_data = self._parse_news_event(config.data_source)
            
            # 轉換為話題格式
            topic_data = self._convert_news_to_topic(news_data)
            
            # 使用統一的流程
            result = await self.flow_manager._execute_unified_flow([topic_data], config)
            return {
                'success': result.get('success', False),
                'processed_items': 1,
                'generated_content': result.get('generated_count', 0),
                'errors': result.get('errors', []),
                'details': {'flow_type': 'news_event', 'news_data': news_data}
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    async def _handle_earnings_report(self, config: TriggerConfig) -> Dict[str, Any]:
        """處理財報發布觸發器"""
        try:
            # 解析財報資料
            earnings_data = self._parse_earnings_report(config.data_source)
            
            # 轉換為話題格式
            topic_data = self._convert_earnings_to_topic(earnings_data)
            
            # 使用統一的流程
            result = await self.flow_manager._execute_unified_flow([topic_data], config)
            return {
                'success': result.get('success', False),
                'processed_items': 1,
                'generated_content': result.get('generated_count', 0),
                'errors': result.get('errors', []),
                'details': {'flow_type': 'earnings_report', 'earnings_data': earnings_data}
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def _parse_stock_ids(self, data_source: Union[str, List[str], Dict[str, Any]]) -> List[str]:
        """解析股票代號"""
        if isinstance(data_source, str):
            # 如果是原始文本，使用解析器
            if hasattr(self.flow_manager, 'limit_up_parser'):
                stock_data_list = self.flow_manager.limit_up_parser.parse_limit_up_data(data_source)
                return [stock['stock_id'] for stock in stock_data_list]
            else:
                # 簡單的分割
                return [s.strip() for s in data_source.split(',') if s.strip()]
        elif isinstance(data_source, list):
            return data_source
        elif isinstance(data_source, dict):
            return data_source.get('stock_ids', [])
        else:
            return []
    
    def _parse_news_event(self, data_source: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """解析新聞事件資料"""
        if isinstance(data_source, str):
            return {
                'title': data_source,
                'content': data_source,
                'type': 'news_event'
            }
        else:
            return data_source
    
    def _parse_earnings_report(self, data_source: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """解析財報資料"""
        if isinstance(data_source, str):
            return {
                'title': data_source,
                'content': data_source,
                'type': 'earnings_report'
            }
        else:
            return data_source
    
    def _convert_news_to_topic(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """將新聞轉換為話題格式"""
        return {
            'id': f"news_{hash(news_data.get('title', ''))}",
            'title': news_data.get('title', ''),
            'description': news_data.get('content', ''),
            'persona_tags': ['市場消息'],
            'industry_tags': [],
            'event_tags': ['新聞事件']
        }
    
    def _convert_earnings_to_topic(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """將財報轉換為話題格式"""
        return {
            'id': f"earnings_{hash(earnings_data.get('title', ''))}",
            'title': earnings_data.get('title', ''),
            'description': earnings_data.get('content', ''),
            'persona_tags': ['基本面分析'],
            'industry_tags': [],
            'event_tags': ['財報發布']
        }

def create_trigger_manager(flow_manager) -> TriggerManager:
    """創建觸發器管理器"""
    return TriggerManager(flow_manager)


