"""
標籤增強服務
用於在發文前自動添加股票標籤和話題標籤，提高內容曝光度
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.services.classification.topic_classifier import TopicClassifier
from src.clients.cmoney.cmoney_client import ArticleData

logger = logging.getLogger(__name__)

@dataclass
class CommodityTag:
    """商品標籤結構"""
    type: str  # "Stock", "Index", "Currency" 等
    key: str   # 股票代碼、指數代碼等
    bullOrBear: int  # 0=中性，1=看多，-1=看空

@dataclass
class CommunityTopic:
    """社區話題結構"""
    id: str  # 話題ID

class TagEnhancer:
    """標籤增強器"""
    
    def __init__(self, topic_classifier: Optional[TopicClassifier] = None):
        """
        初始化標籤增強器
        
        Args:
            topic_classifier: 話題分類器實例
        """
        self.topic_classifier = topic_classifier
        
        # 股票代碼正則表達式
        self.stock_pattern = re.compile(r'(\d{4,5})|([A-Z]{2,4})')
        
        # 常見股票名稱映射
        from ...utils.stock_mapping import STOCK_NAME_TO_CODE
        self.stock_name_mapping = STOCK_NAME_TO_CODE
        
        logger.info("標籤增強器初始化完成")
    
    def enhance_article_tags(self, article: ArticleData, topic_id: str = "", 
                           topic_title: str = "", topic_content: str = "") -> ArticleData:
        """
        增強文章標籤
        
        Args:
            article: 原始文章數據
            topic_id: 話題ID
            topic_title: 話題標題
            topic_content: 話題內容
            
        Returns:
            增強標籤後的文章數據
        """
        try:
            # 1. 生成 commodityTags
            commodity_tags = self._generate_commodity_tags(article.title, article.text, topic_title, topic_content)
            
            # 2. 生成 communityTopic
            community_topic = None
            if topic_id:
                community_topic = {"id": topic_id}
            
            # 3. 更新文章數據
            enhanced_article = ArticleData(
                title=article.title,
                text=article.text,
                communityTopic=community_topic,
                commodity_tags=commodity_tags
            )
            
            logger.info(f"標籤增強完成: commodity_tags={len(commodity_tags)}, community_topic={community_topic}")
            return enhanced_article
            
        except Exception as e:
            logger.error(f"標籤增強失敗: {e}")
            return article
    
    def _generate_commodity_tags(self, title: str, content: str, topic_title: str = "", topic_content: str = "") -> List[Dict[str, Any]]:
        """生成商品標籤"""
        commodity_tags = []
        
        # 合併所有文本進行分析
        all_text = f"{title} {content} {topic_title} {topic_content}"
        
        # 1. 提取股票標籤
        stock_codes = self._extract_stock_codes(all_text)
        
        for stock_code in stock_codes:
            # 分析多空傾向
            bull_or_bear = self._analyze_sentiment(all_text, stock_code)
            
            commodity_tag = {
                "type": "Stock",
                "key": stock_code,
                "bullOrBear": bull_or_bear
            }
            commodity_tags.append(commodity_tag)
        
        # 2. 提取指數標籤（如果有）
        index_tags = self._extract_index_tags(all_text)
        commodity_tags.extend(index_tags)
        
        # 3. 限制標籤數量，避免過多
        return commodity_tags[:5]
    
    def _extract_stock_codes(self, text: str) -> List[str]:
        """提取股票代碼"""
        stock_codes = set()
        
        # 1. 提取數字股票代碼
        stock_codes_matches = self.stock_pattern.findall(text)
        for match in stock_codes_matches:
            if isinstance(match, tuple):
                code = match[0] or match[1]
            else:
                code = match
            if code and len(code) >= 4 and code.isdigit():
                stock_codes.add(code)
        
        # 2. 提取股票名稱對應的代碼
        for name, code in self.stock_name_mapping.items():
            if name in text:
                stock_codes.add(code)
        
        return list(stock_codes)
    
    def _extract_index_tags(self, text: str) -> List[Dict[str, Any]]:
        """提取指數標籤"""
        index_tags = []
        
        # 常見指數關鍵詞
        index_keywords = {
            '台股': 'TWII',
            '加權': 'TWII',
            '電子': 'TEL',
            '金融': 'TFI',
            '櫃買': 'TPEX',
            '道瓊': 'DJI',
            '納斯達克': 'IXIC',
            '標普500': 'SPX',
            '費城半導體': 'SOX'
        }
        
        for keyword, index_code in index_keywords.items():
            if keyword in text:
                # 分析指數的多空傾向
                bull_or_bear = self._analyze_sentiment(text, keyword)
                
                index_tag = {
                    "type": "Index",
                    "key": index_code,
                    "bullOrBear": bull_or_bear
                }
                index_tags.append(index_tag)
        
        return index_tags
    
    def _analyze_sentiment(self, text: str, target: str) -> int:
        """
        分析多空傾向
        
        Returns:
            0: 中性, 1: 看多, -1: 看空
        """
        # 看多關鍵詞
        bullish_keywords = [
            '看多', '看好', '樂觀', '上漲', '突破', '強勢', '買入', '買進',
            '利多', '好消息', '成長', '擴張', '獲利', '營收成長', '業績亮眼',
            '技術面強', '基本面佳', '趨勢向上', '動能強', '量能放大'
        ]
        
        # 看空關鍵詞
        bearish_keywords = [
            '看空', '看壞', '悲觀', '下跌', '跌破', '弱勢', '賣出', '賣出',
            '利空', '壞消息', '衰退', '萎縮', '虧損', '營收下滑', '業績不佳',
            '技術面弱', '基本面差', '趨勢向下', '動能弱', '量能萎縮'
        ]
        
        # 計算多空傾向
        bullish_count = sum(1 for keyword in bullish_keywords if keyword in text)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in text)
        
        if bullish_count > bearish_count:
            return 1  # 看多
        elif bearish_count > bullish_count:
            return -1  # 看空
        else:
            return 0  # 中性
    
    def generate_hashtags_for_content(self, content: str, max_tags: int = 5) -> List[str]:
        """為內容生成標籤（用於內容中）"""
        hashtags = []
        
        # 提取關鍵詞作為標籤
        keywords = self._extract_keywords(content)
        
        for keyword in keywords[:max_tags]:
            hashtag = f"#{keyword}"
            hashtags.append(hashtag)
        
        return hashtags
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取關鍵詞"""
        # 移除標點符號
        import string
        content_clean = content.translate(str.maketrans('', '', string.punctuation))
        
        # 按空格分割
        words = content_clean.split()
        
        # 過濾短詞和常見詞
        stop_words = {'的', '是', '在', '有', '和', '與', '或', '但', '而', '如果', '因為', '所以'}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:10]  # 返回前10個關鍵詞
