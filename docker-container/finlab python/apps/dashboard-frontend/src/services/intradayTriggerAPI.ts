import axios from 'axios';

export interface IntradayTriggerConfig {
  endpoint: string;
  processing: any[];
}

export interface IntradayTriggerResult {
  success: boolean;
  stocks: string[];
  data: any[];
  error?: string;
}

class IntradayTriggerAPI {
  static async executeTrigger(config: IntradayTriggerConfig): Promise<IntradayTriggerResult> {
    try {
      console.log('🚀 [前端] 執行盤中觸發器:', config);
      console.log('🌐 [前端] 請求 URL:', `/intraday-trigger/execute`);
      
      // 使用相對路徑，通過 Vite 代理訪問後端
      const response = await axios.post(
        `/intraday-trigger/execute`,
        config,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 30000
        }
      );

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
