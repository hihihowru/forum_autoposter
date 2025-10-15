import React, { useState, useEffect } from 'react';
import { Layout, ConfigProvider } from 'antd';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import zhTW from 'antd/locale/zh_TW';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-tw';

import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import DashboardOverview from './components/Dashboard/DashboardOverview';
import SystemMonitoring from './components/Dashboard/SystemMonitoring';
import ContentManagement from './components/Dashboard/ContentManagement';
import InteractionAnalysis from './components/Dashboard/InteractionAnalysis';
import KOLDetail from './components/KOL/KOLDetail';
import PostDetail from './components/Dashboard/PostDetail';

import SimpleTest from './SimpleTest';
import { useDashboardStore } from './stores/dashboardStore';

// 發文管理組件
import PostingManagement from './components/PostingManagement/PostingManagement';
import PostingGenerator from './components/PostingManagement/PostingGenerator/PostingGenerator';
import PostingReview from './components/PostingManagement/PostingReview/PostingReview';
import PostingDashboard from './components/PostingManagement/PostingDashboard';
import AfterHoursLimitUpTest from './components/PostingManagement/AfterHoursLimitUpTest';
import PublishSuccessPage from './components/PostingManagement/PublishSuccess/PublishSuccessPage';
import PublishedPostsPage from './pages/PublishedPostsPage';
import KOLManagementPage from './components/KOL/KOLManagementPage';
import KOLDetailPage from './components/KOL/KOLDetail';

// 新增的發文管理組件
import BatchHistoryPage from './components/PostingManagement/BatchHistory/BatchHistoryPage';
import ScheduleManagementPage from './components/PostingManagement/ScheduleManagement/ScheduleManagementPage';
import SelfLearningPage from './pages/SelfLearningPage';
import InteractionAnalysisPage from './components/Dashboard/InteractionAnalysis';
// import PerformanceAnalysisPage from './pages/PerformanceAnalysisPage'; // 檔案不存在，暫時註解
import ManualPostingPage from './components/PostingManagement/ManualPostingPage';

// 系統設置和用戶管理組件
import SettingsPage from './components/Settings/SettingsPage';
import UserManagement from './components/UserManagement/UserManagement';

// 設置 dayjs 語言
dayjs.locale('zh-tw');

const { Content } = Layout;

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  
  // 暫時註釋store調用，使用模擬數據
  // const {
  //   systemMonitoringData,
  //   contentManagementData,
  //   interactionAnalysisData,
  //   loading,
  //   errors,
  //   lastUpdated,
  //   refreshAllData,
  // } = useDashboardStore();

  // 模擬數據
  const systemMonitoringData = null;
  const contentManagementData = null;
  const interactionAnalysisData = null;
  const loading = { systemMonitoring: false, contentManagement: false, interactionAnalysis: false };
  const errors = { systemMonitoring: null, contentManagement: null, interactionAnalysis: null };
  const lastUpdated = { systemMonitoring: null, contentManagement: null, interactionAnalysis: null };
  const refreshAllData = () => Promise.resolve();

  // 組件掛載時載入數據
  // useEffect(() => {
  //   refreshAllData();
  // }, [refreshAllData]);

  // 處理刷新
  const handleRefresh = () => {
    refreshAllData();
  };

  // 處理側邊欄切換
  const handleToggle = () => {
    setCollapsed(!collapsed);
  };

  // 獲取最後更新時間
  const getLastUpdated = () => {
    const times = Object.values(lastUpdated).filter(Boolean);
    if (times.length === 0) return undefined;
    return times.sort().pop() || undefined;
  };

  // 檢查是否有載入中
  const isLoading = Object.values(loading).some(Boolean);

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
            <Content
              style={{
                margin: 0,
                padding: 0,
                background: '#f5f5f5',
                overflow: 'auto',
              }}
            >
              <Routes>
                <Route
                  path="/"
                  element={<SimpleTest />}
                />
                <Route
                  path="/system-monitoring"
                  element={
                    <SystemMonitoring
                      data={systemMonitoringData}
                      loading={loading.systemMonitoring}
                      error={errors.systemMonitoring}
                    />
                  }
                />
                <Route
                  path="/system-monitoring/services"
                  element={
                    <SystemMonitoring
                      data={systemMonitoringData}
                      loading={loading.systemMonitoring}
                      error={errors.systemMonitoring}
                    />
                  }
                />
                <Route
                  path="/system-monitoring/tasks"
                  element={
                    <SystemMonitoring
                      data={systemMonitoringData}
                      loading={loading.systemMonitoring}
                      error={errors.systemMonitoring}
                    />
                  }
                />
                <Route
                  path="/content-management"
                  element={
                    <ContentManagement
                      data={contentManagementData}
                      loading={loading.contentManagement}
                      error={errors.contentManagement}
                    />
                  }
                />
                <Route
                  path="/content-management/kols"
                  element={<KOLManagementPage />}
                />
                <Route
                  path="/content-management/kols/:serial"
                  element={<KOLDetailPage />}
                />
                <Route
                  path="/content-management/posts"
                  element={
                    <ContentManagement
                      data={contentManagementData}
                      loading={loading.contentManagement}
                      error={errors.contentManagement}
                    />
                  }
                />
                <Route
                  path="/interaction-analysis"
                  element={
                    <InteractionAnalysis
                      data={interactionAnalysisData}
                      loading={loading.interactionAnalysis}
                      error={errors.interactionAnalysis}
                    />
                  }
                />
                <Route
                  path="/interaction-analysis/features"
                  element={
                    <InteractionAnalysis
                      data={interactionAnalysisData}
                      loading={loading.interactionAnalysis}
                      error={errors.interactionAnalysis}
                    />
                  }
                />
                <Route
                  path="/interaction-analysis/1hr"
                  element={
                    <InteractionAnalysis
                      data={interactionAnalysisData}
                      loading={loading.interactionAnalysis}
                      error={errors.interactionAnalysis}
                    />
                  }
                />
                <Route
                  path="/interaction-analysis/1day"
                  element={
                    <InteractionAnalysis
                      data={interactionAnalysisData}
                      loading={loading.interactionAnalysis}
                      error={errors.interactionAnalysis}
                    />
                  }
                />
                <Route
                  path="/interaction-analysis/7days"
                  element={
                    <InteractionAnalysis
                      data={interactionAnalysisData}
                      loading={loading.interactionAnalysis}
                      error={errors.interactionAnalysis}
                    />
                  }
                />
                
                {/* 發文管理路由 */}
                <Route
                  path="/posting-management"
                  element={<PostingManagement />}
                />
                <Route
                  path="/posting-management/dashboard"
                  element={<PostingDashboard />}
                />
                <Route
                  path="/posting-management/generator"
                  element={<PostingGenerator />}
                />
                <Route
                  path="/posting-management/review"
                  element={<PostingReview />}
                />
                <Route
                  path="/posting-management/published"
                  element={<PublishedPostsPage />}
                />
                <Route
                  path="/posting-management/test-after-hours"
                  element={<AfterHoursLimitUpTest />}
                />
                <Route
                  path="/posting-management/publish-success"
                  element={<PublishSuccessPage />}
                />
                
                {/* 新增的發文管理路由 */}
                <Route
                  path="/posting-management/batch-history"
                  element={<BatchHistoryPage />}
                />
                <Route
                  path="/posting-management/schedule"
                  element={<ScheduleManagementPage />}
                />
                <Route
                  path="/posting-management/self-learning"
                  element={<SelfLearningPage />}
                />
                <Route
                  path="/posting-management/interaction-analysis"
                  element={<InteractionAnalysisPage />}
                />
                {/* <Route
                  path="/posting-management/performance-analysis"
                  element={<PerformanceAnalysisPage />}
                /> */}
                <Route
                  path="/posting-management/manual-posting"
                  element={<ManualPostingPage />}
                />
                
                <Route
                  path="/content-management/kols/:memberId"
                  element={<KOLDetail />}
                />
                <Route
                  path="/content-management/posts/:postId"
                  element={<PostDetail />}
                />
                
                {/* 系統設置路由 */}
                <Route
                  path="/settings"
                  element={<SettingsPage />}
                />
                <Route
                  path="/settings/api"
                  element={<SettingsPage />}
                />
                <Route
                  path="/settings/data"
                  element={<SettingsPage />}
                />
                
                {/* 用戶管理路由 */}
                <Route
                  path="/users"
                  element={<UserManagement />}
                />
                <Route
                  path="/users/roles"
                  element={<UserManagement />}
                />
                
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
};

export default App;
