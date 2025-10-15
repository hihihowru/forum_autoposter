"""
智能話題分析器
提供語義分析、關聯度評估和動態搜尋策略
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SemanticEntity:
    """語義實體"""
    text: str
    type: str  # COMPANY, EVENT, NUMBER, SENTIMENT
    confidence: float
    position: int

@dataclass
class TopicAnalysis:
    """話題分析結果"""
    topic_id: str
    topic_type: str  # market_trend, company_news, industry_event, general
    entities: List[SemanticEntity]
    sentiment: str  # positive, negative, neutral
    confidence: float
    market_impact: str  # high, medium, low
    timestamp: datetime

class IntelligentTopicAnalyzer:
    """智能話題分析器"""
    
    def __init__(self):
        # 股票代號到名稱的映射
        self.stock_mapping = {
            "2330": "台積電", "2454": "聯發科", "2317": "鴻海",
            "2881": "富邦金", "2882": "國泰金", "1101": "台泥",
            "1102": "亞泥", "1216": "統一", "1303": "南亞",
            "2002": "中鋼", "2308": "台達電", "2412": "中華電",
            "2603": "長榮", "2609": "陽明", "2615": "萬海",
            "2891": "中信金", "2886": "兆豐金", "2880": "華南金",
            "2884": "玉山金", "2885": "元大金", "TWA00": "台指期"
        }
        
        # 產業關鍵字
        self.industry_keywords = {
            "半導體": ["台積電", "聯發科", "台達電", "半導體", "晶片", "IC"],
            "金融": ["富邦金", "國泰金", "中信金", "兆豐金", "華南金", "玉山金", "元大金", "金融", "銀行"],
            "航運": ["長榮", "陽明", "萬海", "航運", "海運"],
            "鋼鐵": ["中鋼", "鋼鐵", "鋼材"],
            "水泥": ["台泥", "亞泥", "水泥"],
            "食品": ["統一", "食品", "飲料"],
            "石化": ["南亞", "石化", "塑膠"],
            "電信": ["中華電", "電信", "通訊"],
            "期貨": ["台指期", "期貨", "指數"]
        }
        
        # 市場事件關鍵字
        self.market_event_keywords = [
            "漲停", "跌停", "漲停板", "跌停板", "漲幅", "跌幅",
            "成交量", "成交金額", "外資", "投信", "自營商",
            "融資", "融券", "除權", "除息", "配股", "配息",
            "財報", "季報", "年報", "法說會", "股東會"
        ]
        
        # 情感關鍵字
        self.sentiment_keywords = {
            "positive": ["上漲", "漲停", "突破", "創新高", "強勢", "看好", "利多", "成長", "獲利"],
            "negative": ["下跌", "跌停", "破底", "創低", "弱勢", "看壞", "利空", "衰退", "虧損"],
            "neutral": ["持平", "震盪", "整理", "觀望", "中性", "穩定"]
        }
    
    async def analyze_topic(self, topic: Dict[str, Any]) -> TopicAnalysis:
        """分析話題"""
        try:
            content = f"{topic.get('title', '')} {topic.get('content', '')}"
            
            # 1. 提取語義實體
            entities = await self._extract_semantic_entities(content)
            
            # 2. 分類話題類型
            topic_type = await self._classify_topic_type(content, entities)
            
            # 3. 分析情感
            sentiment = await self._analyze_sentiment(content)
            
            # 4. 評估市場影響
            market_impact = await self._assess_market_impact(content, entities)
            
            # 5. 計算信心度
            confidence = await self._calculate_confidence(entities, topic_type, sentiment)
            
            return TopicAnalysis(
                topic_id=topic.get('id', ''),
                topic_type=topic_type,
                entities=entities,
                sentiment=sentiment,
                confidence=confidence,
                market_impact=market_impact,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"話題分析失敗: {e}")
            return TopicAnalysis(
                topic_id=topic.get('id', ''),
                topic_type="general",
                entities=[],
                sentiment="neutral",
                confidence=0.0,
                market_impact="low",
                timestamp=datetime.now()
            )
    
    async def _extract_semantic_entities(self, content: str) -> List[SemanticEntity]:
        """提取語義實體"""
        entities = []
        
        # 提取公司名稱
        for stock_code, stock_name in self.stock_mapping.items():
            if stock_name in content:
                entities.append(SemanticEntity(
                    text=stock_name,
                    type="COMPANY",
                    confidence=0.9,
                    position=content.find(stock_name)
                ))
        
        # 提取市場事件
        for event in self.market_event_keywords:
            if event in content:
                entities.append(SemanticEntity(
                    text=event,
                    type="EVENT",
                    confidence=0.8,
                    position=content.find(event)
                ))
        
        # 提取數字
        numbers = re.findall(r'\d+\.?\d*', content)
        for number in numbers:
            entities.append(SemanticEntity(
                text=number,
                type="NUMBER",
                confidence=0.7,
                position=content.find(number)
            ))
        
        return entities
    
    async def _classify_topic_type(self, content: str, entities: List[SemanticEntity]) -> str:
        """分類話題類型"""
        # 檢查是否為市場趨勢
        market_indicators = ["大盤", "指數", "台股", "美股", "市場", "加權", "櫃買"]
        if any(indicator in content for indicator in market_indicators):
            return "market_trend"
        
        # 檢查是否為公司新聞
        company_entities = [e for e in entities if e.type == "COMPANY"]
        if len(company_entities) >= 2:  # 多個公司提及
            return "company_news"
        
        # 檢查是否為產業事件
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in content for keyword in keywords):
                return "industry_event"
        
        return "general"
    
    async def _analyze_sentiment(self, content: str) -> str:
        """分析情感"""
        positive_count = sum(1 for keyword in self.sentiment_keywords["positive"] if keyword in content)
        negative_count = sum(1 for keyword in self.sentiment_keywords["negative"] if keyword in content)
        neutral_count = sum(1 for keyword in self.sentiment_keywords["neutral"] if keyword in content)
        
        if positive_count > negative_count and positive_count > neutral_count:
            return "positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            return "negative"
        else:
            return "neutral"
    
    async def _assess_market_impact(self, content: str, entities: List[SemanticEntity]) -> str:
        """評估市場影響"""
        # 高影響指標
        high_impact_keywords = ["創新高", "破底", "漲停", "跌停", "外資", "投信", "法說會"]
        if any(keyword in content for keyword in high_impact_keywords):
            return "high"
        
        # 中影響指標
        medium_impact_keywords = ["上漲", "下跌", "突破", "成交量", "財報"]
        if any(keyword in content for keyword in medium_impact_keywords):
            return "medium"
        
        return "low"
    
    async def _calculate_confidence(self, entities: List[SemanticEntity], topic_type: str, sentiment: str) -> float:
        """計算信心度"""
        base_confidence = 0.5
        
        # 實體數量加分
        entity_bonus = min(len(entities) * 0.1, 0.3)
        
        # 話題類型加分
        type_bonus = {
            "market_trend": 0.2,
            "company_news": 0.15,
            "industry_event": 0.1,
            "general": 0.0
        }.get(topic_type, 0.0)
        
        # 情感明確性加分
        sentiment_bonus = 0.1 if sentiment != "neutral" else 0.0
        
        return min(base_confidence + entity_bonus + type_bonus + sentiment_bonus, 1.0)
    
    async def calculate_stock_relevance(self, topic: Dict[str, Any], stock_code: str) -> float:
        """計算話題與股票的關聯度"""
        try:
            content = f"{topic.get('title', '')} {topic.get('content', '')}"
            stock_name = self.stock_mapping.get(stock_code, "")
            
            if not stock_name:
                return 0.0
            
            relevance_score = 0.0
            
            # 直接提及加分
            if stock_name in content:
                relevance_score += 0.8
            
            # 股票代號提及加分
            if stock_code in content:
                relevance_score += 0.6
            
            # 產業關聯加分
            stock_industry = self._get_stock_industry(stock_code)
            if stock_industry:
                industry_keywords = self.industry_keywords.get(stock_industry, [])
                if any(keyword in content for keyword in industry_keywords):
                    relevance_score += 0.4
            
            # 市場事件關聯加分
            if any(event in content for event in self.market_event_keywords):
                relevance_score += 0.2
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            logger.error(f"計算股票關聯度失敗: {e}")
            return 0.0
    
    def _get_stock_industry(self, stock_code: str) -> Optional[str]:
        """獲取股票產業"""
        for industry, keywords in self.industry_keywords.items():
            if stock_code in keywords or self.stock_mapping.get(stock_code, "") in keywords:
                return industry
        return None
