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

漲停原因分析

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
- 內容要有條理，邏輯清晰
- 提供具體的數據和事實支撐
- 給出平衡的觀點，包含風險提醒
- 語言專業但易懂
- 避免重複和贅述
- 長度控制在{max_words}字，確保內容充實完整
- 必須達到最低{max_words}字要求
- 不要使用Markdown格式（##、**等）
- 不要使用emoji表情符號

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
            title = f"{stock_name} 分析"
        
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
        logger.warning(f"使用備用模板生成內容: {stock_name}({stock_id})")

        # 根據 KOL 角色選擇不同的分析風格
        if kol_persona == "technical":
            title = f"{stock_name}({stock_id}) 技術面分析與操作策略"
            content = f"""【{stock_name}({stock_id}) 技術面深度分析】

一、技術指標分析
從技術面來看，{stock_name}目前呈現值得關注的訊號。RSI指標顯示股價動能變化，MACD指標則反映短中期趨勢走向。成交量方面，近期量能有所放大，顯示市場關注度提升。

二、關鍵價位觀察
建議關注支撐與壓力區間，若能站穩關鍵價位，後續可能有進一步表現空間。操作上建議設定合理的停損停利點。

三、操作建議
• 短線：觀察突破後的量價配合
• 中線：留意趨勢是否延續
• 風控：嚴格執行停損紀律

⚠️ 以上分析僅供參考，投資需謹慎評估風險。

#技術分析 #操作策略 #{stock_name}"""

        elif kol_persona == "fundamental":
            title = f"{stock_name}({stock_id}) 基本面分析與投資展望"
            content = f"""【{stock_name}({stock_id}) 基本面觀察】

一、產業地位
{stock_name}在產業中具有重要地位，營運狀況值得持續追蹤。投資人應關注公司財報數據、營收表現，以及產業整體景氣變化。

二、財務表現
建議關注公司的獲利能力、成長性，以及現金流狀況。同時留意產業競爭態勢與公司護城河。

三、投資建議
• 長期投資者：評估基本面是否支撐股價
• 價值投資：關注本益比與殖利率
• 風險控管：分散投資降低單一持股風險

⚠️ 投資前請詳閱公司財報，審慎評估。

#基本面分析 #投資展望 #{stock_name}"""

        else:  # 其他角色使用通用模板
            title = f"{stock_name}({stock_id}) 市場觀察與交易想法"
            content = f"""【{stock_name}({stock_id}) 市場觀察】

一、近期走勢
{stock_name}近期走勢值得關注，市場波動提供不同的交易機會。投資人可根據自身風險偏好，選擇適合的操作策略。

二、交易想法
• 趨勢跟隨：順勢而為，不逆勢操作
• 風險管理：控制倉位，設定停損
• 情緒管理：避免追高殺低

三、注意事項
請留意整體市場系統性風險，以及個股基本面變化。建議設定合理的停損停利點，嚴格控制持股比重。

⚠️ 投資有風險，請謹慎評估。

#市場觀察 #交易策略 #{stock_name}"""

        return {
            "title": title,
            "content": content,
            "content_md": content,
            "commodity_tags": [{"type": "Stock", "key": stock_id, "bullOrBear": 0}],
            "community_topic": None,
            "generation_method": "template_fallback",
            "model_used": "template"
        }

# 全域實例
gpt_generator = GPTContentGenerator()
