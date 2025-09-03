import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  SystemMonitoringData,
  ContentManagementData,
  InteractionAnalysisData,
  LoadingState
} from '../types';
import { ApiService } from '../services/api';

interface DashboardState {
  // 數據狀態
  systemMonitoringData: SystemMonitoringData | null;
  contentManagementData: ContentManagementData | null;
  interactionAnalysisData: InteractionAnalysisData | null;
  
  // 載入狀態
  loading: LoadingState;
  
  // 錯誤狀態
  errors: {
    systemMonitoring: string | null;
    contentManagement: string | null;
    interactionAnalysis: string | null;
  };
  
  // 最後更新時間
  lastUpdated: {
    systemMonitoring: string | null;
    contentManagement: string | null;
    interactionAnalysis: string | null;
  };
  
  // Actions
  fetchSystemMonitoring: () => Promise<void>;
  fetchContentManagement: () => Promise<void>;
  fetchInteractionAnalysis: () => Promise<void>;
  refreshAllData: () => Promise<void>;
  clearErrors: () => void;
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    (set, get) => ({
      // 初始狀態
      systemMonitoringData: null,
      contentManagementData: null,
      interactionAnalysisData: null,
      
      loading: {
        systemMonitoring: false,
        contentManagement: false,
        interactionAnalysis: false,
      },
      
      errors: {
        systemMonitoring: null,
        contentManagement: null,
        interactionAnalysis: null,
      },
      
      lastUpdated: {
        systemMonitoring: null,
        contentManagement: null,
        interactionAnalysis: null,
      },
      
      // 獲取系統監控數據
      fetchSystemMonitoring: async () => {
        set((state) => ({
          loading: { ...state.loading, systemMonitoring: true },
          errors: { ...state.errors, systemMonitoring: null },
        }));
        
        // 重試機制
        let retries = 0;
        const maxRetries = 2;
        
        while (retries <= maxRetries) {
          try {
            const data = await ApiService.getSystemMonitoring();
            set((state) => ({
              systemMonitoringData: data,
              loading: { ...state.loading, systemMonitoring: false },
              lastUpdated: { ...state.lastUpdated, systemMonitoring: new Date().toISOString() },
            }));
            return; // 成功則退出
          } catch (error) {
            retries++;
            if (retries > maxRetries) {
              let errorMessage = '獲取系統監控數據失敗';
              if (error && typeof error === 'object' && 'response' in error) {
                const axiosError = error as any;
                if (axiosError.response?.status === 500) {
                  errorMessage = '後端服務器錯誤，請檢查後端日誌';
                } else if (axiosError.response?.status) {
                  errorMessage = `HTTP ${axiosError.response.status}: ${axiosError.response.statusText}`;
                }
              } else if (error instanceof Error) {
                errorMessage = error.message;
              }
              set((state) => ({
                loading: { ...state.loading, systemMonitoring: false },
                errors: { ...state.errors, systemMonitoring: errorMessage },
              }));
            } else {
              // 等待後重試
              console.log(`系統監控 API 重試 ${retries}/${maxRetries}`);
              await new Promise(resolve => setTimeout(resolve, 1000 * retries));
            }
          }
        }
      },
      
      // 獲取內容管理數據
      fetchContentManagement: async () => {
        set((state) => ({
          loading: { ...state.loading, contentManagement: true },
          errors: { ...state.errors, contentManagement: null },
        }));
        
        // 重試機制
        let retries = 0;
        const maxRetries = 2;
        
        while (retries <= maxRetries) {
          try {
            const data = await ApiService.getContentManagement();
            set((state) => ({
              contentManagementData: data,
              loading: { ...state.loading, contentManagement: false },
              lastUpdated: { ...state.lastUpdated, contentManagement: new Date().toISOString() },
            }));
            return; // 成功則退出
          } catch (error) {
            retries++;
            if (retries > maxRetries) {
              const errorMessage = error instanceof Error ? error.message : '獲取內容管理數據失敗';
              set((state) => ({
                loading: { ...state.loading, contentManagement: false },
                errors: { ...state.errors, contentManagement: errorMessage },
              }));
            } else {
              // 等待後重試
              await new Promise(resolve => setTimeout(resolve, 1000 * retries));
            }
          }
        }
      },
      
      // 獲取互動分析數據
      fetchInteractionAnalysis: async () => {
        set((state) => ({
          loading: { ...state.loading, interactionAnalysis: true },
          errors: { ...state.errors, interactionAnalysis: null },
        }));
        
        // 重試機制
        let retries = 0;
        const maxRetries = 2;
        
        while (retries <= maxRetries) {
          try {
            const data = await ApiService.getInteractionAnalysis();
            set((state) => ({
              interactionAnalysisData: data,
              loading: { ...state.loading, interactionAnalysis: false },
              lastUpdated: { ...state.lastUpdated, interactionAnalysis: new Date().toISOString() },
            }));
            return; // 成功則退出
          } catch (error) {
            retries++;
            if (retries > maxRetries) {
              const errorMessage = error instanceof Error ? error.message : '獲取互動分析數據失敗';
              set((state) => ({
                loading: { ...state.loading, interactionAnalysis: false },
                errors: { ...state.errors, interactionAnalysis: errorMessage },
              }));
            } else {
              // 等待後重試
              await new Promise(resolve => setTimeout(resolve, 1000 * retries));
            }
          }
        }
      },
      
      // 刷新所有數據
      refreshAllData: async () => {
        const { fetchSystemMonitoring, fetchContentManagement, fetchInteractionAnalysis } = get();
        
        await Promise.allSettled([
          fetchSystemMonitoring(),
          fetchContentManagement(),
          fetchInteractionAnalysis(),
        ]);
      },
      
      // 清除錯誤
      clearErrors: () => {
        set({
          errors: {
            systemMonitoring: null,
            contentManagement: null,
            interactionAnalysis: null,
          },
        });
      },
    }),
    {
      name: 'dashboard-store',
    }
  )
);
