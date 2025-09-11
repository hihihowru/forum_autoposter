"""
GPT內容生成器
使用OpenAI GPT模型生成高質量股票分析內容
"""

import os
import openai
from typing import Dict, List, Any, Optional
import json
import logging
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('../../../../.env')

logger = logging.getLogger(__name__)

class GPTContentGenerator:
    """GPT內容生成器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        # 重新載入環境變數以確保API Key正確載入
        load_dotenv('../../../../.env')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if self.api_key:
            openai.api_key = self.api_key
            logger.info(f"GPT內容生成器初始化完成，使用模型: {self.model}")
        else:
            logger.warning("OPENAI_API_KEY 未設定，將使用模板生成")
    
    def generate_stock_analysis(self, 
                             stock_id: str, 
                             stock_name: str, 
                             kol_persona: str,
                             serper_analysis: Dict[str, Any],
                             data_sources: List[str],
                             content_length: str = "medium",
                             max_words: int = 200) -> Dict[str, Any]:
        """使用GPT生成股票分析內容"""
        
        try:
            if not self.api_key:
                return self._fallback_generation(stock_id, stock_name, kol_persona)
            
            # 優先使用新聞分析Agent
            news_items = serper_analysis.get('news_items', [])
            if news_items:
                logger.info(f"使用新聞分析Agent分析 {len(news_items)} 則新聞")
                from news_analysis_agent import news_analysis_agent
                return news_analysis_agent.analyze_stock_news(
                    stock_id, stock_name, news_items, kol_persona
                )
            
            # 如果沒有新聞，使用基本GPT分析
            prompt = self._build_analysis_prompt(
                stock_id, stock_name, kol_persona, serper_analysis, data_sources, content_length, max_words
            )
            
            # 調用GPT API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位專業的股票分析師，擅長從多個角度分析股票漲停原因，並提供平衡的投資建議。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # 解析GPT回應
            return self._parse_gpt_response(content, stock_id, stock_name)
            
        except Exception as e:
            logger.error(f"GPT內容生成失敗: {e}")
            return self._fallback_generation(stock_id, stock_name, kol_persona)
    
    def _build_analysis_prompt(self, 
                              stock_id: str, 
                              stock_name: str, 
                              kol_persona: str,
                              serper_analysis: Dict[str, Any],
                              data_sources: List[str],
                              content_length: str = "medium",
                              max_words: int = 200) -> str:
        """構建分析prompt"""
        
        # 提取新聞資訊
        news_items = serper_analysis.get('news_items', [])
        limit_up_analysis = serper_analysis.get('limit_up_analysis', {})
        limit_up_reasons = limit_up_analysis.get('limit_up_reasons', [])
        key_events = limit_up_analysis.get('key_events', [])
        market_sentiment = limit_up_analysis.get('market_sentiment', 'neutral')
        
        # 構建新聞摘要
        news_summary = ""
        if news_items:
            news_summary = "相關新聞資訊：\n"
            for i, news in enumerate(news_items[:5], 1):
                news_summary += f"{i}. {news.get('title', '')}\n"
                news_summary += f"   {news.get('snippet', '')}\n\n"
        
        # 構建漲停原因
        reasons_summary = ""
        if limit_up_reasons:
            reasons_summary = "漲停原因分析：\n"
            for i, reason in enumerate(limit_up_reasons[:3], 1):
                reasons_summary += f"{i}. {reason.get('title', '')}\n"
                reasons_summary += f"   {reason.get('snippet', '')}\n\n"
        
        # 構建關鍵事件
        events_summary = ""
        if key_events:
            events_summary = "關鍵事件：\n"
            for i, event in enumerate(key_events[:3], 1):
                events_summary += f"{i}. {event.get('event', '')}\n"
                events_summary += f"   {event.get('description', '')}\n\n"
        
        # 根據KOL人設調整分析重點
        persona_instruction = self._get_persona_instruction(kol_persona)
        
        prompt = f"""
請分析 {stock_name}({stock_id}) 的漲停原因，並生成一篇專業的股票分析文章。

{persona_instruction}

{news_summary}
{reasons_summary}
{events_summary}

市場情緒：{market_sentiment}
使用的數據源：{', '.join(data_sources)}

請按照以下結構生成分析：

1. 標題：生成一個吸引人的標題
2. 漲停原因深度分析：從多個角度分析（題材面、基本面、技術面、籌碼面）
3. 技術指標分析：基於技術數據的分析
4. 操作建議：具體的投資建議
5. 風險提醒：平衡的風險分析

要求：
- 內容要有條理，邏輯清晰
- 提供具體的數據和事實支撐
- 給出平衡的觀點，包含風險提醒
- 語言專業但易懂
- 避免重複和贅述
- 長度控制在{max_words}字，確保內容充實完整
- 必須達到最低{max_words}字要求

請直接輸出分析內容，不要包含額外的說明文字。
"""
        
        return prompt
    
    def _get_persona_instruction(self, kol_persona: str) -> str:
        """根據KOL人設獲取分析指令"""
        
        instructions = {
            'technical': """
你是一位技術分析專家，擅長從技術指標、圖表形態、成交量等角度分析股票。
分析重點：
- 技術指標信號（MA、RSI、MACD等）
- 圖表形態和突破點
- 成交量變化
- 技術面支撐和阻力位
""",
            'fundamental': """
你是一位基本面分析專家，專注於公司財務狀況、產業前景、競爭優勢等基本面因素。
分析重點：
- 財務數據分析（營收、獲利、負債等）
- 產業趨勢和競爭地位
- 公司治理和經營策略
- 估值合理性
""",
            'news_driven': """
你是一位市場情報專家，善於從新聞事件、政策變化、市場情緒等角度分析股票。
分析重點：
- 新聞事件影響
- 政策利多利空
- 市場情緒變化
- 投資人心理
""",
            'mixed': """
你是一位綜合分析專家，能夠從多個角度全面分析股票。
分析重點：
- 技術面、基本面、消息面綜合分析
- 多維度風險評估
- 平衡的投資觀點
- 長短期投資策略
"""
        }
        
        return instructions.get(kol_persona, instructions['mixed'])
    
    def _parse_gpt_response(self, content: str, stock_id: str, stock_name: str) -> Dict[str, Any]:
        """解析GPT回應"""
        
        # 簡單的內容分割
        lines = content.split('\n')
        title = ""
        main_content = content
        
        # 提取標題
        for line in lines:
            if line.strip() and not line.startswith(' '):
                title = line.strip()
                break
        
        # 如果沒有找到標題，使用預設
        if not title:
            title = f"{stock_name}({stock_id}) 深度分析"
        
        return {
            "title": title,
            "content": main_content,
            "content_md": main_content,
            "commodity_tags": [{"type": "Stock", "key": stock_id, "bullOrBear": 0}],
            "community_topic": None,
            "generation_method": "gpt",
            "model_used": self.model
        }
    
    def _fallback_generation(self, stock_id: str, stock_name: str, kol_persona: str) -> Dict[str, Any]:
        """回退到模板生成"""
        from improved_content_generator import generate_improved_kol_content
        
        return generate_improved_kol_content(
            stock_id, stock_name, kol_persona, 
            "chart_analysis", "active_traders", 
            {}, []
        )

# 全域實例
gpt_generator = GPTContentGenerator()
