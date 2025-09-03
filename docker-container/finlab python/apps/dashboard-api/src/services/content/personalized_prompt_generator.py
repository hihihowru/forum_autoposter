"""
個人化 Prompt 生成器
根據 KOL 設定動態生成個人化的內容生成 prompt
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class KOLSettings:
    """KOL 個人化設定"""
    kol_id: str
    nickname: str
    persona: str
    prompt_template: str
    tone_vector: Dict[str, float]
    content_preferences: Dict[str, Any]
    vocabulary: Dict[str, List[str]]
    data_requirements: Dict[str, Any]
    typing_habits: Dict[str, str]

@dataclass
class PersonalizedPrompt:
    """個人化 Prompt 結果"""
    system_prompt: str
    user_prompt: str
    kol_settings: KOLSettings
    market_data: Optional[Dict[str, Any]]
    generation_params: Dict[str, Any]
    created_at: datetime

class PersonalizedPromptGenerator:
    """個人化 Prompt 生成器"""
    
    def __init__(self):
        self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.kol_settings_cache = {}
        
        # 預設的 KOL 設定 (應該從 Google Sheets 讀取)
        self.default_kol_settings = {
            "200": {  # 川川哥
                "nickname": "川川哥",
                "persona": "技術派",
                "prompt_template": """你是川川哥，一個專精技術分析的股市老手。你的特色是：
- 語氣直接但有料，有時會狂妄，有時又碎碎念
- 大量使用技術分析術語
- 不愛用標點符號，全部用省略號串起來
- 偶爾會英文逗號亂插""",
                "tone_vector": {
                    "formal_level": 3,
                    "emotion_intensity": 7,
                    "confidence_level": 9,
                    "interaction_level": 6
                },
                "content_preferences": {
                    "length_type": "short",
                    "paragraph_style": "省略號分隔，不換行",
                    "ending_style": "想知道的話，留言告訴我，咱們一起討論一下..."
                },
                "vocabulary": {
                    "technical_terms": ["黃金交叉", "均線糾結", "三角收斂", "K棒爆量", "跳空缺口", "支撐帶", "壓力線", "MACD背離"],
                    "casual_expressions": ["穩了啦", "爆啦", "嘎到", "要噴啦", "破線啦", "睡醒漲停"]
                },
                "data_requirements": {
                    "primary": ["ohlc", "technical_indicators"],
                    "finlab_api_needed": True
                },
                "typing_habits": {
                    "punctuation_style": "省略號為主...偶爾逗號,",
                    "sentence_pattern": "短句居多...不愛長句"
                }
            },
            "201": {  # 韭割哥
                "nickname": "韭割哥",
                "persona": "總經派", 
                "prompt_template": """你是韭割哥，一個專精總經分析的投資老手。你的特色是：
- 沉穩理性，但常用比較「說教」的語氣
- 有點像在寫長文分析，偶爾也酸人「你們都短視近利」
- 習慣用全形標點符號""",
                "tone_vector": {
                    "formal_level": 7,
                    "emotion_intensity": 4,
                    "confidence_level": 8,
                    "interaction_level": 5
                },
                "content_preferences": {
                    "length_type": "long",
                    "paragraph_style": "段落間用空行分隔，保持整潔",
                    "ending_style": "如果你也認同這樣的看法，不妨多多研究基本面，長期存股才是王道！"
                },
                "vocabulary": {
                    "economic_terms": ["通膨壓力", "利率決策", "CPI", "GDP成長", "失業率", "美元指數", "資金寬鬆"],
                    "casual_expressions": ["通膨炸裂", "要升息啦", "撐不住了", "別太樂觀", "慢慢加碼", "長線投資"]
                },
                "data_requirements": {
                    "primary": ["macro_economic", "policy_updates"],
                    "finlab_api_needed": False
                },
                "typing_habits": {
                    "punctuation_style": "全形標點「，」「。」",
                    "sentence_pattern": "長句分析，邏輯清晰"
                }
            },
            "202": {  # 梅川褲子
                "nickname": "梅川褲子", 
                "persona": "新聞派",
                "prompt_template": """你是梅川褲子，一個敏銳的財經新聞分析師。你的特色是：
- 語氣急躁，常常「快打快收」
- 看起來像新聞狗，語氣急促有時像在喊口號
- 打字很急不愛空格，爆Emoji
- 會重複字像啦啦啦，驚嘆號狂刷""",
                "tone_vector": {
                    "formal_level": 2,
                    "emotion_intensity": 9,
                    "urgency_level": 10,
                    "interaction_level": 8
                },
                "content_preferences": {
                    "length_type": "medium",
                    "paragraph_style": "段落間用空行分隔，保持緊湊",
                    "ending_style": "別忘了持續鎖定我，隨時更新即時新聞、盤中快訊！快點快點！"
                },
                "vocabulary": {
                    "news_terms": ["爆新聞啦", "風向轉了", "盤中爆炸", "快訊快訊", "漲停新聞", "政策護航"],
                    "casual_expressions": ["現在就進", "看漲", "衝第一", "蹭題材啦", "來不及啦", "有人知道嗎"]
                },
                "data_requirements": {
                    "primary": ["news", "market_sentiment"],
                    "finlab_api_needed": False
                },
                "typing_habits": {
                    "punctuation_style": "驚嘆號!!!狂刷",
                    "spacing": "不愛空格,打字很急"
                }
            },
            "203": {  # 龜狗一日散戶
                "nickname": "龜狗一日散戶",
                "persona": "籌碼派",
                "prompt_template": """你是龜狗一日散戶，一個專精籌碼面分析的投資老手。你的特色是：
- 語氣直接務實，專注資金流向和大戶動向
- 喜歡用「...」分隔句子，表達節奏感
- 常用籌碼面術語，關注外資、投信、散戶動向
- 結尾喜歡問問題，引起討論""",
                "tone_vector": {
                    "formal_level": 4,
                    "emotion_intensity": 6,
                    "confidence_level": 7,
                    "interaction_level": 8
                },
                "content_preferences": {
                    "length_type": "medium",
                    "paragraph_style": "用省略號分隔句子，保持節奏感",
                    "ending_style": "你們覺得目前的籌碼結構如何？有觀察到什麼特別的資金流向嗎？"
                },
                "vocabulary": {
                    "chips_terms": ["外資持股", "融資餘額", "大戶持股", "籌碼集中", "資金流向", "當沖比例", "投信持股", "自營商"],
                    "casual_expressions": ["籌碼面觀察", "資金流向分析", "籌碼結構", "短期震盪", "長期支撐", "減碼跡象", "進場意願"]
                },
                "data_requirements": {
                    "primary": ["chips_data", "fund_flow", "institutional_holdings"],
                    "finlab_api_needed": False
                },
                "typing_habits": {
                    "punctuation_style": "省略號為主...偶爾問號?",
                    "sentence_pattern": "短句居多...用省略號連接"
                }
            },
            "204": {  # 板橋大who
                "nickname": "板橋大who",
                "persona": "情緒派",
                "prompt_template": """你是板橋大who，一個專精市場情緒分析的投資老手。你的特色是：
- 語氣活潑開朗，善於解讀投資人心理
- 喜歡用「！」表達情緒，語氣親切友善
- 關注社群情緒、媒體情緒、恐慌貪婪指數
- 結尾喜歡關心讀者心情，互動性強""",
                "tone_vector": {
                    "formal_level": 3,
                    "emotion_intensity": 8,
                    "confidence_level": 6,
                    "interaction_level": 9
                },
                "content_preferences": {
                    "length_type": "medium",
                    "paragraph_style": "段落間用空行分隔，保持活潑",
                    "ending_style": "你們現在的心情如何？是樂觀還是謹慎？市場情緒會影響你的投資決策嗎？"
                },
                "vocabulary": {
                    "sentiment_terms": ["恐慌貪婪指數", "社群討論熱度", "新聞情緒", "投資人心理", "市場情緒", "情緒傾向", "討論熱度"],
                    "casual_expressions": ["情緒面解讀", "市場情緒", "投資人心理", "情緒狀態", "情緒波動", "情緒指標", "情緒分析"]
                },
                "data_requirements": {
                    "primary": ["sentiment_data", "social_media", "news_sentiment"],
                    "finlab_api_needed": False
                },
                "typing_habits": {
                    "punctuation_style": "感嘆號!和問號?較多",
                    "sentence_pattern": "中等長度，語氣活潑"
                }
            }
        }
    
    def get_kol_settings(self, kol_serial: str) -> KOLSettings:
        """獲取 KOL 個人化設定"""
        
        if kol_serial in self.kol_settings_cache:
            return self.kol_settings_cache[kol_serial]
        
        # 從預設設定載入 (後續應從 Google Sheets 讀取)
        if kol_serial in self.default_kol_settings:
            settings_data = self.default_kol_settings[kol_serial]
            
            kol_settings = KOLSettings(
                kol_id=kol_serial,
                nickname=settings_data["nickname"],
                persona=settings_data["persona"],
                prompt_template=settings_data["prompt_template"],
                tone_vector=settings_data["tone_vector"],
                content_preferences=settings_data["content_preferences"],
                vocabulary=settings_data["vocabulary"],
                data_requirements=settings_data["data_requirements"],
                typing_habits=settings_data["typing_habits"]
            )
            
            self.kol_settings_cache[kol_serial] = kol_settings
            return kol_settings
        
        # 預設設定
        return KOLSettings(
            kol_id=kol_serial,
            nickname=f"KOL_{kol_serial}",
            persona="一般派",
            prompt_template="你是一個專業的投資分析師。",
            tone_vector={"formal_level": 5, "emotion_intensity": 5},
            content_preferences={"length_type": "medium"},
            vocabulary={"terms": []},
            data_requirements={"primary": ["basic"]},
            typing_habits={"punctuation_style": "正常"}
        )
    
    async def generate_personalized_prompt(self, 
                                         kol_serial: str,
                                         topic_title: str,
                                         topic_keywords: str,
                                         market_data: Optional[Dict[str, Any]] = None) -> PersonalizedPrompt:
        """生成個人化 prompt"""
        
        print(f"🎭 為 {kol_serial} 生成個人化 prompt...")
        
        # 1. 獲取 KOL 設定
        kol_settings = self.get_kol_settings(kol_serial)
        print(f"  📋 KOL: {kol_settings.nickname} ({kol_settings.persona})")
        
        # 2. 建構系統 prompt
        system_prompt = self.build_system_prompt(kol_settings, market_data)
        
        # 3. 建構用戶 prompt
        user_prompt = self.build_user_prompt(kol_settings, topic_title, topic_keywords, market_data)
        
        # 4. 設定生成參數
        generation_params = self.get_generation_params(kol_settings)
        
        return PersonalizedPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            kol_settings=kol_settings,
            market_data=market_data,
            generation_params=generation_params,
            created_at=datetime.now()
        )
    
    def build_system_prompt(self, kol_settings: KOLSettings, market_data: Optional[Dict[str, Any]]) -> str:
        """建構系統 prompt"""
        
        # 基礎角色設定
        base_prompt = kol_settings.prompt_template
        
        # 添加語氣指導
        tone_guidance = self.build_tone_guidance(kol_settings.tone_vector)
        
        # 添加詞彙指導
        vocabulary_guidance = self.build_vocabulary_guidance(kol_settings.vocabulary)
        
        # 添加格式指導
        format_guidance = self.build_format_guidance(kol_settings.content_preferences, kol_settings.typing_habits)
        
        # 添加數據上下文
        data_context = self.format_market_data_context(market_data, kol_settings) if market_data else ""
        
        system_prompt = f"""{base_prompt}

語氣特徵：
{tone_guidance}

詞彙風格：
{vocabulary_guidance}

格式要求：
{format_guidance}

{data_context}

重要指導：
1. 嚴格保持 {kol_settings.nickname} 的個人風格和語氣
2. 大量使用專屬詞彙和表達方式
3. 遵循固定的打字習慣和格式
4. 內容長度控制在 {kol_settings.content_preferences.get('length_type', 'medium')} 範圍
5. 結尾使用固定的風格
6. 避免 AI 生成的痕跡，要像真人發文
"""
        
        return system_prompt
    
    def build_user_prompt(self, kol_settings: KOLSettings, topic_title: str, 
                         topic_keywords: str, market_data: Optional[Dict[str, Any]]) -> str:
        """建構用戶 prompt"""
        
        # 根據內容長度設定字數要求
        length_requirements = {
            "short": "50-100字，簡潔有力",
            "medium": "200-300字，適中分析", 
            "long": "400-500字，深度論述"
        }
        
        length_type = kol_settings.content_preferences.get('length_type', 'medium')
        length_req = length_requirements.get(length_type, "200-300字")
        
        # 股票數據提示
        stock_data_hint = ""
        if market_data and market_data.get('has_stock_data'):
            stock_data_hint = f"\n股票數據：{market_data.get('stock_summary', '無特定數據')}"
        
        # 個人化標題指導
        title_guidance = self.get_title_guidance(kol_settings)
        
        user_prompt = f"""請以 {kol_settings.nickname} 的身份，針對以下話題發文：

話題標題：{topic_title}
相關關鍵詞：{topic_keywords}{stock_data_hint}

標題生成要求：
{title_guidance}

內容生成要求：
1. 字數控制：{length_req}
2. 語氣風格：完全符合 {kol_settings.nickname} 的特色
3. 專業角度：從 {kol_settings.persona} 的視角分析
4. 互動性：適度引起討論
5. 結尾方式：{kol_settings.content_preferences.get('ending_style', '歡迎討論')}

請生成標題和內容，格式如下：
標題：[生成的標題]
內容：[生成的內容]
"""
        
        return user_prompt
    
    def get_title_guidance(self, kol_settings: KOLSettings) -> str:
        """獲取個人化隨機標題指導"""
        
        import random
        
        # 隨機標題元素庫
        title_elements = {
            "技術派": {
                "開頭詞": ["技術面看", "圖表說話", "均線告訴你", "技術分析", "K線密碼", "指標顯示"],
                "技術詞": ["黃金交叉", "死亡交叉", "均線糾結", "爆量突破", "支撐位", "壓力線", "背離", "收斂"],
                "情緒詞": ["狂飆", "暴跌", "震盪", "突破", "回檔", "整理", "轉強", "轉弱"],
                "結尾詞": ["來了", "出現", "確認", "成形", "啟動", "到位"],
                "疑問句": ["還能追嗎", "該跑了嗎", "怎麼看", "能抱嗎", "要進場嗎"],
                "狂妄句": ["早就說了", "我就知道", "果然不出我所料", "技術面不會騙人"]
            },
            "籌碼派": {
                "開頭詞": ["籌碼面看", "資金流向", "大戶動向", "籌碼分析", "資金追蹤", "持股變化"],
                "籌碼詞": ["外資持股", "融資餘額", "大戶持股", "籌碼集中", "資金流向", "當沖比例"],
                "情緒詞": ["減碼", "加碼", "進場", "出場", "集中", "分散", "穩定", "鬆動"],
                "結尾詞": ["跡象", "訊號", "變化", "趨勢", "結構", "格局"],
                "疑問句": ["怎麼看", "會怎樣", "有影響嗎", "值得關注嗎", "該注意什麼"],
                "分析句": ["籌碼面告訴你", "資金流向顯示", "大戶動向透露"]
            },
            "情緒派": {
                "開頭詞": ["情緒面看", "市場心情", "投資人心態", "情緒分析", "心理解讀", "氛圍觀察"],
                "情緒詞": ["樂觀", "悲觀", "謹慎", "恐慌", "貪婪", "觀望", "興奮", "擔憂"],
                "指標詞": ["恐慌貪婪指數", "社群熱度", "新聞情緒", "討論熱度", "情緒傾向"],
                "結尾詞": ["階段", "狀態", "氛圍", "趨勢", "變化", "影響"],
                "疑問句": ["心情如何", "是樂觀還是謹慎", "會影響決策嗎", "該怎麼看"],
                "關心句": ["你們現在的心情", "市場情緒如何", "投資人心態"]
            },
            "新聞派": {
                "開頭詞": ["快訊", "重磅", "突發", "最新", "緊急", "爆料", "獨家", "驚爆"],
                "感嘆詞": ["哇塞", "天啊", "不得了", "太扯了", "瘋了", "爆了"],
                "新聞詞": ["消息面", "爆新聞", "內幕消息", "小道消息", "風聲", "傳言"],
                "動作詞": ["大漲", "暴跌", "狂飆", "重挫", "反彈", "跳水", "噴出", "崩盤"],
                "結尾詞": ["啦", "了", "呢", "耶", "喔"],
                "疑問句": ["你知道嗎", "聽說了嗎", "看到了嗎", "相信嗎", "怎麼辦"]
            },
            "總經派": {
                "開頭詞": ["從總經看", "基本面分析", "長期觀點", "價值判斷", "理性分析", "深度解讀"],
                "分析詞": ["基本面", "總經因子", "產業趨勢", "經濟數據", "政策面", "供需關係"],
                "判斷詞": ["合理", "偏高", "偏低", "超值", "泡沫", "轉機", "成長", "衰退"],
                "建議詞": ["建議", "觀察", "關注", "評估", "考慮", "思考"],
                "疑問句": ["值得投資嗎", "有價值嗎", "該怎麼看", "合理嗎", "還有機會嗎"],
                "哲學句": ["投資就是", "市場邏輯", "價值回歸", "時間會證明"]
            }
        }
        
        # 通用隨機元素
        numbers = ["3個", "5大", "7項", "關鍵", "重要", "必看"]
        time_words = ["今天", "現在", "最新", "剛剛", "突然", "馬上"]
        
        persona = kol_settings.persona
        # 映射不同人設到相應的標題元素
        persona_mapping = {
            "技術派": "技術派",
            "籌碼派": "籌碼派",  # 籌碼派使用籌碼派的模式
            "新聞派": "新聞派", 
            "總經派": "總經派",
            "情緒派": "情緒派"   # 情緒派使用情緒派的模式
        }
        mapped_persona = persona_mapping.get(persona, "技術派")
        elements = title_elements.get(mapped_persona, title_elements["技術派"])
        
        # 隨機選擇元素
        random_opening = random.choice(elements.get("開頭詞", ["分析"]))
        random_number = random.choice(numbers)
        random_time = random.choice(time_words)
        
        # 隨機選擇標題模式
        patterns = []
        
        if mapped_persona == "技術派":
            tech_word = random.choice(elements["技術詞"])
            emotion_word = random.choice(elements["情緒詞"])
            ending_word = random.choice(elements["結尾詞"])
            question = random.choice(elements["疑問句"])
            arrogant = random.choice(elements["狂妄句"])
            
            patterns = [
                f"{random_opening}...{emotion_word}{ending_word}",
                f"{tech_word}出現！{question}？",
                f"{kol_settings.nickname}：{arrogant}，{emotion_word}{ending_word}",
                f"{random_time}{tech_word}！{emotion_word}訊號{ending_word}",
                f"{random_number}技術指標告訴你...{emotion_word}{ending_word}"
            ]
        
        elif mapped_persona == "籌碼派":
            chips_word = random.choice(elements["籌碼詞"])
            emotion_word = random.choice(elements["情緒詞"])
            ending_word = random.choice(elements["結尾詞"])
            question = random.choice(elements["疑問句"])
            analysis = random.choice(elements["分析句"])
            
            patterns = [
                f"{random_opening}...{chips_word}{emotion_word}{ending_word}",
                f"{chips_word}變化！{question}？",
                f"{kol_settings.nickname}：{analysis}，{emotion_word}{ending_word}",
                f"{random_time}{chips_word}！{emotion_word}訊號{ending_word}",
                f"{random_number}籌碼指標告訴你...{emotion_word}{ending_word}"
            ]
        
        elif mapped_persona == "情緒派":
            sentiment_word = random.choice(elements["情緒詞"])
            indicator_word = random.choice(elements["指標詞"])
            ending_word = random.choice(elements["結尾詞"])
            question = random.choice(elements["疑問句"])
            care = random.choice(elements["關心句"])
            
            patterns = [
                f"{random_opening}...{sentiment_word}{ending_word}",
                f"{indicator_word}變化！{question}？",
                f"{kol_settings.nickname}：{care}，{sentiment_word}{ending_word}",
                f"{random_time}{indicator_word}！{sentiment_word}訊號{ending_word}",
                f"{random_number}情緒指標告訴你...{sentiment_word}{ending_word}"
            ]
        
        elif mapped_persona == "新聞派":
            exclaim = random.choice(elements["感嘆詞"])
            news_word = random.choice(elements["新聞詞"])
            action_word = random.choice(elements["動作詞"])
            ending = random.choice(elements["結尾詞"])
            question = random.choice(elements["疑問句"])
            
            patterns = [
                f"{random_opening}！{action_word}{ending}",
                f"{exclaim}！{random_time}{action_word}{ending}",
                f"{kol_settings.nickname}快報：{action_word}{ending}",
                f"{news_word}：{random_time}{action_word}{ending}",
                f"{exclaim}！{random_number}消息{question}？"
            ]
        
        else:  # 總經派
            analysis_word = random.choice(elements["分析詞"])
            judgment_word = random.choice(elements["判斷詞"])
            suggest_word = random.choice(elements["建議詞"])
            question = random.choice(elements["疑問句"])
            philosophy = random.choice(elements["哲學句"])
            
            patterns = [
                f"{random_opening}：{judgment_word}了",
                f"{analysis_word}{suggest_word}{judgment_word}評估",
                f"{kol_settings.nickname}觀點：{judgment_word}",
                f"{philosophy}...{judgment_word}時機",
                f"{random_number}{analysis_word}告訴你{question}"
            ]
        
        # 隨機選擇一個模式，並加入更多隨機元素
        selected_pattern = random.choice(patterns)
        
        # 增加額外的隨機性
        random_focus = random.choice([
            "多頭格局", "空頭警訊", "震盪整理", "技術突破", "量價背離", 
            "資金流向", "主力動向", "散戶心態", "外資布局", "內資轉向"
        ])
        
        # 根據時間添加不同的開場
        time_elements = ["今日", "本週", "近期", "這波", "當前", "最新"]
        random_time_element = random.choice(time_elements)
        
        return f"""🎯 {kol_settings.nickname} 個人化標題指導:

📝 隨機生成模式: "{selected_pattern}"
🔄 額外隨機元素: {random_focus} / {random_time_element}

⚠️ 嚴格要求:
1. 絕對不能直接複製話題原標題
2. 必須用 {kol_settings.nickname} 的口吻重新表達
3. 參考模式但要結合實際內容調整
4. 控制在15-25字內，具有吸引力
5. 展現 {persona} 的專業特色
6. 加入個人色彩和隨機變化

💡 表達風格提示:
- 開頭詞庫: {', '.join(elements.get('開頭詞', [])[:3])}...
- 隨機元素: {random_number}, {random_time}
- 結合實際股票/話題內容創造獨特標題

🚫 禁止事項:
- 直接照抄原話題標題
- 使用過於制式化的表達
- 缺乏個人特色和隨機性"""
    
    def build_tone_guidance(self, tone_vector: Dict[str, float]) -> str:
        """建構語氣指導"""
        
        guidance_parts = []
        
        formal_level = tone_vector.get('formal_level', 5)
        if formal_level <= 3:
            guidance_parts.append("語氣非常口語化、隨性")
        elif formal_level >= 7:
            guidance_parts.append("語氣較為正式、專業")
        
        emotion_intensity = tone_vector.get('emotion_intensity', 5)
        if emotion_intensity >= 8:
            guidance_parts.append("情緒表達強烈、有感染力")
        elif emotion_intensity <= 3:
            guidance_parts.append("情緒表達克制、理性")
        
        confidence_level = tone_vector.get('confidence_level', 5)
        if confidence_level >= 8:
            guidance_parts.append("語氣自信、肯定")
        
        urgency_level = tone_vector.get('urgency_level', 5)
        if urgency_level >= 8:
            guidance_parts.append("語氣急迫、催促感")
        
        return "、".join(guidance_parts) if guidance_parts else "自然表達"
    
    def build_vocabulary_guidance(self, vocabulary: Dict[str, List[str]]) -> str:
        """建構詞彙指導"""
        
        guidance_parts = []
        
        for category, words in vocabulary.items():
            if words:
                guidance_parts.append(f"{category}: {', '.join(words[:5])}")  # 只顯示前5個
        
        return "\n".join(guidance_parts) if guidance_parts else "使用一般詞彙"
    
    def build_format_guidance(self, content_preferences: Dict[str, Any], 
                            typing_habits: Dict[str, str]) -> str:
        """建構格式指導"""
        
        guidance = f"""
段落風格：{content_preferences.get('paragraph_style', '正常分段')}
標點習慣：{typing_habits.get('punctuation_style', '正常標點')}
句型模式：{typing_habits.get('sentence_pattern', '正常句型')}
結尾風格：{content_preferences.get('ending_style', '自然結尾')}
"""
        
        return guidance.strip()
    
    def format_market_data_context(self, market_data: Dict[str, Any], 
                                 kol_settings: KOLSettings) -> str:
        """格式化市場數據上下文"""
        
        if not market_data:
            return ""
        
        context_parts = ["市場數據上下文："]
        
        if market_data.get('has_stock_data'):
            context_parts.append(f"相關股票：{market_data.get('stock_summary', '無')}")
        
        if market_data.get('technical_summary') and kol_settings.persona == "技術派":
            context_parts.append(f"技術分析：{market_data['technical_summary']}")
        
        if market_data.get('news_summary') and kol_settings.persona == "新聞派":
            context_parts.append(f"新聞摘要：{market_data['news_summary']}")
        
        return "\n".join(context_parts)
    
    def get_generation_params(self, kol_settings: KOLSettings) -> Dict[str, Any]:
        """獲取生成參數"""
        
        # 根據 KOL 特性調整參數
        base_temperature = 0.7
        
        # 技術派較理性，溫度稍低
        if kol_settings.persona == "技術派":
            base_temperature = 0.6
        # 新聞派較情緒化，溫度稍高
        elif kol_settings.persona == "新聞派":
            base_temperature = 0.8
        
        # 根據情緒強度調整
        emotion_intensity = kol_settings.tone_vector.get('emotion_intensity', 5)
        temperature_adjustment = (emotion_intensity - 5) * 0.02
        final_temperature = max(0.1, min(1.0, base_temperature + temperature_adjustment))
        
        return {
            "model": "gpt-4o-mini",
            "temperature": final_temperature,
            "max_tokens": 800,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
