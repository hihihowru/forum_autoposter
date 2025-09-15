#!/usr/bin/env python3
"""
熱門話題新聞搜尋服務
整合話題分析、多層次搜尋和內容生成，確保每個貼文都有獨立的搜尋策略
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

from .intelligent_topic_analyzer import IntelligentTopicAnalyzer, KeywordAnalysis
from .multi_level_search_strategy import MultiLevelSearchStrategy, NewsSearchResult
from .smart_content_generator import SmartContentGenerator, GeneratedContent

logger = logging.getLogger(__name__)

@dataclass
class TrendingTopicPost:
    """熱門話題貼文"""
    post_id: str
    topic_title: str
    topic_content: str
    stock_ids: List[str]
    is_topic_only: bool  # 是否為純話題（無股票）
    kol_info: Dict[str, Any]  # KOL 資訊

@dataclass
class PostGenerationResult:
    """貼文生成結果"""
    post_id: str
    topic_title: str
    stock_ids: List[str]
    keyword_analysis: KeywordAnalysis
    news_results: List[NewsSearchResult]
    generated_content: GeneratedContent
    success: bool
    error_message: Optional[str] = None

class TrendingTopicNewsService:
    """熱門話題新聞搜尋服務"""
    
    def __init__(self):
        self.topic_analyzer = IntelligentTopicAnalyzer()
        self.search_strategy = MultiLevelSearchStrategy(self.topic_analyzer)
        self.content_generator = SmartContentGenerator()
        
    async def process_trending_topic_posts(self, posts: List[TrendingTopicPost]) -> List[PostGenerationResult]:
        """處理多個熱門話題貼文 - 每個貼文獨立處理"""
        logger.info(f"開始處理 {len(posts)} 個熱門話題貼文")
        
        results = []
        
        # 並行處理所有貼文，但每個貼文內部是獨立的
        tasks = []
        for post in posts:
            task = self._process_single_post(post)
            tasks.append(task)
        
        # 等待所有貼文處理完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理異常結果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"貼文 {posts[i].post_id} 處理失敗: {result}")
                processed_results.append(PostGenerationResult(
                    post_id=posts[i].post_id,
                    topic_title=posts[i].topic_title,
                    stock_ids=posts[i].stock_ids,
                    keyword_analysis=None,
                    news_results=[],
                    generated_content=None,
                    success=False,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        logger.info(f"完成處理 {len(processed_results)} 個貼文")
        return processed_results
    
    async def _process_single_post(self, post: TrendingTopicPost) -> PostGenerationResult:
        """處理單個貼文 - 完全獨立"""
        try:
            logger.info(f"開始處理貼文 {post.post_id}: {post.topic_title}")
            
            # 步驟1: 分析話題關鍵字 - 每個貼文獨立分析
            keyword_analysis = self.topic_analyzer.analyze_topic(
                post.topic_title, 
                post.topic_content, 
                post.stock_ids
            )
            logger.info(f"貼文 {post.post_id} 關鍵字分析完成: {len(keyword_analysis.search_queries)} 個搜尋查詢")
            
            # 步驟2: 搜尋相關新聞 - 每個貼文獨立搜尋
            news_results = await self.search_strategy.search_trending_topic_news(
                post.topic_title,
                post.topic_content,
                post.stock_ids,
                post.post_id
            )
            logger.info(f"貼文 {post.post_id} 找到 {len(news_results)} 條新聞")
            
            # 步驟3: 生成內容 - 每個貼文獨立生成
            generated_content = await self.content_generator.generate_trending_topic_content(
                post.topic_title,
                post.topic_content,
                news_results,
                post.stock_ids,
                post.post_id
            )
            logger.info(f"貼文 {post.post_id} 內容生成完成")
            
            return PostGenerationResult(
                post_id=post.post_id,
                topic_title=post.topic_title,
                stock_ids=post.stock_ids,
                keyword_analysis=keyword_analysis,
                news_results=news_results,
                generated_content=generated_content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"處理貼文 {post.post_id} 失敗: {e}")
            return PostGenerationResult(
                post_id=post.post_id,
                topic_title=post.topic_title,
                stock_ids=post.stock_ids,
                keyword_analysis=None,
                news_results=[],
                generated_content=None,
                success=False,
                error_message=str(e)
            )
    
    async def process_single_trending_topic(self, topic_title: str, topic_content: str, stock_ids: List[str] = None, post_id: str = None) -> PostGenerationResult:
        """處理單個熱門話題 - 用於測試或單獨處理"""
        post = TrendingTopicPost(
            post_id=post_id or f"single_{topic_title}",
            topic_title=topic_title,
            topic_content=topic_content,
            stock_ids=stock_ids or [],
            is_topic_only=not bool(stock_ids),
            kol_info={}
        )
        
        return await self._process_single_post(post)
