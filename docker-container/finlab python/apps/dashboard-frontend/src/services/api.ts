import axios from 'axios';
import type {
  SystemMonitoringData,
  ContentManagementData,
  InteractionAnalysisData,
  KOLData,
  PostData
} from '../types';

// 創建 axios 實例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000, // 增加到 30 秒
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 如果需要跨域攜帶 cookie
});

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.warn(`API 請求超時: ${error.config.url}，建議檢查後端服務響應速度`);
    } else {
      console.error('API Response Error:', error);
    }
    return Promise.reject(error);
  }
);

// API 服務類
export class ApiService {
  // 獲取系統監控數據
  static async getSystemMonitoring(): Promise<SystemMonitoringData> {
    const response = await api.get('/dashboard/system-monitoring');
    return response.data;
  }

  // 獲取內容管理數據
  static async getContentManagement(): Promise<ContentManagementData> {
    const response = await api.get('/dashboard/content-management');
    return response.data;
  }

  // 獲取互動分析數據
  static async getInteractionAnalysis(): Promise<InteractionAnalysisData> {
    const response = await api.get('/dashboard/interaction-analysis');
    return response.data;
  }

  // 獲取特定 KOL 詳細信息
  static async getKOLDetails(memberId: string): Promise<KOLData> {
    const response = await api.get(`/dashboard/kols/${memberId}`);
    return response.data;
  }

  // 獲取特定文章詳細信息
  static async getArticleDetails(articleId: string): Promise<PostData> {
    const response = await api.get(`/dashboard/article/${articleId}`);
    return response.data;
  }

  // 健康檢查
  static async healthCheck(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  }
}

export default api;
