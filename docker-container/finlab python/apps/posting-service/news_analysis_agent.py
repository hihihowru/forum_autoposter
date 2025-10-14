"""
新聞分析Agent
類似ChatGPT的多維度新聞分析和總結系統
"""

import os
import openai
import requests
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('../../../../.env')

logger = logging.getLogger(__name__)

class NewsAnalysisAgent:
    """新聞分析Agent - 多維度分析新聞並提供建設性見解"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        # 重新載入環境變數以確保API Key正確載入
        load_dotenv('../../../../.env')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        print(f"🔑 新聞分析Agent初始化: API Key={'有' if self.api_key else '無'}, 模型={self.model}")
        
        if self.api_key:
            # 清除可能的代理設置
            for key in list(os.environ.keys()):
                if 'proxy' in key.lower():
                    del os.environ[key]
            
            openai.api_key = self.api_key
            logger.info(f"新聞分析Agent初始化完成，使用模型: {self.model}")
        else:
            logger.warning("OPENAI_API_KEY 未設定，將使用基本分析")
    
    def analyze_stock_news(self, 
                          stock_code: str, 
                          stock_name: str, 
                          news_items: List[Dict[str, Any]],
                          kol_persona: str = "mixed",
                          content_length: str = "medium",
                          max_words: int = 200) -> Dict[str, Any]:
        """多維度分析股票新聞"""
        
        try:
            if not self.api_key or not news_items:
                print(f"⚠️ 新聞分析Agent回退到基本分析: api_key={'有' if self.api_key else '無'}, news_items={len(news_items) if news_items else 0}")
                return self._basic_news_analysis(stock_code, stock_name, news_items)
            
            print(f"🤖 新聞分析Agent開始GPT分析: {stock_name}({stock_code}), 字數要求: {max_words}字")
            
            # 構建新聞分析prompt
            prompt = self._build_news_analysis_prompt(
                stock_code, stock_name, news_items, kol_persona, content_length, max_words
            )
            
            # 清除可能的代理設置
            import os
            for key in list(os.environ.keys()):
                if 'proxy' in key.lower():
                    del os.environ[key]
            
            print(f"🔍 準備調用GPT API，API Key: {'有' if self.api_key else '無'}")
            print(f"🔍 環境變量檢查: {[k for k in os.environ.keys() if 'proxy' in k.lower()]}")
            
            # 調用GPT API進行深度分析
            try:
                # 使用 requests 直接調用 OpenAI API
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": """你是一位專業的股票分析師，擅長從多個角度分析新聞事件對股票的影響。
                            
你的分析特點：
1. 多維度分析：從題材面、基本面、技術面、籌碼面等角度分析
2. 新聞整合：將多個新聞來源的資訊整合成有條理的見解
3. 建設性觀點：提供具體的投資建議和風險提醒
4. 平衡觀點：既分析利多也指出風險
5. 數據支撐：基於具體的新聞內容給出分析"""
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_completion_tokens": 2000,
                    "temperature": 1.0
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code != 200:
                    raise Exception(f"OpenAI API 錯誤: {response.status_code} - {response.text}")
                
                response_data = response.json()
                analysis_content = response_data["choices"][0]["message"]["content"]
                
            except Exception as e:
                print(f"🔍 GPT API 調用詳細錯誤: {type(e).__name__}: {str(e)}")
                raise e
            
            print(f"✅ GPT分析完成，內容長度: {len(analysis_content)} 字")
            
            # 解析分析結果
            return self._parse_news_analysis(analysis_content, stock_code, stock_name, news_items)
            
        except Exception as e:
            print(f"❌ 新聞分析Agent GPT調用失敗: {e}")
            logger.error(f"新聞分析失敗: {e}")
            return self._basic_news_analysis(stock_code, stock_name, news_items)
    
    def _build_news_analysis_prompt(self, 
                                   stock_code: str, 
                                   stock_name: str, 
                                   news_items: List[Dict[str, Any]],
                                   kol_persona: str,
                                   content_length: str = "medium",
                                   max_words: int = 200) -> str:
        """構建新聞分析prompt"""
        
        # 整理新聞資訊
        news_summary = f"關於 {stock_name}({stock_code}) 的最新新聞：\n\n"
        
        for i, news in enumerate(news_items[:8], 1):  # 最多分析8則新聞
            news_summary += f"{i}. {news.get('source', '未知來源')}\n"
            news_summary += f"   標題：{news.get('title', '')}\n"
            news_summary += f"   內容：{news.get('snippet', '')}\n"
            if news.get('link'):
                news_summary += f"   連結：{news.get('link', '')}\n"
            if news.get('date'):
                news_summary += f"   時間：{news.get('date', '')}\n"
            news_summary += "\n"
        
        # 根據KOL人設調整分析重點
        analysis_focus = self._get_analysis_focus(kol_persona)
        
        prompt = f"""
請基於以下新聞資訊，對 {stock_name}({stock_code}) 進行深度分析：

{news_summary}

{analysis_focus}

請按照以下結構提供精華分析（不要包含標題，直接開始分析內容）：

題材面
- 簡要分析主要題材和影響

基本面  
- 關鍵財務數據和營運狀況

技術面
- 重要技術指標和價位

籌碼面
- 法人動向和資金流向

操作建議
- 進場點位和停損停利
- 風險提醒

要求：
1. 基於實際新聞內容，簡潔有力
2. 提供具體數據支撐
3. 語言專業易懂，純文字格式
4. 長度控制在{max_words}字，確保內容充實完整
5. 重點突出，避免冗長
6. 不要使用Markdown格式（##、**等）
7. 不要使用emoji表情符號
8. 必須達到最低{max_words}字要求，內容要詳細完整
9. 不要生成任何標題，直接開始分析內容

請直接輸出分析內容，不要包含額外的說明文字。
"""
        
        return prompt
    
    def _get_analysis_focus(self, kol_persona: str) -> str:
        """根據KOL人設獲取分析重點"""
        
        focus_map = {
            'technical': """
分析重點：技術分析為主
- 重點分析技術指標和圖表形態
- 關注成交量變化和突破點
- 提供具體的技術操作建議
- 分析支撐阻力位和趨勢線
""",
            'fundamental': """
分析重點：基本面分析為主
- 重點分析財務數據和營運狀況
- 關注產業趨勢和競爭地位
- 提供長線投資建議
- 分析估值合理性和成長性
""",
            'news_driven': """
分析重點：消息面分析為主
- 重點分析新聞事件影響
- 關注政策變化和市場情緒
- 提供短線操作建議
- 分析投資人心理和資金流向
""",
            'mixed': """
分析重點：綜合分析
- 技術面、基本面、消息面綜合分析
- 多維度風險評估
- 提供平衡的投資觀點
- 長短期投資策略並重
"""
        }
        
        return focus_map.get(kol_persona, focus_map['mixed'])
    
    def _parse_news_analysis(self, 
                            analysis_content: str, 
                            stock_code: str, 
                            stock_name: str,
                            news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析新聞分析結果"""
        
        # 生成精簡標題
        title = f"{stock_name} 分析"
        
        return {
            "title": title,
            "content": analysis_content,
            "content_md": analysis_content,
            "commodity_tags": [{"type": "Stock", "key": stock_code, "bullOrBear": 0}],
            "community_topic": None,
            "generation_method": "news_analysis_agent",
            "model_used": self.model,
            "news_sources_count": len(news_items),
            "analysis_timestamp": datetime.now().isoformat(),
            "news_items": news_items
        }
    
    def _basic_news_analysis(self, 
                            stock_code: str, 
                            stock_name: str, 
                            news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基本新聞分析（回退方案）"""
        
        # 簡單的新聞摘要
        news_summary = f"【新聞摘要】{stock_name}({stock_code})\n\n"
        
        if news_items:
            news_summary += "相關新聞：\n"
            for i, news in enumerate(news_items[:3], 1):
                news_summary += f"{i}. {news.get('title', '')}\n"
                news_summary += f"   {news.get('snippet', '')[:100]}...\n\n"
        else:
            news_summary += "暫無相關新聞資訊\n\n"
        
        news_summary += "⚠️ 投資有風險，請謹慎評估"
        
        return {
            "title": f"{stock_name}({stock_code}) 新聞分析",
            "content": news_summary,
            "content_md": news_summary,
            "commodity_tags": [{"type": "Stock", "key": stock_code, "bullOrBear": 0}],
            "community_topic": None,
            "generation_method": "basic_analysis",
            "model_used": "template",
            "news_sources_count": len(news_items),
            "analysis_timestamp": datetime.now().isoformat(),
            "news_items": news_items
        }

# 全域實例
news_analysis_agent = NewsAnalysisAgent()
