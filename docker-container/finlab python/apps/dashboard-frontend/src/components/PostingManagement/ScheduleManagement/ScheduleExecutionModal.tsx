import React, { useState } from 'react';
import { Modal, Card, Tag, Space, Typography, Row, Col, Button, Spin, Empty, Divider } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined, EyeOutlined, CloseOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface ExecutionResult {
  success: boolean;
  message?: string;
  task_id: string;
  session_id: number;
  schedule_name: string;
  generated_count: number;
  failed_count: number;
  posts: Array<{
    post_id: string;
    stock_code: string;
    kol_serial: number;
    title: string;
    content: string;
  }>;
  errors: Array<{
    stock_code: string;
    error: string;
  }>;
  timestamp: string;
}

interface ScheduleExecutionModalProps {
  visible: boolean;
  executionResult: ExecutionResult | null;
  loading: boolean;
  onClose: () => void;
}

const ScheduleExecutionModal: React.FC<ScheduleExecutionModalProps> = ({
  visible,
  executionResult,
  loading,
  onClose
}) => {
  const [previewPost, setPreviewPost] = useState<any>(null);
  const [previewVisible, setPreviewVisible] = useState(false);

  // Handle post preview
  const handlePreview = (post: any) => {
    setPreviewPost(post);
    setPreviewVisible(true);
  };

  return (
    <>
      <Modal
        title={
          <Space>
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
            <span>排程執行結果</span>
          </Space>
        }
        open={visible}
        onCancel={onClose}
        width={900}
        footer={[
          <Button key="close" type="primary" onClick={onClose}>
            關閉
          </Button>
        ]}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">正在執行排程，生成貼文中...</Text>
            </div>
          </div>
        ) : executionResult ? (
          <div>
            {/* Summary Section */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Card size="small">
                  <Text type="secondary">排程名稱</Text>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', marginTop: 8 }}>
                    {executionResult.schedule_name}
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Text type="secondary">成功生成</Text>
                  <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#52c41a', marginTop: 8 }}>
                    {executionResult.generated_count} 篇
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Text type="secondary">失敗</Text>
                  <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ff4d4f', marginTop: 8 }}>
                    {executionResult.failed_count} 篇
                  </div>
                </Card>
              </Col>
            </Row>

            {/* Success Message */}
            {executionResult.success && executionResult.generated_count > 0 && (
              <div style={{ marginBottom: 24, padding: '12px', background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: '4px' }}>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>排程執行成功！已生成 {executionResult.generated_count} 篇貼文，請前往「發文審核」頁面查看。</Text>
                </Space>
              </div>
            )}

            <Divider>生成的貼文</Divider>

            {/* Posts List */}
            {executionResult.posts && executionResult.posts.length > 0 ? (
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {executionResult.posts.map((post, index) => (
                  <Card
                    key={post.post_id}
                    size="small"
                    style={{ marginBottom: 12 }}
                    extra={
                      <Button
                        type="link"
                        icon={<EyeOutlined />}
                        onClick={() => handlePreview(post)}
                      >
                        預覽
                      </Button>
                    }
                  >
                    <Row gutter={16}>
                      <Col span={4}>
                        <Tag color="blue">{post.stock_code}</Tag>
                      </Col>
                      <Col span={4}>
                        <Tag color="green">KOL-{post.kol_serial}</Tag>
                      </Col>
                      <Col span={16}>
                        <Text strong ellipsis={{ tooltip: post.title }}>
                          {post.title || '未命名貼文'}
                        </Text>
                      </Col>
                    </Row>
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" ellipsis={{ tooltip: post.content, rows: 2 }}>
                        {post.content?.substring(0, 100)}...
                      </Text>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <Empty description="沒有生成任何貼文" />
            )}

            {/* Errors Section */}
            {executionResult.errors && executionResult.errors.length > 0 && (
              <>
                <Divider>錯誤記錄</Divider>
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {executionResult.errors.map((error, index) => (
                    <div
                      key={index}
                      style={{
                        padding: '8px 12px',
                        marginBottom: 8,
                        background: '#fff2f0',
                        border: '1px solid #ffccc7',
                        borderRadius: '4px'
                      }}
                    >
                      <Space>
                        <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
                        <Text strong>{error.stock_code}</Text>
                        <Text type="danger">{error.error}</Text>
                      </Space>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Metadata */}
            <div style={{ marginTop: 24, padding: '12px', background: '#fafafa', borderRadius: '4px' }}>
              <Space direction="vertical" size={4}>
                <Text type="secondary">Session ID: {executionResult.session_id}</Text>
                <Text type="secondary">執行時間: {new Date(executionResult.timestamp).toLocaleString('zh-TW')}</Text>
              </Space>
            </div>
          </div>
        ) : (
          <Empty description="無執行結果" />
        )}
      </Modal>

      {/* Post Preview Modal */}
      <Modal
        title="貼文預覽"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        width={700}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            關閉
          </Button>
        ]}
      >
        {previewPost && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Text strong>股票代碼: </Text>
                <Tag color="blue">{previewPost.stock_code}</Tag>
              </Col>
              <Col span={12}>
                <Text strong>KOL: </Text>
                <Tag color="green">KOL-{previewPost.kol_serial}</Tag>
              </Col>
            </Row>

            <Divider />

            <div style={{ marginBottom: 16 }}>
              <Title level={5}>標題</Title>
              <Paragraph>{previewPost.title}</Paragraph>
            </div>

            <div>
              <Title level={5}>內容</Title>
              <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                {previewPost.content}
              </Paragraph>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
};

export default ScheduleExecutionModal;
