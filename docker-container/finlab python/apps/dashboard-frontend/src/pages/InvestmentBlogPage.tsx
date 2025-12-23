import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Select,
  message,
  Space,
  Typography,
  Spin,
  Table,
  Tag,
  Divider,
  Empty,
  Alert,
  Tooltip,
  Modal,
  Statistic,
} from 'antd';
import {
  SendOutlined,
  SyncOutlined,
  ReadOutlined,
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  StopOutlined,
  EyeOutlined,
  LinkOutlined,
  ReloadOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

// Types
interface Article {
  id: string;
  title: string;
  content: string;
  stock_tags: string[];
  preview_img_url?: string;
  total_views: number;
  status: 'pending' | 'posted' | 'skipped' | 'failed';
  posted_at?: string;
  posted_by?: string;
  cmoney_post_url?: string;
  fetched_at?: string;
  cmoney_created_at?: number;
}

interface SyncState {
  author_id: string;
  last_seen_article_id: string | null;
  last_sync_at: string | null;
  articles_synced_count: number;
}

interface PostingConfig {
  poster_email: string;
  poster_name: string;
}

const InvestmentBlogPage: React.FC = () => {
  // State
  const [articles, setArticles] = useState<Article[]>([]);
  const [syncState, setSyncState] = useState<SyncState | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchingArticles, setFetchingArticles] = useState(false);
  const [posting, setPosting] = useState<{ [key: string]: boolean }>({});
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [contentModalVisible, setContentModalVisible] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);

  // Designated poster config
  const [posterConfig] = useState<PostingConfig>({
    poster_email: 'forum_190@cmoney.com.tw',
    poster_name: '投資網誌專用帳號'
  });

  // API base URL - posting-service runs on port 8001
  const API_BASE = import.meta.env.DEV
    ? 'http://localhost:8001'
    : 'https://forumautoposter-production.up.railway.app';

  // Initialize - load sync state and articles
  useEffect(() => {
    loadSyncState();
    loadArticles();
  }, [statusFilter]);

  // Load sync state
  const loadSyncState = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/sync-state`);
      if (!response.ok) throw new Error('Failed to load sync state');
      const data = await response.json();
      setSyncState(data);
    } catch (error) {
      console.error('Failed to load sync state:', error);
    }
  };

  // Load articles from database
  const loadArticles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      params.append('limit', '100');

      const response = await fetch(`${API_BASE}/api/investment-blog/articles?${params}`);
      if (!response.ok) throw new Error('Failed to load articles');
      const data = await response.json();
      setArticles(data.articles || []);
    } catch (error) {
      console.error('Failed to load articles:', error);
      message.error('Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  // Fetch new articles from CMoney API
  const fetchNewArticles = async () => {
    setFetchingArticles(true);
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/fetch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          author_id: 'newsyoudeservetoknow',
          fetch_content: true
        })
      });

      if (!response.ok) throw new Error('Failed to fetch articles');
      const data = await response.json();

      message.success(`Fetched ${data.articles_count} new articles`);

      // Reload articles and sync state
      await loadArticles();
      await loadSyncState();

    } catch (error) {
      console.error('Failed to fetch articles:', error);
      message.error('Failed to fetch articles: ' + (error as Error).message);
    } finally {
      setFetchingArticles(false);
    }
  };

  // Post article to forum
  const postArticle = async (article: Article) => {
    try {
      setPosting(prev => ({ ...prev, [article.id]: true }));

      message.loading({ content: 'Posting article...', key: 'posting', duration: 0 });

      const response = await fetch(`${API_BASE}/api/investment-blog/post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          article_id: article.id,
          poster_email: posterConfig.poster_email,
          stock_tags: article.stock_tags
        })
      });

      const result = await response.json();

      message.destroy('posting');

      if (result.success) {
        message.success({
          content: (
            <div>
              <div>Posted successfully!</div>
              {result.cmoney_post_url && (
                <a href={result.cmoney_post_url} target="_blank" rel="noopener noreferrer">
                  View article
                </a>
              )}
            </div>
          ),
          duration: 5
        });

        // Reload articles
        await loadArticles();
      } else {
        message.error(`Failed to post: ${result.message}`);
      }

    } catch (error) {
      console.error('Failed to post article:', error);
      message.destroy('posting');
      message.error('Failed to post article: ' + (error as Error).message);
    } finally {
      setPosting(prev => ({ ...prev, [article.id]: false }));
    }
  };

  // Skip article
  const skipArticle = async (article: Article) => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/articles/${article.id}/skip`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to skip article');

      message.success('Article skipped');
      await loadArticles();

    } catch (error) {
      console.error('Failed to skip article:', error);
      message.error('Failed to skip article');
    }
  };

  // Reset article to pending
  const resetArticle = async (article: Article) => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/articles/${article.id}/reset`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to reset article');

      message.success('Article reset to pending');
      await loadArticles();

    } catch (error) {
      console.error('Failed to reset article:', error);
      message.error('Failed to reset article');
    }
  };

  // View full article content
  const viewArticleContent = async (article: Article) => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/articles/${article.id}`);
      if (!response.ok) throw new Error('Failed to load article');
      const data = await response.json();
      setSelectedArticle(data.article);
      setContentModalVisible(true);
    } catch (error) {
      console.error('Failed to load article:', error);
      message.error('Failed to load article content');
    }
  };

  // Get status tag
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'posted':
        return <Tag color="green" icon={<CheckCircleOutlined />}>Posted</Tag>;
      case 'failed':
        return <Tag color="red" icon={<ExclamationCircleOutlined />}>Failed</Tag>;
      case 'skipped':
        return <Tag color="orange" icon={<StopOutlined />}>Skipped</Tag>;
      default:
        return <Tag color="blue" icon={<ClockCircleOutlined />}>Pending</Tag>;
    }
  };

  // Format timestamp
  const formatTimestamp = (ts: number | undefined) => {
    if (!ts) return '-';
    return new Date(ts).toLocaleString('zh-TW');
  };

  // Table columns
  const columns = [
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status)
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: Article) => (
        <div>
          <Tooltip title={title}>
            <Text strong style={{ cursor: 'pointer' }} onClick={() => viewArticleContent(record)}>
              {title.length > 50 ? title.substring(0, 50) + '...' : title}
            </Text>
          </Tooltip>
          {record.cmoney_post_url && (
            <div>
              <a href={record.cmoney_post_url} target="_blank" rel="noopener noreferrer">
                <LinkOutlined /> View Post
              </a>
            </div>
          )}
        </div>
      )
    },
    {
      title: 'Stock Tags',
      dataIndex: 'stock_tags',
      key: 'stock_tags',
      width: 200,
      render: (tags: string[]) => (
        <Space wrap>
          {(tags || []).slice(0, 5).map(tag => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
          {(tags || []).length > 5 && (
            <Tag>+{tags.length - 5} more</Tag>
          )}
        </Space>
      )
    },
    {
      title: 'Views',
      dataIndex: 'total_views',
      key: 'total_views',
      width: 80,
      render: (views: number) => views?.toLocaleString() || '0'
    },
    {
      title: 'Created',
      dataIndex: 'cmoney_created_at',
      key: 'cmoney_created_at',
      width: 150,
      render: (ts: number) => formatTimestamp(ts)
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: any, record: Article) => (
        <Space>
          <Tooltip title="View Content">
            <Button
              icon={<EyeOutlined />}
              size="small"
              onClick={() => viewArticleContent(record)}
            />
          </Tooltip>

          {record.status === 'pending' && (
            <>
              <Button
                type="primary"
                icon={<SendOutlined />}
                size="small"
                loading={posting[record.id]}
                onClick={() => postArticle(record)}
              >
                Post
              </Button>
              <Button
                icon={<StopOutlined />}
                size="small"
                onClick={() => skipArticle(record)}
              >
                Skip
              </Button>
            </>
          )}

          {(record.status === 'skipped' || record.status === 'failed') && (
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={() => resetArticle(record)}
            >
              Reset
            </Button>
          )}
        </Space>
      )
    }
  ];

  // Count articles by status
  const pendingCount = articles.filter(a => a.status === 'pending').length;
  const postedCount = articles.filter(a => a.status === 'posted').length;

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* Page Header */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0 }}>
              <ReadOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
              投資網誌 (Investment Blog)
            </Title>
            <Text type="secondary">
              Fetch articles from newsyoudeservetoknow and post to forum with stock tags
            </Text>
          </Col>
          <Col>
            <Space>
              <Statistic title="Pending" value={pendingCount} valueStyle={{ color: '#1890ff' }} />
              <Statistic title="Posted" value={postedCount} valueStyle={{ color: '#52c41a' }} />
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Poster Configuration & Sync State */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={12}>
          <Card
            title={
              <Space>
                <UserOutlined />
                <span>Designated Poster</span>
              </Space>
            }
            size="small"
          >
            <Tag color="blue" icon={<UserOutlined />} style={{ fontSize: '14px', padding: '4px 12px' }}>
              {posterConfig.poster_email}
            </Tag>
            <div style={{ marginTop: '8px' }}>
              <Text type="secondary">{posterConfig.poster_name}</Text>
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card
            title={
              <Space>
                <SyncOutlined />
                <span>Sync State</span>
              </Space>
            }
            size="small"
          >
            {syncState ? (
              <Space direction="vertical" size="small">
                <Text>
                  <strong>Last Sync:</strong>{' '}
                  {syncState.last_sync_at ? new Date(syncState.last_sync_at).toLocaleString('zh-TW') : 'Never'}
                </Text>
                <Text>
                  <strong>Total Synced:</strong> {syncState.articles_synced_count} articles
                </Text>
              </Space>
            ) : (
              <Text type="secondary">No sync history</Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* Articles Table */}
      <Card
        title={
          <Space>
            <ReadOutlined />
            <span>Articles</span>
          </Space>
        }
        extra={
          <Space>
            <Select
              style={{ width: 120 }}
              placeholder="Filter"
              allowClear
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'posted', label: 'Posted' },
                { value: 'skipped', label: 'Skipped' },
                { value: 'failed', label: 'Failed' },
              ]}
            />
            <Button
              icon={<ReloadOutlined />}
              onClick={loadArticles}
              loading={loading}
            >
              Refresh
            </Button>
            <Button
              type="primary"
              icon={<SyncOutlined spin={fetchingArticles} />}
              onClick={fetchNewArticles}
              loading={fetchingArticles}
            >
              Fetch New Articles
            </Button>
          </Space>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
          </div>
        ) : articles.length === 0 ? (
          <Empty
            description="No articles yet. Click 'Fetch New Articles' to get started."
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={articles}
            rowKey="id"
            pagination={{ pageSize: 20 }}
          />
        )}
      </Card>

      {/* Article Content Modal */}
      <Modal
        title={selectedArticle?.title || 'Article Content'}
        open={contentModalVisible}
        onCancel={() => setContentModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setContentModalVisible(false)}>
            Close
          </Button>,
          selectedArticle?.status === 'pending' && (
            <Button
              key="post"
              type="primary"
              icon={<SendOutlined />}
              loading={selectedArticle ? posting[selectedArticle.id] : false}
              onClick={() => {
                if (selectedArticle) {
                  postArticle(selectedArticle);
                  setContentModalVisible(false);
                }
              }}
            >
              Post Article
            </Button>
          )
        ].filter(Boolean)}
      >
        {selectedArticle && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <Space wrap>
                {getStatusTag(selectedArticle.status)}
                <Text type="secondary">
                  Views: {selectedArticle.total_views?.toLocaleString() || '0'}
                </Text>
              </Space>
            </div>

            {selectedArticle.stock_tags && selectedArticle.stock_tags.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <Text strong>Stock Tags: </Text>
                <Space wrap>
                  {selectedArticle.stock_tags.map(tag => (
                    <Tag key={tag} color="blue">{tag}</Tag>
                  ))}
                </Space>
              </div>
            )}

            <Divider />

            <div
              style={{
                maxHeight: '400px',
                overflow: 'auto',
                padding: '16px',
                background: '#fafafa',
                borderRadius: '4px'
              }}
              dangerouslySetInnerHTML={{ __html: selectedArticle.content || 'No content' }}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default InvestmentBlogPage;
