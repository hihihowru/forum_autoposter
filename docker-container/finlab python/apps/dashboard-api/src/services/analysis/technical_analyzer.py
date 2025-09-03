"""
技術分析計算器
基於 Finlab OHLC 數據計算各種技術指標
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import finlab
import finlab.data as fdata

logger = logging.getLogger(__name__)

@dataclass
class TechnicalIndicator:
    """技術指標數據"""
    name: str
    current_value: float
    previous_value: Optional[float]
    signal: str  # "bullish", "bearish", "neutral"
    strength: str  # "strong", "moderate", "weak"
    description: str

@dataclass
class TechnicalAnalysis:
    """完整技術分析結果"""
    stock_id: str
    stock_name: str
    analysis_date: str
    current_price: float
    indicators: Dict[str, TechnicalIndicator]
    overall_signal: str
    confidence_score: float
    summary: str

class TechnicalAnalyzer:
    """技術分析計算器"""
    
    def __init__(self):
        self._finlab_logged_in = False
        logger.info("技術分析計算器初始化完成")
    
    def _ensure_finlab_login(self):
        """確保 Finlab 已登入"""
        if not self._finlab_logged_in:
            try:
                import os
                finlab_key = os.getenv('FINLAB_API_KEY')
                if finlab_key:
                    finlab.login(finlab_key)
                    self._finlab_logged_in = True
                    logger.info("Finlab API 登入成功")
            except Exception as e:
                logger.error(f"Finlab API 登入失敗: {e}")
    
    async def get_stock_technical_analysis(self, stock_id: str, stock_name: str = "", days: int = 60) -> Optional[TechnicalAnalysis]:
        """獲取股票完整技術分析"""
        
        try:
            self._ensure_finlab_login()
            
            print(f"📊 計算 {stock_name}({stock_id}) 技術指標...")
            
            # 獲取歷史數據
            ohlc_data = await self._fetch_ohlc_history(stock_id, days)
            if ohlc_data is None or len(ohlc_data) < 20:
                logger.error(f"股票 {stock_id} 歷史數據不足")
                return None
            
            # 計算各種技術指標
            indicators = {}
            
            # 1. MACD
            macd_indicator = self._calculate_macd(ohlc_data)
            if macd_indicator:
                indicators['MACD'] = macd_indicator
                
            # 2. KD指標
            kd_indicator = self._calculate_kd(ohlc_data)
            if kd_indicator:
                indicators['KD'] = kd_indicator
                
            # 3. 布林通道
            bollinger_indicator = self._calculate_bollinger_bands(ohlc_data)
            if bollinger_indicator:
                indicators['BOLLINGER'] = bollinger_indicator
                
            # 4. RSI
            rsi_indicator = self._calculate_rsi(ohlc_data)
            if rsi_indicator:
                indicators['RSI'] = rsi_indicator
                
            # 5. 移動平均線
            ma_indicator = self._calculate_moving_averages(ohlc_data)
            if ma_indicator:
                indicators['MA'] = ma_indicator
                
            # 6. 量價分析
            volume_indicator = self._calculate_volume_analysis(ohlc_data)
            if volume_indicator:
                indicators['VOLUME'] = volume_indicator
                
            # 7. 波動率
            volatility_indicator = self._calculate_volatility(ohlc_data)
            if volatility_indicator:
                indicators['VOLATILITY'] = volatility_indicator
            
            # 計算綜合訊號
            overall_signal, confidence = self._calculate_overall_signal(indicators)
            
            # 生成技術分析摘要
            summary = self._generate_technical_summary(indicators, overall_signal)
            
            current_price = float(ohlc_data['close'].iloc[-1])
            analysis_date = ohlc_data.index[-1].strftime('%Y-%m-%d')
            
            technical_analysis = TechnicalAnalysis(
                stock_id=stock_id,
                stock_name=stock_name or stock_id,
                analysis_date=analysis_date,
                current_price=current_price,
                indicators=indicators,
                overall_signal=overall_signal,
                confidence_score=confidence,
                summary=summary
            )
            
            print(f"✅ 完成 {stock_name}({stock_id}) 技術分析")
            print(f"  📈 綜合訊號: {overall_signal} (信心度: {confidence:.1f}%)")
            print(f"  📊 計算指標: {len(indicators)} 個")
            
            return technical_analysis
            
        except Exception as e:
            logger.error(f"計算股票 {stock_id} 技術分析失敗: {e}")
            return None
    
    async def _fetch_ohlc_history(self, stock_id: str, days: int) -> Optional[pd.DataFrame]:
        """獲取股票歷史OHLC數據"""
        
        try:
            # 獲取各種價格數據
            open_price = fdata.get('price:開盤價')
            high_price = fdata.get('price:最高價')
            low_price = fdata.get('price:最低價')
            close_price = fdata.get('price:收盤價')
            volume = fdata.get('price:成交股數')
            
            if stock_id not in close_price.columns:
                logger.error(f"未找到股票 {stock_id} 的數據")
                return None
            
            # 獲取最近N天的數據
            stock_close = close_price[stock_id].dropna()
            if len(stock_close) < days:
                days = len(stock_close)
            
            recent_data = stock_close.tail(days)
            start_date = recent_data.index[0]
            end_date = recent_data.index[-1]
            
            # 組合OHLC數據
            ohlc_df = pd.DataFrame({
                'open': open_price[stock_id][start_date:end_date],
                'high': high_price[stock_id][start_date:end_date],
                'low': low_price[stock_id][start_date:end_date],
                'close': close_price[stock_id][start_date:end_date],
                'volume': volume[stock_id][start_date:end_date] if volume is not None and stock_id in volume.columns else 0
            }).dropna()
            
            return ohlc_df
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 歷史數據失敗: {e}")
            return None
    
    def _calculate_macd(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算 MACD 指標"""
        
        try:
            close = df['close']
            
            # 計算 EMA
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            
            # MACD 線
            macd_line = ema12 - ema26
            
            # 信號線 (9日EMA)
            signal_line = macd_line.ewm(span=9).mean()
            
            # MACD 柱狀圖
            macd_histogram = macd_line - signal_line
            
            # 當前值
            current_macd = float(macd_line.iloc[-1])
            current_signal = float(signal_line.iloc[-1])
            current_histogram = float(macd_histogram.iloc[-1])
            
            # 前一日值
            prev_macd = float(macd_line.iloc[-2])
            prev_signal = float(signal_line.iloc[-2])
            prev_histogram = float(macd_histogram.iloc[-2])
            
            # 判斷訊號
            if current_macd > current_signal and prev_macd <= prev_signal:
                signal = "bullish"
                strength = "strong"
                description = "MACD黃金交叉，買進信號"
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signal = "bearish"
                strength = "strong"
                description = "MACD死亡交叉，賣出信號"
            elif current_histogram > 0 and current_histogram > prev_histogram:
                signal = "bullish"
                strength = "moderate"
                description = "MACD柱狀圖轉強，偏多格局"
            elif current_histogram < 0 and current_histogram < prev_histogram:
                signal = "bearish"
                strength = "moderate"
                description = "MACD柱狀圖轉弱，偏空格局"
            else:
                signal = "neutral"
                strength = "weak"
                description = "MACD盤整格局，方向不明"
            
            return TechnicalIndicator(
                name="MACD",
                current_value=current_histogram,
                previous_value=prev_histogram,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算 MACD 失敗: {e}")
            return None
    
    def _calculate_kd(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算 KD 指標"""
        
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # 計算 RSV
            period = 9
            lowest_low = low.rolling(window=period).min()
            highest_high = high.rolling(window=period).max()
            rsv = 100 * (close - lowest_low) / (highest_high - lowest_low)
            
            # 計算 K 值 (3日移動平均)
            k_values = rsv.ewm(com=2).mean()
            
            # 計算 D 值 (K值的3日移動平均)
            d_values = k_values.ewm(com=2).mean()
            
            current_k = float(k_values.iloc[-1])
            current_d = float(d_values.iloc[-1])
            prev_k = float(k_values.iloc[-2])
            prev_d = float(d_values.iloc[-2])
            
            # 判斷訊號
            if current_k > current_d and prev_k <= prev_d and current_k < 80:
                signal = "bullish"
                strength = "strong"
                description = "KD黃金交叉，且未過熱"
            elif current_k < current_d and prev_k >= prev_d and current_k > 20:
                signal = "bearish"
                strength = "strong"
                description = "KD死亡交叉，且未超賣"
            elif current_k > 80 and current_d > 80:
                signal = "bearish"
                strength = "moderate"
                description = "KD進入超買區，注意回檔"
            elif current_k < 20 and current_d < 20:
                signal = "bullish"
                strength = "moderate"
                description = "KD進入超賣區，可能反彈"
            else:
                signal = "neutral"
                strength = "weak"
                description = "KD處於中性區間"
            
            return TechnicalIndicator(
                name="KD",
                current_value=current_k,
                previous_value=prev_k,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算 KD 失敗: {e}")
            return None
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算布林通道"""
        
        try:
            close = df['close']
            period = 20
            
            # 中軌 (20日移動平均)
            middle_band = close.rolling(window=period).mean()
            
            # 標準差
            std = close.rolling(window=period).std()
            
            # 上軌和下軌
            upper_band = middle_band + (std * 2)
            lower_band = middle_band - (std * 2)
            
            current_price = float(close.iloc[-1])
            current_upper = float(upper_band.iloc[-1])
            current_middle = float(middle_band.iloc[-1])
            current_lower = float(lower_band.iloc[-1])
            
            # 計算位置百分比
            bb_position = (current_price - current_lower) / (current_upper - current_lower) * 100
            
            # 判斷訊號
            if current_price > current_upper:
                signal = "bearish"
                strength = "moderate"
                description = "價格突破上軌，可能過熱"
            elif current_price < current_lower:
                signal = "bullish"
                strength = "moderate"
                description = "價格跌破下軌，可能超賣"
            elif bb_position > 80:
                signal = "bearish"
                strength = "weak"
                description = "接近上軌，注意壓力"
            elif bb_position < 20:
                signal = "bullish"
                strength = "weak"
                description = "接近下軌，可能支撐"
            else:
                signal = "neutral"
                strength = "weak"
                description = "價格在布林通道中軌附近"
            
            return TechnicalIndicator(
                name="BOLLINGER",
                current_value=bb_position,
                previous_value=None,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算布林通道失敗: {e}")
            return None
    
    def _calculate_rsi(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算 RSI 指標"""
        
        try:
            close = df['close']
            period = 14
            
            # 計算價格變化
            delta = close.diff()
            
            # 分離上漲和下跌
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # 計算平均漲跌幅
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # RSI 計算
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1])
            prev_rsi = float(rsi.iloc[-2])
            
            # 判斷訊號
            if current_rsi > 70:
                signal = "bearish"
                strength = "moderate"
                description = f"RSI進入超買區 ({current_rsi:.1f})"
            elif current_rsi < 30:
                signal = "bullish"
                strength = "moderate"
                description = f"RSI進入超賣區 ({current_rsi:.1f})"
            elif current_rsi > 50 and prev_rsi <= 50:
                signal = "bullish"
                strength = "weak"
                description = f"RSI突破中線 ({current_rsi:.1f})"
            elif current_rsi < 50 and prev_rsi >= 50:
                signal = "bearish"
                strength = "weak"
                description = f"RSI跌破中線 ({current_rsi:.1f})"
            else:
                signal = "neutral"
                strength = "weak"
                description = f"RSI中性區間 ({current_rsi:.1f})"
            
            return TechnicalIndicator(
                name="RSI",
                current_value=current_rsi,
                previous_value=prev_rsi,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算 RSI 失敗: {e}")
            return None
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算移動平均線"""
        
        try:
            close = df['close']
            
            # 不同週期的移動平均
            ma5 = close.rolling(window=5).mean()
            ma10 = close.rolling(window=10).mean()
            ma20 = close.rolling(window=20).mean()
            ma60 = close.rolling(window=60).mean() if len(close) >= 60 else None
            
            current_price = float(close.iloc[-1])
            current_ma5 = float(ma5.iloc[-1])
            current_ma10 = float(ma10.iloc[-1])
            current_ma20 = float(ma20.iloc[-1])
            
            # 判斷多空排列
            if current_ma5 > current_ma10 > current_ma20 and current_price > current_ma5:
                signal = "bullish"
                strength = "strong"
                description = "均線多頭排列，價格在均線之上"
            elif current_ma5 < current_ma10 < current_ma20 and current_price < current_ma5:
                signal = "bearish"
                strength = "strong"
                description = "均線空頭排列，價格在均線之下"
            elif current_price > current_ma20:
                signal = "bullish"
                strength = "moderate"
                description = "價格站上20日均線"
            elif current_price < current_ma20:
                signal = "bearish"
                strength = "moderate"
                description = "價格跌破20日均線"
            else:
                signal = "neutral"
                strength = "weak"
                description = "均線糾結，方向不明"
            
            return TechnicalIndicator(
                name="MA",
                current_value=current_price - current_ma20,
                previous_value=None,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算移動平均線失敗: {e}")
            return None
    
    def _calculate_volume_analysis(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算量價分析"""
        
        try:
            close = df['close']
            volume = df['volume']
            
            if volume.sum() == 0:  # 如果沒有成交量數據
                return None
            
            # 價格變化
            price_change = close.pct_change()
            
            # 成交量移動平均
            vol_ma = volume.rolling(window=20).mean()
            
            current_volume = float(volume.iloc[-1])
            current_vol_ma = float(vol_ma.iloc[-1])
            current_price_change = float(price_change.iloc[-1])
            
            # 量比 (當日成交量 / 20日均量)
            volume_ratio = current_volume / current_vol_ma if current_vol_ma > 0 else 1
            
            # 判斷量價關係
            if volume_ratio > 1.5 and current_price_change > 0.02:
                signal = "bullish"
                strength = "strong"
                description = f"價漲量增，量比 {volume_ratio:.1f}"
            elif volume_ratio > 1.5 and current_price_change < -0.02:
                signal = "bearish"
                strength = "strong"
                description = f"價跌量增，量比 {volume_ratio:.1f}"
            elif volume_ratio > 1.2:
                signal = "neutral"
                strength = "moderate"
                description = f"成交量放大，量比 {volume_ratio:.1f}"
            else:
                signal = "neutral"
                strength = "weak"
                description = f"成交量正常，量比 {volume_ratio:.1f}"
            
            return TechnicalIndicator(
                name="VOLUME",
                current_value=volume_ratio,
                previous_value=None,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算量價分析失敗: {e}")
            return None
    
    def _calculate_volatility(self, df: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """計算波動率"""
        
        try:
            close = df['close']
            
            # 日報酬率
            returns = close.pct_change()
            
            # 20日波動率 (年化)
            volatility = returns.rolling(window=20).std() * (252 ** 0.5) * 100
            
            current_vol = float(volatility.iloc[-1])
            avg_vol = float(volatility.mean())
            
            # 判斷波動率水準
            if current_vol > avg_vol * 1.5:
                signal = "bearish"
                strength = "moderate"
                description = f"波動率偏高 ({current_vol:.1f}%)"
            elif current_vol < avg_vol * 0.7:
                signal = "neutral"
                strength = "weak"
                description = f"波動率偏低 ({current_vol:.1f}%)"
            else:
                signal = "neutral"
                strength = "weak"
                description = f"波動率正常 ({current_vol:.1f}%)"
            
            return TechnicalIndicator(
                name="VOLATILITY",
                current_value=current_vol,
                previous_value=avg_vol,
                signal=signal,
                strength=strength,
                description=description
            )
            
        except Exception as e:
            logger.error(f"計算波動率失敗: {e}")
            return None
    
    def _calculate_overall_signal(self, indicators: Dict[str, TechnicalIndicator]) -> Tuple[str, float]:
        """計算綜合技術訊號"""
        
        bullish_score = 0
        bearish_score = 0
        total_weight = 0
        
        # 權重設定
        weights = {
            'MACD': 3,
            'KD': 2,
            'MA': 3,
            'RSI': 2,
            'BOLLINGER': 1,
            'VOLUME': 2,
            'VOLATILITY': 1
        }
        
        for name, indicator in indicators.items():
            weight = weights.get(name, 1)
            
            if indicator.signal == "bullish":
                if indicator.strength == "strong":
                    bullish_score += weight * 3
                elif indicator.strength == "moderate":
                    bullish_score += weight * 2
                else:
                    bullish_score += weight * 1
            elif indicator.signal == "bearish":
                if indicator.strength == "strong":
                    bearish_score += weight * 3
                elif indicator.strength == "moderate":
                    bearish_score += weight * 2
                else:
                    bearish_score += weight * 1
            
            total_weight += weight
        
        # 計算信心度
        net_score = bullish_score - bearish_score
        confidence = abs(net_score) / (total_weight * 3) * 100
        
        # 判斷綜合訊號
        if net_score > total_weight * 0.3:
            return "bullish", confidence
        elif net_score < -total_weight * 0.3:
            return "bearish", confidence
        else:
            return "neutral", confidence
    
    def _generate_technical_summary(self, indicators: Dict[str, TechnicalIndicator], overall_signal: str) -> str:
        """生成技術分析摘要"""
        
        key_signals = []
        
        for name, indicator in indicators.items():
            if indicator.strength in ["strong", "moderate"]:
                key_signals.append(indicator.description)
        
        if overall_signal == "bullish":
            signal_desc = "偏多格局"
        elif overall_signal == "bearish":
            signal_desc = "偏空格局"
        else:
            signal_desc = "中性盤整"
        
        summary = f"技術面{signal_desc}。{' '.join(key_signals[:3])}"
        
        return summary

# 創建服務實例的工廠函數
def create_technical_analyzer() -> TechnicalAnalyzer:
    """創建技術分析器實例"""
    return TechnicalAnalyzer()

