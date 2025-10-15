#!/usr/bin/env python3
"""
漲停家數分析工具
分析過去一年台股每日漲停家數（9.5%以上視為漲停）
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import finlab
from finlab import data
import logging
from typing import Dict, List, Tuple, Optional
import json

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LimitUpAnalyzer:
    """漲停家數分析器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化分析器
        
        Args:
            api_key: FinLab API 金鑰，如果為 None 則從環境變數讀取
        """
        self.api_key = api_key or os.getenv("FINLAB_API_KEY")
        if not self.api_key:
            raise ValueError("請設定 FINLAB_API_KEY 環境變數或傳入 api_key 參數")
        
        # 登入 FinLab
        self._login_finlab()
        
        # 漲停閾值（9.5%以上視為漲停）
        self.limit_up_threshold = 9.5
        
    def _login_finlab(self):
        """登入 FinLab API"""
        try:
            finlab.login(self.api_key)
            logger.info("✅ FinLab API 登入成功")
        except Exception as e:
            logger.error(f"❌ FinLab API 登入失敗: {e}")
            raise
    
    def get_stock_list(self) -> List[str]:
        """
        獲取所有股票代號列表
        
        Returns:
            List[str]: 股票代號列表
        """
        try:
            # 獲取收盤價數據，從中提取股票代號
            close_data = data.get('price:收盤價')
            stock_list = close_data.columns.tolist()
            logger.info(f"📊 獲取到 {len(stock_list)} 檔股票")
            return stock_list
        except Exception as e:
            logger.error(f"❌ 獲取股票列表失敗: {e}")
            return []
    
    def get_daily_price_data(self, date: str) -> Optional[pd.DataFrame]:
        """
        獲取指定日期的所有股票價格數據
        
        Args:
            date: 日期字串 (YYYY-MM-DD)
            
        Returns:
            Optional[pd.DataFrame]: 包含開盤價、收盤價、漲跌幅的 DataFrame
        """
        try:
            # 獲取各種價格數據
            open_data = data.get('price:開盤價')
            close_data = data.get('price:收盤價')
            
            # 轉換日期格式
            target_date = pd.to_datetime(date)
            
            # 檢查日期是否存在於數據中
            if target_date not in close_data.index:
                logger.warning(f"⚠️ 日期 {date} 不在數據範圍內")
                return None
            
            # 獲取該日期的數據
            daily_open = open_data.loc[target_date]
            daily_close = close_data.loc[target_date]
            
            # 計算漲跌幅
            daily_change_pct = ((daily_close - daily_open) / daily_open * 100).fillna(0)
            
            # 組合數據
            daily_data = pd.DataFrame({
                'stock_id': daily_close.index,
                'open': daily_open.values,
                'close': daily_close.values,
                'change_pct': daily_change_pct.values
            })
            
            # 移除無效數據
            daily_data = daily_data.dropna()
            
            logger.info(f"📊 獲取 {date} 的價格數據: {len(daily_data)} 檔股票")
            return daily_data
            
        except Exception as e:
            logger.error(f"❌ 獲取 {date} 價格數據失敗: {e}")
            return None
    
    def count_limit_up_stocks(self, daily_data: pd.DataFrame) -> int:
        """
        計算漲停家數
        
        Args:
            daily_data: 每日價格數據
            
        Returns:
            int: 漲停家數
        """
        if daily_data is None or len(daily_data) == 0:
            return 0
        
        # 計算漲停家數（9.5%以上視為漲停）
        limit_up_count = len(daily_data[daily_data['change_pct'] >= self.limit_up_threshold])
        
        return limit_up_count
    
    def get_trading_dates(self, start_date: str, end_date: str) -> List[str]:
        """
        獲取交易日日期列表
        
        Args:
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            
        Returns:
            List[str]: 交易日日期列表
        """
        try:
            # 獲取收盤價數據的索引（交易日）
            close_data = data.get('price:收盤價')
            
            # 轉換日期格式
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # 篩選日期範圍內的交易日
            trading_dates = close_data.index[
                (close_data.index >= start_dt) & 
                (close_data.index <= end_dt)
            ]
            
            # 轉換為字串格式
            trading_dates_str = [date.strftime('%Y-%m-%d') for date in trading_dates]
            
            logger.info(f"📅 獲取交易日: {len(trading_dates_str)} 天")
            return trading_dates_str
            
        except Exception as e:
            logger.error(f"❌ 獲取交易日失敗: {e}")
            return []
    
    def analyze_limit_up_trend(self, days: int = 365) -> Dict:
        """
        分析過去指定天數的漲停家數趨勢
        
        Args:
            days: 分析天數，預設 365 天（一年）
            
        Returns:
            Dict: 分析結果
        """
        try:
            logger.info(f"🚀 開始分析過去 {days} 天的漲停家數趨勢")
            
            # 計算日期範圍
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            logger.info(f"📅 分析期間: {start_date_str} 到 {end_date_str}")
            
            # 獲取交易日列表
            trading_dates = self.get_trading_dates(start_date_str, end_date_str)
            
            if not trading_dates:
                logger.error("❌ 無法獲取交易日數據")
                return {}
            
            # 分析每日漲停家數
            daily_limit_up_counts = []
            daily_data_list = []
            
            for i, date in enumerate(trading_dates):
                logger.info(f"📊 分析 {date} ({i+1}/{len(trading_dates)})")
                
                # 獲取當日價格數據
                daily_data = self.get_daily_price_data(date)
                
                if daily_data is not None:
                    # 計算漲停家數
                    limit_up_count = self.count_limit_up_stocks(daily_data)
                    daily_limit_up_counts.append(limit_up_count)
                    
                    # 保存詳細數據
                    daily_data_list.append({
                        'date': date,
                        'limit_up_count': limit_up_count,
                        'total_stocks': len(daily_data),
                        'limit_up_stocks': daily_data[daily_data['change_pct'] >= self.limit_up_threshold]['stock_id'].tolist() if limit_up_count > 0 else []
                    })
                else:
                    # 如果無法獲取數據，記錄為 0
                    daily_limit_up_counts.append(0)
                    daily_data_list.append({
                        'date': date,
                        'limit_up_count': 0,
                        'total_stocks': 0,
                        'limit_up_stocks': []
                    })
            
            # 計算統計數據
            limit_up_array = np.array(daily_limit_up_counts)
            
            analysis_result = {
                'analysis_period': {
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                    'total_days': len(trading_dates)
                },
                'limit_up_threshold': self.limit_up_threshold,
                'daily_limit_up_counts': daily_limit_up_counts,
                'trading_dates': trading_dates,
                'statistics': {
                    'total_limit_up_days': len([x for x in daily_limit_up_counts if x > 0]),
                    'max_limit_up_count': int(np.max(limit_up_array)) if len(limit_up_array) > 0 else 0,
                    'min_limit_up_count': int(np.min(limit_up_array)) if len(limit_up_array) > 0 else 0,
                    'avg_limit_up_count': float(np.mean(limit_up_array)) if len(limit_up_array) > 0 else 0,
                    'median_limit_up_count': float(np.median(limit_up_array)) if len(limit_up_array) > 0 else 0,
                    'std_limit_up_count': float(np.std(limit_up_array)) if len(limit_up_array) > 0 else 0
                },
                'detailed_data': daily_data_list
            }
            
            logger.info(f"✅ 分析完成！")
            logger.info(f"📊 統計結果:")
            logger.info(f"   - 總交易日: {analysis_result['statistics']['total_limit_up_days']}")
            logger.info(f"   - 最大漲停家數: {analysis_result['statistics']['max_limit_up_count']}")
            logger.info(f"   - 平均漲停家數: {analysis_result['statistics']['avg_limit_up_count']:.2f}")
            logger.info(f"   - 中位數漲停家數: {analysis_result['statistics']['median_limit_up_count']:.2f}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 分析失敗: {e}")
            return {}
    
    def save_results(self, analysis_result: Dict, filename: str = None):
        """
        保存分析結果到檔案
        
        Args:
            analysis_result: 分析結果
            filename: 檔案名稱，如果為 None 則自動生成
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"limit_up_analysis_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 分析結果已保存到: {filename}")
            
        except Exception as e:
            logger.error(f"❌ 保存結果失敗: {e}")
    
    def print_summary(self, analysis_result: Dict):
        """
        印出分析摘要
        
        Args:
            analysis_result: 分析結果
        """
        if not analysis_result:
            logger.error("❌ 無分析結果可顯示")
            return
        
        print("\n" + "="*60)
        print("📊 台股漲停家數分析報告")
        print("="*60)
        
        # 基本資訊
        period = analysis_result['analysis_period']
        print(f"📅 分析期間: {period['start_date']} 到 {period['end_date']}")
        print(f"📈 漲停閾值: {analysis_result['limit_up_threshold']}%")
        print(f"📊 總交易日: {period['total_days']} 天")
        
        # 統計數據
        stats = analysis_result['statistics']
        print(f"\n📈 統計數據:")
        print(f"   - 有漲停股票的交易日: {stats['total_limit_up_days']} 天")
        print(f"   - 最大漲停家數: {stats['max_limit_up_count']} 家")
        print(f"   - 最小漲停家數: {stats['min_limit_up_count']} 家")
        print(f"   - 平均漲停家數: {stats['avg_limit_up_count']:.2f} 家")
        print(f"   - 中位數漲停家數: {stats['median_limit_up_count']:.2f} 家")
        print(f"   - 標準差: {stats['std_limit_up_count']:.2f}")
        
        # 漲停家數數列（最近10天）
        daily_counts = analysis_result['daily_limit_up_counts']
        trading_dates = analysis_result['trading_dates']
        
        print(f"\n📊 最近10天漲停家數:")
        for i in range(max(0, len(daily_counts)-10), len(daily_counts)):
            print(f"   {trading_dates[i]}: {daily_counts[i]} 家")
        
        print("="*60)


def main():
    """主函數"""
    try:
        # 創建分析器
        analyzer = LimitUpAnalyzer()
        
        # 分析過去一年的漲停家數
        analysis_result = analyzer.analyze_limit_up_trend(days=365)
        
        if analysis_result:
            # 印出摘要
            analyzer.print_summary(analysis_result)
            
            # 保存結果
            analyzer.save_results(analysis_result)
            
            # 返回漲停家數數列
            daily_counts = analysis_result['daily_limit_up_counts']
            trading_dates = analysis_result['trading_dates']
            
            print(f"\n📈 過去一年交易日漲停家數數列:")
            print(f"日期: {trading_dates}")
            print(f"漲停家數: {daily_counts}")
            
            return daily_counts, trading_dates
        else:
            logger.error("❌ 分析失敗，無法獲取結果")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ 程式執行失敗: {e}")
        return None, None


if __name__ == "__main__":
    # 執行主函數
    limit_up_counts, dates = main()
    
    if limit_up_counts is not None:
        print(f"\n✅ 分析完成！共獲取 {len(limit_up_counts)} 個交易日的漲停家數數據")
    else:
        print("\n❌ 分析失敗，請檢查錯誤訊息")


