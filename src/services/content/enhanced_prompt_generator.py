"""
增強版個人化 Prompt 生成器
增加隨機性參數，避免 AI 味太重
"""

import random
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .personalized_title_generator import personalized_title_generator
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RandomizationConfig:
    """隨機化配置"""
    tone_randomness: float = 0.3      # 語氣隨機性 (0-1)
    style_randomness: float = 0.4     # 風格隨機性 (0-1)
    structure_randomness: float = 0.2  # 結構隨機性 (0-1)
    emotion_randomness: float = 0.5    # 情緒隨機性 (0-1)
    technical_randomness: float = 0.3   # 技術用詞隨機性 (0-1)

@dataclass
class PersonalityVariant:
    """個性變體"""
    base_personality: str
    mood_modifier: str      # 心情修飾
    energy_level: str       # 能量等級
    focus_style: str        # 專注風格
    interaction_style: str   # 互動風格
    length_strategy: str = "medium"    # 長度策略
    content_format: str = "analysis"   # 內容形式

class EnhancedPromptGenerator:
    """增強版個人化 Prompt 生成器"""
    
    def __init__(self):
        self.randomization_config = RandomizationConfig()
        
        # 定義各種隨機性元素
        self.mood_modifiers = {
            "技術派": {
                "confident": ["很有信心", "篤定", "肯定", "確信"],
                "cautious": ["謹慎觀察", "小心留意", "保守看待", "觀望"],
                "excited": ["超興奮", "很期待", "蓄勢待發", "摩拳擦掌"],
                "analytical": ["冷靜分析", "理性判斷", "客觀評估", "數據說話"]
            },
            "新聞派": {
                "urgent": ["緊急快訊", "重大消息", "爆炸新聞", "震撼彈"],
                "enthusiastic": ["超級興奮", "熱血沸騰", "激動萬分", "high到不行"],
                "gossipy": ["小道消息", "內幕情報", "獨家爆料", "私房話"],
                "dramatic": ["戲劇性發展", "劇情大逆轉", "意外轉折", "驚人變化"]
            },
            "總經派": {
                "scholarly": ["學術角度", "研究觀點", "理論分析", "深度探討"],
                "experienced": ["經驗分享", "老手觀點", "實戰心得", "歷史借鑑"],
                "forward_looking": ["前瞻視野", "長遠規劃", "戰略思維", "未來布局"],
                "pragmatic": ["務實考量", "實用觀點", "現實分析", "可行性評估"]
            }
        }
        
        self.energy_levels = {
            "high": {
                "技術派": ["爆量突破", "火力全開", "勢如破竹", "一飛沖天"],
                "新聞派": ["狂歡模式", "嗨翻天", "瘋狂狀態", "激情四射"],
                "總經派": ["動能強勁", "蓬勃發展", "活力十足", "生機盎然"]
            },
            "medium": {
                "技術派": ["穩健上漲", "溫和突破", "持續攀升", "逐步向上"],
                "新聞派": ["穩定關注", "持續追蹤", "溫和報導", "理性分析"],
                "總經派": ["穩步成長", "平衡發展", "漸進改善", "持續優化"]
            },
            "low": {
                "技術派": ["整理格局", "盤整待變", "蓄勢待發", "暫時休息"],
                "新聞派": ["靜觀其變", "耐心等待", "冷靜觀察", "低調關注"],
                "總經派": ["審慎評估", "保守觀望", "謹慎分析", "穩健考量"]
            }
        }
        
        self.focus_styles = {
            "技術派": ["技術突破點", "關鍵支撐位", "重要阻力線", "黃金交叉點", "背離訊號"],
            "新聞派": ["市場熱點", "資金流向", "投資人情緒", "政策影響", "國際動態"],
            "總經派": ["基本面分析", "產業趨勢", "經濟指標", "政策導向", "長期價值"]
        }
        
        self.interaction_styles = {
            "direct": ["直接告訴你", "明白說吧", "不囉嗦", "簡單講"],
            "questioning": ["你們覺得呢", "大家怎麼看", "有沒有同感", "是不是這樣"],
            "storytelling": ["來說個故事", "分享一下", "舉個例子", "回想起"],
            "advisory": ["建議大家", "提醒各位", "個人認為", "我的看法是"],
            "provocative": ["你們敢嗎", "誰敢跟我一樣", "有膽的舉手", "敢不敢賭一把"],
            "question_based": ["到底該怎麼辦", "你們會怎麼選", "這樣對嗎", "該進場了嗎"],
            "humorous": ["大家可以放心抱著", "我今天出掉了", "反正我是穩穩的", "你們自己看著辦"],
            "sarcastic": ["呵呵，又來了", "我就說嘛", "果然不出我所料", "這還用說嗎"]
        }
        
        # 內容長度策略
        self.content_length_strategies = {
            "short": {
                "target_words": "100-200字",
                "focus": "重點突出，快速決策",
                "style": "簡潔有力，直擊要害"
            },
            "medium": {
                "target_words": "250-400字", 
                "focus": "平衡分析，完整論述",
                "style": "結構完整，邏輯清晰"
            },
            "long": {
                "target_words": "450-600字",
                "focus": "深度分析，詳細展開", 
                "style": "論述豐富，專業深入"
            }
        }
        
        # 內容形式變體
        self.content_formats = {
            "analysis": "分析型內容",
            "question": "提問型內容", 
            "alert": "快訊型內容",
            "tutorial": "教學型內容",
            "humor": "幽默型內容"
        }
        
        # 幽默幹話庫
        self.humor_lines = {
            "技術派": {
                "買進": [
                    "大家可以放心抱著，我都梭哈了",
                    "反正我是穩穩的，你們自己看著辦",
                    "我已經上車了，慢車的自己想辦法",
                    "技術分析都說可以，不信算了",
                    "均線都金叉了還不買，等什麼"
                ],
                "賣出": [
                    "我今天出掉了，你們保重",
                    "先跑為敬，各位自求多福",
                    "我的停損已經設好了，佛系",
                    "反正我已經落袋為安了",
                    "技術面都破了還不跑，等套牢嗎"
                ],
                "觀望": [
                    "現在這盤面，看戲就好",
                    "技術面亂七八糟，還是睡覺比較實在",
                    "反正我現在空手，爽啦",
                    "這種盤還是去喝茶比較好",
                    "等明確信號再說，急什麼"
                ]
            },
            "新聞派": {
                "利多": [
                    "這消息一出，我就知道要噴了",
                    "內幕消息早就說了，現在才知道太慢",
                    "我早就買好了，就等這個消息",
                    "果然不出我所料，爆新聞來了",
                    "小道消息果然準，賺翻了"
                ],
                "利空": [
                    "我就說會有這一天，果然來了",
                    "幸好我早就出掉了，躲過一劫",
                    "這種消息面，還不快跑",
                    "早就有風聲了，現在才驚慌太慢",
                    "我今天清倉了，你們保重"
                ],
                "混亂": [
                    "現在消息滿天飛，誰知道哪個是真的",
                    "市場風向變太快，看不懂了",
                    "這種時候就是喝茶時間",
                    "反正我躺平了，愛怎樣就怎樣",
                    "新聞太多了，頭都昏了"
                ]
            },
            "總經派": {
                "看多": [
                    "從總經角度看，這波穩的",
                    "基本面支撐，大家可以安心",
                    "我的分析從來不會錯，相信我",
                    "長期投資者的福音來了",
                    "這就是價值投資的魅力"
                ],
                "看空": [
                    "總經面都告訴你要跑了，還不聽",
                    "我早就說過會有這一天",
                    "基本面已經變了，該醒醒了",
                    "這種總經環境，還抱什麼幻想",
                    "我的現金部位已經準備好了"
                ],
                "中性": [
                    "現在總經面混沌，耐心等待",
                    "這種時候就考驗定力了",
                    "反正我是長期投資，不急",
                    "總經派的優勢就是看得遠",
                    "短期波動不用太在意"
                ]
            }
        }
        
        # 經典幹話收尾
        self.humor_endings = [
            "反正我已經賺夠了，你們慢慢玩",
            "以上純屬個人意見，賠錢別找我",
            "投資有賺有賠，申購前請詳閱公開說明書",
            "我只是分享，你們自己判斷",
            "老話一句：投資一定有風險",
            "反正又不是我的錢，隨便啦",
            "看懂的就懂，不懂的就算了",
            "這就是股市，習慣就好",
            "賺錢的時候記得請我喝茶",
            "套牢的話...那就長期投資囉"
        ]
        
        self.technical_terminology_variants = {
            "技術派": {
                "上漲": ["噴發", "爆量", "突破", "衝破", "飆升", "起飛"],
                "下跌": ["破底", "殺低", "回檔", "修正", "整理", "休息"],
                "整理": ["盤整", "糾結", "拉鋸", "震盪", "磨底", "築底"],
                "突破": ["爆量突破", "放量突破", "強勢突破", "有效突破", "確認突破"]
            },
            "新聞派": {
                "消息": ["快訊", "爆料", "獨家", "內幕", "消息面", "風聲"],
                "影響": ["衝擊", "震撼", "影響", "波及", "連帶", "牽動"],
                "反應": ["回應", "反映", "表現", "展現", "顯示", "呈現"],
                "趨勢": ["走向", "方向", "潮流", "風向", "態勢", "局面"]
            },
            "總經派": {
                "成長": ["增長", "擴張", "發展", "提升", "改善", "進步"],
                "影響": ["衝擊", "效應", "作用", "影響力", "帶動", "促進"],
                "趨勢": ["走勢", "方向", "發展方向", "演變", "變化", "動向"],
                "分析": ["解析", "剖析", "研判", "評估", "檢視", "觀察"]
            }
        }
        
        logger.info("增強版個人化 Prompt 生成器初始化完成")
    
    def generate_personality_variant(self, base_persona: str, force_short: bool = False, force_question: bool = False) -> PersonalityVariant:
        """生成個性變體"""
        
        available_moods = list(self.mood_modifiers.get(base_persona, {}).keys())
        available_energy = list(self.energy_levels.keys())
        available_focus = self.focus_styles.get(base_persona, ["一般分析"])
        available_interaction = list(self.interaction_styles.keys())
        
        # 隨機選擇各種變體元素
        mood = random.choice(available_moods) if available_moods else "neutral"
        energy = random.choice(available_energy)
        focus = random.choice(available_focus)
        
        # 根據強制參數調整互動風格
        if force_question:
            interaction = random.choice(["questioning", "question_based", "provocative"])
        else:
            # 加入幽默互動風格的機率
            if random.random() < 0.2:  # 20% 機率選擇幽默風格
                interaction = random.choice(["humorous", "sarcastic"])
            else:
                interaction = random.choice(available_interaction)
        
        variant = PersonalityVariant(
            base_personality=base_persona,
            mood_modifier=mood,
            energy_level=energy,
            focus_style=focus,
            interaction_style=interaction
        )
        
        # 添加長度和形式策略
        if force_short:
            variant.length_strategy = "short"
        else:
            variant.length_strategy = random.choice(["short", "medium", "long"])
        
        if force_question:
            variant.content_format = "question"
        else:
            # 加入幽默內容的機率
            if random.random() < 0.15:  # 15% 機率選擇幽默內容
                variant.content_format = "humor"
            else:
                variant.content_format = random.choice(["analysis", "question", "alert"])
        
        return variant
    
    def generate_randomized_language_elements(self, persona: str, variant: PersonalityVariant) -> Dict[str, Any]:
        """生成隨機化的語言元素"""
        
        # 獲取心情修飾詞
        mood_words = self.mood_modifiers.get(persona, {}).get(variant.mood_modifier, ["正常"])
        selected_mood = random.choice(mood_words)
        
        # 獲取能量詞彙
        energy_words = self.energy_levels.get(variant.energy_level, {}).get(persona, ["穩定"])
        selected_energy = random.choice(energy_words)
        
        # 獲取互動風格
        interaction_words = self.interaction_styles.get(variant.interaction_style, ["簡單說"])
        selected_interaction = random.choice(interaction_words)
        
        # 獲取技術用詞變體
        tech_variants = self.technical_terminology_variants.get(persona, {})
        
        # 隨機決定是否加入幽默元素 (30% 機率)
        humor_elements = {}
        if random.random() < 0.3:
            # 根據市場情況選擇幽默類型
            humor_types = list(self.humor_lines.get(persona, {}).keys())
            if humor_types:
                humor_type = random.choice(humor_types)
                humor_lines = self.humor_lines.get(persona, {}).get(humor_type, [])
                if humor_lines:
                    humor_elements = {
                        "humor_type": humor_type,
                        "humor_line": random.choice(humor_lines),
                        "humor_ending": random.choice(self.humor_endings)
                    }
        
        return {
            "mood_expression": selected_mood,
            "energy_expression": selected_energy,
            "interaction_starter": selected_interaction,
            "technical_variants": tech_variants,
            "focus_style": variant.focus_style,
            "humor_elements": humor_elements
        }
    
    def generate_enhanced_prompt(self, 
                                kol_serial: str,
                                kol_nickname: str, 
                                persona: str,
                                topic_title: str,
                                stock_data: Dict[str, Any],
                                market_context: Optional[str] = None,
                                stock_names: List[str] = None) -> Dict[str, Any]:
        """生成增強版個人化 Prompt"""
        
        try:
            # 生成個性變體 (添加隨機化的長度和形式控制)
            force_short = random.random() < 0.3  # 30% 機率生成短文
            force_question = random.random() < 0.25  # 25% 機率生成提問形式
            
            personality_variant = self.generate_personality_variant(persona, force_short, force_question)
            
            # 生成隨機化語言元素
            language_elements = self.generate_randomized_language_elements(persona, personality_variant)
            
            # 準備股票數據摘要
            stock_summary = self._prepare_stock_summary(stock_data, persona)
            
            # 生成系統 Prompt
            system_prompt = self._build_enhanced_system_prompt(
                kol_nickname, persona, personality_variant, language_elements
            )
            
            # 生成用戶 Prompt  
            user_prompt = self._build_enhanced_user_prompt(
                topic_title, stock_summary, language_elements, personality_variant, 
                market_context, persona, stock_names
            )
            
            # 生成參數（加入隨機性）
            generation_params = self._generate_randomized_params(personality_variant)
            
            return {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "generation_params": generation_params,
                "personality_variant": personality_variant,
                "language_elements": language_elements,
                "randomization_seed": random.randint(1000, 9999)
            }
            
        except Exception as e:
            logger.error(f"生成增強版 Prompt 失敗: {e}")
            return self._fallback_prompt(kol_nickname, persona, topic_title)
    
    def _prepare_stock_summary(self, stock_data: Dict[str, Any], persona: str) -> str:
        """準備股票數據摘要，包含技術指標解釋"""
        
        if not stock_data or not stock_data.get('has_stock_data'):
            return "一般市場分析"
            
        stock_summary = stock_data.get('stock_summary', '')
        technical_summary = stock_data.get('technical_summary', '')
        technical_explanation = stock_data.get('technical_explanation', '')  # 新增
        
        # 根據 persona 調整重點和技術解釋的呈現方式
        if persona == "技術派":
            base_info = f"技術面數據：{technical_summary}。個股表現：{stock_summary}"
            if technical_explanation:
                return f"{base_info}\n\n📊 技術指標詳細分析：\n{technical_explanation}"
            return base_info
        elif persona == "新聞派":
            base_info = f"市場動態：{stock_summary}。技術狀況：{technical_summary}"
            if technical_explanation:
                return f"{base_info}\n\n📈 技術面參考：\n{technical_explanation}"
            return base_info
        else:  # 總經派
            base_info = f"基本面分析：{stock_summary}。市場技術：{technical_summary}"
            if technical_explanation:
                return f"{base_info}\n\n📋 技術背景：\n{technical_explanation}"
            return base_info
    
    def _build_enhanced_system_prompt(self, 
                                    kol_nickname: str, 
                                    persona: str,
                                    variant: PersonalityVariant,
                                    language_elements: Dict[str, Any]) -> str:
        """建立增強版系統 Prompt"""
        
        base_personality = {
            "技術派": f"""你是 {kol_nickname}，一個資深技術分析師。
你的分析風格：{language_elements['mood_expression']}，專注於{language_elements['focus_style']}。
今天的狀態：{language_elements['energy_expression']}。""",
            
            "新聞派": f"""你是 {kol_nickname}，一個敏銳的財經記者。  
你的報導風格：{language_elements['mood_expression']}，特別關注{language_elements['focus_style']}。
今天的精神：{language_elements['energy_expression']}。""",
            
            "總經派": f"""你是 {kol_nickname}，一個深度總體經濟分析師。
你的分析角度：{language_elements['mood_expression']}，專精於{language_elements['focus_style']}。
今天的思維：{language_elements['energy_expression']}。"""
        }
        
        # 加入隨機性指引和技術分析解釋指導
        randomization_guidance = f"""
寫作時請注意：
1. 使用 "{language_elements['interaction_starter']}" 的方式開場
2. 能量等級：{variant.energy_level} - 調整語氣強度
3. 心情狀態：{variant.mood_modifier} - 影響用詞選擇
4. 避免使用制式化的 AI 語言，要更自然、更有個人特色
5. 每次回答都要有些微不同的表達方式，避免重複模式

📊 技術分析解釋指導：
- 當提到技術指標評分時，要解釋評分的原因
- 說明為什麼某個指標得到特定分數（如：MACD轉弱、均線突破等）
- 解釋信心度的含義（基於多項指標一致性）
- 用淺顯易懂的方式說明技術指標代表的市場狀況
- 避免只丟數字，要讓讀者理解數字背後的市場邏輯
"""
        
        return base_personality.get(persona, "") + randomization_guidance
    
    def _build_enhanced_user_prompt(self, 
                                  topic_title: str,
                                  stock_summary: str, 
                                  language_elements: Dict[str, Any],
                                  variant: PersonalityVariant,
                                  market_context: Optional[str] = None,
                                  persona: str = "技術派",
                                  stock_names: List[str] = None) -> str:
        """建立增強版用戶 Prompt"""
        
        context_info = f"市場背景：{market_context}" if market_context else ""
        
        # 根據變體調整內容要求
        length_strategy = self.content_length_strategies.get(variant.length_strategy, self.content_length_strategies["medium"])
        content_format = variant.content_format
        
        # 根據內容形式調整指引
        format_guidance = {
            "analysis": "深度分析並提供專業見解",
            "question": "以提問方式引導討論，讓讀者思考並參與",
            "alert": "快速傳達重要資訊，語氣緊迫",
            "tutorial": "教學式解釋，幫助讀者理解",
            "humor": "幽默風趣地表達觀點，加入搞笑幹話元素"
        }
        
        format_specific = format_guidance.get(content_format, "分析型內容")
        
        # 生成個人化標題建議
        personalized_title = personalized_title_generator.generate_personalized_title(
            topic_title, persona, stock_names
        )
        
        prompt = f"""
請針對以下話題進行{format_specific}：
話題：{topic_title}
數據支撐：{stock_summary}
{context_info}

內容要求：
- 長度策略：{length_strategy['target_words']} ({length_strategy['focus']})
- 寫作風格：{length_strategy['style']}
- 內容形式：{format_specific}
- 互動方式：{language_elements['interaction_starter']}

請用你的風格寫一篇貼文，包含：
1. 個人化標題（參考風格：{personalized_title}，但不要直接複製，要用你的表達方式）
2. 分析內容（結合真實數據，展現專業但不失個人特色）
3. 互動元素（用 "{language_elements['interaction_starter']}" 的方式與讀者互動）

        {"特別注意：以提問形式結尾，引導讀者參與討論" if content_format == "question" else ""}
        {self._get_humor_guidance(language_elements, content_format)}

記住：
- 展現你今天 "{language_elements['energy_expression']}" 的狀態
- 專注於 "{language_elements['focus_style']}" 
- 保持自然，避免 AI 味
- 字數嚴格控制在 {length_strategy['target_words']}
- 標題要有強烈的個人風格，避免制式化

格式：
標題：[你的個人化標題]
內容：[你的分析內容]
"""
        
        return prompt
    
    def _get_humor_guidance(self, language_elements: Dict[str, Any], content_format: str) -> str:
        """獲取幽默指導"""
        
        humor_elements = language_elements.get("humor_elements", {})
        
        if content_format == "humor" and humor_elements:
            humor_type = humor_elements.get("humor_type", "")
            humor_line = humor_elements.get("humor_line", "")
            humor_ending = humor_elements.get("humor_ending", "")
            
            return f"""
幽默指導：
- 適當時機加入這類幹話：「{humor_line}」
- 可以用這種收尾：「{humor_ending}」
- 保持幽默但不失專業，要搞笑但有料
- 幽默類型：{humor_type}相關的搞笑表達"""
            
        elif humor_elements:
            humor_line = humor_elements.get("humor_line", "")
            return f"""
輕鬆提醒：可以適當加入一些幽默元素，像是「{humor_line}」這樣的表達"""
        
        return ""
    
    def _generate_randomized_params(self, variant: PersonalityVariant) -> Dict[str, Any]:
        """生成隨機化的生成參數"""
        
        # 根據個性變體調整參數
        base_temperature = 0.7
        
        # 能量等級影響 temperature
        energy_modifier = {
            "high": 0.2,    # 更隨機、更有活力
            "medium": 0.0,  # 標準
            "low": -0.1     # 更保守、更穩定
        }
        
        # 心情修飾詞影響 temperature
        mood_modifier = {
            "excited": 0.1,
            "confident": 0.05,
            "cautious": -0.05,
            "analytical": -0.1
        }
        
        # 計算最終 temperature
        final_temperature = base_temperature
        final_temperature += energy_modifier.get(variant.energy_level, 0)
        final_temperature += mood_modifier.get(variant.mood_modifier, 0)
        
        # 添加小幅隨機波動
        final_temperature += random.uniform(-0.05, 0.05)
        
        # 確保在合理範圍內
        final_temperature = max(0.3, min(1.0, final_temperature))
        
        return {
            "model": "gpt-4o-mini",
            "temperature": round(final_temperature, 2),
            "max_tokens": random.randint(600, 800),  # 隨機化輸出長度
            "top_p": random.uniform(0.85, 0.95),     # 隨機化詞彙多樣性
            "frequency_penalty": random.uniform(0.1, 0.3),  # 隨機化重複懲罰
            "presence_penalty": random.uniform(0.1, 0.2)    # 隨機化新話題傾向
        }
    
    def _fallback_prompt(self, kol_nickname: str, persona: str, topic_title: str) -> Dict[str, Any]:
        """備用 Prompt（當生成失敗時）"""
        
        return {
            "system_prompt": f"你是 {kol_nickname}，{persona}分析師。",
            "user_prompt": f"請分析：{topic_title}",
            "generation_params": {"model": "gpt-4o-mini", "temperature": 0.7},
            "personality_variant": None,
            "language_elements": {},
            "randomization_seed": 0
        }

# 創建服務實例的工廠函數
def create_enhanced_prompt_generator() -> EnhancedPromptGenerator:
    """創建增強版 Prompt 生成器實例"""
    return EnhancedPromptGenerator()
