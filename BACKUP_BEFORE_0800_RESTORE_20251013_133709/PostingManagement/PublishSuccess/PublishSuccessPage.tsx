import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Tag, 
  Space, 
  Typography, 
  Row, 
  Col, 
  Statistic, 
  Modal, 
  message, 
  Spin,
  Tooltip,
  Popconfirm,
  Divider,
  Badge,
  Alert,
  Timeline,
  Progress
} from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  SendOutlined, 
  EyeOutlined, 
  CopyOutlined,
  LinkOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  ExportOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import PostingManagementAPI from '../../../services/postingManagementAPI';

const { Title, Text, Paragraph } = Typography;
const { Column } = Table;

interface PublishedPost {
  id: string;
  session_id: number;
  title: string;
  content: string;
  status: string;
  kol_serial: number;
  kol_nickname: string;
  kol_persona: string;
  stock_codes: string[];
  stock_names: string[];
  cmoney_post_id: string;
  cmoney_post_url: string;
  published_at: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  created_at: string;
  updated_at: string;
}

interface PublishSuccessPageProps {
  sessionId?: number;
  onBack?: () => void;
}

const PublishSuccessPage: React.FC<PublishSuccessPageProps> = ({ sessionId, onBack }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // 狀態管理
  const [posts, setPosts] = useState<PublishedPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPost, setSelectedPost] = useState<PublishedPost | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);

  // 從URL參數或props獲取sessionId
  const currentSessionId = sessionId || new URLSearchParams(location.search).get('sessionId');

  // 載入已發佈的貼文
  const loadPublishedPosts = async () => {
    if (!currentSessionId) return;
    
    setLoading(true);
    try {
      const response = await PostingManagementAPI.getSessionPosts(
        parseInt(currentSessionId), 
        0, 
        100, 
        'published'
      );
      
      if (response.posts) {
        setPosts(response.posts);
        console.log('✅ 已載入發佈的貼文:', response.posts.length);
      }
    } catch (error) {
      console.error('載入已發佈貼文失敗:', error);
      message.error('載入已發佈貼文失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPublishedPosts();
  }, [currentSessionId]);

  // 刷新數據
  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPublishedPosts();
    setRefreshing(false);
    message.success('數據已刷新');
  };

  // 查看貼文詳情
  const handleViewPost = (post: PublishedPost) => {
    setSelectedPost(post);
    setPreviewVisible(true);
  };

  // 複製貼文URL
  const handleCopyUrl = (url: string) => {
    navigator.clipboard.writeText(url);
    message.success('貼文URL已複製到剪貼板');
  };

  // 在新視窗開啟貼文
  const handleOpenPost = (url: string) => {
    window.open(url, '_blank');
  };

  // 統計數據
  const stats = {
    total: posts.length,
    published: posts.filter(p => p.status === 'published').length,
    totalViews: posts.reduce((sum, p) => sum + (p.views || 0), 0),
    totalLikes: posts.reduce((sum, p) => sum + (p.likes || 0), 0),
    totalComments: posts.reduce((sum, p) => sum + (p.comments || 0), 0),
    totalShares: posts.reduce((sum, p) => sum + (p.shares || 0), 0)
  };

  // 表格列定義
  const columns = [
    {
      title: '貼文標題',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (title: string, record: PublishedPost) => (
        <Space direction="vertical" size="small">
          <Text strong style={{ fontSize: '14px' }}>{title}</Text>
          <Space size="small">
            <Tag color="blue">{record.kol_nickname}</Tag>
            <Tag color="green">{record.stock_names.join(', ')}</Tag>
          </Space>
        </Space>
      )
    },
    {
      title: '發佈狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusConfig = {
          'published': { color: 'green', text: '已發佈', icon: <CheckCircleOutlined /> },
          'failed': { color: 'red', text: '發佈失敗', icon: <CloseCircleOutlined /> },
          'pending': { color: 'orange', text: '發佈中', icon: <ClockCircleOutlined /> }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status };
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: 'CMoney貼文',
      key: 'cmoney_post',
      width: 200,
      render: (record: PublishedPost) => (
        <Space direction="vertical" size="small">
          {record.cmoney_post_id ? (
            <>
              <Text code style={{ fontSize: '12px' }}>{record.cmoney_post_id}</Text>
              <Space size="small">
                <Tooltip title="複製URL">
                  <Button
                    type="link"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => handleCopyUrl(record.cmoney_post_url)}
                  />
                </Tooltip>
                <Tooltip title="開啟貼文">
                  <Button
                    type="link"
                    size="small"
                    icon={<LinkOutlined />}
                    onClick={() => handleOpenPost(record.cmoney_post_url)}
                  />
                </Tooltip>
              </Space>
            </>
          ) : (
            <Text type="secondary">未發佈</Text>
          )}
        </Space>
      )
    },
    {
      title: '互動數據',
      key: 'interactions',
      width: 150,
      render: (record: PublishedPost) => (
        <Space direction="vertical" size="small">
          <Space size="small">
            <Text type="secondary">👁️ {record.views || 0}</Text>
            <Text type="secondary">👍 {record.likes || 0}</Text>
          </Space>
          <Space size="small">
            <Text type="secondary">💬 {record.comments || 0}</Text>
            <Text type="secondary">🔄 {record.shares || 0}</Text>
          </Space>
        </Space>
      )
    },
    {
      title: '發佈時間',
      dataIndex: 'published_at',
      key: 'published_at',
      width: 150,
      render: (publishedAt: string) => (
        <Text type="secondary">
          {publishedAt ? new Date(publishedAt).toLocaleString('zh-TW') : '未發佈'}
        </Text>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (record: PublishedPost) => (
        <Space>
          <Tooltip title="查看詳情">
            <Button
              type="primary"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewPost(record)}
            />
          </Tooltip>
          {record.cmoney_post_url && (
            <Tooltip title="開啟貼文">
              <Button
                size="small"
                icon={<SendOutlined />}
                onClick={() => handleOpenPost(record.cmoney_post_url)}
              />
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <CheckCircleOutlined style={{ color: '#52c41a' }} /> 發文成功
          </Title>
          <Text type="secondary">
            會話ID: {currentSessionId} | 共發佈 {stats.published} 篇貼文
          </Text>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={refreshing}
            >
              刷新數據
            </Button>
            <Button
              icon={<ExportOutlined />}
              onClick={() => message.info('匯出功能開發中...')}
            >
              匯出報告
            </Button>
            {onBack && (
              <Button onClick={onBack}>
                返回
              </Button>
            )}
          </Space>
        </Col>
      </Row>

      {/* 統計卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="總貼文數"
              value={stats.total}
              prefix={<SendOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已發佈"
              value={stats.published}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="總瀏覽數"
              value={stats.totalViews}
              prefix="👁️"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="總互動數"
              value={stats.totalLikes + stats.totalComments + stats.totalShares}
              prefix="💬"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 發佈進度 */}
      {stats.total > 0 && (
        <Card style={{ marginBottom: 24 }}>
          <Title level={4}>發佈進度</Title>
          <Progress
            percent={Math.round((stats.published / stats.total) * 100)}
            status={stats.published === stats.total ? 'success' : 'active'}
            format={(percent) => `${stats.published}/${stats.total} (${percent}%)`}
          />
        </Card>
      )}

      {/* 貼文列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={posts}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 篇貼文`
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 貼文詳情Modal */}
      <Modal
        title={
          <Space>
            <EyeOutlined />
            <span>貼文詳情 - {selectedPost?.title}</span>
          </Space>
        }
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            關閉
          </Button>,
          selectedPost?.cmoney_post_url && (
            <Button
              key="open"
              type="primary"
              icon={<LinkOutlined />}
              onClick={() => handleOpenPost(selectedPost.cmoney_post_url)}
            >
              開啟貼文
            </Button>
          )
        ]}
      >
        {selectedPost && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Text strong>KOL: </Text>
                <Tag color="blue">{selectedPost.kol_nickname}</Tag>
              </Col>
              <Col span={12}>
                <Text strong>股票: </Text>
                <Tag color="green">{selectedPost.stock_names.join(', ')}</Tag>
              </Col>
            </Row>
            
            <Divider />
            
            <div style={{ marginBottom: 16 }}>
              <Text strong>貼文內容:</Text>
              <div
                style={{
                  marginTop: 8,
                  padding: 12,
                  backgroundColor: '#f5f5f5',
                  borderRadius: 6,
                  maxHeight: 300,
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {selectedPost.content}
              </div>
            </div>

            {selectedPost.cmoney_post_url && (
              <div>
                <Text strong>CMoney貼文連結:</Text>
                <div style={{ marginTop: 8 }}>
                  <Text code style={{ fontSize: '12px' }}>
                    {selectedPost.cmoney_post_url}
                  </Text>
                  <Button
                    type="link"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => handleCopyUrl(selectedPost.cmoney_post_url)}
                  >
                    複製
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PublishSuccessPage;
