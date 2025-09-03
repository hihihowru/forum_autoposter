"""
個股數據服務
負責獲取個股的 OHLC、營收、財報等數據
"""
import logging
import httpx
import asyncio
import pandas as pd
import finlab
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from .data_source_scheduler import DataSourceScheduler, DataSourceType, get_data_source_scheduler

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class StockOHLCData:
    """股票 OHLC 數據"""
    stock_id: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class StockRevenueData:
    """股票營收數據"""
    stock_id: str
    current_month_revenue: Optional[float] = None
    last_month_revenue: Optional[float] = None
    last_year_same_month_revenue: Optional[float] = None
    month_over_month_growth: Optional[float] = None
    year_over_year_growth: Optional[float] = None
    cumulative_revenue: Optional[float] = None
    last_year_cumulative_revenue: Optional[float] = None
    cumulative_growth: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class StockFinancialData:
    """股票財務數據"""
    stock_id: str
    revenue: Optional[float] = None
    earnings: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    # 財報數據
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    cash_flow: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class StockAnalysisData:
    """股票分析數據"""
    stock_id: str
    technical_indicators: Dict[str, Any]
    trading_signals: List[Dict[str, Any]]
    market_sentiment: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

class StockDataService:
    """個股數據服務"""
    
    def __init__(self, 
                 ohlc_api_url: str = "http://localhost:8001",
                 analyze_api_url: str = "http://localhost:8002",
                 summary_api_url: str = "http://localhost:8003",
                 finlab_api_key: Optional[str] = None):
        """
        初始化個股數據服務
        
        Args:
            ohlc_api_url: OHLC API 服務 URL
            analyze_api_url: 分析 API 服務 URL
            summary_api_url: 摘要 API 服務 URL
            finlab_api_key: FinLab API 金鑰
        """
        self.ohlc_api_url = ohlc_api_url
        self.analyze_api_url = analyze_api_url
        self.summary_api_url = summary_api_url
        self.finlab_api_key = finlab_api_key
        self.data_scheduler = get_data_source_scheduler()
        
        # 初始化 FinLab
        self._finlab_logged_in = False
        if finlab_api_key:
            self._ensure_finlab_login()
        
        logger.info("個股數據服務初始化完成")
    
    def _ensure_finlab_login(self):
        """確保 FinLab API 已登入"""
        if not self._finlab_logged_in and self.finlab_api_key:
            try:
                finlab.login(self.finlab_api_key)
                self._finlab_logged_in = True
                logger.info("FinLab API 登入成功")
            except Exception as e:
                logger.warning(f"FinLab API 登入失敗: {e}")
                self._finlab_logged_in = False
    
    async def get_stock_ohlc_data(self, stock_id: str) -> Optional[List[StockOHLCData]]:
        """
        獲取股票 OHLC 數據
        
        Args:
            stock_id: 股票代號
            
        Returns:
            OHLC 數據列表
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ohlc_api_url}/get_ohlc",
                    params={"stock_id": stock_id},
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"獲取 {stock_id} OHLC 數據失敗: HTTP {response.status_code}")
                    return None
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"獲取 {stock_id} OHLC 數據錯誤: {data['error']}")
                    return None
                
                # 轉換為 StockOHLCData 物件
                ohlc_data = []
                for item in data:
                    ohlc_data.append(StockOHLCData(
                        stock_id=stock_id,
                        date=item['date'],
                        open=item['open'],
                        high=item['high'],
                        low=item['low'],
                        close=item['close'],
                        volume=item['volume']
                    ))
                
                logger.info(f"成功獲取 {stock_id} 的 {len(ohlc_data)} 筆 OHLC 數據")
                return ohlc_data
                
        except Exception as e:
            logger.error(f"獲取 {stock_id} OHLC 數據異常: {e}")
            return None
    
    async def get_stock_analysis_data(self, stock_id: str) -> Optional[StockAnalysisData]:
        """
        獲取股票分析數據 (技術指標和交易信號)
        
        Args:
            stock_id: 股票代號
            
        Returns:
            分析數據
        """
        try:
            # 先獲取 OHLC 數據
            ohlc_data = await self.get_stock_ohlc_data(stock_id)
            if not ohlc_data:
                logger.error(f"無法獲取 {stock_id} 的 OHLC 數據，跳過分析")
                return None
            
            # 轉換為分析 API 需要的格式
            ohlc_items = []
            for item in ohlc_data:
                ohlc_items.append({
                    "date": item.date,
                    "open": item.open,
                    "high": item.high,
                    "low": item.low,
                    "close": item.close,
                    "volume": item.volume
                })
            
            # 調用分析 API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.analyze_api_url}/analyze",
                    json={
                        "stock_id": stock_id,
                        "ohlc": ohlc_items
                    },
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    logger.error(f"獲取 {stock_id} 分析數據失敗: HTTP {response.status_code}")
                    return None
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"獲取 {stock_id} 分析數據錯誤: {data['error']}")
                    return None
                
                # 轉換為 StockAnalysisData 物件
                analysis_data = StockAnalysisData(
                    stock_id=stock_id,
                    technical_indicators=data.get('indicators', {}),
                    trading_signals=data.get('signals', []),
                    market_sentiment=data.get('sentiment'),
                    raw_data=data
                )
                
                logger.info(f"成功獲取 {stock_id} 的分析數據")
                return analysis_data
                
        except Exception as e:
            logger.error(f"獲取 {stock_id} 分析數據異常: {e}")
            return None
    
    async def get_stock_revenue_data(self, stock_id: str) -> Optional[StockRevenueData]:
        """
        獲取股票月營收數據
        
        Args:
            stock_id: 股票代號
            
        Returns:
            營收數據
        """
        try:
            if not self.finlab_api_key:
                logger.warning("FinLab API 金鑰未設定，無法獲取營收數據")
                return None
            
            # 確保 FinLab 已登入
            self._ensure_finlab_login()
            if not self._finlab_logged_in:
                logger.warning("FinLab API 未登入，無法獲取營收數據")
                return None
            
            from finlab import data
            
            # 獲取營收相關數據
            revenue_data = {}
            
            # 當月營收
            try:
                current_revenue_df = data.get('monthly_revenue:當月營收')
                if stock_id in current_revenue_df.columns:
                    latest_revenue = current_revenue_df[stock_id].dropna().iloc[-1]
                    revenue_data['current_month_revenue'] = float(latest_revenue)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 當月營收失敗: {e}")
            
            # 上月營收
            try:
                last_month_revenue_df = data.get('monthly_revenue:上月營收')
                if stock_id in last_month_revenue_df.columns:
                    latest_last_month = last_month_revenue_df[stock_id].dropna().iloc[-1]
                    revenue_data['last_month_revenue'] = float(latest_last_month)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 上月營收失敗: {e}")
            
            # 去年當月營收
            try:
                last_year_revenue_df = data.get('monthly_revenue:去年當月營收')
                if stock_id in last_year_revenue_df.columns:
                    latest_last_year = last_year_revenue_df[stock_id].dropna().iloc[-1]
                    revenue_data['last_year_same_month_revenue'] = float(latest_last_year)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 去年當月營收失敗: {e}")
            
            # 月增率
            try:
                mom_growth_df = data.get('monthly_revenue:上月比較增減(%)')
                if stock_id in mom_growth_df.columns:
                    latest_mom_growth = mom_growth_df[stock_id].dropna().iloc[-1]
                    revenue_data['month_over_month_growth'] = float(latest_mom_growth)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 月增率失敗: {e}")
            
            # 年增率
            try:
                yoy_growth_df = data.get('monthly_revenue:去年同月增減(%)')
                if stock_id in yoy_growth_df.columns:
                    latest_yoy_growth = yoy_growth_df[stock_id].dropna().iloc[-1]
                    revenue_data['year_over_year_growth'] = float(latest_yoy_growth)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 年增率失敗: {e}")
            
            # 累計營收
            try:
                cumulative_revenue_df = data.get('monthly_revenue:當月累計營收')
                if stock_id in cumulative_revenue_df.columns:
                    latest_cumulative = cumulative_revenue_df[stock_id].dropna().iloc[-1]
                    revenue_data['cumulative_revenue'] = float(latest_cumulative)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 累計營收失敗: {e}")
            
            # 去年累計營收
            try:
                last_year_cumulative_df = data.get('monthly_revenue:去年累計營收')
                if stock_id in last_year_cumulative_df.columns:
                    latest_last_year_cumulative = last_year_cumulative_df[stock_id].dropna().iloc[-1]
                    revenue_data['last_year_cumulative_revenue'] = float(latest_last_year_cumulative)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 去年累計營收失敗: {e}")
            
            # 累計年增率
            try:
                cumulative_growth_df = data.get('monthly_revenue:前期比較增減(%)')
                if stock_id in cumulative_growth_df.columns:
                    latest_cumulative_growth = cumulative_growth_df[stock_id].dropna().iloc[-1]
                    revenue_data['cumulative_growth'] = float(latest_cumulative_growth)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 累計年增率失敗: {e}")
            
            # 創建營收數據物件
            revenue_data_obj = StockRevenueData(
                stock_id=stock_id,
                **revenue_data,
                raw_data={"source": "finlab", "timestamp": datetime.now().isoformat()}
            )
            
            logger.info(f"成功獲取 {stock_id} 的營收數據")
            return revenue_data_obj
            
        except Exception as e:
            logger.error(f"獲取 {stock_id} 營收數據異常: {e}")
            return None
    
    async def get_stock_financial_data(self, stock_id: str) -> Optional[StockFinancialData]:
        """
        獲取股票財務數據 (財報等)
        
        Args:
            stock_id: 股票代號
            
        Returns:
            財務數據
        """
        try:
            if not self.finlab_api_key:
                logger.warning("FinLab API 金鑰未設定，無法獲取財報數據")
                return None
            
            # 確保 FinLab 已登入
            self._ensure_finlab_login()
            if not self._finlab_logged_in:
                logger.warning("FinLab API 未登入，無法獲取財報數據")
                return None
            
            from finlab import data
            
            # 獲取財報相關數據
            financial_data = {}
            
            # 營業收入淨額
            try:
                revenue_df = data.get('financial_statement:營業收入淨額')
                if stock_id in revenue_df.columns:
                    latest_revenue = revenue_df[stock_id].dropna().iloc[-1]
                    financial_data['revenue'] = float(latest_revenue)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 營業收入失敗: {e}")
            
            # 每股盈餘
            try:
                eps_df = data.get('financial_statement:每股盈餘')
                if stock_id in eps_df.columns:
                    latest_eps = eps_df[stock_id].dropna().iloc[-1]
                    financial_data['eps'] = float(latest_eps)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 每股盈餘失敗: {e}")
            
            # 資產總額
            try:
                total_assets_df = data.get('financial_statement:資產總額')
                if stock_id in total_assets_df.columns:
                    latest_assets = total_assets_df[stock_id].dropna().iloc[-1]
                    financial_data['total_assets'] = float(latest_assets)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 資產總額失敗: {e}")
            
            # 負債總額
            try:
                total_liabilities_df = data.get('financial_statement:負債總額')
                if stock_id in total_liabilities_df.columns:
                    latest_liabilities = total_liabilities_df[stock_id].dropna().iloc[-1]
                    financial_data['total_liabilities'] = float(latest_liabilities)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 負債總額失敗: {e}")
            
            # 股東權益總額
            try:
                shareholders_equity_df = data.get('financial_statement:股東權益總額')
                if stock_id in shareholders_equity_df.columns:
                    latest_equity = shareholders_equity_df[stock_id].dropna().iloc[-1]
                    financial_data['shareholders_equity'] = float(latest_equity)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 股東權益失敗: {e}")
            
            # 營業利益
            try:
                operating_income_df = data.get('financial_statement:營業利益')
                if stock_id in operating_income_df.columns:
                    latest_operating_income = operating_income_df[stock_id].dropna().iloc[-1]
                    financial_data['operating_income'] = float(latest_operating_income)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 營業利益失敗: {e}")
            
            # 歸屬母公司淨利
            try:
                net_income_df = data.get('financial_statement:歸屬母公司淨利_損')
                if stock_id in net_income_df.columns:
                    latest_net_income = net_income_df[stock_id].dropna().iloc[-1]
                    financial_data['net_income'] = float(latest_net_income)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 歸屬母公司淨利失敗: {e}")
            
            # 營業活動之淨現金流入
            try:
                cash_flow_df = data.get('financial_statement:營業活動之淨現金流入_流出')
                if stock_id in cash_flow_df.columns:
                    latest_cash_flow = cash_flow_df[stock_id].dropna().iloc[-1]
                    financial_data['cash_flow'] = float(latest_cash_flow)
            except Exception as e:
                logger.warning(f"獲取 {stock_id} 現金流量失敗: {e}")
            
            # 創建財務數據物件
            financial_data_obj = StockFinancialData(
                stock_id=stock_id,
                **financial_data,
                raw_data={"source": "finlab", "timestamp": datetime.now().isoformat()}
            )
            
            logger.info(f"成功獲取 {stock_id} 的財務數據")
            return financial_data_obj
            
        except Exception as e:
            logger.error(f"獲取 {stock_id} 財務數據異常: {e}")
            return None
    
    async def get_comprehensive_stock_data(self, stock_id: str) -> Dict[str, Any]:
        """
        獲取股票綜合數據 (OHLC + 分析 + 財務 + 營收)
        
        Args:
            stock_id: 股票代號
            
        Returns:
            綜合股票數據
        """
        try:
            logger.info(f"開始獲取 {stock_id} 的綜合數據")
            
            # 並行獲取各種數據
            ohlc_task = self.get_stock_ohlc_data(stock_id)
            analysis_task = self.get_stock_analysis_data(stock_id)
            financial_task = self.get_stock_financial_data(stock_id)
            revenue_task = self.get_stock_revenue_data(stock_id)
            
            # 等待所有任務完成
            ohlc_data, analysis_data, financial_data, revenue_data = await asyncio.gather(
                ohlc_task, analysis_task, financial_task, revenue_task, return_exceptions=True
            )
            
            # 處理異常
            if isinstance(ohlc_data, Exception):
                logger.error(f"獲取 {stock_id} OHLC 數據失敗: {ohlc_data}")
                ohlc_data = None
            
            if isinstance(analysis_data, Exception):
                logger.error(f"獲取 {stock_id} 分析數據失敗: {analysis_data}")
                analysis_data = None
            
            if isinstance(financial_data, Exception):
                logger.error(f"獲取 {stock_id} 財務數據失敗: {financial_data}")
                financial_data = None
            
            if isinstance(revenue_data, Exception):
                logger.error(f"獲取 {stock_id} 營收數據失敗: {revenue_data}")
                revenue_data = None
            
            # 組裝綜合數據
            comprehensive_data = {
                "stock_id": stock_id,
                "ohlc_data": ohlc_data,
                "analysis_data": analysis_data,
                "financial_data": financial_data,
                "revenue_data": revenue_data,
                "has_ohlc": ohlc_data is not None,
                "has_analysis": analysis_data is not None,
                "has_financial": financial_data is not None,
                "has_revenue": revenue_data is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"成功獲取 {stock_id} 的綜合數據")
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"獲取 {stock_id} 綜合數據異常: {e}")
            return {
                "stock_id": stock_id,
                "ohlc_data": None,
                "analysis_data": None,
                "financial_data": None,
                "revenue_data": None,
                "has_ohlc": False,
                "has_analysis": False,
                "has_financial": False,
                "has_revenue": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 創建服務實例的工廠函數
def create_stock_data_service(finlab_api_key: Optional[str] = None) -> StockDataService:
    """創建個股數據服務實例"""
    if finlab_api_key is None:
        finlab_api_key = os.getenv('FINLAB_API_KEY')
        if finlab_api_key:
            logger.info(f"從環境變數載入 FinLab API key: {finlab_api_key[:10]}...")
        else:
            logger.warning("環境變數中未找到 FINLAB_API_KEY")
    
    return StockDataService(finlab_api_key=finlab_api_key)

# 測試函數
async def test_stock_data_service():
    """測試個股數據服務"""
    try:
        service = create_stock_data_service()
        
        # 測試股票代號
        test_stock_id = "2330"
        
        print("🔍 測試個股數據服務")
        print("=" * 50)
        
        # 測試綜合數據獲取
        comprehensive_data = await service.get_comprehensive_stock_data(test_stock_id)
        
        print(f"股票代號: {comprehensive_data['stock_id']}")
        print(f"有 OHLC 數據: {comprehensive_data['has_ohlc']}")
        print(f"有分析數據: {comprehensive_data['has_analysis']}")
        print(f"有財務數據: {comprehensive_data['has_financial']}")
        
        if comprehensive_data['ohlc_data']:
            print(f"OHLC 數據筆數: {len(comprehensive_data['ohlc_data'])}")
            if comprehensive_data['ohlc_data']:
                latest = comprehensive_data['ohlc_data'][-1]
                print(f"最新價格: {latest.close}")
        
        if comprehensive_data['analysis_data']:
            print(f"技術指標: {list(comprehensive_data['analysis_data'].technical_indicators.keys())}")
            print(f"交易信號: {len(comprehensive_data['analysis_data'].trading_signals)} 個")
        
        if comprehensive_data['financial_data']:
            print(f"營收: {comprehensive_data['financial_data'].revenue}")
            print(f"本益比: {comprehensive_data['financial_data'].pe_ratio}")
        
        print("\n✅ 測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_stock_data_service())
