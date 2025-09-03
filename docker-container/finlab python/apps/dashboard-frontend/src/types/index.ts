// API 響應類型定義
export interface ApiResponse {
  timestamp: string;
  [key: string]: any;
}

// 系統監控數據類型
export interface SystemMonitoringData {
  timestamp: string;
  system_overview: {
    total_kols: number;
    active_kols: number;
    total_posts: number;
    published_posts: number;
    success_rate: number;
  };
  microservices: {
    [key: string]: {
      status: string;
      uptime: string;
      response_time: string;
    };
  };
  task_execution: {
    hourly_tasks: { success: number; failed: number; total: number };
    daily_tasks: { success: number; failed: number; total: number };
    weekly_tasks: { success: number; failed: number; total: number };
  };
  data_sources: {
    google_sheets: string;
    cmoney_api: string;
    finlab_api: string;
  };
}

// KOL 數據類型
export interface KOLData {
  serial: string;
  nickname: string;
  member_id: string;
  persona: string;
  status: string;
  content_type: string;
  posting_times: string;
  target_audience: string;
}

// 貼文數據類型
export interface PostData {
  post_id: string;
  kol_serial: string;
  kol_nickname: string;
  kol_id: string;
  persona: string;
  content_type: string;
  topic_id: string;
  topic_title: string;
  content: string;
  status: string;
  post_time: string;
  platform_post_id: string;
  platform_post_url: string;
  // 新增的 KOL 設定欄位
  post_type: string;  // 發文類型
  content_length: string;  // 文章長度
  kol_weight_settings: string;  // KOL權重設定
  content_generation_time: string;  // 內容生成時間
  kol_settings_version: string;  // KOL設定版本
}

// 內容管理數據類型
export interface ContentManagementData {
  timestamp: string;
  kol_list: KOLData[];
  post_list: PostData[];
  statistics: {
    kol_stats: {
      total: number;
      active: number;
      by_persona: { [key: string]: number };
    };
    post_stats: {
      total: number;
      published: number;
      pending: number;
      by_kol: { [key: string]: number };
    };
  };
}

// 互動數據類型
export interface InteractionData {
  article_id: string;
  member_id: string;
  nickname: string;
  title: string;
  content: string;
  topic_id: string;
  is_trending_topic: string;
  post_time: string;
  last_update_time: string;
  likes_count: number;
  comments_count: number;
  total_interactions: number;
  engagement_rate: number;
  growth_rate: number;
  collection_error: string;
}

// 互動分析數據類型
export interface InteractionAnalysisData {
  timestamp: string;
  interaction_data: {
    [key: string]: InteractionData[];
  };
  statistics: {
    [key: string]: {
      total_posts: number;
      total_interactions: number;
      total_likes: number;
      total_comments: number;
      avg_engagement_rate: number;
      kol_performance: {
        [key: string]: {
          total_interactions: number;
          likes: number;
          comments: number;
          posts: number;
        };
      };
    };
  };
  data_source: string;
}

// 導航菜單類型
export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  children?: MenuItem[];
}

// 載入狀態類型
export interface LoadingState {
  systemMonitoring: boolean;
  contentManagement: boolean;
  interactionAnalysis: boolean;
}
