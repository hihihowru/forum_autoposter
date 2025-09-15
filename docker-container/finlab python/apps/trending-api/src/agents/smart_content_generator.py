"""
智能內容生成器
整合話題、股票數據、新聞結果生成上下文相關的內容
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ContentContext:
    """內容上下文"""
    topic: Dict[str, Any]
    stock_data: Dict[str, Any]
    news_results: List[Dict[str, Any]]
    topic_analysis: Any
    search_strategy: Any
    timestamp: datetime

@dataclass
class GeneratedContent:
    """生成的內容"""
    content: str
    style: str
    confidence: float
    data_sources: List[str]
    news_sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime

class SmartContentGenerator:
    """智能內容生成器"""
    
    def __init__(self):
        # 內容風格模板
        self.content_styles = {
            "technical": {
                "tone": "專業分析",
                "focus": "技術指標和數據",
                "length": "中等",
                "structure": "數據支撐 + 技術分析 + 結論"
            },
            "fundamental": {
                "tone": "基本面分析",
                "focus": "公司財務和產業趨勢",
                "length": "較長",
                "structure": "產業分析 + 財務數據 + 投資建議"
            },
            "news_driven": {
                "tone": "新聞解讀",
                "focus": "事件影響和市場反應",
                "length": "中等",
                "structure": "事件背景 + 市場影響 + 後續觀察"
            },
            "market_trend": {
                "tone": "市場趨勢",
                "focus": "大盤走勢和資金流向",
                "length": "中等",
                "structure": "趨勢分析 + 資金流向 + 投資策略"
            }
        }
        
        # 內容生成模板
        self.content_templates = {
            "market_trend": """
基於熱門話題「{topic_title}」的分析：

📊 市場數據：
{stock_data_summary}

📰 相關新聞：
{news_summary}

💡 分析觀點：
{analysis_content}

🎯 投資建議：
{investment_advice}
""",
            "company_news": """
針對 {stock_name} 的熱門話題分析：

📈 股價表現：
{price_performance}

📊 基本面數據：
{fundamental_data}

📰 市場消息：
{market_news}

💭 投資觀點：
{investment_perspective}
""",
            "industry_event": """
產業事件「{topic_title}」對 {stock_name} 的影響：

🏭 產業背景：
{industry_background}

📊 公司表現：
{company_performance}

📰 事件影響：
{event_impact}

🎯 投資策略：
{investment_strategy}
"""
        }
    
    async def generate_contextual_content(self, context: ContentContext) -> GeneratedContent:
        """生成上下文相關的內容"""
        try:
            # 1. 分析內容類型
            content_type = await self._determine_content_type(context)
            
            # 2. 選擇內容風格
            content_style = await self._select_content_style(context, content_type)
            
            # 3. 生成內容摘要
            content_summary = await self._generate_content_summary(context)
            
            # 4. 添加數據支撐
            data_support = await self._extract_data_support(context)
            
            # 5. 生成最終內容
            final_content = await self._generate_final_content(context, content_type, content_style, content_summary, data_support)
            
            # 6. 計算信心度
            confidence = await self._calculate_content_confidence(final_content, context)
            
            return GeneratedContent(
                content=final_content,
                style=content_style,
                confidence=confidence,
                data_sources=data_support.get("sources", []),
                news_sources=data_support.get("news", []),
                metadata={
                    "content_type": content_type,
                    "topic_type": context.topic_analysis.topic_type,
                    "sentiment": context.topic_analysis.sentiment,
                    "market_impact": context.topic_analysis.market_impact,
                    "search_strategy": context.search_strategy.recommended_strategy
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"生成內容失敗: {e}")
            return GeneratedContent(
                content="內容生成失敗，請稍後再試",
                style="fallback",
                confidence=0.0,
                data_sources=[],
                news_sources=[],
                metadata={"error": str(e)},
                timestamp=datetime.now()
            )
    
    async def _determine_content_type(self, context: ContentContext) -> str:
        """確定內容類型"""
        topic_type = context.topic_analysis.topic_type
        confidence = context.search_strategy.overall_confidence
        
        if topic_type == "market_trend":
            return "market_trend"
        elif topic_type == "company_news" and confidence >= 0.6:
            return "company_news"
        elif topic_type == "industry_event":
            return "industry_event"
        else:
            return "general"
    
    async def _select_content_style(self, context: ContentContext, content_type: str) -> str:
        """選擇內容風格"""
        # 根據話題類型和信心度選擇風格
        if content_type == "market_trend":
            return "market_trend"
        elif content_type == "company_news":
            return "fundamental"
        elif content_type == "industry_event":
            return "technical"
        else:
            return "news_driven"
    
    async def _generate_content_summary(self, context: ContentContext) -> Dict[str, str]:
        """生成內容摘要"""
        topic = context.topic
        stock_data = context.stock_data
        news_results = context.news_results
        
        # 股票數據摘要
        stock_summary = ""
        if stock_data:
            price = stock_data.get("closing_price", "N/A")
            change = stock_data.get("change_percent", "N/A")
            stock_summary = f"收盤價: {price}, 漲跌幅: {change}%"
        
        # 新聞摘要
        news_summary = ""
        if news_results:
            news_titles = [news.get("title", "")[:50] for news in news_results[:3]]
            news_summary = " | ".join(news_titles)
        
        # 話題摘要
        topic_summary = f"熱門話題: {topic.get('title', '')}"
        
        return {
            "stock_summary": stock_summary,
            "news_summary": news_summary,
            "topic_summary": topic_summary
        }
    
    async def _extract_data_support(self, context: ContentContext) -> Dict[str, Any]:
        """提取數據支撐"""
        data_sources = []
        news_sources = []
        
        # 股票數據來源
        if context.stock_data:
            data_sources.append("FinLab API")
        
        # 新聞來源
        for news in context.news_results:
            if news.get("url"):
                news_sources.append({
                    "title": news.get("title", ""),
                    "url": news.get("url", ""),
                    "source": news.get("source", "")
                })
        
        return {
            "sources": data_sources,
            "news": news_sources
        }
    
    async def _generate_final_content(self, context: ContentContext, content_type: str, 
                                   content_style: str, content_summary: Dict[str, str], 
                                   data_support: Dict[str, Any]) -> str:
        """生成最終內容"""
        topic = context.topic
        stock_data = context.stock_data
        
        # 獲取股票名稱
        stock_name = stock_data.get("name", "該股票") if stock_data else "該股票"
        
        # 根據內容類型選擇模板
        template = self.content_templates.get(content_type, self.content_templates["market_trend"])
        
        # 填充模板
        content = template.format(
            topic_title=topic.get("title", ""),
            stock_name=stock_name,
            stock_data_summary=content_summary["stock_summary"],
            news_summary=content_summary["news_summary"],
            analysis_content=await self._generate_analysis_content(context),
            investment_advice=await self._generate_investment_advice(context),
            price_performance=content_summary["stock_summary"],
            fundamental_data=await self._generate_fundamental_data(context),
            market_news=content_summary["news_summary"],
            investment_perspective=await self._generate_investment_perspective(context),
            industry_background=await self._generate_industry_background(context),
            company_performance=content_summary["stock_summary"],
            event_impact=await self._generate_event_impact(context),
            investment_strategy=await self._generate_investment_strategy(context)
        )
        
        return content.strip()
    
    async def _generate_analysis_content(self, context: ContentContext) -> str:
        """生成分析內容"""
        sentiment = context.topic_analysis.sentiment
        market_impact = context.topic_analysis.market_impact
        
        if sentiment == "positive":
            return "從技術面來看，市場情緒偏向樂觀，投資人對後市抱持正面態度。"
        elif sentiment == "negative":
            return "市場出現謹慎情緒，投資人需要關注風險控制。"
        else:
            return "市場呈現中性態度，建議保持觀望並密切關注後續發展。"
    
    async def _generate_investment_advice(self, context: ContentContext) -> str:
        """生成投資建議"""
        confidence = context.search_strategy.overall_confidence
        
        if confidence >= 0.7:
            return "基於高信心度分析，建議密切關注相關標的。"
        elif confidence >= 0.4:
            return "建議謹慎評估，可考慮小額試單。"
        else:
            return "建議保持觀望，等待更多明確訊號。"
    
    async def _generate_fundamental_data(self, context: ContentContext) -> str:
        """生成基本面數據"""
        stock_data = context.stock_data
        if stock_data:
            return f"收盤價: {stock_data.get('closing_price', 'N/A')}, 成交量: {stock_data.get('volume', 'N/A')}"
        return "基本面數據待更新"
    
    async def _generate_investment_perspective(self, context: ContentContext) -> str:
        """生成投資觀點"""
        topic_type = context.topic_analysis.topic_type
        
        if topic_type == "company_news":
            return "公司層面的消息通常對股價有直接影響，建議關注後續發展。"
        elif topic_type == "industry_event":
            return "產業事件可能影響整個板塊，需要評估對個股的具體影響。"
        else:
            return "建議綜合多個因素進行投資決策。"
    
    async def _generate_industry_background(self, context: ContentContext) -> str:
        """生成產業背景"""
        return "相關產業正處於發展階段，需要關注政策面和基本面變化。"
    
    async def _generate_event_impact(self, context: ContentContext) -> str:
        """生成事件影響"""
        market_impact = context.topic_analysis.market_impact
        
        if market_impact == "high":
            return "此事件對市場影響較大，建議密切關注。"
        elif market_impact == "medium":
            return "事件影響中等，需要持續觀察。"
        else:
            return "事件影響相對有限，但仍需關注。"
    
    async def _generate_investment_strategy(self, context: ContentContext) -> str:
        """生成投資策略"""
        sentiment = context.topic_analysis.sentiment
        
        if sentiment == "positive":
            return "可考慮逢低布局，但需控制風險。"
        elif sentiment == "negative":
            return "建議保守操作，避免追高。"
        else:
            return "建議保持中性策略，等待明確訊號。"
    
    async def _calculate_content_confidence(self, content: str, context: ContentContext) -> float:
        """計算內容信心度"""
        base_confidence = context.search_strategy.overall_confidence
        
        # 內容長度加分
        length_bonus = min(len(content) / 1000, 0.2)
        
        # 數據支撐加分
        data_bonus = 0.1 if context.stock_data else 0.0
        
        # 新聞支撐加分
        news_bonus = min(len(context.news_results) * 0.05, 0.15)
        
        return min(base_confidence + length_bonus + data_bonus + news_bonus, 1.0)
