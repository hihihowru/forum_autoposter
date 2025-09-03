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

import { useDashboardStore } from './stores/dashboardStore';

// 設置 dayjs 語言
dayjs.locale('zh-tw');

const { Content } = Layout;

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  
  const {
    systemMonitoringData,
    contentManagementData,
    interactionAnalysisData,
    loading,
    errors,
    lastUpdated,
    refreshAllData,
  } = useDashboardStore();

  // 組件掛載時載入數據
  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

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
                  element={
                    <DashboardOverview
                      systemData={systemMonitoringData}
                      interactionData={interactionAnalysisData}
                      onRefresh={handleRefresh}
                      loading={isLoading}
                    />
                  }
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
                  path="/content-management/kols/:memberId"
                  element={<KOLDetail />}
                />
                <Route
                  path="/content-management/posts/:postId"
                  element={<PostDetail />}
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
