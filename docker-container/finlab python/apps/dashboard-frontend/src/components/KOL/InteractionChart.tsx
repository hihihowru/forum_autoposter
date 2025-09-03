import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Select, Spin, Alert, message } from 'antd';
import { Line } from '@ant-design/charts';
import { 
  LikeOutlined, 
  BarChartOutlined
} from '@ant-design/icons';
import { InteractionChartProps, InteractionTrend } from '../../types/kol-types';
import api from '../../services/api';

const { Option } = Select;

const InteractionChart: React.FC<InteractionChartProps> = ({
  memberId,
  loading,
  error
}) => {
  const [interactionData, setInteractionData] = useState<any>(null);
  const [timeframe, setTimeframe] = useState<string>('7days');
  const [chartLoading, setChartLoading] = useState(false);

  // 載入互動數據
  const fetchInteractionData = async (timeframe: string) => {
    if (!memberId) return;
    
    setChartLoading(true);
    try {
      const response = await api.get(`/api/dashboard/kols/${memberId}/interactions`, {
        params: { timeframe }
      });
      
      if (response.data.success) {
        setInteractionData(response.data.data);
      }
    } catch (err: any) {
      console.error('獲取互動數據失敗:', err);
      message.error('獲取互動數據失敗');
    } finally {
      setChartLoading(false);
    }
  };

  // 初始化載入
  useEffect(() => {
    fetchInteractionData(timeframe);
  }, [memberId, timeframe]);

  // 處理時間範圍變更
  const handleTimeframeChange = (value: string) => {
    setTimeframe(value);
  };

  // 準備圖表數據
  const prepareChartData = () => {
    if (!interactionData?.interaction_trend) return [];
    
    return interactionData.interaction_trend.map((item: InteractionTrend) => ({
      date: item.date,
      interactions: item.total_interactions,
      likes: item.likes,
      comments: item.comments,
      engagement_rate: item.avg_engagement_rate * 100, // 轉換為百分比
      posts_count: item.posts_count
    }));
  };

  // 圖表配置
  const chartConfig = {
    data: prepareChartData(),
    xField: 'date',
    yField: 'interactions',
    point: {
      size: 5,
      shape: 'diamond',
    },
    label: {
      style: {
        fill: '#aaa',
      },
    },
    smooth: true,
    color: '#1890ff',
    tooltip: {
      formatter: (datum: any) => {
        return {
          name: '總互動數',
          value: `${datum.interactions} (👍 ${datum.likes} 💬 ${datum.comments})`,
        };
      },
    },
  };

  if (loading || chartLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>載入互動數據中...</div>
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
      />
    );
  }

  return (
    <div>
      {/* 時間範圍選擇 */}
      <div style={{ marginBottom: '16px', textAlign: 'right' }}>
        <Select
          value={timeframe}
          onChange={handleTimeframeChange}
          style={{ width: 120 }}
        >
          <Option value="1hr">1小時</Option>
          <Option value="1day">1天</Option>
          <Option value="7days">7天</Option>
        </Select>
      </div>

      {/* 互動趨勢圖 */}
      <Card size="small" style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '16px' }}>
          <BarChartOutlined style={{ marginRight: '8px' }} />
          <span style={{ fontWeight: 'bold' }}>互動趨勢圖 (過去 30 天)</span>
        </div>
        {prepareChartData().length > 0 ? (
          <Line {...chartConfig} height={300} />
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px', 
            color: '#999',
            backgroundColor: '#f5f5f5',
            borderRadius: '4px'
          }}>
            暫無互動數據
          </div>
        )}
      </Card>

      {/* 互動統計卡片 */}
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="1小時互動數據"
              value={interactionData?.interaction_summary?.avg_likes_per_post || 0}
              suffix="平均按讚"
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              平均留言: {interactionData?.interaction_summary?.avg_comments_per_post || 0}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              平均互動率: {((interactionData?.interaction_summary?.avg_interaction_rate || 0) * 100).toFixed(1)}%
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="1天互動數據"
              value={interactionData?.interaction_summary?.avg_likes_per_post || 0}
              suffix="平均按讚"
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              平均留言: {interactionData?.interaction_summary?.avg_comments_per_post || 0}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              平均互動率: {((interactionData?.interaction_summary?.avg_interaction_rate || 0) * 100).toFixed(1)}%
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="7天互動數據"
              value={interactionData?.interaction_summary?.avg_likes_per_post || 0}
              suffix="平均按讚"
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              平均留言: {interactionData?.interaction_summary?.avg_comments_per_post || 0}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              平均互動率: {((interactionData?.interaction_summary?.avg_interaction_rate || 0) * 100).toFixed(1)}%
            </div>
          </Card>
        </Col>
      </Row>

      {/* 話題表現分析 */}
      {interactionData?.performance_by_topic && interactionData.performance_by_topic.length > 0 && (
        <Card size="small" title="話題表現分析" style={{ marginTop: '16px' }}>
          <Row gutter={[16, 16]}>
            {interactionData.performance_by_topic.map((topic: any, index: number) => (
              <Col span={12} key={index}>
                <Card size="small" style={{ backgroundColor: '#f9f9f9' }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                    {topic.topic_title}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    發文數: {topic.posts_count}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    平均互動率: {(topic.avg_interaction_rate * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    總互動數: {topic.total_interactions}
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}
    </div>
  );
};

export default InteractionChart;
