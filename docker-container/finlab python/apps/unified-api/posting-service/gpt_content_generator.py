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
import re

# 載入環境變數
load_dotenv('../../../../.env')

logger = logging.getLogger(__name__)

class GPTContentGenerator:
    """GPT內容生成器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        # 重新載入環境變數以確保API Key正確載入
        load_dotenv('../../../../.env')
        # 🔥 FIX: Strip whitespace and newlines from API key (Railway env var issue)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.api_key = self.api_key.strip()
        self.model = model

        if self.api_key:
            openai.api_key = self.api_key
            logger.info(f"GPT內容生成器初始化完成，使用模型: {self.model}")
        else:
            logger.warning("OPENAI_API_KEY 未設定，將使用模板生成")
    
    def generate_stock_analysis(self,
                             stock_id: str,
                             stock_name: str,
                             kol_profile: Dict[str, Any],
                             posting_type: str = "analysis",
                             trigger_type: str = "custom_stocks",
                             serper_analysis: Optional[Dict[str, Any]] = None,
                             ohlc_data: Optional[Dict[str, Any]] = None,
                             technical_indicators: Optional[Dict[str, Any]] = None,
                             content_length: str = "medium",
                             max_words: int = 200,
                             model: Optional[str] = None,
                             template_id: Optional[int] = None,
                             db_connection = None) -> Dict[str, Any]:
        """使用GPT生成股票分析內容 - Prompt 模板系統

        Args:
            stock_id: 股票代號
            stock_name: 股票名稱
            kol_profile: 完整的KOL資料
            posting_type: 發文類型 (analysis/interaction/personalized)
            trigger_type: 觸發器類型
            serper_analysis: Serper新聞分析結果
            ohlc_data: OHLC價格數據
            technical_indicators: 技術指標數據
            content_length: 內容長度
            max_words: 最大字數
            model: 模型ID
            template_id: Prompt 模板 ID（可選）
            db_connection: 資料庫連線（可選）
        """

        try:
            if not self.api_key:
                kol_persona = kol_profile.get('persona', 'mixed')
                return self._fallback_generation(stock_id, stock_name, kol_persona)

            # 🔥 確定使用的模型
            chosen_model = model if model else self.model
            logger.info(f"🤖 GPT 生成器使用模型: {chosen_model}, posting_type: {posting_type}")

            # 處理預設值
            serper_analysis = serper_analysis or {}

            # 🎯 載入 Prompt 模板
            template = self._load_prompt_template(posting_type, template_id, db_connection)
            logger.info(f"📋 使用模板: {template.get('name', '預設模板')}")

            # 🎯 準備參數
            params = self._prepare_template_parameters(
                kol_profile, stock_id, stock_name, trigger_type,
                serper_analysis, ohlc_data, technical_indicators, max_words
            )

            # 🎯 注入參數到模板
            system_prompt = self._inject_parameters(template['system_prompt_template'], params)
            user_prompt = self._inject_parameters(template['user_prompt_template'], params)

            logger.info(f"📝 System Prompt 長度: {len(system_prompt)} 字")
            logger.info(f"📝 User Prompt 長度: {len(user_prompt)} 字")

            # 調用GPT API
            response = openai.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            content = response.choices[0].message.content

            # 解析GPT回應
            result = self._parse_gpt_response(content, stock_id, stock_name)

            # 記錄使用的模板和 prompt
            result['template_id'] = template.get('id')
            result['prompt_system_used'] = system_prompt
            result['prompt_user_used'] = user_prompt

            return result

        except Exception as e:
            logger.error(f"GPT內容生成失敗: {e}")
            kol_persona = kol_profile.get('persona', 'mixed')
            return self._fallback_generation(stock_id, stock_name, kol_persona)

    def _load_prompt_template(self, posting_type: str, template_id: Optional[int] = None, db_connection = None) -> Dict[str, Any]:
        """載入 Prompt 模板

        優先級：
        1. 指定 template_id → 從資料庫載入
        2. 預設模板 → 從資料庫載入 (posting_type + is_default=TRUE)
        3. Fallback → 使用硬編碼預設模板
        """

        # TODO: 實作資料庫查詢（當 db_connection 可用時）
        # if db_connection and template_id:
        #     return db_connection.fetchone("SELECT * FROM prompt_templates WHERE id = %s", (template_id,))
        # elif db_connection:
        #     return db_connection.fetchone("""
        #         SELECT * FROM prompt_templates
        #         WHERE posting_type = %s AND is_default = TRUE AND is_active = TRUE
        #         ORDER BY performance_score DESC LIMIT 1
        #     """, (posting_type,))

        # 🔥 Fallback: 硬編碼預設模板（與資料庫SQL中的一致）
        default_templates = {
            'analysis': {
                'id': None,
                'name': '預設深度分析模板',
                'posting_type': 'analysis',
                'system_prompt_template': '''你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

{writing_style}

你的目標是提供專業、深入的股票分析，包含技術面、基本面、市場情緒等多角度觀點。

請展現你的獨特分析風格，用你習慣的方式表達觀點。

🔥 格式要求：
- 不要使用 Markdown 格式符號（不要用 #, ##, ###, **, __ 等）
- 使用純文本格式，自然分段
- 可以使用中文標點符號（：、。、！、？）來組織內容''',
                'user_prompt_template': '''我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{tech_summary}
請分析這檔股票，包含：
1. 為什麼值得關注
2. 你的專業看法
3. 潛在機會和風險

目標長度：約 {max_words} 字'''
            },
            'interaction': {
                'id': None,
                'name': '預設互動提問模板',
                'posting_type': 'interaction',
                'system_prompt_template': '''你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

{writing_style}

你的目標是與讀者互動，提出引發思考的問題，鼓勵討論。例如：「你覺得這檔股票現在適合進場嗎？留言分享你的看法！」內容要簡短有力。

請展現你的獨特風格，用你習慣的方式提問。

🔥 格式要求：
- 不要使用 Markdown 格式符號（不要用 #, ##, ###, **, __ 等）
- 使用純文本格式，自然分段
- 可以使用中文標點符號（：、。、！、？）來組織內容''',
                'user_prompt_template': '''我想了解 {stock_name}({stock_id}) 最近的表現。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}
請針對這檔股票提出一個引發討論的問題，鼓勵讀者分享看法。

要求：
- 內容簡短（約 {max_words} 字）
- 提出單一核心問題
- 引發讀者思考和互動'''
            },
            'personalized': {
                'id': None,
                'name': '預設個性化風格模板',
                'posting_type': 'personalized',
                'system_prompt_template': '''你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

{writing_style}

你的目標是展現你獨特的個人風格和觀點，讓讀者感受到你的個性和專業。

請充分發揮你的個人特色，用你最自然、最舒服的方式表達。

🔥 格式要求：
- 不要使用 Markdown 格式符號（不要用 #, ##, ###, **, __ 等）
- 使用純文本格式，自然分段
- 可以使用中文標點符號（：、。、！、？）來組織內容''',
                'user_prompt_template': '''我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{tech_summary}
請用你獨特的風格分析這檔股票，展現你的個性和專業。

要求：
- 目標長度：約 {max_words} 字
- 充分展現你的個人風格
- 用你習慣的方式組織內容'''
            }
        }

        template = default_templates.get(posting_type, default_templates['analysis'])
        logger.info(f"📋 載入模板: {template['name']} (posting_type={posting_type})")
        return template

    def _prepare_template_parameters(self,
                                     kol_profile: Dict[str, Any],
                                     stock_id: str,
                                     stock_name: str,
                                     trigger_type: str,
                                     serper_analysis: Dict[str, Any],
                                     ohlc_data: Optional[Dict[str, Any]],
                                     technical_indicators: Optional[Dict[str, Any]],
                                     max_words: int) -> Dict[str, Any]:
        """準備模板參數"""

        # 基本參數
        params = {
            'kol_nickname': kol_profile.get('nickname', '股市分析師'),
            'persona_name': self._get_persona_name(kol_profile.get('persona', 'mixed')),
            'writing_style': kol_profile.get('writing_style', '請用你的專業風格分析股票。'),
            'stock_id': stock_id,
            'stock_name': stock_name,
            'trigger_description': self._get_trigger_description(trigger_type),
            'max_words': max_words,
        }

        # 新聞摘要
        news_items = serper_analysis.get('news_items', [])
        if news_items:
            news_summary = "近期相關新聞：\n"
            for i, news in enumerate(news_items[:5], 1):
                title = news.get('title', '')
                snippet = news.get('snippet', '')
                news_summary += f"{i}. {title}\n"
                if snippet:
                    news_summary += f"   {snippet}\n"
            news_summary += "\n"
            params['news_summary'] = news_summary
        else:
            params['news_summary'] = ''

        # OHLC 摘要
        if ohlc_data:
            close_price = ohlc_data.get('close', 'N/A')
            change_pct = ohlc_data.get('change_percent', 'N/A')
            volume = ohlc_data.get('volume', 'N/A')
            params['ohlc_summary'] = f"""價格資訊：
- 收盤價：{close_price}
- 漲跌幅：{change_pct}%
- 成交量：{volume}

"""
            # 支援嵌套參數 {ohlc.close}
            params['ohlc'] = ohlc_data
        else:
            params['ohlc_summary'] = ''
            params['ohlc'] = {}

        # 技術指標摘要
        if technical_indicators:
            tech_summary = "技術指標：\n"
            for key, value in technical_indicators.items():
                tech_summary += f"- {key}: {value}\n"
            tech_summary += "\n"
            params['tech_summary'] = tech_summary
            # 支援嵌套參數 {tech.RSI}
            params['tech'] = technical_indicators
        else:
            params['tech_summary'] = ''
            params['tech'] = {}

        # 新聞列表（支援 {news[0].title}）
        params['news'] = news_items

        return params

    def _inject_parameters(self, template: str, params: Dict[str, Any]) -> str:
        """注入參數到模板

        支援：
        - 簡單變數：{kol_nickname}, {stock_id}
        - 嵌套變數：{ohlc.close}, {tech.RSI}
        - 陣列索引：{news[0].title}
        """

        result = template

        # 處理簡單變數和嵌套變數
        for key, value in params.items():
            if isinstance(value, dict):
                # 處理嵌套參數 {ohlc.close}
                for sub_key, sub_value in value.items():
                    pattern = f"{{{key}.{sub_key}}}"
                    result = result.replace(pattern, str(sub_value))
            elif isinstance(value, list):
                # 處理陣列索引 {news[0].title}
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        for item_key, item_value in item.items():
                            pattern = f"{{{key}[{i}].{item_key}}}"
                            result = result.replace(pattern, str(item_value))
            else:
                # 處理簡單變數 {kol_nickname}
                pattern = f"{{{key}}}"
                result = result.replace(pattern, str(value))

        return result

    def _build_system_prompt(self, kol_profile: Dict[str, Any]) -> str:
        """構建 System Prompt - 定義 KOL 角色和風格"""

        nickname = kol_profile.get('nickname', '股市分析師')
        persona = kol_profile.get('persona', 'mixed')
        writing_style = kol_profile.get('writing_style', '')

        # 🎯 簡潔的角色定義，不加限制
        persona_name = self._get_persona_name(persona)

        system_prompt = f"""你是 {nickname}，一位{persona_name}風格的股票分析師。

{writing_style if writing_style else '請用你的專業風格分析股票。'}

請展現你的獨特分析風格，用你習慣的方式表達觀點。"""

        return system_prompt

    def _build_user_prompt(self,
                          stock_id: str,
                          stock_name: str,
                          trigger_type: str,
                          serper_analysis: Dict[str, Any],
                          ohlc_data: Optional[Dict[str, Any]],
                          technical_indicators: Optional[Dict[str, Any]],
                          max_words: int) -> str:
        """構建 User Prompt - 整合所有數據（對話式）"""

        # 🎯 觸發器上下文
        trigger_desc = self._get_trigger_description(trigger_type)

        # 🎯 新聞 summary（永遠處理，Serper API 永遠會跑）
        news_summary = ""
        news_items = serper_analysis.get('news_items', [])
        if news_items:
            news_summary = "近期相關新聞：\n"
            for i, news in enumerate(news_items[:5], 1):
                title = news.get('title', '')
                snippet = news.get('snippet', '')
                news_summary += f"{i}. {title}\n"
                if snippet:
                    news_summary += f"   {snippet}\n"
            news_summary += "\n"

        # 🎯 OHLC（空值用 ''，不補充說明文字）
        ohlc_summary = ""
        if ohlc_data:
            close_price = ohlc_data.get('close', 'N/A')
            change_pct = ohlc_data.get('change_percent', 'N/A')
            volume = ohlc_data.get('volume', 'N/A')
            ohlc_summary = f"""價格資訊：
- 收盤價：{close_price}
- 漲跌幅：{change_pct}%
- 成交量：{volume}

"""

        # 🎯 技術指標（空值用 ''，不補充說明文字）
        tech_summary = ""
        if technical_indicators:
            tech_summary = "技術指標：\n"
            for key, value in technical_indicators.items():
                tech_summary += f"- {key}: {value}\n"
            tech_summary += "\n"

        # 🎯 組合數據區塊
        data_section = news_summary + ohlc_summary + tech_summary

        # 🎯 對話式 User Prompt（讓 GPT 自由發揮）
        user_prompt = f"""我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_desc}

【市場數據】
{data_section}請分析這檔股票，包含：
1. 為什麼值得關注
2. 你的專業看法
3. 潛在機會和風險

目標長度：約 {max_words} 字
"""

        return user_prompt

    def _get_trigger_description(self, trigger_type: str) -> str:
        """獲取觸發器描述"""
        descriptions = {
            'limit_up_after_hours': '這是今日盤後漲停的股票',
            'intraday_gainers_by_amount': '這是今日漲幅領先的股票',
            'trending_topics': '這是社群熱門討論的股票',
            'custom_stocks': '這是特定關注的股票'
        }
        return descriptions.get(trigger_type, '這是需要分析的股票')

    def _get_persona_name(self, persona: str) -> str:
        """獲取人設名稱"""
        names = {
            'technical': '技術分析',
            'fundamental': '基本面分析',
            'news_driven': '消息面分析',
            'mixed': '綜合分析'
        }
        return names.get(persona, '綜合分析')

    def _clean_markdown(self, text: str) -> str:
        """清理 Markdown 格式符號

        移除：
        - ### ## # 標題符號
        - ** __ 粗體符號
        - * _ 斜體符號
        """
        if not text:
            return text

        # 移除標題符號（保留內容）
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # 移除粗體符號 **text** 或 __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)

        # 移除斜體符號 *text* 或 _text_ (但保留單獨的 _ 用於分隔)
        text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'\1', text)
        text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text)

        return text

    def _parse_gpt_response(self, content: str, stock_id: str, stock_name: str) -> Dict[str, Any]:
        """解析GPT回應"""

        # 🔥 清理 Markdown 格式（防禦性編程：即使 GPT 使用了 Markdown，也要移除）
        content = self._clean_markdown(content)

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
