import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Statistic,
  Select,
  Space,
  Button,
  Input,
  DatePicker,
  Row,
  Col,
  Divider,
  Tooltip,
  Badge,
  Spin,
  message,
  Modal,
  Typography,
  Progress,
  Alert,
  List,
  Avatar,
  Timeline,
  Steps,
  Tabs,
  Descriptions,
  Rate
} from 'antd';
import {
  LikeOutlined,
  MessageOutlined,
  ShareAltOutlined,
  EyeOutlined,
  UserOutlined,
  CalendarOutlined,
  ReloadOutlined,
  LinkOutlined,
  BarChartOutlined,
  FilterOutlined,
  ExportOutlined,
  ThunderboltOutlined,
  CrownOutlined,
  RocketOutlined,
  BulbOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ArrowUpOutlined,
  DownOutlined,
  MinusOutlined,
  StarOutlined,
  FireOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;
const { RangePicker } = DatePicker;
const { Step } = Steps;
const { TabPane } = Tabs;

interface PerformanceMetric {
  metric_name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change_percentage: number;
  significance: 'high' | 'medium' | 'low';
}

interface TopPostAnalysis {
  post_id: string;
  article_id: string;
  kol_nickname: string;
  title: string;
  content: string;
  create_time: string;
  total_interactions: number;
  engagement_rate: number;
  performance_score: number;
  ranking: number;
  key_features: string[];
  success_factors: string[];
}

interface FeatureCorrelation {
  feature_pair: string;
  correlation_score: number;
  significance: 'high' | 'medium' | 'low';
  description: string;
  recommendation: string;
}

interface PerformanceInsight {
  insight_id: string;
  insight_type: 'pattern' | 'anomaly' | 'opportunity' | 'risk';
  title: string;
  description: string;
  confidence: number;
  impact_score: number;
  evidence: string[];
  actionable_recommendations: string[];
  affected_kols: string[];
}

interface PerformanceReport {
  analysis_period: string;
  total_posts_analyzed: number;
  top10_percent_count: number;
  overall_performance_score: number;
  performance_metrics: PerformanceMetric[];
  top_posts_analysis: TopPostAnalysis[];
  feature_correlations: FeatureCorrelation[];
  insights: PerformanceInsight[];
  summary: string;
  timestamp: string;
}

const PerformanceAnalysisPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<PerformanceReport | null>(null);
  
  // 篩選條件
  const [selectedKOL, setSelectedKOL] = useState<number | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [includeExternal, setIncludeExternal] = useState(true);
  
  // 顯示狀態
  const [activeTab, setActiveTab] = useState('overview');
  const [showDetails, setShowDetails] = useState(false);

  // 獲取成效分析報告
  const fetchPerformanceReport = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedKOL) params.append('kol_serial', selectedKOL.toString());
      if (dateRange && dateRange[0] && dateRange[1]) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'));
      }
      params.append('include_external', includeExternal.toString());

      const response = await fetch(`http://localhost:8001/performance-analysis/report?${params}`);
      const result = await response.json();

      if (result.success) {
        setReport(result.data);
        setShowDetails(true);
      } else {
        message.error('獲取成效分析報告失敗');
      }
    } catch (error) {
      console.error('獲取成效分析報告失敗:', error);
      message.error('獲取成效分析報告失敗');
    } finally {
      setLoading(false);
    }
  };

  // 獲取趨勢圖標
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowUpOutlined style={{ color: '#52c41a' }} />;
      case 'down':
        return <DownOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <MinusOutlined style={{ color: '#1890ff' }} />;
    }
  };

  // 獲取重要性顏色
  const getSignificanceColor = (significance: string) => {
    switch (significance) {
      case 'high':
        return '#ff4d4f';
      case 'medium':
        return '#fa8c16';
      default:
        return '#52c41a';
    }
  };

  // 獲取洞察類型圖標
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'pattern':
        return <BarChartOutlined style={{ color: '#1890ff' }} />;
      case 'anomaly':
        return <WarningOutlined style={{ color: '#fa8c16' }} />;
      case 'opportunity':
        return <BulbOutlined style={{ color: '#52c41a' }} />;
      case 'risk':
        return <WarningOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  // 高成效貼文表格列定義
  const topPostsColumns: ColumnsType<TopPostAnalysis> = [
    {
      title: '排名',
      dataIndex: 'ranking',
      key: 'ranking',
      width: 80,
      render: (ranking: number) => (
        <Badge 
          count={ranking} 
          style={{ 
            backgroundColor: ranking <= 3 ? '#ff4d4f' : '#1890ff',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        />
      ),
    },
    {
      title: 'KOL',
      dataIndex: 'kol_nickname',
      key: 'kol_nickname',
      width: 120,
      render: (text: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '標題',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      render: (text: string) => (
        <Text ellipsis={{ tooltip: text }} style={{ fontSize: '13px' }}>
          {text}
        </Text>
      ),
    },
    {
      title: '成效分數',
      dataIndex: 'performance_score',
      key: 'performance_score',
      width: 100,
      sorter: (a: TopPostAnalysis, b: TopPostAnalysis) => a.performance_score - b.performance_score,
      render: (score: number) => (
        <Space>
          <Rate disabled value={Math.round(score / 20)} style={{ fontSize: '12px' }} />
          <Text strong style={{ color: score > 80 ? '#52c41a' : score > 60 ? '#fa8c16' : '#ff4d4f' }}>
            {score.toFixed(1)}
          </Text>
        </Space>
      ),
    },
    {
      title: '總互動數',
      dataIndex: 'total_interactions',
      key: 'total_interactions',
      width: 100,
      sorter: (a: TopPostAnalysis, b: TopPostAnalysis) => a.total_interactions - b.total_interactions,
      render: (interactions: number) => (
        <Space>
          <BarChartOutlined style={{ color: '#1890ff' }} />
          <Text strong>{interactions}</Text>
        </Space>
      ),
    },
    {
      title: '互動率',
      dataIndex: 'engagement_rate',
      key: 'engagement_rate',
      width: 100,
      sorter: (a: TopPostAnalysis, b: TopPostAnalysis) => a.engagement_rate - b.engagement_rate,
      render: (rate: number) => (
        <Text strong style={{ color: rate > 10 ? '#52c41a' : rate > 5 ? '#fa8c16' : '#ff4d4f' }}>
          {rate.toFixed(1)}%
        </Text>
      ),
    },
    {
      title: '關鍵特徵',
      dataIndex: 'key_features',
      key: 'key_features',
      width: 150,
      render: (features: string[]) => (
        <Space wrap>
          {features.slice(0, 2).map((feature, index) => (
            <Tag key={index} size="small" color="blue">
              {feature}
            </Tag>
          ))}
          {features.length > 2 && (
            <Tag size="small" color="default">
              +{features.length - 2}
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: '成功因素',
      dataIndex: 'success_factors',
      key: 'success_factors',
      width: 150,
      render: (factors: string[]) => (
        <Space wrap>
          {factors.slice(0, 2).map((factor, index) => (
            <Tag key={index} size="small" color="green">
              {factor}
            </Tag>
          ))}
          {factors.length > 2 && (
            <Tag size="small" color="default">
              +{factors.length - 2}
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: '發文時間',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 120,
      render: (text: string) => (
        <Space>
          <CalendarOutlined />
          <Text style={{ fontSize: '11px' }}>
            {new Date(text).toLocaleDateString()}
          </Text>
        </Space>
      ),
    },
  ];

  // 特徵相關性表格列定義
  const correlationColumns: ColumnsType<FeatureCorrelation> = [
    {
      title: '特徵組合',
      dataIndex: 'feature_pair',
      key: 'feature_pair',
      width: 150,
      render: (text: string) => (
        <Text strong style={{ fontSize: '13px' }}>{text}</Text>
      ),
    },
    {
      title: '相關性分數',
      dataIndex: 'correlation_score',
      key: 'correlation_score',
      width: 120,
      sorter: (a: FeatureCorrelation, b: FeatureCorrelation) => a.correlation_score - b.correlation_score,
      render: (score: number) => (
        <Space>
          <Progress 
            type="circle" 
            size={30} 
            percent={score} 
            format={() => score.toFixed(1)}
            strokeColor={score > 80 ? '#52c41a' : score > 60 ? '#fa8c16' : '#ff4d4f'}
          />
        </Space>
      ),
    },
    {
      title: '重要性',
      dataIndex: 'significance',
      key: 'significance',
      width: 100,
      render: (significance: string) => {
        const colors = { high: '#ff4d4f', medium: '#fa8c16', low: '#52c41a' };
        return (
          <Tag color={colors[significance as keyof typeof colors]}>
            {significance === 'high' ? '高' : significance === 'medium' ? '中' : '低'}
          </Tag>
        );
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => (
        <Text type="secondary" style={{ fontSize: '12px' }}>{text}</Text>
      ),
    },
    {
      title: '建議',
      dataIndex: 'recommendation',
      key: 'recommendation',
      render: (text: string) => (
        <Text style={{ fontSize: '12px' }}>{text}</Text>
      ),
    },
  ];

  useEffect(() => {
    fetchPerformanceReport();
  }, [selectedKOL, dateRange, includeExternal]);

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <TrophyOutlined style={{ marginRight: 8 }} />
          成效分析系統
        </Title>
        <Text type="secondary">深度分析前10%高成效貼文的特徵和模式</Text>
      </div>

      {/* 篩選條件 */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={4}>
            <Select
              placeholder="選擇KOL"
              value={selectedKOL}
              onChange={setSelectedKOL}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value={1}>龜狗一日散戶</Option>
              <Option value={2}>板橋大who</Option>
            </Select>
          </Col>
          <Col span={6}>
            <RangePicker
              placeholder={['開始日期', '結束日期']}
              value={dateRange}
              onChange={setDateRange}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={4}>
            <Select
              value={includeExternal}
              onChange={setIncludeExternal}
              style={{ width: '100%' }}
            >
              <Option value={true}>包含外部數據</Option>
              <Option value={false}>僅系統數據</Option>
            </Select>
          </Col>
          <Col span={10}>
            <Space wrap>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />}
                onClick={fetchPerformanceReport}
                loading={loading}
              >
                刷新分析
              </Button>
              <Button 
                type="default" 
                icon={<ExportOutlined />}
                onClick={() => message.info('導出功能開發中')}
              >
                導出報告
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 分析結果 */}
      {showDetails && report && (
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* 總覽 */}
          <TabPane tab="總覽" key="overview">
            <Row gutter={[16, 16]}>
              {/* 整體統計 */}
              <Col span={24}>
                <Card title="📊 整體成效統計" size="small">
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="分析期間"
                        value={report.analysis_period}
                        prefix={<CalendarOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="總貼文數"
                        value={report.total_posts_analyzed}
                        prefix={<BarChartOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="高成效貼文"
                        value={report.top10_percent_count}
                        prefix={<CrownOutlined />}
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="整體成效分數"
                        value={report.overall_performance_score}
                        suffix="/100"
                        prefix={<TrophyOutlined />}
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Col>
                  </Row>
                </Card>
              </Col>

              {/* 成效指標 */}
              <Col span={24}>
                <Card title="📈 成效指標" size="small">
                  <Row gutter={16}>
                    {report.performance_metrics.map((metric, index) => (
                      <Col span={8} key={index}>
                        <Card size="small" style={{ marginBottom: 16 }}>
                          <Space direction="vertical" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Text strong>{metric.metric_name}</Text>
                              {getTrendIcon(metric.trend)}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Text style={{ fontSize: '20px', fontWeight: 'bold', color: getSignificanceColor(metric.significance) }}>
                                {metric.value.toFixed(1)}{metric.unit}
                              </Text>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                {metric.change_percentage > 0 ? '+' : ''}{metric.change_percentage.toFixed(1)}%
                              </Text>
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </Card>
              </Col>

              {/* 總結 */}
              <Col span={24}>
                <Card title="📝 分析總結" size="small">
                  <Alert
                    message="分析結果"
                    description={report.summary}
                    type="info"
                    showIcon
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* 高成效貼文 */}
          <TabPane tab="高成效貼文" key="top-posts">
            <Card title="🏆 前10%高成效貼文分析" size="small">
              <Table
                columns={topPostsColumns}
                dataSource={report.top_posts_analysis}
                rowKey="post_id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 條，共 ${total} 條`,
                }}
                scroll={{ x: 1200 }}
                size="small"
              />
            </Card>
          </TabPane>

          {/* 特徵相關性 */}
          <TabPane tab="特徵相關性" key="correlations">
            <Card title="🔗 特徵相關性分析" size="small">
              <Table
                columns={correlationColumns}
                dataSource={report.feature_correlations}
                rowKey="feature_pair"
                pagination={false}
                size="small"
              />
            </Card>
          </TabPane>

          {/* 洞察分析 */}
          <TabPane tab="洞察分析" key="insights">
            <Card title="💡 成效洞察" size="small">
              <List
                dataSource={report.insights}
                renderItem={(insight) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Avatar 
                          style={{ 
                            backgroundColor: insight.insight_type === 'pattern' ? '#1890ff' : 
                                          insight.insight_type === 'anomaly' ? '#fa8c16' : 
                                          insight.insight_type === 'opportunity' ? '#52c41a' : '#ff4d4f'
                          }}
                          icon={getInsightIcon(insight.insight_type)}
                        />
                      }
                      title={
                        <Space>
                          <Text strong>{insight.title}</Text>
                          <Tag color={insight.impact_score > 0.7 ? 'red' : insight.impact_score > 0.5 ? 'orange' : 'green'}>
                            影響度: {Math.round(insight.impact_score * 100)}%
                          </Tag>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            信心度: {Math.round(insight.confidence * 100)}%
                          </Text>
                        </Space>
                      }
                      description={
                        <div>
                          <Paragraph style={{ marginBottom: 8 }}>{insight.description}</Paragraph>
                          <div style={{ marginBottom: 8 }}>
                            <Text strong style={{ fontSize: '12px' }}>證據: </Text>
                            <Text style={{ fontSize: '12px' }}>{insight.evidence.join(', ')}</Text>
                          </div>
                          <div style={{ marginBottom: 8 }}>
                            <Text strong style={{ fontSize: '12px' }}>建議行動: </Text>
                            <Text style={{ fontSize: '12px' }}>{insight.actionable_recommendations.join(', ')}</Text>
                          </div>
                          <div>
                            <Text strong style={{ fontSize: '12px' }}>影響KOL: </Text>
                            <Space wrap>
                              {insight.affected_kols.map((kol, index) => (
                                <Tag key={index} size="small" color="blue">
                                  {kol}
                                </Tag>
                              ))}
                            </Space>
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </TabPane>
        </Tabs>
      )}

      {/* 載入狀態 */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>分析中...</div>
        </div>
      )}

      {/* 無數據狀態 */}
      {!loading && !showDetails && (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <TrophyOutlined style={{ fontSize: '48px', color: '#d9d9d9', marginBottom: 16 }} />
          <Text type="secondary">暫無成效分析數據，請點擊上方按鈕開始分析</Text>
        </div>
      )}
    </div>
  );
};

export default PerformanceAnalysisPage;
