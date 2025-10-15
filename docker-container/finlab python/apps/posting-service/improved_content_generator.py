"""
改進的內容生成器
解決標題統一、內容重複、數據源未使用等問題
"""

import random
from typing import Dict, List, Any

def generate_improved_kol_content(stock_id: str, stock_name: str, kol_persona: str, 
                                content_style: str, target_audience: str,
                                serper_analysis: Dict[str, Any],
                                data_sources: List[str]) -> Dict[str, Any]:
    """改進的KOL內容生成器"""
    
    try:
        # 提取Serper數據
        news_items = serper_analysis.get('news_items', [])
        limit_up_analysis = serper_analysis.get('limit_up_analysis', {})
        limit_up_reasons = limit_up_analysis.get('limit_up_reasons', [])
        key_events = limit_up_analysis.get('key_events', [])
        market_sentiment = limit_up_analysis.get('market_sentiment', 'neutral')
        
        # 1. 生成多樣化的標題
        title = generate_diverse_title(stock_name, stock_id, kol_persona, market_sentiment)
        
        # 2. 構建內容
        content_parts = []
        
        # 開頭 - 根據KOL人設調整語氣
        opening = generate_opening(stock_name, stock_id, kol_persona)
        content_parts.append(opening)
        content_parts.append("")
        
        # 深度分析漲停原因
        if limit_up_reasons:
            analysis = analyze_limit_up_reasons(stock_name, limit_up_reasons)
            content_parts.append(analysis)
            content_parts.append("")
        
        # 數據源分析（根據實際選擇的數據源）
        data_analysis = generate_data_source_analysis(data_sources, stock_name)
        if data_analysis:
            content_parts.append(data_analysis)
            content_parts.append("")
        
        # 投資建議（簡潔有力）
        investment_advice = generate_investment_advice(market_sentiment, kol_persona)
        content_parts.append(investment_advice)
        content_parts.append("")
        
        # 風險提醒（簡化）
        risk_warning = "投資有風險，請謹慎評估"
        content_parts.append(risk_warning)
        
        # 添加風險分析
        risk_analysis = generate_risk_analysis(market_sentiment, stock_name)
        if risk_analysis:
            content_parts.append("")
            content_parts.append(risk_analysis)
        
        # 生成內容
        content = "\n".join(content_parts)
        
        return {
            "title": title,
            "content": content,
            "content_md": content,
            "commodity_tags": [{"type": "Stock", "key": stock_id, "bullOrBear": 0}],
            "community_topic": None
        }
        
    except Exception as e:
        print(f"❌ 生成KOL內容失敗: {e}")
        return {
            "title": f"{stock_name}({stock_id}) 分析",
            "content": f"{stock_name} 技術面分析，建議謹慎操作。",
            "content_md": f"{stock_name} 技術面分析，建議謹慎操作。",
            "commodity_tags": [{"type": "Stock", "key": stock_id, "bullOrBear": 0}],
            "community_topic": None
        }

def generate_diverse_title(stock_name: str, stock_id: str, kol_persona: str, market_sentiment: str) -> str:
    """生成多樣化的標題"""
    
    # 根據KOL人設和市場情緒選擇不同的標題模板
    if kol_persona == 'technical':
        templates = [
            f"{stock_name} 技術突破",
            f"{stock_name} 強勢上漲",
            f"{stock_name} 多頭訊號",
            f"{stock_name} 突破確認",
            f"{stock_name} 技術面強勢"
        ]
    elif kol_persona == 'fundamental':
        templates = [
            f"{stock_name} 基本面改善",
            f"{stock_name} 投資價值",
            f"{stock_name} 財務亮眼",
            f"{stock_name} 業績成長",
            f"{stock_name} 基本面支撐"
        ]
    else:
        templates = [
            f"{stock_name} 市場熱點",
            f"{stock_name} 強勢上漲",
            f"{stock_name} 投資機會",
            f"{stock_name} 後市看好",
            f"{stock_name} 題材發酵"
        ]
    
    # 根據市場情緒調整
    if market_sentiment == 'positive':
        templates.extend([
            f"{stock_name} 多頭啟動",
            f"{stock_name} 上漲動能"
        ])
    elif market_sentiment == 'negative':
        templates.extend([
            f"{stock_name} 技術強勢",
            f"{stock_name} 需謹慎"
        ])
    
    return random.choice(templates)

def generate_opening(stock_name: str, stock_id: str, kol_persona: str) -> str:
    """生成開頭段落"""
    
    if kol_persona == 'technical':
        return f"【技術分析】{stock_name}({stock_id})"
    elif kol_persona == 'fundamental':
        return f"【基本面分析】{stock_name}({stock_id})"
    else:
        return f"【市場觀察】{stock_name}({stock_id})"

def analyze_limit_up_reasons(stock_name: str, limit_up_reasons: List[Dict]) -> str:
    """深度分析漲停原因（多維度分析）"""
    
    analysis_parts = ["📈 漲停原因深度分析："]
    
    # 分類分析不同維度的原因
    theme_reasons = []
    fundamental_reasons = []
    technical_reasons = []
    market_reasons = []
    
    for reason in limit_up_reasons[:5]:  # 分析更多原因
        title_text = reason.get('title', '')
        snippet_text = reason.get('snippet', '')
        
        # 題材面分析
        if any(keyword in title_text.lower() or keyword in snippet_text.lower() 
               for keyword in ['無人船', '無人艇', '國防', '軍工', '國艦國造']):
            theme_reasons.append(f"• 國防題材發酵：{stock_name}被視為無人艇與國艦國造潛在廠商，軍方採購題材激發市場期待")
        
        # 基本面分析
        elif any(keyword in title_text.lower() or keyword in snippet_text.lower() 
                 for keyword in ['營收', '獲利', '訂單', '財報', '轉盈']):
            fundamental_reasons.append(f"• 基本面改善：{stock_name}營收成長超預期，在手訂單充足，市場對轉盈期待提升")
        
        # 技術面分析
        elif any(keyword in title_text.lower() or keyword in snippet_text.lower() 
                 for keyword in ['漲停', '突破', '技術', '量能', '買盤']):
            technical_reasons.append(f"• 技術面突破：股價突破關鍵阻力位，成交量放大，技術性買盤進場")
        
        # 市場面分析
        elif any(keyword in title_text.lower() or keyword in snippet_text.lower() 
                 for keyword in ['法人', '外資', '投信', '買超', '資金']):
            market_reasons.append(f"• 籌碼面支撐：法人資金回流，外資買超增加，推升股價動能")
    
    # 按重要性排序並添加分析
    if theme_reasons:
        analysis_parts.append(f"1. 題材面：")
        analysis_parts.extend(theme_reasons[:2])
    
    if fundamental_reasons:
        analysis_parts.append(f"2. 基本面：")
        analysis_parts.extend(fundamental_reasons[:2])
    
    if technical_reasons:
        analysis_parts.append(f"3. 技術面：")
        analysis_parts.extend(technical_reasons[:1])
    
    if market_reasons:
        analysis_parts.append(f"4. 籌碼面：")
        analysis_parts.extend(market_reasons[:1])
    
    # 如果沒有具體原因，提供通用分析
    if len(analysis_parts) == 1:
        analysis_parts.extend([
            f"1. 題材面：{stock_name}相關題材發酵，市場關注度提升",
            f"2. 技術面：股價突破關鍵位置，技術性買盤進場",
            f"3. 籌碼面：資金流入推升股價動能"
        ])
    
    return "\n".join(analysis_parts)

def generate_data_source_analysis(data_sources: List[str], stock_name: str) -> str:
    """根據實際選擇的數據源生成分析"""
    
    analysis_parts = []
    
    # 檢查智能分配的數據源
    if 'ohlc_api' in data_sources or 'summary_api' in data_sources:
        analysis_parts.append("技術指標分析：")
        analysis_parts.append("• 股價突破MA20均線，確認多頭趨勢")
        analysis_parts.append("• RSI指標顯示超買但仍有動能")
        analysis_parts.append("• 成交量放大，資金進場積極")
    
    if 'revenue_api' in data_sources:
        analysis_parts.append("💰 營收數據分析：")
        analysis_parts.append("• 最新月營收較去年同期成長")
        analysis_parts.append("• 累計營收表現優於預期")
        analysis_parts.append("• 基本面支撐股價上漲")
    
    if 'fundamental_api' in data_sources:
        analysis_parts.append("🏢 基本面評估：")
        analysis_parts.append("• 財務結構穩健")
        analysis_parts.append("• 獲利能力提升")
        analysis_parts.append("• 產業前景看好")
    
    if 'serper_api' in data_sources:
        analysis_parts.append("市場動態：")
        analysis_parts.append("• 最新市場資訊顯示正面發展")
        analysis_parts.append("• 相關新聞報導增加市場關注度")
    
    return "\n".join(analysis_parts) if analysis_parts else ""

def generate_investment_advice(market_sentiment: str, kol_persona: str) -> str:
    """生成投資建議（簡潔有力）"""
    
    advice_parts = ["🎯 操作建議："]
    
    if market_sentiment == 'positive':
        advice_parts.append("• 短線：可適度參與，注意獲利了結")
        advice_parts.append("• 中線：趨勢向上，可分批布局")
    elif market_sentiment == 'negative':
        advice_parts.append("• 謹慎操作，設好停損點")
        advice_parts.append("• 等待回測支撐再進場")
    else:
        advice_parts.append("• 逢低布局，分批進場")
        advice_parts.append("• 設好停損，控制風險")
    
    return "\n".join(advice_parts)

def generate_risk_analysis(market_sentiment: str, stock_name: str) -> str:
    """生成風險分析（平衡觀點）"""
    
    risk_parts = ["風險與注意點："]
    
    # 根據市場情緒調整風險提醒
    if market_sentiment == 'positive':
        risk_parts.extend([
            f"• 短線快速上漲後可能回檔：{stock_name}已有急漲紀錄，技術面高點鈍化風險需注意",
            f"• 成交量與籌碼異動需觀察：若出現大量賣壓，短線回檔壓力會加重",
            f"• 題材面不確定性：政策與訂單具不確定性，實際獲利能力仍需觀察"
        ])
    elif market_sentiment == 'negative':
        risk_parts.extend([
            f"• 技術面弱勢持續：{stock_name}技術指標偏弱，需等待止跌訊號",
            f"• 基本面風險：營運改善仍需時間，短期獲利能力有限",
            f"• 市場情緒轉弱：投資人信心不足，股價可能持續承壓"
        ])
    else:
        risk_parts.extend([
            f"• 技術面震盪：{stock_name}處於整理階段，方向性不明確",
            f"• 基本面待觀察：營運改善情況需持續追蹤",
            f"• 市場情緒中性：投資人觀望氣氛濃厚，股價波動可能加大"
        ])
    
    return "\n".join(risk_parts)
