import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Badge, 
  Tag, 
  Space, 
  Typography, 
  Button, 
  Tooltip,
  Spin,
  Empty,
  Divider,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  SendOutlined,
  FileTextOutlined,
  EyeOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import PostingManagementAPI from '../../services/postingManagementAPI';
import { Post } from '../../types/posting';

const { Title, Text } = Typography;

interface ReviewSidebarProps {
  onPostClick?: (post: Post) => void;
  onSessionClick?: (sessionId: number) => void;
  refreshTrigger?: number;
}

interface SessionData {
  session_id: number;
  posts_count: number;
  latest_post: string;
  kol_personas: string[];
  stock_codes: string[];
  posts: Post[];
}

interface SidebarData {
  stats: {
    total_pending: number;
    sessions_count: number;
    latest_session: number | null;
    oldest_pending: string | null;
  };
  sidebar_data: {
    sessions: SessionData[];
  };
}

const ReviewSidebar: React.FC<ReviewSidebarProps> = ({ 
  onPostClick, 
  onSessionClick, 
  refreshTrigger 
}) => {
  const [sidebarData, setSidebarData] = useState<SidebarData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 載入 sidebar 數據
  const loadSidebarData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await PostingManagementAPI.getReviewSidebarData();
      setSidebarData(data);
      
      console.log('✅ 審核 sidebar 數據載入成功:', data);
    } catch (err) {
      console.error('❌ 載入審核 sidebar 數據失敗:', err);
      setError('載入數據失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSidebarData();
  }, [refreshTrigger]);

  // 定時刷新
  useEffect(() => {
    const interval = setInterval(() => {
      // 只在頁面可見時才進行輪詢
      if (!document.hidden) {
        loadSidebarData();
      }
    }, 60000); // 每60秒刷新一次（減少數據庫負載）
    
    return () => clearInterval(interval);
  }, []);

  // 狀態標籤
  const getStatusTag = (status: string) => {
    const statusConfig = {
      'pending_review': { color: 'orange', text: '待審核', icon: <ClockCircleOutlined /> },
      'approved': { color: 'green', text: '已審核', icon: <CheckCircleOutlined /> },
      'rejected': { color: 'red', text: '已拒絕', icon: <ClockCircleOutlined /> },
      'published': { color: 'blue', text: '已發布', icon: <SendOutlined /> },
      'failed': { color: 'red', text: '發布失敗', icon: <ClockCircleOutlined /> }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending_review;
    return (
      <Tag color={config.color} icon={config.icon} size="small">
        {config.text}
      </Tag>
    );
  };

  // 格式化時間
  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString('zh-TW', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && !sidebarData) {
    return (
      <Card title="📝 發文審核" size="small" style={{ height: '100%' }}>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin />
          <div style={{ marginTop: '10px' }}>載入中...</div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="📝 發文審核" size="small" style={{ height: '100%' }}>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Text type="danger">{error}</Text>
          <br />
          <Button 
            type="link" 
            icon={<ReloadOutlined />} 
            onClick={loadSidebarData}
            style={{ marginTop: '10px' }}
          >
            重新載入
          </Button>
        </div>
      </Card>
    );
  }

  if (!sidebarData || sidebarData.sidebar_data.sessions.length === 0) {
    return (
      <Card title="📝 發文審核" size="small" style={{ height: '100%' }}>
        <Empty 
          description="暫無待審核貼文"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  return (
    <Card 
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📝 發文審核</span>
          <Button 
            type="text" 
            icon={<ReloadOutlined />} 
            onClick={loadSidebarData}
            loading={loading}
            size="small"
          />
        </div>
      } 
      size="small" 
      style={{ height: '100%' }}
    >
      {/* 統計數據 */}
      <Row gutter={8} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Statistic 
            title="待審核" 
            value={sidebarData.stats.total_pending} 
            valueStyle={{ color: '#fa8c16', fontSize: '16px' }}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col span={12}>
          <Statistic 
            title="會話數" 
            value={sidebarData.stats.sessions_count} 
            valueStyle={{ color: '#1890ff', fontSize: '16px' }}
            prefix={<FileTextOutlined />}
          />
        </Col>
      </Row>

      <Divider style={{ margin: '12px 0' }} />

      {/* Session 列表 */}
      <List
        size="small"
        dataSource={sidebarData.sidebar_data.sessions}
        renderItem={(session) => (
          <List.Item
            style={{ 
              padding: '8px 0',
              borderBottom: '1px solid #f0f0f0',
              cursor: 'pointer'
            }}
            onClick={() => onSessionClick?.(session.session_id)}
          >
            <div style={{ width: '100%' }}>
              {/* Session 標題 */}
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '4px'
              }}>
                <Text strong style={{ fontSize: '12px' }}>
                  Session: {session.session_id}
                </Text>
                <Badge count={session.posts_count} size="small" />
              </div>

              {/* Session 資訊 */}
              <div style={{ marginBottom: '6px' }}>
                <Space size="small" wrap>
                  {session.kol_personas.slice(0, 2).map(persona => (
                    <Tag key={persona} size="small" color="blue">
                      {persona}
                    </Tag>
                  ))}
                  {session.kol_personas.length > 2 && (
                    <Tag size="small" color="default">
                      +{session.kol_personas.length - 2}
                    </Tag>
                  )}
                </Space>
              </div>

              {/* 股票代碼 */}
              <div style={{ marginBottom: '6px' }}>
                <Text type="secondary" style={{ fontSize: '11px' }}>
                  股票: {session.stock_codes.slice(0, 3).join(', ')}
                  {session.stock_codes.length > 3 && '...'}
                </Text>
              </div>

              {/* 最新貼文時間 */}
              <div style={{ fontSize: '10px', color: '#999' }}>
                {formatTime(session.latest_post)}
              </div>

              {/* 貼文預覽 */}
              <div style={{ marginTop: '6px' }}>
                {session.posts.slice(0, 2).map((post, index) => (
                  <div 
                    key={post.id} 
                    style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '2px 0',
                      fontSize: '11px'
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onPostClick?.(post);
                    }}
                  >
                    <div style={{ flex: 1, overflow: 'hidden' }}>
                      <Text ellipsis style={{ fontSize: '11px' }}>
                        {post.stock_names[0]}({post.stock_codes[0]})
                      </Text>
                    </div>
                    <div>
                      {getStatusTag(post.status)}
                    </div>
                  </div>
                ))}
                {session.posts.length > 2 && (
                  <Text type="secondary" style={{ fontSize: '10px' }}>
                    ...還有 {session.posts.length - 2} 篇貼文
                  </Text>
                )}
              </div>
            </div>
          </List.Item>
        )}
      />
    </Card>
  );
};

export default ReviewSidebar;
