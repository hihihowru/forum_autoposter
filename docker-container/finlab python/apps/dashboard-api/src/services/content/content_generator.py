"""
內容生成服務
整合 OpenAI API 來生成標題和內容
"""

import os
import logging
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from openai import OpenAI
try:
    from services.kol.kol_settings_loader import KOLSettingsLoader
except Exception:
    KOLSettingsLoader = None  # 避免在工具腳本環境無法 import 時出錯
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class ContentRequest:
    """內容生成請求"""
    topic_title: str
    topic_keywords: str
    kol_persona: str
    kol_nickname: str
    content_type: str
    target_audience: str = "active_traders"
    tone: str = "confident"
    market_data: Optional[Dict[str, Any]] = None

@dataclass
class GeneratedContent:
    """生成的內容結果"""
    title: str
    content: str
    hashtags: str
    success: bool = True
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class ContentGenerator:
    """內容生成器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化內容生成器
        
        Args:
            api_key: OpenAI API 金鑰，如果不提供則從環境變數讀取
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API 金鑰未設置，請設置 OPENAI_API_KEY 環境變數")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # 模型配置
        self.title_model = "gpt-4o-mini"
        self.content_model = "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens_title = 100
        self.max_tokens_content = 800
        # 標題生成的額外隨機性與懲罰，避免重複與制式化
        self.title_temperature = 0.9
        self.title_frequency_penalty = 0.5
        self.title_presence_penalty = 0.3
        
        logger.info("內容生成器初始化完成")
    
    def _get_kol_config(self, kol_nickname: str) -> Dict[str, str]:
        """獲取 KOL 詳細配置（優先讀取 Google Sheets 覆蓋預設）"""
        # 預設配置（作為基底）
        kol_configs = {
            "川川哥": {
                "content_type": "technical,chart",
                "target_audience": "active_traders",
                "tone_style": "自信直球，有時會狂妄，有時又碎碎念，像版上常見的「嘴很臭但有料」帳號",
                "common_words": "黃金交叉、均線糾結、三角收斂、K棒爆量、跳空缺口、支撐帶、壓力線、爆量突破、假突破、牛熊交替、短多、日K、週K、月K、EMA、MACD背離、成交量暴增、突破拉回、停利、移動停損",
                "casual_words": "穩了啦、爆啦、開高走低、嘎到、這根要噴、笑死、抄底啦、套牢啦、老師來了、要噴啦、破線啦、還在盤整、穩穩的、這樣嘎死、快停損、這裡進場、紅K守不住、買爆、賣壓炸裂、等回測、睡醒漲停",
                "typing_habit": "不打標點.....全部用省略號串起來,偶爾英文逗號亂插",
                "background_story": "大學就開始玩技術分析，曾經靠抓到台積電一根漲停翻身，信奉「K線就是人生」，常常半夜盯圖到三點。",
                "expertise": "技術分析,圖表解讀",
                "ending_style": "有興趣的朋友們，快來聊聊你們的看法吧...想知道的話，留言告訴我，咱們一起討論一下...",
                "paragraph_spacing": "段落間用省略號分隔，不換行",
                "content_length": "short",  # 固定短內容
                "post_types": {
                    "question": {"weight": 0.6, "style": "疑問句為主，引起討論"},
                    "opinion": {"weight": 0.4, "style": "發表觀點，技術分析"}
                }
            },
            "韭割哥": {
                "content_type": "macro,policy",
                "target_audience": "long_term_investors",
                "tone_style": "沉穩理性，但常用比較「說教」的語氣，有點像在寫長文分析，偶爾也酸人「你們都短視近利」",
                "common_words": "通膨壓力、利率決策、CPI、PPI、GDP成長、失業率、美元指數、資金寬鬆、資金緊縮、景氣循環、聯準會會議紀要、殖利率曲線倒掛、匯率波動、長期趨勢、結構性風險、基本面支撐、資產泡沫、量化緊縮、降息預期、經濟韌性",
                "casual_words": "通膨炸裂、要升息啦、撐不住了、老美又來、美元要衝、景氣差爆、信心不足、要衰退啦、別太樂觀、還在觀望、慢慢加碼、別急、等數據、看長一點、台灣撐得住嗎、外資走啦、長線投資、慢慢存股、經濟週期啦、耐心等",
                "typing_habit": "習慣用全形標點「，」「。」,偶爾丟英文縮寫(GDP,CPI),會用→當連接符號",
                "background_story": "金融業上班族，白天盯數據，下班寫總經分析。曾因提早預測2022升息週期被同事封為「小型央行」。",
                "expertise": "基本面分析,政策解讀",
                "ending_style": "如果你也認同這樣的看法，不妨多多研究基本面，讓自己在這個波動的市場中立於不敗之地，長期存股才是王道！",
                "paragraph_spacing": "段落間用空行分隔，保持整潔",
                "content_length": "long",  # 固定長內容
                "post_types": {
                    "question": {"weight": 0.3, "style": "簡短疑問，引起思考"},
                    "opinion": {"weight": 0.7, "style": "深度總經分析，說教風格"}
                }
            },
            "梅川褲子": {
                "content_type": "news,trending",
                "target_audience": "active_traders",
                "tone_style": "敏銳急躁，常常「快打快收」，看起來像新聞狗；語氣急，有時像是在喊口號",
                "common_words": "熱點題材、政策利多、半導體政策、AI趨勢、能源補助、即時新聞、盤中快訊、法說會、記者會、政策紅利、概念股、風口、新聞帶單、漲停新聞、爆雷、利空出盡、媒體渲染、群組爆料、股版熱帖、產業趨勢",
                "casual_words": "爆新聞啦、風向轉了、現在就進、看漲、利多出盡、利空測試、盤中爆炸、快訊快訊、我先卡位、衝第一、蹭題材啦、漲停新聞、這新聞大條、來不及啦、馬上跟、記者會炸裂、媒體吹風、政策護航、噴爆、有人知道嗎",
                "typing_habit": "打字很急不愛空格,爆Emoji!!!,會重複字像啦啦啦,驚嘆號!!!狂刷",
                "background_story": "熱愛新聞題材，常常半夜盯彭博、路透，隔天一早發文搶風向。曾因提前爆料電動車補助政策被推爆。",
                "expertise": "新聞分析,趨勢解讀",
                "ending_style": "別忘了持續鎖定我，隨時更新即時新聞、盤中快訊，讓你在市場上贏得先機！快點快點！",
                "paragraph_spacing": "段落間用空行分隔，保持緊湊",
                "content_length": "medium",  # 固定中等內容
                "post_types": {
                    "question": {"weight": 0.5, "style": "快訊疑問，引起討論"},
                    "opinion": {"weight": 0.5, "style": "新聞分析，發表觀點"}
                }
            }
        }
        base = kol_configs.get(kol_nickname, {})

        # 嘗試從 Google Sheets 讀取並覆蓋
        try:
            if KOLSettingsLoader is not None:
                loader = KOLSettingsLoader()
                row = loader.get_kol_row_by_nickname(kol_nickname)
                if row:
                    override_cfg = loader.build_kol_config_dict(row)
                    # 合併：後者覆蓋前者
                    merged = {**base, **override_cfg}
                    return merged
        except Exception as e:
            logger.warning(f"讀取 KOL Sheets 設定失敗，使用預設：{e}")
        return base
    
    def _select_post_type(self, kol_config: Dict[str, str]) -> Dict[str, str]:
        """根據權重隨機選擇發文類型（提問/發表觀點）"""
        import random
        
        post_types = kol_config.get('post_types', {})
        if not post_types:
            # 預設配置
            return {"style": "一般分享"}
        
        # 根據權重選擇
        weights = []
        types = []
        for post_type, config in post_types.items():
            weights.append(config['weight'])
            types.append(config)
        
        selected_config = random.choices(types, weights=weights, k=1)[0]
        return selected_config
    
    def _get_length_requirement(self, content_length: str) -> str:
        """根據內容長度設定返回字數要求"""
        length_requirements = {
            "short": "50-100字，簡潔有力，多用疑問句引起討論",
            "medium": "200-300字，適中長度，平衡分析與互動",
            "long": "400-500字，深度分析，詳細論述"
        }
        return length_requirements.get(content_length, "200-300字，適中長度")
    
    def _extract_stock_codes(self, keywords: str) -> str:
        """從關鍵詞中提取股票代號"""
        # 使用動態 API 獲取股票代號
        try:
            from ..stock.company_info_service import get_company_info_service
            import asyncio
            
            # 同步調用異步函數
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已經在事件循環中，使用備用方案
                return self._extract_stock_codes_fallback(keywords)
            else:
                return loop.run_until_complete(self._extract_stock_codes_async(keywords))
                
        except Exception as e:
            logger.warning(f"動態提取股票代號失敗: {e}")
            return self._extract_stock_codes_fallback(keywords)
    
    async def _extract_stock_codes_async(self, keywords: str) -> str:
        """異步提取股票代號"""
        try:
            from ..stock.company_info_service import get_company_info_service
            service = get_company_info_service()
            
            found_codes = []
            
            # 分割關鍵詞並搜尋
            words = keywords.split()
            for word in words:
                if len(word) >= 2:  # 只搜尋長度大於等於2的詞
                    results = await service.search_company_by_name(word, fuzzy=True)
                    for company in results:
                        found_codes.append(f"{company.company_name}({company.stock_code})")
            
            return ", ".join(found_codes) if found_codes else "無"
            
        except Exception as e:
            logger.warning(f"異步提取股票代號失敗: {e}")
            return self._extract_stock_codes_fallback(keywords)
    
    def _extract_stock_codes_fallback(self, keywords: str) -> str:
        """備用股票代號提取"""
        stock_mapping = {
            "台積電": "2330",
            "聯發科": "2454", 
            "鴻海": "2317",
            "中華電": "2412",
            "台塑": "1301",
            "中鋼": "2002",
            "長榮": "2603",
            "陽明": "2609",
            "萬海": "2615",
            "富邦金": "2881"
        }
        
        found_codes = []
        for stock_name, code in stock_mapping.items():
            if stock_name in keywords:
                found_codes.append(f"{stock_name}({code})")
        
        return ", ".join(found_codes) if found_codes else "無"
    
    def _get_stock_info(self, topic_title: str, topic_keywords: str) -> str:
        """獲取股票詳細資訊"""
        # 使用動態 API 獲取股票資訊
        try:
            from ..stock.company_info_service import get_company_info_service
            import asyncio
            
            # 同步調用異步函數
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已經在事件循環中，使用備用方案
                return self._get_stock_info_fallback(topic_title, topic_keywords)
            else:
                return loop.run_until_complete(self._get_stock_info_async(topic_title, topic_keywords))
                
        except Exception as e:
            logger.warning(f"動態獲取股票資訊失敗: {e}")
            return self._get_stock_info_fallback(topic_title, topic_keywords)
    
    async def _get_stock_info_async(self, topic_title: str, topic_keywords: str) -> str:
        """異步獲取股票資訊"""
        try:
            from ..stock.company_info_service import get_company_info_service
            service = get_company_info_service()
            
            # 從話題標題和關鍵詞中尋找股票
            search_text = f"{topic_title} {topic_keywords}"
            words = search_text.split()
            
            for word in words:
                if len(word) >= 2:  # 只搜尋長度大於等於2的詞
                    results = await service.search_company_by_name(word, fuzzy=True)
                    if results:
                        # 取第一個結果
                        company = results[0]
                        return f"{company.company_name}({company.stock_code}) - {company.industry}產業"
            
            return "無特定股票資訊"
            
        except Exception as e:
            logger.warning(f"異步獲取股票資訊失敗: {e}")
            return self._get_stock_info_fallback(topic_title, topic_keywords)
    
    def _get_stock_info_fallback(self, topic_title: str, topic_keywords: str) -> str:
        """備用股票資訊獲取"""
        stock_mapping = {
            "台積電": {
                "code": "2330",
                "info": "台積電(2330) - 全球最大晶圓代工廠，在AI晶片、5G、車用電子等領域具有領先地位"
            },
            "聯發科": {
                "code": "2454", 
                "info": "聯發科(2454) - 全球知名IC設計公司，專精於手機晶片、5G通訊晶片等產品"
            },
            "鴻海": {
                "code": "2317",
                "info": "鴻海(2317) - 全球最大電子代工廠，主要客戶包括蘋果等國際大廠"
            },
            "中華電": {
                "code": "2412",
                "info": "中華電(2412) - 台灣最大電信業者，提供固網、行動通訊等服務"
            }
        }
        
        # 從話題標題和關鍵詞中尋找股票
        for stock_name, stock_data in stock_mapping.items():
            if stock_name in topic_title or stock_name in topic_keywords:
                return stock_data["info"]
        
        return "無特定股票資訊"
    
    def _format_market_data(self, market_data: Optional[Dict[str, Any]]) -> str:
        """格式化市場數據"""
        if not market_data:
            return "無特定市場數據"
        
        formatted_parts = []
        
        # 股票資訊
        if market_data.get('has_stock', False):
            stock_id = market_data.get('stock_id', '')
            stock_name = market_data.get('stock_name', '')
            if stock_id and stock_name:
                formatted_parts.append(f"相關股票: {stock_name}({stock_id})")
                
                # 添加個股數據資訊
                if market_data.get('stock_data'):
                    stock_data = market_data['stock_data']
                    if stock_data.get('has_ohlc'):
                        formatted_parts.append("包含股價數據")
                    if stock_data.get('has_analysis'):
                        formatted_parts.append("包含技術分析")
                    if stock_data.get('has_financial'):
                        formatted_parts.append("包含財務數據")
                    if stock_data.get('has_revenue'):
                        formatted_parts.append("包含營收數據")
        
        # 其他市場數據
        for key, value in market_data.items():
            if key not in ['has_stock', 'stock_id', 'stock_name', 'stock_type', 'stock_data'] and value:
                formatted_parts.append(f"{key}: {value}")
        
        return "; ".join(formatted_parts) if formatted_parts else "無特定市場數據"
    
    def _format_stock_info(self, market_data: Optional[Dict[str, Any]]) -> str:
        """格式化股票資訊"""
        if not market_data or not market_data.get('has_stock', False):
            return "無特定股票資訊"
        
        stock_id = market_data.get('stock_id', '')
        stock_name = market_data.get('stock_name', '')
        
        if stock_id and stock_name:
            stock_info = f"{stock_name}({stock_id})"
            
            # 添加個股數據詳細資訊
            if market_data.get('stock_data'):
                stock_data = market_data['stock_data']
                details = []
                
                # OHLC 數據
                if stock_data.get('has_ohlc') and stock_data.get('ohlc_data'):
                    ohlc_data = stock_data['ohlc_data']
                    if ohlc_data:
                        latest = ohlc_data[-1]
                        details.append(f"最新價格: {latest.close}")
                
                # 技術分析
                if stock_data.get('has_analysis') and stock_data.get('analysis_data'):
                    analysis_data = stock_data['analysis_data']
                    if analysis_data.technical_indicators:
                        indicators = analysis_data.technical_indicators
                        if 'rsi' in indicators:
                            details.append(f"RSI: {indicators['rsi']:.2f}")
                        if 'ma20' in indicators:
                            details.append(f"MA20: {indicators['ma20']:.2f}")
                
                # 財務數據
                if stock_data.get('has_financial') and stock_data.get('financial_data'):
                    financial_data = stock_data['financial_data']
                    if financial_data.pe_ratio:
                        details.append(f"本益比: {financial_data.pe_ratio}")
                    if financial_data.revenue:
                        details.append(f"營收: {financial_data.revenue/100000000:.1f}億")
                    if financial_data.eps:
                        details.append(f"EPS: {financial_data.eps}")
                
                # 營收數據
                if stock_data.get('has_revenue') and stock_data.get('revenue_data'):
                    revenue_data = stock_data['revenue_data']
                    if revenue_data.current_month_revenue:
                        details.append(f"月營收: {revenue_data.current_month_revenue/100000000:.1f}億")
                    if revenue_data.year_over_year_growth:
                        details.append(f"年增率: {revenue_data.year_over_year_growth:.1f}%")
                    if revenue_data.month_over_month_growth:
                        details.append(f"月增率: {revenue_data.month_over_month_growth:.1f}%")
                
                if details:
                    stock_info += f" - {', '.join(details)}"
            
            return stock_info
        elif stock_id:
            return f"股票代號: {stock_id}"
        else:
            return "無特定股票資訊"
    
    def _clean_hashtags(self, content: str) -> str:
        """移除內容中的所有 hashtag"""
        import re
        # 移除所有以 # 開頭的詞彙
        cleaned = re.sub(r'#\w+', '', content)
        # 移除多餘的空格和換行
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        return cleaned
    
    def _truncate_content(self, content: str, max_length: int) -> str:
        """根據字數要求截斷內容"""
        if len(content) <= max_length:
            return content
        
        # 直接截斷到指定長度
        truncated = content[:max_length]
        
        # 尋找最後一個句號、問號或感嘆號
        last_sentence_end = max(
            truncated.rfind('。'),
            truncated.rfind('？'),
            truncated.rfind('！'),
            truncated.rfind('...')
        )
        
        # 如果找到句子結束點且在合理範圍內，使用它
        if last_sentence_end > max_length * 0.7:  # 提高到70%
            return truncated[:last_sentence_end + 1]
        else:
            # 否則直接截斷並添加省略號
            return truncated.rstrip() + '...'
    
    def generate_title(self, request: ContentRequest, used_titles: Optional[List[str]] = None) -> str:
        """
        生成標題
        
        Args:
            request: 內容生成請求
            
        Returns:
            生成的標題
        """
        try:
            # 獲取 KOL 詳細設定
            kol_config = self._get_kol_config(request.kol_nickname)
            used_titles = used_titles or []
            random_seed = random.randint(1000, 9999)
            # 常見的制式化/AI味標題片語（避免）
            banned_generic_phrases = [
                "台股震盪整理", "技術面分析", "怎麼看", "該怎麼看", "開盤指數上漲拉回",
                "內外資分歧", "大盤走勢", "市場觀望", "投資人信心", "短線操作"
            ]
            # 合併 KOL 自訂禁用詞
            banned_override = kol_config.get('banned_generic_phrases_override', []) or []
            if isinstance(banned_override, list):
                banned_generic_phrases.extend([p for p in banned_override if p and p not in banned_generic_phrases])
            
            # 隨機選擇個人化開場（如果有的話）
            openers = kol_config.get('signature_openers', []) or []
            patterns = kol_config.get('signature_patterns', []) or []
            opener_hint = f"可選用開場：{', '.join(openers[:3])}" if openers else ""
            pattern_hint = f"可選用句型：{', '.join(patterns[:2])}" if patterns else ""
            
            # 語氣數值轉換為文字指導
            tone_override = kol_config.get('tone_vector_override', {})
            tone_guidance = ""
            if tone_override:
                formal = tone_override.get('formal_level', 5)
                emotion = tone_override.get('emotion_intensity', 5)
                confidence = tone_override.get('confidence_level', 5)
                tone_guidance = f"語氣調性：正式度{formal}/10, 情緒強度{emotion}/10, 自信度{confidence}/10"

            system_prompt = f"""
你是 {request.kol_nickname}，一個專業的 {request.kol_persona}。

角色設定：
- 暱稱：{request.kol_nickname}
- 人設：{request.kol_persona}
- 內容類型：{kol_config.get('content_type', request.content_type)}
- 目標受眾：{kol_config.get('target_audience', request.target_audience)}
- 語氣風格：{kol_config.get('tone_style', '專業友善')}
{tone_guidance}
- 常用詞彙：{kol_config.get('common_words', '')}
- 口語化用詞：{kol_config.get('casual_words', '')}
- 打字習慣：{kol_config.get('typing_habit', '正常標點')}
- 前導故事：{kol_config.get('background_story', '')}
- 專長領域：{kol_config.get('expertise', '')}
{opener_hint}
{pattern_hint}

標題生成要求：
1. 標題要吸引人，符合社群媒體風格
2. **長度控制在12-20字，簡潔有力**
3. 要完全符合角色的語氣、風格和用詞習慣
4. 使用角色的常用詞彙和口語化用詞
5. 要與話題相關，體現專業領域
6. 如果有股票代號，要包含在標題中
7. **絕對禁止在標題加上【{request.kol_nickname}】或任何名字標註**
8. **重要：標題要體現你獨特的視角和專業領域，避免與其他 KOL 重複**
9. **從你的專業角度切入話題，展現獨特的觀點或分析角度**
10. **標題要有記憶點，讓人一看就知道是你的風格**
11. **每個 KOL 的標題必須完全不同，體現各自的專業特色**
12. **避免使用相同的詞彙組合，要有獨特的切入點**
13. 避免使用以下常見模板詞：{', '.join(banned_generic_phrases)}
14. 本次變體隨機種子：{random_seed}
"""
            
            # 嘗試注入每位 KOL 的簽名式元素，提升辨識度
            signature_openers = ", ".join(kol_config.get('signature_openers', []) or [])
            signature_patterns = ", ".join(kol_config.get('signature_patterns', []) or [])

            # 避免使用已產出的標題或其明顯片語
            previous_titles_block = "\n".join([f"- {t}" for t in used_titles[:8]]) if used_titles else "(無)"

            user_prompt = f"""
話題：{request.topic_title}
關鍵詞：{request.topic_keywords}
股票代號：{self._extract_stock_codes(request.topic_keywords)}

請生成一個完全符合 {request.kol_nickname} 風格的標題。

個人化要求：
- 用你的口吻和專業角度重新詮釋這個話題
- 展現你獨特的分析視角，不要跟別人一樣
- 標題要讓人一看就知道是你的風格
- **絕對不要在標題加上自己的名字或【】符號**

請不要重複以下已生成標題或其明顯片語：
{previous_titles_block}

請只回傳標題，不要其他說明文字。
"""
            
            def _is_bad_title(t: str) -> bool:
                lowered = t.strip().lower()
                # 1) 與已用標題重複
                if any(lowered == ut.strip().lower() for ut in used_titles):
                    return True
                # 2) 命中通用禁詞
                if any(phrase in t for phrase in banned_generic_phrases):
                    return True
                # 3) 過於通用的模式（過短或過長會另外處理）
                generic_patterns = [
                    "台股", "大盤", "技術面", "震盪", "整理", "分析"
                ]
                generic_hits = sum(1 for g in generic_patterns if g in t)
                return generic_hits >= 3

            title = ""
            attempts = 0
            attempts_max = int(kol_config.get('title_retry_max', 3) or 3)
            while attempts < attempts_max:
                attempts += 1
                response = self.client.chat.completions.create(
                    model=self.title_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.title_temperature + random.uniform(-0.1, 0.1),
                    max_tokens=self.max_tokens_title,
                    frequency_penalty=self.title_frequency_penalty,
                    presence_penalty=self.title_presence_penalty
                )
                candidate = response.choices[0].message.content.strip()

                # 長度微調到 12-22 字區間
                if len(candidate) < 12:
                    tail = kol_config.get('tail_word', '...')
                    candidate = (candidate + tail)[:14]
                if len(candidate) > 22:
                    candidate = candidate[:22].rstrip()
                    if not candidate.endswith(('。', '！', '？', '...')):
                        candidate += '...'

                if not _is_bad_title(candidate):
                    title = candidate
                    break
                else:
                    logger.info(f"標題候選不合格，重試第 {attempts} 次: {candidate}")

            # 若三次都不合格，採用最後一次候選
            if not title:
                title = candidate
            
            logger.info(f"成功生成標題: {title} ({len(title)}字)")
            
            return title
            
        except Exception as e:
            logger.error(f"標題生成失敗: {e}")
            # 改善 fallback - 不加名字，用個人化尾詞
            tail = kol_config.get('tail_word', '')
            return f"{request.topic_title[:15]}{tail}"
    
    def generate_content(self, request: ContentRequest, title: str) -> str:
        """
        生成內容
        
        Args:
            request: 內容生成請求
            title: 已生成的標題
            
        Returns:
            生成的內容
        """
        try:
            # 獲取 KOL 詳細設定
            kol_config = self._get_kol_config(request.kol_nickname)
            
            # 獲取固定的字數設定
            content_length = kol_config.get('content_length', 'medium')
            length_requirement = self._get_length_requirement(content_length)
            
            # 根據 QuestionRatio 決定發文類型
            question_ratio = float(kol_config.get('question_ratio', 0.5) or 0.5)
            is_question_post = random.random() < question_ratio
            
            # 獲取互動開場詞
            interaction_starters = kol_config.get('interaction_starters', []) or []
            selected_starter = random.choice(interaction_starters) if interaction_starters else "大家怎麼看"
            
            # 建構增強的個人化 prompt
            system_prompt = self._build_enhanced_content_system_prompt(request, kol_config, is_question_post)
            
            user_prompt = self._build_enhanced_content_user_prompt(request, title, kol_config, selected_starter, is_question_post)
            
            # 在user_prompt中添加字數要求
            user_prompt += f"\n\n字數要求：{length_requirement} - 嚴格控制字數，不得超過上限"
            
            response = self.client.chat.completions.create(
                model=self.content_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens_content
            )
            
            content = response.choices[0].message.content.strip()
            
            # 後處理：移除 hashtag
            content = self._clean_hashtags(content)
            
            # 後處理：根據固定的字數設定控制字數
            if content_length == 'short':
                content = self._truncate_content(content, 90)  # 更嚴格的字數控制
            elif content_length == 'medium':
                content = self._truncate_content(content, 280)  # 更嚴格的字數控制
            elif content_length == 'long':
                content = self._truncate_content(content, 480)  # 更嚴格的字數控制
            
            logger.info(f"成功生成內容，長度: {len(content)} 字")
            
            return content
            
        except Exception as e:
            logger.error(f"內容生成失敗: {e}")
            return f"今天來聊聊 {request.topic_title}...更多分析請關注我的後續發文。"
    
    def generate_hashtags(self, request: ContentRequest) -> str:
        """
        生成 hashtags
        
        Args:
            request: 內容生成請求
            
        Returns:
            生成的 hashtags
        """
        try:
            # 根據內容類型和關鍵詞生成 hashtags
            base_tags = ["#台股", "#投資"]
            
            if "technical" in request.content_type.lower():
                base_tags.extend(["#技術分析", "#K線"])
            elif "macro" in request.content_type.lower():
                base_tags.extend(["#總經", "#經濟分析"])
            
            # 從關鍵詞中提取
            keywords = request.topic_keywords.split(',')
            for keyword in keywords[:3]:
                keyword = keyword.strip()
                if keyword and len(keyword) < 10:
                    base_tags.append(f"#{keyword}")
            
            return " ".join(base_tags[:5])  # 限制最多5個標籤
            
        except Exception as e:
            logger.error(f"Hashtag 生成失敗: {e}")
            return "#台股 #投資 #分析"
    
    def generate_complete_content(self, request: ContentRequest, used_titles: Optional[List[str]] = None) -> GeneratedContent:
        """
        生成完整內容（標題 + 內容 + hashtags）
        
        Args:
            request: 內容生成請求
            
        Returns:
            完整的生成內容結果
        """
        try:
            logger.info(f"開始為 {request.kol_nickname} 生成內容，話題: {request.topic_title}")
            
            # 步驟1: 生成標題（帶入去重上下文）
            title = self.generate_title(request, used_titles=used_titles)
            
            # 步驟2: 生成內容
            content = self.generate_content(request, title)
            
            # 步驟3: 後處理 - 移除任何殘留的 hashtag
            content = self._clean_hashtags(content)
            
            # 步驟4: 重新應用字數控制（因為可能被 _clean_hashtags 影響）
            kol_config = self._get_kol_config(request.kol_nickname)
            content_length = kol_config.get('content_length', 'medium')
            
            if content_length == 'short':
                content = self._truncate_content(content, 90)  # 更嚴格的字數控制
            elif content_length == 'medium':
                content = self._truncate_content(content, 280)  # 更嚴格的字數控制
            elif content_length == 'long':
                content = self._truncate_content(content, 480)  # 更嚴格的字數控制
            
            # 組合最終內容（不包含 hashtags）
            final_content = f"{title}\n\n{content}"
            
            result = GeneratedContent(
                title=title,
                content=final_content,
                hashtags="",  # 不生成 hashtags
                success=True
            )
            
            logger.info(f"內容生成完成，標題: {title}")
            return result
            
        except Exception as e:
            logger.error(f"完整內容生成失敗: {e}")
            return GeneratedContent(
                title="",
                content="",
                hashtags="",
                success=False,
                error_message=str(e)
            )

    def _build_dynamic_system_prompt(self, request: ContentRequest, kol_config: Dict[str, str], market_data: Optional[Dict[str, Any]]) -> str:
        """根據資料類型和股票標籤動態構建系統提示詞"""
        
        # 基礎角色設定
        base_prompt = f"""
你是 {request.kol_nickname}，一個專業的 {request.kol_persona}。

角色設定：
- 暱稱：{request.kol_nickname}
- 人設：{request.kol_persona}
- 內容類型：{kol_config.get('content_type', request.content_type)}
- 目標受眾：{kol_config.get('target_audience', request.target_audience)}
- 語氣風格：{kol_config.get('tone_style', '專業友善')}
- 常用詞彙：{kol_config.get('common_words', '')}
- 口語化用詞：{kol_config.get('casual_words', '')}
- 打字習慣：{kol_config.get('typing_habit', '正常標點')}
- 前導故事：{kol_config.get('background_story', '')}
- 專長領域：{kol_config.get('expertise', '')}
"""

        # 根據股票類型調整內容風格
        stock_type_prompt = self._get_stock_type_prompt(market_data)
        
        # 根據數據類型調整分析深度
        data_type_prompt = self._get_data_type_prompt(market_data)
        
        # 根據市場情境調整內容重點
        market_context_prompt = self._get_market_context_prompt(request, market_data)
        
        # 根據KOL人設調整專業角度
        persona_specific_prompt = self._get_persona_specific_prompt(request.kol_persona, market_data)
        
        # 組合所有提示詞
        full_prompt = f"""{base_prompt}

{stock_type_prompt}

{data_type_prompt}

{market_context_prompt}

{persona_specific_prompt}

內容要求：
1. **字數要求：{kol_config.get('content_length', 'medium')} - 嚴格控制字數**
2. 要完全符合角色的語氣、風格和用詞習慣
3. 大量使用角色的常用詞彙和口語化用詞
4. 按照角色的打字習慣來寫作（標點符號、格式等）
5. 體現角色的專業領域和背景故事
6. 包含對話題的深度分析或觀點
7. 段落間距：{kol_config.get('paragraph_spacing', '正常空行分隔')}
8. 結尾語：{kol_config.get('ending_style', '感謝閱讀，歡迎討論')}
9. 不要有明顯的 AI 生成痕跡
10. 避免投資建議，只做分析分享
11. **絕對禁止使用任何 hashtag 標籤**
12. **內容結尾直接使用角色的專屬結尾語，不要添加任何標籤**
"""
        
        return full_prompt

    def _get_stock_type_prompt(self, market_data: Optional[Dict[str, Any]]) -> str:
        """根據股票類型生成特定的提示詞"""
        if not market_data or not market_data.get('has_stock', False):
            return "股票類型：無特定股票"
        
        stock_type = market_data.get('stock_type', '')
        stock_name = market_data.get('stock_name', '')
        
        if '科技' in stock_type or '半導體' in stock_type or '電子' in stock_type:
            return f"""
股票類型：科技股 ({stock_name})
- 重點分析：技術創新、產品週期、市場競爭
- 用詞風格：技術導向、創新思維、前瞻性
- 分析角度：研發投入、專利技術、供應鏈地位
- 風險提醒：技術迭代、市場變化、競爭加劇
"""
        elif '金融' in stock_type or '銀行' in stock_type or '保險' in stock_type:
            return f"""
股票類型：金融股 ({stock_name})
- 重點分析：政策環境、利率變化、監管要求
- 用詞風格：穩健務實、風險意識、合規導向
- 分析角度：資本充足率、壞帳率、淨利差
- 風險提醒：政策風險、信用風險、市場風險
"""
        elif '傳產' in stock_type or '製造' in stock_type or '營建' in stock_type:
            return f"""
股票類型：傳產股 ({stock_name})
- 重點分析：產業週期、供需關係、成本結構
- 用詞風格：務實穩健、產業經驗、長期思維
- 分析角度：產能利用率、原物料成本、訂單能見度
- 風險提醒：景氣循環、成本波動、競爭加劇
"""
        else:
            return f"""
股票類型：一般股票 ({stock_name})
- 重點分析：基本面、技術面、籌碼面
- 用詞風格：平衡客觀、專業分析、風險提醒
- 分析角度：綜合評估、多面向分析
- 風險提醒：市場風險、個股風險
"""

    def _get_data_type_prompt(self, market_data: Optional[Dict[str, Any]]) -> str:
        """根據數據類型生成特定的提示詞"""
        if not market_data or not market_data.get('stock_data'):
            return "數據類型：無特定數據"
        
        stock_data = market_data['stock_data']
        prompts = []
        
        if stock_data.get('has_ohlc'):
            prompts.append("""
OHLC數據分析：
- 重點關注：價格趨勢、成交量變化、支撐阻力位
- 技術指標：移動平均線、RSI、MACD等
- 分析角度：趨勢判斷、轉折點識別、量價關係
""")
        
        if stock_data.get('has_financial'):
            prompts.append("""
財務數據分析：
- 重點關注：營收成長、獲利能力、財務結構
- 關鍵指標：本益比、ROE、負債比率等
- 分析角度：基本面評估、成長性分析、風險評估
""")
        
        if stock_data.get('has_revenue'):
            prompts.append("""
營收數據分析：
- 重點關注：月營收、年增率、月增率
- 趨勢分析：營收動能、季節性、成長性
- 分析角度：營收品質、成長動能、產業地位
""")
        
        if stock_data.get('has_analysis'):
            prompts.append("""
技術分析數據：
- 重點關注：技術指標、圖表形態、趨勢線
- 分析工具：K線、均線、指標等
- 分析角度：技術面判斷、進出場時機、風險控制
""")
        
        return "\n".join(prompts) if prompts else "數據類型：基礎市場資訊"

    def _get_market_context_prompt(self, request: ContentRequest, market_data: Optional[Dict[str, Any]]) -> str:
        """根據市場情境生成特定的提示詞"""
        topic_title = request.topic_title.lower()
        topic_keywords = request.topic_keywords.lower()
        
        if '大盤' in topic_title or '指數' in topic_title:
            return """
市場情境：大盤指數分析
- 重點分析：大盤趨勢、市場情緒、資金流向
- 用詞風格：宏觀視角、市場觀測、趨勢判斷
- 分析角度：技術面、籌碼面、消息面
- 個股關聯：分析個股與大盤的相關性
"""
        elif '財報' in topic_title or '法說' in topic_title:
            return """
市場情境：財報法說分析
- 重點分析：財報數據、法說重點、未來展望
- 用詞風格：數據導向、專業分析、前瞻性
- 分析角度：營收獲利、產業趨勢、競爭優勢
- 風險提醒：財報風險、展望不確定性
"""
        elif '產業' in topic_title or '趨勢' in topic_title:
            return """
市場情境：產業趨勢分析
- 重點分析：產業發展、技術演進、市場變化
- 用詞風格：產業視角、趨勢觀察、前瞻思維
- 分析角度：產業週期、競爭格局、成長動能
- 個股關聯：分析個股在產業中的定位
"""
        else:
            return """
市場情境：一般市場分析
- 重點分析：綜合評估、多面向分析
- 用詞風格：平衡客觀、專業分析
- 分析角度：基本面、技術面、籌碼面
"""

    def _get_persona_specific_prompt(self, kol_persona: str, market_data: Optional[Dict[str, Any]]) -> str:
        """根據KOL人設生成特定的提示詞"""
        if '技術派' in kol_persona:
            return """
技術派專業角度：
- 分析重點：技術指標、圖表形態、趨勢分析
- 用詞特色：技術術語、指標解讀、趨勢判斷
- 內容結構：技術分析 → 趨勢判斷 → 風險提醒
- 專業展現：使用專業技術指標，展現技術分析能力
"""
        elif '總經派' in kol_persona:
            return """
總經派專業角度：
- 分析重點：宏觀經濟、政策影響、產業趨勢
- 用詞特色：經濟術語、政策解讀、趨勢分析
- 內容結構：宏觀分析 → 政策影響 → 產業展望
- 專業展現：結合經濟數據，展現宏觀分析能力
"""
        elif '新聞派' in kol_persona:
            return """
新聞派專業角度：
- 分析重點：新聞事件、市場反應、影響評估
- 用詞特色：即時性、新聞敏感度、影響分析
- 內容結構：新聞解讀 → 市場影響 → 後續觀察
- 專業展現：快速反應市場變化，展現新聞分析能力
"""
        elif '籌碼派' in kol_persona:
            return """
籌碼派專業角度：
- 分析重點：資金流向、主力動向、籌碼分布
- 用詞特色：籌碼術語、資金分析、主力追蹤
- 內容結構：籌碼分析 → 資金流向 → 主力動向
- 專業展現：分析籌碼變化，展現資金追蹤能力
"""
        elif '情緒派' in kol_persona:
            return """
情緒派專業角度：
- 分析重點：市場情緒、投資心理、群眾行為
- 用詞特色：情緒描述、心理分析、行為解讀
- 內容結構：情緒分析 → 心理解讀 → 行為預測
- 專業展現：分析市場心理，展現情緒分析能力
"""
        else:
            return """
一般專業角度：
- 分析重點：綜合分析、多面向評估
- 用詞特色：專業客觀、平衡分析
- 內容結構：分析 → 判斷 → 提醒
- 專業展現：展現專業分析能力
"""

    def _build_dynamic_user_prompt(self, request: ContentRequest, title: str, market_data: Optional[Dict[str, Any]]) -> str:
        """根據資料類型和股票標籤動態構建用戶提示詞"""
        
        # 基礎提示詞
        base_prompt = f"""
標題：{title}
話題：{request.topic_title}
關鍵詞：{request.topic_keywords}
"""
        
        # 股票特定資訊
        stock_specific = self._get_stock_specific_prompt(market_data)
        
        # 數據特定資訊
        data_specific = self._get_data_specific_prompt(market_data)
        
        # 市場特定資訊
        market_specific = self._get_market_specific_prompt(request, market_data)
        
        # 組合完整提示詞
        full_prompt = f"""{base_prompt}

{stock_specific}

{data_specific}

{market_specific}

請為這個標題生成完全符合 {request.kol_nickname} 風格的內容。
記住：要完全按照角色的語氣、用詞、打字習慣來寫作！

⚠️ 重要要求：
1. 絕對不要使用任何 hashtag 標籤
2. 內容結尾直接使用角色的專屬結尾語，不要添加任何標籤
3. 如果有股票，要具體指出股票名稱和代號，不要用模糊用詞
4. 內容要專業且可信，避免過度聳動的用詞
5. 根據提供的數據類型進行相應的分析
6. 如果內容中出現任何 # 符號，請立即移除
"""
        
        return full_prompt

    def _get_stock_specific_prompt(self, market_data: Optional[Dict[str, Any]]) -> str:
        """獲取股票特定的提示詞"""
        if not market_data or not market_data.get('has_stock', False):
            return "股票資訊：無特定股票"
        
        stock_id = market_data.get('stock_id', '')
        stock_name = market_data.get('stock_name', '')
        stock_type = market_data.get('stock_type', '')
        
        prompt = f"股票資訊：{stock_name}({stock_id}) - {stock_type}"
        
        if market_data.get('stock_data'):
            stock_data = market_data['stock_data']
            details = []
            
            if stock_data.get('has_ohlc') and stock_data.get('ohlc_data'):
                ohlc_data = stock_data['ohlc_data']
                if ohlc_data:
                    latest = ohlc_data[-1]
                    details.append(f"最新價格: {latest.close}")
            
            if stock_data.get('has_analysis') and stock_data.get('analysis_data'):
                analysis_data = stock_data['analysis_data']
                if hasattr(analysis_data, 'technical_indicators') and analysis_data.technical_indicators:
                    indicators = analysis_data.technical_indicators
                    if 'rsi' in indicators:
                        details.append(f"RSI: {indicators['rsi']:.2f}")
                    if 'ma20' in indicators:
                        details.append(f"MA20: {indicators['ma20']:.2f}")
            
            if details:
                prompt += f"\n技術數據：{', '.join(details)}"
        
        return prompt

    def _get_data_specific_prompt(self, market_data: Optional[Dict[str, Any]]) -> str:
        """獲取數據特定的提示詞"""
        if not market_data or not market_data.get('stock_data'):
            return "數據資訊：無特定數據"
        
        stock_data = market_data['stock_data']
        prompts = []
        
        if stock_data.get('has_ohlc'):
            prompts.append("包含股價數據(開高低收、成交量)")
        
        if stock_data.get('has_financial'):
            prompts.append("包含財務數據(本益比、ROE、營收等)")
        
        if stock_data.get('has_revenue'):
            prompts.append("包含營收數據(月營收、年增率、月增率)")
        
        if stock_data.get('has_analysis'):
            prompts.append("包含技術分析數據(RSI、均線、指標等)")
        
        return f"數據資訊：{', '.join(prompts)}" if prompts else "數據資訊：基礎市場資訊"

    def _get_market_specific_prompt(self, request: ContentRequest, market_data: Optional[Dict[str, Any]]) -> str:
        """獲取市場特定的提示詞"""
        topic_title = request.topic_title.lower()
        
        if '大盤' in topic_title or '指數' in topic_title:
            return "市場情境：大盤指數分析，需要結合大盤趨勢和個股表現"
        elif '財報' in topic_title or '法說' in topic_title:
            return "市場情境：財報法說分析，重點在數據解讀和未來展望"
        elif '產業' in topic_title or '趨勢' in topic_title:
            return "市場情境：產業趨勢分析，需要宏觀視角和產業洞察"
        else:
            return "市場情境：一般市場分析，需要綜合評估和專業分析"

    def _build_enhanced_content_system_prompt(self, request: ContentRequest, kol_config: Dict[str, str], is_question_post: bool) -> str:
        """建構增強版內容生成系統 prompt"""
        
        # 語氣數值轉換
        tone_override = kol_config.get('tone_vector_override', {})
        tone_guidance = ""
        if tone_override:
            formal = tone_override.get('formal_level', 5)
            emotion = tone_override.get('emotion_intensity', 5)
            confidence = tone_override.get('confidence_level', 5)
            urgency = tone_override.get('urgency_level', 5)
            interaction = tone_override.get('interaction_level', 5)
            tone_guidance = f"""
語氣調性指導：
- 正式度：{formal}/10 ({'較口語' if formal <= 4 else '較正式' if formal >= 7 else '適中'})
- 情緒強度：{emotion}/10 ({'冷靜' if emotion <= 4 else '激昂' if emotion >= 7 else '適中'})
- 自信度：{confidence}/10 ({'謹慎' if confidence <= 4 else '自信' if confidence >= 7 else '適中'})
- 急迫感：{urgency}/10 ({'從容' if urgency <= 4 else '急迫' if urgency >= 7 else '適中'})
- 互動性：{interaction}/10 ({'內斂' if interaction <= 4 else '互動強' if interaction >= 7 else '適中'})
"""

        post_type_guidance = "以提問方式引導討論，多用疑問句" if is_question_post else "以觀點分析為主，展現專業見解"
        
        return f"""
你是 {request.kol_nickname}，一個專業的 {request.kol_persona}。

角色設定：
- 暱稱：{request.kol_nickname}
- 人設：{request.kol_persona}
- 內容類型：{kol_config.get('content_type', request.content_type)}
- 目標受眾：{kol_config.get('target_audience', request.target_audience)}
- 語氣風格：{kol_config.get('tone_style', '專業友善')}
{tone_guidance}
- 常用詞彙：{kol_config.get('common_words', '')}
- 口語化用詞：{kol_config.get('casual_words', '')}
- 打字習慣：{kol_config.get('typing_habit', '正常標點')}
- 前導故事：{kol_config.get('background_story', '')}
- 專長領域：{kol_config.get('expertise', '')}

內容生成要求：
1. 完全符合你的個人語氣、風格和用詞習慣
2. 大量使用你的常用詞彙和口語化用詞
3. 按照你的打字習慣來寫作（標點符號、格式等）
4. 體現你的專業領域和背景故事
5. {post_type_guidance}
6. 段落間距：{kol_config.get('paragraph_spacing', '正常空行分隔')}
7. 結尾風格：{kol_config.get('ending_style', '感謝閱讀，歡迎討論')}
8. 避免 AI 生成痕跡，要像真人在社群發文
9. 避免投資建議，只做分析分享
10. **絕對禁止使用任何 hashtag 標籤**
11. **內容結尾直接使用你的專屬結尾語，不要添加任何標籤**
"""

    def _build_enhanced_content_user_prompt(self, request: ContentRequest, title: str, kol_config: Dict[str, str], 
                                           selected_starter: str, is_question_post: bool) -> str:
        """建構增強版內容生成用戶 prompt"""
        
        interaction_guidance = f"適當使用「{selected_starter}」的方式與讀者互動" if is_question_post else f"可以用「{selected_starter}」來引起討論"
        
        return f"""
標題：{title}
話題：{request.topic_title}
關鍵詞：{request.topic_keywords}

請用你的風格為這個標題寫一篇貼文內容。

個人化要求：
- 用你獨特的專業角度來分析這個話題
- 完全按照你的語氣、用詞、打字習慣來寫
- {interaction_guidance}
- {'以提問形式引導讀者思考和討論' if is_question_post else '展現你的專業分析和獨特觀點'}
- 內容要自然流暢，像真人發文，不要有 AI 味

重要提醒：
- 不要重複標題內容
- 不要使用任何 # 符號或標籤
- 結尾使用你的專屬風格
- 展現你的個人特色和專業背景
"""

# 工廠函數
def create_content_generator() -> ContentGenerator:
    """創建內容生成器實例"""
    return ContentGenerator()
