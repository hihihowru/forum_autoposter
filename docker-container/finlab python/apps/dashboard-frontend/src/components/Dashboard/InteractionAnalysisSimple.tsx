import React, { useState } from 'react';
import { Card, Row, Col, Statistic, Select, Space, Alert } from 'antd';
import { 
  LikeOutlined, 
  MessageOutlined, 
  BarChartOutlined,
  RiseOutlined
} from '@ant-design/icons';
import type { InteractionAnalysisData } from '../../types';

const { Option } = Select;

interface InteractionAnalysisProps {
  data: InteractionAnalysisData | null;
  loading: boolean;
  error: string | null;
}

const InteractionAnalysisSimple: React.FC<InteractionAnalysisProps> = ({ data, loading, error }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('互動回饋_1hr');

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div>載入互動分析數據中...</div>
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
        description="暫無互動分析數據"
        type="info"
        showIcon
        style={{ margin: '16px' }}
      />
    );
  }

  const { interaction_data, statistics } = data;
  const currentData = interaction_data[selectedPeriod] || [];
  const currentStats = statistics[selectedPeriod] || {
    total_posts: 0,
    total_interactions: 0,
    total_likes: 0,
    total_comments: 0,
    avg_engagement_rate: 0,
    kol_performance: {}
  };

  // 時間週期選項
  const periodOptions = [
    { value: '互動回饋_1hr', label: '1小時數據' },
    { value: '互動回饋_1day', label: '1日數據' },
    { value: '互動回饋_7days', label: '7日數據' },
    { value: '互動回饋即時總表', label: '最新數據' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        {/* 時間週期選擇 */}
        <Col span={24}>
          <Card size="small">
            <Space>
              <span>選擇時間週期:</span>
              <Select
                value={selectedPeriod}
                onChange={setSelectedPeriod}
                style={{ width: 200 }}
              >
                {periodOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Space>
          </Card>
        </Col>

        {/* 統計概覽 */}
        <Col span={24}>
          <Card title={`${periodOptions.find(p => p.value === selectedPeriod)?.label} - 統計概覽`} size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="總貼文數"
                  value={currentStats.total_posts}
                  prefix={<BarChartOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="總互動數"
                  value={currentStats.total_interactions}
                  prefix={<RiseOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="總讚數"
                  value={currentStats.total_likes}
                  prefix={<LikeOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="總留言數"
                  value={currentStats.total_comments}
                  prefix={<MessageOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 數據摘要 */}
        <Col span={24}>
          <Card title="數據摘要" size="small">
            <div style={{ padding: '16px' }}>
              <p><strong>當前時間週期:</strong> {periodOptions.find(p => p.value === selectedPeriod)?.label}</p>
              <p><strong>數據記錄數:</strong> {currentData.length}</p>
              <p><strong>平均互動率:</strong> {currentStats.avg_engagement_rate.toFixed(3)}</p>
              <p><strong>數據來源:</strong> {data.data_source}</p>
              <p><strong>最後更新:</strong> {data.timestamp}</p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default InteractionAnalysisSimple;
