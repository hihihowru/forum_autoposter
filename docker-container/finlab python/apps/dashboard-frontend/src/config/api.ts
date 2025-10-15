/**
 * API 配置
 * 統一管理所有 API 端點
 */

// 環境變數配置
const getApiConfig = () => {
  // 開發環境
  if (import.meta.env.DEV) {
    return {
      BASE_URL: 'http://localhost:8001',
      OHLC_API: 'http://localhost:8005',
      TRENDING_API: 'http://localhost:8004',
      ANALYZE_API: 'http://localhost:8002',
      FINANCIAL_API: 'http://localhost:8006',
      SUMMARY_API: 'http://localhost:8003',
      DASHBOARD_API: 'http://localhost:8012',
    };
  }
  
  // 生產環境 - 使用統一的 API 網關
  const railwayBaseUrl = import.meta.env.VITE_RAILWAY_URL || 'https://forumautoposter-production.up.railway.app';
  
  return {
    BASE_URL: railwayBaseUrl,
    OHLC_API: railwayBaseUrl, // 通過 API 網關路由
    TRENDING_API: railwayBaseUrl,
    ANALYZE_API: railwayBaseUrl,
    FINANCIAL_API: railwayBaseUrl,
    SUMMARY_API: railwayBaseUrl,
    DASHBOARD_API: railwayBaseUrl,
  };
};

export const API_CONFIG = getApiConfig();

// API 端點映射
export const API_ENDPOINTS = {
  // OHLC API
  AFTER_HOURS_LIMIT_UP: '/after_hours_limit_up',
  AFTER_HOURS_LIMIT_DOWN: '/after_hours_limit_down',
  INDUSTRIES: '/industries',
  STOCKS_BY_INDUSTRY: '/stocks_by_industry',
  GET_OHLC: '/get_ohlc',
  
  // Posting Service
  POSTING_SERVICE: '/api/posting',
  MANUAL_POSTING: '/api/manual-posting',
  
  // Dashboard API
  DASHBOARD_HEALTH: '/health',
  SYSTEM_MONITORING: '/dashboard/system-monitoring',
  CONTENT_MANAGEMENT: '/dashboard/content-management',
  INTERACTION_ANALYSIS: '/dashboard/interaction-analysis',
  
  // Trending API
  TRENDING_TOPICS: '/trending',
  EXTRACT_KEYWORDS: '/extract-keywords',
  SEARCH_STOCKS: '/search-stocks-by-keywords',
  ANALYZE_TOPIC: '/analyze-topic',
  GENERATE_CONTENT: '/generate-content',
};

// 創建完整的 API URL
export const createApiUrl = (endpoint: string, service: 'OHLC' | 'BASE' | 'TRENDING' | 'ANALYZE' | 'FINANCIAL' | 'SUMMARY' | 'DASHBOARD' = 'BASE') => {
  const baseUrl = API_CONFIG[`${service}_API`] || API_CONFIG.BASE_URL;
  return `${baseUrl}${endpoint}`;
};

export default API_CONFIG;
