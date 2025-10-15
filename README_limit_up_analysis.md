# 台股漲停家數分析工具

這是一個獨立的 Python 工具，用於分析台股過去一年的每日漲停家數。使用 FinLab API 獲取股票數據，並計算每日漲停家數（9.5%以上視為漲停）。

## 功能特色

- 📊 分析過去一年台股每日漲停家數
- 🎯 9.5%以上漲幅視為漲停（可調整）
- 📈 提供詳細統計數據（最大值、平均值、中位數等）
- 💾 自動保存分析結果為 JSON 格式
- 📅 僅分析交易日，排除週末和假日
- 🔍 提供每日詳細數據，包含漲停股票清單

## 安裝需求

### 1. 安裝 Python 套件

```bash
pip install -r requirements_limit_up.txt
```

### 2. 設定 FinLab API 金鑰

設定環境變數：

```bash
export FINLAB_API_KEY="your_finlab_api_key_here"
```

或在程式中直接傳入：

```python
analyzer = LimitUpAnalyzer(api_key="your_finlab_api_key_here")
```

## 使用方法

### 基本使用

```bash
python limit_up_analysis.py
```

### 程式化使用

```python
from limit_up_analysis import LimitUpAnalyzer

# 創建分析器
analyzer = LimitUpAnalyzer()

# 分析過去一年的漲停家數
result = analyzer.analyze_limit_up_trend(days=365)

# 印出摘要
analyzer.print_summary(result)

# 保存結果
analyzer.save_results(result, "my_analysis.json")
```

### 自訂分析期間

```python
# 分析過去 30 天
result = analyzer.analyze_limit_up_trend(days=30)

# 分析過去 180 天
result = analyzer.analyze_limit_up_trend(days=180)
```

## 輸出結果

### 控制台輸出

```
============================================================
📊 台股漲停家數分析報告
============================================================
📅 分析期間: 2023-01-01 到 2024-01-01
📈 漲停閾值: 9.5%
📊 總交易日: 250 天

📈 統計數據:
   - 有漲停股票的交易日: 180 天
   - 最大漲停家數: 45 家
   - 最小漲停家數: 0 家
   - 平均漲停家數: 12.34 家
   - 中位數漲停家數: 8.00 家
   - 標準差: 8.76

📊 最近10天漲停家數:
   2024-01-15: 15 家
   2024-01-16: 8 家
   2024-01-17: 22 家
   ...
============================================================
```

### JSON 輸出格式

```json
{
  "analysis_period": {
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "total_days": 250
  },
  "limit_up_threshold": 9.5,
  "daily_limit_up_counts": [15, 8, 22, ...],
  "trading_dates": ["2023-01-01", "2023-01-02", ...],
  "statistics": {
    "total_limit_up_days": 180,
    "max_limit_up_count": 45,
    "min_limit_up_count": 0,
    "avg_limit_up_count": 12.34,
    "median_limit_up_count": 8.0,
    "std_limit_up_count": 8.76
  },
  "detailed_data": [
    {
      "date": "2023-01-01",
      "limit_up_count": 15,
      "total_stocks": 1800,
      "limit_up_stocks": ["2330", "2454", ...]
    },
    ...
  ]
}
```

## 主要類別和方法

### LimitUpAnalyzer 類別

#### 初始化
```python
analyzer = LimitUpAnalyzer(api_key="your_api_key")
```

#### 主要方法

- `analyze_limit_up_trend(days=365)`: 分析指定天數的漲停家數趨勢
- `get_daily_price_data(date)`: 獲取指定日期的股票價格數據
- `count_limit_up_stocks(daily_data)`: 計算漲停家數
- `get_trading_dates(start_date, end_date)`: 獲取交易日列表
- `print_summary(result)`: 印出分析摘要
- `save_results(result, filename)`: 保存分析結果

## 漲停定義

- **漲停閾值**: 9.5%以上漲幅視為漲停
- **計算方式**: (收盤價 - 開盤價) / 開盤價 * 100 >= 9.5%
- **數據來源**: FinLab API 的開盤價和收盤價數據

## 注意事項

1. **API 限制**: 需要有效的 FinLab API 金鑰
2. **數據範圍**: 僅分析台股市場數據
3. **交易日**: 自動排除週末和國定假日
4. **數據品質**: 依賴 FinLab API 的數據品質和完整性
5. **執行時間**: 分析一年數據約需 5-10 分鐘（取決於網路速度）

## 錯誤處理

程式包含完整的錯誤處理機制：

- API 連接失敗會顯示錯誤訊息
- 數據缺失會跳過該日期
- 檔案保存失敗會記錄錯誤
- 所有錯誤都會記錄到日誌中

## 範例輸出

執行後會得到兩個主要結果：

1. **漲停家數數列**: 過去一年每個交易日的漲停家數
2. **統計摘要**: 包含最大值、平均值、中位數等統計數據

```python
# 範例：獲取漲停家數數列
limit_up_counts = [15, 8, 22, 5, 18, ...]  # 每日漲停家數
trading_dates = ["2023-01-01", "2023-01-02", ...]  # 對應日期
```

## 技術細節

- **語言**: Python 3.7+
- **主要套件**: pandas, numpy, finlab
- **數據格式**: JSON 輸出，支援中文
- **記憶體使用**: 約 100-200MB（取決於分析期間）
- **網路需求**: 需要穩定的網路連接以訪問 FinLab API

## 授權

此工具僅供學習和研究使用，請遵守 FinLab API 的使用條款。


