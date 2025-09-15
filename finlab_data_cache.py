#!/usr/bin/env python3
"""
FinLab 數據緩存管理器
實現數據緩存機制，降低 API 調用次數
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinLabDataCache:
    """FinLab 數據緩存管理器"""
    
    def __init__(self):
        self.api_key = os.getenv('FINLAB_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 FINLAB_API_KEY 環境變數")
        
        # 緩存目錄
        self.cache_dir = Path("./cache/finlab_data")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 緩存數據
        self.cache_data = {}
        self.cache_date = None
        
        # 數據表配置
        self.data_tables = {
            'price': {
                'open': 'price:開盤價',
                'high': 'price:最高價',
                'low': 'price:最低價',
                'close': 'price:收盤價',
                'volume': 'price:成交股數',
                'amount': 'price:成交金額'
            },
            'revenue': {
                'current_month': 'monthly_revenue:當月營收',
                'previous_month': 'monthly_revenue:上月營收',
                'last_year_same_month': 'monthly_revenue:去年當月營收',
                'mom_change_pct': 'monthly_revenue:上月比較增減(%)',
                'yoy_change_pct': 'monthly_revenue:去年同月增減(%)',
                'ytd_revenue': 'monthly_revenue:當月累計營收',
                'last_year_ytd': 'monthly_revenue:去年累計營收',
                'ytd_change_pct': 'monthly_revenue:前期比較增減(%)'
            },
            'earnings': {
                'eps': 'fundamental_features:每股稅後淨利',
                'revenue_growth': 'fundamental_features:營收成長率',
                'profit_growth': 'fundamental_features:稅後淨利成長率',
                'operating_profit': 'fundamental_features:營業利益',
                'net_profit': 'fundamental_features:歸屬母公司淨利',
                'gross_margin': 'fundamental_features:營業毛利率',
                'net_margin': 'fundamental_features:稅後淨利率'
            }
        }
        
        logger.info("FinLab 數據緩存管理器初始化完成")
    
    def _get_cache_file_path(self, data_type: str) -> Path:
        """獲取緩存文件路徑"""
        today = date.today().strftime('%Y%m%d')
        return self.cache_dir / f"{data_type}_{today}.json"
    
    def _is_cache_valid(self, data_type: str) -> bool:
        """檢查緩存是否有效（當日有效）"""
        cache_file = self._get_cache_file_path(data_type)
        if not cache_file.exists():
            return False
        
        # 檢查文件修改時間是否為今天
        file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_mtime.date() == date.today()
    
    def _load_cache(self, data_type: str) -> Optional[Dict[str, Any]]:
        """載入緩存數據"""
        try:
            cache_file = self._get_cache_file_path(data_type)
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"✅ 載入 {data_type} 緩存數據，包含 {len(data)} 個數據表")
                    return data
        except Exception as e:
            logger.error(f"載入 {data_type} 緩存失敗: {e}")
        
        return None
    
    def _save_cache(self, data_type: str, data: Dict[str, Any]):
        """保存緩存數據"""
        try:
            cache_file = self._get_cache_file_path(data_type)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 保存 {data_type} 緩存數據到 {cache_file}")
        except Exception as e:
            logger.error(f"保存 {data_type} 緩存失敗: {e}")
    
    async def fetch_and_cache_data(self, data_type: str) -> Dict[str, Any]:
        """獲取並緩存數據"""
        # 檢查緩存是否有效
        if self._is_cache_valid(data_type):
            cached_data = self._load_cache(data_type)
            if cached_data:
                return cached_data
        
        # 緩存無效，重新獲取數據
        logger.info(f"🔄 重新獲取 {data_type} 數據...")
        
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取數據
            fetched_data = {}
            tables = self.data_tables.get(data_type, {})
            
            for table_name, table_key in tables.items():
                try:
                    data_source = data.get(table_key)
                    if data_source is not None:
                        # 轉換為可序列化的格式
                        serializable_data = {}
                        for stock_id in data_source.columns:
                            stock_data = data_source[stock_id].dropna()
                            if len(stock_data) > 0:
                                # 只保存最新的幾個數據點
                                latest_data = stock_data.tail(5)
                                serializable_data[stock_id] = {
                                    'values': latest_data.tolist(),
                                    'dates': [str(d) for d in latest_data.index],
                                    'latest_value': float(latest_data.iloc[-1]),
                                    'latest_date': str(latest_data.index[-1])
                                }
                        
                        fetched_data[table_name] = {
                            'table_key': table_key,
                            'data': serializable_data,
                            'total_stocks': len(serializable_data),
                            'fetch_time': datetime.now().isoformat()
                        }
                        
                        logger.info(f"✅ 獲取 {table_name}: {len(serializable_data)} 隻股票")
                    else:
                        logger.warning(f"⚠️ 無法獲取 {table_name} 數據")
                        
                except Exception as e:
                    logger.error(f"獲取 {table_name} 失敗: {e}")
            
            # 保存緩存
            self._save_cache(data_type, fetched_data)
            
            return fetched_data
            
        except Exception as e:
            logger.error(f"獲取 {data_type} 數據失敗: {e}")
            return {}
    
    async def get_stock_ohlc_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取股票 OHLC 數據"""
        try:
            # 獲取價格數據
            price_data = await self.fetch_and_cache_data('price')
            
            if not price_data or 'close' not in price_data:
                logger.warning(f"⚠️ 無法獲取 {stock_name} 價格數據")
                return None
            
            close_data = price_data['close']['data']
            if stock_id not in close_data:
                logger.warning(f"⚠️ 股票 {stock_id} 不在價格數據中")
                return None
            
            # 獲取 OHLC 數據
            stock_close = close_data[stock_id]
            latest_date = stock_close['latest_date']
            
            # 從緩存中獲取其他價格數據
            open_data = price_data.get('open', {}).get('data', {}).get(stock_id, {})
            high_data = price_data.get('high', {}).get('data', {}).get(stock_id, {})
            low_data = price_data.get('low', {}).get('data', {}).get(stock_id, {})
            volume_data = price_data.get('volume', {}).get('data', {}).get(stock_id, {})
            
            # 構建 OHLC 數據
            ohlc_data = {
                'date': latest_date,
                'close': stock_close['latest_value'],
                'open': open_data.get('latest_value', stock_close['latest_value']),
                'high': high_data.get('latest_value', stock_close['latest_value']),
                'low': low_data.get('latest_value', stock_close['latest_value']),
                'volume': volume_data.get('latest_value', 0),
                'daily_change': 0.0,
                'daily_change_pct': 0.0
            }
            
            # 計算漲跌幅
            if ohlc_data['open'] > 0:
                ohlc_data['daily_change'] = ohlc_data['close'] - ohlc_data['open']
                ohlc_data['daily_change_pct'] = (ohlc_data['daily_change'] / ohlc_data['open']) * 100
            
            logger.info(f"✅ 獲取到 {stock_name} OHLC 數據")
            return ohlc_data
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} OHLC 數據失敗: {e}")
            return None
    
    async def get_stock_revenue_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取股票營收數據"""
        try:
            # 獲取營收數據
            revenue_data = await self.fetch_and_cache_data('revenue')
            
            if not revenue_data or 'current_month' not in revenue_data:
                logger.warning(f"⚠️ 無法獲取 {stock_name} 營收數據")
                return None
            
            current_month_data = revenue_data['current_month']['data']
            if stock_id not in current_month_data:
                logger.warning(f"⚠️ 股票 {stock_id} 不在營收數據中")
                return None
            
            # 獲取營收相關數據
            stock_revenue = current_month_data[stock_id]
            latest_date = stock_revenue['latest_date']
            latest_revenue = stock_revenue['latest_value']
            
            # 從緩存中獲取增長率數據
            mom_data = revenue_data.get('mom_change_pct', {}).get('data', {}).get(stock_id, {})
            yoy_data = revenue_data.get('yoy_change_pct', {}).get('data', {}).get(stock_id, {})
            
            revenue_result = {
                'revenue': latest_revenue,
                'yoy_growth': yoy_data.get('latest_value', 0.0),
                'mom_growth': mom_data.get('latest_value', 0.0),
                'period': latest_date[:7],  # 取 YYYY-MM
                'date': latest_date
            }
            
            logger.info(f"✅ 獲取到 {stock_name} 營收數據")
            return revenue_result
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 營收數據失敗: {e}")
            return None
    
    async def get_stock_earnings_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取股票財報數據"""
        try:
            # 獲取財報數據
            earnings_data = await self.fetch_and_cache_data('earnings')
            
            if not earnings_data or 'eps' not in earnings_data:
                logger.warning(f"⚠️ 無法獲取 {stock_name} 財報數據")
                return None
            
            eps_data = earnings_data['eps']['data']
            if stock_id not in eps_data:
                logger.warning(f"⚠️ 股票 {stock_id} 不在財報數據中")
                return None
            
            # 獲取 EPS 數據
            stock_eps = eps_data[stock_id]
            latest_date = stock_eps['latest_date']
            latest_eps = stock_eps['latest_value']
            
            # 從緩存中獲取其他財報數據
            revenue_growth_data = earnings_data.get('revenue_growth', {}).get('data', {}).get(stock_id, {})
            profit_growth_data = earnings_data.get('profit_growth', {}).get('data', {}).get(stock_id, {})
            gross_margin_data = earnings_data.get('gross_margin', {}).get('data', {}).get(stock_id, {})
            net_margin_data = earnings_data.get('net_margin', {}).get('data', {}).get(stock_id, {})
            
            earnings_result = {
                'eps': latest_eps,
                'period': latest_date,
                'date': latest_date,
                'revenue_growth': revenue_growth_data.get('latest_value', 0.0),
                'profit_growth': profit_growth_data.get('latest_value', 0.0),
                'gross_margin': gross_margin_data.get('latest_value', 0.0),
                'net_margin': net_margin_data.get('latest_value', 0.0)
            }
            
            logger.info(f"✅ 獲取到 {stock_name} 財報數據")
            return earnings_result
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 財報數據失敗: {e}")
            return None
    
    def get_cache_status(self) -> Dict[str, Any]:
        """獲取緩存狀態"""
        status = {}
        
        for data_type in self.data_tables.keys():
            cache_file = self._get_cache_file_path(data_type)
            is_valid = self._is_cache_valid(data_type)
            
            status[data_type] = {
                'cache_exists': cache_file.exists(),
                'is_valid': is_valid,
                'cache_file': str(cache_file),
                'last_modified': None
            }
            
            if cache_file.exists():
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                status[data_type]['last_modified'] = mtime.isoformat()
        
        return status

async def test_finlab_cache():
    """測試 FinLab 緩存功能"""
    print("🧪 FinLab 數據緩存測試")
    print("=" * 60)
    
    try:
        cache_manager = FinLabDataCache()
        
        # 測試股票
        test_stocks = [
            ('6732', '昇佳電子'),
            ('4968', '立積'),
            ('3491', '昇達科技')
        ]
        
        print("\n📊 測試 OHLC 數據獲取:")
        for stock_id, stock_name in test_stocks:
            ohlc_data = await cache_manager.get_stock_ohlc_data(stock_id, stock_name)
            if ohlc_data:
                print(f"✅ {stock_name}: 收盤價 {ohlc_data['close']:.2f}, 漲跌幅 {ohlc_data['daily_change_pct']:.2f}%")
            else:
                print(f"❌ {stock_name}: 獲取失敗")
        
        print("\n💰 測試營收數據獲取:")
        for stock_id, stock_name in test_stocks:
            revenue_data = await cache_manager.get_stock_revenue_data(stock_id, stock_name)
            if revenue_data:
                print(f"✅ {stock_name}: 營收 {revenue_data['revenue']:,.0f}, 年增率 {revenue_data['yoy_growth']:.2f}%")
            else:
                print(f"❌ {stock_name}: 獲取失敗")
        
        print("\n📈 測試財報數據獲取:")
        for stock_id, stock_name in test_stocks:
            earnings_data = await cache_manager.get_stock_earnings_data(stock_id, stock_name)
            if earnings_data:
                print(f"✅ {stock_name}: EPS {earnings_data['eps']:.2f}, 期間 {earnings_data['period']}")
            else:
                print(f"❌ {stock_name}: 獲取失敗")
        
        print("\n📋 緩存狀態:")
        cache_status = cache_manager.get_cache_status()
        for data_type, status in cache_status.items():
            print(f"   {data_type}: {'✅ 有效' if status['is_valid'] else '❌ 無效'}")
        
        print("\n🎉 緩存測試完成！")
        
    except Exception as e:
        print(f"❌ 緩存測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_finlab_cache())
