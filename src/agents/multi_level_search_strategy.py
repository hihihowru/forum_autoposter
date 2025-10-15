#!/usr/bin/env python3
"""
多層次搜尋策略
根據話題分析結果，執行多種搜尋策略來獲取相關新聞
"""

import logging
import requests
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from .intelligent_topic_analyzer import IntelligentTopicAnalyzer, KeywordAnalysis

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class NewsSearchResult:
    """新聞搜尋結果"""
    title: str
    snippet: str
    url: str
    published_at: Optional[datetime]
    relevance_score: float
    search_query: str
    source: str

class SerperNewsClient:
    """Serper API 新聞搜尋客戶端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
    
    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """搜尋新聞"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": num_results,
                "type": "search"
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get('organic', [])
            
            # 轉換為標準格式
            news_results = []
            for result in organic_results:
                news_results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'date': result.get('date', ''),
                    'source': result.get('source', ''),
                    'search_query': query
                })
            
            return news_results
            
        except Exception as e:
            logger.error(f"搜尋新聞失敗: {e}")
            return []

class MultiLevelSearchStrategy:
    """多層次搜尋策略"""
    
    def __init__(self, topic_analyzer: IntelligentTopicAnalyzer):
        self.topic_analyzer = topic_analyzer
        self.news_client = SerperNewsClient()
        
    async def search_trending_topic_news(self, topic_title: str, topic_content: str = "", stock_ids: List[str] = None, post_id: str = None) -> List[NewsSearchResult]:
        """搜尋熱門話題相關新聞 - 每個貼文獨立搜尋"""
        try:
            post_identifier = f"{post_id or 'unknown'}_{topic_title}_{stock_ids or 'no_stock'}"
            logger.info(f"開始搜尋熱門話題新聞 (貼文ID: {post_identifier}): {topic_title}")
            
            # 1. 分析話題並提取關鍵字 - 每個貼文獨立分析
            analysis = self.topic_analyzer.analyze_topic(topic_title, topic_content, stock_ids)
            logger.info(f"貼文 {post_identifier} 關鍵字分析完成: {len(analysis.search_queries)} 個搜尋查詢")
            
            # 2. 執行多層次搜尋 - 每個貼文獨立搜尋
            search_results = await self._execute_multi_level_search(analysis, topic_title, stock_ids, post_identifier)
            
            # 3. 去重並評分 - 只在當前貼文內去重
            unique_results = self._deduplicate_and_score(search_results)
            
            logger.info(f"貼文 {post_identifier} 找到 {len(unique_results)} 條相關新聞")
            return unique_results
            
        except Exception as e:
            logger.error(f"搜尋熱門話題新聞失敗 (貼文ID: {post_identifier}): {e}")
            return []
    
    async def _execute_multi_level_search(self, analysis: KeywordAnalysis, topic_title: str, stock_ids: List[str] = None, post_identifier: str = None) -> List[NewsSearchResult]:
        """執行多層次搜尋 - 每個貼文獨立搜尋"""
        all_results = []
        
        # 層次1: 使用 LLM 生成的搜尋查詢
        for query in analysis.search_queries:
            results = await self._search_with_query(query, "llm_generated", post_identifier)
            all_results.extend(results)
        
        # 層次2: 股票相關搜尋（如果有股票）
        if stock_ids:
            for stock_id in stock_ids[:2]:  # 最多搜尋前2個股票
                # 股票 + 主要關鍵字
                for keyword in analysis.primary_keywords[:2]:
                    query = f"{stock_id} {keyword}"
                    results = await self._search_with_query(query, "stock_keyword", post_identifier)
                    all_results.extend(results)
                
                # 股票 + 話題標題
                query = f"{stock_id} {topic_title}"
                results = await self._search_with_query(query, "stock_topic", post_identifier)
                all_results.extend(results)
        
        # 層次3: 產業相關搜尋
        for industry_keyword in analysis.industry_keywords[:2]:
            query = f"{industry_keyword} {topic_title}"
            results = await self._search_with_query(query, "industry", post_identifier)
            all_results.extend(results)
        
        # 層次4: 情感相關搜尋
        for sentiment_keyword in analysis.sentiment_keywords[:2]:
            query = f"{sentiment_keyword} {topic_title}"
            results = await self._search_with_query(query, "sentiment", post_identifier)
            all_results.extend(results)
        
        # 層次5: 純話題搜尋（用於沒有股票的話題）
        if not stock_ids:
            # 主要關鍵字組合
            if len(analysis.primary_keywords) >= 2:
                query = f"{analysis.primary_keywords[0]} {analysis.primary_keywords[1]}"
                results = await self._search_with_query(query, "primary_keywords", post_identifier)
                all_results.extend(results)
            
            # 話題標題本身
            results = await self._search_with_query(topic_title, "topic_title", post_identifier)
            all_results.extend(results)
        
        return all_results
    
    async def _search_with_query(self, query: str, search_type: str, post_identifier: str = None) -> List[NewsSearchResult]:
        """使用特定查詢搜尋新聞 - 每個貼文獨立搜尋"""
        try:
            logger.info(f"搜尋查詢 (貼文: {post_identifier}): {query} (類型: {search_type})")
            
            news_data = await self.news_client.search_news(query, 3)
            
            results = []
            for news in news_data:
                result = NewsSearchResult(
                    title=news['title'],
                    snippet=news['snippet'],
                    url=news['link'],
                    published_at=self._parse_date(news['date']),
                    relevance_score=self._calculate_relevance_score(news, query, search_type),
                    search_query=query,
                    source=f"{search_type}_{post_identifier or 'unknown'}"  # 包含貼文ID避免混淆
                )
                results.append(result)
            
            logger.info(f"貼文 {post_identifier} 查詢 '{query}' 找到 {len(results)} 條新聞")
            return results
            
        except Exception as e:
            logger.error(f"搜尋查詢失敗 {query} (貼文: {post_identifier}): {e}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 嘗試解析不同的日期格式
            date_formats = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y",
                "%d/%m/%Y"
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _calculate_relevance_score(self, news: Dict[str, Any], query: str, search_type: str) -> float:
        """計算新聞相關性分數"""
        score = 0.5  # 基礎分數
        
        title = news['title'].lower()
        snippet = news['snippet'].lower()
        query_lower = query.lower()
        
        # 查詢關鍵字在標題中的匹配
        query_words = query_lower.split()
        title_matches = sum(1 for word in query_words if word in title)
        score += (title_matches / len(query_words)) * 0.3
        
        # 查詢關鍵字在摘要中的匹配
        snippet_matches = sum(1 for word in query_words if word in snippet)
        score += (snippet_matches / len(query_words)) * 0.2
        
        # 根據搜尋類型調整分數
        type_multipliers = {
            "llm_generated": 1.0,
            "stock_keyword": 0.9,
            "stock_topic": 0.8,
            "industry": 0.7,
            "sentiment": 0.6,
            "primary_keywords": 0.8,
            "topic_title": 0.7
        }
        
        score *= type_multipliers.get(search_type, 0.5)
        
        return min(score, 1.0)  # 確保分數不超過1.0
    
    def _deduplicate_and_score(self, results: List[NewsSearchResult]) -> List[NewsSearchResult]:
        """去重並重新評分"""
        # 按URL去重
        unique_results = {}
        for result in results:
            if result.url not in unique_results:
                unique_results[result.url] = result
            else:
                # 如果已存在，選擇分數更高的
                existing = unique_results[result.url]
                if result.relevance_score > existing.relevance_score:
                    unique_results[result.url] = result
        
        # 按相關性分數排序
        sorted_results = sorted(unique_results.values(), key=lambda x: x.relevance_score, reverse=True)
        
        return sorted_results[:10]  # 最多返回10條新聞
