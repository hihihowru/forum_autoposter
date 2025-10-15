# 貼文詳細頁面設計

## 🎯 設計目標

### 主要功能
1. **完整參數展示** - 顯示內容生成的所有技術參數
2. **數據來源追蹤** - 追蹤 OHLC 數據獲取和技術指標計算
3. **品質驗證結果** - 展示股票標記驗證和內容品質檢查
4. **生成過程分析** - 分析內容生成的完整流程和決策邏輯

---

## 📱 頁面結構

### 1. 頁面路由
- **路徑**: `/content-management/posts/:postId`
- **導航**: 從 KOL 詳細頁面的發文歷史表格進入
- **麵包屑**: 內容管理 > KOL 管理 > [KOL 暱稱] > [貼文標題]

### 2. 頁面佈局

#### 2.1 頁面標題區
```
[返回按鈕] 貼文詳情 - [貼文標題]
[編輯按鈕] [刪除按鈕] [重新生成按鈕]
```

#### 2.2 基礎信息卡片 (Row 1)
- **貼文基本信息** (Col 12)
  - 貼文 ID、KOL 信息、話題信息
  - 發文狀態、時間、錯誤訊息
  - 平台發文 ID 和 URL

- **內容預覽** (Col 12)
  - 完整內容展示
  - 內容長度統計
  - 發文類型標籤

#### 2.3 生成參數詳情卡片 (Row 2)
- **技術參數** (Col 8)
  - Temperature 設定、生成時間
  - 文章長度向量、語氣向量
  - KOL 權重設定、設定版本

- **內容分析** (Col 8)
  - 字數統計、長度分類
  - 發文類型、內容風格
  - 生成品質評分

- **數據來源** (Col 8)
  - 調用的數據來源庫
  - OHLC 數據狀態
  - 技術指標計算結果

#### 2.4 驗證結果卡片 (Row 3)
- **股票標記驗證** (Col 12)
  - 識別的股票代碼和名稱
  - 驗證結果和準確性
  - 相關的市場數據

- **內容品質檢查** (Col 12)
  - 格式一致性檢查
  - 標題獨特性分析
  - 內容多樣性評分

#### 2.5 Body Parameter 詳情 (Row 4)
- **API 請求參數** (Col 24)
  - 完整的請求參數展示
  - 參數解析和說明
  - 調用結果和響應

---

## 📊 數據展示設計

### 1. 基礎信息展示
```typescript
interface PostBasicInfo {
  post_id: string;
  kol_nickname: string;
  kol_member_id: string;
  persona: string;
  topic_title: string;
  content: string;
  status: string;
  scheduled_time: string;
  post_time: string;
  error_message: string;
  platform_post_id: string;
  platform_post_url: string;
}
```

### 2. 技術參數展示
```typescript
interface TechnicalParameters {
  temperature: number;
  content_generation_time: string;
  length_vector: number[];
  tone_vector: number[];
  kol_weight_settings: string;
  kol_settings_version: string;
  word_count: number;
  content_length: string;
  post_type: string;
}
```

### 3. 數據來源追蹤
```typescript
interface DataSourceTracking {
  data_sources: string[];
  ohlc_status: string;
  technical_indicators: string;
  stock_validation: string;
  body_parameters: string;
}
```

### 4. 品質驗證結果
```typescript
interface QualityValidation {
  stock_validation_result: {
    identified_stocks: string[];
    validation_accuracy: number;
    market_data: any;
  };
  content_quality: {
    format_consistency: number;
    title_uniqueness: number;
    content_diversity: number;
    overall_score: number;
  };
}
```

---

## 🎨 UI 組件設計

### 1. 參數展示卡片
```typescript
const ParameterCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <Card title={title} size="small" style={{ height: '100%' }}>
    {children}
  </Card>
);
```

### 2. 向量可視化
```typescript
const VectorVisualization: React.FC<{ vector: number[]; labels: string[] }> = ({ vector, labels }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
    {vector.map((value, index) => (
      <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ width: '60px', fontSize: '12px' }}>{labels[index]}</span>
        <Progress 
          percent={value * 100} 
          size="small" 
          showInfo={false}
          strokeColor={value > 0.5 ? '#52c41a' : '#faad14'}
        />
        <span style={{ width: '40px', fontSize: '12px', textAlign: 'right' }}>
          {(value * 100).toFixed(0)}%
        </span>
      </div>
    ))}
  </div>
);
```

### 3. 股票標記驗證
```typescript
const StockValidation: React.FC<{ validation: any }> = ({ validation }) => (
  <div>
    <div style={{ marginBottom: '16px' }}>
      <Tag color={validation.validation_accuracy > 0.8 ? 'green' : 'orange'}>
        準確率: {(validation.validation_accuracy * 100).toFixed(1)}%
      </Tag>
    </div>
    <div>
      <h4>識別的股票:</h4>
      {validation.identified_stocks.map((stock: string, index: number) => (
        <Tag key={index} color="blue" style={{ margin: '4px' }}>
          {stock}
        </Tag>
      ))}
    </div>
  </div>
);
```

---

## 🔧 API 設計

### 1. 獲取貼文詳情
```
GET /api/dashboard/posts/{postId}
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "data": {
    "basic_info": PostBasicInfo,
    "technical_parameters": TechnicalParameters,
    "data_source_tracking": DataSourceTracking,
    "quality_validation": QualityValidation
  }
}
```

### 2. 重新生成內容
```
POST /api/dashboard/posts/{postId}/regenerate
```

**Request Body:**
```json
{
  "temperature": 0.8,
  "content_length": "100-250",
  "post_type": "發表看法"
}
```

### 3. 更新貼文狀態
```
PUT /api/dashboard/posts/{postId}/status
```

**Request Body:**
```json
{
  "status": "已發布",
  "platform_post_id": "173349543",
  "platform_post_url": "https://www.cmoney.tw/forum/article/173349543"
}
```

---

## 📈 數據可視化

### 1. 參數分布圖表
- **Temperature 分布**: 柱狀圖顯示不同溫度值的使用頻率
- **內容長度分布**: 餅圖顯示短/中/長內容的比例
- **生成時間趨勢**: 折線圖顯示生成時間的變化趨勢

### 2. 品質評分雷達圖
- **多維度評分**: 格式一致性、標題獨特性、內容多樣性等
- **歷史對比**: 與其他貼文的品質對比
- **改進建議**: 基於評分提供改進建議

### 3. 數據來源使用分析
- **來源分布**: 不同數據來源的使用比例
- **調用成功率**: OHLC API 調用的成功/失敗統計
- **技術指標熱度**: 各種技術指標的使用頻率

---

## 🚀 功能特性

### 1. 即時數據更新
- 從 Google Sheets 即時讀取最新數據
- 支持手動刷新和自動同步
- 顯示數據最後更新時間

### 2. 參數調試功能
- 支持修改生成參數
- 即時預覽參數調整效果
- 保存參數調整歷史

### 3. 品質改進建議
- 基於品質評分提供改進建議
- 推薦相似的優質貼文作為參考
- 提供 KOL 設定優化建議

### 4. 數據導出功能
- 導出貼文詳情為 PDF 報告
- 導出技術參數為 CSV 數據
- 支持批量導出多個貼文

---

## 🔒 權限控制

### 1. 查看權限
- **所有用戶**: 可以查看已發布貼文的詳情
- **KOL 管理員**: 可以查看所有貼文的詳情
- **系統管理員**: 可以查看所有貼文和系統參數

### 2. 編輯權限
- **KOL 管理員**: 可以編輯貼文狀態和平台信息
- **系統管理員**: 可以修改所有參數和設定
- **普通用戶**: 只能查看，不能編輯

### 3. 刪除權限
- **系統管理員**: 可以刪除任何貼文
- **KOL 管理員**: 只能刪除自己管理的 KOL 貼文
- **普通用戶**: 無刪除權限

---

## 📱 響應式設計

### 1. 桌面版佈局
- 使用 24 列網格系統
- 卡片並排顯示，最大化信息密度
- 支持多列數據展示

### 2. 平板版佈局
- 調整為 12 列網格系統
- 卡片垂直堆疊，保持可讀性
- 優化觸控操作體驗

### 3. 手機版佈局
- 使用單列佈局
- 卡片全寬顯示
- 優化小屏幕的數據展示

---

## 🎯 開發優先級

### Phase 1: 基礎功能
1. 創建貼文詳情頁面路由
2. 實現基礎信息展示
3. 實現技術參數展示

### Phase 2: 數據整合
1. 整合 Google Sheets 數據
2. 實現數據來源追蹤
3. 添加品質驗證結果

### Phase 3: 進階功能
1. 實現參數可視化
2. 添加品質改進建議
3. 實現數據導出功能

### Phase 4: 優化完善
1. 優化響應式設計
2. 添加權限控制
3. 實現性能優化

---

## 📊 預期效果

用戶可以：
1. 深入了解每個貼文的生成過程
2. 分析技術參數對內容品質的影響
3. 追蹤數據來源的使用情況和準確性
4. 識別內容生成的問題和改進點
5. 基於數據優化 KOL 設定和生成策略
6. 導出詳細報告進行進一步分析
7. 監控系統的整體生成品質和一致性

---

*貼文詳細頁面設計版本: v1.0*  
*最後更新: 2025-08-28*  
*設計範圍: 虛擬 KOL 系統貼文詳情展示*



