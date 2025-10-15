"""
增強版技術分析計算器
支援多週期分析和評分機制
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import finlab
import finlab.data as fdata
from ..data.ohlc_cache_manager import OHLCCacheManager

logger = logging.getLogger(__name__)

@dataclass
class EnhancedTechnicalIndicator:
    """增強版技術指標數據"""
    name: str
    overall_score: float  # 總評分 (0 到 10，5為中性)
    confidence: float     # 信心度 (0-100%)
    signal: str          # "bullish", "bearish", "neutral"
    strength: str        # "strong", "moderate", "weak"
    periods_analysis: Dict[str, Dict[str, Any]]  # 各週期分析
    key_insights: List[str]  # 關鍵洞察
    description: str

@dataclass
class EnhancedTechnicalAnalysis:
    """增強版完整技術分析結果"""
    stock_id: str
    stock_name: str
    analysis_date: str
    current_price: float
    indicators: Dict[str, EnhancedTechnicalIndicator]
    overall_score: float  # 總評分
    confidence_score: float
    effective_indicators: List[str]  # 有效指標 (信心度 > 60%)
    summary: str

class EnhancedTechnicalAnalyzer:
    """增強版技術分析計算器"""
    
    def __init__(self):
        self._finlab_logged_in = False
        
        # 立即登入 Finlab
        import os
        finlab_key = os.getenv('FINLAB_API_KEY')
        if finlab_key:
            try:
                finlab.login(finlab_key)
                self._finlab_logged_in = True
                logger.info("增強版技術分析器：Finlab API 登入成功")
            except Exception as e:
                logger.warning(f"增強版技術分析器：Finlab API 登入失敗 - {e}")
        
        self.cache_manager = OHLCCacheManager()
        
        # 定義各週期參數
        self.ma_periods = {
            "周線": 5,
            "月線": 20,
            "季線": 60,
            "半年線": 120,
            "年線": 240
        }
        
        self.volatility_periods = {
            "短期": 5,
            "中期": 20,
            "長期": 60
        }
        
        logger.info("增強版技術分析計算器初始化完成")
    
    def _ensure_finlab_login(self):
        """確保 Finlab 已登入"""
        if not self._finlab_logged_in:
            try:
                # 檢查是否已經登入
                test_data = finlab.data.get('price:收盤價', start=datetime.now() - timedelta(days=1))
                self._finlab_logged_in = True
                logger.info("Finlab API 已登入")
            except Exception as e:
                logger.warning(f"Finlab 登入檢查失敗: {e}")
    
    def _check_data_availability(self, stock_id: str) -> Dict[str, bool]:
        """檢查股票數據可用性"""
        
        availability = {
            'price_data': False,
            'volume_data': False,
            'sufficient_history': False,
            'monthly_revenue': False
        }
        
        try:
            # 檢查是否為ETF或特殊股票類型
            etf_codes = ['0050', '0056', '00878', '00919', '00940', '006208']
            is_etf = stock_id in etf_codes
            
            # 簡單數據檢查
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # 只檢查近30天
            
            logger.info(f"🔍 檢查 {stock_id} 數據可用性...")
            
            # 檢查價格數據
            try:
                # 使用不帶時間參數的版本，避免驗證碼問題
                close_data = finlab.data.get('price:收盤價')
                if stock_id in close_data.columns and not close_data[stock_id].isna().all():
                    availability['price_data'] = True
                    
                    # 檢查歷史數據充足性（簡化檢查，只看總數據量）
                    stock_data = close_data[stock_id].dropna()
                    if len(stock_data) >= 200:  # 至少200個交易日
                        availability['sufficient_history'] = True
            except Exception as e:
                logger.warning(f"價格數據檢查失敗: {e}")
            
            # 檢查成交量數據
            try:
                # 使用不帶時間參數的版本，避免驗證碼問題
                volume_data = finlab.data.get('price:成交股數')
                if stock_id in volume_data.columns and not volume_data[stock_id].isna().all():
                    availability['volume_data'] = True
            except Exception as e:
                logger.warning(f"成交量數據檢查失敗: {e}")
            
            # 檢查月營收數據（ETF通常沒有）
            if not is_etf:
                try:
                    # 假設有月營收數據檢查的API
                    # revenue_data = finlab.data.get('monthly_revenue', start_date, end_date)
                    # if stock_id in revenue_data.columns:
                    #     availability['monthly_revenue'] = True
                    
                    # 暫時對非ETF假設有月營收
                    availability['monthly_revenue'] = True
                except:
                    pass
            
            return availability
            
        except Exception as e:
            logger.error(f"數據可用性檢查失敗: {e}")
            return availability

    async def get_enhanced_stock_analysis(self, stock_id: str, stock_name: str = "", days: int = 300) -> Optional[EnhancedTechnicalAnalysis]:
        """獲取增強版股票技術分析"""
        
        try:
            # 檢查是否已登入 Finlab
            if not self._finlab_logged_in:
                logger.warning(f"Finlab 未登入，跳過 {stock_id} 的技術分析")
                return None
            
            # 步驟 1: 檢查數據可用性
            availability = self._check_data_availability(stock_id)
            
            if not availability['price_data']:
                logger.warning(f"❌ {stock_id} 無價格數據，跳過分析")
                return None
                
            if not availability['sufficient_history']:
                logger.warning(f"⚠️ {stock_id} 歷史數據不足（<200天），技術分析可能不準確")
            
            if not availability['volume_data']:
                logger.warning(f"⚠️ {stock_id} 無成交量數據，部分指標將無法計算")
            
            logger.info(f"✅ {stock_id} 數據檢查通過，開始技術分析")
            
            logger.info(f"📊 計算 {stock_name}({stock_id}) 增強版技術指標...")
            
            # 使用緩存管理器獲取 OHLC 數據
            df = self.cache_manager.get_stock_ohlc(stock_id, days)
            
            if df is None or len(df) == 0:
                logger.error(f"無法獲取股票 {stock_id} 的 OHLC 數據")
                return None
            
            # 清理數據
            df = df.dropna()
            
            if len(df) < 60:
                logger.error(f"數據不足: {len(df)} 筆，需要至少 60 筆")
                return None
            
            current_price = float(df['close'].iloc[-1])
            
            # 計算各技術指標
            indicators = {}
            
            # 1. 增強版均線分析
            ma_indicator = self._calculate_enhanced_ma(df)
            if ma_indicator:
                indicators['moving_averages'] = ma_indicator
            
            # 2. 增強版 MACD 分析
            macd_indicator = self._calculate_enhanced_macd(df)
            if macd_indicator:
                indicators['macd'] = macd_indicator
            
            # 3. 增強版 KD 分析
            kd_indicator = self._calculate_enhanced_kd(df)
            if kd_indicator:
                indicators['kd'] = kd_indicator
            
            # 4. 增強版 RSI 分析
            rsi_indicator = self._calculate_enhanced_rsi(df)
            if rsi_indicator:
                indicators['rsi'] = rsi_indicator
            
            # 5. 增強版布林通道分析
            bb_indicator = self._calculate_enhanced_bollinger(df)
            if bb_indicator:
                indicators['bollinger_bands'] = bb_indicator
            
            # 6. 增強版波動率分析
            vol_indicator = self._calculate_enhanced_volatility(df)
            if vol_indicator:
                indicators['volatility'] = vol_indicator
            
            # 7. 增強版成交量分析
            volume_indicator = self._calculate_enhanced_volume(df)
            if volume_indicator:
                indicators['volume'] = volume_indicator
            
            # 計算整體評分和有效指標
            overall_score, confidence, effective_indicators = self._calculate_overall_assessment(indicators)
            
            # 生成摘要
            summary = self._generate_enhanced_summary(indicators, effective_indicators, overall_score)
            
            logger.info(f"✅ 完成 {stock_name}({stock_id}) 增強版技術分析")
            logger.info(f"  📈 綜合評分: {overall_score:.1f}/10 (信心度: {confidence:.1f}%)")
            logger.info(f"  📊 有效指標: {len(effective_indicators)} 個")
            
            return EnhancedTechnicalAnalysis(
                stock_id=stock_id,
                stock_name=stock_name or stock_id,
                analysis_date=datetime.now().strftime("%Y-%m-%d"),
                current_price=current_price,
                indicators=indicators,
                overall_score=overall_score,
                confidence_score=confidence,
                effective_indicators=effective_indicators,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"增強版技術分析失敗: {e}")
            return None
    
    def _calculate_enhanced_ma(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版均線分析"""
        try:
            current_price = df['close'].iloc[-1]
            periods_analysis = {}
            key_insights = []
            total_score = 0
            valid_periods = 0
            
            # 計算各週期均線
            for period_name, period_days in self.ma_periods.items():
                if len(df) >= period_days:
                    ma = df['close'].rolling(window=period_days).mean()
                    current_ma = ma.iloc[-1]
                    prev_ma = ma.iloc[-2] if len(ma) >= 2 else current_ma
                    
                    # 計算偏離度
                    deviation = (current_price - current_ma) / current_ma * 100
                    trend = "上升" if current_ma > prev_ma else "下降" if current_ma < prev_ma else "持平"
                    
                    # 評分邏輯 - 調整為更寬鬆的標準
                    score = 0
                    if current_price > current_ma:
                        if deviation > 3:  # 降低強勢突破門檻: 5% -> 3%
                            score = 2  # 強勢突破
                            key_insights.append(f"{period_name}強勢突破({deviation:.1f}%)")
                        elif deviation > 1:  # 降低溫和突破門檻: 2% -> 1%
                            score = 1.5  # 提高溫和突破分數
                        else:
                            score = 1  # 提高微幅突破分數: 0.5 -> 1
                    elif current_price < current_ma:
                        if deviation < -3:  # 降低重跌破門檻: -5% -> -3%
                            score = -2  # 重跌破支撐
                            key_insights.append(f"{period_name}重跌破支撐({deviation:.1f}%)")
                        elif deviation < -1:  # 降低跌破門檻: -2% -> -1%
                            score = -1.5  # 提高跌破分數
                        else:
                            score = -1  # 提高微跌破分數: -0.5 -> -1
                    
                    periods_analysis[period_name] = {
                        "ma_value": current_ma,
                        "deviation": deviation,
                        "trend": trend,
                        "score": score,
                        "status": "突破" if current_price > current_ma else "跌破" if current_price < current_ma else "持平"
                    }
                    
                    total_score += score
                    valid_periods += 1
            
            if valid_periods == 0:
                return None
            
            # 計算均線排列
            ma_values = [data["ma_value"] for data in periods_analysis.values()]
            if len(ma_values) >= 3:
                bullish_alignment = all(ma_values[i] <= ma_values[i+1] for i in range(len(ma_values)-1))
                bearish_alignment = all(ma_values[i] >= ma_values[i+1] for i in range(len(ma_values)-1))
                
                if bullish_alignment:
                    total_score += 2
                    key_insights.append("多頭排列確立")
                elif bearish_alignment:
                    total_score -= 2
                    key_insights.append("空頭排列確立")
            
            # 計算信心度和信號 - 調整為更合理的計算方式
            max_score = valid_periods * 2 + 2  # 每個週期最多2分 + 排列2分
            # 基礎信心度提高，並降低達到高信心度的門檻
            base_confidence = 30  # 基礎信心度 30%
            score_confidence = min(abs(total_score) / max_score * 70, 70)  # 評分貢獻最多70%
            confidence = min(base_confidence + score_confidence, 100)
            
            if total_score >= 2:
                signal = "bullish"
                strength = "strong" if confidence > 70 else "moderate"
            elif total_score <= -2:
                signal = "bearish"
                strength = "strong" if confidence > 70 else "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"均線分析: {', '.join(key_insights[:3]) if key_insights else '均線呈現震盪格局'}"
            
            return EnhancedTechnicalIndicator(
                name="moving_averages",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版均線計算失敗: {e}")
            return None
    
    def _calculate_enhanced_macd(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版 MACD 分析"""
        try:
            periods_analysis = {}
            key_insights = []
            total_score = 0
            
            # 1. 標準 MACD (12, 26, 9)
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            current_macd = histogram.iloc[-1]
            prev_macd = histogram.iloc[-2] if len(histogram) >= 2 else 0
            
            # 短期評分 - 更寬鬆的評分標準
            short_score = 0
            if current_macd > 0:
                if current_macd > prev_macd:
                    short_score = 2
                    key_insights.append("短期MACD柱狀圖轉強")
                else:
                    short_score = 1  # 即使略微減弱但仍為正值，給予部分分數
            elif current_macd < 0:
                if current_macd < prev_macd:
                    short_score = -2
                    key_insights.append("短期MACD柱狀圖轉弱")
                else:
                    short_score = -1  # 即使略微好轉但仍為負值，給予部分負分
            
            # 如果接近零軸，也給予適當評分
            if abs(current_macd) < 0.01:  # 接近零軸
                if current_macd > prev_macd:
                    short_score = max(short_score, 0.5)  # 向上趨勢
                else:
                    short_score = min(short_score, -0.5)  # 向下趨勢
            
            periods_analysis["短期MACD"] = {
                "macd_value": current_macd,
                "signal_value": signal_line.iloc[-1],
                "score": short_score,
                "trend": "多頭" if current_macd > 0 else "空頭"
            }
            total_score += short_score
            
            # 2. 中期 MACD (26, 52, 18)
            if len(df) >= 52:
                ema26_mid = df['close'].ewm(span=26).mean()
                ema52_mid = df['close'].ewm(span=52).mean()
                macd_mid = ema26_mid - ema52_mid
                signal_mid = macd_mid.ewm(span=18).mean()
                
                mid_score = 0
                macd_current = macd_mid.iloc[-1]
                signal_current = signal_mid.iloc[-1]
                macd_diff = macd_current - signal_current
                
                if macd_diff > 0:
                    mid_score = 1.5 if abs(macd_diff) > 0.5 else 1  # 強弱程度不同給分
                elif macd_diff < 0:
                    mid_score = -1.5 if abs(macd_diff) > 0.5 else -1
                
                periods_analysis["中期MACD"] = {
                    "macd_value": macd_mid.iloc[-1],
                    "signal_value": signal_mid.iloc[-1],
                    "score": mid_score,
                    "trend": "多頭" if mid_score > 0 else "空頭" if mid_score < 0 else "中性"
                }
                total_score += mid_score
            
            # 3. 長期 MACD (50, 100, 30) 
            if len(df) >= 100:
                ema50_long = df['close'].ewm(span=50).mean()
                ema100_long = df['close'].ewm(span=100).mean()
                macd_long = ema50_long - ema100_long
                signal_long = macd_long.ewm(span=30).mean()
                
                long_score = 0
                if macd_long.iloc[-1] > signal_long.iloc[-1]:
                    long_score = 1
                    key_insights.append("長期MACD偏多")
                elif macd_long.iloc[-1] < signal_long.iloc[-1]:
                    long_score = -1
                    key_insights.append("長期MACD偏空")
                
                periods_analysis["長期MACD"] = {
                    "macd_value": macd_long.iloc[-1],
                    "signal_value": signal_long.iloc[-1], 
                    "score": long_score,
                    "trend": "多頭" if long_score > 0 else "空頭" if long_score < 0 else "中性"
                }
                total_score += long_score
            
            # 4. 黃金/死亡交叉檢測
            macd_curr = macd_line.iloc[-1]
            signal_curr = signal_line.iloc[-1]
            macd_prev = macd_line.iloc[-2] if len(macd_line) >= 2 else 0
            signal_prev = signal_line.iloc[-2] if len(signal_line) >= 2 else 0
            
            if macd_prev <= signal_prev and macd_curr > signal_curr:
                total_score += 3
                key_insights.append("MACD黃金交叉出現")
            elif macd_prev >= signal_prev and macd_curr < signal_curr:
                total_score -= 3
                key_insights.append("MACD死亡交叉出現")
            
            # 計算信心度 - 加入基礎信心度
            max_score = 7  # 短期2 + 中期1 + 長期1 + 交叉3
            base_confidence = 25  # MACD 基礎信心度
            score_confidence = min(abs(total_score) / max_score * 75, 75)
            confidence = min(base_confidence + score_confidence, 100)
            
            # 判斷信號
            if total_score >= 2:
                signal = "bullish"
                strength = "strong" if confidence > 70 else "moderate"
            elif total_score <= -2:
                signal = "bearish"
                strength = "strong" if confidence > 70 else "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"MACD分析: {'; '.join(key_insights[:3]) if key_insights else 'MACD呈現震盪格局'}"
            
            return EnhancedTechnicalIndicator(
                name="macd",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版MACD計算失敗: {e}")
            return None
    
    def _calculate_enhanced_kd(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版 KD 分析"""
        try:
            periods_analysis = {}
            key_insights = []
            total_score = 0
            
            # 計算不同週期的 KD
            kd_periods = {"短期": 9, "中期": 14, "長期": 21}
            
            for period_name, k_period in kd_periods.items():
                if len(df) >= k_period + 3:
                    # 計算 RSV
                    low_min = df['low'].rolling(window=k_period).min()
                    high_max = df['high'].rolling(window=k_period).max()
                    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
                    
                    # 計算 K 和 D
                    k_value = rsv.ewm(com=2).mean()
                    d_value = k_value.ewm(com=2).mean()
                    
                    current_k = k_value.iloc[-1]
                    current_d = d_value.iloc[-1]
                    prev_k = k_value.iloc[-2] if len(k_value) >= 2 else current_k
                    prev_d = d_value.iloc[-2] if len(d_value) >= 2 else current_d
                    
                    # 評分邏輯
                    score = 0
                    status = ""
                    
                    # 超買超賣判斷
                    if current_k > 80 and current_d > 80:
                        score = -1
                        status = "超買"
                        if period_name == "短期":
                            key_insights.append(f"{period_name}KD超買({current_k:.1f})")
                    elif current_k < 20 and current_d < 20:
                        score = 1
                        status = "超賣"
                        if period_name == "短期":
                            key_insights.append(f"{period_name}KD超賣({current_k:.1f})")
                    
                    # 黃金/死亡交叉
                    if prev_k <= prev_d and current_k > current_d and current_k < 80:
                        score += 2
                        status += "黃金交叉"
                        key_insights.append(f"{period_name}KD黃金交叉")
                    elif prev_k >= prev_d and current_k < current_d and current_k > 20:
                        score -= 2
                        status += "死亡交叉"
                        key_insights.append(f"{period_name}KD死亡交叉")
                    
                    periods_analysis[period_name] = {
                        "k_value": current_k,
                        "d_value": current_d,
                        "score": score,
                        "status": status or "正常",
                        "zone": "超買" if current_k > 80 else "超賣" if current_k < 20 else "正常"
                    }
                    
                    total_score += score
            
            # 計算信心度
            max_score = len(periods_analysis) * 2
            confidence = min(abs(total_score) / max_score * 100, 100) if max_score > 0 else 0
            
            # 判斷信號
            if total_score >= 2:
                signal = "bullish"
                strength = "strong" if confidence > 70 else "moderate"
            elif total_score <= -2:
                signal = "bearish"
                strength = "strong" if confidence > 70 else "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"KD分析: {'; '.join(key_insights[:3]) if key_insights else 'KD指標呈現震盪'}"
            
            return EnhancedTechnicalIndicator(
                name="kd",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版KD計算失敗: {e}")
            return None
    
    def _calculate_enhanced_rsi(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版 RSI 分析"""
        try:
            periods_analysis = {}
            key_insights = []
            total_score = 0
            
            # 計算不同週期的 RSI
            rsi_periods = {"短期": 6, "中期": 14, "長期": 21}
            
            for period_name, period_days in rsi_periods.items():
                if len(df) >= period_days + 1:
                    # 計算價格變化
                    price_change = df['close'].diff()
                    gain = price_change.where(price_change > 0, 0)
                    loss = -price_change.where(price_change < 0, 0)
                    
                    # 計算平均漲跌幅
                    avg_gain = gain.rolling(window=period_days).mean()
                    avg_loss = loss.rolling(window=period_days).mean()
                    
                    # 計算 RSI
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    
                    current_rsi = rsi.iloc[-1]
                    prev_rsi = rsi.iloc[-2] if len(rsi) >= 2 else current_rsi
                    
                    # 評分邏輯
                    score = 0
                    status = ""
                    
                    # 超買超賣
                    if current_rsi > 70:
                        score = -1
                        status = "超買"
                        if current_rsi > 80:
                            score = -2
                            key_insights.append(f"{period_name}RSI嚴重超買({current_rsi:.1f})")
                    elif current_rsi < 30:
                        score = 1
                        status = "超賣"
                        if current_rsi < 20:
                            score = 2
                            key_insights.append(f"{period_name}RSI嚴重超賣({current_rsi:.1f})")
                    
                    # 趨勢強度
                    if 50 < current_rsi < 70 and current_rsi > prev_rsi:
                        score += 1
                        status += "強勢"
                    elif 30 < current_rsi < 50 and current_rsi < prev_rsi:
                        score -= 1
                        status += "弱勢"
                    
                    periods_analysis[period_name] = {
                        "rsi_value": current_rsi,
                        "score": score,
                        "status": status or "正常",
                        "zone": "超買" if current_rsi > 70 else "超賣" if current_rsi < 30 else "正常",
                        "trend": "上升" if current_rsi > prev_rsi else "下降"
                    }
                    
                    total_score += score
            
            # 計算信心度 - RSI指標加入基礎信心度
            max_score = len(periods_analysis) * 2
            base_confidence = 20  # RSI 基礎信心度
            score_confidence = min(abs(total_score) / max_score * 80, 80) if max_score > 0 else 0
            confidence = min(base_confidence + score_confidence, 100)
            
            # 判斷信號
            if total_score >= 2:
                signal = "bullish"
                strength = "strong" if confidence > 70 else "moderate"
            elif total_score <= -2:
                signal = "bearish"
                strength = "strong" if confidence > 70 else "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"RSI分析: {'; '.join(key_insights[:3]) if key_insights else 'RSI指標呈現正常波動'}"
            
            return EnhancedTechnicalIndicator(
                name="rsi",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版RSI計算失敗: {e}")
            return None
    
    def _calculate_enhanced_bollinger(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版布林通道分析"""
        try:
            periods_analysis = {}
            key_insights = []
            total_score = 0
            
            # 計算不同週期的布林通道
            bb_periods = {"短期": 10, "中期": 20, "長期": 50}
            
            for period_name, period_days in bb_periods.items():
                if len(df) >= period_days:
                    # 計算布林通道
                    sma = df['close'].rolling(window=period_days).mean()
                    std = df['close'].rolling(window=period_days).std()
                    upper_band = sma + (std * 2)
                    lower_band = sma - (std * 2)
                    
                    current_price = df['close'].iloc[-1]
                    current_upper = upper_band.iloc[-1]
                    current_lower = lower_band.iloc[-1]
                    current_middle = sma.iloc[-1]
                    
                    # 計算位置百分比
                    bb_percent = (current_price - current_lower) / (current_upper - current_lower) * 100
                    
                    # 評分邏輯
                    score = 0
                    status = ""
                    
                    if current_price > current_upper:
                        score = 2
                        status = "突破上軌"
                        key_insights.append(f"{period_name}布林突破上軌")
                    elif current_price < current_lower:
                        score = -2
                        status = "跌破下軌"
                        key_insights.append(f"{period_name}布林跌破下軌")
                    elif bb_percent > 80:
                        score = 1
                        status = "接近上軌"
                    elif bb_percent < 20:
                        score = -1
                        status = "接近下軌"
                    elif 40 <= bb_percent <= 60:
                        score = 0
                        status = "中軌震盪"
                    
                    # 通道寬度分析
                    channel_width = (current_upper - current_lower) / current_middle * 100
                    if channel_width > 15:
                        if status in ["突破上軌", "接近上軌"]:
                            score += 1  # 寬幅通道突破更有意義
                    
                    periods_analysis[period_name] = {
                        "upper_band": current_upper,
                        "middle_band": current_middle,
                        "lower_band": current_lower,
                        "bb_percent": bb_percent,
                        "channel_width": channel_width,
                        "score": score,
                        "status": status
                    }
                    
                    total_score += score
            
            # 計算信心度 - 布林通道加入基礎信心度
            max_score = len(periods_analysis) * 3  # 每個週期最多3分(2基本分+1寬度分)
            base_confidence = 20  # 布林通道基礎信心度
            score_confidence = min(abs(total_score) / max_score * 80, 80) if max_score > 0 else 0
            confidence = min(base_confidence + score_confidence, 100)
            
            # 判斷信號
            if total_score >= 3:
                signal = "bullish"
                strength = "strong" if confidence > 70 else "moderate"
            elif total_score <= -3:
                signal = "bearish"
                strength = "strong" if confidence > 70 else "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"布林通道分析: {'; '.join(key_insights[:3]) if key_insights else '價格在布林通道內震盪'}"
            
            return EnhancedTechnicalIndicator(
                name="bollinger_bands",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版布林通道計算失敗: {e}")
            return None
    
    def _calculate_enhanced_volatility(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版波動率分析"""
        try:
            periods_analysis = {}
            key_insights = []
            total_score = 0
            
            # 計算不同週期的波動率 - 改進波動比較邏輯
            for period_name, period_days in self.volatility_periods.items():
                if len(df) >= period_days + 30:  # 確保有足夠歷史數據比較
                    # 計算歷史波動率
                    returns = df['close'].pct_change()
                    volatility = returns.rolling(window=period_days).std() * np.sqrt(252) * 100
                    
                    current_vol = volatility.iloc[-1]
                    
                    # 改進：使用不同歷史期間比較
                    if period_name == "短期":
                        # 短期波動與過去30日平均比較
                        hist_period = 30
                    elif period_name == "中期":
                        # 中期波動與過去60日平均比較
                        hist_period = 60
                    else:
                        # 長期波動與過去120日平均比較
                        hist_period = 120
                    
                    if len(volatility) >= hist_period:
                        # 計算歷史平均波動和百分位數
                        hist_vol = volatility.iloc[-(hist_period+1):-1]  # 排除當前值
                        avg_vol = hist_vol.mean()
                        vol_75th = hist_vol.quantile(0.75)  # 75百分位
                        vol_25th = hist_vol.quantile(0.25)  # 25百分位
                        
                        # 改進評分邏輯 - 基於歷史分布
                        score = 0
                        status = ""
                        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
                        
                        if current_vol > vol_75th:
                            if vol_ratio > 1.5:
                                score = 2  # 極高波動
                                status = "極高波動"
                                key_insights.append(f"{period_name}波動率創新高({current_vol:.1f}% vs {avg_vol:.1f}%)")
                            else:
                                score = 1  # 高波動
                                status = "高波動"
                        elif current_vol < vol_25th:
                            if vol_ratio < 0.6:
                                score = -1  # 極低波動
                                status = "極低波動"
                                key_insights.append(f"{period_name}波動率創新低({current_vol:.1f}% vs {avg_vol:.1f}%)")
                            else:
                                score = 0  # 低波動但不極端
                                status = "低波動"
                        else:
                            # 在正常範圍內，根據趨勢給分
                            if vol_ratio > 1.1:
                                score = 0.5  # 波動上升
                                status = "波動上升"
                            elif vol_ratio < 0.9:
                                score = -0.5  # 波動下降
                                status = "波動下降"
                            else:
                                score = 0
                                status = "正常波動"
                    else:
                        # 數據不足，使用簡單邏輯
                        score = 0
                        status = "數據不足"
                        vol_ratio = 1
                    
                    periods_analysis[period_name] = {
                        "volatility": current_vol,
                        "avg_volatility": avg_vol,
                        "vol_ratio": vol_ratio,
                        "score": score,
                        "status": status
                    }
                    
                    total_score += score
            
            # 計算信心度 - 波動率分析加入基礎信心度
            max_score = len(periods_analysis) * 2  # 更新最大分數，因為現在可能有±2分
            base_confidence = 15  # 波動率基礎信心度
            score_confidence = min(abs(total_score) / max_score * 85, 85) if max_score > 0 else 0
            confidence = min(base_confidence + score_confidence, 100)
            
            # 判斷信號
            if total_score >= 2:
                signal = "bullish"  # 高波動期待突破
                strength = "moderate"
            elif total_score <= -2:
                signal = "bearish"  # 低波動缺乏動能
                strength = "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"波動率分析: {'; '.join(key_insights[:3]) if key_insights else '波動率處於正常水平'}"
            
            return EnhancedTechnicalIndicator(
                name="volatility",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版波動率計算失敗: {e}")
            return None
    
    def _calculate_enhanced_volume(self, df: pd.DataFrame) -> Optional[EnhancedTechnicalIndicator]:
        """計算增強版成交量分析"""
        try:
            periods_analysis = {}
            key_insights = []
            total_score = 0
            
            # 計算不同週期的成交量分析
            volume_periods = {"短期": 5, "中期": 20, "長期": 60}
            
            current_volume = df['volume'].iloc[-1]
            
            for period_name, period_days in volume_periods.items():
                if len(df) >= period_days:
                    avg_volume = df['volume'].rolling(window=period_days).mean().iloc[-1]
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                    
                    # 價量配合分析
                    price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100
                    
                    # 評分邏輯
                    score = 0
                    status = ""
                    
                    if volume_ratio > 2:
                        if price_change > 2:
                            score = 2
                            status = "爆量上漲"
                            key_insights.append(f"爆量上漲(量比{volume_ratio:.1f})")
                        elif price_change < -2:
                            score = -2
                            status = "爆量下跌"
                            key_insights.append(f"爆量下跌(量比{volume_ratio:.1f})")
                        else:
                            score = 1
                            status = "高量整理"
                    elif volume_ratio > 1.5:
                        if price_change > 1:
                            score = 1
                            status = "放量上漲"
                        elif price_change < -1:
                            score = -1
                            status = "放量下跌"
                    else:
                        score = 0
                        status = "量能正常"
                    
                    periods_analysis[period_name] = {
                        "current_volume": current_volume,
                        "avg_volume": avg_volume,
                        "volume_ratio": volume_ratio,
                        "price_change": price_change,
                        "score": score,
                        "status": status
                    }
                    
                    # 只取短期評分避免重複計分
                    if period_name == "短期":
                        total_score += score
            
            # 計算信心度 - 量價分析加入基礎信心度
            base_confidence = 25  # 量價分析基礎信心度
            score_confidence = min(abs(total_score) / 2 * 75, 75)
            confidence = min(base_confidence + score_confidence, 100)
            
            # 判斷信號
            if total_score >= 1:
                signal = "bullish"
                strength = "strong" if confidence > 70 else "moderate"
            elif total_score <= -1:
                signal = "bearish"
                strength = "strong" if confidence > 70 else "moderate"
            else:
                signal = "neutral"
                strength = "weak"
            
            description = f"成交量分析: {'; '.join(key_insights[:3]) if key_insights else '成交量表現正常'}"
            
            return EnhancedTechnicalIndicator(
                name="volume",
                overall_score=total_score,
                confidence=confidence,
                signal=signal,
                strength=strength,
                periods_analysis=periods_analysis,
                key_insights=key_insights,
                description=description
            )
            
        except Exception as e:
            logger.error(f"增強版成交量計算失敗: {e}")
            return None
    
    def _calculate_overall_assessment(self, indicators: Dict[str, EnhancedTechnicalIndicator]) -> Tuple[float, float, List[str]]:
        """計算整體評估和有效指標"""
        
        total_weighted_score = 0
        total_weight = 0
        effective_indicators = []
        
        # 指標權重設定
        weights = {
            "moving_averages": 0.25,    # 均線 25%
            "macd": 0.20,              # MACD 20%
            "kd": 0.15,                # KD 15%
            "rsi": 0.15,               # RSI 15%
            "bollinger_bands": 0.15,   # 布林通道 15%
            "volume": 0.10,            # 成交量 10%
            "volatility": 0.05         # 波動率 5%  (參考用)
        }
        
        for indicator_name, indicator in indicators.items():
            weight = weights.get(indicator_name, 0.1)
            
            # 只有信心度 > 15% 的指標才納入計算 (進一步降低門檻)
            if indicator.confidence >= 15:
                effective_indicators.append(indicator_name)
                total_weighted_score += indicator.overall_score * weight * (indicator.confidence / 100)
                total_weight += weight
        
        # 計算加權平均分數 (轉換為0-10分制)
        if total_weight > 0:
            # 原本是 -5到+5 的範圍，轉換為 0到10
            # -5分 = 極度看空 → 0分，0分 = 中性 → 5分，+5分 = 極度看多 → 10分
            raw_score = total_weighted_score / total_weight
            overall_score = raw_score + 5  # 轉為0到10分制
            overall_score = max(0, min(10, overall_score))  # 限制範圍
        else:
            overall_score = 5  # 中性分數
        
        # 計算整體信心度
        if indicators:
            confidence = sum(ind.confidence for ind in indicators.values()) / len(indicators)
        else:
            confidence = 0
        
        return overall_score, confidence, effective_indicators
    
    def _generate_enhanced_summary(self, indicators: Dict[str, EnhancedTechnicalIndicator], 
                                  effective_indicators: List[str], overall_score: float) -> str:
        """生成增強版摘要"""
        
        if not effective_indicators:
            return "技術指標信心度不足，建議觀望"
        
        # 收集關鍵洞察
        all_insights = []
        for indicator_name in effective_indicators:
            if indicator_name in indicators:
                all_insights.extend(indicators[indicator_name].key_insights)
        
        # 判斷整體趨勢 (0-10分制)
        if overall_score >= 7:
            trend = "強勢看多"
        elif overall_score >= 6:
            trend = "溫和看多"
        elif overall_score <= 3:
            trend = "強勢看空"
        elif overall_score <= 4:
            trend = "溫和看空"
        else:
            trend = "震盪整理"  # 5分 = 中性
        
        # 組合摘要
        summary_parts = [f"技術面呈現{trend}格局"]
        
        if all_insights:
            key_points = "; ".join(all_insights[:3])
            summary_parts.append(key_points)
        
        summary_parts.append(f"有效指標數: {len(effective_indicators)}")
        
        return "。".join(summary_parts)

def create_enhanced_technical_analyzer() -> EnhancedTechnicalAnalyzer:
    """創建增強版技術分析器實例"""
    return EnhancedTechnicalAnalyzer()
