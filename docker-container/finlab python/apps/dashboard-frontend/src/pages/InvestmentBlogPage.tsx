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
  Tooltip,
  Modal,
  Statistic,
  Switch,
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
  RobotOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

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
  const [autoPostEnabled, setAutoPostEnabled] = useState(false);
  const [togglingAutoPost, setTogglingAutoPost] = useState(false);

  // 指定發文帳號
  const [posterConfig] = useState<PostingConfig>({
    poster_email: 'forum_190@cmoney.com.tw',
    poster_name: '投資網誌專用帳號'
  });

  // API 基礎網址 - posting-service 在 8001 端口
  const API_BASE = import.meta.env.DEV
    ? 'http://localhost:8001'
    : 'https://forumautoposter-production.up.railway.app';

  // 初始化 - 載入同步狀態和文章
  useEffect(() => {
    loadSyncState();
    loadArticles();
    loadAutoPostStatus();
  }, [statusFilter]);

  // 載入自動發文狀態
  const loadAutoPostStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/auto-post/status`);
      if (!response.ok) throw new Error('載入自動發文狀態失敗');
      const data = await response.json();
      setAutoPostEnabled(data.enabled || false);
    } catch (error) {
      console.error('載入自動發文狀態失敗:', error);
    }
  };

  // 切換自動發文
  const toggleAutoPost = async (enabled: boolean) => {
    try {
      setTogglingAutoPost(true);
      const response = await fetch(`${API_BASE}/api/investment-blog/auto-post/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
      });

      if (!response.ok) throw new Error('切換自動發文失敗');
      const data = await response.json();

      setAutoPostEnabled(data.enabled);
      message.success(data.message);
    } catch (error) {
      console.error('切換自動發文失敗:', error);
      message.error('切換自動發文失敗');
    } finally {
      setTogglingAutoPost(false);
    }
  };

  // 載入同步狀態
  const loadSyncState = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/sync-state`);
      if (!response.ok) throw new Error('載入同步狀態失敗');
      const data = await response.json();
      setSyncState(data);
    } catch (error) {
      console.error('載入同步狀態失敗:', error);
    }
  };

  // 從資料庫載入文章
  const loadArticles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      params.append('limit', '100');

      const response = await fetch(`${API_BASE}/api/investment-blog/articles?${params}`);
      if (!response.ok) throw new Error('載入文章失敗');
      const data = await response.json();
      setArticles(data.articles || []);
    } catch (error) {
      console.error('載入文章失敗:', error);
      message.error('載入文章失敗');
    } finally {
      setLoading(false);
    }
  };

  // 從 CMoney API 抓取新文章
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

      if (!response.ok) throw new Error('抓取文章失敗');
      const data = await response.json();

      message.success(`已抓取 ${data.articles_count} 篇新文章`);

      // 重新載入文章和同步狀態
      await loadArticles();
      await loadSyncState();

    } catch (error) {
      console.error('抓取文章失敗:', error);
      message.error('抓取文章失敗: ' + (error as Error).message);
    } finally {
      setFetchingArticles(false);
    }
  };

  // 發佈文章到論壇
  const postArticle = async (article: Article) => {
    try {
      setPosting(prev => ({ ...prev, [article.id]: true }));

      message.loading({ content: '正在發佈文章...', key: 'posting', duration: 0 });

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
              <div>發佈成功！</div>
              {result.cmoney_post_url && (
                <a href={result.cmoney_post_url} target="_blank" rel="noopener noreferrer">
                  查看文章
                </a>
              )}
            </div>
          ),
          duration: 5
        });

        // 重新載入文章
        await loadArticles();
      } else {
        message.error(`發佈失敗: ${result.message}`);
      }

    } catch (error) {
      console.error('發佈文章失敗:', error);
      message.destroy('posting');
      message.error('發佈文章失敗: ' + (error as Error).message);
    } finally {
      setPosting(prev => ({ ...prev, [article.id]: false }));
    }
  };

  // 跳過文章
  const skipArticle = async (article: Article) => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/articles/${article.id}/skip`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('跳過文章失敗');

      message.success('已跳過文章');
      await loadArticles();

    } catch (error) {
      console.error('跳過文章失敗:', error);
      message.error('跳過文章失敗');
    }
  };

  // 重設文章狀態為待處理
  const resetArticle = async (article: Article) => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/articles/${article.id}/reset`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('重設文章失敗');

      message.success('已重設為待處理');
      await loadArticles();

    } catch (error) {
      console.error('重設文章失敗:', error);
      message.error('重設文章失敗');
    }
  };

  // 查看完整文章內容
  const viewArticleContent = async (article: Article) => {
    try {
      const response = await fetch(`${API_BASE}/api/investment-blog/articles/${article.id}`);
      if (!response.ok) throw new Error('載入文章失敗');
      const data = await response.json();
      setSelectedArticle(data.article);
      setContentModalVisible(true);
    } catch (error) {
      console.error('載入文章失敗:', error);
      message.error('載入文章內容失敗');
    }
  };

  // 取得狀態標籤
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'posted':
        return <Tag color="green" icon={<CheckCircleOutlined />}>已發佈</Tag>;
      case 'failed':
        return <Tag color="red" icon={<ExclamationCircleOutlined />}>失敗</Tag>;
      case 'skipped':
        return <Tag color="orange" icon={<StopOutlined />}>已跳過</Tag>;
      default:
        return <Tag color="blue" icon={<ClockCircleOutlined />}>待處理</Tag>;
    }
  };

  // 格式化時間戳
  const formatTimestamp = (ts: number | undefined) => {
    if (!ts) return '-';
    return new Date(ts).toLocaleString('zh-TW');
  };

  // 表格欄位
  const columns = [
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status)
    },
    {
      title: '標題',
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
                <LinkOutlined /> 查看貼文
              </a>
            </div>
          )}
        </div>
      )
    },
    {
      title: '股票標籤',
      dataIndex: 'stock_tags',
      key: 'stock_tags',
      width: 200,
      render: (tags: string[]) => (
        <Space wrap>
          {(tags || []).slice(0, 5).map(tag => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
          {(tags || []).length > 5 && (
            <Tag>+{tags.length - 5} 更多</Tag>
          )}
        </Space>
      )
    },
    {
      title: '瀏覽數',
      dataIndex: 'total_views',
      key: 'total_views',
      width: 80,
      render: (views: number) => views?.toLocaleString() || '0'
    },
    {
      title: '建立時間',
      dataIndex: 'cmoney_created_at',
      key: 'cmoney_created_at',
      width: 150,
      render: (ts: number) => formatTimestamp(ts)
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: Article) => (
        <Space>
          <Tooltip title="查看內容">
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
                發佈
              </Button>
              <Button
                icon={<StopOutlined />}
                size="small"
                onClick={() => skipArticle(record)}
              >
                跳過
              </Button>
            </>
          )}

          {(record.status === 'skipped' || record.status === 'failed') && (
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={() => resetArticle(record)}
            >
              重設
            </Button>
          )}
        </Space>
      )
    }
  ];

  // 統計文章數量
  const pendingCount = articles.filter(a => a.status === 'pending').length;
  const postedCount = articles.filter(a => a.status === 'posted').length;

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 頁面標題 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0 }}>
              <ReadOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
              投資網誌
            </Title>
            <Text type="secondary">
              從 newsyoudeservetoknow 抓取文章並發佈到論壇，自動標記股票代碼
            </Text>
          </Col>
          <Col>
            <Space size="large">
              <Statistic title="待處理" value={pendingCount} valueStyle={{ color: '#1890ff' }} />
              <Statistic title="已發佈" value={postedCount} valueStyle={{ color: '#52c41a' }} />
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 自動發文開關 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space>
              <RobotOutlined style={{ fontSize: '20px', color: autoPostEnabled ? '#52c41a' : '#999' }} />
              <div>
                <Text strong style={{ fontSize: '16px' }}>自動發文</Text>
                <div>
                  <Text type="secondary">
                    {autoPostEnabled
                      ? '已開啟 - 每小時自動抓取新文章並發佈'
                      : '已關閉 - 需手動抓取和發佈文章'}
                  </Text>
                </div>
              </div>
            </Space>
          </Col>
          <Col>
            <Switch
              checked={autoPostEnabled}
              onChange={toggleAutoPost}
              loading={togglingAutoPost}
              checkedChildren="開"
              unCheckedChildren="關"
              style={{ transform: 'scale(1.3)' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 發文帳號設定 & 同步狀態 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={12}>
          <Card
            title={
              <Space>
                <UserOutlined />
                <span>指定發文帳號</span>
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
                <span>同步狀態</span>
              </Space>
            }
            size="small"
          >
            {syncState ? (
              <Space direction="vertical" size="small">
                <Text>
                  <strong>上次同步：</strong>{' '}
                  {syncState.last_sync_at ? new Date(syncState.last_sync_at).toLocaleString('zh-TW') : '從未同步'}
                </Text>
                <Text>
                  <strong>累計同步：</strong> {syncState.articles_synced_count} 篇文章
                </Text>
              </Space>
            ) : (
              <Text type="secondary">尚無同步記錄</Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* 文章列表 */}
      <Card
        title={
          <Space>
            <ReadOutlined />
            <span>文章列表</span>
          </Space>
        }
        extra={
          <Space>
            <Select
              style={{ width: 120 }}
              placeholder="篩選狀態"
              allowClear
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: 'pending', label: '待處理' },
                { value: 'posted', label: '已發佈' },
                { value: 'skipped', label: '已跳過' },
                { value: 'failed', label: '失敗' },
              ]}
            />
            <Button
              icon={<ReloadOutlined />}
              onClick={loadArticles}
              loading={loading}
            >
              重新整理
            </Button>
            <Button
              type="primary"
              icon={<SyncOutlined spin={fetchingArticles} />}
              onClick={fetchNewArticles}
              loading={fetchingArticles}
            >
              抓取新文章
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
            description="尚無文章，點擊「抓取新文章」開始"
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

      {/* 文章內容彈窗 */}
      <Modal
        title={selectedArticle?.title || '文章內容'}
        open={contentModalVisible}
        onCancel={() => setContentModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setContentModalVisible(false)}>
            關閉
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
              發佈文章
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
                  瀏覽數: {selectedArticle.total_views?.toLocaleString() || '0'}
                </Text>
              </Space>
            </div>

            {selectedArticle.stock_tags && selectedArticle.stock_tags.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <Text strong>股票標籤：</Text>
                <Space wrap style={{ marginLeft: '8px' }}>
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
              dangerouslySetInnerHTML={{ __html: selectedArticle.content || '無內容' }}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default InvestmentBlogPage;
