import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Modal,
  Typography,
  Row,
  Col,
  Statistic,
  message,
  Spin,
  Tooltip,
  Badge
} from 'antd';
import {
  EyeOutlined,
  CalendarOutlined,
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  BarChartOutlined,
  LinkOutlined,
  ReloadOutlined,
  FireOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import PostingManagementAPI from '../../../services/postingManagementAPI';
import BatchScheduleModal from './BatchScheduleModal';
import { getApiBaseUrl } from '../../../config/api';


const API_BASE_URL = getApiBaseUrl();
const { Title, Text } = Typography;

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
  has_trending_topics?: boolean;
  trending_topics_count?: number;
  posts: Array<{
    post_id: string;
    title: string;
    content: string;
    kol_nickname: string;
    status: string;
    published_at?: string;
    generation_config: any;
    has_trending_topic?: boolean;
    topic_title?: string;
  }>;
}

const BatchHistoryPage: React.FC = () => {
  const [batches, setBatches] = useState<BatchRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<BatchRecord | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false);
  const [selectedBatchForSchedule, setSelectedBatchForSchedule] = useState<BatchRecord | null>(null);
  const [stats, setStats] = useState({
    totalSessions: 0,
    scheduledSessions: 0,
    completedSessions: 0,
    pendingSessions: 0,
    failedSessions: 0
  });
  const navigate = useNavigate();

  // 獲取批次歷史
  const fetchBatchHistory = async () => {
    setLoading(true);
    try {
      const result = await PostingManagementAPI.getBatchHistory();
      if (result.success) {
        setBatches(result.data);
        
        // 計算統計數據
        const totalSessions = result.data.length;
        const completedSessions = result.data.filter(batch => batch.status === 'completed').length;
        const pendingSessions = result.data.filter(batch => batch.status === 'pending').length;
        const failedSessions = result.data.filter(batch => batch.status === 'failed').length;
        
        // 計算進入排程的數量（這裡假設有 published_posts > 0 的批次已進入排程）
        const scheduledSessions = result.data.filter(batch => batch.published_posts > 0).length;
        
        setStats({
          totalSessions,
          scheduledSessions,
          completedSessions,
          pendingSessions,
          failedSessions
        });
      } else {
        message.error('獲取批次歷史失敗');
      }
    } catch (error) {
      console.error('獲取批次歷史失敗:', error);
      message.error('獲取批次歷史失敗');
    } finally {
      setLoading(false);
    }
  };

  // 查看批次詳情
  const handleViewDetails = async (sessionId: string) => {
    try {
      const result = await PostingManagementAPI.getBatchDetails(sessionId);
      if (result.success) {
        setSelectedBatch(result.data);
        setDetailModalVisible(true);
      } else {
        message.error('獲取批次詳情失敗');
      }
    } catch (error) {
      console.error('獲取批次詳情失敗:', error);
      message.error('獲取批次詳情失敗');
    }
  };

  // 加入排程
  const handleAddToSchedule = async (sessionId: string) => {
    try {
      // 獲取批次詳情
      const batchResult = await PostingManagementAPI.getBatchDetails(sessionId);
      if (!batchResult.success) {
        message.error('獲取批次詳情失敗');
        return;
      }

      const batch = batchResult.data;
      setSelectedBatchForSchedule(batch);
      setScheduleModalVisible(true);
    } catch (error) {
      console.error('獲取批次詳情失敗:', error);
      message.error('獲取批次詳情失敗');
    }
  };

  // 確認排程設定
  const handleConfirmSchedule = async (scheduleConfig: any) => {
    try {
      setLoading(true);

      // 🔥 DEBUG: Log what we're sending to the API
      console.log('🚀 API Request to /api/schedule/create');
      console.log('🔍 trigger_config:', scheduleConfig.trigger_config);
      console.log('🔍 schedule_config:', scheduleConfig.schedule_config);

      // 創建排程
      const response = await fetch(`${API_BASE_URL}/api/schedule/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scheduleConfig)
      });

      const result = await response.json();

      if (result.success) {
        // 排程創建成功，不需要更新貼文狀態
        // 因為排程的是批次歷史，貼文會在排程執行時生成並自動標記為 scheduled
        message.success('排程創建成功！任務 ID: ' + result.task_id);
        setScheduleModalVisible(false);
        setSelectedBatchForSchedule(null);
        // 刷新批次列表
        fetchBatchHistory();
      } else {
        message.error('創建排程失敗: ' + result.message);
      }
    } catch (error) {
      console.error('創建排程失敗:', error);
      message.error('創建排程失敗');
    } finally {
      setLoading(false);
    }
  };

  // 查看審核
  const handleViewReview = (sessionId: string) => {
    navigate('/posting-management/review', { 
      state: { sessionId } 
    });
  };

  // 獲取狀態顏色
  const getStatusColor = (status: string | null) => {
    switch (status) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'pending': return 'orange';
      default: return 'default';
    }
  };

  // 獲取狀態圖標
  const getStatusIcon = (status: string | null) => {
    switch (status) {
      case 'completed': return <CheckCircleOutlined />;
      case 'failed': return <ExclamationCircleOutlined />;
      case 'pending': return <ClockCircleOutlined />;
      default: return <ClockCircleOutlined />;
    }
  };

  // 表格列定義
  const columns: ColumnsType<BatchRecord> = [
    {
      title: 'Session ID',
      dataIndex: 'session_id',
      key: 'session_id',
      width: 150,
      render: (text: string) => (
        <Text code style={{ fontSize: '12px' }}>
          {text}
        </Text>
      ),
    },
    {
      title: '創建時間',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (text: string) => (
        <Space>
          <CalendarOutlined />
          <Text style={{ fontSize: '11px' }}>
            {text}
          </Text>
        </Space>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string | null) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {status || '未知'}
        </Tag>
      ),
    },
    {
      title: '觸發器',
      dataIndex: 'trigger_type',
      key: 'trigger_type',
      width: 120,
      render: (triggerType: string) => {
        // 🔥 觸發器類型映射 - 與發文生成器步驟一保持一致（共14種觸發器）
        const triggerTypeMap: Record<string, { text: string; color: string }> = {
          // ========== 熱門話題 (1個) ==========
          'trending_topics': { text: 'CMoney熱門話題', color: 'orange' },

          // ========== 個股觸發器 - 盤後 (6個) ==========
          'limit_up_after_hours': { text: '盤後漲', color: 'red' },
          'limit_down_after_hours': { text: '盤後跌', color: 'green' },
          'volume_amount_high': { text: '成交金額高', color: 'orange' },
          'volume_amount_low': { text: '成交金額低', color: 'blue' },
          'volume_change_rate_high': { text: '成交金額變化率高', color: 'volcano' },
          'volume_change_rate_low': { text: '成交金額變化率低', color: 'cyan' },

          // ========== 盤中觸發器 (6個) ==========
          'intraday_gainers_by_amount': { text: '強勢股', color: 'volcano' },
          'intraday_volume_leaders': { text: '成交量高', color: 'orange' },
          'intraday_amount_leaders': { text: '成交額高', color: 'gold' },
          'intraday_limit_down': { text: '跌停股', color: 'green' },
          'intraday_limit_up': { text: '漲停股', color: 'red' },
          'intraday_limit_down_by_amount': { text: '弱勢股', color: 'cyan' },

          // ========== 自定義 (1個) ==========
          'custom_stocks': { text: '自選股票', color: 'purple' },

          // ========== 其他/舊觸發器（向後兼容） ==========
          'manual': { text: '手動生成', color: 'default' },
          'volume_surge': { text: '成交量暴增', color: 'orange' },
          'sector_rotation': { text: '類股輪動', color: 'purple' },
          'sector_momentum': { text: '產業動能', color: 'magenta' },
          'sector_selection': { text: '產業選擇', color: 'purple' },
          'sector_news': { text: '產業新聞', color: 'geekblue' },
          'fed_policy': { text: 'Fed政策', color: 'blue' },
          'economic_data': { text: '經濟數據', color: 'cyan' },
          'currency_movement': { text: '匯率變動', color: 'blue' },
          'commodity_prices': { text: '商品價格', color: 'gold' },
          'news_hot': { text: '新聞熱股', color: 'magenta' },
          'company_news': { text: '公司新聞', color: 'geekblue' },
          'regulatory_news': { text: '監管新聞', color: 'purple' },
          'market_news': { text: '市場新聞', color: 'blue' },
          'international_news': { text: '國際新聞', color: 'cyan' },

          // ========== 測試觸發器 (Test Triggers) ==========
          'test_personalized_mode': { text: '測試:個性化模式', color: 'lime' },
          'test_analysis_mode': { text: '測試:分析模式', color: 'lime' },
          'test_interaction_mode': { text: '測試:互動模式', color: 'lime' },
          'final_verification_test': { text: '測試:最終驗證', color: 'lime' },
          'verify_pro_deployment': { text: '測試:Pro部署驗證', color: 'lime' },
          'test_with_stock_name_fix': { text: '測試:股票名稱修復', color: 'lime' },
          'test_final': { text: '測試:最終', color: 'lime' },
          'test_api_key_fix': { text: '測試:API金鑰修復', color: 'lime' },
          'test_log_cleanup_interaction': { text: '測試:日誌清理互動', color: 'lime' },
          'test_log_cleanup_analysis': { text: '測試:日誌清理分析', color: 'lime' },
          'test_log_cleanup_personalized': { text: '測試:日誌清理個性化', color: 'lime' },

          // ========== 未知/備用 (Unknown/Fallback) ==========
          'unknown': { text: '未知觸發器', color: 'default' }
        };
        const mapped = triggerTypeMap[triggerType] || { text: triggerType, color: 'blue' };
        return <Tag color={mapped.color}>{mapped.text}</Tag>;
      },
    },
    {
      title: '生成模式',
      dataIndex: 'generation_mode',
      key: 'generation_mode',
      width: 100,
      render: (generationMode: string) => {
        const modeMap: Record<string, { text: string; color: string }> = {
          'manual': { text: '手動生成', color: 'blue' },
          'scheduled': { text: '排程生成', color: 'green' },
          'self_learning': { text: '自我學習', color: 'purple' },
          // 🔥 FIX: 支援舊的值作為 fallback (歷史數據兼容)
          'high_quality': { text: '手動生成 (舊)', color: 'blue' },
          'fast': { text: '手動生成 (快速)', color: 'cyan' },
          'balanced': { text: '手動生成 (平衡)', color: 'geekblue' },
        };
        const mapped = modeMap[generationMode] || { text: generationMode || '手動生成', color: 'default' };
        return <Tag color={mapped.color}>{mapped.text}</Tag>;
      },
    },
    {
      title: 'KOL分配',
      dataIndex: 'kol_assignment',
      key: 'kol_assignment',
      width: 100,
      render: (text: string) => (
        <Space>
          <UserOutlined />
          <Text>{text}</Text>
        </Space>
      ),
    },
    {
      title: '生成貼文',
      dataIndex: 'total_posts',
      key: 'total_posts',
      width: 100,
      render: (total: number, record: BatchRecord) => (
        <Space>
          <BarChartOutlined />
          <Text>{total} 篇</Text>
        </Space>
      ),
    },
    {
      title: '已發布',
      dataIndex: 'published_posts',
      key: 'published_posts',
      width: 100,
      render: (published: number, record: BatchRecord) => (
        <Space>
          <CheckCircleOutlined />
          <Text>{published} 篇</Text>
        </Space>
      ),
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      width: 100,
      render: (rate: number) => (
        <Text style={{ color: rate >= 80 ? '#52c41a' : rate >= 60 ? '#faad14' : '#ff4d4f' }}>
          {rate}%
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: BatchRecord) => (
        <Space>
          <Tooltip title="查看詳情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(record.session_id)}
            />
          </Tooltip>
          <Tooltip title="查看審核">
            <Button
              type="link"
              icon={<LinkOutlined />}
              onClick={() => handleViewReview(record.session_id)}
            />
          </Tooltip>
          <Tooltip title="加入排程">
            <Button
              type="link"
              icon={<PlusOutlined />}
              onClick={() => handleAddToSchedule(record.session_id)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    fetchBatchHistory();
    
    // 每30秒自動刷新一次
    const interval = setInterval(() => {
      fetchBatchHistory();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2}>
            <BarChartOutlined style={{ marginRight: 8 }} />
            批次歷史
          </Title>
          <Text type="secondary">查看所有批次生成記錄和狀態</Text>
        </div>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={fetchBatchHistory}
          loading={loading}
        >
          刷新
        </Button>
      </div>

      {/* 統計卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="總 Session 數"
              value={stats.totalSessions}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已進入排程"
              value={stats.scheduledSessions}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#52c41a' }}
              suffix={`/ ${stats.totalSessions}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completedSessions}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="待處理"
              value={stats.pendingSessions}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={batches}
            rowKey="session_id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 條，共 ${total} 條`,
            }}
            scroll={{ x: 1000 }}
            size="small"
          />
        </Spin>
      </Card>

      {/* 批次詳情Modal */}
      <Modal
        title="📋 Batch 詳情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedBatch && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Statistic
                  title="Session ID"
                  value={selectedBatch.session_id}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="創建時間"
                  value={selectedBatch.created_at}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Statistic
                  title="狀態"
                  value={selectedBatch.status || '未知'}
                  valueStyle={{ 
                    color: getStatusColor(selectedBatch.status) === 'green' ? '#52c41a' : 
                           getStatusColor(selectedBatch.status) === 'red' ? '#ff4d4f' : '#faad14'
                  }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="觸發器"
                  value={(() => {
                    // 觸發器類型中英文映射 - 完整版本（包含所有生產環境和測試觸發器）
                    const triggerTypeMap: Record<string, string> = {
                      // 盤後觸發器 (After Hours)
                      'limit_up_after_hours': '盤後漲停',
                      'limit_down_after_hours': '盤後跌停',
                      'volume_amount_high': '成交金額高',
                      'volume_amount_low': '成交金額低',
                      'volume_change_rate_high': '成交金額變化率高',
                      'volume_change_rate_low': '成交金額變化率低',

                      // 盤中觸發器 (Intraday)
                      'intraday_limit_up': '盤中漲停',
                      'intraday_limit_down': '盤中跌停',
                      'intraday_gainers_by_amount': '漲幅排序+成交額',
                      'intraday_volume_leaders': '成交量排序',
                      'intraday_amount_leaders': '成交額排序',
                      'intraday_limit_down_by_amount': '跌停篩選+成交額',
                      'volume_surge': '成交量暴增',

                      // 產業觸發器 (Sector)
                      'sector_rotation': '類股輪動',
                      'sector_momentum': '產業動能',
                      'sector_selection': '產業選擇',
                      'sector_news': '產業新聞',

                      // 總經觸發器 (Macro)
                      'fed_policy': 'Fed政策',
                      'economic_data': '經濟數據',
                      'currency_movement': '匯率變動',
                      'commodity_prices': '商品價格',

                      // 新聞觸發器 (News)
                      'news_hot': '新聞熱股',
                      'company_news': '公司新聞',
                      'regulatory_news': '監管新聞',
                      'market_news': '市場新聞',
                      'international_news': '國際新聞',

                      // 熱門話題 (Trending Topics)
                      'trending_topics': '🔥 CMoney熱門話題',

                      // 自定義 (Custom)
                      'custom_stocks': '自選股',
                      'manual': '手動生成',

                      // 測試觸發器 (Test Triggers)
                      'test_personalized_mode': '測試:個性化模式',
                      'test_analysis_mode': '測試:分析模式',
                      'test_interaction_mode': '測試:互動模式',
                      'final_verification_test': '測試:最終驗證',
                      'verify_pro_deployment': '測試:Pro部署驗證',
                      'test_with_stock_name_fix': '測試:股票名稱修復',
                      'test_final': '測試:最終',
                      'test_api_key_fix': '測試:API金鑰修復',
                      'test_log_cleanup_interaction': '測試:日誌清理互動',
                      'test_log_cleanup_analysis': '測試:日誌清理分析',
                      'test_log_cleanup_personalized': '測試:日誌清理個性化',

                      // 未知/備用 (Unknown/Fallback)
                      'unknown': '未知觸發器'
                    };
                    return triggerTypeMap[selectedBatch.trigger_type] || selectedBatch.trigger_type;
                  })()}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="KOL分配"
                  value={selectedBatch.kol_assignment}
                />
              </Col>
            </Row>

            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Statistic
                  title="生成貼文"
                  value={selectedBatch.total_posts}
                  suffix="篇"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="已發布"
                  value={selectedBatch.published_posts}
                  suffix="篇"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="成功率"
                  value={selectedBatch.success_rate}
                  suffix="%"
                  valueStyle={{ 
                    color: selectedBatch.success_rate >= 80 ? '#52c41a' : 
                           selectedBatch.success_rate >= 60 ? '#faad14' : '#ff4d4f'
                  }}
                />
              </Col>
            </Row>

            <div style={{ marginBottom: 16 }}>
              <Text strong>股票列表:</Text>
              <div style={{ marginTop: 8 }}>
                <Space wrap>
                  {selectedBatch.stock_codes.map((code, index) => (
                    <Tag key={index} color="blue">{code}</Tag>
                  ))}
                </Space>
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>KOL池:</Text>
              <div style={{ marginTop: 8 }}>
                <Space wrap>
                  {selectedBatch.kol_names.map((name, index) => (
                    <Tag key={index} color="green">{name}</Tag>
                  ))}
                </Space>
              </div>
            </div>

            <div>
              <Text strong>貼文列表:</Text>
              {selectedBatch.trigger_type === 'trending_topics' && selectedBatch.posts.some(p => p.has_trending_topic) && (
                <Tag color="orange" style={{ marginLeft: 8 }}>
                  🔥 包含 {selectedBatch.posts.filter(p => p.has_trending_topic).length} 篇熱門話題貼文
                </Tag>
              )}
              <div style={{ marginTop: 8, maxHeight: 300, overflowY: 'auto' }}>
                {selectedBatch.posts.map((post, index) => (
                  <Card key={index} size="small" style={{ marginBottom: 8 }}>
                    <Row gutter={8}>
                      <Col span={4}>
                        <Tag color="blue">{post.kol_nickname}</Tag>
                        {post.has_trending_topic && post.topic_title && (
                          <Tag color="orange" icon={<FireOutlined />} style={{ marginTop: 4 }}>
                            {post.topic_title.length > 10 ? `${post.topic_title.substring(0, 10)}...` : post.topic_title}
                          </Tag>
                        )}
                      </Col>
                      <Col span={4}>
                        <Tag color={post.status === 'published' ? 'green' : 'orange'}>
                          {post.status === 'published' ? '已完成' : '待審核'}
                        </Tag>
                      </Col>
                      <Col span={16}>
                        <Text strong ellipsis={{ tooltip: post.title }}>
                          {post.title}
                        </Text>
                        {post.published_at && (
                          <div style={{ fontSize: '10px', color: '#666' }}>
                            已發布: {new Date(post.published_at).toLocaleString()}
                          </div>
                        )}
                      </Col>
                    </Row>
                    <div style={{ marginTop: 8 }}>
                      <Text ellipsis={{ tooltip: post.content, rows: 2 }}>
                        {post.content}
                      </Text>
                    </div>
                    <div style={{ marginTop: 8, fontSize: '10px', color: '#666' }}>
                      生成配置: {JSON.stringify(post.generation_config)}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* 批次排程Modal */}
      <BatchScheduleModal
        visible={scheduleModalVisible}
        onCancel={() => {
          setScheduleModalVisible(false);
          setSelectedBatchForSchedule(null);
        }}
        onConfirm={handleConfirmSchedule}
        batchData={selectedBatchForSchedule}
      />
    </div>
  );
};

export default BatchHistoryPage;