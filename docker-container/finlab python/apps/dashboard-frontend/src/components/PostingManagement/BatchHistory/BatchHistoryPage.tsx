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
  ReloadOutlined
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
  posts: Array<{
    post_id: string;
    title: string;
    content: string;
    kol_nickname: string;
    status: string;
    published_at?: string;
    generation_config: any;
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
        // 觸發器類型中英文映射
        const triggerTypeMap: Record<string, { text: string; color: string }> = {
          'limit_up_after_hours': { text: '盤後漲停', color: 'red' },
          'limit_down_after_hours': { text: '盤後跌停', color: 'green' },
          'intraday_limit_up': { text: '盤中漲停', color: 'volcano' },
          'intraday_limit_down': { text: '盤中跌停', color: 'cyan' },
          'volume_surge': { text: '成交量暴增', color: 'orange' },
          'news_hot': { text: '新聞熱股', color: 'magenta' },
          'custom_stocks': { text: '自選股', color: 'purple' },
          'unknown': { text: '未知觸發器', color: 'default' }
        };
        const mapped = triggerTypeMap[triggerType] || { text: triggerType, color: 'blue' };
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
                    const triggerTypeMap: Record<string, string> = {
                      'limit_up_after_hours': '盤後漲停',
                      'limit_down_after_hours': '盤後跌停',
                      'intraday_limit_up': '盤中漲停',
                      'intraday_limit_down': '盤中跌停',
                      'volume_surge': '成交量暴增',
                      'news_hot': '新聞熱股',
                      'custom_stocks': '自選股',
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
              <div style={{ marginTop: 8, maxHeight: 300, overflowY: 'auto' }}>
                {selectedBatch.posts.map((post, index) => (
                  <Card key={index} size="small" style={{ marginBottom: 8 }}>
                    <Row gutter={8}>
                      <Col span={4}>
                        <Tag color="blue">{post.kol_nickname}</Tag>
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