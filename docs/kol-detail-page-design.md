# KOL 個人詳情頁面設計

## 概述
為每個 KOL 創建個人詳情頁面，展示其完整設定、發文歷史、互動表現等資訊。

## 頁面結構

### 1. 頁面路由
- **路徑**: `/content-management/kols/:memberId`
- **導航**: 從 KOL 列表頁面的「查看」按鈕進入
- **麵包屑**: 內容管理 > KOL 管理 > [KOL 暱稱]

### 2. 頁面佈局

#### 2.1 頁面標題區
```
[返回按鈕] KOL 個人詳情 - [KOL 暱稱]
```

#### 2.2 基本資訊卡片 (Row 1)
- **KOL 基本資料** (Col 8)
  - 暱稱、Member ID、人設、狀態
  - 認領人、Email、密碼狀態
  - 加白名單狀態、備註

- **發文設定** (Col 8)
  - 發文時間設定
  - 目標受眾、互動閾值
  - 內容類型偏好

- **統計概覽** (Col 8)
  - 總發文數、已發布數
  - 平均互動率、最佳表現貼文

#### 2.3 詳細設定卡片 (Row 2)
- **人設設定** (Col 12)
  - 常用詞彙、口語化用詞
  - 語氣風格、常用打字習慣
  - 前導故事、專長領域

- **Prompt 設定** (Col 12)
  - PromptPersona、PromptStyle
  - PromptGuardrails、PromptSkeleton
  - PromptCTA、PromptHashtags

#### 2.4 新增：技術參數統計卡片 (Row 3)
- **內容生成參數** (Col 8)
  - 平均生成時間、Temperature 分布
  - 內容長度分布、語氣向量分析
  - KOL 權重設定統計

- **數據來源分析** (Col 8)
  - OHLC 調用成功率
  - 技術指標計算統計
  - 股票標記驗證準確率

- **生成品質指標** (Col 8)
  - 內容多樣性評分
  - 標題獨特性分析
  - 格式一致性檢查

#### 2.5 發文歷史與互動分析 (Row 4)
- **發文歷史表格** (Col 24)
  - 貼文 ID、話題標題、內容預覽
  - 發文時間、狀態、內容長度、發文類型
  - 生成參數（Temperature、生成時間）
  - 數據來源（OHLC狀態、技術指標）
  - 平台發文 URL（可點擊跳轉到實際文章頁面）
  - 操作按鈕（查看詳情、編輯、參數詳情）

- **互動表現圖表** (Col 24)
  - 時間軸互動趨勢圖
  - 1小時/1天/7天互動數據對比
  - 熱門話題分析

## 數據來源

### 主要數據表
1. **同學會帳號管理** - KOL 基本設定
2. **貼文記錄表** - 發文歷史
3. **互動回饋_1hr** - 1小時互動數據
4. **互動回饋_1day** - 1天互動數據  
5. **互動回饋_7days** - 7天互動數據

### 數據欄位映射

#### KOL 基本資訊
```typescript
interface KOLDetail {
  // 基本資料
  serial: string;           // 序號
  nickname: string;         // 暱稱
  member_id: string;        // MemberId
  persona: string;          // 人設
  status: string;           // 狀態
  owner: string;            // 認領人
  email: string;            // Email
  password: string;         // 密碼
  whitelist: boolean;       // 加白名單
  notes: string;            // 備註
  
  // 發文設定
  post_times: string;       // 發文時間
  target_audience: string;  // 目標受眾
  interaction_threshold: number; // 互動閾值
  content_types: string[];  // 內容類型
  
  // 人設設定
  common_terms: string;     // 常用詞彙
  colloquial_terms: string; // 口語化用詞
  tone_style: string;       // 語氣風格
  typing_habit: string;     // 常用打字習慣
  backstory: string;        // 前導故事
  expertise: string;        // 專長領域
  
  // Prompt 設定
  prompt_persona: string;   // PromptPersona
  prompt_style: string;     // PromptStyle
  prompt_guardrails: string; // PromptGuardrails
  prompt_skeleton: string;  // PromptSkeleton
  prompt_cta: string;       // PromptCTA
  prompt_hashtags: string;  // PromptHashtags
  
  // 統計數據
  total_posts: number;      // 總發文數
  published_posts: number;  // 已發布數
  avg_interaction_rate: number; // 平均互動率
  best_performing_post: string; // 最佳表現貼文
}
```

#### 發文歷史
```typescript
interface PostHistory {
  // 基礎信息
  post_id: string;          // 貼文ID
  kol_serial: string;       // KOL Serial
  kol_nickname: string;     // KOL 暱稱
  kol_member_id: string;    // KOL ID
  persona: string;          // Persona
  content_type: string;     // Content Type
  topic_index: number;      // 已派發TopicIndex
  topic_id: string;         // 已派發TopicID
  topic_title: string;      // 已派發TopicTitle
  topic_keywords: string;   // 已派發TopicKeywords
  content: string;          // 生成內容
  status: string;           // 發文狀態
  scheduled_time: string;   // 上次排程時間
  post_time: string;        // 發文時間戳記
  error_message: string;    // 最近錯誤訊息
  
  // 平台信息
  platform_post_id: string; // 平台發文ID
  platform_post_url: string; // 平台發文URL（可點擊跳轉）
  trending_topic_title: string; // 熱門話題標題
  
  // 新增：內容生成參數
  post_type: '提問型' | '發表看法'; // 發文類型
  content_length: '<100' | '100-250' | '>250'; // 內容長度
  word_count: number;       // 內文字數
  kol_weight_settings: string; // KOL權重設定
  content_generation_time: string; // 內容生成時間
  kol_settings_version: string; // KOL設定版本
  length_vector: number[];   // 文章長度向量
  tone_vector: number[];     // 語氣向量
  temperature: number;       // Temperature設定
  
  // 新增：數據來源追蹤
  data_sources: string[];   // 調用數據來源庫
  ohlc_status: '成功' | '失敗' | '未調用'; // OHLC數據狀態
  technical_indicators: string; // 技術指標計算
  stock_validation: string; // 股票標記驗證
  body_parameters: string;  // Body Parameter
  
  // 互動數據
  interactions_1hr: InteractionData;
  interactions_1day: InteractionData;
  interactions_7days: InteractionData;
}

interface InteractionData {
  likes_count: number;      // 按讚數
  comments_count: number;   // 留言數
  total_interactions: number; // 總互動數
  engagement_rate: number;  // 互動率
  growth_rate: number;      // 成長率
  collection_error: string; // 收集錯誤
}
```

## API 設計

### 1. 獲取 KOL 詳情
```
GET /api/dashboard/kols/{memberId}
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "data": {
    "kol_info": KOLDetail,
    "post_history": PostHistory[],
    "interaction_summary": {
      "total_posts": 25,
      "published_posts": 23,
      "avg_interaction_rate": 0.045,
      "best_performing_post": "post-001",
      "interaction_trend": [
        {
          "date": "2024-01-01",
          "interactions": 150,
          "engagement_rate": 0.05
        }
      ]
    },
    "technical_summary": {
      "avg_generation_time": "2.3秒",
      "temperature_distribution": { "0.7": 15, "0.8": 8, "0.9": 2 },
      "content_length_distribution": { "<100": 5, "100-250": 18, ">250": 2 },
      "ohlc_success_rate": 0.76,
      "stock_validation_accuracy": 0.92,
      "content_diversity_score": 0.85
    }
  }
}
```

### 2. 獲取 KOL 互動數據
```
GET /api/dashboard/kols/{memberId}/interactions
```

**Query Parameters:**
- `timeframe`: 1hr|1day|7days
- `start_date`: 開始日期
- `end_date`: 結束日期

## 功能特性

### 1. 數據展示
- **即時數據**: 從 Google Sheets 即時讀取
- **歷史趨勢**: 互動數據時間軸圖表
- **對比分析**: 不同時間段互動表現對比

### 2. 操作功能
- **查看詳情**: 點擊貼文查看完整內容
- **編輯設定**: 修改 KOL 基本設定（需要權限）
- **數據導出**: 導出 KOL 數據為 CSV/Excel

### 3. 響應式設計
- **桌面版**: 完整佈局，所有資訊並排顯示
- **平板版**: 調整卡片排列，保持可讀性
- **手機版**: 垂直堆疊，優化觸控操作

## 技術實現

### 1. 組件結構
```
src/components/KOL/
├── KOLDetail.tsx           # 主頁面組件
├── KOLBasicInfo.tsx        # 基本資訊卡片
├── KOLSettings.tsx         # 設定資訊卡片
├── TechnicalParameters.tsx  # 技術參數統計卡片
├── DataSourceAnalysis.tsx  # 數據來源分析卡片
├── QualityMetrics.tsx      # 生成品質指標卡片
├── PostHistory.tsx         # 發文歷史表格
├── InteractionChart.tsx    # 互動圖表
└── KOLStats.tsx           # 統計概覽
```

### 2. 路由配置
```typescript
// 在 App.tsx 中添加路由
<Route path="/content-management/kols/:memberId" element={<KOLDetail />} />
```

### 3. 狀態管理
```typescript
// 在 dashboardStore.ts 中添加
interface KOLDetailState {
  kolDetail: KOLDetail | null;
  postHistory: PostHistory[];
  interactionData: InteractionData[];
  technicalSummary: TechnicalSummary | null;
  loading: boolean;
  error: string | null;
}

interface TechnicalSummary {
  avg_generation_time: string;
  temperature_distribution: Record<string, number>;
  content_length_distribution: Record<string, number>;
  ohlc_success_rate: number;
  stock_validation_accuracy: number;
  content_diversity_score: number;
}

const useKOLDetailStore = create<KOLDetailState>((set, get) => ({
  // 狀態和操作
}));
```

## 開發優先級

### Phase 1: 基本功能
1. 創建 KOL 詳情頁面路由
2. 實現基本資訊展示
3. 實現發文歷史表格

### Phase 2: 數據整合
1. 整合 Google Sheets 數據
2. 實現互動數據展示
3. 添加統計概覽
4. 整合新的技術參數欄位

### Phase 3: 進階功能
1. 實現互動圖表
2. 添加數據導出功能
3. 優化響應式設計
4. 實現技術參數統計卡片
5. 添加數據來源分析功能

### Phase 4: 品質監控
1. 實現生成品質指標
2. 添加內容多樣性分析
3. 建立異常檢測機制
4. 實現股票標記驗證

## 注意事項

1. **數據同步**: 確保 Google Sheets 數據即時同步
2. **權限控制**: 編輯功能需要適當的權限驗證
3. **性能優化**: 大量數據時需要分頁和虛擬滾動
4. **錯誤處理**: 處理 Google Sheets API 錯誤和網絡問題
5. **數據驗證**: 確保從 Google Sheets 讀取的數據格式正確

## 預期效果

用戶可以：
1. 快速了解 KOL 的完整設定和狀態
2. 查看 KOL 的發文歷史和表現
3. 分析 KOL 的互動趨勢和效果
4. 監控內容生成的技術參數和品質
5. 追蹤數據來源使用情況和準確性
6. 基於數據做出 KOL 管理決策
7. 導出數據進行進一步分析
8. 識別內容生成的一致性和多樣性問題
