# 虛擬 KOL 儀表板設計指南

## 🎨 設計原則

### 整體設計風格
- **簡潔專業**: 金融數據儀表板的專業感
- **數據驅動**: 突出數據可視化，減少裝飾性元素
- **響應式設計**: 支援桌面、平板、手機多端適配
- **實時更新**: 數據自動刷新，保持時效性

### 色彩方案
```css
/* 主色調 - 專業藍 */
--primary-color: #1890ff;
--primary-hover: #40a9ff;
--primary-active: #096dd9;

/* 功能色 */
--success-color: #52c41a;  /* 成功/健康狀態 */
--warning-color: #faad14;  /* 警告/注意 */
--error-color: #ff4d4f;    /* 錯誤/異常 */
--info-color: #13c2c2;     /* 信息/中性 */

/* 中性色 */
--text-primary: #262626;
--text-secondary: #595959;
--text-disabled: #bfbfbf;
--background: #f5f5f5;
--border: #d9d9d9;
```

### 字體規範
```css
/* 字體族 */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

/* 字體大小 */
--font-size-h1: 24px;    /* 頁面標題 */
--font-size-h2: 20px;    /* 區塊標題 */
--font-size-h3: 16px;    /* 卡片標題 */
--font-size-body: 14px;  /* 正文 */
--font-size-caption: 12px; /* 說明文字 */

/* 字體粗細 */
--font-weight-bold: 600;
--font-weight-medium: 500;
--font-weight-normal: 400;
```

---

## 🏗️ 前端架構設計

### 技術棧
```json
{
  "framework": "React 18",
  "ui_library": "Ant Design 5.x",
  "charts": "Ant Design Charts (@ant-design/charts)",
  "state_management": "Zustand",
  "routing": "React Router v6",
  "http_client": "Axios",
  "build_tool": "Vite",
  "typescript": "TypeScript 5.x",
  "styling": "CSS Modules + Ant Design"
}
```

### 專案結構
```
dashboard-frontend/
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── components/           # 可重用組件
│   │   ├── common/          # 通用組件
│   │   │   ├── MetricCard/
│   │   │   ├── StatusIndicator/
│   │   │   ├── DataTable/
│   │   │   └── LoadingSpinner/
│   │   ├── charts/          # 圖表組件
│   │   │   ├── LineChart/
│   │   │   ├── BarChart/
│   │   │   ├── PieChart/
│   │   │   ├── GaugeChart/
│   │   │   └── HeatmapChart/
│   │   └── layout/          # 布局組件
│   │       ├── Header/
│   │       ├── Sidebar/
│   │       ├── Breadcrumb/
│   │       └── Footer/
│   ├── pages/               # 頁面組件
│   │   ├── SystemMonitor/   # 系統監控儀表板
│   │   ├── ContentAnalysis/ # 內容分析儀表板
│   │   ├── EngagementAnalytics/ # 互動數據儀表板
│   │   └── NotFound/
│   ├── hooks/               # 自定義 Hooks
│   │   ├── useApi.ts
│   │   ├── useWebSocket.ts
│   │   └── useRealTimeData.ts
│   ├── services/            # API 服務
│   │   ├── api.ts
│   │   ├── system.ts
│   │   ├── content.ts
│   │   └── engagement.ts
│   ├── stores/              # 狀態管理
│   │   ├── systemStore.ts
│   │   ├── contentStore.ts
│   │   └── engagementStore.ts
│   ├── types/               # TypeScript 類型
│   │   ├── api.ts
│   │   ├── system.ts
│   │   ├── content.ts
│   │   └── engagement.ts
│   ├── utils/               # 工具函數
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── styles/              # 樣式文件
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── components.css
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## 📊 組件設計規範

### 1. MetricCard 組件
```typescript
interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
  };
  icon?: React.ReactNode;
  loading?: boolean;
  size?: 'small' | 'default' | 'large';
}

// 使用範例
<MetricCard
  title="今日生成內容"
  value={156}
  change={{ value: 12.5, type: 'increase' }}
  icon={<FileTextOutlined />}
/>
```

### 2. StatusIndicator 組件
```typescript
interface StatusIndicatorProps {
  status: 'healthy' | 'warning' | 'error' | 'offline';
  label: string;
  showIcon?: boolean;
}

// 使用範例
<StatusIndicator status="healthy" label="OHLC API" showIcon />
```

### 3. DataTable 組件
```typescript
interface DataTableProps<T> {
  data: T[];
  columns: ColumnType<T>[];
  loading?: boolean;
  pagination?: boolean;
  searchable?: boolean;
  exportable?: boolean;
}

// 使用範例
<DataTable
  data={memberList}
  columns={memberColumns}
  searchable
  exportable
/>
```

### 4. Chart 組件規範
```typescript
// 統一的 Chart 組件接口
interface BaseChartProps {
  data: any[];
  loading?: boolean;
  height?: number;
  color?: string | string[];
  tooltip?: boolean;
  legend?: boolean;
}

// LineChart 範例
<LineChart
  data={responseTimeData}
  xField="time"
  yField="value"
  seriesField="service"
  height={300}
  color={['#1890ff', '#52c41a', '#faad14']}
/>
```

---

## 🎯 三張儀表板詳細設計

### 第一張：系統運營監控儀表板

#### 布局設計
```
┌─────────────────────────────────────────────────────────────┐
│ 系統運營監控儀表板                    [刷新] [設置] [全屏]    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │服務狀態 │ │任務隊列 │ │CPU使用率│ │記憶體   │ │網路流量 │ │
│ │  🟢 6/6 │ │  📊 12  │ │  45%    │ │ 2.1GB   │ │ 1.2MB/s │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                服務響應時間趨勢                         │ │
│ │  [LineChart - 各服務響應時間變化]                       │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │   錯誤率統計    │ │           實時日誌流                │ │
│ │  [BarChart]     │ │  [Scrollable Log List]              │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 組件配置
```typescript
// 系統監控頁面組件
const SystemMonitorPage: React.FC = () => {
  return (
    <PageContainer title="系統運營監控" extra={<PageHeaderExtra />}>
      <Row gutter={[16, 16]}>
        {/* 服務狀態卡片 */}
        <Col span={24}>
          <Row gutter={16}>
            <Col span={4}>
              <MetricCard
                title="服務狀態"
                value="6/6"
                icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                change={{ value: 0, type: 'neutral' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="任務隊列"
                value={12}
                icon={<DatabaseOutlined />}
                change={{ value: -2, type: 'decrease' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="CPU使用率"
                value="45%"
                icon={<CpuOutlined />}
                change={{ value: 5, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="記憶體"
                value="2.1GB"
                icon={<MemoryOutlined />}
                change={{ value: 0.2, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="網路流量"
                value="1.2MB/s"
                icon={<WifiOutlined />}
                change={{ value: 0.1, type: 'increase' }}
              />
            </Col>
          </Row>
        </Col>

        {/* 響應時間趨勢圖 */}
        <Col span={24}>
          <Card title="服務響應時間趨勢" extra={<RefreshButton />}>
            <LineChart
              data={responseTimeData}
              xField="time"
              yField="responseTime"
              seriesField="service"
              height={300}
            />
          </Card>
        </Col>

        {/* 錯誤率統計和實時日誌 */}
        <Col span={12}>
          <Card title="錯誤率統計">
            <BarChart
              data={errorRateData}
              xField="service"
              yField="errorRate"
              height={250}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="實時日誌流">
            <RealTimeLog data={logData} />
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
};
```

### 第二張：內容生成與發布儀表板

#### 布局設計
```
┌─────────────────────────────────────────────────────────────┐
│ 內容生成與發布儀表板                [刷新] [設置] [全屏]    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │今日生成 │ │發布成功 │ │KOL使用  │ │熱門話題 │ │內容品質 │ │
│ │  156    │ │  98.5%  │ │ 5種類型 │ │  12個   │ │  8.2分  │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                內容生成量趨勢                           │ │
│ │  [LineChart - 每日/每週/每月的生成量變化]                │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │   KOL使用分布   │ │           發布成功率                │ │
│ │  [PieChart]     │ │  [GaugeChart]                       │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                Member ID 列表查詢                      │ │
│ │  [DataTable - 可搜尋、可導出]                          │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                Article 列表查詢                        │ │
│ │  [DataTable - 可篩選、可導出]                          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 組件配置
```typescript
// 內容分析頁面組件
const ContentAnalysisPage: React.FC = () => {
  return (
    <PageContainer title="內容生成與發布" extra={<PageHeaderExtra />}>
      <Row gutter={[16, 16]}>
        {/* 關鍵指標卡片 */}
        <Col span={24}>
          <Row gutter={16}>
            <Col span={4}>
              <MetricCard
                title="今日生成"
                value={156}
                icon={<FileTextOutlined />}
                change={{ value: 12.5, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="發布成功"
                value="98.5%"
                icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                change={{ value: 1.2, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="KOL使用"
                value="5種類型"
                icon={<TeamOutlined />}
                change={{ value: 0, type: 'neutral' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="熱門話題"
                value={12}
                icon={<FireOutlined />}
                change={{ value: 3, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="內容品質"
                value="8.2分"
                icon={<StarOutlined />}
                change={{ value: 0.3, type: 'increase' }}
              />
            </Col>
          </Row>
        </Col>

        {/* 內容生成量趨勢 */}
        <Col span={24}>
          <Card title="內容生成量趨勢" extra={<TimeRangeSelector />}>
            <LineChart
              data={generationTrendData}
              xField="date"
              yField="count"
              seriesField="type"
              height={300}
            />
          </Card>
        </Col>

        {/* KOL使用分布和發布成功率 */}
        <Col span={12}>
          <Card title="KOL使用分布">
            <PieChart
              data={kolUsageData}
              angleField="value"
              colorField="type"
              height={250}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="發布成功率">
            <GaugeChart
              data={publishingSuccessRate}
              height={250}
            />
          </Card>
        </Col>

        {/* Member ID 列表查詢 */}
        <Col span={24}>
          <Card title="Member ID 列表查詢" extra={<ExportButton />}>
            <DataTable
              data={memberList}
              columns={memberColumns}
              searchable
              exportable
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>

        {/* Article 列表查詢 */}
        <Col span={24}>
          <Card title="Article 列表查詢" extra={<ExportButton />}>
            <DataTable
              data={articleList}
              columns={articleColumns}
              searchable
              exportable
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
};
```

### 第三張：互動數據分析儀表板

#### 布局設計
```
┌─────────────────────────────────────────────────────────────┐
│ 互動數據分析儀表板                  [刷新] [設置] [全屏]    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │總互動數 │ │互動率   │ │KOL排名  │ │成長率   │ │用戶活躍 │ │
│ │ 2,456   │ │  12.3%  │ │ 技術派  │ │ +15.2%  │ │  85%    │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                互動數據趨勢                             │ │
│ │  [LineChart - 按讚、留言、收藏的趨勢變化]                │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │   KOL表現對比   │ │           熱門內容排行榜            │ │
│ │  [BarChart]     │ │  [DataTable]                        │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                成長率分析                               │ │
│ │  [MultiLineChart - 1hr/1day/7days 成長率]              │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 組件配置
```typescript
// 互動數據分析頁面組件
const EngagementAnalyticsPage: React.FC = () => {
  return (
    <PageContainer title="互動數據分析" extra={<PageHeaderExtra />}>
      <Row gutter={[16, 16]}>
        {/* 關鍵指標卡片 */}
        <Col span={24}>
          <Row gutter={16}>
            <Col span={4}>
              <MetricCard
                title="總互動數"
                value="2,456"
                icon={<HeartOutlined />}
                change={{ value: 15.2, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="互動率"
                value="12.3%"
                icon={<PercentageOutlined />}
                change={{ value: 2.1, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="KOL排名"
                value="技術派"
                icon={<TrophyOutlined />}
                change={{ value: 0, type: 'neutral' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="成長率"
                value="+15.2%"
                icon={<RiseOutlined />}
                change={{ value: 3.5, type: 'increase' }}
              />
            </Col>
            <Col span={4}>
              <MetricCard
                title="用戶活躍"
                value="85%"
                icon={<UserOutlined />}
                change={{ value: 5.2, type: 'increase' }}
              />
            </Col>
          </Row>
        </Col>

        {/* 互動數據趨勢 */}
        <Col span={24}>
          <Card title="互動數據趨勢" extra={<TimeRangeSelector />}>
            <LineChart
              data={engagementTrendData}
              xField="date"
              yField="count"
              seriesField="type"
              height={300}
            />
          </Card>
        </Col>

        {/* KOL表現對比和熱門內容排行榜 */}
        <Col span={12}>
          <Card title="KOL表現對比">
            <BarChart
              data={kolPerformanceData}
              xField="kol"
              yField="engagement"
              height={300}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="熱門內容排行榜">
            <DataTable
              data={topContentData}
              columns={topContentColumns}
              pagination={{ pageSize: 5 }}
            />
          </Card>
        </Col>

        {/* 成長率分析 */}
        <Col span={24}>
          <Card title="成長率分析">
            <LineChart
              data={growthRateData}
              xField="time"
              yField="rate"
              seriesField="period"
              height={300}
            />
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
};
```

---

## 🔧 技術實作細節

### API 服務層設計
```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8007',
  timeout: 10000,
});

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 響應攔截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

### 狀態管理設計
```typescript
// stores/systemStore.ts
import { create } from 'zustand';

interface SystemState {
  services: Service[];
  tasks: Task[];
  metrics: SystemMetrics;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchServices: () => Promise<void>;
  fetchTasks: () => Promise<void>;
  fetchMetrics: () => Promise<void>;
  refreshData: () => Promise<void>;
}

export const useSystemStore = create<SystemState>((set, get) => ({
  services: [],
  tasks: [],
  metrics: {} as SystemMetrics,
  loading: false,
  error: null,

  fetchServices: async () => {
    set({ loading: true, error: null });
    try {
      const services = await api.get('/api/v1/system/services');
      set({ services, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const tasks = await api.get('/api/v1/system/tasks');
      set({ tasks, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  fetchMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const metrics = await api.get('/api/v1/system/metrics');
      set({ metrics, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  refreshData: async () => {
    const { fetchServices, fetchTasks, fetchMetrics } = get();
    await Promise.all([
      fetchServices(),
      fetchTasks(),
      fetchMetrics()
    ]);
  }
}));
```

### 實時數據更新
```typescript
// hooks/useRealTimeData.ts
import { useEffect, useRef } from 'react';
import { useSystemStore } from '../stores/systemStore';

export const useRealTimeData = (interval: number = 30000) => {
  const { refreshData } = useSystemStore();
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    // 初始載入
    refreshData();

    // 設置定時刷新
    intervalRef.current = setInterval(refreshData, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [refreshData, interval]);

  return { refreshData };
};
```

---

## 📱 響應式設計

### 斷點設置
```css
/* 響應式斷點 */
@media (max-width: 576px) {
  /* 手機 */
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 577px) and (max-width: 768px) {
  /* 平板 */
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  /* 小桌面 */
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1201px) {
  /* 大桌面 */
  .dashboard-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
```

### 移動端適配
```typescript
// 響應式配置
const responsiveConfig = {
  xs: { span: 24 },      // 手機
  sm: { span: 12 },      // 平板
  md: { span: 8 },       // 小桌面
  lg: { span: 6 },       // 大桌面
  xl: { span: 4 },       // 超大桌面
};

// 使用範例
<Col {...responsiveConfig}>
  <MetricCard {...cardProps} />
</Col>
```

---

## 🚀 部署配置

### 環境變數配置
```bash
# .env.development
REACT_APP_API_BASE_URL=http://localhost:8007
REACT_APP_WS_URL=ws://localhost:8007/ws
REACT_APP_ENV=development

# .env.production
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com/ws
REACT_APP_ENV=production
```

### Docker 配置
```dockerfile
# Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置
```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8007;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://backend:8007;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## ✅ 開發檢查清單

### 前端開發檢查清單
- [ ] 專案結構符合設計規範
- [ ] 所有組件使用 TypeScript
- [ ] 響應式設計適配所有斷點
- [ ] 圖表組件正確配置
- [ ] 實時數據更新正常
- [ ] 錯誤處理完善
- [ ] 載入狀態處理
- [ ] 無障礙設計 (a11y)
- [ ] 性能優化 (懶加載、虛擬滾動)
- [ ] 單元測試覆蓋

### 後端 API 檢查清單
- [ ] API 接口符合前端需求
- [ ] 數據格式統一
- [ ] 錯誤處理完善
- [ ] 認證授權正確
- [ ] 性能優化 (緩存、索引)
- [ ] 文檔完整
- [ ] 測試覆蓋

### 部署檢查清單
- [ ] 環境變數配置正確
- [ ] Docker 配置完整
- [ ] Nginx 配置正確
- [ ] SSL 證書配置
- [ ] 監控和日誌配置
- [ ] 備份策略
- [ ] 災難恢復計劃

---

*設計指南版本: v1.0*  
*最後更新: 2024-01-01*  
*適用於: Ant Design Dashboard*
