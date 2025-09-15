#!/usr/bin/env python3
"""
Serper API 客戶端
用於搜索新聞和相關資訊
"""

import os
import aiohttp
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NewsResult:
    """新聞結果結構"""
    title: str
    link: str
    snippet: str
    source: str
    date: str
    relevance_score: float

@dataclass
class SearchResult:
    """搜索結果結構"""
    query: str
    total_results: int
    news_results: List[NewsResult]
    organic_results: List[Dict[str, Any]]
    search_time: datetime

class SerperAPIClient:
    """Serper API 客戶端"""
    
    def __init__(self):
        """初始化 Serper API 客戶端"""
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 SERPER_API_KEY 環境變數")
        
        self.base_url = "https://google.serper.dev/search"
        self.session = None
        
        # 可信財經媒體網站列表
        self.trusted_sites = [
            # 📰 主流財經新聞媒體
            "udn.com",
            "ctee.com.tw", 
            "money.udn.com",
            "ec.ltn.com.tw",
            "www.chinatimes.com",
            "www.cnyes.com",
            "news.cnyes.com",
            "tw.stock.yahoo.com",
            "www.businesstoday.com.tw",
            "www.businessweekly.com.tw",
            
            # 📊 財經數據 / 投資研究
            "www.cmoney.tw",
            "statementdog.com",
            "www.macromicro.me",
            "histock.tw",
            "www.wantgoo.com",
            
            # 🏦 官方與交易所
            "www.twse.com.tw",
            "www.tpex.org.tw",
            "www.taifex.com.tw",
            "mops.twse.com.tw",
            
            # 📺 財經電視 / 新聞延伸
            "moneydj.com",
            "www.setn.com/money",
            "news.tvbs.com.tw/money",
            "news.ltn.com.tw/list/business",
            "www.storm.mg/business"
        ]
        
        logger.info("Serper API 客戶端初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def search_news(self, query: str, num_results: int = 10) -> Optional[SearchResult]:
        """搜索新聞"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # 構建查詢（使用可信媒體限制）
            site_restrictions = " OR ".join([f"site:{site}" for site in self.trusted_sites])
            enhanced_query = f"({query}) AND ({site_restrictions})"
            
            payload = {
                'q': enhanced_query,
                'num': num_results * 3,  # 增加搜索數量以彌補網站限制和索引延遲
                'gl': 'tw',  # 台灣地區
                'hl': 'zh-TW',  # 繁體中文
                'type': 'news',  # 新聞搜索
                'sort': 'date'  # 按日期排序，優先最新
            }
            
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                # 調試：記錄請求詳情
                logger.debug(f"Serper API 請求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                logger.debug(f"Serper API 響應狀態: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # 調試：記錄 API 響應
                    logger.debug(f"Serper API 響應: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    
                    news_results = []
                    if 'newsResults' in data:
                        for news in data['newsResults']:
                            # 檢查是否來自可信網站
                            if self._is_trusted_source(news.get('link', '')):
                                news_results.append(NewsResult(
                                    title=news.get('title', ''),
                                    link=news.get('link', ''),
                                    snippet=news.get('snippet', ''),
                                    source=news.get('source', ''),
                                    date=news.get('date', ''),
                                    relevance_score=news.get('relevance_score', 0.0)
                                ))
                    elif 'news' in data:
                        for news in data['news']:
                            # 檢查是否來自可信網站
                            if self._is_trusted_source(news.get('link', '')):
                                news_results.append(NewsResult(
                                    title=news.get('title', ''),
                                    link=news.get('link', ''),
                                    snippet=news.get('snippet', ''),
                                    source=news.get('source', ''),
                                    date=news.get('date', ''),
                                    relevance_score=news.get('relevance_score', 0.0)
                                ))
                    else:
                        logger.warning(f"API 響應中沒有 newsResults 或 news: {list(data.keys())}")
                    
                    # 按日期和相關性排序
                    news_results = self._sort_news_by_relevance_and_date(news_results)
                    
                    # 限制結果數量
                    news_results = news_results[:num_results]
                    
                    organic_results = data.get('organic', [])
                    
                    return SearchResult(
                        query=query,
                        total_results=len(news_results) + len(organic_results),
                        news_results=news_results,
                        organic_results=organic_results,
                        search_time=datetime.now()
                    )
                
                # 記錄錯誤響應詳情
                error_text = await response.text()
                logger.error(f"Serper API 搜索失敗: {response.status}")
                logger.error(f"錯誤響應: {error_text}")
                return None
                
        except Exception as e:
            logger.error(f"Serper API 搜索時發生錯誤: {e}")
            return None
    
    def _is_trusted_source(self, url: str) -> bool:
        """檢查 URL 是否來自可信來源"""
        if not url:
            return False
        
        url_lower = url.lower()
        return any(site in url_lower for site in self.trusted_sites)
    
    def _sort_news_by_relevance_and_date(self, news_results: List[NewsResult]) -> List[NewsResult]:
        """按相關性和日期排序新聞"""
        def sort_key(news):
            # 優先考慮相關性分數
            relevance_score = news.relevance_score or 0.0
            
            # 日期加分：越新越好
            date_bonus = 0.0
            if news.date:
                try:
                    # 嘗試解析日期
                    if '小時前' in news.date or '分鐘前' in news.date:
                        date_bonus = 1.0
                    elif '天前' in news.date:
                        days_ago = int(news.date.split('天前')[0])
                        if days_ago <= 1:
                            date_bonus = 0.8
                        elif days_ago <= 3:
                            date_bonus = 0.6
                        elif days_ago <= 7:
                            date_bonus = 0.4
                        else:
                            date_bonus = 0.2
                    else:
                        # 其他日期格式，給予中等分數
                        date_bonus = 0.5
                except:
                    date_bonus = 0.3
            
            # 內容相關性加分
            content_bonus = 0.0
            title_lower = news.title.lower()
            snippet_lower = news.snippet.lower()
            
            # 股價變化相關關鍵詞
            price_change_keywords = [
                '漲停', '上漲', '大漲', '飆漲', '突破', '創高', '新高',
                '利多', '好消息', '正面', '看好', '成長', '獲利',
                '營收', '財報', 'EPS', '獲利', '業績', '訂單',
                '合作', '併購', '新產品', '技術', '市場'
            ]
            
            for keyword in price_change_keywords:
                if keyword in title_lower or keyword in snippet_lower:
                    content_bonus += 0.1
            
            return -(relevance_score + date_bonus + content_bonus)
        
        return sorted(news_results, key=sort_key)
    
    async def search_stock_news(self, stock_id: str, stock_name: str, num_results: int = 5) -> Optional[SearchResult]:
        """搜索股票相關新聞"""
        # 優先搜尋股價變化原因
        query = f'"{stock_name}" "{stock_id}" (漲停 OR 上漲 OR 大漲 OR 飆漲 OR 突破 OR 創高 OR 利多 OR 好消息)'
        return await self.search_news(query, num_results)
    
    async def search_revenue_news(self, stock_id: str, stock_name: str) -> Optional[SearchResult]:
        """搜索營收相關新聞"""
        query = f'"{stock_name}" "{stock_id}" (營收 OR 月營收 OR 財報 OR 獲利 OR 成長 OR 業績)'
        return await self.search_news(query, 3)
    
    async def search_earnings_news(self, stock_id: str, stock_name: str) -> Optional[SearchResult]:
        """搜索財報相關新聞"""
        query = f'"{stock_name}" "{stock_id}" (財報 OR EPS OR 獲利 OR 盈餘 OR 業績 OR 成長)'
        return await self.search_news(query, 3)
    
    async def search_market_news(self, stock_id: str, stock_name: str) -> Optional[SearchResult]:
        """搜索市場相關新聞"""
        query = f'"{stock_name}" "{stock_id}" (股價 OR 技術分析 OR 市場 OR 利多 OR 好消息 OR 突破)'
        return await self.search_news(query, 3)
    
    async def generate_news_summary(self, news_results: List[NewsResult], summary_count: int = 3) -> List[str]:
        """生成新聞摘要"""
        if not news_results:
            return []
        
        # 按相關性排序
        sorted_news = sorted(news_results, key=lambda x: x.relevance_score, reverse=True)
        
        summaries = []
        for i, news in enumerate(sorted_news[:summary_count]):
            summary = f"{i+1}. {news.title} - {news.snippet[:100]}..."
            summaries.append(summary)
        
        return summaries
    
    async def get_comprehensive_news_analysis(self, stock_id: str, stock_name: str) -> Dict[str, Any]:
        """獲取股票綜合新聞分析"""
        try:
            # 並行搜索不同類型的新聞
            tasks = [
                self.search_revenue_news(stock_id, stock_name),
                self.search_earnings_news(stock_id, stock_name),
                self.search_market_news(stock_id, stock_name)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            revenue_news, earnings_news, market_news = results
            
            analysis = {
                'stock_id': stock_id,
                'stock_name': stock_name,
                'analysis_time': datetime.now().isoformat(),
                'revenue_news': revenue_news,
                'earnings_news': earnings_news,
                'market_news': market_news,
                'news_summaries': {},
                'total_news_count': 0,
                'news_sentiment': 'neutral'
            }
            
            # 生成新聞摘要
            if revenue_news and revenue_news.news_results:
                analysis['news_summaries']['revenue'] = await self.generate_news_summary(
                    revenue_news.news_results, 2
                )
                analysis['total_news_count'] += len(revenue_news.news_results)
            
            if earnings_news and earnings_news.news_results:
                analysis['news_summaries']['earnings'] = await self.generate_news_summary(
                    earnings_news.news_results, 2
                )
                analysis['total_news_count'] += len(earnings_news.news_results)
            
            if market_news and market_news.news_results:
                analysis['news_summaries']['market'] = await self.generate_news_summary(
                    market_news.news_results, 2
                )
                analysis['total_news_count'] += len(market_news.news_results)
            
            # 簡單的情感分析（基於關鍵詞）
            positive_keywords = ['成長', '亮眼', '優異', '強勁', '看好', '上漲', '突破']
            negative_keywords = ['下滑', '衰退', '虧損', '下跌', '看壞', '風險']
            
            all_titles = []
            if revenue_news and revenue_news.news_results:
                all_titles.extend([news.title for news in revenue_news.news_results])
            if earnings_news and earnings_news.news_results:
                all_titles.extend([news.title for news in earnings_news.news_results])
            if market_news and market_news.news_results:
                all_titles.extend([news.title for news in market_news.news_results])
            
            positive_count = sum(1 for title in all_titles if any(keyword in title for keyword in positive_keywords))
            negative_count = sum(1 for title in all_titles if any(keyword in title for keyword in negative_keywords))
            
            if positive_count > negative_count:
                analysis['news_sentiment'] = 'positive'
            elif negative_count > positive_count:
                analysis['news_sentiment'] = 'negative'
            else:
                analysis['news_sentiment'] = 'neutral'
            
            return analysis
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 新聞分析時發生錯誤: {e}")
            return {
                'stock_id': stock_id,
                'stock_name': stock_name,
                'error': str(e),
                'analysis_time': datetime.now().isoformat()
            }

