import React from 'react';
import { Card, Row, Col, Statistic, Progress, Tag, Alert, Spin } from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  DatabaseOutlined,
  ApiOutlined,
  CloudOutlined
} from '@ant-design/icons';
import type { SystemMonitoringData } from '../../types';

interface SystemMonitoringProps {
  data: SystemMonitoringData | null;
  loading: boolean;
  error: string | null;
}

const SystemMonitoring: React.FC<SystemMonitoringProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>載入系統監控數據中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="載入失敗"
        description={error}
        type="error"
        showIcon
        style={{ margin: '16px' }}
      />
    );
  }

  if (!data) {
    return (
      <Alert
        message="無數據"
        description="暫無系統監控數據"
        type="info"
        showIcon
        style={{ margin: '16px' }}
      />
    );
  }

  const { system_overview, microservices, task_execution, data_sources } = data;

  // 微服務狀態顏色
  const getServiceStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  // 數據源狀態顏色
  const getDataSourceStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'success';
      case 'not_connected': return 'error';
      default: return 'default';
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        {/* 系統概覽 */}
        <Col span={24}>
          <Card title="系統概覽" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="總 KOL 數"
                  value={system_overview.total_kols}
                  prefix={<DatabaseOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="活躍 KOL 數"
                  value={system_overview.active_kols}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="總貼文數"
                  value={system_overview.total_posts}
                  prefix={<ApiOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="發布成功率"
                  value={system_overview.success_rate}
                  suffix="%"
                  prefix={<CloudOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 微服務狀態 */}
        <Col span={24}>
          <Card title="微服務狀態" size="small">
            <Row gutter={[16, 16]}>
              {Object.entries(microservices).map(([serviceName, serviceData]) => (
                <Col span={8} key={serviceName}>
                  <Card size="small" style={{ height: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ marginBottom: '8px' }}>
                        <Tag color={getServiceStatusColor(serviceData.status)}>
                          {serviceData.status === 'healthy' ? (
                            <CheckCircleOutlined />
                          ) : (
                            <CloseCircleOutlined />
                          )}
                          {serviceData.status}
                        </Tag>
                      </div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>
                        {serviceName.replace('_', ' ').toUpperCase()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        運行時間: {serviceData.uptime}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        響應時間: {serviceData.response_time}
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* 任務執行統計 */}
        <Col span={24}>
          <Card title="任務執行統計" size="small">
            <Row gutter={16}>
              <Col span={8}>
                <Card size="small">
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>每小時任務</div>
                    <Progress
                      type="circle"
                      percent={Math.round((task_execution.hourly_tasks.success / task_execution.hourly_tasks.total) * 100)}
                      size={80}
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
                      {task_execution.hourly_tasks.success}/{task_execution.hourly_tasks.total}
                    </div>
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>每日任務</div>
                    <Progress
                      type="circle"
                      percent={Math.round((task_execution.daily_tasks.success / task_execution.daily_tasks.total) * 100)}
                      size={80}
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
                      {task_execution.daily_tasks.success}/{task_execution.daily_tasks.total}
                    </div>
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>每週任務</div>
                    <Progress
                      type="circle"
                      percent={Math.round((task_execution.weekly_tasks.success / task_execution.weekly_tasks.total) * 100)}
                      size={80}
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
                      {task_execution.weekly_tasks.success}/{task_execution.weekly_tasks.total}
                    </div>
                  </div>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 數據源狀態 */}
        <Col span={24}>
          <Card title="數據源狀態" size="small">
            <Row gutter={16}>
              {Object.entries(data_sources).map(([sourceName, status]) => (
                <Col span={8} key={sourceName}>
                  <div style={{ textAlign: 'center', padding: '16px' }}>
                    <div style={{ marginBottom: '8px' }}>
                      <Tag color={getDataSourceStatusColor(status)}>
                        {status === 'connected' ? (
                          <CheckCircleOutlined />
                        ) : (
                          <CloseCircleOutlined />
                        )}
                        {status}
                      </Tag>
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                      {sourceName.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SystemMonitoring;
