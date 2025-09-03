"""
OHLC 數據緩存管理器
實現本地 CSV 存儲，避免重複 API 調用
"""

import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import finlab
import finlab.data as fdata

logger = logging.getLogger(__name__)

class OHLCCacheManager:
    """OHLC 數據緩存管理器"""
    
    def __init__(self, cache_dir: str = "data/cache/ohlc"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 確保 Finlab 已登入
        import os
        finlab_key = os.getenv('FINLAB_API_KEY')
        if finlab_key:
            try:
                finlab.login(finlab_key)
                logger.info("OHLC 緩存管理器：Finlab API 登入成功")
            except Exception as e:
                logger.warning(f"OHLC 緩存管理器：Finlab API 登入失敗 - {e}")
        else:
            logger.warning("OHLC 緩存管理器：未找到 FINLAB_API_KEY 環境變數")
        
        # 數據類型映射
        self.data_types = {
            'close': 'price:收盤價',
            'open': 'price:開盤價', 
            'high': 'price:最高價',
            'low': 'price:最低價',
            'volume': 'price:成交股數'
        }
        
        logger.info(f"OHLC 緩存管理器初始化完成，緩存目錄: {self.cache_dir}")
    
    def _get_cache_filename(self, data_type: str, date: str) -> Path:
        """獲取緩存文件名"""
        return self.cache_dir / f"{data_type}_{date}.csv"
    
    def _get_today_date(self) -> str:
        """獲取今日日期字符串"""
        return datetime.now().strftime('%Y%m%d')
    
    def _is_cache_valid(self, cache_file: Path, target_date: str) -> bool:
        """檢查緩存是否有效"""
        
        if not cache_file.exists():
            return False
        
        try:
            # 檢查文件修改時間
            file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            target_datetime = datetime.strptime(target_date, '%Y%m%d')
            
            # 如果是今天的數據，檢查是否在交易時間後更新
            if target_date == self._get_today_date():
                # 台股交易時間通常在 13:30 結束
                market_close = target_datetime.replace(hour=14, minute=0)
                current_time = datetime.now()
                
                # 如果現在還在交易時間內，使用緩存但標記可能需要更新
                if current_time < market_close:
                    return True
                
                # 如果交易已結束，檢查緩存是否在收盤後更新
                return file_mtime > market_close
            
            # 歷史數據，檢查文件是否存在且非空
            if cache_file.stat().st_size > 0:
                return True
                
        except Exception as e:
            logger.warning(f"緩存有效性檢查失敗: {e}")
            
        return False
    
    def _load_cache(self, data_type: str, date: str) -> Optional[pd.DataFrame]:
        """載入緩存數據"""
        
        cache_file = self._get_cache_filename(data_type, date)
        
        if not self._is_cache_valid(cache_file, date):
            return None
            
        try:
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            logger.info(f"✅ 從緩存載入 {data_type} 數據: {cache_file}")
            return df
            
        except Exception as e:
            logger.warning(f"載入緩存失敗: {e}")
            return None
    
    def _save_cache(self, data: pd.DataFrame, data_type: str, date: str):
        """保存數據到緩存"""
        
        cache_file = self._get_cache_filename(data_type, date)
        
        try:
            data.to_csv(cache_file)
            logger.info(f"💾 保存 {data_type} 數據到緩存: {cache_file}")
            
        except Exception as e:
            logger.error(f"保存緩存失敗: {e}")
    
    def _fetch_from_finlab(self, data_type: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """從 Finlab API 獲取數據"""
        
        finlab_key = self.data_types[data_type]
        logger.info(f"📡 從 Finlab API 獲取 {data_type} 數據...")
        
        # 使用不帶時間參數的版本，避免驗證碼問題
        full_data = finlab.data.get(finlab_key)
        
        # 手動篩選時間範圍
        if not full_data.empty:
            # 確保索引是 datetime 格式
            if not isinstance(full_data.index, pd.DatetimeIndex):
                full_data.index = pd.to_datetime(full_data.index)
            
            # 篩選日期範圍
            mask = (full_data.index >= start_date) & (full_data.index <= end_date)
            filtered_data = full_data.loc[mask]
            
            logger.info(f"✅ 獲取 {data_type} 數據：{len(filtered_data)} 個交易日")
            return filtered_data
        
        return full_data
    
    def get_ohlc_data(self, stock_ids: List[str], days: int = 300) -> Dict[str, pd.DataFrame]:
        """獲取 OHLC 數據（優先使用緩存）"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        today_str = self._get_today_date()
        
        result = {}
        
        for data_type in self.data_types.keys():
            # 嘗試載入緩存
            cached_data = self._load_cache(data_type, today_str)
            
            if cached_data is not None:
                # 過濾所需股票並檢查日期範圍
                available_stocks = [sid for sid in stock_ids if sid in cached_data.columns]
                
                if available_stocks:
                    # 檢查日期範圍是否足夠
                    data_start = cached_data.index.min()
                    if data_start <= start_date:
                        # 緩存數據充足，直接使用
                        filtered_data = cached_data[available_stocks]
                        filtered_data = filtered_data[filtered_data.index >= start_date]
                        result[data_type] = filtered_data
                        
                        logger.info(f"✅ 使用緩存 {data_type} 數據，股票: {available_stocks}")
                        continue
            
            # 緩存不足，從 API 獲取
            logger.info(f"📡 緩存不足，從 API 獲取 {data_type} 數據...")
            
            try:
                api_data = self._fetch_from_finlab(data_type, start_date, end_date)
                
                # 保存到緩存
                self._save_cache(api_data, data_type, today_str)
                
                # 過濾所需股票
                available_stocks = [sid for sid in stock_ids if sid in api_data.columns]
                if available_stocks:
                    result[data_type] = api_data[available_stocks]
                    logger.info(f"✅ API 獲取 {data_type} 數據成功，股票: {available_stocks}")
                else:
                    logger.warning(f"⚠️ {data_type} 數據中無所需股票: {stock_ids}")
                    
            except Exception as e:
                logger.error(f"從 API 獲取 {data_type} 數據失敗: {e}")
                result[data_type] = pd.DataFrame()
        
        return result
    
    def get_stock_ohlc(self, stock_id: str, days: int = 300) -> Optional[pd.DataFrame]:
        """獲取單一股票的完整 OHLC 數據"""
        
        ohlc_data = self.get_ohlc_data([stock_id], days)
        
        if not all(data_type in ohlc_data for data_type in self.data_types.keys()):
            logger.error(f"無法獲取 {stock_id} 的完整 OHLC 數據")
            return None
        
        try:
            # 組合成完整的 OHLC DataFrame
            df = pd.DataFrame({
                'open': ohlc_data['open'][stock_id] if stock_id in ohlc_data['open'].columns else pd.Series(),
                'high': ohlc_data['high'][stock_id] if stock_id in ohlc_data['high'].columns else pd.Series(),
                'low': ohlc_data['low'][stock_id] if stock_id in ohlc_data['low'].columns else pd.Series(),
                'close': ohlc_data['close'][stock_id] if stock_id in ohlc_data['close'].columns else pd.Series(),
                'volume': ohlc_data['volume'][stock_id] if stock_id in ohlc_data['volume'].columns else pd.Series()
            })
            
            # 移除空值行
            df = df.dropna()
            
            if len(df) == 0:
                logger.warning(f"⚠️ {stock_id} 無有效數據")
                return None
                
            logger.info(f"✅ 成功獲取 {stock_id} OHLC 數據: {len(df)} 個交易日")
            return df
            
        except Exception as e:
            logger.error(f"組合 {stock_id} OHLC 數據失敗: {e}")
            return None
    
    def clear_old_cache(self, days_to_keep: int = 7):
        """清理舊緩存文件"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for cache_file in self.cache_dir.glob("*.csv"):
                file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    cache_file.unlink()
                    logger.info(f"🗑️ 清理舊緩存: {cache_file}")
                    
        except Exception as e:
            logger.error(f"清理緩存失敗: {e}")
    
    def get_cache_status(self) -> Dict[str, any]:
        """獲取緩存狀態"""
        
        status = {
            'cache_dir': str(self.cache_dir),
            'cache_files': [],
            'total_size_mb': 0
        }
        
        try:
            total_size = 0
            for cache_file in self.cache_dir.glob("*.csv"):
                file_size = cache_file.stat().st_size
                file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                
                status['cache_files'].append({
                    'filename': cache_file.name,
                    'size_mb': round(file_size / 1024 / 1024, 2),
                    'modified': file_mtime.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                total_size += file_size
            
            status['total_size_mb'] = round(total_size / 1024 / 1024, 2)
            status['file_count'] = len(status['cache_files'])
            
        except Exception as e:
            logger.error(f"獲取緩存狀態失敗: {e}")
        
        return status

def create_ohlc_cache_manager(cache_dir: str = "data/cache/ohlc") -> OHLCCacheManager:
    """創建 OHLC 緩存管理器"""
    return OHLCCacheManager(cache_dir)
