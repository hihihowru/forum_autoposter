#!/usr/bin/env python3
"""
模擬失敗的 Finlab API 客戶端
用於測試數據獲取失敗的情況
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

class FailingFinlabAPIClient:
    """模擬失敗的 Finlab API 客戶端"""
    
    def __init__(self):
        """初始化模擬失敗的 Finlab API 客戶端"""
        self.api_key = os.getenv('FINLAB_API_KEY', 'mock_key')
        self.base_url = "https://api.finlab.tw"
        self.session = None
        
        logger.info("模擬失敗的 Finlab API 客戶端初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def get_stock_data(self, stock_id: str, days: int = 30) -> Optional[StockData]:
        """獲取股票數據（模擬失敗）"""
        try:
            # 模擬延遲
            await asyncio.sleep(0.1)
            
            # 模擬失敗
            logger.warning(f"模擬股票 {stock_id} 數據獲取失敗")
            return None
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 數據時發生錯誤: {e}")
            return None
    
    async def get_revenue_data(self, stock_id: str) -> Optional[RevenueData]:
        """獲取營收數據（模擬失敗）"""
        try:
            # 模擬延遲
            await asyncio.sleep(0.1)
            
            # 模擬失敗
            logger.warning(f"模擬股票 {stock_id} 營收數據獲取失敗")
            return None
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 營收數據時發生錯誤: {e}")
            return None
    
    async def get_earnings_data(self, stock_id: str) -> Optional[EarningsData]:
        """獲取財報數據（模擬失敗）"""
        try:
            # 模擬延遲
            await asyncio.sleep(0.1)
            
            # 模擬失敗
            logger.warning(f"模擬股票 {stock_id} 財報數據獲取失敗")
            return None
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 財報數據時發生錯誤: {e}")
            return None
    
    async def get_comprehensive_stock_analysis(self, stock_id: str) -> Dict[str, Any]:
        """獲取股票綜合分析數據（模擬失敗）"""
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
                'stock_name': f'股票{stock_id}',
                'analysis_time': datetime.now().isoformat(),
                'stock_data': stock_data,
                'revenue_data': revenue_data,
                'earnings_data': earnings_data,
                'data_completeness': 0,
                'analysis_summary': {},
                'error': '所有數據獲取失敗'
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
FinlabAPIClient = FailingFinlabAPIClient
