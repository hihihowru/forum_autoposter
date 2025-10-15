"""
自動熱門話題標籤服務
根據觸發器類型自動標記對應的熱門話題標籤
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TrendingTopicTag:
    """熱門話題標籤"""
    topic_id: str
    topic_title: str
    topic_category: str
    engagement_score: float
    related_stocks: List[str]
    auto_generated: bool = True
    source: str = "trigger"  # trigger, manual

class AutoTopicTaggingService:
    """自動熱門話題標籤服務"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("自動熱門話題標籤服務初始化完成")
    
    def generate_trending_topic_tags(self, 
                                   trigger_type: str,
                                   topic_data: Dict[str, Any],
                                   stock_selections: List[Dict[str, Any]]) -> List[TrendingTopicTag]:
        """根據觸發器類型和選擇的股票自動生成熱門話題標籤"""
        
        self.logger.info(f"開始為觸發器 {trigger_type} 生成自動熱門話題標籤")
        
        generated_tags = []
        
        if trigger_type == "trending_topic":
            # 熱門話題觸發器 - 自動標記所有相關話題
            generated_tags = self._generate_trending_topic_tags(topic_data, stock_selections)
            
        elif trigger_type == "limit_up_after_hours":
            # 盤後漲停觸發器 - 根據股票查找相關熱門話題
            generated_tags = self._generate_limit_up_topic_tags(topic_data, stock_selections)
            
        elif trigger_type == "intraday_limit_up":
            # 盤中漲停觸發器 - 根據股票查找相關熱門話題
            generated_tags = self._generate_intraday_topic_tags(topic_data, stock_selections)
            
        elif trigger_type == "custom_stocks":
            # 自定義股票觸發器 - 根據股票查找相關熱門話題
            generated_tags = self._generate_custom_stock_topic_tags(topic_data, stock_selections)
            
        else:
            self.logger.warning(f"未知的觸發器類型: {trigger_type}")
        
        self.logger.info(f"為觸發器 {trigger_type} 生成了 {len(generated_tags)} 個自動熱門話題標籤")
        return generated_tags
    
    def _generate_trending_topic_tags(self, 
                                    topic_data: Dict[str, Any],
                                    stock_selections: List[Dict[str, Any]]) -> List[TrendingTopicTag]:
        """為熱門話題觸發器生成標籤"""
        tags = []
        
        # 從話題數據中提取熱門話題
        if 'trending_topics' in topic_data:
            for topic in topic_data['trending_topics']:
                # 檢查是否有選中的股票與此話題相關
                related_stocks = []
                for stock_selection in stock_selections:
                    if stock_selection.get('code') in topic.get('stock_ids', []):
                        related_stocks.append(stock_selection.get('code'))
                
                # 只為有相關股票選擇的話題生成標籤
                if related_stocks:
                    tag = TrendingTopicTag(
                        topic_id=topic.get('id', ''),
                        topic_title=topic.get('title', ''),
                        topic_category=topic.get('category', ''),
                        engagement_score=topic.get('engagement_score', 0.0),
                        related_stocks=related_stocks,
                        auto_generated=True,
                        source="trending_topic_trigger"
                    )
                    tags.append(tag)
                    self.logger.info(f"自動生成熱門話題標籤: {tag.topic_title}")
        
        return tags
    
    def _generate_limit_up_topic_tags(self, 
                                    topic_data: Dict[str, Any],
                                    stock_selections: List[Dict[str, Any]]) -> List[TrendingTopicTag]:
        """為盤後漲停觸發器生成標籤"""
        tags = []
        
        # 為每個選中的股票查找相關熱門話題
        for stock_selection in stock_selections:
            stock_code = stock_selection.get('code')
            stock_name = stock_selection.get('name')
            
            # 模擬查找相關熱門話題（實際應該從 trending-api 獲取）
            related_topic = self._find_related_trending_topic(stock_code, topic_data)
            
            if related_topic:
                tag = TrendingTopicTag(
                    topic_id=related_topic.get('id', f'limit_up_{stock_code}'),
                    topic_title=f"盤後漲停 - {stock_name}",
                    topic_category="limit_up",
                    engagement_score=0.8,  # 漲停股票熱度較高
                    related_stocks=[stock_code],
                    auto_generated=True,
                    source="limit_up_trigger"
                )
                tags.append(tag)
                self.logger.info(f"為盤後漲停股票 {stock_name} 自動生成話題標籤")
        
        return tags
    
    def _generate_intraday_topic_tags(self, 
                                    topic_data: Dict[str, Any],
                                    stock_selections: List[Dict[str, Any]]) -> List[TrendingTopicTag]:
        """為盤中漲停觸發器生成標籤"""
        tags = []
        
        # 為每個選中的股票查找相關熱門話題
        for stock_selection in stock_selections:
            stock_code = stock_selection.get('code')
            stock_name = stock_selection.get('name')
            
            # 模擬查找相關熱門話題
            related_topic = self._find_related_trending_topic(stock_code, topic_data)
            
            if related_topic:
                tag = TrendingTopicTag(
                    topic_id=related_topic.get('id', f'intraday_limit_up_{stock_code}'),
                    topic_title=f"盤中漲停 - {stock_name}",
                    topic_category="intraday_limit_up",
                    engagement_score=0.9,  # 盤中漲停熱度更高
                    related_stocks=[stock_code],
                    auto_generated=True,
                    source="intraday_limit_up_trigger"
                )
                tags.append(tag)
                self.logger.info(f"為盤中漲停股票 {stock_name} 自動生成話題標籤")
        
        return tags
    
    def _generate_custom_stock_topic_tags(self, 
                                        topic_data: Dict[str, Any],
                                        stock_selections: List[Dict[str, Any]]) -> List[TrendingTopicTag]:
        """為自定義股票觸發器生成標籤"""
        tags = []
        
        # 為每個選中的股票查找相關熱門話題
        for stock_selection in stock_selections:
            stock_code = stock_selection.get('code')
            stock_name = stock_selection.get('name')
            
            # 模擬查找相關熱門話題
            related_topic = self._find_related_trending_topic(stock_code, topic_data)
            
            if related_topic:
                tag = TrendingTopicTag(
                    topic_id=related_topic.get('id', f'custom_{stock_code}'),
                    topic_title=f"自定義關注 - {stock_name}",
                    topic_category="custom_stock",
                    engagement_score=0.7,
                    related_stocks=[stock_code],
                    auto_generated=True,
                    source="custom_stock_trigger"
                )
                tags.append(tag)
                self.logger.info(f"為自定義股票 {stock_name} 自動生成話題標籤")
        
        return tags
    
    def _find_related_trending_topic(self, stock_code: str, topic_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """查找與股票相關的熱門話題"""
        # 這裡應該實際調用 trending-api 查找相關話題
        # 目前返回模擬數據
        
        # 模擬相關話題查找
        mock_topic = {
            'id': f'related_{stock_code}',
            'title': f'{stock_code} 相關熱門話題',
            'category': 'stock_analysis',
            'engagement_score': 0.75
        }
        
        return mock_topic
    
    def format_tags_for_database(self, tags: List[TrendingTopicTag]) -> List[Dict[str, Any]]:
        """將標籤格式化為數據庫存儲格式"""
        formatted_tags = []
        
        for tag in tags:
            formatted_tag = {
                'topic_id': tag.topic_id,
                'topic_title': tag.topic_title,
                'topic_category': tag.topic_category,
                'engagement_score': tag.engagement_score,
                'related_stocks': ','.join(tag.related_stocks),
                'auto_generated': tag.auto_generated,
                'source': tag.source,
                'created_at': datetime.now().isoformat()
            }
            formatted_tags.append(formatted_tag)
        
        return formatted_tags
    
    def get_tag_summary(self, tags: List[TrendingTopicTag]) -> Dict[str, Any]:
        """獲取標籤摘要信息"""
        if not tags:
            return {
                'total_tags': 0,
                'categories': [],
                'stocks_covered': [],
                'avg_engagement': 0.0
            }
        
        categories = list(set(tag.topic_category for tag in tags))
        stocks_covered = list(set(stock for tag in tags for stock in tag.related_stocks))
        avg_engagement = sum(tag.engagement_score for tag in tags) / len(tags)
        
        return {
            'total_tags': len(tags),
            'categories': categories,
            'stocks_covered': stocks_covered,
            'avg_engagement': avg_engagement,
            'auto_generated_count': sum(1 for tag in tags if tag.auto_generated)
        }
