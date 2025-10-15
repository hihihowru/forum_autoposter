import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Space, Typography, List, Tag, DatePicker, Select, Table, message, Spin } from 'antd';
import { 
  EditOutlined,
  CheckCircleOutlined, 
  ClockCircleOutlined,
  ScheduleOutlined,
  TagsOutlined,
  RocketOutlined,
  FileTextOutlined,
  BarChartOutlined,
  DownloadOutlined
} from '@ant-design/icons';
// import PostingManagementAPI, { PostingAPIUtils } from '../../services/postingManagementAPI';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

const PostingDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [posts, setPosts] = useState([]);
  const [dateRange, setDateRange] = useState<any>(null);
  const [triggerType, setTriggerType] = useState<string>('all');

  // 模擬數據
  const stats = {
    total_sessions: 15,
    total_posts: 45,
    published_posts: 38,
    pending_review: 7,
    success_rate: 84.4
  };

  const mockSessions = [
    {
      id: 'session_001',
      name: '盤後漲停分析_2024-01-15',
      trigger_type: 'after_hours_limit_up',
      status: 'completed',
      created_at: '2024-01-15 14:30:00',
      posts_count: 5,
      published_count: 4
    },
    {
      id: 'session_002', 
      name: '自定義股票分析_2024-01-14',
      trigger_type: 'custom_stocks',
      status: 'in_progress',
      created_at: '2024-01-14 09:15:00',
      posts_count: 3,
      published_count: 1
    }
  ];

  const mockPosts = [
    {
      id: 1,
      title: '台積電突破800元大關，技術面強勢',
      kol_nickname: '川川哥',
      status: 'published',
      created_at: '2024-01-15 15:30:00',
      interactions: 156
    },
    {
      id: 2,
      title: '聯發科財報亮眼，後市看好',
      kol_nickname: '韭割哥', 
      status: 'pending',
      created_at: '2024-01-15 15:45:00',
      interactions: 0
    }
  ];

  const columns = [
    {
      title: '發文標題',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: 'KOL',
      dataIndex: 'kol_nickname',
      key: 'kol_nickname',
      width: 100,
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap = {
          'published': { color: 'green', text: '已發布' },
          'pending': { color: 'orange', text: '待審核' },
          'draft': { color: 'blue', text: '草稿' },
          'rejected': { color: 'red', text: '已拒絕' }
        };
        const config = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '互動數',
      dataIndex: 'interactions',
      key: 'interactions',
      width: 100,
      render: (count: number) => count || 0
    },
    {
      title: '創建時間',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
    }
  ];

  const sessionColumns = [
    {
      title: '會話名稱',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '觸發類型',
      dataIndex: 'trigger_type',
      key: 'trigger_type',
      width: 120,
      render: (type: string) => {
        const typeMap = {
          'after_hours_limit_up': '盤後漲停',
          'custom_stocks': '自定義股票',
          'stock_code_list': '股票代號列表'
        };
        return typeMap[type as keyof typeof typeMap] || type;
      }
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap = {
          'completed': { color: 'green', text: '已完成' },
          'in_progress': { color: 'blue', text: '進行中' },
          'failed': { color: 'red', text: '失敗' }
        };
        const config = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '發文數',
      dataIndex: 'posts_count',
      key: 'posts_count',
      width: 80,
    },
    {
      title: '已發布',
      dataIndex: 'published_count',
      key: 'published_count',
      width: 80,
    },
    {
      title: '創建時間',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
    }
  ];

  useEffect(() => {
    loadData();
  }, [dateRange, triggerType]);

  const loadData = async () => {
    setLoading(true);
    try {
      // 模擬API調用
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSessions(mockSessions);
      setPosts(mockPosts);
    } catch (error) {
      message.error('載入數據失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    message.success('數據導出功能開發中...');
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>發文管理儀表板</Title>
        <Text type="secondary">發文系統統計與管理</Text>
      </div>

      {/* 統計卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="總會話數"
              value={stats.total_sessions}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="總發文數"
              value={stats.total_posts}
              prefix={<EditOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已發布"
              value={stats.published_posts}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="成功率"
              value={stats.success_rate}
              suffix="%"
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 篩選器 */}
      <Card style={{ marginBottom: '24px' }}>
        <Space wrap>
          <RangePicker
            placeholder={['開始日期', '結束日期']}
            onChange={setDateRange}
          />
          <Select
            value={triggerType}
            onChange={setTriggerType}
            style={{ width: 150 }}
          >
            <Option value="all">全部觸發器</Option>
            <Option value="after_hours_limit_up">盤後漲停</Option>
            <Option value="custom_stocks">自定義股票</Option>
            <Option value="stock_code_list">股票代號列表</Option>
          </Select>
          <Button onClick={loadData} loading={loading}>
            刷新數據
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            導出數據
          </Button>
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        {/* 發文會話 */}
        <Col xs={24} lg={12}>
          <Card 
            title="發文會話" 
            extra={<Button type="link">查看全部</Button>}
          >
            <Table
              dataSource={sessions}
              columns={sessionColumns}
              rowKey="id"
              pagination={{ pageSize: 5 }}
              size="small"
              loading={loading}
            />
          </Card>
        </Col>

        {/* 最近發文 */}
        <Col xs={24} lg={12}>
          <Card 
            title="最近發文" 
            extra={<Button type="link">查看全部</Button>}
          >
            <Table
              dataSource={posts}
              columns={columns}
              rowKey="id"
              pagination={{ pageSize: 5 }}
              size="small"
              loading={loading}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PostingDashboard;
