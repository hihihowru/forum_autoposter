# 發文管理系統前端設計文稿

## 📋 專案概述

### 專案目標
在現有的互動儀表板系統中整合發文管理功能，提供完整的發文生成、審核和排程管理功能。

### 技術架構
- **前端框架**: React 18 + TypeScript
- **UI 組件庫**: Ant Design 5.x
- **路由管理**: React Router 6
- **狀態管理**: Zustand
- **圖表庫**: Chart.js + react-chartjs-2
- **語言**: 繁體中文

---

## 🏗️ 組件架構設計

### 1. 組件層級結構

```
src/
├── components/
│   ├── Layout/ (現有)
│   │   ├── Sidebar.tsx (擴展)
│   │   ├── Header.tsx (現有)
│   │   └── Content.tsx (現有)
│   ├── Dashboard/ (現有)
│   │   ├── DashboardOverview.tsx (擴展)
│   │   └── ContentManagement.tsx (擴展)
│   ├── PostingManagement/ (新增)
│   │   ├── PostingGenerator/
│   │   │   ├── PostingGenerator.tsx
│   │   │   ├── TriggerSelector.tsx
│   │   │   ├── DataSourceSelector.tsx
│   │   │   ├── ExplainabilityConfig.tsx
│   │   │   ├── NewsConfig.tsx
│   │   │   ├── KOLSelector.tsx
│   │   │   ├── GenerationSettings.tsx
│   │   │   ├── TagSettings.tsx
│   │   │   └── BatchModeSettings.tsx
│   │   ├── PostingReview/
│   │   │   ├── PostingReview.tsx
│   │   │   ├── ReviewList.tsx
│   │   │   ├── ContentEditor.tsx
│   │   │   ├── QualityChecker.tsx
│   │   │   └── BatchOperations.tsx
│   │   ├── DeploymentScheduling/
│   │   │   ├── DeploymentScheduling.tsx
│   │   │   ├── ScheduleList.tsx
│   │   │   ├── ScheduleEditor.tsx
│   │   │   ├── ScheduleMonitor.tsx
│   │   │   └── ScheduleLogs.tsx
│   │   └── TagManagement/
│   │       ├── TagManagement.tsx
│   │       ├── StockTags.tsx
│   │       ├── TopicTags.tsx
│   │       └── CustomTags.tsx
│   └── Common/ (新增)
│       ├── StepIndicator.tsx
│       ├── ProgressBar.tsx
│       ├── QualityScore.tsx
│       └── AIDetection.tsx
├── stores/ (現有)
│   ├── dashboardStore.ts (擴展)
│   └── postingStore.ts (新增)
├── types/ (現有)
│   ├── index.ts (擴展)
│   └── posting.ts (新增)
├── services/ (現有)
│   ├── api.ts (擴展)
│   └── postingApi.ts (新增)
└── utils/ (現有)
    ├── constants.ts (擴展)
    └── postingUtils.ts (新增)
```

---

## 📱 頁面設計規格

### 1. 主儀表板擴展 (DashboardOverview.tsx)

#### 新增區塊設計
```typescript
interface PostingManagementStats {
  pending_review: number;
  published_today: number;
  scheduled_tasks: number;
  error_alerts: number;
}

interface DashboardOverviewProps {
  // 現有屬性
  systemData: SystemMonitoringData | null;
  interactionData: InteractionAnalysisData | null;
  onRefresh: () => void;
  loading: boolean;
  
  // 新增屬性
  postingStats: PostingManagementStats | null;
  onNavigateToPosting: (path: string) => void;
}
```

#### UI 佈局
```jsx
// 新增發文管理快速操作區塊
<Card title="發文管理快速操作" size="small">
  <Row gutter={16}>
    <Col span={6}>
      <Card size="small" style={{ textAlign: 'center' }}>
        <Statistic
          title="待審核"
          value={postingStats?.pending_review || 0}
          prefix={<ClockCircleOutlined />}
          valueStyle={{ color: '#faad14' }}
        />
        <Button 
          type="link" 
          onClick={() => onNavigateToPosting('/content-management/posting/review')}
        >
          前往審核
        </Button>
      </Card>
    </Col>
    <Col span={6}>
      <Card size="small" style={{ textAlign: 'center' }}>
        <Statistic
          title="今日發布"
          value={postingStats?.published_today || 0}
          prefix={<CheckCircleOutlined />}
          valueStyle={{ color: '#52c41a' }}
        />
        <Button 
          type="link" 
          onClick={() => onNavigateToPosting('/content-management/posting/generator')}
        >
          快速生成
        </Button>
      </Card>
    </Col>
    <Col span={6}>
      <Card size="small" style={{ textAlign: 'center' }}>
        <Statistic
          title="排程任務"
          value={postingStats?.scheduled_tasks || 0}
          prefix={<ScheduleOutlined />}
          valueStyle={{ color: '#1890ff' }}
        />
        <Button 
          type="link" 
          onClick={() => onNavigateToPosting('/content-management/posting/scheduling')}
        >
          管理排程
        </Button>
      </Card>
    </Col>
    <Col span={6}>
      <Card size="small" style={{ textAlign: 'center' }}>
        <Statistic
          title="異常告警"
          value={postingStats?.error_alerts || 0}
          prefix={<ExclamationCircleOutlined />}
          valueStyle={{ color: '#ff4d4f' }}
        />
        <Button 
          type="link" 
          onClick={() => onNavigateToPosting('/content-management/posting/alerts')}
        >
          查看詳情
        </Button>
      </Card>
    </Col>
  </Row>
</Card>
```

### 2. 內容管理頁面擴展 (ContentManagement.tsx)

#### 新增 Tab 設計
```typescript
interface ContentManagementProps {
  // 現有屬性
  data: ContentManagementData | null;
  loading: boolean;
  error: string | null;
  
  // 新增屬性
  postingData: PostingManagementData | null;
  onPostingAction: (action: string, data?: any) => void;
}
```

#### Tab 結構
```jsx
const tabItems = [
  {
    key: 'overview',
    label: '內容總覽',
    children: <ContentOverview data={data} />
  },
  {
    key: 'kols',
    label: 'KOL 管理',
    children: <KOLManagement data={data?.kols} />
  },
  {
    key: 'posts',
    label: '貼文管理',
    children: <PostManagement data={data?.posts} />
  },
  {
    key: 'posting',
    label: '發文管理',
    children: <PostingManagement 
      data={postingData}
      onAction={onPostingAction}
    />
  }
];
```

### 3. 發文生成器頁面 (PostingGenerator.tsx)

#### 組件結構
```typescript
interface PostingGeneratorProps {
  onGenerate: (config: GenerationConfig) => Promise<void>;
  onSaveTemplate: (template: GenerationTemplate) => void;
  onLoadTemplate: (templateId: string) => void;
  loading: boolean;
}

interface GenerationConfig {
  triggers: TriggerSelection;
  dataSources: DataSourceSelection;
  explainability: ExplainabilityConfig;
  news: NewsConfig;
  kol: KOLConfig;
  settings: GenerationSettings;
  tags: TagConfig;
  batchMode: BatchModeConfig;
}
```

#### 步驟導航設計
```jsx
const steps = [
  { title: '觸發器選擇', description: '選擇內容觸發器' },
  { title: '數據源配置', description: '配置數據來源' },
  { title: '解釋層設定', description: '設定可解釋性' },
  { title: '新聞搜尋', description: '配置新聞搜尋' },
  { title: 'KOL 選擇', description: '選擇 KOL' },
  { title: '生成設定', description: '配置生成參數' },
  { title: '標籤設定', description: '設定標籤' },
  { title: '批量模式', description: '配置批量生成' }
];

<Steps current={currentStep} items={steps} />
```

#### 觸發器選擇組件 (TriggerSelector.tsx)
```typescript
interface TriggerSelection {
  trending_topic: boolean;
  limit_up_after_hours: boolean;
  intraday_limit_up: boolean;
  custom_stocks: boolean;
  news_event: boolean;
  earnings_report: boolean;
  market_analysis: boolean;
  technical_signals: boolean;
}

const TriggerSelector: React.FC<{
  value: TriggerSelection;
  onChange: (value: TriggerSelection) => void;
}> = ({ value, onChange }) => {
  return (
    <Card title="觸發器選擇" size="small">
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Checkbox
            checked={value.trending_topic}
            onChange={(e) => onChange({...value, trending_topic: e.target.checked})}
          >
            熱門話題
          </Checkbox>
        </Col>
        <Col span={8}>
          <Checkbox
            checked={value.limit_up_after_hours}
            onChange={(e) => onChange({...value, limit_up_after_hours: e.target.checked})}
          >
            盤後漲停
          </Checkbox>
        </Col>
        <Col span={8}>
          <Checkbox
            checked={value.intraday_limit_up}
            onChange={(e) => onChange({...value, intraday_limit_up: e.target.checked})}
          >
            盤中漲停
          </Checkbox>
        </Col>
        {/* 更多觸發器選項... */}
      </Row>
    </Card>
  );
};
```

### 4. 發文審核頁面 (PostingReview.tsx)

#### 審核列表設計
```typescript
interface ReviewItem {
  id: string;
  kol_name: string;
  kol_serial: string;
  trigger_type: string;
  title: string;
  content: string;
  quality_score: number;
  ai_detection: 'passed' | 'warning' | 'failed';
  risk_level: 'low' | 'medium' | 'high';
  data_sources: string[];
  news_links: number;
  generated_at: string;
  status: 'pending' | 'approved' | 'rejected' | 'delayed';
}

const ReviewList: React.FC<{
  items: ReviewItem[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onEdit: (id: string) => void;
  onRegenerate: (id: string) => void;
}> = ({ items, onApprove, onReject, onEdit, onRegenerate }) => {
  return (
    <List
      dataSource={items}
      renderItem={(item) => (
        <List.Item
          actions={[
            <Button type="link" onClick={() => onEdit(item.id)}>編輯</Button>,
            <Button type="primary" onClick={() => onApprove(item.id)}>通過</Button>,
            <Button danger onClick={() => onReject(item.id)}>拒絕</Button>,
            <Button onClick={() => onRegenerate(item.id)}>重新生成</Button>
          ]}
        >
          <List.Item.Meta
            title={
              <Space>
                <Tag color="blue">{item.kol_name}</Tag>
                <Tag color="green">{item.trigger_type}</Tag>
                <QualityScore score={item.quality_score} />
                <AIDetection status={item.ai_detection} />
              </Space>
            }
            description={
              <div>
                <div><strong>標題:</strong> {item.title}</div>
                <div><strong>內容:</strong> {item.content.substring(0, 100)}...</div>
                <div>
                  <Text type="secondary">
                    數據源: {item.data_sources.join(', ')} | 
                    新聞連結: {item.news_links}個 | 
                    生成時間: {item.generated_at}
                  </Text>
                </div>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
};
```

### 5. 部署排程頁面 (DeploymentScheduling.tsx)

#### 排程列表設計
```typescript
interface ScheduleItem {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'stopped' | 'paused';
  trigger_type: string;
  kol_name: string;
  execution_time: string;
  last_execution: string;
  next_execution: string;
  success_rate: number;
  created_at: string;
}

const ScheduleList: React.FC<{
  schedules: ScheduleItem[];
  onStart: (id: string) => void;
  onStop: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}> = ({ schedules, onStart, onStop, onEdit, onDelete }) => {
  return (
    <Table
      dataSource={schedules}
      columns={[
        {
          title: '排程名稱',
          dataIndex: 'name',
          key: 'name',
        },
        {
          title: '狀態',
          dataIndex: 'status',
          key: 'status',
          render: (status) => (
            <Tag color={status === 'running' ? 'green' : 'red'}>
              {status === 'running' ? '運行中' : '已停止'}
            </Tag>
          ),
        },
        {
          title: '觸發器',
          dataIndex: 'trigger_type',
          key: 'trigger_type',
        },
        {
          title: 'KOL',
          dataIndex: 'kol_name',
          key: 'kol_name',
        },
        {
          title: '執行時間',
          dataIndex: 'execution_time',
          key: 'execution_time',
        },
        {
          title: '成功率',
          dataIndex: 'success_rate',
          key: 'success_rate',
          render: (rate) => `${rate}%`,
        },
        {
          title: '操作',
          key: 'actions',
          render: (_, record) => (
            <Space>
              <Button 
                type="primary" 
                size="small"
                onClick={() => record.status === 'running' ? onStop(record.id) : onStart(record.id)}
              >
                {record.status === 'running' ? '停止' : '啟動'}
              </Button>
              <Button size="small" onClick={() => onEdit(record.id)}>編輯</Button>
              <Button danger size="small" onClick={() => onDelete(record.id)}>刪除</Button>
            </Space>
          ),
        },
      ]}
    />
  );
};
```

---

## 🎨 UI 組件設計

### 1. 通用組件

#### StepIndicator.tsx
```typescript
interface StepIndicatorProps {
  current: number;
  total: number;
  steps: Array<{
    title: string;
    description: string;
    completed?: boolean;
  }>;
}

const StepIndicator: React.FC<StepIndicatorProps> = ({ current, total, steps }) => {
  return (
    <div className="step-indicator">
      <Progress 
        percent={(current / total) * 100} 
        showInfo={false}
        strokeColor="#1890ff"
      />
      <div className="step-labels">
        {steps.map((step, index) => (
          <div 
            key={index}
            className={`step-label ${index <= current ? 'active' : ''}`}
          >
            <div className="step-title">{step.title}</div>
            <div className="step-description">{step.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### QualityScore.tsx
```typescript
interface QualityScoreProps {
  score: number;
  showLabel?: boolean;
}

const QualityScore: React.FC<QualityScoreProps> = ({ score, showLabel = true }) => {
  const getColor = (score: number) => {
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 70) return '#faad14';
    return '#ff4d4f';
  };

  const getStars = (score: number) => {
    const stars = Math.floor(score / 20);
    return '⭐'.repeat(stars);
  };

  return (
    <Space>
      <span style={{ color: getColor(score) }}>
        {getStars(score)}
      </span>
      {showLabel && (
        <span style={{ color: getColor(score) }}>
          {score}分
        </span>
      )}
    </Space>
  );
};
```

#### AIDetection.tsx
```typescript
interface AIDetectionProps {
  status: 'passed' | 'warning' | 'failed';
  score?: number;
}

const AIDetection: React.FC<AIDetectionProps> = ({ status, score }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'passed':
        return { color: 'green', icon: '✅', text: '通過' };
      case 'warning':
        return { color: 'orange', icon: '⚠️', text: '警告' };
      case 'failed':
        return { color: 'red', icon: '❌', text: '失敗' };
      default:
        return { color: 'default', icon: '❓', text: '未知' };
    }
  };

  const config = getStatusConfig();

  return (
    <Tag color={config.color}>
      {config.icon} {config.text}
      {score && ` (${score}%)`}
    </Tag>
  );
};
```

---

## 📊 狀態管理設計

### 1. PostingStore.ts
```typescript
interface PostingState {
  // 生成器狀態
  generationConfig: GenerationConfig | null;
  currentStep: number;
  generatedContent: GeneratedContent[];
  
  // 審核狀態
  reviewItems: ReviewItem[];
  selectedItems: string[];
  
  // 排程狀態
  schedules: ScheduleItem[];
  
  // UI 狀態
  loading: {
    generating: boolean;
    reviewing: boolean;
    scheduling: boolean;
  };
  
  // 錯誤狀態
  errors: {
    generation: string | null;
    review: string | null;
    scheduling: string | null;
  };
}

interface PostingActions {
  // 生成器操作
  setGenerationConfig: (config: GenerationConfig) => void;
  setCurrentStep: (step: number) => void;
  generateContent: (config: GenerationConfig) => Promise<void>;
  
  // 審核操作
  loadReviewItems: () => Promise<void>;
  approveItem: (id: string) => Promise<void>;
  rejectItem: (id: string) => Promise<void>;
  editItem: (id: string, content: Partial<ReviewItem>) => Promise<void>;
  
  // 排程操作
  loadSchedules: () => Promise<void>;
  createSchedule: (schedule: Omit<ScheduleItem, 'id'>) => Promise<void>;
  updateSchedule: (id: string, schedule: Partial<ScheduleItem>) => Promise<void>;
  deleteSchedule: (id: string) => Promise<void>;
  
  // 通用操作
  setLoading: (key: keyof PostingState['loading'], loading: boolean) => void;
  setError: (key: keyof PostingState['errors'], error: string | null) => void;
}

export const usePostingStore = create<PostingState & PostingActions>((set, get) => ({
  // 初始狀態
  generationConfig: null,
  currentStep: 0,
  generatedContent: [],
  reviewItems: [],
  selectedItems: [],
  schedules: [],
  loading: {
    generating: false,
    reviewing: false,
    scheduling: false,
  },
  errors: {
    generation: null,
    review: null,
    scheduling: null,
  },
  
  // 生成器操作
  setGenerationConfig: (config) => set({ generationConfig: config }),
  setCurrentStep: (step) => set({ currentStep: step }),
  generateContent: async (config) => {
    set({ loading: { ...get().loading, generating: true } });
    try {
      const content = await postingApi.generateContent(config);
      set({ generatedContent: content });
    } catch (error) {
      set({ errors: { ...get().errors, generation: error.message } });
    } finally {
      set({ loading: { ...get().loading, generating: false } });
    }
  },
  
  // 審核操作
  loadReviewItems: async () => {
    set({ loading: { ...get().loading, reviewing: true } });
    try {
      const items = await postingApi.getReviewItems();
      set({ reviewItems: items });
    } catch (error) {
      set({ errors: { ...get().errors, review: error.message } });
    } finally {
      set({ loading: { ...get().loading, reviewing: false } });
    }
  },
  
  // 排程操作
  loadSchedules: async () => {
    set({ loading: { ...get().loading, scheduling: true } });
    try {
      const schedules = await postingApi.getSchedules();
      set({ schedules });
    } catch (error) {
      set({ errors: { ...get().errors, scheduling: error.message } });
    } finally {
      set({ loading: { ...get().loading, scheduling: false } });
    }
  },
  
  // 通用操作
  setLoading: (key, loading) => 
    set({ loading: { ...get().loading, [key]: loading } }),
  setError: (key, error) => 
    set({ errors: { ...get().errors, [key]: error } }),
}));
```

---

## 🔌 API 接口設計

### 1. PostingAPI.ts
```typescript
class PostingAPI {
  private baseURL = '/api/v1/posting';
  
  // 生成器 API
  async generateContent(config: GenerationConfig): Promise<GeneratedContent[]> {
    const response = await fetch(`${this.baseURL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    return response.json();
  }
  
  async saveTemplate(template: GenerationTemplate): Promise<void> {
    await fetch(`${this.baseURL}/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(template),
    });
  }
  
  async loadTemplate(templateId: string): Promise<GenerationTemplate> {
    const response = await fetch(`${this.baseURL}/templates/${templateId}`);
    return response.json();
  }
  
  // 審核 API
  async getReviewItems(): Promise<ReviewItem[]> {
    const response = await fetch(`${this.baseURL}/review/items`);
    return response.json();
  }
  
  async approveItem(id: string): Promise<void> {
    await fetch(`${this.baseURL}/review/items/${id}/approve`, {
      method: 'POST',
    });
  }
  
  async rejectItem(id: string, reason?: string): Promise<void> {
    await fetch(`${this.baseURL}/review/items/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    });
  }
  
  async editItem(id: string, content: Partial<ReviewItem>): Promise<void> {
    await fetch(`${this.baseURL}/review/items/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(content),
    });
  }
  
  // 排程 API
  async getSchedules(): Promise<ScheduleItem[]> {
    const response = await fetch(`${this.baseURL}/schedules`);
    return response.json();
  }
  
  async createSchedule(schedule: Omit<ScheduleItem, 'id'>): Promise<ScheduleItem> {
    const response = await fetch(`${this.baseURL}/schedules`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(schedule),
    });
    return response.json();
  }
  
  async updateSchedule(id: string, schedule: Partial<ScheduleItem>): Promise<void> {
    await fetch(`${this.baseURL}/schedules/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(schedule),
    });
  }
  
  async deleteSchedule(id: string): Promise<void> {
    await fetch(`${this.baseURL}/schedules/${id}`, {
      method: 'DELETE',
    });
  }
  
  async startSchedule(id: string): Promise<void> {
    await fetch(`${this.baseURL}/schedules/${id}/start`, {
      method: 'POST',
    });
  }
  
  async stopSchedule(id: string): Promise<void> {
    await fetch(`${this.baseURL}/schedules/${id}/stop`, {
      method: 'POST',
    });
  }
}

export const postingApi = new PostingAPI();
```

---

## 🎯 路由設計

### 1. 更新 App.tsx 路由
```typescript
const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhTW}>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Sidebar collapsed={collapsed} onRefresh={handleRefresh} />
          <Layout>
            <Header
              collapsed={collapsed}
              onToggle={handleToggle}
              onRefresh={handleRefresh}
              lastUpdated={getLastUpdated()}
              loading={isLoading}
            />
            <Content style={{ margin: 0, padding: 0, background: '#f5f5f5' }}>
              <Routes>
                {/* 現有路由 */}
                <Route path="/" element={<DashboardOverview />} />
                <Route path="/system-monitoring" element={<SystemMonitoring />} />
                <Route path="/content-management" element={<ContentManagement />} />
                <Route path="/interaction-analysis" element={<InteractionAnalysis />} />
                
                {/* 新增發文管理路由 */}
                <Route path="/content-management/posting" element={<PostingManagement />} />
                <Route path="/content-management/posting/generator" element={<PostingGenerator />} />
                <Route path="/content-management/posting/review" element={<PostingReview />} />
                <Route path="/content-management/posting/scheduling" element={<DeploymentScheduling />} />
                <Route path="/content-management/posting/tags" element={<TagManagement />} />
                
                {/* 現有其他路由 */}
                <Route path="/content-management/kols/:memberId" element={<KOLDetail />} />
                <Route path="/content-management/posts/:postId" element={<PostDetail />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
};
```

### 2. 更新 Sidebar.tsx 導航
```typescript
const menuItems = [
  // 現有菜單項...
  {
    key: 'content-management',
    label: '內容管理',
    icon: <FileTextOutlined />,
    children: [
      {
        key: '/content-management',
        label: '內容總覽',
      },
      {
        key: '/content-management/kols',
        label: 'KOL 管理',
      },
      {
        key: '/content-management/posts',
        label: '貼文管理',
      },
      {
        key: '/content-management/posting',
        label: '發文管理',
        children: [
          {
            key: '/content-management/posting/generator',
            label: '發文生成器',
          },
          {
            key: '/content-management/posting/review',
            label: '發文審核',
          },
          {
            key: '/content-management/posting/scheduling',
            label: '部署排程',
          },
          {
            key: '/content-management/posting/tags',
            label: '標籤管理',
          },
        ],
      },
    ],
  },
  // 其他現有菜單項...
];
```

---

## 📱 響應式設計

### 1. 斷點設定
```typescript
const breakpoints = {
  xs: 480,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1600,
};

// 在組件中使用
const { xs, sm, md, lg, xl } = breakpoints;
```

### 2. 響應式佈局
```jsx
// 發文生成器響應式佈局
<Row gutter={[16, 16]}>
  <Col xs={24} sm={24} md={12} lg={8} xl={6}>
    <TriggerSelector />
  </Col>
  <Col xs={24} sm={24} md={12} lg={8} xl={6}>
    <DataSourceSelector />
  </Col>
  <Col xs={24} sm={24} md={12} lg={8} xl={6}>
    <ExplainabilityConfig />
  </Col>
  <Col xs={24} sm={24} md={12} lg={8} xl={6}>
    <NewsConfig />
  </Col>
</Row>
```

---

## 🎨 樣式設計

### 1. CSS 變數
```css
:root {
  --primary-color: #1890ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #ff4d4f;
  --text-color: #262626;
  --text-color-secondary: #8c8c8c;
  --background-color: #f5f5f5;
  --border-color: #d9d9d9;
  --border-radius: 6px;
  --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

### 2. 組件樣式
```css
.step-indicator {
  margin: 24px 0;
}

.step-indicator .step-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.step-indicator .step-label {
  text-align: center;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.step-indicator .step-label.active {
  opacity: 1;
}

.step-indicator .step-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.step-indicator .step-description {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.quality-score {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.ai-detection {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
```

---

## 🧪 測試設計

### 1. 單元測試
```typescript
// PostingGenerator.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { PostingGenerator } from '../PostingGenerator';

describe('PostingGenerator', () => {
  it('should render all steps correctly', () => {
    render(<PostingGenerator />);
    
    expect(screen.getByText('觸發器選擇')).toBeInTheDocument();
    expect(screen.getByText('數據源配置')).toBeInTheDocument();
    expect(screen.getByText('解釋層設定')).toBeInTheDocument();
  });
  
  it('should handle step navigation', () => {
    render(<PostingGenerator />);
    
    const nextButton = screen.getByText('下一步');
    fireEvent.click(nextButton);
    
    expect(screen.getByText('數據源配置')).toBeInTheDocument();
  });
});
```

### 2. 整合測試
```typescript
// PostingManagement.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { PostingManagement } from '../PostingManagement';

describe('PostingManagement Integration', () => {
  it('should load and display review items', async () => {
    render(<PostingManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('待審核內容')).toBeInTheDocument();
    });
  });
});
```

---

## 📋 實施檢查清單

### 第一階段：基礎架構
- [ ] 更新 Sidebar.tsx 導航結構
- [ ] 擴展 DashboardOverview.tsx 主頁面
- [ ] 更新 ContentManagement.tsx Tab 結構
- [ ] 創建 PostingStore.ts 狀態管理
- [ ] 創建 PostingAPI.ts API 服務

### 第二階段：核心組件
- [ ] 實現 PostingGenerator.tsx 主組件
- [ ] 實現 TriggerSelector.tsx 觸發器選擇
- [ ] 實現 DataSourceSelector.tsx 數據源選擇
- [ ] 實現 ExplainabilityConfig.tsx 解釋層設定
- [ ] 實現 NewsConfig.tsx 新聞搜尋設定
- [ ] 實現 KOLSelector.tsx KOL 選擇
- [ ] 實現 GenerationSettings.tsx 生成設定
- [ ] 實現 TagSettings.tsx 標籤設定
- [ ] 實現 BatchModeSettings.tsx 批量模式設定

### 第三階段：審核系統
- [ ] 實現 PostingReview.tsx 審核主頁面
- [ ] 實現 ReviewList.tsx 審核列表
- [ ] 實現 ContentEditor.tsx 內容編輯器
- [ ] 實現 QualityChecker.tsx 品質檢查
- [ ] 實現 BatchOperations.tsx 批量操作

### 第四階段：排程管理
- [ ] 實現 DeploymentScheduling.tsx 排程主頁面
- [ ] 實現 ScheduleList.tsx 排程列表
- [ ] 實現 ScheduleEditor.tsx 排程編輯器
- [ ] 實現 ScheduleMonitor.tsx 排程監控
- [ ] 實現 ScheduleLogs.tsx 排程日誌

### 第五階段：標籤管理
- [ ] 實現 TagManagement.tsx 標籤主頁面
- [ ] 實現 StockTags.tsx 股票標籤
- [ ] 實現 TopicTags.tsx 話題標籤
- [ ] 實現 CustomTags.tsx 自定義標籤

### 第六階段：通用組件
- [ ] 實現 StepIndicator.tsx 步驟指示器
- [ ] 實現 ProgressBar.tsx 進度條
- [ ] 實現 QualityScore.tsx 品質評分
- [ ] 實現 AIDetection.tsx AI 檢測

### 第七階段：測試和優化
- [ ] 編寫單元測試
- [ ] 編寫整合測試
- [ ] 性能優化
- [ ] 響應式設計測試
- [ ] 用戶體驗測試

---

## 📝 總結

這個前端設計文稿提供了完整的發文管理系統前端實現方案，包括：

1. **完整的組件架構** - 模組化設計，易於維護和擴展
2. **詳細的頁面設計** - 每個頁面都有具體的實現規格
3. **統一的 UI 組件** - 基於 Ant Design 的統一設計語言
4. **完善的狀態管理** - 使用 Zustand 進行狀態管理
5. **清晰的 API 設計** - RESTful API 接口設計
6. **響應式設計** - 適配不同螢幕尺寸
7. **完整的測試方案** - 單元測試和整合測試
8. **詳細的實施計劃** - 分階段實施，降低風險

這個設計完全基於你現有的架構，可以無縫整合到現有系統中，大大提升開發效率。
