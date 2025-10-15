#!/usr/bin/env python3
"""
模擬 Finlab API 客戶端
由於真實的 Finlab API 端點不可用，提供模擬數據
"""

import os
import aiohttp
import asyncio
import logging
import random
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
    """營收數據結構"""
    stock_id: str
    stock_name: str
    period: str
    revenue: float
    yoy_growth: float
    mom_growth: float
    ytd_revenue: float
    ytd_growth: float

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

class MockFinlabAPIClient:
    """模擬 Finlab API 客戶端"""
    
    def __init__(self):
        """初始化模擬 Finlab API 客戶端"""
        self.api_key = os.getenv('FINLAB_API_KEY', 'mock_key')
        self.base_url = "https://api.finlab.tw"
        self.session = None
        
        # 股票名稱對應
        self.stock_names = {
            "6732": "昇佳電子", "4968": "立積", "3491": "昇達科技",
            "6919": "康霈生技", "5314": "世紀鋼", "4108": "懷特",
            "8150": "南茂", "3047": "訊舟", "8033": "雷虎",
            "1256": "鮮活果汁-KY", "8028": "昇陽半導體", "8255": "朋程", "6753": "龍德造船"
        }
        
        logger.info("模擬 Finlab API 客戶端初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def get_stock_data(self, stock_id: str, days: int = 30) -> Optional[StockData]:
        """獲取股票數據（模擬）"""
        try:
            # 模擬延遲
            await asyncio.sleep(0.1)
            
            # 生成模擬數據
            base_price = 50 + random.uniform(20, 100)
            change_pct = random.uniform(-5, 10)
            change = base_price * change_pct / 100
            close_price = base_price + change
            
            return StockData(
                stock_id=stock_id,
                stock_name=self.stock_names.get(stock_id, f'股票{stock_id}'),
                date=datetime.now().strftime('%Y-%m-%d'),
                open=base_price,
                high=close_price * 1.02,
                low=close_price * 0.98,
                close=close_price,
                volume=random.randint(1000000, 5000000),
                daily_change=change,
                daily_change_pct=change_pct
            )
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 數據時發生錯誤: {e}")
            return None
    
    async def get_revenue_data(self, stock_id: str) -> Optional[RevenueData]:
        """獲取營收數據（模擬）"""
        try:
            # 模擬延遲
            await asyncio.sleep(0.1)
            
            # 生成模擬數據
            revenue = random.uniform(500000000, 2000000000)  # 5億到20億
            yoy_growth = random.uniform(-10, 50)  # -10% 到 50%
            mom_growth = random.uniform(-5, 20)   # -5% 到 20%
            
            return RevenueData(
                stock_id=stock_id,
                stock_name=self.stock_names.get(stock_id, f'股票{stock_id}'),
                period='2024-12',
                revenue=revenue,
                yoy_growth=yoy_growth,
                mom_growth=mom_growth,
                ytd_revenue=revenue * 12,
                ytd_growth=yoy_growth
            )
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 營收數據時發生錯誤: {e}")
            return None
    
    async def get_earnings_data(self, stock_id: str) -> Optional[EarningsData]:
        """獲取財報數據（模擬）"""
        try:
            # 模擬延遲
            await asyncio.sleep(0.1)
            
            # 生成模擬數據
            eps = random.uniform(0.5, 5.0)
            eps_growth = random.uniform(-20, 100)
            revenue = random.uniform(1000000000, 5000000000)
            revenue_growth = random.uniform(-15, 60)
            gross_margin = random.uniform(15, 50)
            net_margin = random.uniform(5, 25)
            
            return EarningsData(
                stock_id=stock_id,
                stock_name=self.stock_names.get(stock_id, f'股票{stock_id}'),
                period='2024-Q4',
                eps=eps,
                eps_growth=eps_growth,
                revenue=revenue,
                revenue_growth=revenue_growth,
                gross_margin=gross_margin,
                net_margin=net_margin,
                net_income=revenue * net_margin / 100,
                net_income_growth=eps_growth
            )
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 財報數據時發生錯誤: {e}")
            return None
    
    async def get_comprehensive_stock_analysis(self, stock_id: str) -> Dict[str, Any]:
        """獲取股票綜合分析數據（模擬）"""
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

# 替換原始的 FinlabAPIClient
FinlabAPIClient = MockFinlabAPIClient
