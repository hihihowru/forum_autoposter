"""
個人化模組 - 統一架構處理KOL內容個人化
"""

import random
import json
import logging
import os
import openai
from typing import Dict, List, Any, Optional, Tuple
from kol_database_service import KOLProfile, KOLDatabaseService
from random_content_generator import RandomContentGenerator

logger = logging.getLogger(__name__)

# LLM配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
openai.api_key = OPENAI_API_KEY

# 混合方案三：LLM驅動的個人化系統
class cLLMPersonalizationProcessor:
    """LLM驅動的個人化處理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_personalized_content(self, standard_content: str, kol_profile: KOLProfile, trigger_type: str = None) -> str:
        """使用LLM生成個人化內容"""
        
        try:
            # 1. 構建動態prompt
            prompt = self._build_dynamic_prompt(standard_content, kol_profile, trigger_type)
            
            # 2. 調用指定的GPT模型
            response = self._call_llm(prompt, kol_profile)
            
            # 3. 後處理和驗證
            personalized_content = self._post_process_content(response, kol_profile)
            
            self.logger.info(f"🤖 LLM個人化完成 - 模型: {kol_profile.model_id}, 長度: {len(personalized_content)} 字")
            return personalized_content
            
        except Exception as e:
            self.logger.error(f"❌ LLM個人化失敗: {e}")
            # 回退到配置驅動
            return self._fallback_to_config(standard_content, kol_profile)
    
    def generate_personalized_title(self, content: str, kol_profile: KOLProfile, standard_title: str) -> str:
        """使用LLM生成個人化標題"""
        
        try:
            # 1. 構建標題生成prompt
            prompt = self._build_title_prompt(content, kol_profile, standard_title)
            
            # 2. 調用指定的GPT模型
            response = self._call_llm(prompt, kol_profile)
            
            # 3. 後處理標題
            personalized_title = self._post_process_title(response, kol_profile)
            
            self.logger.info(f"🤖 LLM標題生成完成: {personalized_title}")
            return personalized_title
            
        except Exception as e:
            self.logger.error(f"❌ LLM標題生成失敗: {e}")
            # 回退到配置驅動
            return self._fallback_title_generation(content, kol_profile, standard_title)
    
    def _build_dynamic_prompt(self, standard_content: str, kol_profile: KOLProfile, trigger_type: str = None) -> str:
        """構建動態個人化prompt"""
        
        # 基礎角色設定
        persona_prompt = f"""
你是一個{kol_profile.persona}風格的股票分析師，名為{kol_profile.nickname}。

## 角色背景
{kol_profile.backstory or '資深股票分析師'}

## 專業領域
{kol_profile.expertise or '股票分析'}

## 寫作風格設定
- 語氣風格：{kol_profile.tone_style or '專業理性'}
- 打字習慣：{kol_profile.typing_habit or '標準標點符號'}
- 常用術語：{kol_profile.common_terms or '專業術語'}
- 口語化用詞：{kol_profile.colloquial_terms or '口語化表達'}

## 語調控制
- 正式程度：{kol_profile.tone_formal or 7}/10
- 情感強度：{kol_profile.tone_emotion or 5}/10
- 自信程度：{kol_profile.tone_confidence or 7}/10
- 緊迫感：{kol_profile.tone_urgency or 6}/10

## 內容結構偏好
- 內容骨架：{kol_profile.prompt_skeleton or '標準分析結構'}
- 行動呼籲：{kol_profile.prompt_cta or '歡迎討論'}
- 標籤風格：{kol_profile.prompt_hashtags or '相關標籤'}
- 個人簽名：{kol_profile.signature or ''}

## 互動風格
- 提問比例：{int((kol_profile.question_ratio or 0.3) * 100)}%
- 幽默機率：{int((getattr(kol_profile, 'humor_probability', 0.3) * 100))}%
- 互動開場白：{', '.join(kol_profile.interaction_starters) if kol_profile.interaction_starters else '你覺得呢？'}

## 目標受眾
{kol_profile.target_audience or '一般投資者'}

## 內容類型偏好
{', '.join(kol_profile.content_types) if kol_profile.content_types else '技術分析'}

## 數據來源偏好
{kol_profile.data_source or '綜合分析'}

## 發文時間偏好
{kol_profile.post_times or '隨時'}

## 內容長度偏好
{kol_profile.content_length or '中等'}

## 模型設定
- 模型溫度：{kol_profile.model_temp or 0.7}
- 最大token數：{kol_profile.max_tokens or 1000}
- 模板變體：{kol_profile.template_variant or '標準'}

## 任務
請將以下標準化內容轉換為符合你個人風格的版本：

**標準內容：** {standard_content[:500]}...

**觸發器類型：** {trigger_type or '一般分析'}

**🔥 重要提醒：**
- 如果觸發器是 "limit_down_after_hours"（盤後跌停），內容必須反映股票下跌的事實
- 如果觸發器是 "limit_up_after_hours"（盤後漲停），內容必須反映股票上漲的事實
- 必須根據觸發器類型和新聞內容保持一致，不能產生相反的內容

**要求：**
1. 完全符合你的角色設定和寫作風格
2. 使用你的常用術語和口語化用詞
3. 保持核心資訊不變，但表達方式要個人化
4. 避免聳動性用詞，保持客觀理性
5. 根據你的語調設定調整內容風格
6. 如果啟用幽默模式，適度添加輕鬆元素
7. 根據你的互動風格添加適當的互動元素
8. 使用你的個人簽名和標籤風格
9. 🔥 不要使用結構化標題（如：【酸民觀點】、【技術分析】、【小道消息】等）
10. 🔥 不要使用emoji表情符號
11. 🔥 內容要自然流暢，像真人寫的分析
12. 🔥 不要使用編號列表（如：1. 消息來源、2. 重點內容等）
13. 🔥 必須根據觸發器類型和新聞內容保持一致，不能產生相反的內容

**輸出格式：**
直接輸出個人化後的內容，不需要額外說明。
"""
        
        return persona_prompt
    
    def _build_title_prompt(self, content: str, kol_profile: KOLProfile, standard_title: str) -> str:
        """構建標題生成prompt"""
        
        # 從標準標題中提取股票名稱
        stock_name = self._extract_stock_name_from_title(standard_title)
        
        title_prompt = f"""
你是一個{kol_profile.persona}風格的股票分析師，名為{kol_profile.nickname}。

## 角色設定
- 語氣風格：{kol_profile.tone_style or '專業理性'}
- 常用術語：{kol_profile.common_terms or '專業術語'}
- 口語化用詞：{kol_profile.colloquial_terms or '口語化表達'}

## 標題風格設定
- 標題開場詞：{', '.join(kol_profile.title_openers) if kol_profile.title_openers else '無'}
- 標題簽名模式：{', '.join(kol_profile.title_signature_patterns) if kol_profile.title_signature_patterns else '無'}
- 標題結尾詞：{kol_profile.title_tail_word or '無'}
- 禁用詞彙：{', '.join(kol_profile.title_banned_words) if kol_profile.title_banned_words else '無'}

## 語調控制
- 正式程度：{kol_profile.tone_formal or 7}/10
- 情感強度：{kol_profile.tone_emotion or 5}/10
- 自信程度：{kol_profile.tone_confidence or 7}/10

## 任務
請根據以下內容生成一個符合你個人風格的標題：

**股票名稱：** {stock_name}
**內容摘要：** {content[:300]}...

**要求：**
1. 完全符合你的角色設定和標題風格
2. 使用你的常用術語和口語化用詞
3. 避免聳動性用詞，保持客觀理性
4. 根據你的語調設定調整標題風格
5. 可以適當使用你的標題開場詞和結尾詞
6. 避免使用禁用詞彙
7. 標題長度控制在15字以內
8. 🔥 不要使用結構化標題（如：【酸民觀點】、【技術分析】、【小道消息】等）
9. 🔥 不要使用emoji表情符號
10. 🔥 標題要自然流暢，像真人寫的

**輸出格式：**
直接輸出標題，不需要額外說明。
"""
        
        return title_prompt
    
    def _call_llm(self, prompt: str, kol_profile: KOLProfile) -> str:
        """調用指定的LLM模型"""
        
        try:
            # 根據KOL設定選擇模型
            model = kol_profile.model_id or "gpt-4o-mini"
            temperature = kol_profile.model_temp or 0.7
            max_tokens = kol_profile.max_tokens or 1000
            
            self.logger.info(f"🤖 調用LLM - 模型: {model}, 溫度: {temperature}, 最大token: {max_tokens}")
            
            response = openai.chat.completions.create(
                   model=model,
                   messages=[
                       {"role": "system", "content": "你是一個專業的股票分析師，擅長個人化內容生成。"},
                       {"role": "user", "content": prompt}
                   ],
                   temperature=temperature,
                   max_tokens=max_tokens
               )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"❌ LLM調用失敗: {e}")
            raise e
    
    def _post_process_content(self, content: str, kol_profile: KOLProfile) -> str:
        """後處理個人化內容"""
        
        # 1. 根據KOL設定調整內容
        if kol_profile.allow_hashtags and kol_profile.prompt_hashtags:
            content = f"{content}\n\n{kol_profile.prompt_hashtags}"
        
        if kol_profile.signature:
            content = f"{content}\n\n{kol_profile.signature}"
        
        if kol_profile.prompt_cta:
            content = f"{content}\n\n{kol_profile.prompt_cta}"
        
        # 2. 根據內容長度偏好調整
        if kol_profile.content_length == "short":
            sentences = content.split('。')
            content = '。'.join(sentences[:2]) + '。'
        elif kol_profile.content_length == "long":
            content = f"{content}\n\n📈 延伸分析：\n• 市場趨勢觀察\n• 風險評估建議"
        
        return content
    
    def _post_process_title(self, title: str, kol_profile: KOLProfile) -> str:
        """後處理個人化標題"""
        
        # 1. 檢查禁用詞彙
        if kol_profile.title_banned_words:
            for banned_word in kol_profile.title_banned_words:
                if banned_word in title:
                    title = title.replace(banned_word, "分析")
        
        # 2. 過濾聳動性用詞
        sensational_words = ["強勢突破", "爆量上攻", "衝高", "強勢上漲", "突破性上漲", "量價齊揚"]
        for word in sensational_words:
            if word in title:
                title = title.replace(word, "盤後分析")
        
        return title
    
    def _fallback_to_config(self, standard_content: str, kol_profile: KOLProfile) -> str:
        """回退到配置驅動的個人化"""
        
        self.logger.info("🔄 回退到配置驅動個人化")
        
        # 使用現有的配置驅動邏輯
        content = standard_content
        
        # 根據KOL設定進行基本替換
        if kol_profile.common_terms:
            terms = [term.strip() for term in kol_profile.common_terms.split(',') if term.strip()]
            for term in terms[:2]:
                content = content.replace("分析", f"{term}分析")
        
        if kol_profile.colloquial_terms:
            terms = [term.strip() for term in kol_profile.colloquial_terms.split(',') if term.strip()]
            for term in terms[:1]:
                content = content.replace("股票", term)
        
        return content
    
    def _fallback_title_generation(self, content: str, kol_profile: KOLProfile, standard_title: str) -> str:
        """回退到配置驅動的標題生成"""
        
        self.logger.info("🔄 回退到配置驅動標題生成")
        
        # 從標準標題中提取股票名稱
        stock_name = self._extract_stock_name_from_title(standard_title)
        
        # 使用KOL的標題設定
        title_openers = kol_profile.title_openers or [""]
        opener = random.choice(title_openers) if title_openers else ""
        
        title_signature_patterns = kol_profile.title_signature_patterns or ["{stock}分析"]
        pattern = random.choice(title_signature_patterns) if title_signature_patterns else "{stock}分析"
        
        title_tail_word = kol_profile.title_tail_word or ""
        
        # 生成標題
        if opener:
            title = f"{opener}{stock_name} 盤後分析{title_tail_word}"
        else:
            title = pattern.format(stock=stock_name) + title_tail_word
        
        return title
    
    def _extract_stock_name_from_title(self, title: str) -> str:
        """從標題中提取股票名稱"""
        
        import re
        
        # 匹配股票名稱模式
        patterns = [
            r'【.*?】(.+?)\(',  # 【KOL-200】第一銅(
            r'(.+?)\(',         # 第一銅(
            r'【.*?】(.+?)$',   # 【KOL-200】第一銅
            r'^(.+?)\s+',       # 嘉鋼 分析
            r'^(.+?)$',         # 嘉鋼
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1).strip()
        
        return "台股"

# 增強版個人化Prompt模板
ENHANCED_PERSONALIZATION_PROMPT_TEMPLATE = """
你是一個{persona}風格的股票分析師，名為{nickname}。

## 角色背景
{backstory}

## 專業領域
{expertise}

## 寫作風格設定
- 語氣風格：{tone_style}
- 打字習慣：{typing_habit}
- 常用術語：{common_terms}
- 口語化用詞：{colloquial_terms}

## 標題風格設定
- 標題開場詞：{title_openers}
- 標題簽名模式：{title_signature_patterns}
- 標題結尾詞：{title_tail_word}
- 禁用詞彙：{title_banned_words}

## 互動風格
- 提問比例：{question_ratio}%
- 幽默機率：{humor_probability}%
- 互動開場白：{interaction_starters}

## 內容結構偏好
- 內容骨架：{prompt_skeleton}
- 行動呼籲：{prompt_cta}
- 標籤風格：{prompt_hashtags}
- 個人簽名：{signature}

## 語調控制
- 正式程度：{tone_formal}/10
- 情感強度：{tone_emotion}/10
- 自信程度：{tone_confidence}/10
- 緊迫感：{tone_urgency}/10

## 內容風格機率分布
- 輕鬆風格：{casual_probability}%
- 幽默風格：{humorous_probability}%
- 技術風格：{technical_probability}%
- 專業風格：{professional_probability}%

## 分析深度偏好
- 基礎分析：{basic_analysis_probability}%
- 詳細分析：{detailed_analysis_probability}%
- 全面分析：{comprehensive_analysis_probability}%

## 內容長度偏好
- 短內容：{short_content_probability}%
- 中等內容：{medium_content_probability}%
- 長內容：{long_content_probability}%

## 發文形態指令
{style_instructions}

## 任務
請將以下標準化內容轉換為符合你個人風格的版本：

**標準標題：** {standard_title}
**標準內容：** {standard_content}

**要求：**
1. 標題必須符合你的標題風格設定
2. 內容結構要符合你的偏好
3. 語調要符合你的設定
4. 保持核心資訊不變
5. 🔥 不要使用結構化標題（如：【酸民觀點】、【技術分析】等）
6. 🔥 不要使用emoji表情符號
7. 🔥 內容要自然流暢，像真人寫的分析

**輸出格式：**
標題：[個人化標題]
內容：[個人化內容]
"""

class PostingStyleRandomizer:
    """發文形態隨機器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def determine_posting_style(self, kol_profile: KOLProfile) -> Tuple[str, Dict[str, Any]]:
        """決定發文形態：提問 vs 發表看法"""
        
        # 1. 根據question_ratio決定是否提問
        question_probability = kol_profile.question_ratio or 0.3
        
        if random.random() < question_probability:
            return "question", self.generate_question_style(kol_profile)
        else:
            return "opinion", self.generate_opinion_style(kol_profile)
    
    def generate_question_style(self, kol_profile: KOLProfile) -> Dict[str, Any]:
        """生成提問風格參數"""
        return {
            "style": "question",
            "interaction_starter": self.random_select(kol_profile.interaction_starters),
            "tone_interaction": kol_profile.tone_interaction or 6,
            "question_ratio": 1.0,  # 強制提問
            "tone_confidence": min(kol_profile.tone_confidence or 7, 6),  # 提問時降低自信度
        }
    
    def generate_opinion_style(self, kol_profile: KOLProfile) -> Dict[str, Any]:
        """生成發表看法風格參數"""
        return {
            "style": "opinion",
            "tone_confidence": kol_profile.tone_confidence or 7,
            "tone_formal": kol_profile.tone_formal or 5,
            "tone_emotion": kol_profile.tone_emotion or 5,
            "question_ratio": 0.0,  # 不提問
        }
    
    def random_select(self, array_field: List[str]) -> str:
        """隨機選擇陣列中的一個元素"""
        if not array_field or len(array_field) == 0:
            return "你覺得呢？"
        return random.choice(array_field)

class EnhancedParameterMapper:
    """增強版參數映射器 - 使用更多KOL欄位"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def map_kol_to_prompt(self, kol_profile: KOLProfile, style_params: Dict[str, Any], content_length: str = None) -> Dict[str, Any]:
        """將KOL資料庫欄位映射到prompt參數"""
        
        # 基本資訊映射
        basic_params = {
            'persona': kol_profile.persona or '專業分析師',
            'nickname': kol_profile.nickname or '分析師',
            'backstory': kol_profile.backstory or '資深股票分析師',
            'expertise': kol_profile.expertise or '股票分析',
        }
        
        # 風格設定映射
        style_mapping = {
            'tone_style': kol_profile.tone_style or '專業理性',
            'typing_habit': kol_profile.typing_habit or '標準標點符號',
            'common_terms': kol_profile.common_terms or '專業術語',
            'colloquial_terms': kol_profile.colloquial_terms or '口語化表達',
        }
        
        # 標題設定映射
        title_params = {
            'title_openers': self.format_array(kol_profile.title_openers),
            'title_signature_patterns': self.format_array(kol_profile.title_signature_patterns),
            'title_tail_word': kol_profile.title_tail_word or '',
            'title_banned_words': self.format_array(kol_profile.title_banned_words),
        }
        
        # 互動設定映射
        interaction_params = {
            'question_ratio': int((style_params.get('question_ratio', 0.3) * 100)),
            'humor_probability': int((getattr(kol_profile, 'humor_probability', 0.3) * 100)),
            'interaction_starters': self.format_array(kol_profile.interaction_starters),
        }
        
        # 內容結構映射
        content_params = {
            'prompt_skeleton': kol_profile.prompt_skeleton or '標準分析結構',
            'prompt_cta': kol_profile.prompt_cta or '歡迎討論',
            'prompt_hashtags': kol_profile.prompt_hashtags or '相關標籤',
            'signature': kol_profile.signature or '',
        }
        
        # 語調控制映射
        tone_params = {
            'tone_formal': kol_profile.tone_formal or 7,
            'tone_emotion': kol_profile.tone_emotion or 5,
            'tone_confidence': style_params.get('tone_confidence', kol_profile.tone_confidence or 7),
            'tone_urgency': kol_profile.tone_urgency or 6,
        }
        
        # 機率分布映射
        probability_params = self._map_probability_distributions(kol_profile)
        
        # 合併所有參數
        return {
            **basic_params, 
            **style_mapping, 
            **title_params,
            **interaction_params, 
            **content_params, 
            **tone_params,
            **probability_params
        }
    
    def _map_probability_distributions(self, kol_profile: KOLProfile) -> Dict[str, int]:
        """映射機率分布"""
        
        # 內容風格機率分布
        content_style_probs = kol_profile.content_style_probabilities or {
            'casual': 0.3, 'humorous': 0.1, 'technical': 0.3, 'professional': 0.3
        }
        
        # 分析深度機率分布
        analysis_depth_probs = kol_profile.analysis_depth_probabilities or {
            'basic': 0.2, 'detailed': 0.5, 'comprehensive': 0.3
        }
        
        # 內容長度機率分布
        content_length_probs = kol_profile.content_length_probabilities or {
            'short': 0.1, 'medium': 0.4, 'long': 0.3, 'extended': 0.15, 'thorough': 0.0, 'comprehensive': 0.05
        }
        
        return {
            'casual_probability': int(content_style_probs.get('casual', 0.3) * 100),
            'humorous_probability': int(content_style_probs.get('humorous', 0.1) * 100),
            'technical_probability': int(content_style_probs.get('technical', 0.3) * 100),
            'professional_probability': int(content_style_probs.get('professional', 0.3) * 100),
            'basic_analysis_probability': int(analysis_depth_probs.get('basic', 0.2) * 100),
            'detailed_analysis_probability': int(analysis_depth_probs.get('detailed', 0.5) * 100),
            'comprehensive_analysis_probability': int(analysis_depth_probs.get('comprehensive', 0.3) * 100),
            'short_content_probability': int(content_length_probs.get('short', 0.1) * 100),
            'medium_content_probability': int(content_length_probs.get('medium', 0.4) * 100),
            'long_content_probability': int(content_length_probs.get('long', 0.3) * 100),
        }
    
    def format_array(self, array_field: List[str]) -> str:
        """格式化陣列欄位"""
        if not array_field:
            return '無'
        if isinstance(array_field, list):
            return '、'.join(array_field)
        return str(array_field)
    
    def get_style_instructions(self, style_type: str, style_params: Dict[str, Any]) -> str:
        """根據發文形態生成指令"""
        if style_type == "question":
            return f"""
            發文形態：提問式
            - 使用互動開場白：{style_params.get('interaction_starter', '你覺得呢？')}
            - 互動語調：{style_params.get('tone_interaction', 6)}/10
            - 降低自信度，以詢問的方式表達
            - 結尾要包含提問或邀請討論
            """
        else:  # opinion
            return f"""
            發文形態：發表看法
            - 自信程度：{style_params.get('tone_confidence', 7)}/10
            - 正式程度：{style_params.get('tone_formal', 5)}/10
            - 情感強度：{style_params.get('tone_emotion', 5)}/10
            - 以肯定的語氣表達觀點
            - 結尾要包含明確的結論或建議
            """

class EnhancedPersonalizationProcessor:
    """增強版個人化處理器 - 使用更多KOL欄位"""
    
    def __init__(self):
        self.kol_service = KOLDatabaseService()
        self.parameter_mapper = EnhancedParameterMapper()
        self.style_randomizer = PostingStyleRandomizer()
        self.llm_processor = cLLMPersonalizationProcessor()  # 新增：LLM處理器
        self.random_generator = RandomContentGenerator()  # 新增：隨機化生成器
        self.prompt_template = ENHANCED_PERSONALIZATION_PROMPT_TEMPLATE
        self.logger = logging.getLogger(__name__)
    
    def _format_realtime_data_for_llm(self, price_data: Dict, trigger_type: str) -> str:
        """將盤中觸發器的 JSON 數據格式化為 LLM 可讀的格式 - 包含完整的 column names
        
        Args:
            price_data: 盤中觸發器返回的即時股價 JSON 數據
            trigger_type: 觸發器類型
            
        Returns:
            str: 格式化後的數據摘要（包含 column names）
        """
        try:
            if not price_data:
                return ""
            
            # 🔥 直接使用盤中觸發器的原始 JSON 數據，包含所有 column names
            # 數據格式: [交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價]
            
            # 構建完整的數據摘要，包含 column names
            summary_parts = []
            
            # 基本股價信息（包含 column name）
            current_price = price_data.get('current_price', 0)
            if current_price > 0:
                summary_parts.append(f"即時成交價: {current_price} 元")
            
            # 漲跌信息（包含 column name）
            change_amount = price_data.get('change_amount', 0)
            if change_amount != 0:
                direction = "上漲" if change_amount > 0 else "下跌"
                summary_parts.append(f"漲跌: {direction} {abs(change_amount)} 元")
            
            change_percentage = price_data.get('change_percentage', 0)
            if change_percentage != 0:
                summary_parts.append(f"漲跌幅: {change_percentage:+.2f}%")
            
            # 成交量信息（包含 column name）
            current_volume = price_data.get('current_volume', 0)
            if current_volume > 0:
                summary_parts.append(f"即時成交量: {current_volume:,} 張")
            
            total_volume = price_data.get('total_volume', 0)
            if total_volume > 0:
                summary_parts.append(f"累計成交量: {total_volume:,} 張")
            
            # 價格區間（包含 column name）
            high_price = price_data.get('high_price', 0)
            low_price = price_data.get('low_price', 0)
            if high_price > 0 and low_price > 0:
                summary_parts.append(f"最高價: {high_price} 元")
                summary_parts.append(f"最低價: {low_price} 元")
            
            open_price = price_data.get('open_price', 0)
            if open_price > 0:
                summary_parts.append(f"開盤價: {open_price} 元")
            
            # 漲停/跌停狀態
            is_limit_up = price_data.get('is_limit_up', False)
            is_limit_down = price_data.get('is_limit_down', False)
            if is_limit_up:
                summary_parts.append("狀態: 已漲停")
            elif is_limit_down:
                summary_parts.append("狀態: 已跌停")
            elif abs(change_percentage) >= 9.5:
                if change_percentage > 0:
                    summary_parts.append("狀態: 接近漲停")
                else:
                    summary_parts.append("狀態: 接近跌停")
            
            # 根據觸發器類型添加特殊信息
            if trigger_type in ['intraday_limit_up', 'limit_up_after_hours']:
                summary_parts.append("觸發原因: 漲停觸發")
            elif trigger_type in ['intraday_limit_down', 'limit_down_after_hours']:
                summary_parts.append("觸發原因: 跌停觸發")
            elif trigger_type in ['intraday_gainers_by_amount', 'intraday_gainers_by_volume']:
                summary_parts.append("觸發原因: 漲幅排序")
            
            # 🔥 新增：包含原始 JSON 數據的完整信息（使用 column_names）
            column_names = price_data.get('column_names', ['交易時間', '傳輸序號', '內外盤旗標', '即時成交價', '即時成交量', '最低價', '最高價', '標的', '漲跌', '漲跌幅', '累計成交總額', '累計成交量', '開盤價'])
            raw_data = price_data.get('raw_data', [])
            
            json_context = f"""
【盤中觸發器原始數據結構】
數據格式: {', '.join(column_names)}

【原始數據數組】
{raw_data}

【當前股票即時數據】
"""
            
            # 格式化為 LLM 可讀的文本
            if summary_parts:
                formatted_summary = json_context + "\n".join(f"• {part}" for part in summary_parts)
                self.logger.info(f"📊 格式化即時數據摘要: {len(summary_parts)} 項數據（包含 column names）")
                return formatted_summary
            else:
                return json_context + "• 無即時數據"
                
        except Exception as e:
            self.logger.error(f"❌ 格式化即時數據失敗: {e}")
            return ""
    
    def _enhance_content_with_realtime_data(self, content: str, price_data: Dict, trigger_type: str) -> str:
        """將即時股價數據整合到內容中 - 直接使用盤中觸發器 JSON 數據
        
        Args:
            content: 原始內容
            price_data: 盤中觸發器返回的即時股價 JSON 數據
            trigger_type: 觸發器類型
            
        Returns:
            str: 整合後的內容
        """
        try:
            # 🔥 直接使用盤中觸發器的 JSON 數據
            if not price_data:
                return content
            
            # 🔥 直接將 JSON 數據格式化為 LLM 可讀的格式（包含 column names）
            json_summary = self._format_realtime_data_for_llm(price_data, trigger_type)
            
            if not json_summary:
                return content
            
            # 🔥 直接將格式化後的 JSON 數據整合到內容中
            # 根據觸發器類型決定插入位置和方式
            if trigger_type in ['intraday_limit_up', 'limit_up_after_hours']:
                # 漲停觸發器：在開頭加入完整的 JSON 數據
                enhanced_content = f"{json_summary}\n\n{content}"
            elif trigger_type in ['intraday_limit_down', 'limit_down_after_hours']:
                # 跌停觸發器：在開頭加入完整的 JSON 數據
                enhanced_content = f"{json_summary}\n\n{content}"
            else:
                # 其他觸發器：在內容中自然插入完整的 JSON 數據
                enhanced_content = f"{content}\n\n{json_summary}"
            
            self.logger.info(f"📊 整合即時股價 JSON 數據到內容中（包含 column names）")
            return enhanced_content
            
        except Exception as e:
            self.logger.error(f"❌ 整合即時股價數據失敗: {e}")
            return content
    
    def personalize_content(self, standard_title: str, standard_content: str, kol_serial: str, batch_config: Dict = None, serper_analysis: Dict = None, trigger_type: str = None, real_time_price_data: Dict = None, posting_type: str = 'analysis', max_words: int = None) -> Tuple[str, str, Dict]:
        """增強版個人化處理函數 - 整合隨機化生成

        Args:
            standard_title: 標準化標題
            standard_content: 標準化內容
            kol_serial: KOL序號
            batch_config: 批次設定 (可選)
            serper_analysis: Serper新聞分析數據 (可選)
            trigger_type: 觸發器類型 (可選)
            real_time_price_data: 即時股價數據 (可選)
            posting_type: 發文類型 ('analysis' 或 'interaction')
            max_words: 最大字數限制 (可選)

        Returns:
            Tuple[str, str, Dict]: (個人化標題, 個人化內容, 隨機化元數據)
        """
        try:
            # 🔇 SIMPLIFIED: Single line instead of 5 verbose input logs
            self.logger.info(f"🎨 個人化 KOL{kol_serial} | {posting_type} | {trigger_type or 'manual'} | {len(standard_content)}字")
            
            # 🔥 新增：處理即時股價數據
            if real_time_price_data:
                self.logger.info(f"📊 個人化模組 INPUT - 即時股價數據: {real_time_price_data}")
                # 將即時股價數據整合到標準內容中
                enhanced_content = self._enhance_content_with_realtime_data(standard_content, real_time_price_data, trigger_type)
                if enhanced_content != standard_content:
                    standard_content = enhanced_content
                    self.logger.info(f"✅ 已整合即時股價數據到內容中")
            else:
                self.logger.info(f"⚠️ 沒有即時股價數據，使用原始內容")
            
            # 1. 獲取KOL設定
            kol_profile = self.kol_service.get_kol_by_serial(str(kol_serial))
            if not kol_profile:
                self.logger.warning(f"⚠️ 找不到KOL {kol_serial}，返回原始內容")
                return standard_title, standard_content, {}
            
            # 🎲 新增：使用隨機化生成器
            self.logger.info(f"🎲 開始隨機化內容生成 - 發文類型: {posting_type}")
            
            # 從 serper_analysis 中提取股票信息
            stock_name = ""
            stock_code = ""
            if serper_analysis:
                stock_name = serper_analysis.get('stock_name', '')
                stock_code = serper_analysis.get('stock_code', '')
                self.logger.info(f"🎲 從 serper_analysis 提取股票信息: {stock_name}({stock_code})")
            else:
                self.logger.info(f"🎲 沒有 serper_analysis 數據")
            
            # 使用隨機化生成器
            self.logger.info(f"🎲 開始調用隨機化生成器...")
            try:
                random_result = self.random_generator.generate_randomized_content(
                    original_title=standard_title,
                    original_content=standard_content,
                    kol_profile=kol_profile,
                    posting_type=posting_type,
                    stock_name=stock_name,
                    stock_code=stock_code,
                    trigger_type=trigger_type,
                    serper_data=serper_analysis,
                    max_words=max_words
                )
                self.logger.info(f"🎲 隨機化生成器調用成功，結果: {type(random_result)}")
            except Exception as e:
                self.logger.error(f"❌ 隨機化生成器調用失敗: {e}")
                # 回退到基本處理
                return standard_title, standard_content, {}
            
            # 獲取選中的版本
            selected_version = random_result['selected_version']
            alternative_versions = random_result['alternative_versions']
            generation_metadata = random_result['generation_metadata']
            
            personalized_title = selected_version['title']
            personalized_content = selected_version['content']
            
            # 7. 整合新聞來源
            if serper_analysis:
                personalized_content = self._integrate_news_sources(
                    personalized_content, serper_analysis, kol_profile
                )

            # 🔇 SIMPLIFIED: Single line summary instead of 6 verbose output logs
            self.logger.info(f"✅ 完成: {personalized_title[:40]}... ({len(personalized_content)}字, {len(alternative_versions)}個替代版本)")
            
            # 返回隨機化元數據
            random_metadata = {
                'alternative_versions': alternative_versions,
                'generation_metadata': generation_metadata
            }
            
            return personalized_title, personalized_content, random_metadata
            
        except Exception as e:
            self.logger.error(f"❌ 增強版個人化處理失敗: {e}")
            return standard_title, standard_content, {}
    
    def resolve_content_length_with_style(self, kol_profile: KOLProfile, batch_config: Dict, style_type: str) -> str:
        """根據發文形態決定內容長度"""
        
        if style_type == "question":
            # 疑問句類型：強制100字以下
            self.logger.info("❓ 疑問句類型，強制使用短內容 (100字以下)")
            return "short"
        else:
            # 發表看法：使用KOL的機率分布或Batch設定
            if hasattr(kol_profile, 'content_length_probabilities') and kol_profile.content_length_probabilities:
                # 使用KOL的機率分布隨機選擇
                return self.random_select_by_probability(kol_profile.content_length_probabilities)
            else:
                # 使用Batch設定
                return batch_config.get('content_length', 'medium')
    
    def random_select_by_probability(self, probability_distribution: Dict[str, float]) -> str:
        """根據機率分布隨機選擇"""
        import random
        
        # 生成隨機數
        rand = random.random()
        cumulative = 0.0
        
        # 按機率累積選擇
        for option, probability in probability_distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return option
        
        # 如果沒有匹配，返回第一個選項
        return list(probability_distribution.keys())[0]
    
    def _integrate_news_sources(self, content: str, serper_analysis: Dict, kol_profile: KOLProfile) -> str:
        """整合新聞來源到個人化內容中 - 避免重複添加"""
        try:
            # 檢查內容中是否已經有新聞來源
            if "新聞來源:" in content or "📰 新聞來源:" in content:
                self.logger.info("⚠️ 內容中已包含新聞來源，跳過重複添加")
                return content
            
            news_items = serper_analysis.get('news_items', [])
            if not news_items:
                return content
            
            self.logger.info(f"📰 開始整合 {len(news_items)} 則新聞來源")
            
            # 根據KOL風格調整新聞來源格式
            news_sources = []
            # 從 serper_analysis 獲取新聞連結配置
            news_max_links = serper_analysis.get('news_max_links', 5)
            enable_news_links = serper_analysis.get('enable_news_links', True)
            
            if not enable_news_links:
                self.logger.info("⚠️ 新聞連結已停用，跳過新聞來源整合")
                return content
            
            for i, news in enumerate(news_items[:news_max_links]):  # 根據配置取新聞數量
                title = news.get('title', '')
                link = news.get('link', '')
                snippet = news.get('snippet', '')
                
                if title:
                    # 根據KOL風格調整格式
                    if hasattr(kol_profile, 'tone_style') and 'casual' in str(kol_profile.tone_style).lower():
                        # 輕鬆風格：簡化格式
                        if link:
                            news_sources.append(f"{i+1}. {title}\n   🔗 {link}")
                        else:
                            news_sources.append(f"{i+1}. {title}")
                    else:
                        # 專業風格：完整格式
                        if link:
                            news_sources.append(f"{i+1}. {title}\n   連結: {link}")
                        else:
                            news_sources.append(f"{i+1}. {title}")
            
            if news_sources:
                # 根據KOL風格調整標題
                if hasattr(kol_profile, 'tone_style') and 'casual' in str(kol_profile.tone_style).lower():
                    sources_section = "\n\n📰 新聞來源:\n" + "\n".join(news_sources)
                else:
                    sources_section = "\n\n新聞來源:\n" + "\n".join(news_sources)
                
                self.logger.info(f"✅ 新聞來源整合完成: {len(sources_section)} 字")
                return content + sources_section
            
            return content
            
        except Exception as e:
            self.logger.error(f"❌ 新聞來源整合失敗: {e}")
            return content
    
    def simulate_personalization(self, standard_title: str, standard_content: str, 
                                kol_profile: KOLProfile, style_type: str) -> Tuple[str, str]:
        """動態個人化處理 - 完全基於KOL欄位"""
        
        self.logger.info(f"🎭 開始動態個人化 - KOL: {kol_profile.serial}")
        self.logger.info(f"🎭 發文形態: {style_type}")
        self.logger.info(f"🎭 原始標題: {standard_title}")
        self.logger.info(f"🎭 原始內容長度: {len(standard_content)} 字")
        
        # 1. 根據KOL機率分布動態選擇內容風格
        content_style = self._select_dynamic_content_style(kol_profile)
        self.logger.info(f"🎯 動態選擇的內容風格: {content_style}")
        
        # 2. 根據KOL機率分布動態選擇分析深度
        analysis_depth = self._select_dynamic_analysis_depth(kol_profile)
        self.logger.info(f"🎯 動態選擇的分析深度: {analysis_depth}")
        
        # 3. 根據KOL機率分布動態選擇內容長度
        content_length = self._select_dynamic_content_length(kol_profile)
        self.logger.info(f"🎯 動態選擇的內容長度: {content_length}")
        
        # 4. 根據KOL設定動態生成內容結構
        personalized_content = self._generate_dynamic_content_structure(
            standard_content, kol_profile, content_style, analysis_depth
        )
        
        # 5. 根據KOL設定動態應用語調控制
        style_params = {"tone_confidence": kol_profile.tone_confidence or 7}
        personalized_content = self._apply_dynamic_tone_control(
            personalized_content, kol_profile, style_params
        )
        
        # 6. 根據KOL設定動態應用互動元素
        personalized_content = self._apply_dynamic_interaction_elements(
            personalized_content, kol_profile, style_type
        )
        
        # 7. 根據KOL設定動態應用標籤與簽名
        personalized_content = self._apply_dynamic_tags_and_signature(
            personalized_content, kol_profile
        )
        
        # 8. 根據動態選擇的內容長度調整內容
        personalized_content = self._adjust_dynamic_content_length(personalized_content, content_length)
        
        # 9. 根據動態選擇的分析深度調整內容
        personalized_content = self._adjust_dynamic_analysis_depth(personalized_content, analysis_depth)
        
        # 10. 動態生成標題
        personalized_title = self._generate_dynamic_title_from_content(
            personalized_content, kol_profile, standard_title
        )
        
        self.logger.info(f"🎭 動態個人化完成 - 標題: {personalized_title}")
        self.logger.info(f"🎭 動態個人化完成 - 內容長度: {len(personalized_content)} 字")
        self.logger.info(f"🎭 動態個人化完成 - 內容前100字: {personalized_content[:100]}...")
        
        return personalized_title, personalized_content
    
    def _generate_dynamic_title_from_content(self, content: str, kol_profile: KOLProfile, standard_title: str) -> str:
        """根據內容動態生成標題"""
        
        # 1. 從標準標題中提取股票名稱
        stock_name = self._extract_stock_name_from_title(standard_title)
        
        # 2. 使用KOL的標題風格設定
        title_openers = kol_profile.title_openers or ["", "注意！", "重點！", "最新！", "今天！"]
        opener = random.choice(title_openers) if title_openers else ""
        
        title_signature_patterns = kol_profile.title_signature_patterns or ["{stock}分析", "{stock}觀察", "{stock}聊聊"]
        pattern = random.choice(title_signature_patterns) if title_signature_patterns else "{stock}分析"
        
        title_tail_word = kol_profile.title_tail_word or ""
        
        # 3. 基於內容摘要生成標題
        title = self._generate_summary_based_title(content, stock_name, opener, pattern, title_tail_word, kol_profile)
        
        return title
    
    def _select_content_style(self, kol_profile: KOLProfile) -> str:
        """根據KOL機率分布選擇內容風格"""
        try:
            if hasattr(kol_profile, 'content_style_probabilities') and kol_profile.content_style_probabilities:
                return self.random_select_by_probability(kol_profile.content_style_probabilities)
            else:
                # 預設機率分布
                default_probs = {
                    "technical": 0.3,
                    "casual": 0.4,
                    "professional": 0.2,
                    "humorous": 0.1
                }
                return self.random_select_by_probability(default_probs)
        except Exception as e:
            self.logger.error(f"❌ 選擇內容風格失敗: {e}")
            return "casual"
    
    def _select_analysis_depth(self, kol_profile: KOLProfile) -> str:
        """根據KOL機率分布選擇分析深度"""
        try:
            if hasattr(kol_profile, 'analysis_depth_probabilities') and kol_profile.analysis_depth_probabilities:
                return self.random_select_by_probability(kol_profile.analysis_depth_probabilities)
            else:
                # 預設機率分布
                default_probs = {
                    "basic": 0.2,
                    "detailed": 0.5,
                    "comprehensive": 0.3
                }
                return self.random_select_by_probability(default_probs)
        except Exception as e:
            self.logger.error(f"❌ 選擇分析深度失敗: {e}")
            return "detailed"
    
    def _select_content_length(self, kol_profile: KOLProfile) -> str:
        """根據KOL機率分布選擇內容長度"""
        try:
            if hasattr(kol_profile, 'content_length_probabilities') and kol_profile.content_length_probabilities:
                return self.random_select_by_probability(kol_profile.content_length_probabilities)
            else:
                # 預設機率分布
                default_probs = {
                    "short": 0.1,
                    "medium": 0.4,
                    "long": 0.3,
                    "extended": 0.15,
                    "comprehensive": 0.05,
                    "thorough": 0.0
                }
                return self.random_select_by_probability(default_probs)
        except Exception as e:
            self.logger.error(f"❌ 選擇內容長度失敗: {e}")
            return "medium"
    
    def _adjust_content_length(self, content: str, length_type: str) -> str:
        """根據內容長度類型調整內容"""
        if length_type == "short":
            # 縮短內容，保留核心信息
            sentences = content.split('。')
            return '。'.join(sentences[:3]) + '。'
        elif length_type == "long":
            # 擴展內容，添加更多細節
            return content + "\n\n詳細分析顯示技術指標變化，成交量配合情況，後市展望需要持續觀察"
        elif length_type == "extended":
            # 大幅擴展內容
            return content + "\n\n深度解析顯示技術面指標變化，基本面營收表現，籌碼面法人動向，後市展望需要持續觀察"
        else:
            return content
    
    def _adjust_analysis_depth(self, content: str, depth_type: str) -> str:
        """根據分析深度調整內容"""
        if depth_type == "basic":
            # 基礎分析，簡化內容
            return content.replace("技術指標分析：", "技術面：").replace("基本面分析：", "基本面：")
        elif depth_type == "comprehensive":
            # 全面分析，添加更多維度
            return content + "\n\n🔍 綜合評估：\n• 風險等級：中等\n• 投資建議：謹慎樂觀\n• 停損點位：建議設定"
        else:
            return content
    
    def _adjust_content_style(self, content: str, style_type: str) -> str:
        """根據內容風格調整內容"""
        if style_type == "casual":
            # 輕鬆風格，添加口語化表達
            return content.replace("分析", "聊聊").replace("建議", "覺得")
        elif style_type == "humorous":
            # 幽默風格，添加輕鬆元素
            return content + "\n\n😄 輕鬆一下：市場就像天氣，變化無常但總有規律！"
        elif style_type == "professional":
            # 專業風格，使用更正式的用詞
            return content.replace("聊聊", "分析").replace("覺得", "建議")
        else:
            return content

    def _generate_enhanced_personalized_content(self, standard_content: str, kol_profile: KOLProfile, style_type: str, style_params: Dict, content_length: str) -> str:
        """增強版個人化內容生成 - 完全動態化"""
        
        self.logger.info(f"🎭 開始動態個人化內容生成 - KOL: {kol_profile.serial}")
        
        # 1. 根據KOL機率分布動態選擇內容風格
        content_style = self._select_dynamic_content_style(kol_profile)
        self.logger.info(f"🎯 動態選擇的內容風格: {content_style}")
        
        # 2. 根據KOL機率分布動態選擇分析深度
        analysis_depth = self._select_dynamic_analysis_depth(kol_profile)
        self.logger.info(f"🎯 動態選擇的分析深度: {analysis_depth}")
        
        # 3. 根據KOL機率分布動態選擇內容長度
        selected_length = self._select_dynamic_content_length(kol_profile)
        self.logger.info(f"🎯 動態選擇的內容長度: {selected_length}")
        
        # 4. 根據KOL設定動態生成內容結構
        personalized_content = self._generate_dynamic_content_structure(
            standard_content, kol_profile, content_style, analysis_depth
        )
        
        # 5. 根據KOL設定動態應用語調控制
        personalized_content = self._apply_dynamic_tone_control(
            personalized_content, kol_profile, style_params
        )
        
        # 6. 根據KOL設定動態應用互動元素
        personalized_content = self._apply_dynamic_interaction_elements(
            personalized_content, kol_profile, style_type
        )
        
        # 7. 根據KOL設定動態應用標籤與簽名
        personalized_content = self._apply_dynamic_tags_and_signature(
            personalized_content, kol_profile
        )
        
        # 8. 根據動態選擇的內容長度調整內容
        personalized_content = self._adjust_dynamic_content_length(personalized_content, selected_length)
        
        # 9. 根據動態選擇的分析深度調整內容
        personalized_content = self._adjust_dynamic_analysis_depth(personalized_content, analysis_depth)
        
        # 10. 根據KOL的模型設定調整內容
        personalized_content = self._apply_model_specific_settings(personalized_content, kol_profile)
        
        # 11. 根據KOL的人設動態調整內容
        personalized_content = self._apply_persona_specific_logic(personalized_content, kol_profile)
        
        self.logger.info(f"🎭 動態個人化內容完成 - 長度: {len(personalized_content)} 字")
        return personalized_content
    
    def _generate_title_from_final_content(self, content: str, kol_profile: KOLProfile, standard_title: str, trigger_type: str = None) -> str:
        """基於最終內容生成標題 - 使用內容摘要方式"""
        
        self.logger.info(f"📝 開始基於最終內容摘要生成標題")
        
        # 1. 從內容中提取股票名稱
        stock_name = self._extract_stock_name_from_title(standard_title)
        
        # 2. 使用KOL的標題風格設定
        title_openers = kol_profile.title_openers or ["", "注意！", "重點！", "最新！", "今天！"]
        opener = random.choice(title_openers) if title_openers else ""
        
        title_signature_patterns = kol_profile.title_signature_patterns or ["{stock}分析", "{stock}觀察", "{stock}聊聊"]
        pattern = random.choice(title_signature_patterns) if title_signature_patterns else "{stock}分析"
        
        title_tail_word = kol_profile.title_tail_word or ""
        
        # 3. 基於內容摘要生成標題
        title = self._generate_summary_based_title(content, stock_name, opener, pattern, title_tail_word, kol_profile)
        
        self.logger.info(f"📝 摘要式標題生成完成: {title}")
        return title
    
    def _generate_summary_based_title(self, content: str, stock_name: str, opener: str, pattern: str, tail_word: str, kol_profile: KOLProfile) -> str:
        """基於內容摘要生成標題 - 完全動態化"""
        
        self.logger.info(f"🎯 開始動態標題生成 - KOL: {kol_profile.serial}")
        
        # 1. 分析內容的核心重點
        summary_keywords = self._extract_content_summary(content)
        
        # 2. 根據KOL的機率分布動態選擇標題風格
        title_style = self._select_dynamic_title_style(kol_profile, content)
        self.logger.info(f"🎯 選擇的標題風格: {title_style}")
        
        # 3. 根據KOL的常用術語動態生成核心詞彙
        core_phrase = self._generate_dynamic_core_phrase(kol_profile, content, title_style)
        self.logger.info(f"🎯 生成的核心詞彙: {core_phrase}")
        
        # 4. 根據KOL的標題風格設定動態組合標題
        title = self._combine_dynamic_title(stock_name, opener, pattern, core_phrase, tail_word, kol_profile)
        
        self.logger.info(f"🎯 動態標題生成完成: {title}")
        return title
    
    def _extract_content_summary(self, content: str) -> List[str]:
        """從內容中提取摘要關鍵詞"""
        
        keywords = []
        
        # 檢查主要趨勢
        if "漲停" in content:
            keywords.append("漲停")
        if "突破" in content:
            keywords.append("突破")
        if "支撐" in content:
            keywords.append("支撐")
        if "阻力" in content:
            keywords.append("阻力")
        if "爆量" in content:
            keywords.append("爆量")
        if "強勢" in content:
            keywords.append("強勢")
            
        # 檢查基本面關鍵詞
        if "營收" in content:
            keywords.append("營收")
        if "獲利" in content:
            keywords.append("獲利")
        if "財報" in content:
            keywords.append("財報")
            
        # 檢查技術面關鍵詞
        if "技術面" in content:
            keywords.append("技術面")
        if "K線" in content:
            keywords.append("K線")
        if "均線" in content:
            keywords.append("均線")
        if "RSI" in content:
            keywords.append("RSI")
            
        self.logger.info(f"🔍 提取的摘要關鍵詞: {keywords}")
        return keywords
    
    def _analyze_content_highlights(self, content: str) -> Dict[str, Any]:
        """分析內容重點"""
        
        # 簡單的關鍵詞分析
        content_lower = content.lower()
        
        analysis = {
            "main_trend": None,
            "key_factors": [],
            "specific_data": [],
            "sentiment": "neutral",
            "urgency": "medium"
        }
        
        # 檢查主要趨勢
        if any(keyword in content for keyword in ["漲停", "鎖漲停", "爆量", "強勢上漲", "拉至漲停", "漲停價"]):
            analysis["main_trend"] = "漲停"
            analysis["sentiment"] = "positive"
            self.logger.info(f"🔍 檢測到漲停關鍵詞，設定 main_trend = 漲停")
        elif any(keyword in content for keyword in ["跌停", "重挫", "暴跌", "大幅下跌"]):
            analysis["main_trend"] = "跌停"
            analysis["sentiment"] = "negative"
        elif any(keyword in content for keyword in ["震盪", "整理", "盤整", "區間"]):
            analysis["main_trend"] = "震盪"
        elif any(keyword in content for keyword in ["上漲", "上揚", "走高", "突破"]):
            analysis["main_trend"] = "上漲"
            analysis["sentiment"] = "positive"
        elif any(keyword in content for keyword in ["下跌", "下挫", "走低", "疲弱"]):
            analysis["main_trend"] = "下跌"
            analysis["sentiment"] = "negative"
        
        # 檢查關鍵因素
        if any(keyword in content for keyword in ["技術面", "技術指標", "K線", "均線"]):
            analysis["key_factors"].append("技術面")
        if any(keyword in content for keyword in ["基本面", "營收", "獲利", "財務"]):
            analysis["key_factors"].append("基本面")
        if any(keyword in content for keyword in ["消息面", "新聞", "政策", "題材"]):
            analysis["key_factors"].append("消息面")
        
        return analysis
    
    def _generate_dynamic_title(self, content_analysis: Dict, kol_profile: KOLProfile, standard_title: str, trigger_type: str = None) -> str:
        """動態標題生成 - 基於KOL設定"""
        
        # 使用KOL的標題開場詞
        title_openers = kol_profile.title_openers or ["", "注意！", "重點！"]
        opener = random.choice(title_openers) if title_openers else ""
        
        # 使用KOL的標題簽名模式
        signature_patterns = kol_profile.title_signature_patterns or ["{stock}分析", "{stock}觀察"]
        pattern = random.choice(signature_patterns) if signature_patterns else "{stock}分析"
        
        # 使用KOL的標題結尾詞
        tail_word = kol_profile.title_tail_word or ""
        
        # 根據內容分析結果選擇關鍵詞
        key_highlight = self._extract_key_highlight(content_analysis)
        
        # 從標準標題中提取股票名稱
        stock_name = self._extract_stock_name_from_title(standard_title)
        
        # 動態組合標題
        if opener:
            title = f"{opener}{stock_name} {key_highlight}{tail_word}"
        else:
            title = pattern.format(stock=stock_name).replace("分析", key_highlight)
        
        return title
    
    def _extract_key_highlight(self, content_analysis: Dict) -> str:
        """從內容分析中提取關鍵亮點"""
        
        # 根據內容分析結果動態選擇關鍵詞
        if content_analysis.get("main_trend") == "漲停":
            self.logger.info(f"🎯 檢測到漲停，返回強勢突破")
            return "強勢突破"
        elif content_analysis.get("main_trend") == "跌停":
            return "技術轉弱"
        elif content_analysis.get("main_trend") == "震盪":
            return "震盪整理"
        elif content_analysis.get("key_factors"):
            # 如果有重要因素，突出因素
            if "技術面" in content_analysis["key_factors"]:
                return "技術分析"
            elif "基本面" in content_analysis["key_factors"]:
                return "基本面分析"
            else:
                return "深度分析"
        else:
            self.logger.info(f"⚠️ 未檢測到特殊趨勢，返回預設盤後分析")
            return "盤後分析"
    
    def _extract_stock_name_from_title(self, title: str) -> str:
        """從標題中提取股票名稱"""
        
        # 簡單的股票名稱提取邏輯
        import re
        
        self.logger.info(f"🔍 提取股票名稱 - 輸入標題: {title}")
        
        # 匹配股票名稱模式
        patterns = [
            r'【.*?】(.+?)\(',  # 【KOL-200】第一銅(
            r'(.+?)\(',         # 第一銅(
            r'【.*?】(.+?)$',   # 【KOL-200】第一銅
            r'^(.+?)\s+',       # 嘉鋼 分析
            r'^(.+?)$',         # 嘉鋼
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                stock_name = match.group(1).strip()
                self.logger.info(f"🔍 提取到股票名稱: {stock_name}")
                return stock_name
        
        self.logger.warning(f"⚠️ 無法提取股票名稱，使用預設值")
        return "台股"
    
    def _apply_content_style_personalization(self, content: str, kol_profile: KOLProfile, content_style: str) -> str:
        """應用內容風格個人化"""
        
        if content_style == "technical":
            # 技術風格：使用技術術語
            if kol_profile.common_terms:
                terms = kol_profile.common_terms.split(',')
                for term in terms[:3]:  # 使用前3個術語
                    content = content.replace("分析", f"{term.strip()}分析")
        elif content_style == "casual":
            # 輕鬆風格：使用口語化用詞
            if kol_profile.colloquial_terms:
                terms = kol_profile.colloquial_terms.split(',')
                for term in terms[:2]:  # 使用前2個口語化用詞
                    content = content.replace("股票", f"{term.strip()}")
        elif content_style == "professional":
            # 專業風格：保持專業用詞
            pass  # 保持原樣
        
        return content
    
    def _apply_tone_control_personalization(self, content: str, kol_profile: KOLProfile, style_params: Dict) -> str:
        """應用語調控制個人化"""
        
        # 根據語調設定調整內容
        tone_formal = kol_profile.tone_formal or 7
        tone_emotion = kol_profile.tone_emotion or 5
        tone_confidence = style_params.get('tone_confidence', kol_profile.tone_confidence or 7)
        
        # 正式程度調整
        if tone_formal >= 8:
            # 高正式度：使用正式用詞
            content = content.replace("很", "相當")
            content = content.replace("非常", "極其")
        elif tone_formal <= 4:
            # 低正式度：使用輕鬆用詞
            content = content.replace("相當", "很")
            content = content.replace("極其", "非常")
        
        # 情感強度調整
        if tone_emotion >= 7:
            # 高情感度：添加情感詞彙
            if "強勢" in content:
                content = content.replace("強勢", "強勢突破")
        elif tone_emotion <= 3:
            # 低情感度：使用中性詞彙
            content = content.replace("強勢突破", "穩健上漲")
        
        return content
    
    def _apply_interaction_elements_personalization(self, content: str, kol_profile: KOLProfile, style_type: str) -> str:
        """應用互動元素個人化"""
        
        if style_type == "question":
            # 提問風格：添加互動元素
            if kol_profile.interaction_starters:
                starter = random.choice(kol_profile.interaction_starters)
                content = f"{content}\n\n{starter}"
            else:
                content = f"{content}\n\n大家怎麼看？"
        
        # 根據幽默機率添加幽默元素
        humor_probability = getattr(kol_profile, 'humor_probability', 0.2)
        if random.random() < humor_probability:
            humor_endings = ["😄 輕鬆一下：市場就像天氣，變化無常！", "😊 投資有風險，請謹慎評估！"]
            content = f"{content}\n\n{random.choice(humor_endings)}"
        
        return content
    
    def _apply_tags_and_signature_personalization(self, content: str, kol_profile: KOLProfile) -> str:
        """應用標籤與簽名個人化"""
        
        # 🔥 修復：完全移除標籤、簽名和CTA添加，避免重複和hashtag問題
        # 不添加任何標籤、簽名和CTA，保持內容自然
        
        return content
    
    def _select_dynamic_title_style(self, kol_profile: KOLProfile, content: str) -> str:
        """根據KOL機率分布動態選擇標題風格"""
        
        # 使用KOL的內容風格機率分布
        if hasattr(kol_profile, 'content_style_probabilities') and kol_profile.content_style_probabilities:
            return self.random_select_by_probability(kol_profile.content_style_probabilities)
        else:
            # 預設機率分布
            default_probs = {
                "technical": 0.3,
                "casual": 0.4, 
                "professional": 0.2,
                "humorous": 0.1
            }
            return self.random_select_by_probability(default_probs)
    
    def _generate_dynamic_core_phrase(self, kol_profile: KOLProfile, content: str, title_style: str) -> str:
        """根據KOL設定動態生成核心詞彙 - 避免聳動性用詞"""
        
        # 1. 根據KOL的常用術語生成詞彙庫
        common_terms = []
        if kol_profile.common_terms:
            common_terms = [term.strip() for term in kol_profile.common_terms.split(',') if term.strip()]
        
        # 2. 根據KOL的口語化用詞生成詞彙庫
        colloquial_terms = []
        if kol_profile.colloquial_terms:
            colloquial_terms = [term.strip() for term in kol_profile.colloquial_terms.split(',') if term.strip()]
        
        # 3. 根據內容分析結果選擇詞彙 - 使用中性、客觀的用詞
        if "漲停" in content:
            if title_style == "technical":
                phrases = ["技術面分析", "量價觀察", "指標解析"] + common_terms
            elif title_style == "casual":
                phrases = ["盤後觀察", "市場動態", "走勢分析"] + colloquial_terms
            elif title_style == "professional":
                phrases = ["盤後分析", "市場觀察", "走勢解析"] + common_terms
            else:  # humorous
                phrases = ["盤後聊聊", "市場觀察", "走勢討論"] + colloquial_terms
        elif "突破" in content:
            if title_style == "technical":
                phrases = ["技術面觀察", "關鍵位分析", "趨勢判斷"] + common_terms
            elif title_style == "casual":
                phrases = ["走勢分析", "技術觀察", "市場動態"] + colloquial_terms
            else:
                phrases = ["技術分析", "走勢解析", "市場觀察"] + common_terms
        else:
            if title_style == "technical":
                phrases = ["技術分析", "指標觀察", "趨勢分析"] + common_terms
            elif title_style == "casual":
                phrases = ["盤後聊聊", "市場觀察", "走勢討論"] + colloquial_terms
            elif title_style == "professional":
                phrases = ["盤後分析", "市場解析", "專業觀點"] + common_terms
            else:  # humorous
                phrases = ["輕鬆聊聊", "市場觀察", "投資心得"] + colloquial_terms
        
        # 4. 隨機選擇一個詞彙
        if phrases:
            return random.choice(phrases)
        else:
            return "分析"
    
    def _combine_dynamic_title(self, stock_name: str, opener: str, pattern: str, core_phrase: str, tail_word: str, kol_profile: KOLProfile) -> str:
        """根據KOL設定動態組合標題 - 避免聳動性標題"""
        
        # 1. 過濾過於興奮的開場詞
        if opener and opener in ["快報！", "突發！", "重點！", "笑死！", "太神了！", "跪了！", "推爆！"]:
            # 替換為中性開場詞
            neutral_openers = ["", "盤後", "觀察", "分析"]
            opener = random.choice(neutral_openers)
        
        # 2. 根據KOL的標題風格設定選擇組合方式
        if hasattr(kol_profile, 'title_style_examples') and kol_profile.title_style_examples:
            # 使用KOL的標題範例作為模板，但過濾聳動性用詞
            template = random.choice(kol_profile.title_style_examples)
            title = template.replace("{stock}", stock_name).replace("{phrase}", core_phrase)
        else:
            # 使用預設組合邏輯
            if opener:
                title = f"{opener}{stock_name} {core_phrase}{tail_word}"
            else:
                # 使用pattern但替換核心詞彙
                title = pattern.format(stock=stock_name).replace("分析", core_phrase).replace("觀察", core_phrase).replace("聊聊", core_phrase) + tail_word
        
        # 3. 檢查禁用詞彙
        if hasattr(kol_profile, 'title_banned_words') and kol_profile.title_banned_words:
            for banned_word in kol_profile.title_banned_words:
                if banned_word in title:
                    # 替換禁用詞彙
                    title = title.replace(banned_word, "分析")
        
        # 4. 過濾聳動性用詞
        sensational_words = ["強勢突破", "爆量上攻", "衝高", "強勢上漲", "突破性上漲", "量價齊揚"]
        for word in sensational_words:
            if word in title:
                title = title.replace(word, "盤後分析")
        
        return title
    
    def _select_dynamic_content_style(self, kol_profile: KOLProfile) -> str:
        """根據KOL機率分布動態選擇內容風格"""
        return self._select_content_style(kol_profile)
    
    def _select_dynamic_analysis_depth(self, kol_profile: KOLProfile) -> str:
        """根據KOL機率分布動態選擇分析深度"""
        return self._select_analysis_depth(kol_profile)
    
    def _select_dynamic_content_length(self, kol_profile: KOLProfile) -> str:
        """根據KOL機率分布動態選擇內容長度"""
        return self._select_content_length(kol_profile)
    
    def _generate_dynamic_content_structure(self, standard_content: str, kol_profile: KOLProfile, content_style: str, analysis_depth: str) -> str:
        """根據KOL設定動態生成內容結構 - 完全基於KOL欄位"""
        
        # 1. 根據KOL的常用術語動態替換內容
        if kol_profile.common_terms:
            terms = [term.strip() for term in kol_profile.common_terms.split(',') if term.strip()]
            for term in terms[:3]:  # 使用前3個術語
                if term in standard_content:
                    # 根據內容風格選擇替換方式
                    if content_style == "casual":
                        standard_content = standard_content.replace(term, f"{term}聊聊")
                    elif content_style == "technical":
                        standard_content = standard_content.replace(term, f"{term}技術分析")
                    elif content_style == "professional":
                        standard_content = standard_content.replace(term, f"{term}專業解析")
        
        # 2. 根據KOL的口語化用詞動態替換內容
        if kol_profile.colloquial_terms:
            terms = [term.strip() for term in kol_profile.colloquial_terms.split(',') if term.strip()]
            for term in terms[:2]:  # 使用前2個口語化用詞
                if content_style == "casual":
                    standard_content = standard_content.replace("股票", term)
                    standard_content = standard_content.replace("分析", f"{term}分析")
        
        # 3. 根據KOL的語調風格動態調整內容
        if kol_profile.tone_style:
            tone_style = kol_profile.tone_style.lower()
            if "輕鬆" in tone_style or "casual" in tone_style:
                standard_content = standard_content.replace("分析", "聊聊").replace("建議", "覺得")
            elif "專業" in tone_style or "professional" in tone_style:
                standard_content = standard_content.replace("聊聊", "分析").replace("覺得", "建議")
            elif "幽默" in tone_style or "humorous" in tone_style:
                standard_content = standard_content.replace("分析", "輕鬆聊聊")
        
        # 4. 根據KOL的目標受眾調整內容
        if kol_profile.target_audience:
            if "active_traders" in kol_profile.target_audience:
                standard_content = standard_content.replace("投資", "交易").replace("長期", "短線")
            elif "long_term_investors" in kol_profile.target_audience:
                standard_content = standard_content.replace("交易", "投資").replace("短線", "長期")
        
        # 5. 根據KOL的內容類型偏好調整
        if kol_profile.content_types:
            if "technical_analysis" in kol_profile.content_types:
                standard_content = standard_content.replace("基本面", "技術面").replace("財報", "指標")
            elif "fundamental_analysis" in kol_profile.content_types:
                standard_content = standard_content.replace("技術面", "基本面").replace("指標", "財報")
        
        # 6. 根據KOL的數據來源偏好調整
        if kol_profile.data_source:
            if "technical_indicators" in kol_profile.data_source:
                standard_content = standard_content.replace("消息面", "技術指標")
            elif "news_analysis" in kol_profile.data_source:
                standard_content = standard_content.replace("技術面", "新聞面")
        
        return standard_content
    
    def _apply_dynamic_tone_control(self, content: str, kol_profile: KOLProfile, style_params: Dict) -> str:
        """根據KOL設定動態應用語調控制 - 避免聳動性內容"""
        
        # 1. 根據KOL的語調設定動態調整
        tone_formal = kol_profile.tone_formal or 7
        tone_emotion = kol_profile.tone_emotion or 5
        tone_confidence = style_params.get('tone_confidence', kol_profile.tone_confidence or 7)
        
        # 2. 動態調整正式程度
        if tone_formal >= 8:
            # 高正式度：使用正式用詞
            content = content.replace("很", "相當").replace("非常", "極其").replace("超", "極度")
        elif tone_formal <= 4:
            # 低正式度：使用輕鬆用詞
            content = content.replace("相當", "很").replace("極其", "非常").replace("極度", "超")
        
        # 3. 動態調整情感強度 - 避免過度興奮
        if tone_emotion >= 7:
            # 高情感度：使用中性情感詞彙
            content = content.replace("強勢", "穩健").replace("上漲", "上揚")
        elif tone_emotion <= 3:
            # 低情感度：使用中性詞彙
            content = content.replace("強勢突破", "穩健上漲").replace("強勢上漲", "溫和上漲")
        
        # 4. 動態調整自信程度
        if tone_confidence >= 8:
            # 高自信度：使用謹慎肯定詞彙
            content = content.replace("可能", "預期").replace("或許", "有望")
        elif tone_confidence <= 4:
            # 低自信度：使用謹慎詞彙
            content = content.replace("將", "可能").replace("必定", "或許")
        
        # 5. 過濾聳動性用詞
        sensational_words = ["強勢突破", "爆量上攻", "衝高", "強勢上漲", "突破性上漲", "量價齊揚", "強勢表現"]
        for word in sensational_words:
            if word in content:
                content = content.replace(word, "穩健表現")
        
        return content
    
    def _apply_dynamic_interaction_elements(self, content: str, kol_profile: KOLProfile, style_type: str) -> str:
        """根據KOL設定動態應用互動元素 - 完全基於KOL欄位"""
        
        # 1. 根據發文形態動態添加互動元素
        if style_type == "question":
            # 提問風格：動態選擇互動開場白
            if kol_profile.interaction_starters:
                starter = random.choice(kol_profile.interaction_starters)
                content = f"{content}\n\n{starter}"
            else:
                # 根據KOL的語調風格選擇提問方式
                if kol_profile.tone_style and "輕鬆" in kol_profile.tone_style:
                    content = f"{content}\n\n大家怎麼看？"
                elif kol_profile.tone_style and "專業" in kol_profile.tone_style:
                    content = f"{content}\n\n歡迎討論交流"
                else:
                    content = f"{content}\n\n你覺得呢？"
        
        # 2. 根據KOL的幽默機率動態添加幽默元素
        humor_probability = getattr(kol_profile, 'humor_probability', 0.2)
        if random.random() < humor_probability and getattr(kol_profile, 'humor_enabled', True):
            # 根據KOL的語調風格選擇幽默元素
            if kol_profile.tone_style and "輕鬆" in kol_profile.tone_style:
                humor_endings = ["輕鬆一下：市場就像天氣，變化無常！", "投資有風險，請謹慎評估！"]
            elif kol_profile.tone_style and "專業" in kol_profile.tone_style:
                humor_endings = ["專業分析，僅供參考", "投資建議，謹慎評估"]
            else:
                humor_endings = ["輕鬆一下：市場就像天氣，變化無常但總有規律！", "投資有風險，請謹慎評估！"]
            
            content = f"{content}\n\n{random.choice(humor_endings)}"
        
        # 3. 根據KOL的互動閾值調整互動強度
        if kol_profile.interaction_threshold:
            if kol_profile.interaction_threshold > 0.7:
                # 高互動閾值：增加互動元素
                content = f"{content}\n\n歡迎分享你的看法！"
            elif kol_profile.interaction_threshold < 0.3:
                # 低互動閾值：減少互動元素
                pass  # 保持原樣
        
        # 🔥 修復4: 移除所有 emoji 使用，確保內容看起來更自然
        # 不添加任何 emoji，讓內容看起來更自然
        
        return content
    
    def _apply_dynamic_tags_and_signature(self, content: str, kol_profile: KOLProfile) -> str:
        """根據KOL設定動態應用標籤與簽名 - 完全基於KOL欄位"""
        
        # 🔥 修復1: 移除所有可能的簽名檔，避免重複
        import re
        
        # 檢查各種可能的簽名格式並移除
        possible_signatures = [
            kol_profile.signature.strip() if kol_profile.signature else "",
            f"📊 {kol_profile.nickname} - 技術分析",
            f"📊 {kol_profile.nickname} - 技術分析\n\n技術分析僅供參考，投資有風險，請謹慎決策。",
            f"😂 {kol_profile.nickname} - 鄉民觀點",
            f"😂 {kol_profile.nickname} - 鄉民觀點\n\n鄉民觀點僅供娛樂，投資請理性思考。",
            f"📰 {kol_profile.nickname} - 新聞快報",
            f"📰 {kol_profile.nickname} - 新聞快報\n\n消息僅供參考，投資決策請自行判斷。",
        ]
        
        # 移除所有可能的簽名檔
        for sig in possible_signatures:
            if sig and sig in content:
                content = content.replace(sig, '')
                self.logger.info(f"⚠️ 移除重複簽名檔: {sig}")
        
        # 移除重複的簽名模式
        signature_patterns = [
            r'😂\s*板橋大who\s*-\s*鄉民觀點.*?鄉民觀點僅供娛樂，投資請理性思考。',
            r'📊\s*[^-\n]+\s*-\s*技術分析.*?技術分析僅供參考，投資有風險，請謹慎決策。',
            r'📰\s*[^-\n]+\s*-\s*新聞快報.*?消息僅供參考，投資決策請自行判斷。',
        ]
        
        for pattern in signature_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 🔥 修復2: 移除所有 hashtag，確保內容看起來更自然
        # 移除所有hashtag模式
        import re
        # 更強力的hashtag移除模式
        hashtag_patterns = [
            r'#[\w\u4e00-\u9fff]+(?:\s+#[\w\u4e00-\u9fff]+)*',  # 標準hashtag
            r'#[\w\u4e00-\u9fff]+',  # 單個hashtag
            r'#鄉民觀點\s*#PTT\s*#股市討論\s*#幽默分析',  # 特定的hashtag組合
            r'#[\w\u4e00-\u9fff]+\s*#[\w\u4e00-\u9fff]+',  # 多個hashtag
        ]
        
        for pattern in hashtag_patterns:
            content = re.sub(pattern, '', content)
        
        # 清理多餘的空格和換行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # 移除多餘的換行
        content = re.sub(r' +', ' ', content)  # 移除多餘的空格
        
        # 🔥 修復3: 只添加一次簽名檔，且不添加任何簽名
        # 完全移除簽名添加邏輯，避免重複
        
        # 🔥 修復4: 簡化結尾，避免過多結構化內容
        # 移除過多的結構化結尾，保持自然
        
        return content
    
    def _adjust_dynamic_content_length(self, content: str, length_type: str) -> str:
        """根據動態選擇的內容長度調整內容"""
        return self._adjust_content_length(content, length_type)
    
    def _adjust_dynamic_analysis_depth(self, content: str, depth_type: str) -> str:
        """根據動態選擇的分析深度調整內容"""
        return self._adjust_analysis_depth(content, depth_type)
    
    def _apply_model_specific_settings(self, content: str, kol_profile: KOLProfile) -> str:
        """根據KOL的模型設定調整內容"""
        
        # 1. 根據模型溫度調整內容風格
        if kol_profile.model_temp:
            if kol_profile.model_temp > 0.8:
                # 高溫度：增加創意和變化
                content = content.replace("分析", "創意分析").replace("觀察", "獨特觀察")
            elif kol_profile.model_temp < 0.3:
                # 低溫度：保持穩定和一致
                content = content.replace("創意分析", "分析").replace("獨特觀察", "觀察")
        
        # 2. 根據最大token數調整內容長度
        if kol_profile.max_tokens:
            if kol_profile.max_tokens < 500:
                # 短內容：精簡表達
                sentences = content.split('。')
                content = '。'.join(sentences[:2]) + '。'
            elif kol_profile.max_tokens > 2000:
                # 長內容：可以擴展
                pass  # 保持原樣
        
        # 3. 根據模板變體調整內容結構
        if kol_profile.template_variant:
            if "detailed" in kol_profile.template_variant:
                content = f"{content}\n\n詳細分析顯示技術指標趨勢變化，基本面支撐情況需要持續觀察"
            elif "concise" in kol_profile.template_variant:
                # 簡潔版本：移除冗長部分
                content = content.split('\n\n')[0]  # 只保留第一段
        
        return content
    
    def _apply_persona_specific_logic(self, content: str, kol_profile: KOLProfile) -> str:
        """根據KOL的人設動態調整內容 - 完全基於KOL欄位"""
        
        # 1. 根據KOL的提示詞人設調整
        if kol_profile.prompt_persona:
            if "analyst" in kol_profile.prompt_persona:
                content = content.replace("聊聊", "分析").replace("覺得", "評估")
            elif "educator" in kol_profile.prompt_persona:
                content = content.replace("分析", "教學分析").replace("觀察", "學習觀察")
            elif "trader" in kol_profile.prompt_persona:
                content = content.replace("投資", "交易").replace("長期", "短線")
        
        # 2. 根據KOL的發文時間偏好調整
        if kol_profile.post_times:
            if "morning" in kol_profile.post_times:
                content = f"🌅 早安！{content}"
            elif "evening" in kol_profile.post_times:
                content = f"🌙 晚安！{content}"
        
        # 3. 根據KOL的內容長度偏好調整
        if kol_profile.content_length:
            if kol_profile.content_length == "short":
                sentences = content.split('。')
                content = '。'.join(sentences[:2]) + '。'
            elif kol_profile.content_length == "long":
                content = f"{content}\n\n📈 延伸分析：\n• 市場趨勢觀察\n• 風險評估建議"
        
            return content

# 創建全局實例
enhanced_personalization_processor = EnhancedPersonalizationProcessor()
