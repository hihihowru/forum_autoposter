# Serper API 統一整合 PRD

## 📋 產品需求文檔 (PRD)

### 🎯 產品概述

**產品名稱**: Serper API 統一整合系統 (Unified Serper API Integration System)  
**版本**: v1.0  
**創建日期**: 2025-01-15  
**負責人**: AI Assistant  

### 🔍 背景與問題

#### 現有問題
1. **重複實現**: 多個 `SerperNewsClient` 類別分散在不同檔案中
2. **功能重複**: 相同的搜尋功能在多個地方重複實現
3. **缺乏統一管理**: 沒有統一的 API 調用、錯誤處理和監控
4. **關鍵字策略單一**: 所有搜尋都使用固定的關鍵字策略
5. **結果處理不一致**: 不同實現對搜尋結果的處理方式不同

#### 受影響的檔案
- `generate_kangpei_posts_v2.py`
- `generate_kangpei_posts_v3.py` 
- `generate_kangpei_posts_v4.py`
- `generate_kangpei_posts_v6.py`
- `smart_limit_up_generator.py`
- `src/agents/multi_level_search_strategy.py`

#### 業務影響
- 維護成本高，需要同時維護多個重複的實現
- 功能不一致，可能導致搜尋結果品質差異
- 缺乏統一監控，難以追蹤 API 使用情況
- 擴展困難，新增功能需要在多個地方修改

### 🎯 產品目標

#### 主要目標
1. **統一 API 調用**: 建立統一的 Serper API 調用介面
2. **智能關鍵字優化**: 實現動態關鍵字生成和優化
3. **結果處理標準化**: 統一搜尋結果的處理和增強邏輯
4. **監控和管理**: 實現 API 使用量監控和錯誤處理

#### 成功指標
- 代碼重複率降低 90%
- API 調用統一性 100%
- 搜尋結果處理一致性 100%
- 維護成本降低 70%

### 🏗️ 系統架構設計

#### 核心組件

##### 1. 統一 Serper 客戶端
```
UnifiedSerperClient
├── API 調用管理
├── 錯誤處理和重試
├── 使用量監控
├── 結果快取
└── 配置管理
```

##### 2. 智能搜尋引擎
```
IntelligentSearchEngine
├── 關鍵字生成器
├── 搜尋策略選擇器
├── 結果分析器
├── 相關性評分器
└── 內容增強器
```

##### 3. 搜尋策略管理器
```
SearchStrategyManager
├── TrendingTopicStrategy
├── LimitUpStrategy
├── NewsEventStrategy
├── CustomStockStrategy
└── EarningsReportStrategy
```

### 📝 功能需求

#### 功能 1: 統一 Serper 客戶端

##### 1.1 API 調用管理
**目標**: 提供統一的 Serper API 調用介面

**功能描述**:
- 統一的 API 端點配置
- 標準化的請求格式
- 統一的響應處理
- 支援多種搜尋類型

**API 介面設計**:
```python
class UnifiedSerperClient:
    def __init__(self, api_key: str, config: SerperConfig)
    
    async def search_news(self, query: str, params: SearchParams) -> SearchResult
    async def search_web(self, query: str, params: SearchParams) -> SearchResult
    async def search_images(self, query: str, params: SearchParams) -> SearchResult
    
    def get_usage_stats(self) -> UsageStats
    def get_error_logs(self) -> List[ErrorLog]
```

##### 1.2 錯誤處理和重試
**目標**: 實現健壯的錯誤處理和自動重試機制

**功能描述**:
- 自動重試機制 (最多3次)
- 指數退避策略
- 錯誤分類和處理
- 降級策略

**錯誤處理策略**:
```
API 限制錯誤 (429):
- 等待 60 秒後重試
- 最多重試 3 次
- 記錄使用量統計

網路錯誤 (5xx):
- 立即重試
- 最多重試 3 次
- 使用指數退避

認證錯誤 (401):
- 不重試
- 立即記錄錯誤
- 通知管理員
```

##### 1.3 使用量監控
**目標**: 監控 API 使用量並提供預警

**功能描述**:
- 實時使用量追蹤
- 每日/每月使用量統計
- 使用量預警機制
- 成本分析

#### 功能 2: 智能搜尋引擎

##### 2.1 關鍵字生成器
**目標**: 根據不同觸發器類型生成最優關鍵字

**功能描述**:
- 觸發器專用關鍵字策略
- LLM 輔助關鍵字生成
- 關鍵字相關性分析
- 動態關鍵字調整

**關鍵字生成策略**:
```python
class KeywordGenerator:
    def generate_trending_topic_keywords(self, topic: str) -> List[str]
    def generate_limit_up_keywords(self, stock: StockInfo) -> List[str]
    def generate_news_event_keywords(self, event: NewsEvent) -> List[str]
    def optimize_keywords(self, keywords: List[str], context: Dict) -> List[str]
```

##### 2.2 搜尋策略選擇器
**目標**: 根據不同場景選擇最適合的搜尋策略

**功能描述**:
- 策略模板管理
- 動態策略選擇
- 策略效果評估
- 策略優化建議

**搜尋策略類型**:
```
新聞搜尋策略:
- 即時性優先
- 相關性優先
- 權威性優先

網頁搜尋策略:
- 綜合性搜尋
- 專業性搜尋
- 社群性搜尋

圖片搜尋策略:
- 圖表優先
- 新聞圖片優先
- 社群圖片優先
```

##### 2.3 結果分析器
**目標**: 分析和處理搜尋結果

**功能描述**:
- 結果相關性評分
- 內容品質評估
- 重複內容過濾
- 結果排序和篩選

**分析維度**:
```
相關性評分:
- 關鍵字匹配度 (40%)
- 內容相關性 (30%)
- 時間新鮮度 (20%)
- 來源權威性 (10%)

品質評估:
- 內容完整性
- 資訊準確性
- 語言品質
- 結構清晰度
```

#### 功能 3: 搜尋策略管理器

##### 3.1 熱門話題搜尋策略
**目標**: 為熱門話題觸發器設計專用搜尋策略

**策略特點**:
- 搜尋話題相關新聞和討論
- 關注社群反應和影響力
- 包含相關產業和公司資訊
- 強調社會影響和投資機會

**關鍵字組合**:
```
主要關鍵字: 話題名稱 + 相關產業
次要關鍵字: 社會影響 + 投資機會  
長尾關鍵字: 具體事件 + 市場反應
```

##### 3.2 漲停股搜尋策略
**目標**: 為漲停股觸發器設計專用搜尋策略

**策略特點**:
- 搜尋漲停原因和技術分析
- 關注籌碼面和資金流向
- 包含產業動態和公司消息
- 強調技術指標和走勢預測

**關鍵字組合**:
```
主要關鍵字: 股票名稱 + 漲停原因
次要關鍵字: 技術分析 + 籌碼面
長尾關鍵字: 具體指標 + 走勢預測
```

##### 3.3 新聞事件搜尋策略
**目標**: 為新聞事件觸發器設計專用搜尋策略

**策略特點**:
- 搜尋事件相關的即時新聞
- 關注市場反應和影響分析
- 包含專家評論和預測
- 強調投資機會和風險提醒

### 🔧 技術規格

#### 技術架構
- **語言**: Python 3.9+
- **框架**: FastAPI, asyncio
- **外部服務**: Serper API
- **數據存儲**: PostgreSQL
- **快取**: Redis
- **監控**: Prometheus + Grafana (可選)

#### API 設計
```python
# 統一 Serper 客戶端
class UnifiedSerperClient:
    def __init__(self, api_key: str, config: SerperConfig)
    async def search(self, strategy: SearchStrategy) -> SearchResult
    def get_usage_stats(self) -> UsageStats
    def get_error_logs(self) -> List[ErrorLog]

# 智能搜尋引擎
class IntelligentSearchEngine:
    def __init__(self, serper_client: UnifiedSerperClient)
    async def search_with_strategy(self, trigger_type: TriggerType, context: Dict) -> EnhancedSearchResult
    def generate_keywords(self, trigger_type: TriggerType, context: Dict) -> List[str]
    def analyze_results(self, results: List[Dict]) -> AnalysisResult

# 搜尋策略管理器
class SearchStrategyManager:
    def get_strategy(self, trigger_type: TriggerType) -> SearchStrategy
    def optimize_strategy(self, strategy: SearchStrategy, feedback: Feedback) -> SearchStrategy
    def evaluate_strategy(self, strategy: SearchStrategy, results: List[Dict]) -> EvaluationResult
```

#### 數據模型
```python
@dataclass
class SerperConfig:
    api_key: str
    base_url: str = "https://google.serper.dev/search"
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100  # requests per minute

@dataclass
class SearchParams:
    query: str
    num_results: int = 10
    search_type: str = "search"
    language: str = "zh-TW"
    country: str = "TW"
    custom_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchResult:
    success: bool
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float
    error_message: Optional[str] = None

@dataclass
class SearchStrategy:
    trigger_type: TriggerType
    keyword_generation_prompt: str
    search_params_template: Dict[str, Any]
    result_filtering_rules: List[FilterRule]
    enhancement_prompt: str

@dataclass
class EnhancedSearchResult:
    original_results: List[Dict[str, Any]]
    enhanced_results: List[Dict[str, Any]]
    analysis: AnalysisResult
    keywords_used: List[str]
    strategy_applied: SearchStrategy
```

### 📊 實施計劃

#### 階段 1: 統一 Serper 客戶端 (1週)
- 設計統一的 API 調用介面
- 實現錯誤處理和重試機制
- 建立使用量監控系統
- 單元測試和整合測試

#### 階段 2: 智能搜尋引擎 (2週)
- 實現關鍵字生成器
- 建立搜尋策略選擇器
- 開發結果分析器
- 整合 LLM 輔助功能

#### 階段 3: 搜尋策略管理器 (1週)
- 實現各觸發器專用策略
- 建立策略評估和優化機制
- 整合到現有系統
- 完整測試和部署

#### 階段 4: 遷移和優化 (1週)
- 遷移現有重複實現
- 性能優化和監控
- 文檔更新和培訓
- 生產環境部署

### 🧪 測試策略

#### 單元測試
- API 調用功能測試
- 錯誤處理機制測試
- 關鍵字生成演算法測試
- 搜尋策略邏輯測試

#### 整合測試
- 端到端搜尋流程測試
- 不同觸發器策略比較測試
- 性能基準測試
- 錯誤恢復測試

#### 負載測試
- API 調用頻率測試
- 並發搜尋測試
- 記憶體使用測試
- 響應時間測試

### 📈 成功指標

#### 技術指標
- API 調用統一性: 100%
- 搜尋結果一致性: 100%
- 錯誤處理覆蓋率: 100%
- 響應時間: < 2秒

#### 業務指標
- 代碼重複率: < 10%
- 維護成本降低: 70%
- 搜尋結果相關性: > 85%
- 系統可用性: > 99%

### 🔒 風險評估

#### 技術風險
- **API 限制**: Serper API 使用量限制
- **性能影響**: 額外的處理邏輯可能影響響應時間
- **複雜度增加**: 統一系統可能增加系統複雜度

#### 緩解措施
- 實現智能快取和預載入
- 優化搜尋策略和關鍵字生成
- 提供降級和回退機制
- 建立完善的監控和告警

### 📚 相關文檔

- [智能優化關鍵字系統 PRD](./intelligent-keyword-optimization-prd.md)
- [Serper API 使用指南](./serper-api-usage-guide.md)
- [搜尋策略設計規範](./search-strategy-design.md)
- [API 整合最佳實踐](./api-integration-best-practices.md)

---

**文檔版本**: v1.0  
**最後更新**: 2025-01-15  
**審核狀態**: 待審核
