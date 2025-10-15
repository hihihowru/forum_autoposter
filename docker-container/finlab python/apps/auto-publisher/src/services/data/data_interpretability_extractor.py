#!/usr/bin/env python3
"""
數據可解釋性提取器
將原始數據轉化為可解釋的洞察，支持月營收、財報、技術面數據
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class DataInterpretabilityExtractor:
    """數據可解釋性提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_revenue_insights(self, revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取月營收數據洞察"""
        try:
            insights = {
                'type': 'revenue',
                'symbol': revenue_data.get('symbol', ''),
                'company_name': revenue_data.get('company_name', ''),
                'revenue': revenue_data.get('revenue', 0),
                'yoy_growth': revenue_data.get('yoy_growth', 0),
                'mom_growth': revenue_data.get('mom_growth', 0),
                'insights': []
            }
            
            # 分析營收成長趨勢
            if insights['yoy_growth'] > 20:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"年增率達 {insights['yoy_growth']:.1f}%，成長動能強勁",
                    'confidence': 0.9
                })
            elif insights['yoy_growth'] > 0:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"年增率 {insights['yoy_growth']:.1f}%，維持成長趨勢",
                    'confidence': 0.7
                })
            else:
                insights['insights'].append({
                    'type': 'negative',
                    'message': f"年增率 {insights['yoy_growth']:.1f}%，成長動能減弱",
                    'confidence': 0.8
                })
            
            # 分析月增率
            if insights['mom_growth'] > 10:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"月增率 {insights['mom_growth']:.1f}%，單月表現亮眼",
                    'confidence': 0.8
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"提取營收洞察失敗: {str(e)}")
            return {}
    
    def extract_financial_insights(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取財報數據洞察"""
        try:
            insights = {
                'type': 'financial',
                'symbol': financial_data.get('symbol', ''),
                'company_name': financial_data.get('company_name', ''),
                'eps': financial_data.get('eps', 0),
                'eps_yoy': financial_data.get('eps_yoy', 0),
                'revenue': financial_data.get('revenue', 0),
                'revenue_yoy': financial_data.get('revenue_yoy', 0),
                'gross_margin': financial_data.get('gross_margin', 0),
                'net_margin': financial_data.get('net_margin', 0),
                'insights': []
            }
            
            # 分析 EPS 表現
            if insights['eps'] > 0 and insights['eps_yoy'] > 0:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"EPS {insights['eps']:.2f} 元，年增 {insights['eps_yoy']:.1f}%",
                    'confidence': 0.9
                })
            
            # 分析毛利率
            if insights['gross_margin'] > 30:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"毛利率 {insights['gross_margin']:.1f}%，獲利能力強",
                    'confidence': 0.8
                })
            
            # 分析營收成長
            if insights['revenue_yoy'] > 20:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"營收年增 {insights['revenue_yoy']:.1f}%，成長動能強勁",
                    'confidence': 0.9
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"提取財報洞察失敗: {str(e)}")
            return {}
    
    def extract_technical_insights(self, technical_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取技術面數據洞察"""
        try:
            insights = {
                'type': 'technical',
                'symbol': technical_data.get('symbol', ''),
                'current_price': technical_data.get('current_price', 0),
                'ma5': technical_data.get('ma5', 0),
                'ma10': technical_data.get('ma10', 0),
                'ma20': technical_data.get('ma20', 0),
                'rsi': technical_data.get('rsi', 0),
                'macd': technical_data.get('macd', 0),
                'volume': technical_data.get('volume', 0),
                'avg_volume': technical_data.get('avg_volume', 0),
                'insights': []
            }
            
            # 分析均線排列
            if insights['ma5'] > insights['ma10'] > insights['ma20']:
                insights['insights'].append({
                    'type': 'positive',
                    'message': "均線多頭排列，技術面偏多",
                    'confidence': 0.8
                })
            elif insights['ma5'] < insights['ma10'] < insights['ma20']:
                insights['insights'].append({
                    'type': 'negative',
                    'message': "均線空頭排列，技術面偏空",
                    'confidence': 0.8
                })
            
            # 分析 RSI
            if insights['rsi'] > 70:
                insights['insights'].append({
                    'type': 'warning',
                    'message': f"RSI {insights['rsi']:.1f}，可能過熱",
                    'confidence': 0.7
                })
            elif insights['rsi'] < 30:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"RSI {insights['rsi']:.1f}，可能超賣",
                    'confidence': 0.7
                })
            
            # 分析成交量
            volume_ratio = insights['volume'] / insights['avg_volume'] if insights['avg_volume'] > 0 else 1
            if volume_ratio > 2:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"成交量放大 {volume_ratio:.1f} 倍，交投熱絡",
                    'confidence': 0.8
                })
            
            # 分析 MACD
            if insights['macd'] > 0:
                insights['insights'].append({
                    'type': 'positive',
                    'message': "MACD 為正，動能向上",
                    'confidence': 0.7
                })
            else:
                insights['insights'].append({
                    'type': 'negative',
                    'message': "MACD 為負，動能向下",
                    'confidence': 0.7
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"提取技術面洞察失敗: {str(e)}")
            return {}
    
    def generate_explanations(self, insights: Dict[str, Any]) -> List[str]:
        """生成數據解釋"""
        explanations = []
        
        if not insights or 'insights' not in insights:
            return explanations
        
        for insight in insights['insights']:
            if insight['type'] == 'positive':
                explanations.append(f"✅ {insight['message']}")
            elif insight['type'] == 'negative':
                explanations.append(f"⚠️ {insight['message']}")
            elif insight['type'] == 'warning':
                explanations.append(f"⚠️ {insight['message']}")
        
        return explanations
    
    def format_for_content(self, insights: Dict[str, Any]) -> str:
        """格式化為內容生成格式"""
        try:
            if not insights:
                return ""
            
            content_parts = []
            
            # 添加標題
            if insights['type'] == 'revenue':
                content_parts.append(f"📊 {insights['company_name']}({insights['symbol']}) 月營收分析")
            elif insights['type'] == 'financial':
                content_parts.append(f"📈 {insights['company_name']}({insights['symbol']}) 財報分析")
            elif insights['type'] == 'technical':
                content_parts.append(f"📉 {insights['symbol']} 技術面分析")
            
            content_parts.append("")
            
            # 添加關鍵數據
            if insights['type'] == 'revenue':
                content_parts.append(f"💰 營收: {insights['revenue']:,.0f} 萬元")
                content_parts.append(f"📈 年增率: {insights['yoy_growth']:.1f}%")
                content_parts.append(f"📊 月增率: {insights['mom_growth']:.1f}%")
            elif insights['type'] == 'financial':
                content_parts.append(f"💰 EPS: {insights['eps']:.2f} 元")
                content_parts.append(f"📈 毛利率: {insights['gross_margin']:.1f}%")
                content_parts.append(f"📊 營收年增: {insights['revenue_yoy']:.1f}%")
            elif insights['type'] == 'technical':
                content_parts.append(f"💰 現價: {insights['current_price']:.2f}")
                content_parts.append(f"📈 RSI: {insights['rsi']:.1f}")
                content_parts.append(f"📊 成交量比: {insights['volume']/insights['avg_volume']:.1f}x")
            
            content_parts.append("")
            
            # 添加洞察
            explanations = self.generate_explanations(insights)
            for explanation in explanations:
                content_parts.append(explanation)
            
            return "\n".join(content_parts)
            
        except Exception as e:
            self.logger.error(f"格式化內容失敗: {str(e)}")
            return ""
    
    def extract_all_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """提取所有類型的洞察"""
        try:
            all_insights = {
                'revenue': None,
                'financial': None,
                'technical': None,
                'summary': []
            }
            
            # 提取營收洞察
            if 'revenue_data' in data:
                all_insights['revenue'] = self.extract_revenue_insights(data['revenue_data'])
            
            # 提取財報洞察
            if 'financial_data' in data:
                all_insights['financial'] = self.extract_financial_insights(data['financial_data'])
            
            # 提取技術面洞察
            if 'technical_data' in data:
                all_insights['technical'] = self.extract_technical_insights(data['technical_data'])
            
            # 生成總結
            for insight_type, insight_data in all_insights.items():
                if insight_data and insight_type != 'summary':
                    explanations = self.generate_explanations(insight_data)
                    all_insights['summary'].extend(explanations)
            
            return all_insights
            
        except Exception as e:
            self.logger.error(f"提取所有洞察失敗: {str(e)}")
            return {}

# 測試函數
def test_extractor():
    """測試數據可解釋性提取器"""
    extractor = DataInterpretabilityExtractor()
    
    # 測試營收數據
    revenue_data = {
        'symbol': '2330',
        'company_name': '台積電',
        'revenue': 150000000,
        'yoy_growth': 25.5,
        'mom_growth': 8.2
    }
    
    revenue_insights = extractor.extract_revenue_insights(revenue_data)
    print("營收洞察:")
    print(extractor.format_for_content(revenue_insights))
    print()
    
    # 測試技術面數據
    technical_data = {
        'symbol': '2330',
        'current_price': 580.0,
        'ma5': 575.0,
        'ma10': 570.0,
        'ma20': 565.0,
        'rsi': 65.0,
        'macd': 2.5,
        'volume': 50000000,
        'avg_volume': 30000000
    }
    
    technical_insights = extractor.extract_technical_insights(technical_data)
    print("技術面洞察:")
    print(extractor.format_for_content(technical_insights))

if __name__ == "__main__":
    test_extractor()


