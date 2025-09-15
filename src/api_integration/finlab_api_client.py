#!/usr/bin/env python3
"""
Finlab API 客戶端
用於獲取股票數據、營收數據、財報數據
"""

import os
import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """股票數據結構"""
    stock_id: str
    stock_name: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_change: float
    daily_change_pct: float

@dataclass
class RevenueData:
    """月營收數據結構 - 基於 Finlab 資料庫結構"""
    stock_id: str
    stock_name: str
    period: str
    # 當月營收
    current_month_revenue: int
    # 上月營收
    last_month_revenue: int
    # 去年當月營收
    last_year_same_month_revenue: int
    # 上月比較增減(%)
    mom_growth_pct: float
    # 去年同月增減(%)
    yoy_growth_pct: float
    # 當月累計營收
    ytd_revenue: int
    # 去年累計營收
    last_year_ytd_revenue: int
    # 前期比較增減(%)
    ytd_growth_pct: float

@dataclass
class EarningsData:
    """財報數據結構"""
    stock_id: str
    stock_name: str
    period: str
    eps: float
    eps_growth: float
    revenue: float
    revenue_growth: float
    gross_margin: float
    net_margin: float
    net_income: float
    net_income_growth: float

class FinlabAPIClient:
    """Finlab API 客戶端"""
    
    def __init__(self):
        """初始化 Finlab API 客戶端"""
        self.api_key = os.getenv('FINLAB_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 FINLAB_API_KEY 環境變數")
        
        self.base_url = "https://api.finlab.tw"
        self.session = None
        
        logger.info("Finlab API 客戶端初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def get_stock_data(self, stock_id: str, days: int = 30) -> Optional[StockData]:
        """獲取股票數據"""
        try:
            url = f"{self.base_url}/api/v1/stock/{stock_id}/ohlc"
            params = {
                'days': days,
                'api_key': self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and 'data' in data and len(data['data']) > 0:
                        latest_data = data['data'][-1]
                        
                        return StockData(
                            stock_id=stock_id,
                            stock_name=data.get('stock_name', f'股票{stock_id}'),
                            date=latest_data['date'],
                            open=float(latest_data['open']),
                            high=float(latest_data['high']),
                            low=float(latest_data['low']),
                            close=float(latest_data['close']),
                            volume=int(latest_data['volume']),
                            daily_change=float(latest_data.get('change', 0)),
                            daily_change_pct=float(latest_data.get('change_pct', 0))
                        )
                
                logger.warning(f"獲取股票 {stock_id} 數據失敗: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 數據時發生錯誤: {e}")
            return None
    
    async def get_revenue_data(self, stock_id: str) -> Optional[RevenueData]:
        """獲取月營收數據 - 使用 Finlab 資料庫 API"""
        try:
            # 使用 Finlab 資料庫 API 獲取月營收數據
            url = f"{self.base_url}/api/v1/data/monthly_revenue"
            params = {
                'api_key': self.api_key,
                'stock_id': stock_id,
                'latest': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and 'data' in data:
                        monthly_data = data['data']
                        
                        return RevenueData(
                            stock_id=stock_id,
                            stock_name=data.get('stock_name', f'股票{stock_id}'),
                            period=data.get('period', ''),
                            # 當月營收
                            current_month_revenue=int(monthly_data.get('當月營收', 0)),
                            # 上月營收
                            last_month_revenue=int(monthly_data.get('上月營收', 0)),
                            # 去年當月營收
                            last_year_same_month_revenue=int(monthly_data.get('去年當月營收', 0)),
                            # 上月比較增減(%)
                            mom_growth_pct=float(monthly_data.get('上月比較增減(%)', 0)),
                            # 去年同月增減(%)
                            yoy_growth_pct=float(monthly_data.get('去年同月增減(%)', 0)),
                            # 當月累計營收
                            ytd_revenue=int(monthly_data.get('當月累計營收', 0)),
                            # 去年累計營收
                            last_year_ytd_revenue=int(monthly_data.get('去年累計營收', 0)),
                            # 前期比較增減(%)
                            ytd_growth_pct=float(monthly_data.get('前期比較增減(%)', 0))
                        )
                
                logger.warning(f"獲取股票 {stock_id} 月營收數據失敗: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 月營收數據時發生錯誤: {e}")
            return None
    
    async def get_earnings_data(self, stock_id: str) -> Optional[EarningsData]:
        """獲取財報數據"""
        try:
            url = f"{self.base_url}/api/v1/stock/{stock_id}/earnings"
            params = {
                'api_key': self.api_key,
                'latest': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and 'data' in data and len(data['data']) > 0:
                        latest_data = data['data'][-1]
                        
                        return EarningsData(
                            stock_id=stock_id,
                            stock_name=data.get('stock_name', f'股票{stock_id}'),
                            period=latest_data['period'],
                            eps=float(latest_data.get('eps', 0)),
                            eps_growth=float(latest_data.get('eps_growth', 0)),
                            revenue=float(latest_data.get('revenue', 0)),
                            revenue_growth=float(latest_data.get('revenue_growth', 0)),
                            gross_margin=float(latest_data.get('gross_margin', 0)),
                            net_margin=float(latest_data.get('net_margin', 0)),
                            net_income=float(latest_data.get('net_income', 0)),
                            net_income_growth=float(latest_data.get('net_income_growth', 0))
                        )
                
                logger.warning(f"獲取股票 {stock_id} 財報數據失敗: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 財報數據時發生錯誤: {e}")
            return None
    
    async def get_comprehensive_stock_analysis(self, stock_id: str) -> Dict[str, Any]:
        """獲取股票綜合分析數據"""
        try:
            # 並行獲取所有數據
            tasks = [
                self.get_stock_data(stock_id),
                self.get_revenue_data(stock_id),
                self.get_earnings_data(stock_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            stock_data, revenue_data, earnings_data = results
            
            analysis = {
                'stock_id': stock_id,
                'stock_name': '',
                'analysis_time': datetime.now().isoformat(),
                'stock_data': stock_data,
                'revenue_data': revenue_data,
                'earnings_data': earnings_data,
                'data_completeness': 0,
                'analysis_summary': {}
            }
            
            # 計算數據完整性
            data_count = 0
            if stock_data:
                data_count += 1
                analysis['stock_name'] = stock_data.stock_name
            if revenue_data:
                data_count += 1
            if earnings_data:
                data_count += 1
            
            analysis['data_completeness'] = data_count / 3
            
            # 生成分析摘要
            if stock_data:
                analysis['analysis_summary']['price_analysis'] = {
                    'current_price': stock_data.close,
                    'daily_change': stock_data.daily_change_pct,
                    'price_trend': 'up' if stock_data.daily_change > 0 else 'down'
                }
            
            if revenue_data:
                analysis['analysis_summary']['revenue_analysis'] = {
                    'revenue': revenue_data.revenue,
                    'yoy_growth': revenue_data.yoy_growth,
                    'mom_growth': revenue_data.mom_growth,
                    'growth_trend': 'strong' if revenue_data.yoy_growth > 20 else 'moderate' if revenue_data.yoy_growth > 0 else 'weak'
                }
            
            if earnings_data:
                analysis['analysis_summary']['earnings_analysis'] = {
                    'eps': earnings_data.eps,
                    'eps_growth': earnings_data.eps_growth,
                    'gross_margin': earnings_data.gross_margin,
                    'profitability': 'high' if earnings_data.gross_margin > 30 else 'medium' if earnings_data.gross_margin > 15 else 'low'
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 綜合分析時發生錯誤: {e}")
            return {
                'stock_id': stock_id,
                'error': str(e),
                'analysis_time': datetime.now().isoformat()
            }

