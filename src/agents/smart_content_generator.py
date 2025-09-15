#!/usr/bin/env python3
"""
智能內容生成器
根據熱門話題和新聞搜尋結果生成相關內容
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
import os
from dotenv import load_dotenv

from .multi_level_search_strategy import NewsSearchResult

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class GeneratedContent:
    """生成的內容"""
    title: str
    content: str
    summary: str
    key_points: List[str]
    related_links: List[str]
    confidence_score: float

class SmartContentGenerator:
    """智能內容生成器"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_trending_topic_content(self, topic_title: str, topic_content: str, news_results: List[NewsSearchResult], stock_ids: List[str] = None, post_id: str = None) -> GeneratedContent:
        """根據熱門話題和新聞生成內容 - 每個貼文獨立生成"""
        try:
            post_identifier = f"{post_id or 'unknown'}_{topic_title}_{stock_ids or 'no_stock'}"
            logger.info(f"生成熱門話題內容 (貼文ID: {post_identifier}): {topic_title}")
            
            # 準備新聞摘要 - 只使用當前貼文的新聞
            news_summary = self._prepare_news_summary(news_results)
            logger.info(f"貼文 {post_identifier} 使用 {len(news_results)} 條新聞生成內容")
            
            # 生成內容
            content_prompt = self._create_content_generation_prompt(
                topic_title, topic_content, news_summary, stock_ids
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一個專業的金融內容創作者，擅長根據熱門話題和相關新聞生成有價值的投資分析內容。"},
                    {"role": "user", "content": content_prompt}
                ],
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content
            
            # 解析生成的內容
            return self._parse_generated_content(generated_text, news_results)
            
        except Exception as e:
            logger.error(f"生成內容失敗 (貼文ID: {post_identifier}): {e}")
            return self._generate_fallback_content(topic_title, topic_content, news_results)
    
    def _prepare_news_summary(self, news_results: List[NewsSearchResult]) -> str:
        """準備新聞摘要"""
        if not news_results:
            return "無相關新聞資料"
        
        summary_parts = []
        for i, news in enumerate(news_results[:5], 1):  # 最多取前5條新聞
            summary_parts.append(f"{i}. {news.title}\n   {news.snippet}\n   來源: {news.url}")
        
        return "\n\n".join(summary_parts)
    
    def _create_content_generation_prompt(self, topic_title: str, topic_content: str, news_summary: str, stock_ids: List[str] = None) -> str:
        """創建內容生成提示詞"""
        stock_info = f"相關股票: {', '.join(stock_ids)}" if stock_ids else "無特定股票"
        
        prompt = f"""
請根據以下熱門話題和相關新聞，生成一篇有價值的投資分析內容：

熱門話題:
標題: {topic_title}
內容: {topic_content}
{stock_info}

相關新聞摘要:
{news_summary}

請按照以下格式生成內容：

標題: [一個吸引人的標題，不超過30字]

內容: [主要內容，300-500字]
- 分析熱門話題的背景和影響
- 結合新聞資料提供深度見解
- 提供投資建議或風險提示
- 保持客觀和專業的語調

重點摘要: [3-5個要點，每個不超過50字]

相關連結: [列出2-3個最有價值的新聞連結]

請確保：
1. 內容有深度且具有投資價值
2. 避免過度樂觀或悲觀的語調
3. 提供具體的數據或事實支持
4. 適合投資者閱讀和理解
"""
        return prompt
    
    def _parse_generated_content(self, generated_text: str, news_results: List[NewsSearchResult]) -> GeneratedContent:
        """解析生成的內容"""
        try:
            lines = generated_text.strip().split('\n')
            
            title = ""
            content = ""
            summary = ""
            key_points = []
            related_links = []
            
            current_section = None
            content_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 識別段落標題
                if line.startswith('標題:'):
                    title = line.replace('標題:', '').strip()
                    current_section = 'title'
                elif line.startswith('內容:'):
                    current_section = 'content'
                elif line.startswith('重點摘要:'):
                    current_section = 'summary'
                elif line.startswith('相關連結:'):
                    current_section = 'links'
                else:
                    # 處理內容
                    if current_section == 'content':
                        content_lines.append(line)
                    elif current_section == 'summary':
                        if line.startswith('-') or line.startswith('•'):
                            key_points.append(line[1:].strip())
                    elif current_section == 'links':
                        if line.startswith('-') or line.startswith('•'):
                            link_text = line[1:].strip()
                            # 嘗試從新聞結果中找到對應的連結
                            matching_news = self._find_matching_news(link_text, news_results)
                            if matching_news:
                                related_links.append(matching_news.url)
                            else:
                                related_links.append(link_text)
            
            # 合併內容
            content = '\n'.join(content_lines)
            
            # 生成摘要
            if key_points:
                summary = ' '.join(key_points[:3])  # 取前3個要點作為摘要
            
            # 計算信心分數
            confidence_score = self._calculate_confidence_score(content, news_results)
            
            return GeneratedContent(
                title=title or topic_title,
                content=content or "內容生成失敗",
                summary=summary or "摘要生成失敗",
                key_points=key_points,
                related_links=related_links,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"解析生成內容失敗: {e}")
            return self._generate_fallback_content("", "", news_results)
    
    def _find_matching_news(self, link_text: str, news_results: List[NewsSearchResult]) -> Optional[NewsSearchResult]:
        """找到匹配的新聞"""
        for news in news_results:
            if news.title in link_text or any(word in link_text for word in news.title.split()[:3]):
                return news
        return None
    
    def _calculate_confidence_score(self, content: str, news_results: List[NewsSearchResult]) -> float:
        """計算信心分數"""
        score = 0.5  # 基礎分數
        
        # 根據內容長度調整
        if len(content) > 200:
            score += 0.2
        elif len(content) > 100:
            score += 0.1
        
        # 根據新聞數量調整
        if len(news_results) >= 5:
            score += 0.2
        elif len(news_results) >= 3:
            score += 0.1
        
        # 根據新聞相關性調整
        if news_results:
            avg_relevance = sum(news.relevance_score for news in news_results) / len(news_results)
            score += avg_relevance * 0.1
        
        return min(score, 1.0)
    
    def _generate_fallback_content(self, topic_title: str, topic_content: str, news_results: List[NewsSearchResult]) -> GeneratedContent:
        """生成回退內容"""
        logger.info("使用回退內容生成方法")
        
        # 簡單的內容生成
        title = f"熱門話題分析: {topic_title}"
        
        content_parts = [
            f"近期市場關注的熱門話題「{topic_title}」引發投資人廣泛討論。",
            topic_content or "此話題涉及多個層面的市場變化。",
            "投資人在關注此話題時，建議保持理性分析，綜合考慮基本面、技術面和市場情緒等多重因素。",
            "建議密切關注相關新聞動態，並根據個人風險承受能力做出投資決策。"
        ]
        
        content = ' '.join(content_parts)
        
        key_points = [
            "關注市場熱門話題的發展動向",
            "綜合分析基本面與技術面因素",
            "保持理性投資心態"
        ]
        
        related_links = [news.url for news in news_results[:3]]
        
        return GeneratedContent(
            title=title,
            content=content,
            summary="熱門話題分析與投資建議",
            key_points=key_points,
            related_links=related_links,
            confidence_score=0.6
        )
