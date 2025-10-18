/**
 * API 配置
 * 統一管理所有 API 端點
 * 直接調用 Railway 後端 (CORS 已啟用)
 */

// Railway 後端 URL
const RAILWAY_API_URL = 'https://forumautoposter-production.up.railway.app';

// 環境變數配置
const getApiConfig = () => {
  // 開發環境
  if ((import.meta as any).env.DEV) {
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

  // 生產環境 - 直接調用 Railway 後端
  return {
    BASE_URL: RAILWAY_API_URL,
    OHLC_API: RAILWAY_API_URL,
    TRENDING_API: RAILWAY_API_URL,
    ANALYZE_API: RAILWAY_API_URL,
    FINANCIAL_API: RAILWAY_API_URL,
    SUMMARY_API: RAILWAY_API_URL,
    DASHBOARD_API: RAILWAY_API_URL,
  };
};

export const API_CONFIG = getApiConfig();

// API 端點映射
export const API_ENDPOINTS = {
  // OHLC API - After Hours Triggers
  AFTER_HOURS_LIMIT_UP: '/api/after_hours_limit_up',
  AFTER_HOURS_LIMIT_DOWN: '/api/after_hours_limit_down',
  AFTER_HOURS_VOLUME_AMOUNT_HIGH: '/api/after_hours_volume_amount_high',
  AFTER_HOURS_VOLUME_AMOUNT_LOW: '/api/after_hours_volume_amount_low',
  AFTER_HOURS_VOLUME_CHANGE_RATE_HIGH: '/api/after_hours_volume_change_rate_high',
  AFTER_HOURS_VOLUME_CHANGE_RATE_LOW: '/api/after_hours_volume_change_rate_low',

  // Stock Data
  INDUSTRIES: '/api/industries',
  STOCKS_BY_INDUSTRY: '/api/stocks_by_industry',
  GET_OHLC: '/api/get_ohlc',
  
  // Posting Service
  POSTING_SERVICE: '/api/posting',
  MANUAL_POSTING: '/api/manual-posting',
  
  // Dashboard API
  DASHBOARD_HEALTH: '/api/health',
  SYSTEM_MONITORING: '/api/dashboard/system-monitoring',
  CONTENT_MANAGEMENT: '/api/dashboard/content-management',
  INTERACTION_ANALYSIS: '/api/dashboard/interaction-analysis',

  // Trending API
  TRENDING_TOPICS: '/api/trending',
  EXTRACT_KEYWORDS: '/api/extract-keywords',
  SEARCH_STOCKS: '/api/search-stocks-by-keywords',
  ANALYZE_TOPIC: '/api/analyze-topic',
  GENERATE_CONTENT: '/api/generate-content',

  // Intraday Triggers - 6 separate endpoints
  INTRADAY_TRIGGER: '/api/intraday-trigger/execute',
  INTRADAY_GAINERS_BY_AMOUNT: '/api/intraday/gainers-by-amount',
  INTRADAY_VOLUME_LEADERS: '/api/intraday/volume-leaders',
  INTRADAY_AMOUNT_LEADERS: '/api/intraday/amount-leaders',
  INTRADAY_LIMIT_DOWN: '/api/intraday/limit-down',
  INTRADAY_LIMIT_UP: '/api/intraday/limit-up',
  INTRADAY_LIMIT_DOWN_BY_AMOUNT: '/api/intraday/limit-down-by-amount',
};

// 創建完整的 API URL
export const createApiUrl = (endpoint: string, service: 'OHLC' | 'BASE' | 'TRENDING' | 'ANALYZE' | 'FINANCIAL' | 'SUMMARY' | 'DASHBOARD' = 'BASE') => {
  let baseUrl = API_CONFIG[`${service}_API` as keyof typeof API_CONFIG] || API_CONFIG.BASE_URL;

  const fullUrl = `${baseUrl}${endpoint}`;
  console.log(`🔗 createApiUrl: ${fullUrl}`);
  return fullUrl;
};

// 獲取 API 基礎 URL - 簡單版本，直接返回 BASE_URL
export const getApiBaseUrl = () => {
  return API_CONFIG.BASE_URL;
};

export default API_CONFIG;