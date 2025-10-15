#!/usr/bin/env python3
"""
技術指標解釋生成器
提供具體的技術分析解釋，避免空洞的數字描述
"""

import random
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class TechnicalExplanation:
    """技術指標解釋"""
    indicator_name: str
    current_value: str
    signal: str
    explanation: str
    confidence: str

class TechnicalExplanationGenerator:
    """技術指標解釋生成器"""
    
    def __init__(self):
        self.technical_indicators = {
            "MACD": {
                "bullish": [
                    "MACD柱狀圖由負轉正，動能開始改善",
                    "MACD快線突破慢線，短期動能轉強",
                    "MACD柱狀圖持續放大，買盤動能增強"
                ],
                "bearish": [
                    "MACD柱狀圖由正轉負，動能開始減弱",
                    "MACD快線跌破慢線，短期動能轉弱",
                    "MACD柱狀圖持續縮小，賣盤壓力增加"
                ],
                "neutral": [
                    "MACD柱狀圖在零軸附近震盪，動能不明確",
                    "MACD快慢線糾纏，短期方向不明",
                    "MACD柱狀圖變化不大，市場觀望氣氛濃"
                ]
            },
            "KD": {
                "bullish": [
                    "KD指標出現黃金交叉，K線突破D線向上",
                    "KD指標在20以下出現背離，超賣反彈機會",
                    "KD指標持續向上，短期動能改善"
                ],
                "bearish": [
                    "KD指標出現死亡交叉，K線跌破D線向下",
                    "KD指標在80以上出現背離，超買回調風險",
                    "KD指標持續向下，短期動能減弱"
                ],
                "neutral": [
                    "KD指標在50附近震盪，方向不明確",
                    "KD指標快慢線糾纏，短期趨勢不明",
                    "KD指標變化不大，市場觀望"
                ]
            },
            "均線": {
                "bullish": [
                    "股價站上5日、10日均線，短期趨勢向上",
                    "5日均線突破10日均線，形成多頭排列",
                    "股價突破20日均線，中期趨勢轉強"
                ],
                "bearish": [
                    "股價跌破5日、10日均線，短期趨勢向下",
                    "5日均線跌破10日均線，形成空頭排列",
                    "股價跌破20日均線，中期趨勢轉弱"
                ],
                "neutral": [
                    "股價在均線間震盪，趨勢不明確",
                    "均線糾纏，短期方向不明",
                    "股價與均線關係變化不大"
                ]
            },
            "RSI": {
                "bullish": [
                    "RSI從超賣區回升，反彈動能增強",
                    "RSI突破50中軸，動能轉為正面",
                    "RSI在30以下出現背離，超賣反彈信號"
                ],
                "bearish": [
                    "RSI從超買區回落，回調壓力增加",
                    "RSI跌破50中軸，動能轉為負面",
                    "RSI在70以上出現背離，超買回調信號"
                ],
                "neutral": [
                    "RSI在40-60區間震盪，動能中性",
                    "RSI變化不大，市場觀望",
                    "RSI在中軸附近，方向不明"
                ]
            },
            "布林通道": {
                "bullish": [
                    "股價突破布林上軌，動能強勁",
                    "布林通道開口擴大，波動性增加",
                    "股價在布林上軌附近，強勢整理"
                ],
                "bearish": [
                    "股價跌破布林下軌，壓力沉重",
                    "布林通道開口擴大，波動性增加",
                    "股價在布林下軌附近，弱勢整理"
                ],
                "neutral": [
                    "股價在布林通道中軌附近，震盪整理",
                    "布林通道開口收窄，波動性降低",
                    "股價在布林通道內正常波動"
                ]
            }
        }
        
        self.volatility_patterns = {
            "high": [
                "五日波動率達到15%以上，市場不確定性增加",
                "日內振幅擴大，投資人需謹慎操作",
                "波動率創近期新高，風險控制更重要"
            ],
            "medium": [
                "五日波動率在8-12%之間，屬於正常範圍",
                "日內振幅適中，市場情緒相對穩定",
                "波動率維持在合理水平"
            ],
            "low": [
                "五日波動率低於5%，市場趨於平靜",
                "日內振幅縮小，觀望氣氛濃厚",
                "波動率創新低，市場缺乏方向"
            ]
        }
        
        self.volume_patterns = {
            "high": [
                "成交量放大至日均量的1.5倍以上，買盤積極",
                "量價配合良好，上漲動能強勁",
                "放量突破，技術面轉強"
            ],
            "medium": [
                "成交量維持在日均量附近，市場觀望",
                "量價關係正常，無特殊信號",
                "成交量適中，市場情緒穩定"
            ],
            "low": [
                "成交量萎縮至日均量的0.7倍以下，買盤觀望",
                "量縮價跌，動能不足",
                "成交量低迷，市場缺乏參與度"
            ]
        }
    
    def generate_technical_explanation(self, 
                                      stock_name: str,
                                      technical_score: float,
                                      confidence_score: float,
                                      persona: str) -> str:
        """生成技術指標解釋"""
        
        # 根據評分決定整體傾向
        if technical_score > 6.5:
            overall_signal = "bullish"
            signal_strength = "偏多"
        elif technical_score < 3.5:
            overall_signal = "bearish"
            signal_strength = "偏空"
        else:
            overall_signal = "neutral"
            signal_strength = "中性"
        
        # 根據信心度調整解釋的確定性
        if confidence_score > 70:
            certainty = "明確"
            confidence_desc = "技術指標一致性高"
        elif confidence_score > 50:
            certainty = "較明確"
            confidence_desc = "技術指標部分一致"
        else:
            certainty = "不明確"
            confidence_desc = "技術指標分歧較大"
        
        # 生成具體的技術指標解釋
        explanations = []
        
        # 隨機選擇2-3個技術指標進行解釋
        selected_indicators = random.sample(list(self.technical_indicators.keys()), 
                                          min(3, len(self.technical_indicators)))
        
        for indicator in selected_indicators:
            indicator_explanation = self._generate_indicator_explanation(
                indicator, overall_signal, persona
            )
            explanations.append(indicator_explanation)
        
        # 添加波動率和成交量分析
        volatility_explanation = self._generate_volatility_explanation(persona)
        volume_explanation = self._generate_volume_explanation(persona)
        
        explanations.extend([volatility_explanation, volume_explanation])
        
        # 根據persona調整解釋風格
        if persona == "技術派":
            return self._format_technical_style(stock_name, signal_strength, certainty, 
                                              confidence_desc, explanations, technical_score)
        elif persona == "新聞派":
            return self._format_news_style(stock_name, signal_strength, certainty, 
                                          confidence_desc, explanations, technical_score)
        else:  # 總經派
            return self._format_macro_style(stock_name, signal_strength, certainty, 
                                          confidence_desc, explanations, technical_score)
    
    def _generate_indicator_explanation(self, indicator: str, signal: str, persona: str) -> str:
        """生成單一指標解釋"""
        
        explanations = self.technical_indicators[indicator][signal]
        explanation = random.choice(explanations)
        
        # 根據persona調整表達方式
        if persona == "技術派":
            return f"📊 {indicator}：{explanation}"
        elif persona == "新聞派":
            return f"📈 {indicator}指標顯示：{explanation}"
        else:  # 總經派
            return f"📋 {indicator}技術面：{explanation}"
    
    def _generate_volatility_explanation(self, persona: str) -> str:
        """生成波動率解釋"""
        
        # 隨機選擇波動率模式
        volatility_type = random.choice(list(self.volatility_patterns.keys()))
        explanation = random.choice(self.volatility_patterns[volatility_type])
        
        if persona == "技術派":
            return f"📊 波動率分析：{explanation}"
        elif persona == "新聞派":
            return f"📈 市場波動：{explanation}"
        else:  # 總經派
            return f"📋 波動狀況：{explanation}"
    
    def _generate_volume_explanation(self, persona: str) -> str:
        """生成成交量解釋"""
        
        # 隨機選擇成交量模式
        volume_type = random.choice(list(self.volume_patterns.keys()))
        explanation = random.choice(self.volume_patterns[volume_type])
        
        if persona == "技術派":
            return f"📊 成交量分析：{explanation}"
        elif persona == "新聞派":
            return f"📈 市場參與度：{explanation}"
        else:  # 總經派
            return f"📋 成交狀況：{explanation}"
    
    def _format_technical_style(self, stock_name: str, signal: str, certainty: str, 
                               confidence: str, explanations: List[str], score: float) -> str:
        """技術派風格格式化"""
        
        return f"""📊 {stock_name} 技術分析報告：

🎯 整體評分：{score:.1f}/10 ({signal})
🎯 信心度：{certainty} ({confidence})

📈 技術指標詳解：
{chr(10).join(explanations)}

💡 操作建議：基於技術指標，建議{'偏多操作' if signal == '偏多' else '偏空操作' if signal == '偏空' else '觀望等待'}"""
    
    def _format_news_style(self, stock_name: str, signal: str, certainty: str, 
                          confidence: str, explanations: List[str], score: float) -> str:
        """新聞派風格格式化"""
        
        return f"""📈 {stock_name} 市場分析：

📊 技術評分：{score:.1f}/10 ({signal})
📊 可信度：{certainty} ({confidence})

📋 市場動態：
{chr(10).join(explanations)}

💡 市場觀點：目前市場{'樂觀' if signal == '偏多' else '謹慎' if signal == '偏空' else '觀望'}"""
    
    def _format_macro_style(self, stock_name: str, signal: str, certainty: str, 
                           confidence: str, explanations: List[str], score: float) -> str:
        """總經派風格格式化"""
        
        return f"""📋 {stock_name} 基本面分析：

📊 技術面評分：{score:.1f}/10 ({signal})
📊 分析可信度：{certainty} ({confidence})

📈 技術背景：
{chr(10).join(explanations)}

💡 投資建議：從基本面角度，建議{'長期持有' if signal == '偏多' else '謹慎投資' if signal == '偏空' else '分批布局'}"""

# 創建全局實例
technical_explanation_generator = TechnicalExplanationGenerator()
























