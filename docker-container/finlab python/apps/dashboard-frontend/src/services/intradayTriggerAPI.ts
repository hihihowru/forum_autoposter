import axios from 'axios';
import { createApiUrl, API_ENDPOINTS } from '../config/api';

export interface IntradayTriggerConfig {
  endpoint: string;
  processing: any[];
}

export interface StockInfo {
  stock_code: string;
  stock_name: string;
  industry: string;
}

export interface IntradayTriggerResult {
  success: boolean;
  stocks: string[] | StockInfo[];  // 支持兩種格式：舊格式（字符串數組）和新格式（對象數組）
  data: any[];
  error?: string;
  count?: number;
}

class IntradayTriggerAPI {
  static async executeTrigger(config: IntradayTriggerConfig): Promise<IntradayTriggerResult> {
    try {
      console.log('🚀 [前端] 執行盤中觸發器:', config);
      
      // 使用 Vercel Rewrites 調用 API
      const apiUrl = createApiUrl(API_ENDPOINTS.INTRADAY_TRIGGER);
      console.log('🌐 [前端] 請求 URL (通過 Vercel Rewrites):', apiUrl);
      
      const response = await axios.get(apiUrl, {
        params: config,  // 將配置作為查詢參數
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000
      });

      console.log('📡 [前端] 後端響應狀態:', response.status);
      console.log('📊 [前端] 後端響應數據:', response.data);

      if (response.data.success) {
        console.log('✅ [前端] 盤中觸發器執行成功:', response.data);
        return {
          success: true,
          stocks: response.data.stocks,
          data: response.data.data
        };
      } else {
        console.error('❌ [前端] 盤中觸發器執行失敗:', response.data);
        return {
          success: false,
          stocks: [],
          data: [],
          error: response.data.error || '執行失敗'
        };
      }
    } catch (error) {
      console.error('❌ [前端] 盤中觸發器執行失敗:', error);
      if (axios.isAxiosError(error)) {
        console.error('📡 [前端] HTTP 錯誤詳情:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          url: error.config?.url
        });
      }
      return {
        success: false,
        stocks: [],
        data: [],
        error: error instanceof Error ? error.message : '未知錯誤'
      };
    }
  }
}

export default IntradayTriggerAPI;