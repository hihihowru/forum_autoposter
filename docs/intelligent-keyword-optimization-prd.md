# 智能優化關鍵字系統 PRD

## 📋 產品需求文檔 (PRD)

### 🎯 產品概述

**產品名稱**: 智能優化關鍵字系統 (Intelligent Keyword Optimization System)  
**版本**: v1.0  
**創建日期**: 2025-01-15  
**負責人**: AI Assistant  

### 🔍 背景與問題

#### 現有問題
1. **Prompt 重複使用**: 熱門話題和漲停分析使用相同的 prompt 模板
2. **缺乏針對性**: 沒有根據不同觸發器類型調整內容風格
3. **關鍵字策略單一**: 所有觸發器都使用固定的關鍵字搜尋策略
4. **Serper API 整合分散**: 多個重複實現，缺乏統一管理

#### 業務影響
- 內容重複性高，影響 KOL 個性化表現
- 搜尋結果相關性低，影響內容品質
- 維護成本高，代碼重複

### 🎯 產品目標

#### 主要目標
1. **實現觸發器專用 Prompt**: 不同觸發器使用專屬的 title 和 content agent prompt
2. **智能關鍵字生成**: 使用 LLM 動態生成最優搜尋關鍵字
3. **統一 Serper API 整合**: 建立統一的關鍵字優化和新聞搜尋系統

#### 成功指標
- 內容重複率降低 60%
- 搜尋結果相關性提升 40%
- 代碼重複率降低 80%

### 🏗️ 系統架構設計

#### 核心組件

##### 1. 觸發器專用 Prompt 系統
```
TriggerSpecificPromptSystem
├── TrendingTopicPromptStrategy
├── LimitUpAfterHoursPromptStrategy  
├── IntradayLimitUpPromptStrategy
├── CustomStocksPromptStrategy
├── NewsEventPromptStrategy
└── EarningsReportPromptStrategy
```

##### 2. 智能關鍵字優化系統
```
IntelligentKeywordOptimizer
├── KeywordGenerationAgent
├── SearchStrategySelector
├── RelevanceAnalyzer
└── KeywordRefinementEngine
```

##### 3. 統一 Serper API 整合
```
UnifiedSerperIntegration
├── SerperClient
├── NewsSearchEngine
├── KeywordOptimizer
└── ContentEnhancer
```

### 📝 功能需求

#### 功能 1: 觸發器專用 Prompt 系統

##### 1.1 熱門話題 Prompt 策略
**目標**: 為熱門話題觸發器設計專用的 prompt 模板

**功能描述**:
- 專注於話題討論和社群互動
- 強調話題的社會影響力和討論熱度
- 使用更輕鬆、互動性強的語氣
- 包含話題背景和相關新聞

**Prompt 特點**:
```
系統角色: 你是 {kol_nickname}，一個善於捕捉市場熱點的 {kol_persona} 分析師
內容重點: 
- 話題的社會影響力
- 相關新聞和背景
- 投資機會分析
- 風險提醒
語氣風格: 輕鬆互動，善於引發討論
```

##### 1.2 盤後漲停 Prompt 策略
**目標**: 為盤後漲停觸發器設計專用的 prompt 模板

**功能描述**:
- 專注於技術分析和籌碼面
- 強調漲停原因和後續走勢預測
- 使用專業、理性的分析語氣
- 包含技術指標和籌碼分析

**Prompt 特點**:
```
系統角色: 你是 {kol_nickname}，一個專業的 {kol_persona} 技術分析師
內容重點:
- 漲停原因分析
- 技術指標解讀
- 籌碼面分析
- 後續走勢預測
語氣風格: 專業理性，數據導向
```

##### 1.3 盤中漲停 Prompt 策略
**目標**: 為盤中漲停觸發器設計專用的 prompt 模板

**功能描述**:
- 專注於即時市場動態和交易機會
- 強調短線操作和風險控制
- 使用緊湊、行動導向的語氣
- 包含即時數據和交易建議

**Prompt 特點**:
```
系統角色: 你是 {kol_nickname}，一個敏銳的 {kol_persona} 短線交易員
內容重點:
- 即時市場動態
- 短線交易機會
- 風險控制提醒
- 操作建議
語氣風格: 緊湊行動，即時反應
```

#### 功能 2: 智能關鍵字生成系統

##### 2.1 LLM 關鍵字生成
**目標**: 使用 LLM 動態生成最優搜尋關鍵字

**功能描述**:
- 根據觸發器類型生成專用關鍵字
- 考慮 KOL 人設和內容風格
- 動態調整關鍵字策略
- 優化搜尋結果相關性

**關鍵字生成策略**:
```
熱門話題關鍵字:
- 話題名稱 + 相關產業
- 社會影響 + 投資機會
- 新聞熱點 + 市場反應

盤後漲停關鍵字:
- 股票名稱 + 漲停原因
- 技術分析 + 籌碼面
- 產業動態 + 公司消息

盤中漲停關鍵字:
- 即時新聞 + 市場動態
- 交易機會 + 風險提醒
- 短線分析 + 操作建議
```

##### 2.2 多層次搜尋策略
**目標**: 實現多層次的關鍵字搜尋和結果優化

**功能描述**:
- 主要關鍵字搜尋
- 相關關鍵字擴展
- 結果相關性分析
- 關鍵字動態調整

**搜尋層次**:
```
第一層: 主要關鍵字 (3-5個)
第二層: 相關關鍵字 (5-8個)  
第三層: 長尾關鍵字 (8-12個)
第四層: 結果優化調整
```

#### 功能 3: 統一 Serper API 整合

##### 3.1 統一搜尋客戶端
**目標**: 建立統一的 Serper API 搜尋客戶端

**功能描述**:
- 統一的 API 調用介面
- 錯誤處理和重試機制
- 結果快取和優化
- 使用量監控和限制

##### 3.2 智能內容增強
**目標**: 使用搜尋結果智能增強內容品質

**功能描述**:
- 新聞內容分析和摘要
- 相關資訊提取和整合
- 內容相關性驗證
- 品質評分和優化建議

### 🔧 技術規格

#### 技術架構
- **語言**: Python 3.9+
- **框架**: FastAPI, OpenAI API
- **外部服務**: Serper API
- **數據存儲**: PostgreSQL
- **快取**: Redis (可選)

#### API 設計
```python
# 觸發器專用 Prompt 系統
class TriggerSpecificPromptSystem:
    def get_prompt_strategy(self, trigger_type: TriggerType) -> PromptStrategy
    def generate_title_prompt(self, trigger_type: TriggerType, context: Dict) -> str
    def generate_content_prompt(self, trigger_type: TriggerType, context: Dict) -> str

# 智能關鍵字優化系統  
class IntelligentKeywordOptimizer:
    def generate_keywords(self, trigger_type: TriggerType, context: Dict) -> List[str]
    def optimize_search_strategy(self, keywords: List[str]) -> SearchStrategy
    def analyze_relevance(self, results: List[Dict]) -> RelevanceScore

# 統一 Serper API 整合
class UnifiedSerperIntegration:
    def search_news(self, keywords: List[str], strategy: SearchStrategy) -> List[Dict]
    def enhance_content(self, content: str, news_data: List[Dict]) -> EnhancedContent
```

#### 數據模型
```python
@dataclass
class PromptStrategy:
    trigger_type: TriggerType
    system_prompt: str
    user_prompt_template: str
    keyword_generation_prompt: str
    content_enhancement_prompt: str

@dataclass
class SearchStrategy:
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    search_params: Dict[str, Any]

@dataclass
class EnhancedContent:
    original_content: str
    enhanced_content: str
    news_sources: List[Dict]
    relevance_score: float
    enhancement_notes: List[str]
```

### 📊 實施計劃

#### 階段 1: 觸發器專用 Prompt 系統 (2週)
- 設計各觸發器的專用 prompt 模板
- 實現 PromptStrategy 類別
- 整合到現有內容生成流程
- 測試和優化

#### 階段 2: 智能關鍵字生成 (2週)  
- 實現 LLM 關鍵字生成功能
- 設計多層次搜尋策略
- 建立關鍵字優化演算法
- 整合 Serper API

#### 階段 3: 統一整合和優化 (1週)
- 統一所有 Serper API 調用
- 實現智能內容增強
- 性能優化和監控
- 完整測試和部署

### 🧪 測試策略

#### 單元測試
- 各觸發器 prompt 策略測試
- 關鍵字生成演算法測試
- Serper API 整合測試

#### 整合測試
- 端到端內容生成流程測試
- 不同觸發器類型比較測試
- 性能基準測試

#### 用戶驗收測試
- KOL 內容品質評估
- 搜尋結果相關性評估
- 用戶體驗測試

### 📈 成功指標

#### 技術指標
- 內容重複率: < 20%
- 搜尋結果相關性: > 80%
- API 響應時間: < 2秒
- 系統可用性: > 99%

#### 業務指標
- KOL 內容品質評分提升
- 用戶互動率提升
- 內容分享率提升
- 系統維護成本降低

### 🔒 風險評估

#### 技術風險
- **API 限制**: Serper API 使用量限制
- **LLM 成本**: OpenAI API 調用成本
- **性能影響**: 額外的 API 調用可能影響響應時間

#### 緩解措施
- 實現 API 使用量監控和限制
- 優化 LLM 調用策略，減少不必要的調用
- 實現結果快取和異步處理

### 📚 相關文檔

- [動態 Prompting 系統設計](./dynamic-prompting-system.md)
- [Serper API 整合指南](./serper-api-integration.md)
- [觸發器系統架構](./trigger-system-architecture.md)
- [內容生成流程](./content-generation-flow.md)

---

**文檔版本**: v1.0  
**最後更新**: 2025-01-15  
**審核狀態**: 待審核
