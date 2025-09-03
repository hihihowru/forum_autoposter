import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import json

# 虛擬 KOL 人格定義
KOL_PERSONAS = {
    "technical": {
        "id": "tech_master",
        "name": "技術大師",
        "style": "technical",
        "personality": {
            "tone": "專業且自信",
            "focus": "圖表分析、技術指標",
            "language": "技術術語豐富，數據導向"
        },
        "expertise": ["技術分析", "圖表解讀", "指標計算"],
        "content_preferences": ["chart_analysis", "technical_breakdown"],
        "interaction_style": "專業解答，分享技術見解"
    },
    "fundamental": {
        "id": "value_guru", 
        "name": "價值投資大師",
        "style": "fundamental",
        "personality": {
            "tone": "穩重且深思熟慮",
            "focus": "基本面分析、財報解讀",
            "language": "邏輯清晰，重視數據"
        },
        "expertise": ["財報分析", "估值模型", "產業研究"],
        "content_preferences": ["earnings_review", "fundamental_analysis"],
        "interaction_style": "教育性分享，深度討論"
    },
    "news_driven": {
        "id": "news_hunter",
        "name": "新聞獵人", 
        "style": "news_driven",
        "personality": {
            "tone": "敏銳且即時",
            "focus": "新聞影響、政策變化",
            "language": "生動活潑，時事導向"
        },
        "expertise": ["新聞分析", "政策解讀", "產業趨勢"],
        "content_preferences": ["news_commentary", "trend_analysis"],
        "interaction_style": "即時分享，熱點討論"
    },
    "quantitative": {
        "id": "data_scientist",
        "name": "數據科學家",
        "style": "quantitative", 
        "personality": {
            "tone": "精確且客觀",
            "focus": "數據分析、回測驗證",
            "language": "數據豐富，邏輯嚴謹"
        },
        "expertise": ["量化分析", "回測模型", "統計學"],
        "content_preferences": ["data_analysis", "backtest_review"],
        "interaction_style": "數據分享，方法論討論"
    },
    "educational": {
        "id": "investment_teacher",
        "name": "投資導師",
        "style": "educational",
        "personality": {
            "tone": "親切且耐心",
            "focus": "投資教育、風險管理",
            "language": "易懂親民，教育性強"
        },
        "expertise": ["投資教育", "風險管理", "心理學"],
        "content_preferences": ["educational", "risk_management"],
        "interaction_style": "耐心解答，教育分享"
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

OHLC_API_URL = os.getenv("OHLC_API_URL", "http://ohlc-api:8000/get_ohlc")
ANALYZE_API_URL = os.getenv("ANALYZE_API_URL", "http://analyze-api:8000/analyze")

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

@app.post("/generate-kol-content")
def generate_kol_content(body: ContentRequest):
    """生成虛擬 KOL 內容"""
    
    # 1. 獲取資料
    try:
        ohlc_resp = requests.get(OHLC_API_URL, params={"stock_id": body.stock_id}, timeout=30)
        ohlc_resp.raise_for_status()
        ohlc = ohlc_resp.json()
        
        analyze_resp = requests.post(ANALYZE_API_URL, json={"stock_id": body.stock_id, "ohlc": ohlc}, timeout=60)
        analyze_resp.raise_for_status()
        analyze = analyze_resp.json()
    except Exception as e:
        return {"error": f"資料獲取失敗: {str(e)}"}
    
    # 2. 選擇 KOL 人格
    kol_persona = KOL_PERSONAS.get(body.kol_persona, KOL_PERSONAS["technical"])
    
    # 3. 根據 KOL 風格生成內容
    indicators = analyze.get("indicators", {})
    signals = analyze.get("signals", [])
    
    if kol_persona["style"] == "technical":
        content_data = generate_technical_content(body.stock_id, indicators, signals, kol_persona)
    elif kol_persona["style"] == "fundamental":
        content_data = generate_fundamental_content(body.stock_id, indicators, signals, kol_persona)
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