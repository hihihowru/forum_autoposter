import React, { useState } from 'react';
import { Card, Row, Col, Table, Tag, Statistic, Select, Space, Alert, Button, message } from 'antd';
import { 
  LikeOutlined, 
  MessageOutlined, 
  BarChartOutlined,
  RiseOutlined,
  UserOutlined,
  FireOutlined,
  DownloadOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { Column, Pie } from '@ant-design/charts';
import type { InteractionAnalysisData } from '../../types';
import { getApiBaseUrl } from '../../config/api';


const API_BASE_URL = getApiBaseUrl();
const { Option } = Select;

interface InteractionAnalysisProps {
  data: InteractionAnalysisData | null;
  loading: boolean;
  error: string | null;
}

const InteractionAnalysis: React.FC<InteractionAnalysisProps> = ({ data, loading, error }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('互動回饋_1hr');
  const [fetchingData, setFetchingData] = useState(false);

  // 刷新所有互動數據
  const refreshAllInteractions = async () => {
    setFetchingData(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/posts/refresh-all`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        message.success(`刷新完成：${result.message}`);
        console.log('刷新結果:', result);
        
        // 顯示詳細統計
        if (result.deduplicate) {
          message.info(`去重完成：移除 ${result.deduplicate.removed_count} 個重複記錄`);
        }
        if (result.fetch) {
          message.info(`開始抓取 ${result.fetch.total_posts} 篇貼文的互動數據`);
        }
      } else {
        message.error('刷新數據失敗');
      }
    } catch (error) {
      console.error('刷新數據錯誤:', error);
      message.error('刷新數據時發生錯誤');
    } finally {
      setFetchingData(false);
    }
  };

  // 抓取所有貼文數據
  const fetchAllPostsData = async () => {
    setFetchingData(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/posts?skip=0&limit=10000`);
      if (response.ok) {
        const result = await response.json();
        message.success(`成功抓取 ${result.posts?.length || 0} 筆貼文數據`);
        console.log('抓取的貼文數據:', result);
      } else {
        message.error('抓取數據失敗');
      }
    } catch (error) {
      console.error('抓取數據錯誤:', error);
      message.error('抓取數據時發生錯誤');
    } finally {
      setFetchingData(false);
    }
  };

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

  // 互動數據表格列定義
  const interactionColumns = [
    {
      title: '文章 ID',
      dataIndex: 'article_id',
      key: 'article_id',
      width: 120,
    },
    {
      title: 'KOL',
      dataIndex: 'nickname',
      key: 'nickname',
      width: 100,
    },
    {
      title: '標題',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '熱門話題',
      dataIndex: 'is_trending_topic',
      key: 'is_trending_topic',
      width: 100,
      render: (isTrending: string) => (
        <Tag color={isTrending === 'TRUE' ? 'red' : 'default'} icon={<FireOutlined />}>
          {isTrending === 'TRUE' ? '熱門' : '一般'}
        </Tag>
      ),
    },
    {
      title: '讚數',
      dataIndex: 'likes_count',
      key: 'likes_count',
      width: 80,
      render: (count: number) => (
        <span style={{ color: '#1890ff' }}>
          <LikeOutlined /> {count}
        </span>
      ),
    },
    {
      title: '留言數',
      dataIndex: 'comments_count',
      key: 'comments_count',
      width: 80,
      render: (count: number) => (
        <span style={{ color: '#52c41a' }}>
          <MessageOutlined /> {count}
        </span>
      ),
    },
    {
      title: '總互動數',
      dataIndex: 'total_interactions',
      key: 'total_interactions',
      width: 100,
      render: (count: number) => (
        <span style={{ color: '#fa8c16', fontWeight: 'bold' }}>
          <BarChartOutlined /> {count}
        </span>
      ),
    },
    {
      title: '互動率',
      dataIndex: 'engagement_rate',
      key: 'engagement_rate',
      width: 100,
      render: (rate: number) => (
        <span style={{ color: '#722ed1' }}>
          {(rate * 100).toFixed(2)}%
        </span>
      ),
    },
    {
      title: '成長率',
      dataIndex: 'growth_rate',
      key: 'growth_rate',
      width: 100,
      render: (rate: number) => (
        <span style={{ color: rate > 0 ? '#52c41a' : '#f5222d' }}>
          <RiseOutlined /> {(rate * 100).toFixed(1)}%
        </span>
      ),
    },
  ];

  // 準備圖表數據
  const kolPerformanceData = Object.entries(currentStats.kol_performance).map(([kol, stats]) => ({
    kol,
    interactions: stats.total_interactions,
    likes: stats.likes,
    comments: stats.comments,
    posts: stats.posts,
  }));

  // KOL 表現柱狀圖配置
  const kolPerformanceConfig = {
    data: kolPerformanceData,
    xField: 'kol',
    yField: 'interactions',
    color: '#1890ff',
    meta: {
      kol: { alias: 'KOL' },
      interactions: { alias: '總互動數' },
    },
  };

  // 互動類型餅圖配置
  const interactionTypeConfig = {
    data: [
      { type: '讚數', value: currentStats.total_likes },
      { type: '留言數', value: currentStats.total_comments },
    ],
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
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
        {/* 時間週期選擇和數據抓取 */}
        <Col span={24}>
          <Card size="small">
            <Row justify="space-between" align="middle">
              <Col>
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
              </Col>
              <Col>
                <Space>
                  <Button
                    type="primary"
                    icon={<ReloadOutlined />}
                    loading={fetchingData}
                    onClick={refreshAllInteractions}
                  >
                    刷新所有互動數據
                  </Button>
                  <Button
                    icon={<DownloadOutlined />}
                    loading={fetchingData}
                    onClick={fetchAllPostsData}
                  >
                    抓取所有貼文數據
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => window.location.reload()}
                  >
                    重新整理
                  </Button>
                </Space>
              </Col>
            </Row>
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

        {/* 圖表分析 */}
        <Col span={12}>
          <Card title="KOL 表現排名" size="small">
            <Column {...kolPerformanceConfig} height={300} />
          </Card>
        </Col>

        <Col span={12}>
          <Card title="互動類型分布" size="small">
            <Pie {...interactionTypeConfig} height={300} />
          </Card>
        </Col>

        {/* 詳細數據表格 */}
        <Col span={24}>
          <Card title="詳細互動數據" size="small">
            <Table
              columns={interactionColumns}
              dataSource={currentData}
              rowKey="article_id"
              size="small"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) =>
                  `第 ${range[0]}-${range[1]} 項，共 ${total} 項`,
              }}
            />
          </Card>
        </Col>

        {/* KOL 表現統計 */}
        <Col span={24}>
          <Card title="KOL 表現統計" size="small">
            <Row gutter={[16, 16]}>
              {Object.entries(currentStats.kol_performance).map(([kol, stats]) => (
                <Col span={8} key={kol}>
                  <Card size="small" style={{ textAlign: 'center' }}>
                    <div style={{ marginBottom: '8px' }}>
                      <UserOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
                      {kol}
                    </div>
                    <Row gutter={8}>
                      <Col span={12}>
                        <div style={{ fontSize: '12px', color: '#666' }}>總互動</div>
                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                          {stats.total_interactions}
                        </div>
                      </Col>
                      <Col span={12}>
                        <div style={{ fontSize: '12px', color: '#666' }}>貼文數</div>
                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                          {stats.posts}
                        </div>
                      </Col>
                    </Row>
                    <Row gutter={8} style={{ marginTop: '8px' }}>
                      <Col span={12}>
                        <div style={{ fontSize: '12px', color: '#666' }}>讚數</div>
                        <div style={{ fontSize: '14px', color: '#1890ff' }}>
                          {stats.likes}
                        </div>
                      </Col>
                      <Col span={12}>
                        <div style={{ fontSize: '12px', color: '#666' }}>留言數</div>
                        <div style={{ fontSize: '14px', color: '#52c41a' }}>
                          {stats.comments}
                        </div>
                      </Col>
                    </Row>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default InteractionAnalysis;
