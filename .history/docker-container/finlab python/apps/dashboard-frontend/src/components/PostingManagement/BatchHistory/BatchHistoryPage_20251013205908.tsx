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
  Switch,
  Timeline,
  Steps
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
  ExperimentOutlined,
  ThunderboltOutlined,
  CrownOutlined,
  RocketOutlined,
  BulbOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ClockCircleOutlined,
  QuestionCircleOutlined,
  SmileOutlined,
  PlusOutlined,
  FileTextOutlined,
  FileOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import BatchScheduleModal from './BatchScheduleModal';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;
const { RangePicker } = DatePicker;
const { Step } = Steps;

interface Post {
  post_id: string;
  article_id: string;
  kol_serial: number;
  kol_nickname: string;
  title: string;
  content: string;
  article_url: string;
  create_time: string;
  commodity_tags: Array<{key: string, type: string, bullOrBear: string}>;
  community_topic?: string;
  source: 'system' | 'external';
  status: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  bookmarks: number;
  donations?: number;
  engagement_rate: number;
}

interface BatchRecord {
  session_id: string;
  created_at: string;
  status: string | null;
  trigger_type: string;
  kol_assignment: string;
  total_posts: number;
  published_posts: number;
  success_rate: number;
  stock_codes: string[];
  kol_names: string[];
  posts: Array<{
    post_id: string;
    title: string;
    content: string;
    kol_nickname: string;
    status: string;
    generation_config: any;
  }>;
}

interface OverallStats {
  total_posts: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  avg_engagement_rate: number;
}

interface HighPerformanceFeature {
  feature_id: string;
  feature_name: string;
  feature_type: string;
  description: string;
  frequency_in_top_posts: number;
  frequency_in_all_posts: number;
  improvement_potential: number;
  setting_key: string;
  is_modifiable: boolean;
  modification_method: string;
  examples: string[];
}

interface ContentCategory {
  category_id: string;
  category_name: string;
  description: string;
  top_posts: any[];
  avg_performance_score: number;
  key_characteristics: string[];
  success_rate: number;
}

const BatchHistoryPage: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // 篩選條件
  const [selectedKOL, setSelectedKOL] = useState<number | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [includeExternal, setIncludeExternal] = useState(true);
  
  // 統計數據
  const [overallStats, setOverallStats] = useState<OverallStats>({
    total_posts: 0,
    total_views: 0,
    total_likes: 0,
    total_comments: 0,
    total_shares: 0,
    avg_engagement_rate: 0
  });
  
  // 高表現特徵分析
  const [highPerformanceFeatures, setHighPerformanceFeatures] = useState<HighPerformanceFeature[]>([]);
  const [calculationResults, setCalculationResults] = useState<any>(null);
  const [contentCategories, setContentCategories] = useState<ContentCategory[]>([]);
  
  // 顯示狀態
  const [showFeatureAnalysis, setShowFeatureAnalysis] = useState(false);
  const [showCalculationResults, setShowCalculationResults] = useState(false);
  const [showHighPerformanceFeatures, setShowHighPerformanceFeatures] = useState(false);
  const [showContentCategories, setShowContentCategories] = useState(false);
  
  // 排程模態框
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<BatchRecord | null>(null);

  // 獲取貼文成效數據
  const fetchPostPerformanceData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedKOL) params.append('kol_serial', selectedKOL.toString());
      if (dateRange && dateRange[0] && dateRange[1]) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'));
      }
      params.append('include_external', includeExternal.toString());

      // 使用 /posts API 端點
      const response = await fetch(`http://localhost:8001/posts?${params}`);
      const result = await response.json();

      if (result.success) {
        // 從 /posts API 回應中獲取貼文數據
        const posts = result.posts || [];
        
        // 計算 overallStats
        const overallStats = {
          total_posts: posts.length,
          total_views: posts.reduce((sum: number, p: any) => sum + (p.views || 0), 0),
          total_likes: posts.reduce((sum: number, p: any) => sum + (p.likes || 0), 0),
          total_comments: posts.reduce((sum: number, p: any) => sum + (p.comments || 0), 0),
          total_shares: posts.reduce((sum: number, p: any) => sum + (p.shares || 0), 0),
          avg_engagement_rate: posts.length > 0 ? 
            posts.reduce((sum: number, p: any) => sum + ((p.likes || 0) + (p.comments || 0) + (p.shares || 0)) / (p.views || 1), 0) / posts.length * 100
            : 0
        };
        
        console.log(`📊 獲取到 ${posts.length} 篇貼文數據`);
        console.log(`📈 總體統計:`, overallStats);
        
        setPosts(posts);
        setOverallStats(overallStats); // 設置整體統計數據
        
        const analysisResult = analyzeHighPerformanceFeaturesFromPosts(posts);
        setHighPerformanceFeatures(analysisResult.features);
        setCalculationResults(analysisResult.calculationResults);
        
        const categories = analyzeContentCategoriesFromPosts(posts);
        setContentCategories(categories);
        
        message.success('批次歷史數據載入成功！');
      } else {
        message.error('載入批次歷史數據失敗: ' + result.message);
      }
    } catch (error) {
      console.error('載入批次歷史數據失敗:', error);
      message.error('載入批次歷史數據失敗');
    } finally {
      setLoading(false);
    }
  };

  // 分析高表現特徵
  const analyzeHighPerformanceFeaturesFromPosts = (posts: Post[]) => {
    if (posts.length === 0) return { features: [], calculationResults: null };

    // 按互動率排序，取前20%
    const sortedPosts = [...posts].sort((a, b) => b.engagement_rate - a.engagement_rate);
    const top20Percent = Math.ceil(posts.length * 0.2);
    const topPosts = sortedPosts.slice(0, top20Percent);

    // 分析特徵
    const features: HighPerformanceFeature[] = [
      {
        feature_id: 'has_emoji',
        feature_name: '表情符號',
        feature_type: 'content',
        description: '貼文中包含表情符號',
        frequency_in_top_posts: topPosts.filter(p => p.content.includes('😊') || p.content.includes('📈')).length,
        frequency_in_all_posts: posts.filter(p => p.content.includes('😊') || p.content.includes('📈')).length,
        improvement_potential: 0,
        setting_key: 'include_emoji',
        is_modifiable: true,
        modification_method: '在生成設定中啟用表情符號',
        examples: ['😊', '📈', '🚀', '💪']
      },
      {
        feature_id: 'has_hashtag',
        feature_name: '標籤',
        feature_type: 'content',
        description: '貼文中包含標籤',
        frequency_in_top_posts: topPosts.filter(p => p.content.includes('#')).length,
        frequency_in_all_posts: posts.filter(p => p.content.includes('#')).length,
        improvement_potential: 0,
        setting_key: 'include_hashtags',
        is_modifiable: true,
        modification_method: '在生成設定中啟用標籤',
        examples: ['#台股', '#投資', '#分析']
      },
      {
        feature_id: 'question_interaction',
        feature_name: '互動問答',
        feature_type: 'content',
        description: '貼文中包含問答互動',
        frequency_in_top_posts: topPosts.filter(p => p.content.includes('?') || p.content.includes('？')).length,
        frequency_in_all_posts: posts.filter(p => p.content.includes('?') || p.content.includes('？')).length,
        improvement_potential: 0,
        setting_key: 'include_questions',
        is_modifiable: true,
        modification_method: '在生成設定中啟用問答互動',
        examples: ['你覺得如何？', '有什麼看法？']
      }
    ];

    // 計算改善潛力
    features.forEach(feature => {
      const topRate = feature.frequency_in_top_posts / topPosts.length;
      const allRate = feature.frequency_in_all_posts / posts.length;
      feature.improvement_potential = topRate - allRate;
    });

    const calculationResults = {
      total_posts: posts.length,
      top_posts_count: topPosts.length,
      analysis_date: new Date().toISOString(),
      features_analyzed: features.length
    };

    return { features, calculationResults };
  };

  // 分析內容類別
  const analyzeContentCategoriesFromPosts = (posts: Post[]) => {
    if (posts.length === 0) return [];

    const categories: ContentCategory[] = [
      {
        category_id: 'technical_analysis',
        category_name: '技術分析',
        description: '以技術指標為主的分析內容',
        top_posts: posts.filter(p => p.content.includes('技術') || p.content.includes('指標')),
        avg_performance_score: 0,
        key_characteristics: ['技術指標', '圖表分析', '趨勢判斷'],
        success_rate: 0
      },
      {
        category_id: 'fundamental_analysis',
        category_name: '基本面分析',
        description: '以公司基本面為主的分析內容',
        top_posts: posts.filter(p => p.content.includes('財報') || p.content.includes('基本面')),
        avg_performance_score: 0,
        key_characteristics: ['財報分析', '公司價值', '成長性'],
        success_rate: 0
      },
      {
        category_id: 'market_sentiment',
        category_name: '市場情緒',
        description: '以市場情緒為主的分析內容',
        top_posts: posts.filter(p => p.content.includes('情緒') || p.content.includes('氣氛')),
        avg_performance_score: 0,
        key_characteristics: ['市場情緒', '投資氣氛', '心理分析'],
        success_rate: 0
      }
    ];

    // 計算各類別的平均表現
    categories.forEach(category => {
      if (category.top_posts.length > 0) {
        category.avg_performance_score = category.top_posts.reduce((sum, p) => sum + p.engagement_rate, 0) / category.top_posts.length;
        category.success_rate = (category.top_posts.filter(p => p.engagement_rate > 0.05).length / category.top_posts.length) * 100;
      }
    });

    return categories;
  };

  // 處理排程
  const handleSchedule = (batch: BatchRecord) => {
    setSelectedBatch(batch);
    setScheduleModalVisible(true);
  };

  // 確認排程
  const handleScheduleConfirm = async (scheduleConfig: any) => {
    try {
      // 這裡可以調用排程 API
      console.log('排程配置:', scheduleConfig);
      message.success('排程設定成功！');
      setScheduleModalVisible(false);
    } catch (error) {
      console.error('排程設定失敗:', error);
      message.error('排程設定失敗');
    }
  };

  // 組件載入時獲取數據
  useEffect(() => {
    fetchPostPerformanceData();
  }, []);

  // 表格列定義
  const columns: ColumnsType<Post> = [
    {
      title: '貼文ID',
      dataIndex: 'post_id',
      key: 'post_id',
      width: 120,
      render: (text: string) => (
        <Text code style={{ fontSize: '12px' }}>
          {text.slice(-8)}
        </Text>
      ),
    },
    {
      title: 'KOL',
      dataIndex: 'kol_nickname',
      key: 'kol_nickname',
      width: 100,
      render: (text: string, record: Post) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '標題',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <span>{text}</span>
        </Tooltip>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusConfig = {
          published: { color: 'green', text: '已發布' },
          draft: { color: 'orange', text: '草稿' },
          pending: { color: 'blue', text: '待審核' },
          failed: { color: 'red', text: '失敗' }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '互動數據',
      key: 'interactions',
      width: 200,
      render: (_, record: Post) => (
        <Space size="small">
          <Tooltip title="瀏覽數">
            <span><EyeOutlined /> {record.views}</span>
          </Tooltip>
          <Tooltip title="讚數">
            <span><LikeOutlined /> {record.likes}</span>
          </Tooltip>
          <Tooltip title="留言數">
            <span><MessageOutlined /> {record.comments}</span>
          </Tooltip>
          <Tooltip title="分享數">
            <span><ShareAltOutlined /> {record.shares}</span>
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '互動率',
      dataIndex: 'engagement_rate',
      key: 'engagement_rate',
      width: 100,
      render: (rate: number) => (
        <span style={{ color: rate > 0.05 ? '#52c41a' : '#faad14' }}>
          {(rate * 100).toFixed(2)}%
        </span>
      ),
    },
    {
      title: '建立時間',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 150,
      render: (time: string) => new Date(time).toLocaleString('zh-TW'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record: Post) => (
        <Space size="small">
          <Button size="small" type="link" icon={<EyeOutlined />}>
            查看
          </Button>
          <Button size="small" type="link" icon={<SettingOutlined />}>
            設定
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>
              <BarChartOutlined style={{ marginRight: 8 }} />
              批次歷史分析
            </Title>
            <Text type="secondary">分析批次發文的成效和特徵</Text>
          </div>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchPostPerformanceData}
            loading={loading}
          >
            重新整理
          </Button>
        </div>

        {/* 篩選條件 */}
        <Card size="small" style={{ marginBottom: 24 }}>
          <Row gutter={16} align="middle">
            <Col span={6}>
              <Select
                placeholder="選擇KOL"
                style={{ width: '100%' }}
                allowClear
                value={selectedKOL}
                onChange={setSelectedKOL}
              >
                <Option value={1}>KOL 1</Option>
                <Option value={2}>KOL 2</Option>
                <Option value={3}>KOL 3</Option>
              </Select>
            </Col>
            <Col span={8}>
              <RangePicker
                style={{ width: '100%' }}
                value={dateRange}
                onChange={setDateRange}
                placeholder={['開始日期', '結束日期']}
              />
            </Col>
            <Col span={4}>
              <Switch
                checkedChildren="包含外部"
                unCheckedChildren="僅系統"
                checked={includeExternal}
                onChange={setIncludeExternal}
              />
            </Col>
            <Col span={6}>
              <Space>
                <Button type="primary" onClick={fetchPostPerformanceData} loading={loading}>
                  分析數據
                </Button>
                <Button icon={<ExportOutlined />}>
                  匯出
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 統計概覽 */}
        <Card size="small" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={4}>
              <Statistic
                title="總貼文數"
                value={overallStats.total_posts}
                prefix={<FileTextOutlined />}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="總瀏覽數"
                value={overallStats.total_views}
                prefix={<EyeOutlined />}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="總讚數"
                value={overallStats.total_likes}
                prefix={<LikeOutlined />}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="總留言數"
                value={overallStats.total_comments}
                prefix={<MessageOutlined />}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="總分享數"
                value={overallStats.total_shares}
                prefix={<ShareAltOutlined />}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="平均互動率"
                value={overallStats.avg_engagement_rate}
                suffix="%"
                prefix={<BarChartOutlined />}
                precision={2}
              />
            </Col>
          </Row>
        </Card>

        {/* 高表現特徵分析 */}
        {showHighPerformanceFeatures && (
          <Card title="🎯 高表現特徵分析" style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              {highPerformanceFeatures.map((feature) => (
                <Col span={8} key={feature.feature_id}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
                        {feature.feature_name}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '12px' }}>
                        {feature.description}
                      </div>
                      <Row gutter={8}>
                        <Col span={12}>
                          <div style={{ fontSize: '12px', color: '#666' }}>前20%使用率</div>
                          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                            {((feature.frequency_in_top_posts / Math.ceil(posts.length * 0.2)) * 100).toFixed(1)}%
                          </div>
                        </Col>
                        <Col span={12}>
                          <div style={{ fontSize: '12px', color: '#666' }}>整體使用率</div>
                          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                            {((feature.frequency_in_all_posts / posts.length) * 100).toFixed(1)}%
                          </div>
                        </Col>
                      </Row>
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#faad14' }}>
                        改善潛力: {(feature.improvement_potential * 100).toFixed(1)}%
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* 內容類別分析 */}
        {showContentCategories && (
          <Card title="📊 內容類別分析" style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              {contentCategories.map((category) => (
                <Col span={8} key={category.category_id}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
                        {category.category_name}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '12px' }}>
                        {category.description}
                      </div>
                      <Row gutter={8}>
                        <Col span={12}>
                          <div style={{ fontSize: '12px', color: '#666' }}>貼文數</div>
                          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                            {category.top_posts.length}
                          </div>
                        </Col>
                        <Col span={12}>
                          <div style={{ fontSize: '12px', color: '#666' }}>成功率</div>
                          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                            {category.success_rate.toFixed(1)}%
                          </div>
                        </Col>
                      </Row>
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#faad14' }}>
                        平均表現: {(category.avg_performance_score * 100).toFixed(2)}%
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* 分析按鈕 */}
        <Card size="small" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Button
                type="primary"
                icon={<ExperimentOutlined />}
                onClick={() => {
                  setShowHighPerformanceFeatures(!showHighPerformanceFeatures);
                  setShowCalculationResults(!showCalculationResults);
                }}
                block
              >
                {showHighPerformanceFeatures ? '隱藏' : '顯示'}特徵分析
              </Button>
            </Col>
            <Col span={6}>
              <Button
                icon={<BarChartOutlined />}
                onClick={() => setShowContentCategories(!showContentCategories)}
                block
              >
                {showContentCategories ? '隱藏' : '顯示'}類別分析
              </Button>
            </Col>
            <Col span={6}>
              <Button
                icon={<RocketOutlined />}
                onClick={() => message.info('AI優化建議功能開發中')}
                block
              >
                AI優化建議
              </Button>
            </Col>
            <Col span={6}>
              <Button
                icon={<SettingOutlined />}
                onClick={() => message.info('批量設定功能開發中')}
                block
              >
                批量設定
              </Button>
            </Col>
          </Row>
        </Card>

        {/* 貼文列表 */}
        <Card title="📋 貼文列表">
          <Table
            columns={columns}
            dataSource={posts}
            rowKey="post_id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `第 ${range[0]}-${range[1]} 項，共 ${total} 項`,
            }}
            scroll={{ x: 1200 }}
          />
        </Card>
      </Card>

      {/* 排程模態框 */}
      <BatchScheduleModal
        visible={scheduleModalVisible}
        onCancel={() => setScheduleModalVisible(false)}
        onConfirm={handleScheduleConfirm}
        batchData={selectedBatch}
      />
    </div>
  );
};

export default BatchHistoryPage;