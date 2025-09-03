# KOL 個人詳情頁面開發計劃

## 開發概述
基於現有的儀表板架構，擴展 KOL 個人詳情頁面功能，從 Google Sheets 獲取真實數據並提供完整的 KOL 管理界面。

## 開發階段

### Phase 1: 基礎架構 (1-2 天)

#### 1.1 後端 API 擴展
**目標**: 擴展現有的 Dashboard API，添加 KOL 詳情相關的端點

**任務**:
- [ ] 在 `dashboard-api/main.py` 中添加新的路由
- [ ] 實現 KOL 基本資訊獲取 API
- [ ] 實現發文歷史獲取 API
- [ ] 實現互動數據獲取 API
- [ ] 添加數據緩存機制
- [ ] 實現錯誤處理和日誌記錄

**文件修改**:
```
docker-container/finlab python/apps/dashboard-api/
├── main.py (新增路由)
├── utils/
│   ├── data_processor.py (新增)
│   ├── cache_manager.py (新增)
│   └── error_handler.py (新增)
└── models/
    └── kol_models.py (新增)
```

#### 1.2 前端路由配置
**目標**: 配置前端路由，支持 KOL 詳情頁面導航

**任務**:
- [ ] 在 `App.tsx` 中添加新路由
- [ ] 創建 KOL 詳情頁面組件
- [ ] 實現麵包屑導航
- [ ] 添加返回按鈕功能

**文件修改**:
```
docker-container/finlab python/apps/dashboard-frontend/src/
├── App.tsx (新增路由)
├── components/
│   └── KOL/
│       ├── KOLDetail.tsx (新增)
│       ├── KOLBasicInfo.tsx (新增)
│       ├── KOLSettings.tsx (新增)
│       ├── PostHistory.tsx (新增)
│       └── InteractionChart.tsx (新增)
└── types/
    └── kol-types.ts (新增)
```

### Phase 2: 數據整合 (2-3 天)

#### 2.1 Google Sheets 數據讀取
**目標**: 從真實的 Google Sheets 讀取 KOL 數據

**任務**:
- [ ] 實現 `同學會帳號管理` 表數據讀取
- [ ] 實現 `貼文記錄表` 數據讀取
- [ ] 實現 `互動回饋_1hr/1day/7days` 數據讀取
- [ ] 實現數據解析和格式化
- [ ] 添加數據驗證和錯誤處理

**實現重點**:
```python
# 數據讀取示例
def get_kol_basic_info(member_id: str):
    """從同學會帳號管理表獲取 KOL 基本資訊"""
    try:
        data = sheets_client.read_sheet("同學會帳號管理")
        for row in data[1:]:  # 跳過標題行
            if len(row) > 5 and row[5] == member_id:
                return parse_kol_row(row)
        return None
    except Exception as e:
        logger.error(f"Error reading KOL data: {str(e)}")
        raise
```

#### 2.2 數據處理和統計
**目標**: 實現 KOL 數據的統計分析和計算

**任務**:
- [ ] 實現發文統計計算
- [ ] 實現互動數據統計
- [ ] 實現趨勢分析計算
- [ ] 實現最佳表現貼文識別
- [ ] 添加數據緩存機制

**統計計算示例**:
```python
def calculate_kol_statistics(member_id: str):
    """計算 KOL 統計數據"""
    posts = get_kol_posts(member_id)
    interactions = get_kol_interactions(member_id)
    
    return {
        "total_posts": len(posts),
        "published_posts": len([p for p in posts if p.status == "已發布"]),
        "avg_interaction_rate": calculate_avg_interaction_rate(interactions),
        "best_performing_post": find_best_performing_post(interactions),
        "total_interactions": sum(i.total_interactions for i in interactions)
    }
```

#### 2.3 API 端點實現
**目標**: 實現完整的 API 端點，提供前端所需的數據

**任務**:
- [ ] 實現 `GET /api/dashboard/kols/{memberId}` 端點
- [ ] 實現 `GET /api/dashboard/kols/{memberId}/posts` 端點
- [ ] 實現 `GET /api/dashboard/kols/{memberId}/interactions` 端點
- [ ] 實現 `GET /api/dashboard/kols/{memberId}/settings` 端點
- [ ] 添加分頁和篩選功能
- [ ] 實現數據導出功能

### Phase 3: 前端界面實現 (3-4 天)

#### 3.1 基本資訊展示
**目標**: 實現 KOL 基本資訊的展示界面

**任務**:
- [ ] 創建 KOL 基本資料卡片
- [ ] 創建發文設定卡片
- [ ] 創建統計概覽卡片
- [ ] 實現響應式佈局
- [ ] 添加載入狀態和錯誤處理

**組件結構**:
```typescript
// KOLBasicInfo.tsx
interface KOLBasicInfoProps {
  kolInfo: KOLInfo;
  statistics: KOLStatistics;
  loading: boolean;
  error: string | null;
}

const KOLBasicInfo: React.FC<KOLBasicInfoProps> = ({ kolInfo, statistics, loading, error }) => {
  // 實現基本資訊展示
};
```

#### 3.2 人設設定展示
**目標**: 實現 KOL 人設設定的詳細展示

**任務**:
- [ ] 創建人設設定卡片
- [ ] 實現常用詞彙展示
- [ ] 實現口語化用詞展示
- [ ] 實現語氣風格展示
- [ ] 實現 Prompt 設定展示
- [ ] 添加可折疊的詳細資訊

#### 3.3 發文歷史表格
**目標**: 實現發文歷史的表格展示和交互

**任務**:
- [ ] 創建發文歷史表格組件
- [ ] 實現分頁功能
- [ ] 實現搜索和篩選功能
- [ ] 實現排序功能
- [ ] 添加貼文詳情查看功能
- [ ] 實現平台 URL 點擊跳轉功能
- [ ] 實現數據導出功能

**表格功能**:
```typescript
// PostHistory.tsx
const PostHistory: React.FC<PostHistoryProps> = ({ posts, loading, onViewDetail }) => {
  const columns = [
    {
      title: '貼文 ID',
      dataIndex: 'post_id',
      key: 'post_id',
      render: (text: string) => (
        <Button type="link" onClick={() => onViewDetail(text)}>
          {text}
        </Button>
      )
    },
    {
      title: '平台 URL',
      dataIndex: 'platform_post_url',
      key: 'platform_post_url',
      render: (url: string, record: PostHistory) => {
        if (!url || url.trim() === '') {
          return <span style={{ color: '#999' }}>未發布</span>;
        }
        return (
          <Button 
            type="link" 
            size="small"
            onClick={() => window.open(url, '_blank')}
            icon={<ExternalLinkOutlined />}
          >
            查看
          </Button>
        );
      }
    },
    // ... 其他列
  ];
  
  return (
    <Table
      columns={columns}
      dataSource={posts}
      loading={loading}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showQuickJumper: true
      }}
    />
  );
};
```

#### 3.4 互動分析圖表
**目標**: 實現互動數據的圖表展示

**任務**:
- [ ] 創建互動趨勢圖表
- [ ] 實現時間範圍選擇
- [ ] 實現互動數據對比
- [ ] 添加圖表交互功能
- [ ] 實現數據點懸停顯示
- [ ] 添加圖表導出功能

**圖表實現**:
```typescript
// InteractionChart.tsx
import { Line } from '@ant-design/charts';

const InteractionChart: React.FC<InteractionChartProps> = ({ data, timeframe }) => {
  const config = {
    data: data,
    xField: 'date',
    yField: 'interactions',
    point: {
      size: 5,
      shape: 'diamond',
    },
    label: {
      style: {
        fill: '#aaa',
      },
    },
  };
  
  return <Line {...config} />;
};
```

### Phase 4: 進階功能 (2-3 天)

#### 4.1 編輯功能
**目標**: 實現 KOL 設定的編輯功能

**任務**:
- [ ] 創建編輯模式界面
- [ ] 實現表單驗證
- [ ] 實現數據保存功能
- [ ] 添加權限控制
- [ ] 實現編輯歷史記錄

#### 4.2 數據導出
**目標**: 實現數據導出功能

**任務**:
- [ ] 實現 CSV 導出
- [ ] 實現 Excel 導出
- [ ] 實現 PDF 報告生成
- [ ] 添加導出選項配置
- [ ] 實現批量導出功能

#### 4.3 性能優化
**目標**: 優化頁面性能和用戶體驗

**任務**:
- [ ] 實現數據緩存
- [ ] 實現虛擬滾動
- [ ] 實現懶載入
- [ ] 優化圖表渲染
- [ ] 實現預載入機制

### Phase 5: 測試和優化 (1-2 天)

#### 5.1 功能測試
**目標**: 確保所有功能正常運作

**任務**:
- [ ] 測試數據讀取功能
- [ ] 測試 API 端點
- [ ] 測試前端界面
- [ ] 測試響應式設計
- [ ] 測試錯誤處理

#### 5.2 性能測試
**目標**: 確保頁面性能符合要求

**任務**:
- [ ] 測試大量數據載入
- [ ] 測試並發請求處理
- [ ] 測試緩存效果
- [ ] 測試圖表渲染性能
- [ ] 優化載入時間

#### 5.3 用戶體驗優化
**目標**: 提升用戶體驗

**任務**:
- [ ] 優化載入動畫
- [ ] 優化錯誤提示
- [ ] 優化操作流程
- [ ] 添加操作確認
- [ ] 實現無障礙設計

## 技術實現細節

### 1. 數據模型設計

```typescript
// kol-types.ts
export interface KOLInfo {
  serial: string;
  nickname: string;
  member_id: string;
  persona: string;
  status: string;
  owner: string;
  email: string;
  password: string;
  whitelist: boolean;
  notes: string;
  post_times: string;
  target_audience: string;
  interaction_threshold: number;
  content_types: string[];
  common_terms: string;
  colloquial_terms: string;
  tone_style: string;
  typing_habit: string;
  backstory: string;
  expertise: string;
  prompt_persona: string;
  prompt_style: string;
  prompt_guardrails: string;
  prompt_skeleton: string;
  prompt_cta: string;
  prompt_hashtags: string;
  signature: string;
  emoji_pack: string;
  model_id: string;
  model_temp: number;
  max_tokens: number;
}

export interface KOLStatistics {
  total_posts: number;
  published_posts: number;
  draft_posts: number;
  avg_interaction_rate: number;
  best_performing_post: string;
  total_interactions: number;
  avg_likes_per_post: number;
  avg_comments_per_post: number;
}

export interface PostHistory {
  post_id: string;
  topic_id: string;
  topic_title: string;
  topic_keywords: string;
  content: string;
  status: string;
  scheduled_time: string;
  post_time: string;
  error_message: string;
  platform_post_id: string;
  platform_post_url: string; // 平台發文URL（可點擊跳轉）
  trending_topic_title: string; // 熱門話題標題
  interactions: {
    '1hr': InteractionData;
    '1day': InteractionData;
    '7days': InteractionData;
  };
}

export interface InteractionData {
  likes_count: number;
  comments_count: number;
  total_interactions: number;
  engagement_rate: number;
  growth_rate: number;
}
```

### 2. 狀態管理

```typescript
// kol-detail-store.ts
import { create } from 'zustand';

interface KOLDetailState {
  kolInfo: KOLInfo | null;
  statistics: KOLStatistics | null;
  postHistory: PostHistory[];
  interactionData: InteractionData[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchKOLDetail: (memberId: string) => Promise<void>;
  fetchPostHistory: (memberId: string, page?: number) => Promise<void>;
  fetchInteractionData: (memberId: string, timeframe?: string) => Promise<void>;
  clearData: () => void;
}

export const useKOLDetailStore = create<KOLDetailState>((set, get) => ({
  kolInfo: null,
  statistics: null,
  postHistory: [],
  interactionData: [],
  loading: false,
  error: null,
  
  fetchKOLDetail: async (memberId: string) => {
    set({ loading: true, error: null });
    try {
      const response = await api.get(`/api/dashboard/kols/${memberId}`);
      set({
        kolInfo: response.data.kol_info,
        statistics: response.data.statistics,
        loading: false
      });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  // ... 其他 actions
}));
```

### 3. 路由配置

```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import KOLDetail from './components/KOL/KOLDetail';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 現有路由 */}
        <Route path="/" element={<DashboardOverview />} />
        <Route path="/system-monitoring" element={<SystemMonitoring />} />
        <Route path="/content-management" element={<ContentManagement />} />
        <Route path="/interaction-analysis" element={<InteractionAnalysis />} />
        
        {/* 新增 KOL 詳情路由 */}
        <Route path="/content-management/kols/:memberId" element={<KOLDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## 部署和測試

### 1. 開發環境測試
```bash
# 啟動後端服務
cd docker-container/finlab\ python
docker-compose up dashboard-api

# 啟動前端服務
docker-compose up dashboard-frontend

# 測試 API 端點
curl http://localhost:8007/api/dashboard/kols/9505546
```

### 2. 生產環境部署
```bash
# 構建 Docker 映像
docker-compose build

# 部署到生產環境
docker-compose up -d
```

### 3. 監控和日誌
- 監控 API 響應時間
- 監控 Google Sheets API 使用量
- 記錄錯誤和異常
- 監控用戶操作行為

## 風險評估和應對

### 1. 技術風險
- **Google Sheets API 限制**: 實現緩存和批量處理
- **數據格式不一致**: 添加數據驗證和錯誤處理
- **性能問題**: 實現分頁和虛擬滾動

### 2. 業務風險
- **數據隱私**: 實現適當的權限控制
- **數據準確性**: 添加數據驗證和校驗
- **用戶體驗**: 進行充分的用戶測試

### 3. 應對策略
- 實現完整的錯誤處理機制
- 添加數據備份和恢復功能
- 進行充分的測試和驗證
- 實現監控和告警機制

## 成功標準

### 1. 功能完整性
- [ ] 所有 KOL 基本資訊正確顯示
- [ ] 發文歷史完整且可搜索
- [ ] 互動數據準確且可視化
- [ ] 編輯功能正常運作
- [ ] 數據導出功能正常

### 2. 性能要求
- [ ] 頁面載入時間 < 3 秒
- [ ] API 響應時間 < 1 秒
- [ ] 支持 100+ KOL 數據
- [ ] 支持 1000+ 貼文記錄

### 3. 用戶體驗
- [ ] 界面直觀易用
- [ ] 響應式設計正常
- [ ] 錯誤提示清晰
- [ ] 操作流程順暢

### 4. 技術要求
- [ ] 代碼質量符合標準
- [ ] 錯誤處理完善
- [ ] 日誌記錄完整
- [ ] 文檔齊全

## 總結

這個開發計劃提供了完整的 KOL 個人詳情頁面實現方案，包括：

1. **分階段開發**: 從基礎架構到進階功能，確保開發進度可控
2. **真實數據整合**: 直接從 Google Sheets 讀取真實數據
3. **完整功能覆蓋**: 包含查看、編輯、導出等完整功能
4. **性能優化**: 考慮大量數據的處理和展示
5. **用戶體驗**: 提供直觀易用的界面

預計總開發時間：**8-12 天**
- Phase 1: 1-2 天
- Phase 2: 2-3 天  
- Phase 3: 3-4 天
- Phase 4: 2-3 天
- Phase 5: 1-2 天

這個計劃確保了功能的完整性和開發的可控性，同時考慮了實際的技術挑戰和業務需求。
