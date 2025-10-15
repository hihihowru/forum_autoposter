import React from 'react';
import { Card, Row, Col, Statistic, Button, Space, Typography, List, Tag } from 'antd';
import { 
  EditOutlined,
  CheckCircleOutlined, 
  ClockCircleOutlined,
  ScheduleOutlined,
  TagsOutlined,
  RocketOutlined,
  FileTextOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const PostingManagement: React.FC = () => {
  const navigate = useNavigate();

  // 模擬數據
  const stats = {
    pending_review: 5,
    published_today: 12,
    scheduled_tasks: 3,
    error_alerts: 2
  };

  const recentActivities = [
    {
      id: 'GEN_001',
      type: 'generated',
      title: '台股突破24000點分析',
      kol: '川川哥',
      time: '14:30',
      status: 'pending'
    },
    {
      id: 'GEN_002',
      type: 'approved',
      title: '漲停股資金流向分析',
      kol: '籌碼派',
      time: '14:25',
      status: 'approved'
    },
    {
      id: 'SCH_001',
      type: 'scheduled',
      title: '熱門話題發文機器人',
      kol: '自動',
      time: '18:00',
      status: 'running'
    }
  ];

  const quickActions = [
    {
      title: '發文生成器',
      description: '快速生成新內容',
      icon: <RocketOutlined />,
      color: '#1890ff',
      path: '/posting-management/generator'
    },
    {
      title: '發文審核',
      description: '審核待發布內容',
      icon: <CheckCircleOutlined />,
      color: '#52c41a',
      path: '/posting-management/review'
    },
    {
      title: '部署排程',
      description: '管理自動化排程',
      icon: <ScheduleOutlined />,
      color: '#faad14',
      path: '/posting-management/scheduling'
    },
    {
      title: '標籤管理',
      description: '管理內容標籤',
      icon: <TagsOutlined />,
      color: '#722ed1',
      path: '/posting-management/tags'
    }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'generated': return <FileTextOutlined />;
      case 'approved': return <CheckCircleOutlined />;
      case 'scheduled': return <ScheduleOutlined />;
      default: return <BarChartOutlined />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'generated': return 'blue';
      case 'approved': return 'green';
      case 'scheduled': return 'orange';
      default: return 'default';
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
          <Col>
            <Space>
              <EditOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <div>
                <h2 style={{ margin: 0 }}>發文管理系統</h2>
                <p style={{ margin: 0, color: '#666' }}>
                  智能內容生成、審核和排程管理平台
                </p>
              </div>
            </Space>
          </Col>
        </Row>

        {/* 統計概覽 */}
        <Card size="small" style={{ marginBottom: '24px' }}>
          <Title level={4}>今日統計</Title>
          <Row gutter={16}>
            <Col span={6}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <Statistic
                  title="待審核"
                  value={stats.pending_review}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
                <Button 
                  type="link" 
                  size="small"
                  onClick={() => navigate('/posting-management/review')}
                >
                  前往審核
                </Button>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <Statistic
                  title="今日發布"
                  value={stats.published_today}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
                <Button 
                  type="link" 
                  size="small"
                  onClick={() => navigate('/posting-management/generator')}
                >
                  快速生成
                </Button>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <Statistic
                  title="排程任務"
                  value={stats.scheduled_tasks}
                  prefix={<ScheduleOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
                <Button 
                  type="link" 
                  size="small"
                  onClick={() => navigate('/posting-management/scheduling')}
                >
                  管理排程
                </Button>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <Statistic
                  title="異常告警"
                  value={stats.error_alerts}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#ff4d4f' }}
                />
                <Button 
                  type="link" 
                  size="small"
                  onClick={() => navigate('/posting-management/review')}
                >
                  查看詳情
                </Button>
              </Card>
            </Col>
          </Row>
        </Card>

        <Row gutter={[16, 16]}>
          {/* 快速操作 */}
          <Col xs={24} lg={12}>
            <Card title="快速操作" size="small">
              <Row gutter={[16, 16]}>
                {quickActions.map((action, index) => (
                  <Col xs={24} sm={12} key={index}>
                    <Card 
                      size="small" 
                      hoverable
                      style={{ 
                        height: '100%',
                        cursor: 'pointer',
                        border: '1px solid #d9d9d9'
                      }}
                      onClick={() => navigate(action.path)}
                    >
                      <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }}>
                        <div style={{ fontSize: '24px', color: action.color }}>
                          {action.icon}
                        </div>
                        <div>
                          <Text strong>{action.title}</Text>
                        </div>
                        <div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {action.description}
                          </Text>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>

          {/* 最近活動 */}
          <Col xs={24} lg={12}>
            <Card title="最近活動" size="small">
              <List
                size="small"
                dataSource={recentActivities}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <div style={{ 
                          fontSize: '16px', 
                          color: getActivityColor(item.type) === 'blue' ? '#1890ff' : 
                                 getActivityColor(item.type) === 'green' ? '#52c41a' : '#faad14'
                        }}>
                          {getActivityIcon(item.type)}
                        </div>
                      }
                      title={
                        <Space>
                          <Text strong>{item.title}</Text>
                          <Tag color={getActivityColor(item.type)}>
                            {item.type === 'generated' ? '已生成' : 
                             item.type === 'approved' ? '已通過' : '已排程'}
                          </Tag>
                        </Space>
                      }
                      description={
                        <Space>
                          <Text type="secondary">KOL: {item.kol}</Text>
                          <Text type="secondary">時間: {item.time}</Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default PostingManagement;
