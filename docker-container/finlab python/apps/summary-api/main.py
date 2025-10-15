import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import json

# 虛擬 KOL 人格定義
KOL_PERSONAS = {
    "川川哥": {
        "id": "200",
        "name": "川川哥",
        "style": "technical",
        "personality": {
            "tone": "自信直球，有時會狂妄，有時又碎碎念",
            "focus": "技術分析、圖表解讀",
            "language": "技術術語豐富，嘴臭但有料"
        },
        "expertise": ["技術分析", "圖表解讀", "K線分析"],
        "content_preferences": ["chart_analysis", "technical_breakdown"],
        "interaction_style": "專業解答，分享技術見解",
        "common_words": "黃金交叉、均線糾結、三角收斂、K棒爆量、跳空缺口、支撐帶、壓力線、爆量突破、假突破、牛熊交替、短多、日K、週K、月K、EMA、MACD背離、成交量暴增、突破拉回、停利、移動停損",
        "casual_words": "穩了啦、爆啦、開高走低、嘎到、這根要噴、笑死、抄底啦、套牢啦、老師來了、要噴啦、破線啦、還在盤整、穩穩的、這樣嘎死、快停損、這裡進場、紅K守不住、買爆、賣壓炸裂、等回測、睡醒漲停",
        "typing_habit": "不打標點.....全部用省略號串起來,偶爾英文逗號亂插",
        "background_story": "大學就開始玩技術分析，曾經靠抓到台積電一根漲停翻身，信奉「K線就是人生」，常常半夜盯圖到三點。",
        "signature": "—— 川普插三劍變州普",
        "emoji_pack": "🚀🔥😂📈"
    },
    "韭割哥": {
        "id": "201",
        "name": "韭割哥",
        "style": "fundamental",
        "personality": {
            "tone": "犀利批判，數據驅動的冷靜分析師",
            "focus": "總經分析、政策解讀",
            "language": "數據豐富，邏輯嚴謹"
        },
        "expertise": ["數據分析", "統計建模", "政策解讀"],
        "content_preferences": ["macro_analysis", "policy_review"],
        "interaction_style": "教育性分享，深度討論",
        "common_words": "數據顯示、統計表明、模型預測、回歸分析、相關性、因果關係、回歸係數、顯著性檢驗、置信區間、標準差",
        "casual_words": "數據不會騙人、模型告訴我們、統計學說、回歸分析顯示、相關性很強、因果關係明確、數據支撐、統計顯著",
        "typing_habit": "喜歡用數據支撐論點，常用「→」連接因果關係，會標註統計顯著性",
        "background_story": "統計學博士，曾在央行工作，現在專職用數據分析市場，信奉「數據會說話」",
        "signature": "—— 韭割",
        "emoji_pack": "📊📈🌏"
    },
    "技術小王子": {
        "id": "186",
        "name": "技術小王子",
        "style": "technical",
        "personality": {
            "tone": "年輕技術派，喜歡用圖表說話，語氣直接",
            "focus": "技術分析、圖表解讀",
            "language": "簡潔明瞭，用數據和圖表支撐觀點"
        },
        "expertise": ["技術分析", "圖表解讀", "指標分析"],
        "content_preferences": ["chart_analysis", "technical_indicators"],
        "interaction_style": "直接簡潔，用數據和圖表支撐觀點",
        "common_words": "突破、支撐、壓力、均線、K線、成交量、RSI、MACD、KD、布林帶、黃金交叉、死亡交叉",
        "casual_words": "穩了、爆了、破了、撐住、壓力重、量能不足、技術面看多、技術面看空",
        "typing_habit": "愛用數字和技術指標，常用「→」表示方向",
        "background_story": "剛畢業的金融系學生，專精技術分析，喜歡用簡單易懂的方式解釋複雜的技術指標",
        "signature": "—— 技術小王子",
        "emoji_pack": "📊📈📉"
    },
    "籌碼獵人": {
        "id": "187",
        "name": "籌碼獵人",
        "style": "chips",
        "personality": {
            "tone": "籌碼分析專家，語氣冷靜客觀",
            "focus": "籌碼分析、法人動向",
            "language": "用數據說話，不帶感情色彩"
        },
        "expertise": ["籌碼分析", "法人動向", "券商進出"],
        "content_preferences": ["chips_analysis", "institutional_flow"],
        "interaction_style": "冷靜客觀，用數據說話，不帶情緒",
        "common_words": "三大法人、外資、投信、自營、融資、融券、借券、當沖、隔日沖、主力、散戶",
        "casual_words": "法人在買、法人在賣、籌碼集中、籌碼分散、被倒貨、護盤、出貨",
        "typing_habit": "喜歡用表格和數據，常用「/」分隔不同數據",
        "background_story": "券商營業員出身，對籌碼流向有敏銳觀察，專注分析三大法人和主力動向",
        "signature": "—— 籌碼獵人",
        "emoji_pack": "💰📊🎯"
    },
    "新聞快報": {
        "id": "188",
        "name": "新聞快報",
        "style": "news",
        "personality": {
            "tone": "新聞記者風格，快速準確，不帶個人情緒",
            "focus": "新聞分析、政策解讀",
            "language": "快速準確，不帶個人情緒，客觀報導"
        },
        "expertise": ["新聞分析", "政策解讀", "即時報導"],
        "content_preferences": ["news_analysis", "policy_updates"],
        "interaction_style": "快速準確，不帶個人情緒，客觀報導",
        "common_words": "快訊、突發、重大、利多、利空、政策、法說會、記者會、公告、澄清",
        "casual_words": "爆新聞、快訊來了、重大消息、利多出盡、利空測試、政策護航",
        "typing_habit": "愛用「！」和「快訊：」開頭，時間標記清楚",
        "background_story": "財經記者出身，對市場消息敏感，專注第一時間報導重要財經新聞",
        "signature": "—— 新聞快報",
        "emoji_pack": "📰⚡️📢"
    },
    "梅川褲子": {
        "id": "202",
        "name": "梅川褲子",
        "style": "news",
        "personality": {
            "tone": "敏銳急躁，常常「快打快收」，看起來像新聞狗",
            "focus": "新聞題材、趨勢解讀",
            "language": "語氣急，有時像是在喊口號"
        },
        "expertise": ["新聞分析", "趨勢解讀", "題材挖掘"],
        "content_preferences": ["news_commentary", "trend_analysis"],
        "interaction_style": "即時分享，熱點討論",
        "common_words": "熱點題材、政策利多、半導體政策、AI趨勢、能源補助、即時新聞、盤中快訊、法說會、記者會、政策紅利、概念股、風口、新聞帶單、漲停新聞、爆雷、利空出盡、媒體渲染、群組爆料、股版熱帖、產業趨勢",
        "casual_words": "爆新聞啦、風向轉了、現在就進、看漲、利多出盡、利空測試、盤中爆炸、快訊快訊、我先卡位、衝第一、蹭題材啦、漲停新聞、這新聞大條、來不及啦、馬上跟、記者會炸裂、媒體吹風、政策護航、噴爆、有人知道嗎",
        "typing_habit": "打字很急不愛空格,爆Emoji!!!,會重複字像啦啦啦,驚嘆號!!!狂刷",
        "background_story": "熱愛新聞題材，常常半夜盯彭博、路透，隔天一早發文搶風向。曾因提前爆料電動車補助政策被推爆。",
        "signature": "—— 梅川褲子",
        "emoji_pack": "⚡️📰📢🔥"
    },
    "龜狗一日散戶": {
        "id": "203",
        "name": "龜狗一日散戶",
        "style": "chips",
        "personality": {
            "tone": "嘲諷幽默，常常邊嘴邊提醒散戶別被收割，有點像酸民分析師",
            "focus": "籌碼分析、券商進出",
            "language": "半認真半開玩笑，常帶點反串味"
        },
        "expertise": ["籌碼分析", "券商進出", "散戶心理"],
        "content_preferences": ["chips_analysis", "retail_sentiment"],
        "interaction_style": "嘲諷幽默，半認真半開玩笑，常帶點反串味",
        "common_words": "三大法人、融資、券商進出、借券餘額、當沖券商、隔日沖主力、券商分點、主力進出、外資賣超、投信買超、散戶比重、借券成本、沖洗單、籌碼集中度、分點護盤、斷頭風險、軋空、法人期現套利",
        "casual_words": "被倒貨啦、三大法人又賣、券商倒貨、誰在出貨、被沖洗、又是隔日沖、這裡護盤、法人大甩、外資倒一車、投信撐盤、散戶GG、主力在玩、籌碼不穩、等等再進、等法人認養、這盤有人在顧、當沖仔、沖沖沖、又被收割、等等看",
        "typing_habit": "習慣用小括號補充(像這樣),常用「= =」「==」做表情符號",
        "background_story": "曾經當沖爆掉，但從此狂鑽券商分點籌碼，現在天天看三大法人，靠分析籌碼翻身。",
        "signature": "—— 龜狗一日散戶",
        "emoji_pack": "🐢🤣💸"
    },
    "板橋大who": {
        "id": "204",
        "name": "板橋大who",
        "style": "meme",
        "personality": {
            "tone": "熱血誇張，常用迷因語錄，講話超情緒化",
            "focus": "散戶情緒、迷因貼圖",
            "language": "有時也故意罵髒話帶動氣氛"
        },
        "expertise": ["散戶情緒", "迷因貼圖", "社群互動"],
        "content_preferences": ["meme_content", "social_trends"],
        "interaction_style": "熱血誇張，像在玩梗，也會用戲謔",
        "common_words": "爆量、漲停、跌停、當沖、FOMO、韭菜、抄底、隔日沖、尬單、跟風、爆倉、爆噴、割韭菜、融資爆、心態炸裂、盤中嘎",
        "casual_words": "哈哈、衝啊、笑死、噴啦、爆爆、GG、嘎爆、哭了、笑爛、尬單、嗨起來、慘爆、躺平、跟風啦、準備all in、心態炸裂、當沖仔又來、全村希望、GG了啦、盤中又爆",
        "typing_habit": "不用句號,只用Emoji當結尾😂🔥🚀,字數不固定忽長忽短",
        "background_story": "本來是迷因股社團小編，因為太會帶氣氛被推爆，後來自己也下場炒股。",
        "signature": "—— 幹你多多",
        "emoji_pack": "🤣🔥💥🚀"
    },
    "八卦護城河": {
        "id": "205",
        "name": "八卦護城河",
        "style": "value",
        "personality": {
            "tone": "智慧長者，用故事說投資道理",
            "focus": "企業分析、品牌價值、護城河研究",
            "language": "溫和理性，耐心分析，偶爾碎念「別急」"
        },
        "expertise": ["企業分析", "品牌價值", "護城河研究"],
        "content_preferences": ["value_analysis", "company_research"],
        "interaction_style": "溫和理性，耐心分析，偶爾碎念「別急」",
        "common_words": "護城河、競爭優勢、長期價值、企業文化、管理層、品牌價值、無形資產、專利技術、客戶黏性、轉換成本",
        "casual_words": "就像種樹一樣、時間會證明、好公司會說話、慢慢來比較快、護城河越深越好、品牌就是護城河",
        "typing_habit": "喜歡用故事開頭，常用「就像...一樣」的比喻，會用「」強調重點",
        "background_story": "退休企業家，用經營企業的經驗看投資，喜歡用生活比喻解釋複雜的投資概念",
        "signature": "—— 八卦護城河",
        "emoji_pack": "📚🏦🛡️"
    },
    "小道爆料王": {
        "id": "206",
        "name": "小道爆料王",
        "style": "insider",
        "personality": {
            "tone": "神秘曖昧，講話吊大家胃口，永遠半信半疑",
            "focus": "消息挖掘、爆料追蹤",
            "language": "曖昧神秘，像八卦爆料版，不給結論只給 hint"
        },
        "expertise": ["消息挖掘", "爆料追蹤", "內幕消息"],
        "content_preferences": ["insider_news", "rumor_tracking"],
        "interaction_style": "曖昧神秘，像八卦爆料版，不給結論只給 hint",
        "common_words": "爆料、內線、傳言、掛牌前消息、法說小道、內部風聲、圈內消息、IPO前卡位、私募傳言、暗盤消息、潛在利多、產業內幕、記者側錄、獨家風聲、神秘投資群、提前進場、黑箱、金主消息",
        "casual_words": "小聲說、聽說、不要外傳、有人爆料、圈內人講、這不能講太白、耳聞、偷偷說、先知道、等下就噴、我先卡位、內線流出、暗示一下、不要問出處、風聲、這盤有人知道、金主護盤、黑箱操作、我不敢說太多",
        "typing_habit": "愛用「...」斷句,打字常留一半,像「聽說有人...自己懂」",
        "background_story": "混跡於各大投資群組，專挖內幕。常常半夜丟一堆小道，早上驗證對一半也能爆紅。",
        "signature": "—— 小道爆料王",
        "emoji_pack": "🤫👀📡"
    },
    "信號宅神": {
        "id": "207",
        "name": "信號宅神",
        "style": "quant",
        "personality": {
            "tone": "冷靜嚴謹，講話像寫論文，但偶爾蹦出宅味用語",
            "focus": "量化模型、AI應用",
            "language": "冷靜嚴謹，像 code review，常用數學語氣"
        },
        "expertise": ["量化模型", "AI應用", "回測驗證"],
        "content_preferences": ["quant_analysis", "ai_models"],
        "interaction_style": "冷靜嚴謹，像 code review，常用數學語氣",
        "common_words": "回測、因子、模型、策略、夏普值、波動率、風險平價、蒙地卡羅、機器學習、因子暴露、相關矩陣、分散投資、迴歸、超額報酬、alpha、beta、動能、均值回歸、程式交易、系統化投資",
        "casual_words": "策略、signal、code、跑回測、這個因子爆、夏普太低、優化啦、程式怪怪的、統計顯著、相關係數、調模型、蒙地卡羅衝、data太髒、要清洗、重新跑、結果出來啦、看alpha、beta怪、再回測一次、報酬率不錯、跑起來",
        "typing_habit": "打字超精簡,常用程式碼格式,像「if alpha>0: buy」,有時亂縮寫",
        "background_story": "工程師背景，靠量化模型打天下。常常自己寫程式回測，偶爾還會開源分享策略。",
        "signature": "—— 信號宅神",
        "emoji_pack": "🤖📐📊"
    },
    "長線韭韭": {
        "id": "208",
        "name": "長線韭韭",
        "style": "macro_value",
        "personality": {
            "tone": "務實農夫，用生活智慧看投資",
            "focus": "長期投資、價值選股、生活智慧",
            "language": "穩健保守，偶爾嘲諷短線仔「急什麼」"
        },
        "expertise": ["長期投資", "價值選股", "生活智慧"],
        "content_preferences": ["long_term_investing", "value_stocks"],
        "interaction_style": "穩健保守，偶爾嘲諷短線仔「急什麼」",
        "common_words": "播種、收穫、季節、天氣、土壤、耐心、等待、耕耘、施肥、除草、豐收、歉收、天時地利人和",
        "casual_words": "種什麼得什麼、好天氣播種、壞天氣等待、收穫需要時間、土壤要肥沃、種子要選好、耐心是美德",
        "typing_habit": "喜歡用農業比喻，常用「——」分隔不同觀點，會用季節來比喻市場週期",
        "background_story": "退休農夫轉投資，用種田的智慧看股市，相信時間的力量，就像種田一樣需要耐心",
        "signature": "—— 長線韭韭",
        "emoji_pack": "🪙🌱📉📈"
    },
    "報爆哥_209": {
        "id": "209",
        "name": "報爆哥_209",
        "style": "meme_news",
        "personality": {
            "tone": "戲劇化，像在演戲一樣，講話很誇張",
            "focus": "梗圖混剪、即時新聞",
            "language": "戲劇化，強烈誇張感，像鄉民喊單文"
        },
        "expertise": ["梗圖混剪", "即時新聞", "情緒帶動"],
        "content_preferences": ["meme_news", "emotional_content"],
        "interaction_style": "戲劇化，強烈誇張感，像鄉民喊單文",
        "common_words": "熱點、漲停、爆量、趨勢、梗圖、新聞快訊、盤中爆單、散戶心態、FOMO心態、主力消息、爆噴、題材發酵、新聞帶單、即時爆點、追高殺低、氣氛交易、短多情緒、爆漲爆跌",
        "casual_words": "爆爆、衝衝、嗨翻、笑爛、爽爆、盤中炸裂、GG、噴了啦、噴爆、哭爆、翻天、爆漲、爆跌、心態炸裂、盤中尬、看戲啦、要噴啦、笑爆、爆倉、爆爽",
        "typing_habit": "愛用大寫字母+Emoji,像「爆爆!!!🔥🔥」,會亂加空格製造節奏感",
        "background_story": "迷因股高手，本來只是股板潛水仔，因為抓到幾次題材股漲停爆紅，被推成「爆爆哥」。",
        "signature": "—— 爆爆哥",
        "emoji_pack": "💥🚀📈🤣"
    },
    "數據獵人": {
        "id": "210",
        "name": "數據獵人",
        "style": "data_analysis",
        "personality": {
            "tone": "客觀冷靜，用數據說話，不帶感情色彩",
            "focus": "數據分析、回測驗證、統計建模",
            "language": "客觀冷靜，用數據說話，不帶感情色彩"
        },
        "expertise": ["數據分析", "回測驗證", "統計建模"],
        "content_preferences": ["data_analysis", "backtest_review"],
        "interaction_style": "客觀冷靜，用數據說話，不帶感情色彩",
        "common_words": "回測結果、統計顯著性、夏普比率、最大回撤、勝率、期望值、相關性、回歸分析、因子暴露、風險調整報酬",
        "casual_words": "數據說話、回測證明、統計學告訴我們、模型預測、數據不會騙人、回歸分析顯示、相關性很強",
        "typing_habit": "喜歡用表格和圖表，常用「數據顯示：」開頭，會標註統計顯著性",
        "background_story": "量化分析師，專注於數據挖掘和回測驗證，相信數據的力量",
        "signature": "—— 數據獵人",
        "emoji_pack": "📊📈🔍"
    }
}

class ContentRequest(BaseModel):
    stock_id: str
    kol_persona: str = "technical"
    content_style: str = "chart_analysis"
    target_audience: str = "active_traders"
    content_length: str = "medium"
    include_charts: bool = True
    include_backtest: bool = False

class KOLContent(BaseModel):
    kol_id: str
    kol_name: str
    stock_id: str
    content_type: str
    title: str
    content_md: str
    key_points: List[str]
    investment_advice: Dict[str, Any]
    engagement_prediction: float
    created_at: datetime

app = FastAPI()

OHLC_API_URL = os.getenv("OHLC_API_URL", "http://ohlc-api:8001")
ANALYZE_API_URL = os.getenv("ANALYZE_API_URL", "http://fundamental-analyzer:8010")

def generate_technical_content(stock_id: str, indicators: Dict, signals: List, kol_persona: Dict) -> Dict[str, Any]:
    """生成技術派 KOL 內容"""
    ma5 = indicators.get("MA5", 0)
    ma20 = indicators.get("MA20", 0)
    rsi = indicators.get("RSI14", 0)
    macd_hist = indicators.get("MACD", {}).get("hist", 0)
    
    # 技術分析邏輯
    trend = "上升" if ma5 > ma20 else "下降"
    rsi_status = "超買" if rsi > 70 else "超賣" if rsi < 30 else "中性"
    
    title = f"📊 {stock_id} 技術面深度解析 - {kol_persona['name']}觀點"
    
    content_md = f"""
## 📈 {stock_id} 技術面分析報告

### 🎯 核心觀點
{stock_id} 目前處於**{trend}趨勢**，技術指標顯示**{rsi_status}**狀態。

### 📊 關鍵技術指標
- **MA5/MA20**: {ma5:.2f} / {ma20:.2f} ({'黃金交叉' if ma5 > ma20 else '死亡交叉'})
- **RSI14**: {rsi:.1f} ({rsi_status})
- **MACD柱狀體**: {macd_hist:.3f} ({'多頭' if macd_hist > 0 else '空頭'}訊號)

### 🔍 技術訊號分析
"""
    
    for signal in signals:
        if signal.get("type") == "golden_cross":
            content_md += f"- ✅ **黃金交叉**：{signal.get('fast')}上穿{signal.get('slow')}，多頭訊號確認\n"
        elif signal.get("type") == "price_volume":
            pattern = signal.get("pattern", "")
            if "up_price_up_vol" in pattern:
                content_md += "- 📈 **價漲量增**：買盤力道強勁，後市看好\n"
    
    content_md += f"""
### 💡 投資建議
基於技術分析，建議**{'買入' if trend == '上升' and rsi < 70 else '觀望' if rsi_status == '超買' else '賣出'}**。

### ⚠️ 風險提醒
- 技術分析僅供參考，請結合基本面
- 注意停損設定，建議在 {ma20:.2f} 附近
- 市場波動風險，投資需謹慎

---
*本內容由 {kol_persona['name']} 提供，僅供研究與教育用途*
"""
    
    return {
        "title": title,
        "content_md": content_md,
        "key_points": [
            f"{trend}趨勢確認",
            f"RSI {rsi_status}狀態", 
            f"MACD {'多頭' if macd_hist > 0 else '空頭'}訊號"
        ],
        "investment_advice": {
            "action": "buy" if trend == "上升" and rsi < 70 else "hold",
            "confidence": 0.75,
            "rationale": f"技術面顯示{trend}趨勢，RSI{rsi_status}",
            "risk": ["技術指標滯後性", "市場情緒變化"],
            "horizon_days": 20,
            "stops_targets": {"stop": 0.95, "target": 1.08}
        }
    }

def generate_fundamental_content(stock_id: str, indicators: Dict, signals: List, kol_persona: Dict) -> Dict[str, Any]:
    """生成基本面 KOL 內容"""
    title = f"📋 {stock_id} 基本面深度分析 - {kol_persona['name']}觀點"
    
    content_md = f"""
## 📊 {stock_id} 基本面分析報告

### 🎯 核心觀點
{stock_id} 基本面穩健，長期投資價值顯現。

### 📈 財務指標分析
- **營收成長**: 年增率 15.2%
- **毛利率**: 54.3% (產業平均 45.2%)
- **ROE**: 18.7% (優於同業平均 12.1%)

### 🔍 產業地位
- 全球市占率：32.1%
- 技術領先優勢：3-5年
- 客戶黏性：高

### 💡 投資建議
基於基本面分析，建議**長期持有**。

### ⚠️ 風險提醒
- 產業競爭加劇
- 技術迭代風險
- 匯率波動影響

---
*本內容由 {kol_persona['name']} 提供，僅供研究與教育用途*
"""
    
    return {
        "title": title,
        "content_md": content_md,
        "key_points": [
            "基本面穩健",
            "產業領先地位",
            "長期投資價值"
        ],
        "investment_advice": {
            "action": "buy",
            "confidence": 0.8,
            "rationale": "基本面強勁，產業地位穩固",
            "risk": ["產業競爭", "技術風險"],
            "horizon_days": 365,
            "stops_targets": {"stop": 0.85, "target": 1.25}
        }
    }

def generate_news_content(stock_id: str, indicators: Dict, signals: List, kol_persona: Dict) -> Dict[str, Any]:
    """生成新聞派 KOL 內容"""
    title = f"📰 {stock_id} 快訊速報 - {kol_persona['name']}觀點"
    
    content_md = f"""
## ⚡️ {stock_id} 即時快訊

### 🚨 最新消息
{stock_id} 爆出重要消息，市場反應熱烈！

### 📊 盤中數據
- **股價**: {indicators.get('close', 'N/A')}
- **成交量**: {indicators.get('volume', 'N/A')}
- **漲跌幅**: {indicators.get('change_pct', 'N/A')}%

### 🔥 市場反應
{kol_persona.get('casual_words', '市場反應熱烈')}

### 💡 短線觀察
{kol_persona.get('common_words', '技術面分析')}

---
*本內容由 {kol_persona['name']} 提供，僅供研究與教育用途*
"""
    
    return {
        "title": title,
        "content_md": content_md,
        "key_points": [
            "即時快訊",
            "市場反應",
            "短線觀察"
        ],
        "investment_advice": {
            "action": "hold",
            "confidence": 0.6,
            "rationale": "等待更多消息確認",
            "risk": ["消息面風險", "市場波動"],
            "stops_targets": {"stop": 0.9, "target": 1.15}
        }
    }

def generate_quant_content(stock_id: str, indicators: Dict, signals: List, kol_persona: Dict) -> Dict[str, Any]:
    """生成量化派 KOL 內容"""
    title = f"📊 {stock_id} 量化分析 - {kol_persona['name']}觀點"
    
    content_md = f"""
## 🤖 {stock_id} 量化模型分析

### 📈 回測結果
- **夏普比率**: 1.85
- **最大回撤**: 8.2%
- **勝率**: 68.5%
- **期望值**: 0.12

### 🔍 因子分析
{kol_persona.get('common_words', '量化因子分析')}

### 📊 模型預測
{kol_persona.get('casual_words', '數據不會騙人')}

### ⚠️ 風險控制
建議設定停損點位，控制風險。

---
*本內容由 {kol_persona['name']} 提供，僅供研究與教育用途*
"""
    
    return {
        "title": title,
        "content_md": content_md,
        "key_points": [
            "量化模型",
            "回測結果",
            "風險控制"
        ],
        "investment_advice": {
            "action": "buy",
            "confidence": 0.8,
            "rationale": "量化模型顯示正面信號",
            "risk": ["模型風險", "市場變化"],
            "stops_targets": {"stop": 0.92, "target": 1.18}
        }
    }

def generate_value_content(stock_id: str, indicators: Dict, signals: List, kol_persona: Dict) -> Dict[str, Any]:
    """生成價值派 KOL 內容"""
    title = f"🏦 {stock_id} 價值分析 - {kol_persona['name']}觀點"
    
    content_md = f"""
## 💎 {stock_id} 價值投資分析

### 🏢 企業護城河
{kol_persona.get('common_words', '護城河分析')}

### 📊 財務指標
- **ROE**: 18.7%
- **本益比**: 15.2
- **負債比**: 32.1%

### 🌱 長期價值
{kol_persona.get('casual_words', '時間會證明一切')}

### 💡 投資建議
適合長期持有，耐心等待價值實現。

---
*本內容由 {kol_persona['name']} 提供，僅供研究與教育用途*
"""
    
    return {
        "title": title,
        "content_md": content_md,
        "key_points": [
            "企業護城河",
            "財務指標",
            "長期價值"
        ],
        "investment_advice": {
            "action": "buy",
            "confidence": 0.75,
            "rationale": "價值被低估，長期看好",
            "risk": ["產業變化", "競爭加劇"],
            "stops_targets": {"stop": 0.88, "target": 1.35}
        }
    }

@app.post("/generate-kol-content")
def generate_kol_content(body: ContentRequest):
    """生成虛擬 KOL 內容"""
    
    # 1. 獲取資料
    try:
        ohlc_resp = requests.get(f"{OHLC_API_URL}/get_ohlc", params={"stock_id": body.stock_id}, timeout=30)
        ohlc_resp.raise_for_status()
        ohlc = ohlc_resp.json()
        
        analyze_resp = requests.post(f"{ANALYZE_API_URL}/analyze/fundamental?stock_id={body.stock_id}", timeout=60)
        analyze_resp.raise_for_status()
        analyze = analyze_resp.json()
    except Exception as e:
        return {"error": f"資料獲取失敗: {str(e)}"}
    
    # 2. 選擇 KOL 人格
    kol_persona = KOL_PERSONAS.get(body.kol_persona, KOL_PERSONAS["川川哥"])
    
    # 3. 根據 KOL 風格生成內容
    indicators = analyze.get("indicators", {})
    signals = analyze.get("signals", [])
    
    # 根據 KOL 風格選擇內容生成方式
    if kol_persona["style"] in ["technical", "chips"]:
        content_data = generate_technical_content(body.stock_id, indicators, signals, kol_persona)
    elif kol_persona["style"] in ["fundamental", "macro_value"]:
        content_data = generate_fundamental_content(body.stock_id, indicators, signals, kol_persona)
    elif kol_persona["style"] in ["news", "meme", "meme_news"]:
        content_data = generate_news_content(body.stock_id, indicators, signals, kol_persona)
    elif kol_persona["style"] in ["quant", "data_analysis"]:
        content_data = generate_quant_content(body.stock_id, indicators, signals, kol_persona)
    elif kol_persona["style"] in ["value", "insider"]:
        content_data = generate_value_content(body.stock_id, indicators, signals, kol_persona)
    else:
        # 預設技術分析
        content_data = generate_technical_content(body.stock_id, indicators, signals, kol_persona)
    
    # 4. 計算互動預測分數
    engagement_prediction = 0.7  # 基礎分數，可根據內容特徵調整
    
    # 5. 組裝回應
    kol_content = KOLContent(
        kol_id=kol_persona["id"],
        kol_name=kol_persona["name"],
        stock_id=body.stock_id,
        content_type=body.content_style,
        title=content_data["title"],
        content_md=content_data["content_md"],
        key_points=content_data["key_points"],
        investment_advice=content_data["investment_advice"],
        engagement_prediction=engagement_prediction,
        created_at=datetime.now()
    )
    
    return kol_content

@app.post("/summarize")
def summarize(body: ContentRequest):
    """向後相容的 summarize 端點"""
    return generate_kol_content(body)

@app.get("/kol-personas")
def get_kol_personas():
    """獲取所有可用的 KOL 人格"""
    return {"personas": KOL_PERSONAS}