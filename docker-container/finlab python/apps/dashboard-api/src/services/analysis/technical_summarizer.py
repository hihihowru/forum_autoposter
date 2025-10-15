"""
技術指標 LLM 摘要生成器
使用 LLM 對各技術指標進行專業摘要
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .technical_analyzer import TechnicalAnalysis, TechnicalIndicator

logger = logging.getLogger(__name__)

@dataclass
class IndicatorSummary:
    """技術指標摘要"""
    indicator_name: str
    technical_summary: str
    market_implication: str
    trading_suggestion: str
    confidence_level: str

@dataclass
class ComprehensiveTechnicalSummary:
    """綜合技術分析摘要"""
    stock_id: str
    stock_name: str
    individual_summaries: Dict[str, IndicatorSummary]
    integrated_analysis: str
    key_levels: Dict[str, float]
    risk_assessment: str
    trading_strategy: str

class TechnicalSummarizer:
    """技術指標 LLM 摘要生成器"""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_openai()
        logger.info("技術指標摘要生成器初始化完成")
    
    def _initialize_openai(self):
        """初始化 OpenAI 客戶端"""
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        except ImportError:
            logger.error("無法導入 OpenAI 套件")
        except Exception as e:
            logger.error(f"初始化 OpenAI 客戶端失敗: {e}")
    
    async def generate_comprehensive_summary(self, technical_analysis: TechnicalAnalysis) -> Optional[ComprehensiveTechnicalSummary]:
        """生成綜合技術分析摘要"""
        
        try:
            print(f"🤖 生成 {technical_analysis.stock_name} 技術指標 LLM 摘要...")
            
            # 為每個技術指標生成個別摘要
            individual_summaries = {}
            
            for indicator_name, indicator in technical_analysis.indicators.items():
                summary = await self._summarize_individual_indicator(
                    indicator, technical_analysis.stock_name, technical_analysis.current_price
                )
                if summary:
                    individual_summaries[indicator_name] = summary
                    print(f"  ✅ {indicator_name}: {summary.technical_summary[:50]}...")
                
                # 避免 API 限制
                await asyncio.sleep(0.5)
            
            # 生成綜合分析
            integrated_analysis = await self._generate_integrated_analysis(
                technical_analysis, individual_summaries
            )
            
            # 識別關鍵價位
            key_levels = self._identify_key_levels(technical_analysis)
            
            # 生成風險評估
            risk_assessment = await self._generate_risk_assessment(
                technical_analysis, individual_summaries
            )
            
            # 生成交易策略
            trading_strategy = await self._generate_trading_strategy(
                technical_analysis, individual_summaries
            )
            
            comprehensive_summary = ComprehensiveTechnicalSummary(
                stock_id=technical_analysis.stock_id,
                stock_name=technical_analysis.stock_name,
                individual_summaries=individual_summaries,
                integrated_analysis=integrated_analysis or "技術面分析完成",
                key_levels=key_levels,
                risk_assessment=risk_assessment or "風險中性",
                trading_strategy=trading_strategy or "建議觀望"
            )
            
            print(f"✅ 完成 {technical_analysis.stock_name} LLM 技術摘要")
            
            return comprehensive_summary
            
        except Exception as e:
            logger.error(f"生成綜合技術摘要失敗: {e}")
            return None
    
    async def _summarize_individual_indicator(self, 
                                           indicator: TechnicalIndicator, 
                                           stock_name: str, 
                                           current_price: float) -> Optional[IndicatorSummary]:
        """為單一技術指標生成摘要"""
        
        if not self.openai_client:
            return None
        
        try:
            # 針對不同指標設計專門的 prompt
            prompts = {
                'MACD': self._get_macd_prompt(indicator, stock_name, current_price),
                'KD': self._get_kd_prompt(indicator, stock_name, current_price),
                'BOLLINGER': self._get_bollinger_prompt(indicator, stock_name, current_price),
                'RSI': self._get_rsi_prompt(indicator, stock_name, current_price),
                'MA': self._get_ma_prompt(indicator, stock_name, current_price),
                'VOLUME': self._get_volume_prompt(indicator, stock_name, current_price),
                'VOLATILITY': self._get_volatility_prompt(indicator, stock_name, current_price)
            }
            
            prompt = prompts.get(indicator.name, self._get_default_prompt(indicator, stock_name, current_price))
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一位資深技術分析師，專精於各種技術指標的解讀與應用。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # 解析回應
            lines = content.split('\n')
            technical_summary = ""
            market_implication = ""
            trading_suggestion = ""
            confidence_level = indicator.strength
            
            for line in lines:
                if line.startswith('技術摘要:') or line.startswith('摘要:'):
                    technical_summary = line.split(':', 1)[1].strip()
                elif line.startswith('市場含義:') or line.startswith('含義:'):
                    market_implication = line.split(':', 1)[1].strip()
                elif line.startswith('交易建議:') or line.startswith('建議:'):
                    trading_suggestion = line.split(':', 1)[1].strip()
            
            # 如果沒有明確分段，使用整段作為技術摘要
            if not technical_summary:
                technical_summary = content[:100] + "..." if len(content) > 100 else content
            
            return IndicatorSummary(
                indicator_name=indicator.name,
                technical_summary=technical_summary or indicator.description,
                market_implication=market_implication or "市場反應待觀察",
                trading_suggestion=trading_suggestion or "建議持續關注",
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error(f"生成 {indicator.name} 指標摘要失敗: {e}")
            return None
    
    def _get_macd_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的 MACD 指標：
當前狀況：{indicator.description}
訊號強度：{indicator.strength}
數值：{indicator.current_value:.3f}

請用技術分析師的角度，簡潔專業地說明：
1. 技術摘要：MACD 當前的技術意義
2. 市場含義：對股價走勢的影響
3. 交易建議：基於此指標的操作建議

請保持簡潔，每項不超過30字。
"""
    
    def _get_kd_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的 KD 指標：
當前狀況：{indicator.description}
K值：{indicator.current_value:.1f}
訊號：{indicator.signal}

請用技術分析師的角度說明：
1. 技術摘要：KD 指標的超買超賣狀況
2. 市場含義：對短期走勢的指引
3. 交易建議：進出場時機判斷

每項請控制在30字內。
"""
    
    def _get_bollinger_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的布林通道：
當前狀況：{indicator.description}
位置百分比：{indicator.current_value:.1f}%
價格：${current_price:.2f}

請說明：
1. 技術摘要：價格在布林通道中的位置意義
2. 市場含義：支撐壓力的判斷
3. 交易建議：基於通道位置的策略

請保持簡潔專業。
"""
    
    def _get_rsi_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的 RSI 指標：
當前 RSI：{indicator.current_value:.1f}
狀況：{indicator.description}
趨勢：{indicator.signal}

請說明：
1. 技術摘要：RSI 的超買超賣判斷
2. 市場含義：動能強弱的解讀
3. 交易建議：基於 RSI 的操作指引

請用專業術語，保持簡潔。
"""
    
    def _get_ma_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的移動平均線：
當前狀況：{indicator.description}
價格位置：${current_price:.2f}
相對位置：{indicator.current_value:.2f}

請說明：
1. 技術摘要：均線排列與趨勢判斷
2. 市場含義：多空格局的確認
3. 交易建議：基於均線的進出場策略

請用技術分析的專業語言。
"""
    
    def _get_volume_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的量價關係：
當前狀況：{indicator.description}
量比：{indicator.current_value:.1f}
價量配合度：{indicator.signal}

請說明：
1. 技術摘要：成交量的技術意義
2. 市場含義：量價背離或確認的判斷
3. 交易建議：基於量能的操作策略

請用量價分析的專業觀點。
"""
    
    def _get_volatility_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的波動率：
當前波動率：{indicator.current_value:.1f}%
狀況：{indicator.description}
市場風險：{indicator.signal}

請說明：
1. 技術摘要：波動率的技術含義
2. 市場含義：市場情緒與風險評估
3. 交易建議：基於波動率的風險管理

請用風險管理的角度分析。
"""
    
    def _get_default_prompt(self, indicator: TechnicalIndicator, stock_name: str, current_price: float) -> str:
        return f"""
請分析 {stock_name} 的 {indicator.name} 技術指標：
當前狀況：{indicator.description}
訊號：{indicator.signal}
強度：{indicator.strength}

請簡潔說明這個技術指標的市場意義和交易建議。
"""
    
    async def _generate_integrated_analysis(self, 
                                          technical_analysis: TechnicalAnalysis, 
                                          individual_summaries: Dict[str, IndicatorSummary]) -> Optional[str]:
        """生成綜合技術分析"""
        
        if not self.openai_client:
            return None
        
        try:
            # 準備綜合分析的輸入
            summaries_text = []
            for name, summary in individual_summaries.items():
                summaries_text.append(f"{name}: {summary.technical_summary}")
            
            prompt = f"""
作為資深技術分析師，請綜合以下技術指標，為 {technical_analysis.stock_name}(${technical_analysis.current_price:.2f}) 提供整體技術分析：

技術指標摘要：
{chr(10).join(summaries_text)}

綜合技術訊號：{technical_analysis.overall_signal}
信心度：{technical_analysis.confidence_score:.1f}%

請提供一個50-80字的綜合技術分析，包括：
1. 整體技術格局判斷
2. 關鍵技術信號確認
3. 短期走勢展望

請用專業但易懂的語言。
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是資深技術分析師，擅長綜合多項技術指標進行整體判斷。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"生成綜合技術分析失敗: {e}")
            return None
    
    async def _generate_risk_assessment(self, 
                                      technical_analysis: TechnicalAnalysis, 
                                      individual_summaries: Dict[str, IndicatorSummary]) -> Optional[str]:
        """生成風險評估"""
        
        # 簡化的風險評估邏輯
        risk_factors = []
        
        # 檢查波動率
        if 'VOLATILITY' in technical_analysis.indicators:
            vol_indicator = technical_analysis.indicators['VOLATILITY']
            if vol_indicator.signal == "bearish":
                risk_factors.append("高波動風險")
        
        # 檢查超買超賣
        if 'RSI' in technical_analysis.indicators:
            rsi_indicator = technical_analysis.indicators['RSI']
            if rsi_indicator.current_value > 70:
                risk_factors.append("超買風險")
            elif rsi_indicator.current_value < 30:
                risk_factors.append("超賣反彈機會")
        
        # 檢查技術背離
        if technical_analysis.overall_signal == "bearish" and technical_analysis.confidence_score > 60:
            risk_factors.append("技術面偏空")
        elif technical_analysis.overall_signal == "bullish" and technical_analysis.confidence_score > 60:
            risk_factors.append("技術面偏多")
        
        if risk_factors:
            return f"注意：{', '.join(risk_factors)}"
        else:
            return "技術風險適中"
    
    async def _generate_trading_strategy(self, 
                                       technical_analysis: TechnicalAnalysis, 
                                       individual_summaries: Dict[str, IndicatorSummary]) -> Optional[str]:
        """生成交易策略建議"""
        
        # 基於綜合訊號的簡化策略
        signal = technical_analysis.overall_signal
        confidence = technical_analysis.confidence_score
        
        if signal == "bullish" and confidence > 70:
            return "建議逢低布局，設定停損"
        elif signal == "bullish" and confidence > 50:
            return "可考慮分批進場"
        elif signal == "bearish" and confidence > 70:
            return "建議減碼或停損"
        elif signal == "bearish" and confidence > 50:
            return "建議保守觀望"
        else:
            return "建議區間操作，等待明確訊號"
    
    def _identify_key_levels(self, technical_analysis: TechnicalAnalysis) -> Dict[str, float]:
        """識別關鍵價位"""
        
        key_levels = {}
        current_price = technical_analysis.current_price
        
        # 基於布林通道識別支撐壓力
        if 'BOLLINGER' in technical_analysis.indicators:
            # 這裡需要更詳細的實現，暫時使用簡化邏輯
            key_levels['support'] = current_price * 0.95
            key_levels['resistance'] = current_price * 1.05
        
        # 基於移動平均線
        if 'MA' in technical_analysis.indicators:
            key_levels['ma20'] = current_price  # 簡化處理
        
        return key_levels

# 創建服務實例的工廠函數
def create_technical_summarizer() -> TechnicalSummarizer:
    """創建技術指標摘要生成器實例"""
    return TechnicalSummarizer()

