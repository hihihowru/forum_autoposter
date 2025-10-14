"""
股票價格驗證模組
用於驗證觸發器類型與實際股價表現是否相符
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class StockPriceValidator:
    """股票價格驗證器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("股票價格驗證器初始化完成")
    
    def validate_trigger_type(self, 
                            stock_code: str, 
                            stock_name: str, 
                            trigger_type: str, 
                            actual_price_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        驗證觸發器類型與實際股價表現是否相符
        
        Args:
            stock_code: 股票代碼
            stock_name: 股票名稱
            trigger_type: 觸發器類型
            actual_price_data: 實際股價數據
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否相符, 驗證結果訊息, 建議的觸發器類型)
        """
        try:
            self.logger.info(f"🔍 開始驗證觸發器類型: {stock_code} - {trigger_type}")
            
            # 提取股價數據
            current_price = actual_price_data.get('current_price', 0)
            change_amount = actual_price_data.get('change_amount', 0)
            change_percentage = actual_price_data.get('change_percentage', 0)
            is_limit_up = actual_price_data.get('is_limit_up', False)
            is_limit_down = actual_price_data.get('is_limit_down', False)
            
            self.logger.info(f"📊 股價數據: 價格={current_price}, 漲跌={change_amount}, 漲跌幅={change_percentage}%")
            self.logger.info(f"📊 漲停狀態: {is_limit_up}, 跌停狀態: {is_limit_down}")
            
            # 根據觸發器類型進行驗證
            if trigger_type == 'intraday_limit_up':
                return self._validate_limit_up_trigger(
                    stock_code, stock_name, change_percentage, is_limit_up, change_amount
                )
            elif trigger_type == 'limit_up_after_hours':
                return self._validate_limit_up_trigger(
                    stock_code, stock_name, change_percentage, is_limit_up, change_amount
                )
            elif trigger_type == 'intraday_limit_down':
                return self._validate_limit_down_trigger(
                    stock_code, stock_name, change_percentage, is_limit_down, change_amount
                )
            elif trigger_type == 'limit_down_after_hours':
                return self._validate_limit_down_trigger(
                    stock_code, stock_name, change_percentage, is_limit_down, change_amount
                )
            elif trigger_type == 'volume_surge':
                return self._validate_volume_surge_trigger(
                    stock_code, stock_name, actual_price_data
                )
            else:
                # 未知觸發器類型，預設通過
                return True, f"未知觸發器類型 {trigger_type}，預設通過驗證", None
                
        except Exception as e:
            self.logger.error(f"❌ 觸發器類型驗證失敗: {e}")
            return False, f"驗證過程發生錯誤: {str(e)}", None
    
    def _validate_limit_up_trigger(self, 
                                 stock_code: str, 
                                 stock_name: str, 
                                 change_percentage: float, 
                                 is_limit_up: bool, 
                                 change_amount: float) -> Tuple[bool, str, Optional[str]]:
        """驗證漲停觸發器"""
        
        # 檢查是否真的漲停
        if is_limit_up:
            return True, f"{stock_name}({stock_code}) 確實漲停，觸發器類型正確", None
        
        # 檢查漲幅是否為正
        if change_percentage > 0:
            if change_percentage >= 9.5:  # 接近漲停
                return True, f"{stock_name}({stock_code}) 漲幅 {change_percentage}%，接近漲停", None
            else:
                return False, f"{stock_name}({stock_code}) 漲幅僅 {change_percentage}%，不符合漲停觸發器", "volume_surge"
        
        # 如果是下跌，建議使用跌停觸發器
        elif change_percentage < 0:
            if change_percentage <= -9.5:  # 接近跌停
                return False, f"{stock_name}({stock_code}) 跌幅 {change_percentage}%，應使用跌停觸發器", "intraday_limit_down"
            else:
                return False, f"{stock_name}({stock_code}) 下跌 {change_percentage}%，不適合漲停觸發器", "volume_surge"
        
        # 平盤
        else:
            return False, f"{stock_name}({stock_code}) 平盤，不適合漲停觸發器", "volume_surge"
    
    def _validate_limit_down_trigger(self, 
                                   stock_code: str, 
                                   stock_name: str, 
                                   change_percentage: float, 
                                   is_limit_down: bool, 
                                   change_amount: float) -> Tuple[bool, str, Optional[str]]:
        """驗證跌停觸發器"""
        
        # 檢查是否真的跌停
        if is_limit_down:
            return True, f"{stock_name}({stock_code}) 確實跌停，觸發器類型正確", None
        
        # 檢查跌幅是否為負
        if change_percentage < 0:
            if change_percentage <= -9.5:  # 接近跌停
                return True, f"{stock_name}({stock_code}) 跌幅 {change_percentage}%，接近跌停", None
            else:
                return False, f"{stock_name}({stock_code}) 跌幅僅 {change_percentage}%，不符合跌停觸發器", "volume_surge"
        
        # 如果是上漲，建議使用漲停觸發器
        elif change_percentage > 0:
            if change_percentage >= 9.5:  # 接近漲停
                return False, f"{stock_name}({stock_code}) 漲幅 {change_percentage}%，應使用漲停觸發器", "intraday_limit_up"
            else:
                return False, f"{stock_name}({stock_code}) 上漲 {change_percentage}%，不適合跌停觸發器", "volume_surge"
        
        # 平盤
        else:
            return False, f"{stock_name}({stock_code}) 平盤，不適合跌停觸發器", "volume_surge"
    
    def _validate_volume_surge_trigger(self, 
                                     stock_code: str, 
                                     stock_name: str, 
                                     price_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """驗證成交量激增觸發器"""
        
        volume_ratio = price_data.get('volume_ratio', 1.0)
        current_volume = price_data.get('current_volume', 0)
        avg_volume = price_data.get('avg_volume', 0)
        
        if volume_ratio >= 2.0:  # 成交量是平均的2倍以上
            return True, f"{stock_name}({stock_code}) 成交量激增 {volume_ratio:.1f}倍，觸發器類型正確", None
        elif volume_ratio >= 1.5:
            return True, f"{stock_name}({stock_code}) 成交量增加 {volume_ratio:.1f}倍，符合激增標準", None
        else:
            return False, f"{stock_name}({stock_code}) 成交量僅 {volume_ratio:.1f}倍，不符合激增標準", None
    
    def get_corrected_news_keywords(self, 
                                  stock_code: str, 
                                  stock_name: str, 
                                  trigger_type: str, 
                                  actual_price_data: Dict[str, Any]) -> list:
        """
        根據實際股價表現獲取正確的新聞搜尋關鍵字
        
        Args:
            stock_code: 股票代碼
            stock_name: 股票名稱
            trigger_type: 觸發器類型
            actual_price_data: 實際股價數據
            
        Returns:
            list: 修正後的新聞搜尋關鍵字列表
        """
        try:
            change_percentage = actual_price_data.get('change_percentage', 0)
            is_limit_up = actual_price_data.get('is_limit_up', False)
            is_limit_down = actual_price_data.get('is_limit_down', False)
            
            # 基礎關鍵字
            base_keywords = [
                {"type": "stock_name", "keyword": stock_name},
                {"type": "stock_code", "keyword": stock_code}
            ]
            
            # 根據實際股價表現調整關鍵字
            if is_limit_up or change_percentage >= 9.5:
                # 確實漲停或接近漲停
                trigger_keyword = "漲停"
                reason_keywords = ["漲停", "原因", "利多", "消息", "突破"]
            elif is_limit_down or change_percentage <= -9.5:
                # 確實跌停或接近跌停
                trigger_keyword = "跌停"
                reason_keywords = ["跌停", "原因", "利空", "消息", "下跌"]
            elif change_percentage > 0:
                # 上漲但未漲停
                trigger_keyword = "上漲"
                reason_keywords = ["上漲", "原因", "利多", "消息", "表現"]
            elif change_percentage < 0:
                # 下跌但未跌停
                trigger_keyword = "下跌"
                reason_keywords = ["下跌", "原因", "利空", "消息", "表現"]
            else:
                # 平盤
                trigger_keyword = "表現"
                reason_keywords = ["表現", "分析", "消息", "財報", "營收"]
            
            # 添加觸發器關鍵字
            base_keywords.append({"type": "trigger_keyword", "keyword": trigger_keyword})
            
            # 添加原因分析關鍵字
            for reason in reason_keywords:
                base_keywords.append({"type": "reason_analysis", "keyword": reason})
            
            self.logger.info(f"📝 修正後的新聞關鍵字: {[kw['keyword'] for kw in base_keywords]}")
            return base_keywords
            
        except Exception as e:
            self.logger.error(f"❌ 獲取修正新聞關鍵字失敗: {e}")
            # 返回預設關鍵字
            return [
                {"type": "stock_name", "keyword": stock_name},
                {"type": "stock_code", "keyword": stock_code},
                {"type": "trigger_keyword", "keyword": "表現"}
            ]

# 創建全局實例
stock_price_validator = StockPriceValidator()




