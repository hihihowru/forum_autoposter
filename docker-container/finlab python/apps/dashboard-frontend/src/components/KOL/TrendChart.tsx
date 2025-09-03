import React, { useState } from 'react';
import { Card, Row, Col, Select, Space, Typography } from 'antd';
import { Line, Column } from '@ant-design/charts';
import { BarChartOutlined, LineChartOutlined, BarChartOutlined as ColumnChartOutlined } from '@ant-design/icons';
import { MonthlyStats, WeeklyStats, DailyStats } from '../../types/kol-types';

const { Option } = Select;
const { Title, Text } = Typography;

interface TrendChartProps {
  monthlyStats: MonthlyStats[];
  weeklyStats: WeeklyStats[];
  dailyStats: DailyStats[];
  loading?: boolean;
}

const TrendChart: React.FC<TrendChartProps> = ({
  monthlyStats,
  weeklyStats,
  dailyStats,
  loading = false
}) => {
  const [timeframe, setTimeframe] = useState<'monthly' | 'weekly' | 'daily'>('monthly');
  const [chartType, setChartType] = useState<'line' | 'column'>('line');

  // 根據時間框架選擇數據
  const getChartData = () => {
    switch (timeframe) {
      case 'monthly':
        return monthlyStats.map(item => ({
          period: item.month,
          posts: item.posts_count,
          interactions: item.total_interactions,
          avgLikes: item.avg_likes_per_post,
          avgComments: item.avg_comments_per_post,
          engagement: item.engagement_rate
        }));
      case 'weekly':
        return weeklyStats.map(item => ({
          period: item.week,
          posts: item.posts_count,
          interactions: item.total_interactions,
          avgLikes: item.avg_likes_per_post,
          avgComments: item.avg_comments_per_post,
          engagement: item.engagement_rate
        }));
      case 'daily':
        return dailyStats.map(item => ({
          period: item.date,
          posts: item.posts_count,
          interactions: item.total_interactions,
          avgLikes: item.avg_likes_per_post,
          avgComments: item.avg_comments_per_post,
          engagement: item.engagement_rate
        }));
      default:
        return [];
    }
  };

  const chartData = getChartData();

  // 發文數量圖表配置
  const postsConfig = {
    data: chartData.map(item => ({ period: item.period, value: item.posts, type: '發文數量' })),
    xField: 'period',
    yField: 'value',
    seriesField: 'type',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    color: '#1890ff',
    point: {
      size: 5,
      shape: 'diamond',
    },
    label: {
      style: {
        fill: '#aaa',
      },
    },
  };

  // 互動數據圖表配置
  const interactionsConfig = {
    data: chartData.map(item => [
      { period: item.period, value: item.avgLikes, type: '平均按讚數' },
      { period: item.period, value: item.avgComments, type: '平均留言數' },
      { period: item.period, value: item.interactions, type: '總互動數' }
    ]).flat(),
    xField: 'period',
    yField: 'value',
    seriesField: 'type',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    color: ['#fa8c16', '#722ed1', '#52c41a'],
    point: {
      size: 4,
      shape: 'circle',
    },
    legend: {
      position: 'top',
    },
  };

  // 互動率圖表配置
  const engagementConfig = {
    data: chartData.map(item => ({ period: item.period, value: item.engagement })),
    xField: 'period',
    yField: 'value',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    color: '#eb2f96',
    point: {
      size: 5,
      shape: 'square',
    },
    area: {
      style: {
        fill: 'l(270) 0:#ffffff 0.5:#7ec2f3 1:#1890ff',
      },
    },
  };

  if (loading) {
    return (
      <Card title="📈 趨勢圖表" size="small">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Text>載入趨勢數據中...</Text>
        </div>
      </Card>
    );
  }

  if (chartData.length === 0) {
    return (
      <Card title="📈 趨勢圖表" size="small">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Text type="secondary">暫無趨勢數據</Text>
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title={
        <Space>
          <BarChartOutlined />
          <span>📈 趨勢圖表</span>
        </Space>
      } 
      size="small"
      extra={
        <Space>
          <Select
            value={timeframe}
            onChange={setTimeframe}
            style={{ width: 100 }}
            size="small"
          >
            <Option value="monthly">月度</Option>
            <Option value="weekly">週度</Option>
            <Option value="daily">日度</Option>
          </Select>
          <Select
            value={chartType}
            onChange={setChartType}
            style={{ width: 100 }}
            size="small"
          >
            <Option value="line">
              <LineChartOutlined /> 折線圖
            </Option>
            <Option value="column">
              <ColumnChartOutlined /> 柱狀圖
            </Option>
          </Select>
        </Space>
      }
    >
      <Row gutter={[16, 16]}>
        {/* 發文數量趨勢 */}
        <Col span={12}>
          <Card title="📝 發文數量趨勢" size="small">
            {chartType === 'line' ? (
              <Line {...postsConfig} height={200} />
            ) : (
              <Column {...postsConfig} height={200} />
            )}
          </Card>
        </Col>

        {/* 互動數據趨勢 */}
        <Col span={12}>
          <Card title="💬 互動數據趨勢" size="small">
            <Line {...interactionsConfig} height={200} />
          </Card>
        </Col>

        {/* 互動率趨勢 */}
        <Col span={24}>
          <Card title="📊 互動率趨勢" size="small">
            <Line {...engagementConfig} height={200} />
          </Card>
        </Col>
      </Row>

      {/* 數據摘要 */}
      <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
        <Col span={6}>
          <div style={{ textAlign: 'center' }}>
            <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
              {chartData.reduce((sum, item) => sum + item.posts, 0)}
            </Title>
            <Text type="secondary">總發文數</Text>
          </div>
        </Col>
        <Col span={6}>
          <div style={{ textAlign: 'center' }}>
            <Title level={4} style={{ margin: 0, color: '#52c41a' }}>
              {chartData.reduce((sum, item) => sum + item.interactions, 0)}
            </Title>
            <Text type="secondary">總互動數</Text>
          </div>
        </Col>
        <Col span={6}>
          <div style={{ textAlign: 'center' }}>
            <Title level={4} style={{ margin: 0, color: '#fa8c16' }}>
              {(chartData.reduce((sum, item) => sum + item.avgLikes, 0) / chartData.length).toFixed(1)}
            </Title>
            <Text type="secondary">平均按讚數</Text>
          </div>
        </Col>
        <Col span={6}>
          <div style={{ textAlign: 'center' }}>
            <Title level={4} style={{ margin: 0, color: '#722ed1' }}>
              {(chartData.reduce((sum, item) => sum + item.avgComments, 0) / chartData.length).toFixed(1)}
            </Title>
            <Text type="secondary">平均留言數</Text>
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default TrendChart;
