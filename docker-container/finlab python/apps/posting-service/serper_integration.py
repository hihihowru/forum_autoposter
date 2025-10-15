"""
Serper API 整合服務
負責搜尋股票相關新聞和漲停原因分析
"""

import os
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SerperNewsService:
    """Serper API 新聞搜尋服務"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
        
        if not self.api_key:
            logger.warning("SERPER_API_KEY 未設定，將使用模擬數據")
    
    def search_stock_news(self, stock_code: str, stock_name: str, limit: int = 5, 
                          search_keywords: Optional[List[Dict[str, Any]]] = None,
                          time_range: str = "d1") -> List[Dict[str, Any]]:
        """搜尋股票相關新聞"""
        try:
            if not self.api_key:
                return self._get_mock_news(stock_code, stock_name)
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            # 構建搜尋查詢 - 使用前端配置的關鍵字
            if search_keywords:
                query_parts = []
                for keyword_config in search_keywords:
                    keyword = keyword_config.get('keyword', '')
                    keyword_type = keyword_config.get('type', 'custom')
                    
                    # 根據關鍵字類型替換變數
                    if keyword_type == 'stock_name':
                        query_parts.append(stock_name)
                    elif keyword_type == 'trigger_keyword':
                        # 這裡可以根據觸發器類型動態選擇關鍵字
                        query_parts.append(keyword)
                    else:  # custom
                        query_parts.append(keyword)
                
                query = ' '.join(query_parts)
                print(f"🔍 使用前端配置搜尋關鍵字: {query}")
            else:
                # 預設搜尋查詢
                query = f"{stock_name} {stock_code} 新聞 最新"
                print(f"🔍 使用預設搜尋關鍵字: {query}")
            
            payload = {
                "q": query,
                "num": limit,
                "type": "search",
                "gl": "tw",  # 台灣地區
                "hl": "zh-tw",  # 繁體中文
                "tbs": self._get_time_range_filter(time_range)  # 時間範圍過濾器
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get('organic', [])
            
            # 處理搜尋結果
            news_items = []
            for result in organic_results:
                news_items.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'date': result.get('date', ''),
                    'source': self._extract_source(result.get('link', ''))
                })
            
            logger.info(f"為 {stock_name}({stock_code}) 找到 {len(news_items)} 則新聞")
            return news_items
            
        except Exception as e:
            logger.error(f"搜尋 {stock_name}({stock_code}) 新聞失敗: {e}")
            return self._get_mock_news(stock_code, stock_name)
    
    def analyze_limit_up_reason(self, stock_code: str, stock_name: str, 
                               search_keywords: Optional[List[Dict[str, Any]]] = None,
                               time_range: str = "d1", trigger_type: str = None) -> Dict[str, Any]:
        """分析漲停原因"""
        try:
            if not self.api_key:
                return self._get_mock_limit_up_analysis(stock_code, stock_name)
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            # 搜尋漲停相關資訊 - 使用前端配置的關鍵字
            if search_keywords:
                query_parts = []
                for keyword_config in search_keywords:
                    keyword = keyword_config.get('keyword', '')
                    keyword_type = keyword_config.get('type', 'custom')
                    
                    if keyword_type == 'stock_name':
                        query_parts.append(stock_name)
                    elif keyword_type == 'trigger_keyword':
                        query_parts.append(keyword)
                    else:  # custom
                        query_parts.append(keyword)
                
                # 根據觸發器類型添加相關關鍵字
                if trigger_type == 'intraday_limit_down' or trigger_type == 'limit_down_after_hours':
                    # 跌停觸發器
                    query_parts.extend(['跌停', '原因', '利空', '消息'])
                    print(f"🔍 使用前端配置分析跌停原因: {' '.join(query_parts)}")
                elif trigger_type == 'intraday_limit_up' or trigger_type == 'limit_up_after_hours':
                    # 漲停觸發器
                    query_parts.extend(['漲停', '原因', '利多', '消息'])
                    print(f"🔍 使用前端配置分析漲停原因: {' '.join(query_parts)}")
                else:
                    # 其他觸發器，使用中性關鍵字
                    query_parts.extend(['表現', '原因', '分析', '消息'])
                    print(f"🔍 使用前端配置分析表現原因: {' '.join(query_parts)}")
                
                query = ' '.join(query_parts)
            else:
                # 預設搜尋查詢
                query = f"{stock_name} {stock_code} 漲停 原因 利多 消息"
                print(f"🔍 使用預設分析關鍵字: {query}")
            
            payload = {
                "q": query,
                "num": 3,
                "type": "search",
                "gl": "tw",
                "hl": "zh-tw",
                "tbs": self._get_time_range_filter(time_range)  # 時間範圍過濾器
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get('organic', [])
            
            # 分析漲停原因
            reasons = []
            key_events = []
            market_sentiment = "neutral"
            
            for result in organic_results:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                
                # 提取關鍵資訊
                if any(keyword in title.lower() or keyword in snippet.lower() 
                      for keyword in ['漲停', '大漲', '飆漲', '利多', '好消息', '財報', '營收']):
                    reasons.append({
                        'title': title,
                        'snippet': snippet,
                        'link': result.get('link', ''),
                        'relevance_score': self._calculate_relevance_score(title, snippet)
                    })
                
                # 提取關鍵事件
                if any(keyword in title.lower() or keyword in snippet.lower()
                      for keyword in ['財報', '營收', '合作', '訂單', '獲利', '成長']):
                    key_events.append({
                        'event': title,
                        'description': snippet,
                        'link': result.get('link', '')
                    })
            
            # 判斷市場情緒
            positive_keywords = ['利多', '好消息', '成長', '獲利', '合作', '訂單']
            negative_keywords = ['利空', '壞消息', '虧損', '下跌', '風險']
            
            all_text = ' '.join([r['title'] + ' ' + r['snippet'] for r in reasons])
            positive_count = sum(1 for keyword in positive_keywords if keyword in all_text.lower())
            negative_count = sum(1 for keyword in negative_keywords if keyword in all_text.lower())
            
            if positive_count > negative_count:
                market_sentiment = "positive"
            elif negative_count > positive_count:
                market_sentiment = "negative"
            
            return {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'limit_up_reasons': reasons,
                'key_events': key_events,
                'market_sentiment': market_sentiment,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_source': 'serper_api'
            }
            
        except Exception as e:
            logger.error(f"分析 {stock_name}({stock_code}) 漲停原因失敗: {e}")
            return self._get_mock_limit_up_analysis(stock_code, stock_name)
    
    def get_comprehensive_stock_analysis(self, stock_code: str, stock_name: str, 
                                        search_keywords: Optional[List[Dict[str, Any]]] = None,
                                        time_range: str = "d1", trigger_type: str = None) -> Dict[str, Any]:
        """獲取股票綜合分析資料"""
        try:
            # 根據觸發器類型調整搜尋關鍵字
            adjusted_keywords = self._adjust_keywords_for_trigger(search_keywords, trigger_type)
            
            # 並行獲取新聞和漲停分析
            news_items = self.search_stock_news(stock_code, stock_name, limit=5, search_keywords=adjusted_keywords, time_range=time_range)
            limit_up_analysis = self.analyze_limit_up_reason(stock_code, stock_name, search_keywords=adjusted_keywords, time_range=time_range, trigger_type=trigger_type)
            
            return {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'news_items': news_items,
                'limit_up_analysis': limit_up_analysis,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_quality': 'high' if self.api_key else 'mock',
                'enable_news_links': True,  # 添加新聞連結配置
                'news_max_links': 5
            }
            
        except Exception as e:
            logger.error(f"獲取 {stock_name}({stock_code}) 綜合分析失敗: {e}")
            return self._get_mock_comprehensive_analysis(stock_code, stock_name)
    
    def _adjust_keywords_for_trigger(self, search_keywords: Optional[List[Dict[str, Any]]], trigger_type: str) -> Optional[List[Dict[str, Any]]]:
        """根據觸發器類型調整搜尋關鍵字"""
        if not search_keywords:
            return search_keywords
        
        # 複製關鍵字列表
        adjusted_keywords = search_keywords.copy()
        
        # 根據觸發器類型調整關鍵字
        if trigger_type == 'intraday_limit_down' or trigger_type == 'limit_down_after_hours':
            # 跌停觸發器：移除漲停相關關鍵字，確保搜尋跌停相關內容
            for keyword_config in adjusted_keywords:
                if keyword_config.get('type') == 'trigger_keyword':
                    keyword = keyword_config.get('keyword', '')
                    if '漲停' in keyword:
                        keyword_config['keyword'] = keyword.replace('漲停', '跌停')
                    elif keyword == '跌停':
                        # 保持跌停關鍵字
                        pass
                    else:
                        # 其他關鍵字保持不變
                        pass
        elif trigger_type == 'intraday_limit_up' or trigger_type == 'limit_up_after_hours':
            # 漲停觸發器：確保搜尋漲停相關內容
            for keyword_config in adjusted_keywords:
                if keyword_config.get('type') == 'trigger_keyword':
                    keyword = keyword_config.get('keyword', '')
                    if '跌停' in keyword:
                        keyword_config['keyword'] = keyword.replace('跌停', '漲停')
                    elif keyword == '漲停':
                        # 保持漲停關鍵字
                        pass
        
        logger.info(f"🔧 根據觸發器類型 {trigger_type} 調整關鍵字: {[kw.get('keyword') for kw in adjusted_keywords]}")
        return adjusted_keywords
    
    def _get_time_range_filter(self, time_range: str) -> str:
        """獲取時間範圍過濾器
        
        Args:
            time_range: 時間範圍選項
                - "h1": 過去1小時
                - "d1": 過去1天 (預設)
                - "d2": 過去2天
                - "w1": 過去1週
                - "m1": 過去1個月
                - "y1": 過去1年
        
        Returns:
            Google 搜尋時間過濾器字串
        """
        time_filters = {
            "h1": "qdr:h",      # 過去1小時
            "d1": "qdr:d",      # 過去1天
            "d2": "qdr:d2",     # 過去2天
            "w1": "qdr:w",      # 過去1週
            "m1": "qdr:m",      # 過去1個月
            "y1": "qdr:y"       # 過去1年
        }
        
        return time_filters.get(time_range, "qdr:d")  # 預設為過去1天
    
    def _extract_source(self, url: str) -> str:
        """從URL提取新聞來源"""
        try:
            if 'money.udn.com' in url:
                return '聯合新聞網'
            elif 'chinatimes.com' in url:
                return '中時新聞網'
            elif 'ltn.com.tw' in url:
                return '自由時報'
            elif 'cnyes.com' in url:
                return '鉅亨網'
            elif 'moneydj.com' in url:
                return 'MoneyDJ'
            elif 'cmoney.tw' in url:
                return 'CMoney'
            else:
                return '其他'
        except:
            return '未知'
    
    def _calculate_relevance_score(self, title: str, snippet: str) -> float:
        """計算相關性分數"""
        score = 0.0
        text = (title + ' ' + snippet).lower()
        
        # 關鍵字權重
        keywords = {
            '漲停': 2.0,
            '大漲': 1.8,
            '飆漲': 1.8,
            '利多': 1.5,
            '好消息': 1.5,
            '財報': 1.2,
            '營收': 1.2,
            '成長': 1.0,
            '獲利': 1.0
        }
        
        for keyword, weight in keywords.items():
            if keyword in text:
                score += weight
        
        return min(score, 10.0)  # 最高10分
    
    def _get_mock_news(self, stock_code: str, stock_name: str) -> List[Dict[str, Any]]:
        """模擬新聞數據"""
        return [
            {
                'title': f'{stock_name}({stock_code}) 最新財報表現亮眼',
                'snippet': f'{stock_name} 發布最新財報，營收成長超預期，獲利能力持續提升，市場看好後市表現。',
                'link': f'https://example.com/news/{stock_code}',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': '模擬新聞'
            },
            {
                'title': f'{stock_name} 技術面突破關鍵阻力位',
                'snippet': f'{stock_name} 技術指標顯示強勢突破，成交量放大，後市可期。',
                'link': f'https://example.com/analysis/{stock_code}',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': '模擬分析'
            }
        ]
    
    def _get_mock_limit_up_analysis(self, stock_code: str, stock_name: str) -> Dict[str, Any]:
        """模擬漲停分析數據"""
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'limit_up_reasons': [
                {
                    'title': f'{stock_name} 財報亮眼帶動股價上漲',
                    'snippet': f'{stock_name} 最新財報表現優異，營收成長超預期，獲利能力持續提升。',
                    'link': f'https://example.com/news/{stock_code}',
                    'relevance_score': 8.5
                }
            ],
            'key_events': [
                {
                    'event': f'{stock_name} 營收成長超預期',
                    'description': f'{stock_name} 最新營收數據顯示強勁成長動能。',
                    'link': f'https://example.com/earnings/{stock_code}'
                }
            ],
            'market_sentiment': 'positive',
            'analysis_timestamp': datetime.now().isoformat(),
            'data_source': 'mock_data'
        }
    
    def _get_mock_comprehensive_analysis(self, stock_code: str, stock_name: str) -> Dict[str, Any]:
        """模擬綜合分析數據"""
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'news_items': self._get_mock_news(stock_code, stock_name),
            'limit_up_analysis': self._get_mock_limit_up_analysis(stock_code, stock_name),
            'analysis_timestamp': datetime.now().isoformat(),
            'data_quality': 'mock'
        }

# 全域實例
serper_service = SerperNewsService()
