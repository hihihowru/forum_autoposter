import React from 'react';
import { Card, Row, Col, Statistic, Progress, Tag, Space, Button } from 'antd';
import { 
  DashboardOutlined,
  UserOutlined, 
  FileTextOutlined, 
  BarChartOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { SystemMonitoringData, InteractionAnalysisData } from '../../types';

interface DashboardOverviewProps {
  systemData: SystemMonitoringData | null;
  interactionData: InteractionAnalysisData | null;
  onRefresh: () => void;
  loading: boolean;
}

const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  systemData,
  interactionData,
  onRefresh,
  loading
}) => {
  const navigate = useNavigate();

  // 計算總體統計
  const totalKOLs = systemData?.system_overview.total_kols || 0;
  const activeKOLs = systemData?.system_overview.active_kols || 0;
  const totalPosts = systemData?.system_overview.total_posts || 0;
  const publishedPosts = systemData?.system_overview.published_posts || 0;
  const successRate = systemData?.system_overview.success_rate || 0;

  // 計算互動統計
  const totalInteractions = interactionData ? 
    Object.values(interactionData.statistics).reduce((sum, stat) => sum + stat.total_interactions, 0) : 0;
  const totalLikes = interactionData ?
    Object.values(interactionData.statistics).reduce((sum, stat) => sum + stat.total_likes, 0) : 0;
  const totalComments = interactionData ?
    Object.values(interactionData.statistics).reduce((sum, stat) => sum + stat.total_comments, 0) : 0;

  // 微服務健康狀態
  const healthyServices = systemData ? 
    Object.values(systemData.microservices).filter(service => service.status === 'healthy').length : 0;
  const totalServices = systemData ? Object.keys(systemData.microservices).length : 0;

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        {/* 頁面標題 */}
        <Col span={24}>
          <Card>
            <Row justify="space-between" align="middle">
              <Col>
                <Space>
                  <DashboardOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
                  <div>
                    <h2 style={{ margin: 0 }}>儀表板總覽</h2>
                    <p style={{ margin: 0, color: '#666' }}>
                      虛擬 KOL 系統運行狀態和關鍵指標
                    </p>
                  </div>
                </Space>
              </Col>
              <Col>
                <Button 
                  type="primary" 
                  icon={<ReloadOutlined />}
                  onClick={onRefresh}
                  loading={loading}
                >
                  刷新數據
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 核心指標 */}
        <Col span={24}>
          <Card title="核心指標" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic
                    title="總 KOL 數"
                    value={totalKOLs}
                    prefix={<UserOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                  <div style={{ marginTop: '8px' }}>
                    <Tag color="green">活躍: {activeKOLs}</Tag>
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic
                    title="總貼文數"
                    value={totalPosts}
                    prefix={<FileTextOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                  <div style={{ marginTop: '8px' }}>
                    <Tag color="blue">已發布: {publishedPosts}</Tag>
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic
                    title="總互動數"
                    value={totalInteractions}
                    prefix={<BarChartOutlined />}
                    valueStyle={{ color: '#fa8c16' }}
                  />
                  <div style={{ marginTop: '8px' }}>
                    <Tag color="orange">讚: {totalLikes}</Tag>
                    <Tag color="green">留言: {totalComments}</Tag>
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic
                    title="發布成功率"
                    value={successRate}
                    suffix="%"
                    prefix={<CheckCircleOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                  <div style={{ marginTop: '8px' }}>
                    <Progress 
                      percent={successRate} 
                      size="small" 
                      strokeColor="#722ed1"
                    />
                  </div>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 系統狀態 */}
        <Col span={12}>
          <Card title="系統狀態" size="small">
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#52c41a' }}>
                    {healthyServices}/{totalServices}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    微服務健康狀態
                  </div>
                </div>
              </Col>
              <Col span={24}>
                <Progress 
                  percent={Math.round((healthyServices / totalServices) * 100)} 
                  strokeColor="#52c41a"
                  showInfo={false}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 數據源狀態 */}
        <Col span={12}>
          <Card title="數據源狀態" size="small">
            <Row gutter={[8, 8]}>
              {systemData?.data_sources && Object.entries(systemData.data_sources).map(([source, status]) => (
                <Col span={8} key={source}>
                  <div style={{ textAlign: 'center', padding: '8px' }}>
                    <div style={{ marginBottom: '4px' }}>
                      <Tag color={status === 'connected' ? 'green' : 'red'}>
                        {status === 'connected' ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
                        {status === 'connected' ? '已連接' : '未連接'}
                      </Tag>
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {source.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* 快速導航 */}
        <Col span={24}>
          <Card title="快速導航" size="small">
            <Row gutter={16}>
              <Col span={8}>
                <Card 
                  size="small" 
                  hoverable
                  onClick={() => navigate('/system-monitoring')}
                  style={{ textAlign: 'center', cursor: 'pointer' }}
                >
                  <div style={{ fontSize: '24px', color: '#1890ff', marginBottom: '8px' }}>
                    <CheckCircleOutlined />
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>系統監控</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    監控微服務狀態和任務執行
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card 
                  size="small" 
                  hoverable
                  onClick={() => navigate('/content-management')}
                  style={{ textAlign: 'center', cursor: 'pointer' }}
                >
                  <div style={{ fontSize: '24px', color: '#52c41a', marginBottom: '8px' }}>
                    <FileTextOutlined />
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>內容管理</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    管理 KOL 和貼文內容
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card 
                  size="small" 
                  hoverable
                  onClick={() => navigate('/interaction-analysis')}
                  style={{ textAlign: 'center', cursor: 'pointer' }}
                >
                  <div style={{ fontSize: '24px', color: '#fa8c16', marginBottom: '8px' }}>
                    <RiseOutlined />
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>互動分析</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    分析互動數據和 KOL 表現
                  </div>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 最近活動 */}
        <Col span={24}>
          <Card title="最近活動" size="small">
            <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
              <ClockCircleOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
              <div>暫無最近活動記錄</div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardOverview;
