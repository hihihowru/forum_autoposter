"""
漲停資料解析器
解析你提供的漲停排行資料
"""

import re
from typing import Dict, List, Any, Optional

class LimitUpDataParser:
    """漲停資料解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.stock_data_map = {}
    
    def parse_limit_up_data(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        解析漲停排行資料
        
        Args:
            raw_data: 原始漲停排行資料文字
            
        Returns:
            解析後的股票資料列表
        """
        try:
            lines = raw_data.strip().split('\n')
            stock_data_list = []
            
            for line in lines:
                # 跳過標題行和空行
                if not line.strip() or '名次' in line or '資料時間' in line or '漲幅排行' in line:
                    continue
                
                # 解析股票資料行
                stock_data = self._parse_stock_line(line)
                if stock_data:
                    stock_data_list.append(stock_data)
            
            # 建立股票代號到資料的映射
            for stock_data in stock_data_list:
                stock_id = stock_data.get('stock_id', '')
                if stock_id:
                    self.stock_data_map[stock_id] = stock_data
            
            return stock_data_list
            
        except Exception as e:
            print(f"解析漲停資料失敗: {e}")
            return []
    
    def _parse_stock_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析單行股票資料"""
        try:
            # 使用正則表達式解析
            # 格式: 名次 股名/股號 股價 漲跌 漲跌幅(%) 最高 最低 價差 成交量(張) 成交金額(億)
            
            # 移除多餘空格
            line = re.sub(r'\s+', ' ', line.strip())
            
            # 分割欄位
            parts = line.split(' ')
            
            if len(parts) < 10:
                return None
            
            # 解析各欄位
            rank = int(parts[0])
            stock_name_code = parts[1]
            current_price = float(parts[2])
            change_amount = float(parts[3])
            change_percent = float(parts[4].replace('%', ''))
            high_price = float(parts[5])
            low_price = float(parts[6])
            price_range = float(parts[7])
            volume = int(parts[8].replace(',', ''))
            turnover = float(parts[9])
            
            # 解析股名和股號
            stock_name, stock_id = self._parse_stock_name_code(stock_name_code)
            
            stock_data = {
                'rank': rank,
                'stock_name': stock_name,
                'stock_id': stock_id,
                'current_price': current_price,
                'change_amount': change_amount,
                'change_percent': change_percent,
                'high_price': high_price,
                'low_price': low_price,
                'price_range': price_range,
                'volume': volume,
                'turnover': turnover,
                'is_limit_up': change_percent >= 9.8
            }
            
            return stock_data
            
        except Exception as e:
            print(f"解析股票行失敗: {line} - {e}")
            return None
    
    def _parse_stock_name_code(self, stock_name_code: str) -> tuple[str, str]:
        """解析股名和股號"""
        try:
            # 格式: "仲琦 2419.TW" 或 "越峰 8121.TWO"
            if '.' in stock_name_code:
                # 包含交易所代號
                parts = stock_name_code.split(' ')
                if len(parts) >= 2:
                    stock_name = parts[0]
                    stock_code = parts[1]
                    # 提取純數字股號
                    stock_id = stock_code.split('.')[0]
                    return stock_name, stock_id
            
            # 如果沒有交易所代號，嘗試其他格式
            parts = stock_name_code.split(' ')
            if len(parts) >= 2:
                stock_name = parts[0]
                stock_id = parts[1]
                return stock_name, stock_id
            
            return stock_name_code, ""
            
        except Exception as e:
            print(f"解析股名股號失敗: {stock_name_code} - {e}")
            return stock_name_code, ""
    
    def get_stock_data(self, stock_id: str) -> Optional[Dict[str, Any]]:
        """根據股票代號獲取資料"""
        return self.stock_data_map.get(stock_id)
    
    def get_limit_up_stocks(self) -> List[Dict[str, Any]]:
        """獲取所有漲停股票"""
        return [data for data in self.stock_data_map.values() if data.get('is_limit_up', False)]
    
    def get_stock_ids(self) -> List[str]:
        """獲取所有股票代號"""
        return list(self.stock_data_map.keys())

# 測試函數
def test_limit_up_parser():
    """測試漲停資料解析器"""
    
    # 你提供的漲停資料
    raw_data = """
漲幅排行
資料時間：2025/09/03
名次
股名/股號
股價
漲跌
漲跌幅(%)
最高
最低
價差
成交量(張)
成交金額(億)
1
仲琦
2419.TW
25.30
2.30
10.00%
25.30
23.20
2.10
3,149
0.7833
2
越峰
8121.TWO
25.30
2.30
10.00%
25.30
23.40
1.90
1,471
0.3685
3
昇佳電子
6732.TWO
198.50
18.00
9.97%
198.50
188.00
10.50
250
0.4908
4
東友
5438.TWO
28.15
2.55
9.96%
28.15
26.10
2.05
10,423
2.8571
5
如興
4414.TW
11.60
1.05
9.95%
11.60
11.60
0.00
168
0.0195
"""
    
    parser = LimitUpDataParser()
    stock_data_list = parser.parse_limit_up_data(raw_data)
    
    print("解析結果:")
    for stock_data in stock_data_list:
        print(f"  {stock_data['stock_name']} ({stock_data['stock_id']}) - 漲幅 {stock_data['change_percent']}%")
    
    print(f"\n總共解析 {len(stock_data_list)} 檔股票")
    print(f"漲停股票: {len(parser.get_limit_up_stocks())} 檔")

if __name__ == "__main__":
    test_limit_up_parser()
