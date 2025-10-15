# 前端架構

## 🎯 前端技術棧

### 核心技術
- **React 18** - 用戶界面框架
- **TypeScript** - 類型安全的 JavaScript
- **Ant Design** - UI 組件庫
- **Vite** - 快速構建工具
- **React Router** - 路由管理
- **Axios** - HTTP 客戶端

### 開發工具
- **ESLint** - 代碼檢查
- **Prettier** - 代碼格式化
- **Husky** - Git hooks
- **Lint-staged** - 暫存區檢查

## 🏗️ 項目結構

```
dashboard-frontend/
├── src/
│   ├── components/           # 可重用組件
│   │   ├── Layout/          # 布局組件
│   │   │   ├── Sidebar.tsx  # 側邊欄
│   │   │   ├── Header.tsx   # 頂部導航
│   │   │   └── Footer.tsx   # 底部
│   │   ├── Dashboard/       # 儀表板組件
│   │   │   ├── SystemMonitoring.tsx
│   │   │   ├── ContentManagement.tsx
│   │   │   └── InteractionAnalysis.tsx
│   │   ├── KOL/            # KOL 管理組件
│   │   │   ├── KOLManagementPage.tsx
│   │   │   ├── KOLDetail.tsx
│   │   │   └── KOLProfile.tsx
│   │   └── PostingManagement/  # 發文管理組件
│   │       ├── PostingManagement.tsx
│   │       ├── PostingGenerator/  # 發文生成器組件
│   │       │   ├── PostingGenerator.tsx  # 主生成器組件
│   │       │   ├── TriggerSelector.tsx  # 觸發器選擇器
│   │       │   ├── DataSourceSelector.tsx  # 數據源選擇器
│   │       │   ├── ExplainabilityConfig.tsx  # 可解釋性配置
│   │       │   ├── NewsConfig.tsx  # 新聞配置
│   │       │   ├── KOLSelector.tsx  # KOL 選擇器
│   │       │   ├── GenerationSettings.tsx  # 生成設定
│   │       │   ├── TagSettings.tsx  # 標籤設定
│   │       │   ├── BatchModeSettings.tsx  # 批次模式設定
│   │       │   ├── AfterHoursLimitUpDisplay.tsx  # 盤後漲停顯示
│   │       │   ├── TrendingTopicsDisplay.tsx  # 熱門話題顯示
│   │       │   ├── IntradayTriggerDisplay.tsx  # 盤中觸發器顯示
│   │       │   ├── KOLPromptTuner.tsx  # KOL 提示詞調節器
│   │       │   ├── StockFilterDisplay.tsx  # 股票篩選顯示
│   │       │   ├── StockCodeListInput.tsx  # 股票代號列表輸入
│   │       │   └── CustomStockInput.tsx  # 自定義股票輸入
│   │       ├── PostingReview/  # 發文審核組件
│   │       │   ├── PostReviewPage.tsx  # 審核頁面
│   │       │   ├── PostReviewCard.tsx  # 審核卡片
│   │       │   └── ReviewActions.tsx  # 審核操作
│   │       ├── BatchHistory/  # 批次歷史組件
│   │       │   ├── BatchHistoryPage.tsx  # 批次歷史頁面
│   │       │   ├── BatchDetailModal.tsx  # 批次詳情彈窗
│   │       │   ├── BatchScheduleModal.tsx  # 批次排程彈窗
│   │       │   └── BatchStatsCard.tsx  # 批次統計卡片
│   │       ├── ScheduleManagement/  # 排程管理組件
│   │       │   ├── ScheduleManagementPage.tsx  # 排程管理頁面
│   │       │   ├── ScheduleConfigModal.tsx  # 排程配置彈窗
│   │       │   ├── ScheduleList.tsx  # 排程列表
│   │       │   └── ScheduleStats.tsx  # 排程統計
│   │       ├── PostingDashboard.tsx  # 發文儀表板
│   │       └── AfterHoursLimitUpTest.tsx  # 盤後漲停測試
│   ├── pages/              # 頁面組件
│   │   ├── PublishedPostsPage.tsx
│   │   ├── SelfLearningPage.tsx
│   │   ├── InteractionAnalysisPage.tsx
│   │   └── PerformanceAnalysisPage.tsx
│   ├── services/           # API 服務層
│   │   ├── postingManagementAPI.ts
│   │   ├── kolService.ts
│   │   └── dashboardAPI.ts
│   ├── stores/            # 狀態管理
│   │   └── dashboardStore.ts
│   ├── types/             # TypeScript 類型定義
│   │   ├── api.ts
│   │   ├── kol.ts
│   │   └── posting.ts
│   ├── utils/             # 工具函數
│   │   ├── dateUtils.ts
│   │   ├── formatUtils.ts
│   │   └── validationUtils.ts
│   ├── App.tsx            # 主應用組件
│   ├── main.tsx           # 應用入口
│   └── vite-env.d.ts      # Vite 類型定義
├── public/                # 靜態資源
├── package.json           # 依賴配置
├── vite.config.ts         # Vite 配置
├── tsconfig.json          # TypeScript 配置
└── tailwind.config.js     # Tailwind 配置
```

## 🛣️ 路由配置

### 主要路由結構

```typescript
// App.tsx 路由配置
const routes = [
  {
    path: '/',
    element: <SimpleTest />,
    label: '儀表板總覽'
  },
  {
    path: '/system-monitoring',
    element: <SystemMonitoring />,
    label: '系統監控',
    children: [
      { path: '/system-monitoring', label: '系統狀態' },
      { path: '/system-monitoring/services', label: '微服務監控' },
      { path: '/system-monitoring/tasks', label: '任務執行' }
    ]
  },
  {
    path: '/content-management',
    element: <ContentManagement />,
    label: '內容管理',
    children: [
      { path: '/content-management', label: '內容總覽' },
      { path: '/content-management/kols', label: 'KOL 管理' },
      { path: '/content-management/posts', label: '貼文管理' }
    ]
  },
  {
    path: '/posting-management',
    element: <PostingManagement />,
    label: '發文管理',
    children: [
      { path: '/posting-management', label: '發文總覽' },
      { path: '/posting-management/dashboard', label: '發文儀表板' },
      { path: '/posting-management/generator', label: '發文生成器' },
      { path: '/posting-management/review', label: '發文審核' },
      { path: '/posting-management/published', label: '已發布貼文' },
      { path: '/posting-management/test-after-hours', label: '盤後漲停測試' },
      { path: '/posting-management/batch-history', label: '批次歷史' },
      { path: '/posting-management/schedule', label: '排程管理' },
      { path: '/posting-management/self-learning', label: '自我學習' },
      { path: '/posting-management/interaction-analysis', label: '互動分析' },
      { path: '/posting-management/performance-analysis', label: '成效分析' },
      { path: '/posting-management/manual-posting', label: '手動發文' }
    ]
  },
  {
    path: '/interaction-analysis',
    element: <InteractionAnalysis />,
    label: '互動分析',
    children: [
      { path: '/interaction-analysis', label: '互動總覽' },
      { path: '/interaction-analysis/features', label: '內容特徵分析' },
      { path: '/interaction-analysis/1hr', label: '1小時數據' },
      { path: '/interaction-analysis/1day', label: '1日數據' },
      { path: '/interaction-analysis/7days', label: '7日數據' }
    ]
  },
  {
    path: '/settings',
    element: <SettingsPage />,
    label: '系統設置',
    children: [
      { path: '/settings', label: '基本設置' },
      { path: '/settings/api', label: 'API 設置' },
      { path: '/settings/data', label: '數據源設置' }
    ]
  },
  {
    path: '/users',
    element: <UserManagement />,
    label: '用戶管理',
    children: [
      { path: '/users', label: '用戶列表' },
      { path: '/users/roles', label: '角色權限' }
    ]
  }
];
```

## 🧩 組件架構

### 布局組件

#### Sidebar.tsx
```typescript
interface SidebarProps {
  collapsed: boolean;
  onRefresh: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onRefresh }) => {
  // 側邊欄導航邏輯
  // 菜單項配置
  // 路由導航處理
};
```

#### Header.tsx
```typescript
interface HeaderProps {
  collapsed: boolean;
  onToggle: () => void;
  onRefresh: () => void;
  lastUpdated: string;
  loading: boolean;
}

const Header: React.FC<HeaderProps> = ({ ... }) => {
  // 頂部導航邏輯
  // 刷新按鈕
  // 用戶信息
};
```

### 核心業務組件

#### PostingGenerator.tsx - 主生成器組件
```typescript
interface PostingGeneratorProps {
  onGenerate?: (config: GenerationConfig) => Promise<void>;
  onSaveTemplate?: (template: GenerationTemplate) => void;
  onLoadTemplate?: (templateId: string) => void;
  loading?: boolean;
}

const PostingGenerator: React.FC<PostingGeneratorProps> = ({
  onGenerate,
  onSaveTemplate,
  onLoadTemplate,
  loading = false
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [generationConfig, setGenerationConfig] = useState<GenerationConfig>({
    triggers: {},      // 觸發器配置
    dataSources: {},   // 數據源配置
    explainability: {}, // 可解釋性配置
    news: {},         // 新聞配置
    kol: {},          // KOL 配置
    settings: {},     // 生成設定
    tags: {},         // 標籤設定
    batchMode: {}     // 批次模式設定
  });

  // 步驟配置
  const steps = [
    { title: '觸發器選擇', component: TriggerSelector },
    { title: '數據源配置', component: DataSourceSelector },
    { title: '可解釋性設定', component: ExplainabilityConfig },
    { title: '新聞配置', component: NewsConfig },
    { title: 'KOL 選擇', component: KOLSelector },
    { title: '生成設定', component: GenerationSettings },
    { title: '標籤設定', component: TagSettings },
    { title: '批次模式', component: BatchModeSettings }
  ];

  // 渲染當前步驟內容
  const renderStepContent = () => {
    const StepComponent = steps[currentStep].component;
    return (
      <StepComponent
        value={generationConfig[steps[currentStep].key]}
        onChange={(value) => updateConfig(steps[currentStep].key, value)}
      />
    );
  };
};
```

#### TriggerSelector.tsx - 觸發器選擇器
```typescript
interface TriggerConfig {
  triggerType: 'individual' | 'sector' | 'macro' | 'news' | 'intraday' | 'volume' | 'custom';
  triggerKey: string;
  stockFilter: string;
  newsKeywords?: string[];
}

const TriggerSelector: React.FC<TriggerSelectorProps> = ({ value, onChange, onNewsConfigChange }) => {
  // 觸發器分類配置
  const triggerCategories = [
    {
      key: 'individual',
      label: '個股觸發器',
      triggers: [
        { key: 'limit_up_after_hours', label: '盤後漲', newsKeywords: ['上漲', '漲停', '突破', '強勢'] },
        { key: 'limit_down_after_hours', label: '盤後跌', newsKeywords: ['下跌', '跌停', '弱勢', '回檔'] }
      ]
    },
    {
      key: 'volume',
      label: '成交量觸發器',
      triggers: [
        { key: 'volume_amount_high', label: '成交金額高', newsKeywords: ['成交量', '爆量', '大量', '活躍'] },
        { key: 'volume_amount_low', label: '成交金額低', newsKeywords: ['量縮', '清淡', '觀望'] },
        { key: 'volume_change_rate_high', label: '成交金額變化率高', newsKeywords: ['放量', '增量', '活躍'] },
        { key: 'volume_change_rate_low', label: '成交金額變化率低', newsKeywords: ['縮量', '量縮', '觀望'] }
      ]
    },
    {
      key: 'intraday',
      label: '盤中觸發器',
      triggers: [
        { key: 'intraday_gainers_by_amount', label: '漲幅排序+成交額' },
        { key: 'intraday_volume_leaders', label: '成交量排序' },
        { key: 'intraday_amount_leaders', label: '成交額排序' },
        { key: 'intraday_limit_down', label: '跌停篩選' },
        { key: 'intraday_limit_up', label: '漲停篩選' },
        { key: 'intraday_limit_down_by_amount', label: '跌停篩選+成交額' }
      ]
    }
  ];

  // 處理觸發器選擇
  const handleTriggerSelect = (categoryKey: string, triggerKey: string) => {
    const category = triggerCategories.find(c => c.key === categoryKey);
    const trigger = category?.triggers.find(t => t.key === triggerKey);
    
    if (trigger) {
      const triggerConfig: TriggerConfig = {
        triggerType: categoryKey as any,
        triggerKey: triggerKey,
        stockFilter: trigger.stockFilter,
        newsKeywords: trigger.newsKeywords
      };
      
      onChange({ ...value, triggerConfig });
      
      // 智能更新新聞搜尋關鍵字
      if (trigger.newsKeywords && onNewsConfigChange) {
        onNewsConfigChange(trigger.newsKeywords);
      }
    }
  };
};
```

#### KOLSelector.tsx - KOL 選擇器
```typescript
interface KOLConfig {
  allocation_mode: 'random' | 'fixed' | 'dynamic';
  selected_kols: number[];
  kol_persona: string;
  content_style: string;
  target_audience: string;
}

const KOLSelector: React.FC<KOLSelectorProps> = ({ value, onChange }) => {
  const [kolList, setKolList] = useState<KOL[]>([]);
  const [loading, setLoading] = useState(false);

  // 獲取 KOL 列表
  useEffect(() => {
    const fetchKOLList = async () => {
      setLoading(true);
      try {
        const kols = await KOLService.getKOLList();
        setKolList(kols);
      } catch (error) {
        console.error('獲取 KOL 列表失敗:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchKOLList();
  }, []);

  // 處理 KOL 分配模式變更
  const handleAllocationModeChange = (mode: string) => {
    onChange({
      ...value,
      allocation_mode: mode,
      selected_kols: mode === 'random' ? [] : value.selected_kols
    });
  };

  // 生成隨機 KOL
  const generateRandomKOLs = () => {
    const randomKols = kolList
      .sort(() => Math.random() - 0.5)
      .slice(0, 5)
      .map(kol => kol.serial);
    
    onChange({
      ...value,
      selected_kols: randomKols
    });
  };
};
```

#### GenerationSettings.tsx - 生成設定
```typescript
interface GenerationSettings {
  post_mode: 'one_to_one' | 'one_to_many';
  content_length: 'short' | 'medium' | 'long' | 'extended' | 'comprehensive' | 'thorough';
  max_stocks_per_post: number;
  content_style: 'technical' | 'casual' | 'professional' | 'humorous';
  include_analysis_depth: 'basic' | 'detailed' | 'comprehensive';
  max_words: number;
  include_charts: boolean;
  include_risk_warning: boolean;
  posting_type: 'interaction' | 'analysis';
  include_questions: boolean;
  include_emoji: boolean;
  include_hashtag: boolean;
}

const GenerationSettings: React.FC<GenerationSettingsProps> = ({ value, onChange }) => {
  // 發文模式選擇
  const handlePostModeChange = (mode: string) => {
    onChange({
      ...value,
      post_mode: mode,
      max_stocks_per_post: mode === 'one_to_one' ? 1 : value.max_stocks_per_post
    });
  };

  // 內容長度選擇
  const handleContentLengthChange = (length: string) => {
    const lengthConfig = {
      short: 200,
      medium: 500,
      long: 800,
      extended: 1200,
      comprehensive: 1500,
      thorough: 2000
    };
    
    onChange({
      ...value,
      content_length: length,
      max_words: lengthConfig[length]
    });
  };
};
```

#### BatchModeSettings.tsx - 批次模式設定
```typescript
interface BatchModeConfig {
  enabled: boolean;
  batch_size: number;
  kol_allocation: 'random' | 'fixed' | 'dynamic';
  content_distribution: {
    analysis: number;
    interaction: number;
  };
  posting_type: 'interaction' | 'analysis';
}

const BatchModeSettings: React.FC<BatchModeSettingsProps> = ({ value, onChange }) => {
  // 批次模式開關
  const handleBatchModeToggle = (enabled: boolean) => {
    onChange({
      ...value,
      enabled,
      batch_size: enabled ? value.batch_size : 1
    });
  };

  // 批次大小設定
  const handleBatchSizeChange = (size: number) => {
    onChange({
      ...value,
      batch_size: Math.max(1, Math.min(50, size))
    });
  };
};
```

#### TriggerSelector.tsx
```typescript
interface TriggerConfig {
  triggerType: 'individual' | 'sector' | 'macro' | 'news' | 'intraday' | 'volume' | 'custom';
  triggerKey: string;
  stockFilter: string;
  newsKeywords?: string[];
}

const TriggerSelector: React.FC<TriggerSelectorProps> = () => {
  // 觸發器類型選擇
  // 智能新聞搜尋關鍵字更新
  // 自定義股票輸入
};
```

#### BatchHistoryPage.tsx
```typescript
const BatchHistoryPage: React.FC = () => {
  // 批次歷史展示
  // 批次詳情查看
  // 排程創建
  // 數據統計
};
```

#### ScheduleManagementPage.tsx
```typescript
const ScheduleManagementPage: React.FC = () => {
  // 排程列表展示
  // 排程創建/編輯
  // 排程執行監控
  // 排程統計分析
};
```

## 🔌 API 服務層

### postingManagementAPI.ts
```typescript
export class PostingManagementAPI {
  // 貼文管理 API
  static async getPosts(params: GetPostsParams): Promise<Post[]>
  static async createPost(data: CreatePostData): Promise<Post>
  static async updatePost(id: string, data: UpdatePostData): Promise<Post>
  static async deletePost(id: string): Promise<void>
  
  // 批次管理 API
  static async getBatchHistory(params: GetBatchParams): Promise<Batch[]>
  static async createBatch(data: CreateBatchData): Promise<Batch>
  static async getBatchDetail(id: string): Promise<BatchDetail>
  
  // 排程管理 API
  static async getSchedules(params: GetScheduleParams): Promise<Schedule[]>
  static async createSchedule(data: CreateScheduleData): Promise<Schedule>
  static async updateSchedule(id: string, data: UpdateScheduleData): Promise<Schedule>
  static async deleteSchedule(id: string): Promise<void>
  
  // 互動分析 API
  static async getInteractionData(params: GetInteractionParams): Promise<InteractionData>
  static async getInteractionStats(): Promise<InteractionStats>
  static async refreshInteractionData(): Promise<void>
}
```

### kolService.ts
```typescript
export class KOLService {
  // KOL 管理 API
  static async getKOLList(): Promise<KOL[]>
  static async getKOLDetail(id: string): Promise<KOLDetail>
  static async createKOL(data: CreateKOLData): Promise<KOL>
  static async updateKOL(id: string, data: UpdateKOLData): Promise<KOL>
  static async deleteKOL(id: string): Promise<void>
  
  // KOL 配置 API
  static async getKOLConfig(id: string): Promise<KOLConfig>
  static async updateKOLConfig(id: string, config: KOLConfig): Promise<void>
  static async getKOLStats(id: string): Promise<KOLStats>
}
```

## 🗄️ 狀態管理

### dashboardStore.ts
```typescript
interface DashboardState {
  // 系統監控數據
  systemMonitoring: {
    data: SystemMonitoringData | null;
    loading: boolean;
    error: string | null;
  };
  
  // 互動分析數據
  interactionAnalysis: {
    data: InteractionAnalysisData | null;
    loading: boolean;
    error: string | null;
  };
  
  // 內容管理數據
  contentManagement: {
    data: ContentManagementData | null;
    loading: boolean;
    error: string | null;
  };
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  // 狀態定義
  // 動作定義
  // 異步操作
}));
```

## 🎨 UI 設計系統

### Ant Design 主題配置
```typescript
// 主題配置
const theme = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    borderRadius: 6,
    fontSize: 14,
  },
  components: {
    Button: {
      borderRadius: 6,
    },
    Card: {
      borderRadius: 8,
    },
    Table: {
      borderRadius: 8,
    },
  },
};
```

### 自定義組件
```typescript
// 可重用組件
export const StatusTag: React.FC<{ status: string }> = ({ status }) => {
  // 狀態標籤組件
};

export const LoadingSpinner: React.FC<{ size?: number }> = ({ size = 24 }) => {
  // 載入動畫組件
};

export const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 錯誤邊界組件
};
```

## 📱 響應式設計

### 斷點配置
```typescript
const breakpoints = {
  xs: '480px',
  sm: '576px',
  md: '768px',
  lg: '992px',
  xl: '1200px',
  xxl: '1600px',
};
```

### 響應式組件
```typescript
const ResponsiveLayout: React.FC = () => {
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  return (
    <Layout>
      {!isMobile && <Sidebar />}
      <Content>
        {/* 內容 */}
      </Content>
    </Layout>
  );
};
```

## 🔧 開發工具配置

### Vite 配置
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
```

### TypeScript 配置
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## 🚀 性能優化

### 代碼分割
```typescript
// 懶加載組件
const LazyComponent = lazy(() => import('./LazyComponent'));

// 路由級代碼分割
const routes = [
  {
    path: '/posting-management',
    element: lazy(() => import('./pages/PostingManagementPage')),
  },
];
```

### 緩存策略
```typescript
// API 緩存
const useApiCache = <T>(key: string, fetcher: () => Promise<T>) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const cached = localStorage.getItem(key);
    if (cached) {
      setData(JSON.parse(cached));
    } else {
      setLoading(true);
      fetcher().then(result => {
        setData(result);
        localStorage.setItem(key, JSON.stringify(result));
        setLoading(false);
      });
    }
  }, [key]);
  
  return { data, loading };
};
```

### 虛擬化
```typescript
// 大列表虛擬化
import { FixedSizeList as List } from 'react-window';

const VirtualizedList: React.FC<{ items: any[] }> = ({ items }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {items[index]}
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={50}
    >
      {Row}
    </List>
  );
};
```
