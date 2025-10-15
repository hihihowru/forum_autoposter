import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Row, Col, Table, Tag, Statistic, Space, Button, Typography, Descriptions, Divider, Alert, Modal, message } from 'antd';
import { 
  ArrowLeftOutlined,
  LikeOutlined, 
  MessageOutlined, 
  EyeOutlined,
  LinkOutlined,
  CalendarOutlined,
  UserOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { Column } from '@ant-design/charts';

const { Title, Text, Paragraph } = Typography;

interface PostDetailData {
  post_id: string;
  kol_serial: string;
  kol_nickname: string;
  kol_id: string;
  persona: string;
  content_type: string;
  topic_id: string;
  topic_title: string;
  content: string;
  status: string;
  post_time: string;
  platform_post_id: string;
  platform_post_url: string;
  post_type: string;
  content_length: string;
  kol_weight_settings: string;
  content_generation_time: string;
  kol_settings_version: string;
  // 互動數據
  likes_count?: number;
  comments_count?: number;
  total_interactions?: number;
  engagement_rate?: number;
  // 詳細表情數據
  dislikes?: number;
  laughs?: number;
  money?: number;
  shock?: number;
  cry?: number;
  think?: number;
  angry?: number;
  total_emojis?: number;
  collections?: number;
  donations?: number;
}

const PostDetail: React.FC = () => {
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
  const [postData, setPostData] = useState<PostDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchPostDetail = async () => {
      try {
        setLoading(true);
        // 從 content management API 獲取貼文數據
        const response = await fetch('/api/dashboard/content-management');
        const data = await response.json();
        
        // 找到對應的貼文
        const post = data.post_list?.find((p: PostDetailData) => p.post_id === postId);
        
        if (post) {
          // 嘗試從互動分析 API 獲取互動數據
          try {
            const interactionResponse = await fetch('/api/dashboard/interaction-analysis');
            const interactionData = await interactionResponse.json() as {
              interaction_data?: Record<string, Array<{
                article_id: string;
                likes_count: number;
                comments_count: number;
                total_interactions: number;
                engagement_rate: number;
              }>>;
            };
            
            // 在所有時間週期中查找該貼文的互動數據
            const allInteractions = Object.values(interactionData.interaction_data || {}).flat();
            const interaction = allInteractions.find(i => i.article_id === (post as PostDetailData).platform_post_id);
            
            if (interaction) {
              setPostData(prev => ({
                ...prev!,
                likes_count: interaction.likes_count,
                comments_count: interaction.comments_count,
                total_interactions: interaction.total_interactions,
                engagement_rate: interaction.engagement_rate
              }));
            }
          } catch (e) {
            console.warn('無法獲取互動數據:', e);
          }
          
          setPostData(post);
        } else {
          setError('找不到該貼文');
        }
      } catch (e) {
        setError('載入貼文詳情失敗');
      } finally {
        setLoading(false);
      }
    };

    if (postId) {
      fetchPostDetail();
    }
  }, [postId]);

  // 刪除貼文函數
  const handleDeletePost = async () => {
    if (!postData) return;
    
    try {
      setDeleting(true);
      
      // 調用刪除API
      const response = await fetch(`/api/dashboard/posts/${postData.post_id}/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        message.success('貼文已成功刪除');
        setDeleteModalVisible(false);
        // 返回貼文管理頁面
        navigate('/content-management');
      } else {
        const errorData = await response.json();
        message.error(errorData.message || '刪除貼文失敗');
      }
    } catch (error) {
      console.error('刪除貼文錯誤:', error);
      message.error('刪除貼文時發生錯誤');
    } finally {
      setDeleting(false);
    }
  };

  // 顯示刪除確認對話框
  const showDeleteModal = () => {
    setDeleteModalVisible(true);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div>載入貼文詳情中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="載入失敗"
        description={error}
        type="error"
        showIcon
        style={{ margin: '16px' }}
      />
    );
  }

  if (!postData) {
    return (
      <Alert
        message="無數據"
        description="找不到該貼文"
        type="info"
        showIcon
        style={{ margin: '16px' }}
      />
    );
  }

  // 表情數據圖表配置
  const emojiData = [
    { type: '讚', value: postData.likes_count || 0, color: '#1890ff' },
    { type: '倒讚', value: postData.dislikes || 0, color: '#f5222d' },
    { type: '笑', value: postData.laughs || 0, color: '#faad14' },
    { type: '錢', value: postData.money || 0, color: '#52c41a' },
    { type: '震驚', value: postData.shock || 0, color: '#722ed1' },
    { type: '哭', value: postData.cry || 0, color: '#13c2c2' },
    { type: '思考', value: postData.think || 0, color: '#eb2f96' },
    { type: '生氣', value: postData.angry || 0, color: '#fa541c' },
  ].filter(item => item.value > 0);

  const emojiConfig = {
    data: emojiData,
    xField: 'type',
    yField: 'value',
    color: '#1890ff',
    meta: {
      type: { alias: '表情類型' },
      value: { alias: '數量' },
    },
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 返回按鈕和操作按鈕 */}
      <Row style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/content-management')}
          >
            返回貼文管理
          </Button>
        </Col>
        <Col span={12} style={{ textAlign: 'right' }}>
          <Space>
            <Button 
              icon={<EditOutlined />}
              onClick={() => message.info('編輯功能開發中')}
            >
              編輯
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={() => message.info('重新生成功能開發中')}
            >
              重新生成
            </Button>
            <Button 
              type="primary"
              danger
              icon={<DeleteOutlined />}
              onClick={showDeleteModal}
              disabled={postData?.status === '已刪除' || postData?.status !== '已發布' || !postData?.platform_post_id}
            >
              刪除貼文
            </Button>
          </Space>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 貼文基本資訊 */}
        <Col span={24}>
          <Card title="貼文基本資訊" size="small">
            <Descriptions column={2} size="small">
              <Descriptions.Item label="貼文 ID">{postData.post_id}</Descriptions.Item>
              <Descriptions.Item label="KOL">{postData.kol_nickname}</Descriptions.Item>
              <Descriptions.Item label="人設">
                <Tag color="blue">{postData.persona}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="狀態">
                <Tag color={postData.status === '已發布' ? 'green' : 'orange'}>
                  {postData.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="發文時間">
                {postData.post_time ? new Date(postData.post_time).toLocaleString('zh-TW') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="平台狀態">
                {postData.platform_post_id ? (
                  <Tag color="green" icon={<LinkOutlined />}>
                    已發布到CMoney
                  </Tag>
                ) : (
                  <Tag color="orange">未發布</Tag>
                )}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* CMoney平台資訊 */}
        {postData.platform_post_id && (
          <Col span={24}>
            <Card title="CMoney平台資訊" size="small">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <div style={{ marginBottom: '12px' }}>
                    <Text strong>文章 ID:</Text>
                    <div style={{ marginTop: '4px' }}>
                      <Text code style={{ fontSize: '16px', backgroundColor: '#f5f5f5', padding: '4px 8px', borderRadius: '4px' }}>
                        {postData.platform_post_id}
                      </Text>
                    </div>
                  </div>
                </Col>
                <Col span={12}>
                  <div style={{ marginBottom: '12px' }}>
                    <Text strong>文章連結:</Text>
                    <div style={{ marginTop: '4px' }}>
                      {postData.platform_post_url ? (
                        <Button
                          type="primary"
                          icon={<LinkOutlined />}
                          onClick={() => window.open(postData.platform_post_url, '_blank')}
                          style={{ width: '100%' }}
                        >
                          查看CMoney文章
                        </Button>
                      ) : (
                        <Text type="secondary">無連結</Text>
                      )}
                    </div>
                  </div>
                </Col>
              </Row>
              {postData.platform_post_url && (
                <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    <LinkOutlined style={{ marginRight: '4px' }} />
                    {postData.platform_post_url}
                  </Text>
                </div>
              )}
            </Card>
          </Col>
        )}

        {/* 話題資訊 */}
        <Col span={24}>
          <Card title="話題資訊" size="small">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="話題 ID">{postData.topic_id}</Descriptions.Item>
              <Descriptions.Item label="話題標題">
                <Text strong>{postData.topic_title}</Text>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 內容 */}
        <Col span={24}>
          <Card title="貼文內容" size="small">
            <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
              {postData.content}
            </Paragraph>
            <Divider />
            <Row gutter={16}>
              <Col span={8}>
                <Text type="secondary">內容類型: </Text>
                <Tag color="purple">{postData.content_type}</Tag>
              </Col>
              <Col span={8}>
                <Text type="secondary">發文類型: </Text>
                <Tag color="blue">{postData.post_type || '-'}</Tag>
              </Col>
              <Col span={8}>
                <Text type="secondary">內容長度: </Text>
                <Text>{postData.content_length || '-'}</Text>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 互動統計 */}
        <Col span={24}>
          <Card title="互動統計" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="總互動數"
                  value={postData.total_interactions || 0}
                  prefix={<EyeOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="讚數"
                  value={postData.likes_count || 0}
                  prefix={<LikeOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="留言數"
                  value={postData.comments_count || 0}
                  prefix={<MessageOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="互動率"
                  value={postData.engagement_rate ? (postData.engagement_rate * 100).toFixed(2) : 0}
                  suffix="%"
                />
              </Col>
            </Row>
            
            {/* 其他互動數據 */}
            <Row gutter={16} style={{ marginTop: '16px' }}>
              <Col span={6}>
                <Statistic
                  title="收藏數"
                  value={postData.collections || 0}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="打賞數"
                  value={postData.donations || 0}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="表情總數"
                  value={postData.total_emojis || 0}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="內容生成時間"
                  value={postData.content_generation_time || '-'}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 表情分析圖表 */}
        {emojiData.length > 0 && (
          <Col span={24}>
            <Card title="表情分析" size="small">
              <Column {...emojiConfig} height={300} />
            </Card>
          </Col>
        )}

        {/* KOL 設定 */}
        <Col span={24}>
          <Card title="KOL 設定" size="small">
            <Descriptions column={2} size="small">
              <Descriptions.Item label="KOL 序號">{postData.kol_serial}</Descriptions.Item>
              <Descriptions.Item label="Member ID">{postData.kol_id}</Descriptions.Item>
              <Descriptions.Item label="設定版本">{postData.kol_settings_version || '-'}</Descriptions.Item>
              <Descriptions.Item label="權重設定">
                {postData.kol_weight_settings ? (
                  <Button type="link" size="small">
                    查看設定
                  </Button>
                ) : '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* 刪除確認對話框 */}
      <Modal
        title="確認刪除貼文"
        open={deleteModalVisible}
        onOk={handleDeletePost}
        onCancel={() => setDeleteModalVisible(false)}
        confirmLoading={deleting}
        okText="確認刪除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <p>您確定要刪除這篇貼文嗎？</p>
        <p><strong>貼文 ID:</strong> {postData?.post_id}</p>
        <p><strong>KOL:</strong> {postData?.kol_nickname}</p>
        <p><strong>話題標題:</strong> {postData?.topic_title}</p>
        <Alert
          message="警告"
          description="此操作將從CMoney平台實際刪除貼文，並在我們的系統中標記為已刪除。此操作不可逆轉！"
          type="warning"
          showIcon
          style={{ marginTop: '16px' }}
        />
      </Modal>
    </div>
  );
};

export default PostDetail;


