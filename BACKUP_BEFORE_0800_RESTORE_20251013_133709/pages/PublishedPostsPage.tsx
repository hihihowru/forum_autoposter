import React, { useState, useEffect } from 'react';
import {
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
  message,
  Input,
  DatePicker,
  Modal,
  Popconfirm
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
  CheckCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import PostingManagementAPI from '../services/postingManagementAPI';
import { Post } from '../types/posting';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;
const { RangePicker } = DatePicker;

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

const PublishedPostsPage: React.FC = () => {
  const [posts, setPosts] = useState<PublishedPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<'published' | 'deleted'>('published');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    published: 0,
    deleted: 0,
    totalViews: 0,
    totalLikes: 0,
    totalComments: 0,
    totalShares: 0
  });
  const [deletingPostId, setDeletingPostId] = useState<string | null>(null);

  // 獲取已發布的貼文
  const fetchPublishedPosts = async () => {
    setLoading(true);
    try {
      // 獲取所有貼文（不限於特定會話）
      const response = await PostingManagementAPI.getPosts(0, 1000); // 獲取最多1000篇貼文
      
      console.log('🔍 PublishedPostsPage - 原始響應:', response);
      
      if (response.posts) {
        const allPosts = response.posts || [];
        console.log('🔍 PublishedPostsPage - 所有貼文:', allPosts);
        
        // 篩選已發布或已刪除的貼文
        const publishedPosts = allPosts.filter(post => 
          post.status === 'published' || post.status === 'deleted'
        );
        
        console.log('🔍 PublishedPostsPage - 篩選後的貼文:', publishedPosts);
        console.log('🔍 PublishedPostsPage - 篩選後數量:', publishedPosts.length);
        
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
    fetchPublishedPosts();
  }, []);

  // 根據狀態、關鍵字和日期範圍篩選貼文
  const filteredPosts = posts.filter(post => {
    // 狀態篩選
    const statusMatch = filterStatus === 'published' ? post.status === 'published' : post.status === 'deleted';
    
    // 關鍵字篩選
    const keywordMatch = !searchKeyword || 
      post.title.toLowerCase().includes(searchKeyword.toLowerCase()) ||
      post.content.toLowerCase().includes(searchKeyword.toLowerCase()) ||
      post.stock_name?.toLowerCase().includes(searchKeyword.toLowerCase()) ||
      post.kol_nickname?.toLowerCase().includes(searchKeyword.toLowerCase());
    
    // 日期範圍篩選
    let dateMatch = true;
    if (dateRange && dateRange[0] && dateRange[1]) {
      const postDate = new Date(post.published_at || post.created_at);
      const startDate = dateRange[0].startOf('day');
      const endDate = dateRange[1].endOf('day');
      dateMatch = postDate >= startDate && postDate <= endDate;
    }
    
    return statusMatch && keywordMatch && dateMatch;
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

  // 刪除貼文
  const handleDeletePost = async (postId: string, postTitle: string) => {
    setDeletingPostId(postId);
    
    try {
      const result = await PostingManagementAPI.deletePost(postId);
      
      if (result.success) {
        message.success(`貼文「${postTitle}」已成功刪除`);
        // 重新獲取貼文列表
        await fetchPublishedPosts();
      } else {
        message.error(`刪除失敗: ${result.error || '未知錯誤'}`);
      }
    } catch (error) {
      console.error('刪除貼文失敗:', error);
      message.error('刪除貼文時發生錯誤');
    } finally {
      setDeletingPostId(null);
    }
  };

  // 確認刪除對話框
  const showDeleteConfirm = (postId: string, postTitle: string) => {
    Modal.confirm({
      title: '確認刪除',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>您確定要刪除這篇貼文嗎？</p>
          <p><strong>標題：</strong>{postTitle}</p>
          <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
            ⚠️ 此操作將從 CMoney 平台刪除該貼文，並將狀態標記為「已刪除」
          </p>
        </div>
      ),
      okText: '確認刪除',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => handleDeletePost(postId, postTitle),
    });
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <SendOutlined style={{ marginRight: 8 }} />
          已發布貼文管理
        </Title>
        <Text type="secondary">查看和管理所有已發布的貼文記錄與互動數據</Text>
      </div>

      {/* 統計數據 */}
      <Card size="small" style={{ marginBottom: 24 }}>
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

      {/* 篩選和搜索 */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select
              value={filterStatus}
              onChange={setFilterStatus}
              style={{ width: '100%' }}
            >
              <Option value="published">已發布</Option>
              <Option value="deleted">已刪除</Option>
            </Select>
          </Col>
          <Col span={8}>
            <Search
              placeholder="搜索標題、內容、股票或KOL"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={8}>
            <RangePicker
              placeholder={['開始日期', '結束日期']}
              value={dateRange}
              onChange={setDateRange}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={2}>
            <Button 
              type="primary" 
              icon={<ReloadOutlined />}
              onClick={fetchPublishedPosts}
              loading={loading}
            >
              刷新
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 貼文列表 */}
      <Card title={`📋 貼文列表 (${filteredPosts.length} 篇)`}>
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
                        {post.status === 'published' && (
                          <Tooltip title="刪除貼文">
                            <Button
                              type="link"
                              danger
                              icon={<DeleteOutlined />}
                              loading={deletingPostId === post.post_id}
                              onClick={() => showDeleteConfirm(post.post_id, post.title)}
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
      </Card>
    </div>
  );
};

export default PublishedPostsPage;
