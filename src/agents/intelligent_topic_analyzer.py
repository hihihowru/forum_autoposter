#!/usr/bin/env python3
"""
智能話題分析器
分析熱門話題並提取關鍵字，用於新聞搜尋
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class KeywordAnalysis:
    """關鍵字分析結果"""
    primary_keywords: List[str]  # 主要關鍵字
    secondary_keywords: List[str]  # 次要關鍵字
    industry_keywords: List[str]  # 產業關鍵字
    sentiment_keywords: List[str]  # 情感關鍵字
    search_queries: List[str]  # 搜尋查詢建議

class IntelligentTopicAnalyzer:
    """智能話題分析器"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def analyze_topic(self, topic_title: str, topic_content: str = "", stock_ids: List[str] = None) -> KeywordAnalysis:
        """分析熱門話題並提取關鍵字"""
        try:
            logger.info(f"分析話題: {topic_title}")
            
            # 使用 LLM 分析話題
            analysis_prompt = self._create_analysis_prompt(topic_title, topic_content, stock_ids)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一個專業的金融話題分析師，擅長從熱門話題中提取關鍵字並生成搜尋查詢。"},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # 解析 LLM 回應
            return self._parse_analysis_response(analysis_text)
            
        except Exception as e:
            logger.error(f"話題分析失敗: {e}")
            # 回退到簡單的關鍵字提取
            return self._fallback_keyword_extraction(topic_title, topic_content, stock_ids)
    
    def _create_analysis_prompt(self, topic_title: str, topic_content: str, stock_ids: List[str]) -> str:
        """創建分析提示詞"""
        stock_info = f"相關股票: {', '.join(stock_ids)}" if stock_ids else "無特定股票"
        
        prompt = f"""
請分析以下熱門話題，並提取關鍵字用於新聞搜尋：

話題標題: {topic_title}
話題內容: {topic_content}
{stock_info}

請按照以下格式提供分析結果：

主要關鍵字 (3-5個): 與話題核心概念相關的關鍵字
次要關鍵字 (5-8個): 相關但較為廣泛的關鍵字
產業關鍵字 (3-5個): 相關產業或領域的關鍵字
情感關鍵字 (2-4個): 表達市場情緒的關鍵字
搜尋查詢建議 (3-5個): 用於新聞搜尋的完整查詢語句

請確保：
1. 關鍵字簡潔明確
2. 搜尋查詢包含多個關鍵字組合
3. 考慮不同的搜尋角度（基本面、技術面、消息面等）
4. 避免使用過於狹窄的關鍵字
"""
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str) -> KeywordAnalysis:
        """解析 LLM 分析回應"""
        try:
            lines = analysis_text.strip().split('\n')
            
            primary_keywords = []
            secondary_keywords = []
            industry_keywords = []
            sentiment_keywords = []
            search_queries = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 識別段落標題
                if '主要關鍵字' in line:
                    current_section = 'primary'
                elif '次要關鍵字' in line:
                    current_section = 'secondary'
                elif '產業關鍵字' in line:
                    current_section = 'industry'
                elif '情感關鍵字' in line:
                    current_section = 'sentiment'
                elif '搜尋查詢建議' in line:
                    current_section = 'search'
                else:
                    # 提取關鍵字
                    if current_section == 'primary':
                        keywords = self._extract_keywords_from_line(line)
                        primary_keywords.extend(keywords)
                    elif current_section == 'secondary':
                        keywords = self._extract_keywords_from_line(line)
                        secondary_keywords.extend(keywords)
                    elif current_section == 'industry':
                        keywords = self._extract_keywords_from_line(line)
                        industry_keywords.extend(keywords)
                    elif current_section == 'sentiment':
                        keywords = self._extract_keywords_from_line(line)
                        sentiment_keywords.extend(keywords)
                    elif current_section == 'search':
                        if line and not line.startswith(':'):
                            search_queries.append(line.strip())
            
            return KeywordAnalysis(
                primary_keywords=primary_keywords[:5],
                secondary_keywords=secondary_keywords[:8],
                industry_keywords=industry_keywords[:5],
                sentiment_keywords=sentiment_keywords[:4],
                search_queries=search_queries[:5]
            )
            
        except Exception as e:
            logger.error(f"解析分析回應失敗: {e}")
            return self._fallback_keyword_extraction("", "", [])
    
    def _extract_keywords_from_line(self, line: str) -> List[str]:
        """從行中提取關鍵字"""
        # 移除標題部分
        if ':' in line:
            line = line.split(':', 1)[1]
        
        # 分割關鍵字
        keywords = []
        for keyword in line.split(','):
            keyword = keyword.strip()
            if keyword and len(keyword) > 1:
                keywords.append(keyword)
        
        return keywords
    
    def _fallback_keyword_extraction(self, topic_title: str, topic_content: str, stock_ids: List[str]) -> KeywordAnalysis:
        """回退的關鍵字提取方法"""
        logger.info("使用回退關鍵字提取方法")
        
        # 從標題中提取關鍵字
        title_keywords = self._extract_keywords_from_text(topic_title)
        
        # 從內容中提取關鍵字
        content_keywords = self._extract_keywords_from_text(topic_content)
        
        # 合併關鍵字
        all_keywords = list(set(title_keywords + content_keywords))
        
        # 生成搜尋查詢
        search_queries = []
        if stock_ids:
            for stock_id in stock_ids[:2]:  # 最多取前2個股票
                search_queries.append(f"{stock_id} {topic_title}")
        
        # 添加一般性搜尋查詢
        search_queries.append(topic_title)
        if len(all_keywords) > 2:
            search_queries.append(f"{all_keywords[0]} {all_keywords[1]}")
        
        return KeywordAnalysis(
            primary_keywords=all_keywords[:5],
            secondary_keywords=all_keywords[5:13],
            industry_keywords=[],
            sentiment_keywords=[],
            search_queries=search_queries[:5]
        )
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """從文本中提取關鍵字"""
        if not text:
            return []
        
        # 移除標點符號和特殊字符
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 分割成詞語
        words = text.split()
        
        # 過濾短詞和常見詞
        stop_words = {'的', '是', '在', '有', '和', '與', '或', '但', '然而', '因此', '所以', '因為', '如果', '當', '時', '後', '前', '上', '下', '中', '內', '外', '大', '小', '多', '少', '好', '壞', '新', '舊', '高', '低', '強', '弱', '快', '慢', '長', '短', '深', '淺', '厚', '薄', '寬', '窄', '粗', '細', '直', '彎', '平', '斜', '正', '反', '左', '右', '東', '西', '南', '北', '前', '後', '上', '下', '中', '內', '外', '大', '小', '多', '少', '好', '壞', '新', '舊', '高', '低', '強', '弱', '快', '慢', '長', '短', '深', '淺', '厚', '薄', '寬', '窄', '粗', '細', '直', '彎', '平', '斜', '正', '反', '左', '右', '東', '西', '南', '北'}
        
        keywords = []
        for word in words:
            if len(word) > 1 and word not in stop_words:
                keywords.append(word)
        
        return keywords[:10]  # 最多取10個關鍵字
