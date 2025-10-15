import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Card,
  List,
  Tag,
  Typography,
  Space,
  Button,
  Select,
  Statistic,
  Row,
  Col,
  Divider,
  Tooltip,
  Badge,
  Empty,
  Spin,
  message
} from 'antd';
import {
  SendOutlined,
  EyeOutlined,
  LinkOutlined,
  IdcardOutlined,
  LikeOutlined,
  MessageOutlined,
  ShareAltOutlined,
  CalendarOutlined,
  UserOutlined,
  StockOutlined,
  FireOutlined,
  DeleteOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import PostingManagementAPI from '../../../services/postingManagementAPI';
import { Post } from '../../../types/posting';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface PublishedPostsSidebarProps {
  visible: boolean;
  onClose: () => void;
  sessionId?: number;
}

interface PublishedPost extends Post {
  cmoney_post_id?: string;
  cmoney_post_url?: string;
  views?: number;
  likes?: number;
  comments?: number;
  shares?: number;
  topic_id?: string;
  topic_title?: string;
}

const PublishedPostsSidebar: React.FC<PublishedPostsSidebarProps> = ({
  visible,
  onClose,
  sessionId
}) => {
  const [posts, setPosts] = useState<PublishedPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<'published' | 'deleted'>('published');
  const [stats, setStats] = useState({
    total: 0,
    published: 0,
    deleted: 0,
    totalViews: 0,
    totalLikes: 0,
    totalComments: 0,
    totalShares: 0
  });

  // 獲取已發布的貼文
  const fetchPublishedPosts = async () => {
    setLoading(true);
    try {
      const response = await PostingManagementAPI.getSessionPosts(sessionId || 1);
      
      if (response.success && response.data) {
        const allPosts = response.data.posts || [];
        
        // 篩選已發布或已刪除的貼文
        const publishedPosts = allPosts.filter(post => 
          post.status === 'published' || post.status === 'deleted'
        );
        
        setPosts(publishedPosts);
        
        // 計算統計數據
        const publishedCount = allPosts.filter(p => p.status === 'published').length;
        const deletedCount = allPosts.filter(p => p.status === 'deleted').length;
        const totalViews = allPosts.reduce((sum, p) => sum + (p.views || 0), 0);
        const totalLikes = allPosts.reduce((sum, p) => sum + (p.likes || 0), 0);
        const totalComments = allPosts.reduce((sum, p) => sum + (p.comments || 0), 0);
        const totalShares = allPosts.reduce((sum, p) => sum + (p.shares || 0), 0);
        
        setStats({
          total: publishedPosts.length,
          published: publishedCount,
          deleted: deletedCount,
          totalViews,
          totalLikes,
          totalComments,
          totalShares
        });
      }
    } catch (error) {
      console.error('獲取已發布貼文失敗:', error);
      message.error('獲取已發布貼文失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible) {
      fetchPublishedPosts();
    }
  }, [visible, sessionId]);

  // 根據狀態篩選貼文
  const filteredPosts = posts.filter(post => {
    if (filterStatus === 'published') {
      return post.status === 'published';
    } else if (filterStatus === 'deleted') {
      return post.status === 'deleted';
    }
    return true;
  });

  // 獲取狀態標籤
  const getStatusTag = (status: string) => {
    const statusConfig = {
      'published': { color: 'green', text: '已發布', icon: <CheckCircleOutlined /> },
      'deleted': { color: 'red', text: '已刪除', icon: <DeleteOutlined /> }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.published;
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 打開外部連結
  const openExternalLink = (url: string) => {
    if (url) {
      window.open(url, '_blank');
    }
  };

  // 複製到剪貼板
  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success(`${label}已複製到剪貼板`);
    }).catch(() => {
      message.error('複製失敗');
    });
  };

  return (
    <Drawer
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <Title level={4} style={{ margin: 0 }}>
              <SendOutlined style={{ marginRight: 8 }} />
              已發布貼文
            </Title>
            <Text type="secondary">查看詳細的發文記錄與互動數據</Text>
          </div>
          <Button 
            type="primary" 
            size="small" 
            onClick={fetchPublishedPosts}
            loading={loading}
          >
            刷新
          </Button>
        </div>
      }
      placement="right"
      width={600}
      open={visible}
      onClose={onClose}
      extra={
        <Space>
          <Select
            value={filterStatus}
            onChange={setFilterStatus}
            style={{ width: 120 }}
          >
            <Option value="published">已發布</Option>
            <Option value="deleted">已刪除</Option>
          </Select>
        </Space>
      }
    >
      {/* 統計數據 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="總數"
              value={stats.total}
              prefix={<SendOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="已發布"
              value={stats.published}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="已刪除"
              value={stats.deleted}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<DeleteOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="總瀏覽"
              value={stats.totalViews}
              prefix={<EyeOutlined />}
            />
          </Col>
        </Row>
        <Divider style={{ margin: '12px 0' }} />
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="總讚數"
              value={stats.totalLikes}
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="總留言"
              value={stats.totalComments}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="總分享"
              value={stats.totalShares}
              prefix={<ShareAltOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 貼文列表 */}
      <Spin spinning={loading}>
        {filteredPosts.length === 0 ? (
          <Empty
            description="暫無已發布的貼文"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <List
            dataSource={filteredPosts}
            renderItem={(post) => (
              <List.Item>
                <Card
                  size="small"
                  style={{ width: '100%' }}
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Text strong ellipsis={{ tooltip: post.title }}>
                        {post.title}
                      </Text>
                      {getStatusTag(post.status)}
                    </div>
                  }
                  extra={
                    <Space>
                      {post.cmoney_post_url && (
                        <Tooltip title="查看原文">
                          <Button
                            type="link"
                            icon={<LinkOutlined />}
                            onClick={() => openExternalLink(post.cmoney_post_url!)}
                          />
                        </Tooltip>
                      )}
                    </Space>
                  }
                >
                  {/* 基本信息 */}
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {/* KOL 和股票信息 */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Tag icon={<UserOutlined />} color="blue">
                        {post.kol_nickname || `KOL-${post.kol_serial}`}
                      </Tag>
                      <Tag icon={<StockOutlined />} color="green">
                        {post.stock_name}({post.stock_code})
                      </Tag>
                      {post.topic_id && (
                        <Tag icon={<FireOutlined />} color="orange">
                          熱門話題
                        </Tag>
                      )}
                    </div>

                    {/* 發布信息 */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                      <Space>
                        <CalendarOutlined />
                        <Text type="secondary">
                          {post.published_at ? new Date(post.published_at).toLocaleString() : '未發布'}
                        </Text>
                      </Space>
                      {post.cmoney_post_id && (
                        <Space>
                          <IdcardOutlined />
                          <Text 
                            code 
                            style={{ cursor: 'pointer' }}
                            onClick={() => copyToClipboard(post.cmoney_post_id!, '文章ID')}
                          >
                            {post.cmoney_post_id}
                          </Text>
                        </Space>
                      )}
                    </div>

                    {/* 互動數據 */}
                    {(post.views || post.likes || post.comments || post.shares) && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        {post.views && (
                          <Badge count={post.views} showZero>
                            <Button type="text" icon={<EyeOutlined />} size="small">
                              瀏覽
                            </Button>
                          </Badge>
                        )}
                        {post.likes && (
                          <Badge count={post.likes} showZero>
                            <Button type="text" icon={<LikeOutlined />} size="small">
                              讚
                            </Button>
                          </Badge>
                        )}
                        {post.comments && (
                          <Badge count={post.comments} showZero>
                            <Button type="text" icon={<MessageOutlined />} size="small">
                              留言
                            </Button>
                          </Badge>
                        )}
                        {post.shares && (
                          <Badge count={post.shares} showZero>
                            <Button type="text" icon={<ShareAltOutlined />} size="small">
                              分享
                            </Button>
                          </Badge>
                        )}
                      </div>
                    )}

                    {/* 熱門話題信息 */}
                    {post.topic_id && post.topic_title && (
                      <Card size="small" style={{ backgroundColor: '#fff7e6' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Text strong>關聯熱門話題</Text>
                          <Text ellipsis={{ tooltip: post.topic_title }}>
                            {post.topic_title}
                          </Text>
                          <Text code style={{ fontSize: '12px' }}>
                            Topic ID: {post.topic_id}
                          </Text>
                        </Space>
                      </Card>
                    )}

                    {/* 貼文內容預覽 */}
                    <div style={{ maxHeight: 100, overflow: 'hidden' }}>
                      <Paragraph
                        ellipsis={{ rows: 3, expandable: false }}
                        style={{ margin: 0, fontSize: '12px' }}
                      >
                        {post.content}
                      </Paragraph>
                    </div>
                  </Space>
                </Card>
              </List.Item>
            )}
          />
        )}
      </Spin>
    </Drawer>
  );
};

export default PublishedPostsSidebar;
