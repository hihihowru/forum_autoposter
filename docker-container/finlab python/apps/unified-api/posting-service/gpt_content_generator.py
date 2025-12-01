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

def format_price(value) -> str:
    """格式化股價，移除不必要的小數點（如 201.0 → 201）"""
    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_number_chinese(value) -> str:
    """格式化數字為中文單位（萬、億）"""
    try:
        num = float(value)
        if abs(num) >= 100000000:  # 1億以上
            return f"{num/100000000:.2f}億"
        elif abs(num) >= 10000:  # 1萬以上
            return f"{num/10000:.2f}萬"
        elif num == int(num):
            return str(int(num))
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(value)

class GPTContentGenerator:
    """GPT內容生成器

    預設使用 gpt-4o-mini 模型，提供良好的速度和質量平衡。
    注意：gpt-5 系列模型已禁用（OpenAI 尚未發布）
    """

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
                             realtime_price_data: Optional[Dict[str, Any]] = None,
                             ohlc_data: Optional[Dict[str, Any]] = None,
                             technical_indicators: Optional[Dict[str, Any]] = None,
                             dtno_data: Optional[Dict[str, Any]] = None,  # 🔥 NEW: DTNO 數據
                             content_length: str = "medium",
                             max_words: int = 1000,  # 🔥 增加字數限制以獲得更詳細的分析
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
            realtime_price_data: CMoney即時股價資訊 (包含 current_price, volume, change等)
            ohlc_data: OHLC價格數據
            technical_indicators: 技術指標數據
            dtno_data: DTNO 數據 (基本面/技術面/籌碼面)
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
                serper_analysis, realtime_price_data, ohlc_data, technical_indicators, dtno_data, max_words
            )

            # 🎯 注入參數到模板
            system_prompt = self._inject_parameters(template['system_prompt_template'], params)
            user_prompt = self._inject_parameters(template['user_prompt_template'], params)

            # 🔍 DEBUG: 印出關鍵參數
            logger.info(f"🔍 DEBUG params keys: {list(params.keys())}")
            logger.info(f"🔍 DEBUG has_realtime_price: {params.get('has_realtime_price', False)}")
            logger.info(f"🔍 DEBUG ohlc_summary 長度: {len(params.get('ohlc_summary', ''))} 字")
            if params.get('ohlc_summary'):
                logger.info(f"🔍 DEBUG ohlc_summary 前 200 字: {params['ohlc_summary'][:200]}")
            logger.info(f"📝 System Prompt 長度: {len(system_prompt)} 字")
            logger.info(f"📝 User Prompt 長度: {len(user_prompt)} 字")
            logger.info(f"🔍 DEBUG User Prompt 前 500 字: {user_prompt[:500]}")

            # 🔥 判斷是否為 GPT-5 系列
            # ⚠️ GPT-5 已禁用 - OpenAI 尚未發布 gpt-5 模型，會導致 API 錯誤
            is_gpt5_model = False  # chosen_model.startswith('gpt-5') - DISABLED

            # 🔥 如果使用者選擇了 gpt-5，自動降級到 gpt-4o-mini
            if chosen_model.startswith('gpt-5'):
                logger.warning(f"⚠️ GPT-5 模型已禁用，自動降級到 gpt-4o-mini")
                chosen_model = 'gpt-4o-mini'

            # 🔥 GPT-5 可以使用兩種 API：
            # 1. Responses API (推薦，支援 CoT) - DISABLED
            # 2. Chat Completions API (傳統方式，用 reasoning_effort 參數)
            # 目前統一使用 Chat Completions API

            if is_gpt5_model:
                # 🔥 GPT-5: 使用 Responses API
                logger.info(f"🤖 使用 GPT-5 Responses API")

                # 🔥 所有 GPT-5 模型都使用 medium reasoning effort
                # medium 提供最佳的速度/質量平衡：
                # - gpt-5: ~30-40秒，800-1200字 ✅
                # - gpt-5-mini: ~15-25秒，600-1000字 ✅
                # - gpt-5-nano: ~10-15秒，400-800字 ✅
                #
                # 避免使用 high（太慢，60-90秒，經常 incomplete）
                # 避免使用 low（太快，但內容太短 200-300字）
                reasoning_effort = "medium"

                # 🔥 使用 instructions (system prompt) 和 input (user prompt) 分開傳遞
                api_params = {
                    "model": chosen_model,
                    "instructions": system_prompt,  # System/developer message
                    "input": user_prompt,  # User input
                    "max_output_tokens": 3000,  # 增加輸出長度限制
                    "reasoning": {"effort": reasoning_effort},  # 🔥 根據模型動態調整
                    "text": {"verbosity": "high"}  # 🔥 保持 high 以獲得詳細內容
                }

                logger.info(f"🤖 GPT-5 參數: model={chosen_model}, max_output_tokens=3000, reasoning={reasoning_effort}, verbosity=high")

                # 調用 Responses API
                try:
                    response = openai.responses.create(**api_params)
                except Exception as api_error:
                    logger.error(f"❌ OpenAI Responses API 調用失敗: {type(api_error).__name__}: {api_error}")
                    logger.error(f"❌ 使用的模型: {chosen_model}")
                    logger.error(f"❌ API 參數: {api_params}")
                    raise

                # 🔍 DEBUG: 印出 Responses API 回應結構
                logger.info(f"🔍 DEBUG response.status: {response.status}")
                logger.info(f"🔍 DEBUG response.output 長度: {len(response.output)}")

                # 🔥 如果 response 還沒完成，等待它完成
                if response.status == "incomplete" or response.status == "in_progress":
                    logger.warning(f"⚠️ Response 狀態為 {response.status}，嘗試輪詢獲取完整結果...")

                    # 輪詢等待完成（最多等待 60 秒）
                    import time
                    max_retries = 60
                    retry_count = 0

                    while retry_count < max_retries and response.status in ["incomplete", "in_progress"]:
                        time.sleep(1)
                        retry_count += 1

                        # 重新獲取 response
                        try:
                            response = openai.responses.retrieve(response.id)
                            logger.info(f"🔄 輪詢 {retry_count}/{max_retries}: status={response.status}")
                        except Exception as poll_error:
                            logger.error(f"❌ 輪詢失敗: {poll_error}")
                            break

                    if response.status != "completed":
                        logger.error(f"❌ Response 未在時限內完成，最終狀態: {response.status}")
                    else:
                        logger.info(f"✅ Response 完成，共輪詢 {retry_count} 次")

                # 從 Responses API 提取內容
                content = None

                # 🔥 首先嘗試使用 SDK 的便捷屬性 output_text
                if hasattr(response, 'output_text') and response.output_text:
                    content = response.output_text
                    logger.info(f"✅ 使用 SDK output_text 屬性提取內容，長度: {len(content)} 字")

                # 如果沒有 output_text，手動遍歷 output array
                elif response.output and len(response.output) > 0:
                    logger.info(f"⚠️ SDK 沒有 output_text，手動遍歷 output array")

                    # 遍歷所有 output items，找到 message 類型
                    for i, output_item in enumerate(response.output):
                        logger.info(f"🔍 DEBUG output[{i}].type: {output_item.type}")

                        if output_item.type == "message":
                            logger.info(f"✅ 找到 message item at index {i}")

                            # 檢查 message 是否有 content
                            if hasattr(output_item, 'content') and output_item.content:
                                # 提取 output_text
                                for content_item in output_item.content:
                                    if hasattr(content_item, 'type') and content_item.type == "output_text":
                                        content = content_item.text
                                        logger.info(f"✅ 成功提取文字內容，長度: {len(content)} 字")
                                        break

                                if content:
                                    break  # 找到內容後跳出循環

                    if not content:
                        logger.error(f"❌ 無法從 Responses API 提取文字內容")
                        logger.error(f"❌ response.status: {response.status}")
                        logger.error(f"❌ 所有 output types: {[item.type for item in response.output]}")

                        # 🔥 FIX: 如果 GPT-5 無法提取內容，直接 fallback 到模板
                        logger.warning(f"⚠️ GPT-5 生成失敗，使用備用模板")
                        kol_persona = kol_profile.get('persona', 'mixed')
                        return self._fallback_generation(stock_id, stock_name, kol_persona)
                else:
                    logger.error(f"❌ Responses API 回應沒有 output")
                    # 🔥 FIX: 如果沒有 output，直接 fallback 到模板
                    logger.warning(f"⚠️ GPT-5 沒有回應，使用備用模板")
                    kol_persona = kol_profile.get('persona', 'mixed')
                    return self._fallback_generation(stock_id, stock_name, kol_persona)

            else:
                # 🔥 舊模型: 使用 Chat Completions API
                api_params = {
                    "model": chosen_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }

                # 判斷是否為推理模型（o1, o3 等）
                is_reasoning_model = any(model_prefix in chosen_model.lower() for model_prefix in ['o1', 'o3'])

                # 🔥 根據 max_words 動態計算 max_tokens
                # 中文: 1 token ≈ 1-2 個字，給3倍緩衝確保完整生成
                # 最小 1500，最大 16000（GPT-4 限制）
                calculated_max_tokens = min(max(max_words * 3, 1500), 16000)

                if is_reasoning_model:
                    # 推理模型：使用 max_completion_tokens，不使用 temperature
                    api_params["max_completion_tokens"] = calculated_max_tokens
                    logger.info(f"🤖 使用推理模型參數: max_completion_tokens={calculated_max_tokens} (max_words={max_words})")
                else:
                    # 一般模型：使用 max_tokens + temperature
                    api_params["max_tokens"] = calculated_max_tokens
                    api_params["temperature"] = 0.7
                    logger.info(f"🤖 使用一般模型參數: max_tokens={calculated_max_tokens}, temperature=0.7 (max_words={max_words})")

                # 調用 Chat Completions API
                try:
                    response = openai.chat.completions.create(**api_params)
                except Exception as api_error:
                    logger.error(f"❌ OpenAI Chat Completions API 調用失敗: {type(api_error).__name__}: {api_error}")
                    logger.error(f"❌ 使用的模型: {chosen_model}")
                    logger.error(f"❌ API 參數: {api_params}")
                    raise

                # 🔍 DEBUG: 印出完整 response 結構
                logger.info(f"🔍 DEBUG response.choices 長度: {len(response.choices)}")
                logger.info(f"🔍 DEBUG response.choices[0].message: {response.choices[0].message}")
                logger.info(f"🔍 DEBUG response.choices[0].finish_reason: {response.choices[0].finish_reason}")

                # ⚠️ 檢查是否因 token 限制而截斷
                finish_reason = response.choices[0].finish_reason
                if finish_reason == "length":
                    logger.warning(f"⚠️ 內容因達到 max_tokens 限制而被截斷！")
                    logger.warning(f"⚠️ 當前設定: max_tokens={calculated_max_tokens}, max_words={max_words}")
                    logger.warning(f"⚠️ 建議: 減少 max_words 或內容會不完整")

                content = response.choices[0].message.content

            # 🔍 DEBUG: 印出 GPT 原始回應
            logger.info(f"🔍 DEBUG GPT 原始回應長度: {len(content) if content else 0} 字")
            logger.info(f"🔍 DEBUG GPT 原始回應前 200 字: {content[:200] if content else 'None'}")

            # 解析GPT回應
            result = self._parse_gpt_response(content, stock_id, stock_name)

            # 🔍 DEBUG: 印出解析後的結果
            logger.info(f"🔍 DEBUG 解析後 title: {result.get('title', 'None')}")
            logger.info(f"🔍 DEBUG 解析後 content 長度: {len(result.get('content', ''))}")

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

【角色設定】
{prompt_persona}

【寫作風格】
{writing_style}

【內容護欄】
{prompt_guardrails}

你的目標是提供專業、深入的股票分析，包含技術面、基本面、市場情緒等多角度觀點。

請展現你的獨特分析風格，用你習慣的方式表達觀點。

🔥 重要原則：
- 如果有提供即時股價數據，要自然地融入文章敘述中（例如："台積電今日收在1465元，上漲2.3%"）
- 不要把股價數據當成列表呈現，要像說故事一樣自然提到
- 股價只是分析的一部分，重點是你的觀點和見解

🔥 格式要求：
- 不要使用 Markdown 格式符號（不要用 #, ##, ###, **, __ 等）
- 使用純文本格式，自然分段
- 可以使用中文標點符號（：、。、！、？）來組織內容''',
                'user_prompt_template': '''我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{tech_summary}{dtno_summary}
請分析這檔股票，包含：
1. 為什麼值得關注
2. 你的專業看法
3. 潛在機會和風險

🔥 重要格式要求：
- 第一行是標題，必須精簡（限制 15 字以內）
- 標題範例：「康舒漲停分析」「台積電展望」「聯發科觀察」
- ⚠️ 標題超過 15 字會被截斷
{price_instruction}- 內容長度：約 {max_words} 字，提供深入分析'''
            },
            'interaction': {
                'id': None,
                'name': '預設互動提問模板',
                'posting_type': 'interaction',
                'system_prompt_template': '''你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

【角色設定】
{prompt_persona}

【寫作風格】
{writing_style}

【內容護欄】
{prompt_guardrails}

你的目標是與讀者互動，提出引發思考的問題，鼓勵討論。例如：「你覺得這檔股票現在適合進場嗎？留言分享你的看法！」內容要簡短有力。

請展現你的獨特風格，用你習慣的方式提問。

🔥 重要原則：
- 如果有即時股價數據，在描述市況時自然提到（例如："看到台積電今天漲了2.3%到1465元"）
- 用對話的方式融入股價，不要硬梆梆地列出數字
- 重點是引發討論，不是報價

🔥 格式要求：
- 不要使用 Markdown 格式符號（不要用 #, ##, ###, **, __ 等）
- 使用純文本格式，自然分段
- 可以使用中文標點符號（：、。、！、？）來組織內容''',
                'user_prompt_template': '''我想了解 {stock_name}({stock_id}) 最近的表現。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{dtno_summary}
請針對這檔股票提出一個引發討論的問題，鼓勵讀者分享看法。

要求：
- 🔥 第一行是標題，必須精簡（限制 15 字以內）
- 標題範例：「康舒怎麼看？」「台積電進場？」
- ⚠️ 標題超過 15 字會被截斷
{price_instruction}- 內容長度：約 {max_words} 字
- 提出單一核心問題
- 引發讀者思考和互動'''
            },
            'personalized': {
                'id': None,
                'name': '預設個性化風格模板',
                'posting_type': 'personalized',
                'system_prompt_template': '''你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

【角色設定】
{prompt_persona}

【寫作風格】
{writing_style}

【內容護欄】
{prompt_guardrails}

【內容骨架參考】
{prompt_skeleton}

你的目標是展現你獨特的個人風格和觀點，讓讀者感受到你的個性和專業。

請充分發揮你的個人特色，用你最自然、最舒服的方式表達。

🔥 重要原則：
- 如果有即時股價，用你個人的方式提到（例如："剛看了一下，現在1465元，漲了2.3%，不錯啊"）
- 把股價當成你分析的素材，不是要背誦的數據
- 展現你的個性，股價只是你觀點的佐證

🔥 格式要求：
- 不要使用 Markdown 格式符號（不要用 #, ##, ###, **, __ 等）
- 使用純文本格式，自然分段
- 可以使用中文標點符號（：、。、！、？）來組織內容''',
                'user_prompt_template': '''我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{tech_summary}{dtno_summary}
請用你獨特的風格分析這檔股票，展現你的個性和專業。

要求：
- 🔥 第一行是標題，必須精簡（限制 15 字以內）
- 標題範例：「康舒看法」「台積電筆記」
- ⚠️ 標題超過 15 字會被截斷
{price_instruction}- 目標長度：約 {max_words} 字，提供深入分析
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
                                     realtime_price_data: Optional[Dict[str, Any]],
                                     ohlc_data: Optional[Dict[str, Any]],
                                     technical_indicators: Optional[Dict[str, Any]],
                                     dtno_data: Optional[Dict[str, Any]],
                                     max_words: int) -> Dict[str, Any]:
        """準備模板參數"""

        # 基本參數
        params = {
            'kol_nickname': kol_profile.get('nickname', '股市分析師'),
            'persona_name': self._get_persona_name(kol_profile.get('persona', 'mixed')),
            'writing_style': kol_profile.get('writing_style', '請用你的專業風格分析股票。'),
            # 🔥 NEW: 完整的 KOL Prompt 設定
            'prompt_persona': kol_profile.get('prompt_persona', ''),
            'prompt_guardrails': kol_profile.get('prompt_guardrails', ''),
            'prompt_skeleton': kol_profile.get('prompt_skeleton', ''),
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

        # 🔥 NEW: 即時股價資訊 (優先使用 CMoney 即時數據)
        if realtime_price_data and realtime_price_data.get('is_realtime'):
            current_price = realtime_price_data.get('current_price', 'N/A')
            price_change = realtime_price_data.get('price_change', 0)
            price_change_pct = realtime_price_data.get('price_change_pct', 0)
            volume = realtime_price_data.get('volume', 'N/A')
            high_price = realtime_price_data.get('high_price', 'N/A')
            low_price = realtime_price_data.get('low_price', 'N/A')
            timestamp = realtime_price_data.get('timestamp', '')

            # 格式化漲跌幅
            change_sign = '+' if price_change >= 0 else ''
            change_str = f"{change_sign}{price_change:.2f} ({change_sign}{price_change_pct:.2f}%)"

            # 🔥 NEW APPROACH: Provide context instead of pre-formatted text
            # Let GPT naturally integrate the price info into narrative
            # 🔥 FIX: Use format_price() to remove unnecessary decimal (.0)
            params['ohlc_summary'] = f"""【參考數據 - 請自然融入文章中，不要直接列出】
時間: {timestamp}
當前股價: {format_price(current_price)} 元
漲跌: {change_str}
開盤: {format_price(realtime_price_data.get('open_price', 'N/A'))} 元
最高: {format_price(high_price)} 元
最低: {format_price(low_price)} 元
成交量: {volume:,} 張

"""
            # 支援嵌套參數 {price.current}, {price.change_pct}
            params['price'] = realtime_price_data
            params['has_realtime_price'] = True
            # 🔥 UPDATED: Natural integration instruction
            params['price_instruction'] = '- 在文章開頭自然地提到當前股價和漲跌情況（用敘述方式，不要列點）\n'
        # Fallback: OHLC 摘要
        elif ohlc_data:
            close_price = ohlc_data.get('close', 'N/A')
            change_pct = ohlc_data.get('change_percent', 'N/A')
            volume = ohlc_data.get('volume', 'N/A')
            # 🔥 FIX: Use format_price() to remove unnecessary decimal (.0)
            params['ohlc_summary'] = f"""價格資訊：
- 收盤價：{format_price(close_price)}
- 漲跌幅：{change_pct}%
- 成交量：{volume}

"""
            # 支援嵌套參數 {ohlc.close}
            params['ohlc'] = ohlc_data
            params['has_realtime_price'] = False
            # No price instruction for historical data
            params['price_instruction'] = ''
        else:
            params['ohlc_summary'] = ''
            params['ohlc'] = {}
            params['price'] = {}
            params['has_realtime_price'] = False
            # No price instruction when no price data
            params['price_instruction'] = ''

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

        # 🔥 NEW: DTNO 數據摘要 (基本面/技術面/籌碼面)
        if dtno_data:
            dtno_summary = self._format_dtno_summary(dtno_data)
            params['dtno_summary'] = dtno_summary
            params['dtno'] = dtno_data
            params['has_dtno_data'] = True
            logger.info(f"📊 DTNO 數據已注入: {len(dtno_data)} 個分類")
        else:
            params['dtno_summary'] = ''
            params['dtno'] = {}
            params['has_dtno_data'] = False

        # 新聞列表（支援 {news[0].title}）
        params['news'] = news_items

        return params

    def _format_dtno_summary(self, dtno_data: Dict[str, Any]) -> str:
        """格式化 DTNO 數據為 prompt 摘要"""
        if not dtno_data:
            return ''

        # 分類名稱對照 (30張 DTNO 表 + 別名)
        sub_cat_names = {
            # 基本面 (9張)
            'revenue_stats': '月營收統計',
            'revenue': '月營收詳細',
            'eps': '財報摘要',
            'profitability': '獲利能力',
            'eps_estimate': '機構預估EPS',
            'quarterly_earnings': '季盈餘自結',
            'financial_health': 'IFRS年財報',
            'dividend': '股利政策',
            'analyst_rating': '機構評等',
            # 技術面 (8張)
            'daily_close': '日收盤表',
            'prediction': '預測主要股',
            'daily_kline': '日K線',
            'ma': '均線系統',
            'momentum': '報酬率動能',
            'yearly_stats': '年度統計',
            'technical': '技術指標',
            'industry': '產業標的',
            # 技術面別名
            'kd': 'KD指標',
            'rsi': 'RSI指標',
            'macd': 'MACD指標',
            'bias': '乖離率',
            'volatility': '波動率',
            # 籌碼面 (14張)
            'institutional': '三大法人',
            'foreign_detail': '外資詳細',
            'trust_detail': '投信詳細',
            'dealer_detail': '自營商詳細',
            'broker_top1': 'Top1券商',
            'broker_top5': 'Top5券商',
            'broker_top10': 'Top10券商',
            'broker_top15': 'Top15券商',
            'broker_daily_top15': '每日Top15券商',
            'winner_loser': '贏家輸家統計',
            'major_select': '分點主力選股',
            'major_daily': '日主力買超',
            'major_trading': '主力買超統計',
            'broker_analysis': '分點籌碼分析',
            # 籌碼面別名
            'concentration': '籌碼集中度',
            'broker': '券商分點',
            'major_streak': '主力連續買賣',
        }

        lines = ["\n【DTNO 數據分析資料 - 請融入文章分析中】\n"]

        for sub_cat, data in dtno_data.items():
            if not data or not data.get('data'):
                continue

            titles = data.get('titles', [])
            rows = data.get('data', [])
            display_name = sub_cat_names.get(sub_cat, sub_cat)

            lines.append(f"\n### {display_name}")

            # 只取最新一筆資料
            if rows:
                latest_row = rows[0]
                # 跳過前幾個 meta columns (日期、代號、名稱)
                for i, title in enumerate(titles):
                    if i < 4:  # 跳過 date, time, code, name
                        continue
                    if i >= len(latest_row):
                        break

                    value = latest_row[i]
                    if value is not None and value != '':
                        try:
                            num_val = float(value)

                            # 🔥 FIX: Handle unit conversion based on title
                            # If title contains "千元", multiply by 1000 to get actual 元 value
                            # If title contains "百萬", multiply by 1000000
                            display_title = title
                            if '(千元)' in title or '（千元）' in title:
                                num_val = num_val * 1000  # Convert 千元 to 元
                                display_title = title.replace('(千元)', '').replace('（千元）', '').strip()
                            elif '(百萬)' in title or '（百萬）' in title:
                                num_val = num_val * 1000000  # Convert 百萬 to 元
                                display_title = title.replace('(百萬)', '').replace('（百萬）', '').strip()

                            # 🔥 FIX: Use Chinese units (萬、億) and format cleanly
                            if abs(num_val) >= 100000000:  # 1億以上
                                formatted = f"{num_val/100000000:.2f}億"
                            elif abs(num_val) >= 10000:  # 1萬以上
                                formatted = f"{num_val/10000:.2f}萬"
                            elif num_val == int(num_val):  # 整數 (如股價 201.0 → 201)
                                formatted = f"{int(num_val)}"
                            else:
                                formatted = f"{num_val:.2f}"
                            lines.append(f"- {display_title}: {formatted}")
                        except (ValueError, TypeError):
                            lines.append(f"- {title}: {value}")

        return "\n".join(lines)

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

        # 🎯 對話式 User Prompt（更自然、不強制結構）
        user_prompt = f"""請分析 {stock_name}({stock_id}) 的投資價值。

背景：{trigger_desc}

相關資訊：
{data_section}
用你的專業角度分析這檔股票，包括值得關注的重點、你的看法、以及投資人應該注意的機會與風險。

請用自然流暢的方式表達，不需要固定格式，約 {max_words} 字。"""

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

        # 🔥 FIX: 防禦性檢查 - 如果 content 是 None 或空字串
        if not content:
            logger.error(f"❌ _parse_gpt_response 收到空內容，返回預設結構")
            return {
                "title": f"{stock_name}({stock_id}) 市場分析",
                "content": f"【{stock_name}({stock_id}) 市場觀察】\n\n目前暫無詳細分析內容，請稍後再試。",
                "content_md": f"【{stock_name}({stock_id}) 市場觀察】\n\n目前暫無詳細分析內容，請稍後再試。",
                "commodity_tags": [{"type": "Stock", "key": stock_id, "bullOrBear": 0}],
                "community_topic": None,
                "generation_method": "empty_fallback",
                "model_used": self.model
            }

        # 🔥 清理 Markdown 格式（防禦性編程：即使 GPT 使用了 Markdown，也要移除）
        content = self._clean_markdown(content)

        # 簡單的內容分割
        lines = content.split('\n')
        title = ""
        main_content = content

        # 提取標題（第一行非空行）
        title_line_index = -1
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(' '):
                title = line.strip()
                title_line_index = i
                break

        # 如果沒有找到標題，使用預設
        if not title:
            title = f"{stock_name} 分析"

        # 🔥 標題長度控制（最多 25 字，CMoney 標題限制約 30 字）
        MAX_TITLE_LENGTH = 25
        if len(title) > MAX_TITLE_LENGTH:
            logger.warning(f"⚠️ 標題過長 ({len(title)} 字)，進行截斷: {title[:30]}...")

            # 策略 1: 嘗試在標點符號處截斷
            punctuation_marks = ['，', '、', '！', '？', '：', '｜', '|', '-', '—', ' ']
            truncated = False
            for i in range(MAX_TITLE_LENGTH - 1, 5, -1):  # 從最大長度往回找，最少保留 5 字
                if title[i] in punctuation_marks:
                    title = title[:i]
                    truncated = True
                    break

            # 策略 2: 如果沒有合適的標點，直接截斷
            if not truncated and len(title) > MAX_TITLE_LENGTH:
                title = title[:MAX_TITLE_LENGTH]

            logger.info(f"✂️ 截斷後標題: {title}")

        # 🔥 移除內容開頭的重複標題
        # 如果內容以標題開頭，則移除第一行（標題行）及其後的空行
        if title_line_index >= 0:
            # 從標題行之後開始
            content_lines = lines[title_line_index + 1:]

            # 跳過標題後的空行
            while content_lines and not content_lines[0].strip():
                content_lines.pop(0)

            # 重新組合內容（不包含標題）
            main_content = '\n'.join(content_lines).strip()

        # 如果移除標題後內容為空，使用原始內容
        if not main_content:
            main_content = content

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
