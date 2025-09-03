import os
import json
import pandas as pd
import finlab
from finlab import data
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from typing import Dict, Any, Optional
import random

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """啟動時登入 FinLab"""
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)

def format_large_number(num):
    """格式化大數字，例如 1204532131 -> 12億453萬"""
    if pd.isna(num) or num == 0:
        return "0"
    
    num = int(num)
    
    if num >= 100000000:  # 億
        yi = num // 100000000
        wan = (num % 100000000) // 10000
        if wan > 0:
            return f"{yi}億{wan}萬"
        else:
            return f"{yi}億"
    elif num >= 10000:  # 萬
        wan = num // 10000
        return f"{wan}萬"
    else:
        return str(num)

def get_industry_analysis(stock_id: str) -> Dict[str, Any]:
    """根據股票代號判斷產業並提供分析"""
    # 簡化的產業判斷邏輯
    if stock_id.startswith('23'):  # 電子業
        return {
            "industry": "電子業",
            "key_metrics": ["營業毛利率", "營業利益率", "ROE稅後"],
            "focus_areas": ["研發投入", "毛利率", "營收成長"]
        }
    elif stock_id.startswith('28'):  # 金融業
        return {
            "industry": "金融業",
            "key_metrics": ["ROE稅後", "流動比率", "營業利益率"],
            "focus_areas": ["資本適足率", "淨利差", "手續費收入"]
        }
    elif stock_id.startswith('13'):  # 傳產業
        return {
            "industry": "傳產業",
            "key_metrics": ["營業毛利率", "存貨週轉率", "ROA稅後息前"],
            "focus_areas": ["成本控制", "營運效率", "市場佔有率"]
        }
    else:
        return {
            "industry": "其他產業",
            "key_metrics": ["營業利益率", "ROE稅後", "營運現金流"],
            "focus_areas": ["獲利能力", "財務結構", "現金流"]
        }

def generate_kol_insights(stock_id: str, revenue_data: Dict, financial_data: Dict) -> Dict[str, Any]:
    """生成 KOL 洞察內容"""
    
    # 取得產業分析
    industry_info = get_industry_analysis(stock_id)
    
    # 分析營收趨勢
    revenue_trend = revenue_data.get("trend", "穩定")
    revenue_growth = revenue_data.get("growth", {}).get("year_over_year", 0)
    
    # 分析財務健康度
    financial_health = financial_data.get("analysis", {}).get("overall_health", "一般")
    operating_margin = financial_data.get("profitability", {}).get("operating_margin", 0)
    roe = financial_data.get("profitability", {}).get("roe", 0)
    
    # 生成洞察標題
    insight_titles = [
        f"{stock_id} 財報分析：{industry_info['industry']}龍頭表現亮眼",
        f"深度解析 {stock_id}：{revenue_trend}營收背後的投資價值",
        f"{stock_id} 投資機會：{financial_health}財務體質支撐長期成長",
        f"從財報看 {stock_id}：{industry_info['industry']}產業趨勢與投資策略"
    ]
    
    # 生成關鍵洞察點
    key_insights = []
    
    if revenue_growth > 20:
        key_insights.append(f"營收年增率達 {revenue_growth:.1f}%，顯示強勁成長動能")
    elif revenue_growth > 0:
        key_insights.append(f"營收年增率 {revenue_growth:.1f}%，維持穩定成長")
    else:
        key_insights.append(f"營收年增率 {revenue_growth:.1f}%，需要關注營運改善")
    
    if operating_margin > 15:
        key_insights.append(f"營業利益率 {operating_margin:.1f}%，展現優秀的獲利能力")
    elif operating_margin > 10:
        key_insights.append(f"營業利益率 {operating_margin:.1f}%，獲利能力穩定")
    else:
        key_insights.append(f"營業利益率 {operating_margin:.1f}%，建議關注成本控制")
    
    if roe > 15:
        key_insights.append(f"ROE {roe:.1f}%，股東權益報酬率表現優異")
    elif roe > 10:
        key_insights.append(f"ROE {roe:.1f}%，股東權益報酬率穩定")
    else:
        key_insights.append(f"ROE {roe:.1f}%，建議關注營運效率提升")
    
    # 生成投資建議
    investment_advice = []
    if financial_health == "優秀" and revenue_growth > 10:
        investment_advice.append("財務體質優秀且營收成長強勁，適合長期投資")
    elif financial_health == "良好":
        investment_advice.append("財務體質良好，可考慮分批布局")
    else:
        investment_advice.append("建議觀察後續營運改善情況")
    
    # 加入隨機性
    random_insights = [
        "從產業週期角度來看，目前處於成長階段",
        "相較於同業，在成本控制方面表現突出",
        "研發投入持續增加，為未來成長奠定基礎",
        "現金流充沛，財務結構穩健"
    ]
    
    if len(key_insights) < 3:
        key_insights.append(random.choice(random_insights))
    
    return {
        "stock_id": stock_id,
        "industry": industry_info,
        "insight_title": random.choice(insight_titles),
        "key_insights": key_insights,
        "investment_advice": investment_advice,
        "analysis_summary": f"{stock_id} 在 {industry_info['industry']} 產業中表現{financial_health}，營收{revenue_trend}，建議投資人關注{', '.join(industry_info['focus_areas'])}等關鍵指標。"
    }

@app.post("/analyze/fundamental")
def analyze_fundamental(stock_id: str):
    """基本面分析"""
    try:
        # 取得營收資料
        current_revenue = data.get('monthly_revenue:當月營收')
        yoy_change = data.get('monthly_revenue:去年同月增減(%)')
        
        # 取得財務資料
        operating_profit = data.get('fundamental_features:營業利益')
        operating_margin = data.get('fundamental_features:營業利益率')
        roe = data.get('fundamental_features:ROE稅後')
        
        if stock_id not in current_revenue.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        # 取得最新資料
        latest_revenue = current_revenue[stock_id].dropna().iloc[-1]
        latest_yoy = yoy_change[stock_id].dropna().iloc[-1]
        latest_profit = operating_profit[stock_id].dropna().iloc[-1]
        latest_margin = operating_margin[stock_id].dropna().iloc[-1]
        latest_roe = roe[stock_id].dropna().iloc[-1]
        
        # 計算趨勢
        recent_revenues = current_revenue[stock_id].dropna().tail(3)
        trend = "上升" if recent_revenues.iloc[-1] > recent_revenues.iloc[0] else "下降"
        
        # 分析財務健康度
        financial_health = "優秀" if latest_margin > 15 else "良好" if latest_margin > 10 else "一般"
        
        revenue_data = {
            "trend": trend,
            "growth": {"year_over_year": float(latest_yoy)}
        }
        
        financial_data = {
            "analysis": {"overall_health": financial_health},
            "profitability": {
                "operating_margin": float(latest_margin),
                "roe": float(latest_roe)
            }
        }
        
        # 生成 KOL 洞察
        kol_insights = generate_kol_insights(stock_id, revenue_data, financial_data)
        
        result = {
            "stock_id": stock_id,
            "analysis_date": datetime.now().isoformat(),
            "revenue_analysis": {
                "current_revenue": {
                    "value": int(latest_revenue),
                    "formatted": format_large_number(latest_revenue)
                },
                "year_over_year_growth": round(float(latest_yoy), 2),
                "trend": trend
            },
            "financial_analysis": {
                "operating_profit": {
                    "value": int(latest_profit),
                    "formatted": format_large_number(latest_profit)
                },
                "operating_margin": round(float(latest_margin), 2),
                "roe": round(float(latest_roe), 2),
                "financial_health": financial_health
            },
            "kol_insights": kol_insights
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/kol-content")
def generate_kol_content(stock_id: str, content_style: str = Query("analysis", description="內容風格：analysis, bullish, bearish, neutral")):
    """生成 KOL 內容"""
    try:
        # 取得基本面分析
        analysis_result = analyze_fundamental(stock_id)
        
        # 根據風格調整內容
        if content_style == "bullish":
            tone = "樂觀"
            emphasis = "投資機會"
        elif content_style == "bearish":
            tone = "謹慎"
            emphasis = "風險提醒"
        elif content_style == "neutral":
            tone = "客觀"
            emphasis = "平衡分析"
        else:
            tone = "專業"
            emphasis = "深度分析"
        
        # 生成內容
        content = {
            "stock_id": stock_id,
            "content_style": content_style,
            "tone": tone,
            "title": analysis_result["kol_insights"]["insight_title"],
            "summary": analysis_result["kol_insights"]["analysis_summary"],
            "key_points": analysis_result["kol_insights"]["key_insights"],
            "investment_advice": analysis_result["kol_insights"]["investment_advice"],
            "industry_focus": analysis_result["kol_insights"]["industry"]["focus_areas"],
            "generated_at": datetime.now().isoformat()
        }
        
        return content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy", "service": "fundamental-analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)


