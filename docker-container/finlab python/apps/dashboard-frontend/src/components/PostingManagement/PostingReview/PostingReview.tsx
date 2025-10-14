import React, { useState, useEffect } from 'react';
import { Card, List, Button, Space, Tag, Typography, Row, Col, Statistic, Input, Modal, Form, Avatar, Divider, Tooltip, Spin, Select, message } from 'antd';
import { 
  EditOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  ClockCircleOutlined,
  ReloadOutlined,
  SearchOutlined,
  FilterOutlined,
  UserOutlined,
  EyeOutlined,
  FileTextOutlined,
  LinkOutlined,
  SendOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import PostingManagementAPI, { Post, PostingAPIUtils } from '../../../services/postingManagementAPI';
// import { usePostingStore, GeneratedPost } from '../../../stores/postingStore';

const { Title, Text } = Typography;
const { Search } = Input;
const { TextArea } = Input;
const { Option } = Select;

const PostingReview: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [editingItem, setEditingItem] = useState<Post | null>(null);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [form] = Form.useForm();
  
  // 使用真實API而不是全局狀態
  // const { 
  //   getAllPosts, 
  //   updatePostStatus, 
  //   updatePostContent, 
  //   clearPosts 
  // } = usePostingStore();
  
  const [posts, setPosts] = useState<Post[]>([]);

  // 載入發文數據
  const loadPosts = async () => {
    try {
      setLoading(true);
      
      // 從真實API獲取數據
      const postsData = await PostingManagementAPI.getPosts(
        0, 
        10000, 
        statusFilter === 'all' ? undefined : statusFilter
      );
      
      console.log('📊 獲取到的貼文數據:', postsData);
      
      // 檢查響應結構
      if (!postsData || !postsData.posts) {
        console.error('❌ API 響應格式錯誤:', postsData);
        message.error('API 響應格式錯誤');
        setPosts([]);
        return;
      }
      
      // 確保 posts 是陣列
      const postsArray = Array.isArray(postsData.posts) ? postsData.posts : [];
      
      setPosts(postsArray);
      message.success(`載入 ${postsArray.length} 篇貼文`);
      
    } catch (error) {
      console.error('❌ 載入發文失敗:', error);
      const errorMessage = error.response?.data?.detail || error.message || '未知錯誤';
      message.error(`載入發文失敗: ${errorMessage}`);
      
      // 如果API失敗，顯示示例數據
      const samplePosts: Post[] = [
        { 
          id: 1, 
          title: '台積電技術面強勢突破', 
          content: '台積電(2330) 從技術面來看，MACD出現黃金交叉，均線呈現多頭排列，成交量放大，技術指標顯示強勢突破信號。', 
          status: 'draft', 
          kol_nickname: '川川哥', 
          kol_serial: 200,
          stock_codes: ['2330'],
          stock_names: ['台積電'],
          created_at: '2024-01-15 15:30:00',
          updated_at: '2024-01-15 15:30:00',
          session_id: 'session_001',
          trigger_type: 'custom_stocks',
          content_length: 'medium',
          tags: ['#台積電', '#技術分析'],
          interactions: 0,
          stock_data: {},
          generation_config: {},
          technical_indicators: [],
          quality_score: 0.8,
          ai_detection_score: 0.1,
          risk_level: 'low',
          views: 0,
          likes: 0,
          comments: 0,
          shares: 0
        },
        { 
          id: 2, 
          title: '聯發科基本面分析看好', 
          content: '聯發科(2454) 從基本面分析來看，營收成長超預期，財務指標穩健，長期投資價值顯現。', 
          status: 'pending', 
          kol_nickname: '韭割哥', 
          kol_serial: 201,
          stock_codes: ['2454'],
          stock_names: ['聯發科'],
          created_at: '2024-01-15 15:45:00',
          updated_at: '2024-01-15 15:45:00',
          session_id: 'session_001',
          trigger_type: 'custom_stocks',
          content_length: 'long',
          tags: ['#聯發科', '#基本面'],
          interactions: 0,
          stock_data: {},
          generation_config: {},
          technical_indicators: [],
          quality_score: 0.7,
          ai_detection_score: 0.2,
          risk_level: 'low',
          views: 0,
          likes: 0,
          comments: 0,
          shares: 0
        }
      ];
      setPosts(samplePosts);
      message.info('使用示例數據，請確保後端服務正在運行');
    } finally {
      setLoading(false);
    }
  };

  // 刷新數據
  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPosts();
    setRefreshing(false);
  };

  // 初始載入
  useEffect(() => {
    loadPosts();
  }, [statusFilter]);

  // 過濾發文
  const filteredPosts = posts.filter(post => {
    const matchesSearch = searchText === '' || 
      (post.title && post.title.toLowerCase().includes(searchText.toLowerCase())) ||
      (post.kol_nickname && post.kol_nickname.toLowerCase().includes(searchText.toLowerCase())) ||
      (post.stock_names && Array.isArray(post.stock_names) && post.stock_names.some(name => 
        name && name.toLowerCase().includes(searchText.toLowerCase())
      ));
    
    return matchesSearch;
  });

  // 統計數據
  const stats = {
    total: posts.length,
    pending: posts.filter(p => p.status === 'pending_review').length,
    approved: posts.filter(p => p.status === 'approved').length,
    published: posts.filter(p => p.status === 'published').length,
    rejected: posts.filter(p => p.status === 'rejected').length
  };

  const handleApprove = async (postId: number) => {
    try {
      await PostingManagementAPI.approvePost(postId);
      message.success('發文已審核通過');
      await loadPosts();
    } catch (error) {
      console.error('審核失敗:', error);
      message.error('審核失敗');
    }
  };

  const handleReject = async (postId: number) => {
    try {
      await PostingManagementAPI.rejectPost(postId);
      message.success('發文已拒絕');
      await loadPosts();
    } catch (error) {
      console.error('拒絕失敗:', error);
      message.error('拒絕失敗');
    }
  };

  const handlePublish = async (postId: number) => {
    try {
      const result = await PostingManagementAPI.publishPost(postId);
      if (result.success) {
        message.success('發文發布成功');
      } else {
        message.error('發布失敗');
      }
      await loadPosts();
    } catch (error) {
      console.error('發布失敗:', error);
      message.error('發布失敗');
    }
  };

  const handleDelete = async (postId: number) => {
    Modal.confirm({
      title: '確認刪除',
      content: '確定要刪除這篇貼文嗎？此操作無法復原。',
      okText: '確認刪除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await PostingManagementAPI.deletePost(postId);
          message.success('貼文已刪除');
          await loadPosts();
        } catch (error) {
          console.error('刪除失敗:', error);
          message.error('刪除失敗');
        }
      },
    });
  };

  const handleRestore = async (postId: number) => {
    Modal.confirm({
      title: '確認還原',
      content: '確定要還原這篇貼文嗎？',
      okText: '確認還原',
      okType: 'primary',
      cancelText: '取消',
      onOk: async () => {
        try {
          await PostingManagementAPI.restorePost(postId);
          message.success('貼文已還原');
          await loadPosts();
        } catch (error) {
          console.error('還原失敗:', error);
          message.error('還原失敗');
        }
      },
    });
  };

  const handleEdit = (post: Post) => {
    setEditingItem(post);
    form.setFieldsValue({
      title: post.title,
      content: post.content
    });
    setIsEditModalVisible(true);
  };

  const handleSaveEdit = async () => {
    try {
      if (!editingItem) return;
      
      const values = await form.validateFields();
      await PostingManagementAPI.approvePost(editingItem.id, '內容已更新', 'system', values.title, values.content);
      message.success('發文更新成功');
      setIsEditModalVisible(false);
      setEditingItem(null);
      await loadPosts();
    } catch (error) {
      console.error('更新失敗:', error);
      message.error('更新失敗');
    }
  };

  const handleCancelEdit = () => {
    setIsEditModalVisible(false);
    setEditingItem(null);
    form.resetFields();
  };

  const getStatusColor = (status: string) => {
    return PostingAPIUtils.getStatusColor(status);
  };

  const getStatusText = (status: string) => {
    return PostingAPIUtils.getStatusText(status);
  };

  const getRiskColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'low': return 'green';
      case 'medium': return 'orange';
      case 'high': return 'red';
      default: return 'default';
    }
  };

  const getAIDetectionColor = (score?: number) => {
    if (!score) return 'default';
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'orange';
    return 'red';
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
          <Col>
            <Space>
              <FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <div>
                <Title level={2} style={{ margin: 0 }}>發文審核</Title>
                <Text type="secondary">審核和管理生成的發文內容</Text>
              </div>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={handleRefresh}
                loading={refreshing}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 統計卡片 */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={4}>
            <Card size="small">
              <Statistic title="總發文數" value={stats.total} />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic title="待審核" value={stats.pending} valueStyle={{ color: '#faad14' }} />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic title="已審核" value={stats.approved} valueStyle={{ color: '#52c41a' }} />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic title="已發布" value={stats.published} valueStyle={{ color: '#1890ff' }} />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic title="已拒絕" value={stats.rejected} valueStyle={{ color: '#f5222d' }} />
            </Card>
          </Col>
        </Row>

        {/* 搜尋和篩選 */}
        <Card size="small" style={{ marginBottom: '16px' }}>
          <Row gutter={16} align="middle">
            <Col span={8}>
              <Search
                placeholder="搜尋標題、KOL或股票..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ width: '100%' }}
              />
            </Col>
            <Col span={4}>
              <Select
                value={statusFilter}
                onChange={setStatusFilter}
                style={{ width: '100%' }}
              >
                <Option value="all">全部狀態</Option>
                <Option value="pending_review">待審核</Option>
                <Option value="approved">已審核</Option>
                <Option value="published">已發布</Option>
                <Option value="rejected">已拒絕</Option>
              </Select>
            </Col>
          </Row>
        </Card>

        {/* 發文列表 */}
        <Spin spinning={loading}>
          {filteredPosts.length > 0 ? (
            <List
              dataSource={filteredPosts}
              renderItem={(post, index) => {
                try {
                  // 確保 post 物件有必要的屬性
                  const safePost = {
                    id: post?.id || post?.post_id || index,
                    title: post?.title || '無標題',
                    content: post?.content || '無內容',
                    status: post?.status || 'draft',
                    kol_nickname: post?.kol_nickname || '未知KOL',
                    stock_names: Array.isArray(post?.stock_names) ? post.stock_names : [],
                    stock_codes: Array.isArray(post?.stock_codes) ? post.stock_codes : [],
                    created_at: post?.created_at || new Date().toISOString(),
                    quality_score: post?.quality_score || 0,
                    ai_detection_score: post?.ai_detection_score || 0,
                    risk_level: post?.risk_level || 'low',
                    technical_indicators: Array.isArray(post?.technical_indicators) ? post.technical_indicators : [],
                    views: post?.views || 0,
                    likes: post?.likes || 0,
                    comments: post?.comments || 0,
                    shares: post?.shares || 0,
                    ...post
                  };

                  return (
                    <List.Item
                      key={safePost.id}
                      actions={[
                      <Button
                        key="edit"
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(safePost)}
                      >
                        編輯
                      </Button>,
                      safePost.status === 'pending_review' && (
                        <Button
                          key="approve"
                          type="text"
                          icon={<CheckCircleOutlined />}
                          onClick={() => handleApprove(safePost.id)}
                          style={{ color: '#52c41a' }}
                        >
                          審核通過
                        </Button>
                      ),
                      safePost.status === 'pending_review' && (
                        <Button
                          key="reject"
                          type="text"
                          icon={<CloseCircleOutlined />}
                          onClick={() => handleReject(safePost.id)}
                          style={{ color: '#f5222d' }}
                        >
                          拒絕
                        </Button>
                      ),
                      safePost.status === 'approved' && (
                        <Button
                          key="publish"
                          type="text"
                          icon={<SendOutlined />}
                          onClick={() => handlePublish(safePost.id)}
                          style={{ color: '#1890ff' }}
                        >
                          發布
                        </Button>
                      ),
                      safePost.status === 'published' && (
                        <Button
                          key="delete"
                          type="text"
                          icon={<DeleteOutlined />}
                          onClick={() => handleDelete(safePost.id)}
                          style={{ color: '#f5222d' }}
                        >
                          刪除
                        </Button>
                      ),
                      safePost.status === 'deleted' && (
                        <Button
                          key="restore"
                          type="text"
                          icon={<CheckCircleOutlined />}
                          onClick={() => handleRestore(safePost.id)}
                          style={{ color: '#52c41a' }}
                        >
                          還原
                        </Button>
                      )
                    ].filter(Boolean)}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar 
                          icon={<UserOutlined />} 
                          style={{ backgroundColor: '#1890ff' }}
                        >
                          {safePost.kol_nickname.charAt(0)}
                        </Avatar>
                      }
                      title={
                        <Space>
                          <Text strong>{safePost.title}</Text>
                          <Tag color={getStatusColor(safePost.status)}>
                            {getStatusText(safePost.status)}
                          </Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Space wrap>
                            <Text type="secondary">KOL: {safePost.kol_nickname}</Text>
                            <Text type="secondary">|</Text>
                            <Text type="secondary">股票: {safePost.stock_names.join(', ') || '無'}</Text>
                            <Text type="secondary">|</Text>
                            <Text type="secondary">生成時間: {PostingAPIUtils.formatDate(safePost.created_at)}</Text>
                          </Space>
                          
                          <Text ellipsis={{ rows: 2 }} style={{ fontSize: '14px' }}>
                            {safePost.content}
                          </Text>
                          
                          <Space wrap>
                            {safePost.quality_score > 0 && (
                              <Tag color="blue">品質分數: {safePost.quality_score}</Tag>
                            )}
                            {safePost.ai_detection_score > 0 && (
                              <Tag color={getAIDetectionColor(safePost.ai_detection_score)}>
                                AI檢測: {(safePost.ai_detection_score * 100).toFixed(0)}%
                              </Tag>
                            )}
                            {safePost.risk_level && (
                              <Tag color={getRiskColor(safePost.risk_level)}>
                                風險等級: {safePost.risk_level}
                              </Tag>
                            )}
                            {safePost.technical_indicators.length > 0 && (
                              <Tag color="purple">
                                技術指標: {safePost.technical_indicators.join(', ')}
                              </Tag>
                            )}
                          </Space>
                          
                          {safePost.status === 'published' && (
                            <Space>
                              <Text type="secondary">互動數據:</Text>
                              <Text type="secondary">瀏覽 {safePost.views}</Text>
                              <Text type="secondary">讚 {safePost.likes}</Text>
                              <Text type="secondary">留言 {safePost.comments}</Text>
                              <Text type="secondary">分享 {safePost.shares}</Text>
                            </Space>
                          )}
                        </Space>
                      }
                    />
                  </List.Item>
                );
                } catch (error) {
                  console.error('渲染貼文項目時發生錯誤:', error, post);
                  return (
                    <List.Item key={index || 'error'}>
                      <List.Item.Meta
                        title="渲染錯誤"
                        description={`貼文 ${index + 1} 渲染失敗: ${error.message}`}
                      />
                    </List.Item>
                  );
                }
              }}
            />
          ) : (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Text type="secondary">沒有找到符合條件的貼文</Text>
            </div>
          )}
        </Spin>
      </Card>

      {/* 編輯模態框 */}
      <Modal
        title="編輯發文"
        open={isEditModalVisible}
        onOk={handleSaveEdit}
        onCancel={handleCancelEdit}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        {editingItem && (
          <div>
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={12}>
                <Text strong>KOL資訊</Text>
                <div>
                  <Text>{editingItem.kol_nickname}</Text>
                  {editingItem.kol_persona && (
                    <Tag color="blue" style={{ marginLeft: '8px' }}>
                      {editingItem.kol_persona}
                    </Tag>
                  )}
                </div>
              </Col>
              <Col span={12}>
                <Text strong>股票資訊</Text>
                <div>
                  {editingItem.stock_names.map((name, index) => (
                    <Tag key={index} color="green">
                      {editingItem.stock_codes[index]} {name}
                    </Tag>
                  ))}
                </div>
              </Col>
            </Row>
            
            <Divider />
            
            <Form form={form} layout="vertical">
              <Form.Item
                label="標題"
                name="title"
                rules={[{ required: true, message: '請輸入標題' }]}
              >
                <Input placeholder="輸入標題..." />
              </Form.Item>
              
              <Form.Item
                label="內容"
                name="content"
                rules={[{ required: true, message: '請輸入內容' }]}
              >
                <TextArea
                  rows={8}
                  placeholder="輸入內容..."
                />
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PostingReview;