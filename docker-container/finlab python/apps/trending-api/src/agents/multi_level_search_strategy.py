"""
多層次搜尋策略
根據話題類型和股票關聯度生成智能搜尋查詢
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """搜尋查詢"""
    level: str  # direct, industry, event, market
    query: str
    priority: str  # high, medium, low
    weight: float
    strategy: str
    confidence: float

@dataclass
class SearchStrategy:
    """搜尋策略"""
    stock_code: str
    topic_id: str
    queries: List[SearchQuery]
    recommended_strategy: str
    overall_confidence: float
    timestamp: datetime

class MultiLevelSearchStrategy:
    """多層次搜尋策略"""
    
    def __init__(self, topic_analyzer):
        self.topic_analyzer = topic_analyzer
        
        # 搜尋策略模板
        self.search_templates = {
            "direct_mention": "{stock_name} {topic_title}",
            "industry_related": "{stock_name} {industry} {topic_title}",
            "market_event": "{stock_name} 市場 {topic_title}",
            "sentiment_based": "{stock_name} {sentiment} {topic_title}",
            "event_driven": "{stock_name} {event_keywords} {topic_title}",
            "comprehensive": "{stock_name} {topic_title} {industry} {sentiment}"
        }
        
        # 優先級權重
        self.priority_weights = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4
        }
    
    async def generate_search_strategy(self, topic: Dict[str, Any], stock_code: str) -> SearchStrategy:
        """生成搜尋策略"""
        try:
            # 1. 分析話題
            topic_analysis = await self.topic_analyzer.analyze_topic(topic)
            
            # 2. 計算關聯度
            relevance_score = await self.topic_analyzer.calculate_stock_relevance(topic, stock_code)
            
            # 3. 生成搜尋查詢
            queries = await self._generate_search_queries(topic, stock_code, topic_analysis, relevance_score)
            
            # 4. 選擇推薦策略
            recommended_strategy = await self._select_recommended_strategy(queries, relevance_score)
            
            # 5. 計算整體信心度
            overall_confidence = await self._calculate_overall_confidence(queries, relevance_score)
            
            return SearchStrategy(
                stock_code=stock_code,
                topic_id=topic.get('id', ''),
                queries=queries,
                recommended_strategy=recommended_strategy,
                overall_confidence=overall_confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"生成搜尋策略失敗: {e}")
            return SearchStrategy(
                stock_code=stock_code,
                topic_id=topic.get('id', ''),
                queries=[],
                recommended_strategy="fallback",
                overall_confidence=0.0,
                timestamp=datetime.now()
            )
    
    async def _generate_search_queries(self, topic: Dict[str, Any], stock_code: str, 
                                    topic_analysis, relevance_score: float) -> List[SearchQuery]:
        """生成搜尋查詢"""
        queries = []
        stock_name = self.topic_analyzer.stock_mapping.get(stock_code, "")
        topic_title = topic.get('title', '')
        
        if not stock_name:
            return queries
        
        # 層級 1：直接關聯搜尋
        if relevance_score >= 0.6:
            queries.append(SearchQuery(
                level="direct",
                query=f"{stock_name} {topic_title}",
                priority="high",
                weight=1.0,
                strategy="direct_mention",
                confidence=relevance_score
            ))
        
        # 層級 2：產業關聯搜尋
        industry = self.topic_analyzer._get_stock_industry(stock_code)
        if industry and relevance_score >= 0.3:
            industry_keywords = self.topic_analyzer.industry_keywords.get(industry, [])
            industry_context = " ".join(industry_keywords[:2])  # 取前兩個關鍵字
            
            queries.append(SearchQuery(
                level="industry",
                query=f"{stock_name} {industry_context} {topic_title}",
                priority="medium",
                weight=0.8,
                strategy="industry_related",
                confidence=relevance_score * 0.8
            ))
        
        # 層級 3：事件關聯搜尋
        event_entities = [e for e in topic_analysis.entities if e.type == "EVENT"]
        if event_entities and relevance_score >= 0.2:
            event_keywords = " ".join([e.text for e in event_entities[:2]])
            
            queries.append(SearchQuery(
                level="event",
                query=f"{stock_name} {event_keywords} {topic_title}",
                priority="medium",
                weight=0.6,
                strategy="event_driven",
                confidence=relevance_score * 0.6
            ))
        
        # 層級 4：情感關聯搜尋
        if topic_analysis.sentiment != "neutral" and relevance_score >= 0.1:
            sentiment_keywords = {
                "positive": "上漲 看好 利多",
                "negative": "下跌 看壞 利空",
                "neutral": "持平 觀望"
            }.get(topic_analysis.sentiment, "")
            
            if sentiment_keywords:
                queries.append(SearchQuery(
                    level="sentiment",
                    query=f"{stock_name} {sentiment_keywords} {topic_title}",
                    priority="low",
                    weight=0.4,
                    strategy="sentiment_based",
                    confidence=relevance_score * 0.4
                ))
        
        # 層級 5：市場關聯搜尋
        if topic_analysis.topic_type == "market_trend" and relevance_score >= 0.1:
            queries.append(SearchQuery(
                level="market",
                query=f"{stock_name} 市場 {topic_title}",
                priority="low",
                weight=0.3,
                strategy="market_event",
                confidence=relevance_score * 0.3
            ))
        
        # 層級 6：綜合搜尋（備用）
        if not queries and relevance_score >= 0.05:
            queries.append(SearchQuery(
                level="comprehensive",
                query=f"{stock_name} {topic_title}",
                priority="low",
                weight=0.2,
                strategy="comprehensive",
                confidence=relevance_score * 0.2
            ))
        
        return queries
    
    async def _select_recommended_strategy(self, queries: List[SearchQuery], relevance_score: float) -> str:
        """選擇推薦策略"""
        if not queries:
            return "fallback"
        
        # 根據優先級和信心度選擇最佳策略
        best_query = max(queries, key=lambda q: q.weight * q.confidence)
        
        # 根據關聯度調整策略
        if relevance_score >= 0.8:
            return "high_confidence"
        elif relevance_score >= 0.5:
            return "medium_confidence"
        elif relevance_score >= 0.2:
            return "low_confidence"
        else:
            return "fallback"
    
    async def _calculate_overall_confidence(self, queries: List[SearchQuery], relevance_score: float) -> float:
        """計算整體信心度"""
        if not queries:
            return 0.0
        
        # 基礎信心度
        base_confidence = relevance_score
        
        # 查詢數量加分
        query_bonus = min(len(queries) * 0.1, 0.3)
        
        # 最高優先級查詢的信心度
        high_priority_queries = [q for q in queries if q.priority == "high"]
        if high_priority_queries:
            max_confidence = max(q.confidence for q in high_priority_queries)
            confidence_bonus = max_confidence * 0.2
        else:
            confidence_bonus = 0.0
        
        return min(base_confidence + query_bonus + confidence_bonus, 1.0)
    
    def get_search_keywords_for_news(self, search_strategy: SearchStrategy) -> List[str]:
        """為新聞搜尋生成關鍵字列表"""
        keywords = []
        
        # 按優先級排序查詢
        sorted_queries = sorted(search_strategy.queries, 
                             key=lambda q: self.priority_weights[q.priority], 
                             reverse=True)
        
        # 選擇前3個最有信心的查詢
        for query in sorted_queries[:3]:
            if query.confidence >= 0.3:  # 只選擇信心度足夠的查詢
                keywords.append(query.query)
        
        # 如果沒有足夠的查詢，使用備用策略
        if not keywords:
            stock_name = self.topic_analyzer.stock_mapping.get(search_strategy.stock_code, "")
            if stock_name:
                keywords.append(f"{stock_name} 熱門話題")
        
        return keywords
