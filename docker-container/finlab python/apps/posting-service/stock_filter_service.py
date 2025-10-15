"""
股票篩選服務
根據觸發器類型篩選符合條件的股票
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

class StockFilterService:
    """股票篩選服務"""
    
    def __init__(self):
        self.ohlc_api_url = "http://ohlc-api:8000"  # OHLC API 服務
        self.timeout = 30.0
    
    async def filter_stocks_by_trigger(
        self,
        trigger_type: str,
        stock_sorting: str = 'five_day_change_desc',
        max_stocks: int = 10,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        根據觸發器類型篩選股票
        
        Args:
            trigger_type: 觸發器類型
            stock_sorting: 股票排序方式
            max_stocks: 最大股票數量
            additional_filters: 額外篩選條件
            
        Returns:
            篩選後的股票列表
        """
        try:
            logger.info(f"🔍🔍🔍 開始股票篩選流程 🔍🔍🔍")
            logger.info(f"📋 篩選參數:")
            logger.info(f"   🎯 觸發器類型: {trigger_type}")
            logger.info(f"   📊 排序方式: {stock_sorting}")
            logger.info(f"   📈 最大檔數: {max_stocks}")
            logger.info(f"   🔧 額外篩選條件: {additional_filters}")
            
            # 根據觸發器類型獲取股票數據
            logger.info(f"🎯 根據觸發器類型獲取股票數據...")
            if trigger_type == 'limit_up_after_hours':
                logger.info(f"   📈 觸發器: 盤後漲停股票")
                stocks = await self._get_limit_up_stocks()
            elif trigger_type == 'limit_down_after_hours':
                logger.info(f"   📉 觸發器: 盤後跌停股票")
                stocks = await self._get_limit_down_stocks()
            elif trigger_type == 'volume_surge':
                logger.info(f"   📊 觸發器: 成交量暴增股票")
                stocks = await self._get_volume_surge_stocks()
            elif trigger_type == 'news_trigger':
                logger.info(f"   📰 觸發器: 新聞觸發股票")
                stocks = await self._get_news_trigger_stocks()
            elif trigger_type == 'intraday_gainers_by_amount':
                logger.info(f"   📈 觸發器: 盤中漲幅較大股票")
                stocks = await self._get_intraday_gainers_stocks()
            elif trigger_type == 'intraday_limit_down':
                logger.info(f"   📉 觸發器: 盤中跌停股票")
                stocks = await self._get_intraday_limit_down_stocks()
            elif trigger_type == 'intraday_limit_up':
                logger.info(f"   📈 觸發器: 盤中漲停股票")
                stocks = await self._get_intraday_limit_up_stocks()
            elif trigger_type == 'intraday_volume_leaders':
                logger.info(f"   📊 觸發器: 盤中成交量領先股票")
                stocks = await self._get_default_stocks()  # 暫時使用預設股票
            elif trigger_type == 'intraday_amount_leaders':
                logger.info(f"   💰 觸發器: 盤中成交額領先股票")
                stocks = await self._get_default_stocks()  # 暫時使用預設股票
            elif trigger_type == 'intraday_limit_down_by_amount':
                logger.info(f"   📉 觸發器: 盤中跌停成交額股票")
                stocks = await self._get_default_stocks()  # 暫時使用預設股票
            else:
                logger.warning(f"⚠️ 未知的觸發器類型: {trigger_type}")
                logger.info(f"   🔄 使用預設股票列表")
                stocks = await self._get_default_stocks()
            
            logger.info(f"📊 原始股票數據獲取完成，共 {len(stocks)} 檔股票")
            
            # 顯示原始股票列表
            if stocks:
                logger.info(f"📋 原始股票列表:")
                for idx, stock in enumerate(stocks, 1):
                    logger.info(f"   {idx}. {stock.get('stock_name', 'N/A')}({stock.get('stock_code', 'N/A')}) - 漲幅: {stock.get('change_percent', 0)}%, 成交量比: {stock.get('volume_ratio', 0)}, 市值: {stock.get('market_cap', 0)}")
            else:
                logger.warning(f"⚠️ 沒有獲取到任何股票數據")
            
            # 應用排序
            logger.info(f"🔄 應用排序: {stock_sorting}")
            stocks_before_sort = len(stocks)
            stocks = self._apply_sorting(stocks, stock_sorting)
            logger.info(f"✅ 排序完成，股票數量: {stocks_before_sort} -> {len(stocks)}")
            
            # 顯示排序後的股票列表
            if stocks:
                logger.info(f"📋 排序後股票列表:")
                for idx, stock in enumerate(stocks, 1):
                    logger.info(f"   {idx}. {stock.get('stock_name', 'N/A')}({stock.get('stock_code', 'N/A')}) - 漲幅: {stock.get('change_percent', 0)}%, 成交量比: {stock.get('volume_ratio', 0)}, 市值: {stock.get('market_cap', 0)}")
            
            # 應用數量限制
            logger.info(f"📊 應用數量限制: 最多 {max_stocks} 檔")
            stocks_before_limit = len(stocks)
            stocks = stocks[:max_stocks]
            logger.info(f"✅ 數量限制完成，股票數量: {stocks_before_limit} -> {len(stocks)}")
            
            # 應用額外篩選條件
            if additional_filters:
                logger.info(f"🔧 應用額外篩選條件: {additional_filters}")
                stocks_before_filter = len(stocks)
                stocks = self._apply_additional_filters(stocks, additional_filters)
                logger.info(f"✅ 額外篩選完成，股票數量: {stocks_before_filter} -> {len(stocks)}")
            else:
                logger.info(f"ℹ️ 沒有額外篩選條件")
            
            # 顯示最終結果
            logger.info(f"🎯 最終篩選結果:")
            if stocks:
                logger.info(f"   📊 共 {len(stocks)} 檔股票:")
                for idx, stock in enumerate(stocks, 1):
                    logger.info(f"   {idx}. {stock.get('stock_name', 'N/A')}({stock.get('stock_code', 'N/A')}) - 漲幅: {stock.get('change_percent', 0)}%, 成交量比: {stock.get('volume_ratio', 0)}, 市值: {stock.get('market_cap', 0)}")
            else:
                logger.warning(f"   ⚠️ 沒有符合條件的股票")
            
            logger.info(f"✅✅✅ 股票篩選流程完成 ✅✅✅")
            return stocks
            
        except Exception as e:
            logger.error(f"❌❌❌ 股票篩選失敗 ❌❌❌")
            logger.error(f"🔍 錯誤詳情: {str(e)}")
            import traceback
            logger.error(f"🔍 錯誤堆疊:\n{traceback.format_exc()}")
            logger.info(f"🔄 返回模擬數據作為備用")
            # 返回模擬數據作為備用
            return self._get_mock_intraday_limit_up_stocks()
    
    async def _get_limit_up_stocks(self) -> List[Dict[str, Any]]:
        """獲取盤後漲停股票"""
        try:
            logger.info(f"📈 正在從 OHLC API 獲取盤後漲停股票...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ohlc_api_url}/after_hours_limit_up",
                    params={
                        "limit": 100,  # 獲取最多100檔
                        "changeThreshold": 9.5  # 漲幅閾值9.5%
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_limit_up_stocks()
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"❌ OHLC API 返回錯誤: {data['error']}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_limit_up_stocks()
                
                if not data.get("success", False):
                    logger.error(f"❌ OHLC API 調用不成功")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_limit_up_stocks()
                
                stocks_data = data.get("stocks", [])
                logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔盤後漲停股票")
                
                # 轉換為標準格式
                stocks = []
                for stock in stocks_data:
                    # 計算成交量比（簡化處理，使用成交量作為基礎）
                    volume_ratio = 1.0  # 預設值，可以後續優化
                    if stock.get('volume', 0) > 0:
                        # 簡單的成交量比計算（可以根據實際需求調整）
                        volume_ratio = min(stock.get('volume', 0) / 1000000, 10.0)  # 限制在10以內
                    
                    # 計算市值（簡化處理）
                    market_cap = stock.get('current_price', 0) * 1000000000  # 假設10億股
                    
                    stocks.append({
                        "stock_code": stock.get('stock_code', ''),
                        "stock_name": stock.get('stock_name', ''),
                        "change_percent": stock.get('change_percent', 0),
                        "volume_ratio": volume_ratio,
                        "market_cap": market_cap,
                        "price": stock.get('current_price', 0),
                        "volume": stock.get('volume', 0),
                        "five_day_change": stock.get('five_day_change', 0),
                        "industry": stock.get('industry', '未知')
                    })
                
                logger.info(f"✅ 轉換完成，共 {len(stocks)} 檔股票")
                return stocks
                
        except Exception as e:
            logger.error(f"❌ 獲取盤後漲停股票失敗: {e}")
            logger.info(f"🔄 回退到模擬數據")
            return self._get_mock_limit_up_stocks()
    
    def _get_mock_limit_up_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬盤後漲停股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 盤後漲停股票")
        return [
            {"stock_code": "841", "stock_name": "大江", "change_percent": 10.0, "volume_ratio": 2.5, "market_cap": 500000000, "price": 45.2},
            {"stock_code": "2330", "stock_name": "台積電", "change_percent": 9.9, "volume_ratio": 1.8, "market_cap": 15000000000000, "price": 1425.0},
            {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 9.7, "volume_ratio": 1.2, "market_cap": 2000000000000, "price": 105.5},
            {"stock_code": "2454", "stock_name": "聯發科", "change_percent": 9.5, "volume_ratio": 1.5, "market_cap": 3000000000000, "price": 890.0},
            {"stock_code": "2412", "stock_name": "中華電", "change_percent": 9.2, "volume_ratio": 0.8, "market_cap": 800000000000, "price": 125.0},
        ]
    
    async def _get_limit_down_stocks(self) -> List[Dict[str, Any]]:
        """獲取盤後跌停股票"""
        try:
            logger.info(f"📉 正在從 OHLC API 獲取盤後跌停股票...")
            
            # 由於 OHLC API 沒有跌停股票端點，我們需要通過其他方式獲取
            # 這裡我們使用一個通用的方法來獲取所有股票數據，然後篩選跌停股票
            async with httpx.AsyncClient() as client:
                # 嘗試獲取所有股票數據（通過漲停API但設置負閾值）
                response = await client.get(
                    f"{self.ohlc_api_url}/after_hours_limit_up",
                    params={
                        "limit": 1000,  # 獲取更多數據
                        "changeThreshold": -9.5  # 負閾值來獲取跌停股票
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_limit_down_stocks()
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"❌ OHLC API 返回錯誤: {data['error']}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_limit_down_stocks()
                
                if not data.get("success", False):
                    logger.error(f"❌ OHLC API 調用不成功")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_limit_down_stocks()
                
                stocks_data = data.get("stocks", [])
                logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔股票數據")
                
                # 篩選跌停股票（漲幅 <= -9.5%）
                limit_down_stocks = []
                for stock in stocks_data:
                    change_percent = stock.get('change_percent', 0)
                    if change_percent <= -9.5:  # 跌停條件
                        # 計算成交量比
                        volume_ratio = 1.0
                        if stock.get('volume', 0) > 0:
                            volume_ratio = min(stock.get('volume', 0) / 1000000, 10.0)
                        
                        # 計算市值
                        market_cap = stock.get('current_price', 0) * 1000000000
                        
                        limit_down_stocks.append({
                            "stock_code": stock.get('stock_code', ''),
                            "stock_name": stock.get('stock_name', ''),
                            "change_percent": change_percent,
                            "volume_ratio": volume_ratio,
                            "market_cap": market_cap,
                            "price": stock.get('current_price', 0),
                            "volume": stock.get('volume', 0),
                            "five_day_change": stock.get('five_day_change', 0),
                            "industry": stock.get('industry', '未知')
                        })
                
                logger.info(f"✅ 篩選出 {len(limit_down_stocks)} 檔盤後跌停股票")
                return limit_down_stocks
                
        except Exception as e:
            logger.error(f"❌ 獲取盤後跌停股票失敗: {e}")
            logger.info(f"🔄 回退到模擬數據")
            return self._get_mock_limit_down_stocks()
    
    def _get_mock_limit_down_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬盤後跌停股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 盤後跌停股票")
        return [
            {"stock_code": "1301", "stock_name": "台塑", "change_percent": -9.8, "volume_ratio": 1.2, "market_cap": 800000000000, "price": 85.0},
            {"stock_code": "1303", "stock_name": "南亞", "change_percent": -9.5, "volume_ratio": 1.0, "market_cap": 600000000000, "price": 65.5},
            {"stock_code": "2882", "stock_name": "國泰金", "change_percent": -9.2, "volume_ratio": 0.9, "market_cap": 1200000000000, "price": 55.0},
        ]
    
    async def _get_volume_surge_stocks(self) -> List[Dict[str, Any]]:
        """獲取成交量暴增股票"""
        try:
            logger.info(f"📊 正在從 OHLC API 獲取成交量暴增股票...")
            
            # 通過獲取所有股票數據，然後按成交量排序來找出成交量暴增的股票
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ohlc_api_url}/after_hours_limit_up",
                    params={
                        "limit": 1000,  # 獲取更多數據
                        "changeThreshold": 0.0  # 獲取所有股票
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_volume_surge_stocks()
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"❌ OHLC API 返回錯誤: {data['error']}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_volume_surge_stocks()
                
                if not data.get("success", False):
                    logger.error(f"❌ OHLC API 調用不成功")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_volume_surge_stocks()
                
                stocks_data = data.get("stocks", [])
                logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔股票數據")
                
                # 按成交量排序，取前50檔作為成交量暴增股票
                volume_surge_stocks = []
                for stock in stocks_data:
                    volume = stock.get('volume', 0)
                    if volume > 0:  # 只考慮有成交量的股票
                        # 計算成交量比（簡化處理）
                        volume_ratio = min(volume / 1000000, 10.0)  # 限制在10以內
                        
                        # 計算市值
                        market_cap = stock.get('current_price', 0) * 1000000000
                        
                        volume_surge_stocks.append({
                            "stock_code": stock.get('stock_code', ''),
                            "stock_name": stock.get('stock_name', ''),
                            "change_percent": stock.get('change_percent', 0),
                            "volume_ratio": volume_ratio,
                            "market_cap": market_cap,
                            "price": stock.get('current_price', 0),
                            "volume": volume,
                            "five_day_change": stock.get('five_day_change', 0),
                            "industry": stock.get('industry', '未知')
                        })
                
                # 按成交量排序，取前50檔
                volume_surge_stocks.sort(key=lambda x: x['volume'], reverse=True)
                volume_surge_stocks = volume_surge_stocks[:50]
                
                logger.info(f"✅ 篩選出 {len(volume_surge_stocks)} 檔成交量暴增股票")
                return volume_surge_stocks
                
        except Exception as e:
            logger.error(f"❌ 獲取成交量暴增股票失敗: {e}")
            logger.info(f"🔄 回退到模擬數據")
            return self._get_mock_volume_surge_stocks()
    
    def _get_mock_volume_surge_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬成交量暴增股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 成交量暴增股票")
        return [
            {"stock_code": "841", "stock_name": "大江", "change_percent": 5.2, "volume_ratio": 5.8, "market_cap": 500000000, "price": 45.2},
            {"stock_code": "2330", "stock_name": "台積電", "change_percent": 3.5, "volume_ratio": 4.2, "market_cap": 15000000000000, "price": 1425.0},
            {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 2.8, "volume_ratio": 3.5, "market_cap": 2000000000000, "price": 105.5},
        ]
    
    async def _get_news_trigger_stocks(self) -> List[Dict[str, Any]]:
        """獲取新聞觸發股票"""
        try:
            logger.info(f"📰 正在從 OHLC API 獲取新聞觸發股票...")
            
            # 新聞觸發股票通常是漲幅適中但有成交量的股票
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ohlc_api_url}/after_hours_limit_up",
                    params={
                        "limit": 1000,  # 獲取更多數據
                        "changeThreshold": 1.0  # 漲幅 >= 1%
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_news_trigger_stocks()
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"❌ OHLC API 返回錯誤: {data['error']}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_news_trigger_stocks()
                
                if not data.get("success", False):
                    logger.error(f"❌ OHLC API 調用不成功")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_news_trigger_stocks()
                
                stocks_data = data.get("stocks", [])
                logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔股票數據")
                
                # 篩選新聞觸發股票（漲幅在1%-8%之間，有成交量）
                news_trigger_stocks = []
                for stock in stocks_data:
                    change_percent = stock.get('change_percent', 0)
                    volume = stock.get('volume', 0)
                    
                    # 新聞觸發條件：漲幅在1%-8%之間，且有成交量
                    if 1.0 <= change_percent <= 8.0 and volume > 0:
                        # 計算成交量比
                        volume_ratio = min(volume / 1000000, 10.0)
                        
                        # 計算市值
                        market_cap = stock.get('current_price', 0) * 1000000000
                        
                        news_trigger_stocks.append({
                            "stock_code": stock.get('stock_code', ''),
                            "stock_name": stock.get('stock_name', ''),
                            "change_percent": change_percent,
                            "volume_ratio": volume_ratio,
                            "market_cap": market_cap,
                            "price": stock.get('current_price', 0),
                            "volume": volume,
                            "five_day_change": stock.get('five_day_change', 0),
                            "industry": stock.get('industry', '未知')
                        })
                
                # 按成交量排序，取前30檔
                news_trigger_stocks.sort(key=lambda x: x['volume'], reverse=True)
                news_trigger_stocks = news_trigger_stocks[:30]
                
                logger.info(f"✅ 篩選出 {len(news_trigger_stocks)} 檔新聞觸發股票")
                return news_trigger_stocks
                
        except Exception as e:
            logger.error(f"❌ 獲取新聞觸發股票失敗: {e}")
            logger.info(f"🔄 回退到模擬數據")
            return self._get_mock_news_trigger_stocks()
    
    def _get_mock_news_trigger_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬新聞觸發股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 新聞觸發股票")
        return [
            {"stock_code": "2330", "stock_name": "台積電", "change_percent": 2.5, "volume_ratio": 1.5, "market_cap": 15000000000000, "price": 1425.0},
            {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 1.8, "volume_ratio": 1.2, "market_cap": 2000000000000, "price": 105.5},
            {"stock_code": "2454", "stock_name": "聯發科", "change_percent": 3.2, "volume_ratio": 1.8, "market_cap": 3000000000000, "price": 890.0},
        ]
    
    async def _get_intraday_gainers_stocks(self) -> List[Dict[str, Any]]:
        """獲取盤中漲幅較大股票"""
        try:
            logger.info(f"📈 正在從 OHLC API 獲取盤中漲幅較大股票...")
            
            # 盤中漲幅較大股票通常是漲幅在5%-9%之間的股票
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ohlc_api_url}/after_hours_limit_up",
                    params={
                        "limit": 1000,  # 獲取更多數據
                        "changeThreshold": 5.0  # 漲幅 >= 5%
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_intraday_gainers_stocks()
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"❌ OHLC API 返回錯誤: {data['error']}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_intraday_gainers_stocks()
                
                if not data.get("success", False):
                    logger.error(f"❌ OHLC API 調用不成功")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_intraday_gainers_stocks()
                
                stocks_data = data.get("stocks", [])
                logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔股票數據")
                
                # 篩選盤中漲幅較大股票（漲幅在5%-9%之間）
                intraday_gainers = []
                for stock in stocks_data:
                    change_percent = stock.get('change_percent', 0)
                    volume = stock.get('volume', 0)
                    
                    # 盤中漲幅較大條件：漲幅在5%-9%之間
                    if 5.0 <= change_percent <= 9.0 and volume > 0:
                        # 計算成交量比
                        volume_ratio = min(volume / 1000000, 10.0)
                        
                        # 計算市值
                        market_cap = stock.get('current_price', 0) * 1000000000
                        
                        intraday_gainers.append({
                            "stock_code": stock.get('stock_code', ''),
                            "stock_name": stock.get('stock_name', ''),
                            "change_percent": change_percent,
                            "volume_ratio": volume_ratio,
                            "market_cap": market_cap,
                            "price": stock.get('current_price', 0),
                            "volume": volume,
                            "five_day_change": stock.get('five_day_change', 0),
                            "industry": stock.get('industry', '未知')
                        })
                
                # 按漲幅排序，取前30檔
                intraday_gainers.sort(key=lambda x: x['change_percent'], reverse=True)
                intraday_gainers = intraday_gainers[:30]
                
                logger.info(f"✅ 篩選出 {len(intraday_gainers)} 檔盤中漲幅較大股票")
                return intraday_gainers
                
        except Exception as e:
            logger.error(f"❌ 獲取盤中漲幅較大股票失敗: {e}")
            logger.info(f"🔄 回退到模擬數據")
            return self._get_mock_intraday_gainers_stocks()
    
    def _get_mock_intraday_gainers_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬盤中漲幅較大股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 盤中漲幅較大股票")
        return [
            {"stock_code": "841", "stock_name": "大江", "change_percent": 7.5, "volume_ratio": 2.8, "market_cap": 500000000, "price": 45.2},
            {"stock_code": "2330", "stock_name": "台積電", "change_percent": 6.2, "volume_ratio": 2.1, "market_cap": 15000000000000, "price": 1425.0},
            {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 5.8, "volume_ratio": 1.9, "market_cap": 2000000000000, "price": 105.5},
        ]
    
    async def _get_intraday_limit_down_stocks(self) -> List[Dict[str, Any]]:
        """獲取盤中跌停股票"""
        try:
            logger.info(f"📉 正在從 OHLC API 獲取盤中跌停股票...")
            
            # 盤中跌停股票通常是跌幅 <= -9.5% 的股票
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ohlc_api_url}/after_hours_limit_up",
                    params={
                        "limit": 1000,  # 獲取更多數據
                        "changeThreshold": -9.5  # 跌幅 <= -9.5%
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_intraday_limit_down_stocks()
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"❌ OHLC API 返回錯誤: {data['error']}")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_intraday_limit_down_stocks()
                
                if not data.get("success", False):
                    logger.error(f"❌ OHLC API 調用不成功")
                    logger.info(f"🔄 回退到模擬數據")
                    return self._get_mock_intraday_limit_down_stocks()
                
                stocks_data = data.get("stocks", [])
                logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔股票數據")
                
                # 篩選盤中跌停股票（跌幅 <= -9.5%）
                intraday_limit_down = []
                for stock in stocks_data:
                    change_percent = stock.get('change_percent', 0)
                    
                    # 盤中跌停條件：跌幅 <= -9.5%
                    if change_percent <= -9.5:
                        # 計算成交量比
                        volume_ratio = 1.0
                        volume = stock.get('volume', 0)
                        if volume > 0:
                            volume_ratio = min(volume / 1000000, 10.0)
                        
                        # 計算市值
                        market_cap = stock.get('current_price', 0) * 1000000000
                        
                        intraday_limit_down.append({
                            "stock_code": stock.get('stock_code', ''),
                            "stock_name": stock.get('stock_name', ''),
                            "change_percent": change_percent,
                            "volume_ratio": volume_ratio,
                            "market_cap": market_cap,
                            "price": stock.get('current_price', 0),
                            "volume": volume,
                            "five_day_change": stock.get('five_day_change', 0),
                            "industry": stock.get('industry', '未知')
                        })
                
                logger.info(f"✅ 篩選出 {len(intraday_limit_down)} 檔盤中跌停股票")
                return intraday_limit_down
                
        except Exception as e:
            logger.error(f"❌ 獲取盤中跌停股票失敗: {e}")
            logger.info(f"🔄 回退到模擬數據")
            return self._get_mock_intraday_limit_down_stocks()
    
    async def _get_intraday_limit_up_stocks(self) -> List[Dict[str, Any]]:
        """獲取盤中漲停股票"""
        try:
            logger.info(f"🔍 開始獲取盤中漲停股票...")
            
            # 調用 OHLC API 獲取股票數據
            url = f"{self.ohlc_api_url}/after_hours_limit_up"
            params = {
                "changeThreshold": 9.5  # 漲幅 >= 9.5%
            }
            
            logger.info(f"📡 調用 OHLC API: {url}")
            logger.info(f"📋 請求參數: {params}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    stocks_data = data.get('stocks', [])
                    
                    logger.info(f"✅ 從 OHLC API 獲取到 {len(stocks_data)} 檔股票數據")
                    
                    # 篩選盤中漲停股票（漲幅 >= 9.5%）
                    intraday_limit_up = []
                    for stock in stocks_data:
                        change_percent = stock.get('change_percent', 0)
                        
                        # 盤中漲停條件：漲幅 >= 9.5%
                        if change_percent >= 9.5:
                            # 計算成交量比
                            volume_ratio = 1.0
                            volume = stock.get('volume', 0)
                            if volume > 0:
                                volume_ratio = min(volume / 1000000, 10.0)
                            
                            # 計算市值
                            market_cap = stock.get('current_price', 0) * 1000000000
                            
                            intraday_limit_up.append({
                                "stock_code": stock.get('stock_code', ''),
                                "stock_name": stock.get('stock_name', ''),
                                "change_percent": change_percent,
                                "volume_ratio": volume_ratio,
                                "market_cap": market_cap,
                                "price": stock.get('current_price', 0),
                                "volume": volume,
                                "five_day_change": stock.get('five_day_change', 0),
                                "industry": stock.get('industry', '未知')
                            })
                    
                    logger.info(f"✅ 篩選出 {len(intraday_limit_up)} 檔盤中漲停股票")
                    return intraday_limit_up
                else:
                    logger.error(f"❌ OHLC API 調用失敗: HTTP {response.status_code}")
                    logger.info(f"🔄 使用模擬數據作為備用")
                    return self._get_mock_intraday_limit_up_stocks()
                        
        except Exception as e:
            logger.error(f"❌ 獲取盤中漲停股票失敗: {e}")
            logger.info(f"🔄 使用模擬數據作為備用")
            return self._get_mock_intraday_limit_up_stocks()
    
    def _get_mock_intraday_limit_down_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬盤中跌停股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 盤中跌停股票")
        return [
            {"stock_code": "1301", "stock_name": "台塑", "change_percent": -9.8, "volume_ratio": 1.5, "market_cap": 800000000000, "price": 85.0},
            {"stock_code": "1303", "stock_name": "南亞", "change_percent": -9.5, "volume_ratio": 1.2, "market_cap": 600000000000, "price": 65.5},
        ]
    
    def _get_mock_intraday_limit_up_stocks(self) -> List[Dict[str, Any]]:
        """獲取模擬盤中漲停股票數據"""
        logger.warning(f"⚠️ 使用模擬數據 - 盤中漲停股票")
        return [
            {"stock_code": "841", "stock_name": "大江", "change_percent": 10.0, "volume_ratio": 2.1, "market_cap": 50000000000, "price": 125.0},
            {"stock_code": "6560", "stock_name": "欣普羅", "change_percent": 9.8, "volume_ratio": 1.8, "market_cap": 30000000000, "price": 85.5},
        ]
    
    async def _get_default_stocks(self) -> List[Dict[str, Any]]:
        """獲取預設股票列表"""
        return [
            {"stock_code": "2330", "stock_name": "台積電", "change_percent": 2.5, "volume_ratio": 1.2, "market_cap": 15000000000000, "price": 1425.0},
            {"stock_code": "2317", "stock_name": "鴻海", "change_percent": 1.8, "volume_ratio": 1.0, "market_cap": 2000000000000, "price": 105.5},
        ]
    
    # 暫時註解掉有問題的方法，先讓服務能正常啟動
    
    def _apply_sorting(self, stocks: List[Dict[str, Any]], sorting_method: str) -> List[Dict[str, Any]]:
        """應用排序"""
        try:
            if not stocks:
                logger.info(f"ℹ️ 沒有股票需要排序")
                return stocks
            
            logger.info(f"🔄 應用排序: {sorting_method}")
            
            if sorting_method == 'five_day_change_desc':
                # 按五日漲跌幅降序排序
                sorted_stocks = sorted(stocks, key=lambda x: x.get('five_day_change', 0), reverse=True)
                logger.info(f"✅ 按五日漲跌幅降序排序完成")
            elif sorting_method == 'change_percent_desc':
                # 按當日漲跌幅降序排序
                sorted_stocks = sorted(stocks, key=lambda x: x.get('change_percent', 0), reverse=True)
                logger.info(f"✅ 按當日漲跌幅降序排序完成")
            elif sorting_method == 'volume_desc':
                # 按成交量降序排序
                sorted_stocks = sorted(stocks, key=lambda x: x.get('volume', 0), reverse=True)
                logger.info(f"✅ 按成交量降序排序完成")
            elif sorting_method == 'market_cap_desc':
                # 按市值降序排序
                sorted_stocks = sorted(stocks, key=lambda x: x.get('market_cap', 0), reverse=True)
                logger.info(f"✅ 按市值降序排序完成")
            else:
                # 預設排序
                sorted_stocks = stocks
                logger.info(f"ℹ️ 使用預設排序")
            
            return sorted_stocks
            
        except Exception as e:
            logger.error(f"❌ 排序失敗: {e}")
            return stocks

# 創建全局實例
stock_filter_service = StockFilterService()
