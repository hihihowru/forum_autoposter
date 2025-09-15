# 動態Prompting系統

## 🎯 系統目標

解決原有prompting系統的問題，根據不同的資料類型和股票標籤來設計差異化的內容生成策略，避免內容重複，提升KOL個性化表現。

## 🔍 問題分析

### 原有系統的問題
1. **內容重複性**：所有KOL使用相同的prompting模板
2. **缺乏針對性**：沒有根據股票類型調整分析角度
3. **數據利用不足**：沒有根據可用數據類型調整分析深度
4. **情境適應性差**：沒有根據市場情境調整內容重點

### 解決方案
設計一個動態prompting系統，根據以下維度自動調整prompting策略：
- 股票類型（科技股、金融股、傳產股等）
- 數據類型（OHLC、財務、營收、技術分析等）
- 市場情境（大盤分析、財報分析、產業趨勢等）
- KOL人設（技術派、總經派、新聞派、籌碼派、情緒派）

## 🏗️ 系統架構

### 核心組件

#### 1. 動態系統提示詞生成器 (`_build_dynamic_system_prompt`)
```python
def _build_dynamic_system_prompt(self, request: ContentRequest, kol_config: Dict[str, str], market_data: Optional[Dict[str, Any]]) -> str:
    # 基礎角色設定
    base_prompt = f"你是 {request.kol_nickname}，一個專業的 {request.kol_persona}..."
    
    # 根據股票類型調整內容風格
    stock_type_prompt = self._get_stock_type_prompt(market_data)
    
    # 根據數據類型調整分析深度
    data_type_prompt = self._get_data_type_prompt(market_data)
    
    # 根據市場情境調整內容重點
    market_context_prompt = self._get_market_context_prompt(request, market_data)
    
    # 根據KOL人設調整專業角度
    persona_specific_prompt = self._get_persona_specific_prompt(request.kol_persona, market_data)
    
    # 組合所有提示詞
    return full_prompt
```

#### 2. 動態用戶提示詞生成器 (`_build_dynamic_user_prompt`)
```python
def _build_dynamic_user_prompt(self, request: ContentRequest, title: str, market_data: Optional[Dict[str, Any]]) -> str:
    # 基礎提示詞
    base_prompt = f"標題：{title}\n話題：{request.topic_title}..."
    
    # 股票特定資訊
    stock_specific = self._get_stock_specific_prompt(market_data)
    
    # 數據特定資訊
    data_specific = self._get_data_specific_prompt(market_data)
    
    # 市場特定資訊
    market_specific = self._get_market_specific_prompt(request, market_data)
    
    # 組合完整提示詞
    return full_prompt
```

## 📊 差異化策略

### 1. 股票類型差異化

#### 科技股
- **重點分析**：技術創新、產品週期、市場競爭
- **用詞風格**：技術導向、創新思維、前瞻性
- **分析角度**：研發投入、專利技術、供應鏈地位
- **風險提醒**：技術迭代、市場變化、競爭加劇

#### 金融股
- **重點分析**：政策環境、利率變化、監管要求
- **用詞風格**：穩健務實、風險意識、合規導向
- **分析角度**：資本充足率、壞帳率、淨利差
- **風險提醒**：政策風險、信用風險、市場風險

#### 傳產股
- **重點分析**：產業週期、供需關係、成本結構
- **用詞風格**：務實穩健、產業經驗、長期思維
- **分析角度**：產能利用率、原物料成本、訂單能見度
- **風險提醒**：景氣循環、成本波動、競爭加劇

### 2. 數據類型差異化

#### OHLC數據
- **重點關注**：價格趨勢、成交量變化、支撐阻力位
- **技術指標**：移動平均線、RSI、MACD等
- **分析角度**：趨勢判斷、轉折點識別、量價關係

#### 財務數據
- **重點關注**：營收成長、獲利能力、財務結構
- **關鍵指標**：本益比、ROE、負債比率等
- **分析角度**：基本面評估、成長性分析、風險評估

#### 營收數據
- **重點關注**：月營收、年增率、月增率
- **趨勢分析**：營收動能、季節性、成長性
- **分析角度**：營收品質、成長動能、產業地位

#### 技術分析數據
- **重點關注**：技術指標、圖表形態、趨勢線
- **分析工具**：K線、均線、指標等
- **分析角度**：技術面判斷、進出場時機、風險控制

### 3. 市場情境差異化

#### 大盤指數分析
- **重點分析**：大盤趨勢、市場情緒、資金流向
- **用詞風格**：宏觀視角、市場觀測、趨勢判斷
- **分析角度**：技術面、籌碼面、消息面
- **個股關聯**：分析個股與大盤的相關性

#### 財報法說分析
- **重點分析**：財報數據、法說重點、未來展望
- **用詞風格**：數據導向、專業分析、前瞻性
- **分析角度**：營收獲利、產業趨勢、競爭優勢
- **風險提醒**：財報風險、展望不確定性

#### 產業趨勢分析
- **重點分析**：產業發展、技術演進、市場變化
- **用詞風格**：產業視角、趨勢觀察、前瞻思維
- **分析角度**：產業週期、競爭格局、成長動能
- **個股關聯**：分析個股在產業中的定位

### 4. KOL人設差異化

#### 技術派
- **分析重點**：技術指標、圖表形態、趨勢分析
- **用詞特色**：技術術語、指標解讀、趨勢判斷
- **內容結構**：技術分析 → 趨勢判斷 → 風險提醒
- **專業展現**：使用專業技術指標，展現技術分析能力

#### 總經派
- **分析重點**：宏觀經濟、政策影響、產業趨勢
- **用詞特色**：經濟術語、政策解讀、趨勢分析
- **內容結構**：宏觀分析 → 政策影響 → 產業展望
- **專業展現**：結合經濟數據，展現宏觀分析能力

#### 新聞派
- **分析重點**：新聞事件、市場反應、影響評估
- **用詞特色**：即時性、新聞敏感度、影響分析
- **內容結構**：新聞解讀 → 市場影響 → 後續觀察
- **專業展現**：快速反應市場變化，展現新聞分析能力

#### 籌碼派
- **分析重點**：資金流向、主力動向、籌碼分布
- **用詞特色**：籌碼術語、資金分析、主力追蹤
- **內容結構**：籌碼分析 → 資金流向 → 主力動向
- **專業展現**：分析籌碼變化，展現資金追蹤能力

#### 情緒派
- **分析重點**：市場情緒、投資心理、群眾行為
- **用詞特色**：情緒描述、心理分析、行為解讀
- **內容結構**：情緒分析 → 心理解讀 → 行為預測
- **專業展現**：分析市場心理，展現情緒分析能力

## 🚀 使用方式

### 基本用法
```python
from src.services.content.content_generator import ContentGenerator, ContentRequest

# 創建內容生成器
generator = ContentGenerator()

# 準備市場數據
market_data = {
    "has_stock": True,
    "stock_id": "2330",
    "stock_name": "台積電",
    "stock_type": "科技股",
    "stock_data": {
        "has_ohlc": True,
        "has_analysis": True
    }
}

# 創建內容請求
request = ContentRequest(
    topic_title="台積電技術面分析",
    topic_keywords="台積電, 技術分析, 半導體",
    kol_persona="技術派",
    kol_nickname="技術大師",
    content_type="technical_analysis",
    market_data=market_data
)

# 生成內容
content = generator.generate_content(request, "台積電技術分析")
```

### 數據結構示例

#### 科技股 + OHLC數據
```python
tech_stock_data = {
    "has_stock": True,
    "stock_id": "2330",
    "stock_name": "台積電",
    "stock_type": "科技股",
    "stock_data": {
        "has_ohlc": True,
        "ohlc_data": [
            {"close": 850, "volume": 50000},
            {"close": 860, "volume": 52000}
        ],
        "has_analysis": True,
        "analysis_data": {
            "technical_indicators": {"rsi": 65.5, "ma20": 845.0}
        }
    }
}
```

#### 金融股 + 財務數據
```python
finance_stock_data = {
    "has_stock": True,
    "stock_id": "2881",
    "stock_name": "富邦金",
    "stock_type": "金融股",
    "stock_data": {
        "has_financial": True,
        "financial_data": {
            "pe_ratio": 12.5,
            "roe": 15.2,
            "revenue": 50000000000
        },
        "has_revenue": True,
        "revenue_data": {
            "current_month_revenue": 4500000000,
            "year_over_year_growth": 8.5,
            "month_over_month_growth": 2.1
        }
    }
}
```

## 📈 系統優勢

### 1. 內容差異化
- 每個KOL都有獨特的內容風格
- 避免內容重複和模板化
- 提升用戶體驗和互動率

### 2. 專業針對性
- 根據數據類型調整分析深度
- 充分利用可用的市場數據
- 提供更專業和準確的分析

### 3. 情境適應性
- 根據市場情境調整內容重點
- 適應不同的分析需求
- 提升內容的時效性和相關性

### 4. 股票特化性
- 根據股票類型調整分析角度
- 針對不同產業提供專業見解
- 提升分析的準確性和實用性

### 5. 避免重複性
- 每個組合都會產生不同的內容
- 解決原有系統的內容重複問題
- 提升KOL系統的整體品質

## 🔧 技術實現

### 核心方法
- `_build_dynamic_system_prompt()`: 動態構建系統提示詞
- `_build_dynamic_user_prompt()`: 動態構建用戶提示詞
- `_get_stock_type_prompt()`: 根據股票類型生成提示詞
- `_get_data_type_prompt()`: 根據數據類型生成提示詞
- `_get_market_context_prompt()`: 根據市場情境生成提示詞
- `_get_persona_specific_prompt()`: 根據KOL人設生成提示詞

### 擴展性
- 支持新增股票類型
- 支持新增數據類型
- 支持新增市場情境
- 支持新增KOL人設

## 📝 未來改進

### 短期目標
1. 優化提示詞模板
2. 增加更多股票類型支持
3. 完善數據類型識別

### 長期目標
1. 機器學習優化提示詞
2. 動態調整生成策略
3. 個性化學習和適應

## 🎉 總結

動態Prompting系統通過多維度的差異化策略，成功解決了原有系統的內容重複問題，為每個KOL提供了獨特且專業的內容生成能力。系統的靈活性和擴展性為未來的功能增強奠定了堅實的基礎。











