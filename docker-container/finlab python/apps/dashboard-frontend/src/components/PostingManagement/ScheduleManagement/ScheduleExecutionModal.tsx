import React, { useState } from 'react';
import { Modal, Card, Tag, Space, Typography, Row, Col, Button, Spin, Empty, Divider, message, Form, Input, Alert } from 'antd';
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  EyeOutlined,
  CloseOutlined,
  EditOutlined,
  CloseCircleOutlined,
  SendOutlined,
  SwapOutlined,
  SaveOutlined,
  BranchesOutlined
} from '@ant-design/icons';
import PostingManagementAPI from '../../../services/postingManagementAPI';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

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
  const [refreshing, setRefreshing] = useState(false);

  // Edit modal state
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingPost, setEditingPost] = useState<any>(null);
  const [form] = Form.useForm();

  // Version modal state
  const [versionModalVisible, setVersionModalVisible] = useState(false);
  const [selectedPostForVersions, setSelectedPostForVersions] = useState<any>(null);
  const [alternativeVersions, setAlternativeVersions] = useState<any[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);

  // Handle post preview
  const handlePreview = (post: any) => {
    setPreviewPost(post);
    setPreviewVisible(true);
  };

  // Handle post actions
  const handleApprove = async (postId: string) => {
    try {
      await PostingManagementAPI.approvePost(postId);
      message.success('發文已審核通過');
      setRefreshing(true);
      // Optionally reload data
    } catch (error) {
      console.error('審核失敗:', error);
      message.error('審核失敗');
    }
  };

  const handleReject = async (postId: string) => {
    try {
      await PostingManagementAPI.rejectPost(postId);
      message.success('發文已拒絕');
      setRefreshing(true);
    } catch (error) {
      console.error('拒絕失敗:', error);
      message.error('拒絕失敗');
    }
  };

  const handlePublish = async (postId: string) => {
    try {
      const result = await PostingManagementAPI.publishPost(postId);
      if (result.success) {
        message.success('發文發布成功');
      } else {
        message.error('發布失敗');
      }
      setRefreshing(true);
    } catch (error) {
      console.error('發布失敗:', error);
      message.error('發布失敗');
    }
  };

  // Handle view/edit content
  const handleViewBody = (post: any) => {
    setEditingPost(post);
    form.setFieldsValue({
      title: post.title,
      content: post.content
    });
    setEditModalVisible(true);
  };

  // Handle save edited content
  const handleSaveEdit = async () => {
    try {
      const values = await form.validateFields();
      console.log('💾 保存編輯:', editingPost.post_id, values);

      // Call API to update post
      await PostingManagementAPI.updatePost(editingPost.post_id, {
        title: values.title,
        content: values.content
      });

      message.success('貼文已更新');

      // Update local state
      if (executionResult && executionResult.posts) {
        executionResult.posts = executionResult.posts.map(p =>
          p.post_id === editingPost.post_id
            ? { ...p, title: values.title, content: values.content }
            : p
        );
      }

      setEditModalVisible(false);
      setEditingPost(null);
      form.resetFields();
    } catch (error) {
      console.error('保存失敗:', error);
      message.error('保存失敗');
    }
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setEditModalVisible(false);
    setEditingPost(null);
    form.resetFields();
  };

  // Handle view versions
  const handleVersions = async (post: any) => {
    console.log('🔍 查看版本:', post);
    setSelectedPostForVersions(post);
    setVersionModalVisible(true);
    setLoadingVersions(true);

    try {
      // Fetch alternative versions from API
      const versions = await PostingManagementAPI.getPostVersions(post.post_id);
      console.log('📦 獲取到版本:', versions);
      setAlternativeVersions(versions || []);

      if (!versions || versions.length === 0) {
        message.warning('此貼文沒有其他版本可供選擇');
      }
    } catch (error) {
      console.error('獲取版本失敗:', error);
      message.error('獲取版本失敗');
      setAlternativeVersions([]);
    } finally {
      setLoadingVersions(false);
    }
  };

  // Handle select version
  const handleSelectVersion = async (version: any) => {
    console.log('🔄 選擇版本:', version);

    try {
      // Update post with selected version using updatePostContent API
      const result = await PostingManagementAPI.updatePostContent(selectedPostForVersions.post_id, {
        title: version.title,
        content: version.content
      });

      if (result.success) {
        message.success(`版本 ${version.version_number} 已套用成功`);

        // Update local state
        if (executionResult && executionResult.posts) {
          executionResult.posts = executionResult.posts.map(p =>
            p.post_id === selectedPostForVersions.post_id
              ? { ...p, title: version.title, content: version.content }
              : p
          );
        }

        setVersionModalVisible(false);
        setSelectedPostForVersions(null);
        setAlternativeVersions([]);
      } else {
        message.error(`版本更新失敗: ${result.error}`);
      }
    } catch (error) {
      console.error('版本更新失敗:', error);
      message.error('版本更新失敗');
    }
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

            {/* Header Message */}
            <div style={{ marginBottom: 16, padding: '12px', background: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: '4px' }}>
              <Text type="secondary">會一次回傳生成的貼文，請稍微耐心等候，謝謝！</Text>
            </div>

            {/* Success Message */}
            {executionResult.success && executionResult.generated_count > 0 && (
              <div style={{ marginBottom: 24, padding: '12px', background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: '4px' }}>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text>排程執行成功！已生成 {executionResult.generated_count} 篇貼文。</Text>
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
                    <div style={{ marginTop: 8, marginBottom: 12 }}>
                      <Text type="secondary" ellipsis={{ tooltip: post.content, rows: 2 }}>
                        {post.content?.substring(0, 100)}...
                      </Text>
                    </div>
                    {/* Action Buttons */}
                    <div style={{ marginTop: 12, borderTop: '1px solid #f0f0f0', paddingTop: 8 }}>
                      <Space wrap>
                        <Button
                          size="small"
                          icon={<EyeOutlined />}
                          onClick={() => handlePreview(post)}
                        >
                          預覽
                        </Button>
                        <Button
                          size="small"
                          icon={<EditOutlined />}
                          onClick={() => handleViewBody(post)}
                        >
                          查看內容
                        </Button>
                        <Button
                          size="small"
                          type="primary"
                          icon={<CheckCircleOutlined />}
                          onClick={() => handleApprove(post.post_id)}
                          style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                        >
                          審核
                        </Button>
                        <Button
                          size="small"
                          danger
                          icon={<CloseCircleOutlined />}
                          onClick={() => handleReject(post.post_id)}
                        >
                          拒絕
                        </Button>
                        <Button
                          size="small"
                          type="primary"
                          icon={<SendOutlined />}
                          onClick={() => handlePublish(post.post_id)}
                        >
                          發布
                        </Button>
                        <Button
                          size="small"
                          icon={<SwapOutlined />}
                          onClick={() => handleVersions(post)}
                        >
                          版本
                        </Button>
                      </Space>
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

      {/* Edit Content Modal */}
      <Modal
        title={`編輯貼文內容 - ${editingPost?.stock_code || '未知股票'}`}
        open={editModalVisible}
        onCancel={handleCancelEdit}
        width={900}
        footer={[
          <Button key="cancel" onClick={handleCancelEdit}>
            取消
          </Button>,
          <Button key="save" type="primary" onClick={handleSaveEdit} icon={<SaveOutlined />}>
            保存
          </Button>
        ]}
      >
        {editingPost && (
          <Form form={form} layout="vertical">
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={12}>
                <Text strong>股票代碼: </Text>
                <Text>{editingPost.stock_code}</Text>
              </Col>
              <Col span={12}>
                <Text strong>KOL: </Text>
                <Text>{editingPost.kol_serial}</Text>
              </Col>
            </Row>

            <Divider />

            <Form.Item
              label="標題"
              name="title"
              rules={[{ required: true, message: '請輸入標題' }]}
            >
              <Input
                placeholder="請輸入貼文標題"
              />
            </Form.Item>

            <Form.Item
              label="內容"
              name="content"
              rules={[{ required: true, message: '請輸入內容' }]}
            >
              <TextArea
                placeholder="請輸入貼文內容"
                rows={15}
                showCount
                maxLength={2000}
              />
            </Form.Item>

            <Alert
              message="提示"
              description="編輯後的內容將自動保存到資料庫，並更新顯示。"
              type="info"
              showIcon
              style={{ marginTop: '12px' }}
            />
          </Form>
        )}
      </Modal>

      {/* Version Viewer Modal */}
      <Modal
        title={
          <Space>
            <BranchesOutlined />
            <span>版本預覽 - {selectedPostForVersions?.stock_code || '未知股票'}</span>
          </Space>
        }
        open={versionModalVisible}
        onCancel={() => {
          setVersionModalVisible(false);
          setSelectedPostForVersions(null);
          setAlternativeVersions([]);
        }}
        width={1200}
        footer={[
          <Button key="cancel" onClick={() => {
            setVersionModalVisible(false);
            setSelectedPostForVersions(null);
            setAlternativeVersions([]);
          }}>
            關閉
          </Button>
        ]}
      >
        {loadingVersions ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">正在載入版本...</Text>
            </div>
          </div>
        ) : selectedPostForVersions && (
          <div>
            <Alert
              message="版本選擇"
              description={`當前貼文有 ${alternativeVersions.length} 個其他版本可供選擇。點擊「選擇此版本」來替換當前內容。`}
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />

            {/* Current Version */}
            <div style={{ marginBottom: '16px' }}>
              <Title level={5}>當前版本</Title>
              <Card size="small" style={{ backgroundColor: '#f0f8ff', border: '2px solid #1890ff' }}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Text strong>股票代碼: </Text>
                    <Text>{selectedPostForVersions.stock_code}</Text>
                  </Col>
                  <Col span={12}>
                    <Text strong>KOL: </Text>
                    <Text>{selectedPostForVersions.kol_serial}</Text>
                  </Col>
                </Row>
                <Divider style={{ margin: '12px 0' }} />
                <div style={{ marginBottom: '8px' }}>
                  <Text strong>標題：</Text>
                  <div style={{ marginTop: '4px', padding: '8px', backgroundColor: 'white', borderRadius: '4px' }}>
                    {selectedPostForVersions.title}
                  </div>
                </div>
                <div>
                  <Text strong>內容：</Text>
                  <div style={{
                    marginTop: '4px',
                    padding: '8px',
                    backgroundColor: 'white',
                    borderRadius: '4px',
                    fontSize: '12px',
                    maxHeight: '150px',
                    overflow: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {selectedPostForVersions.content}
                  </div>
                </div>
              </Card>
            </div>

            <Divider />

            {/* Alternative Versions */}
            <Title level={5}>其他版本 ({alternativeVersions.length} 個)</Title>

            {alternativeVersions.length === 0 ? (
              <Empty description="沒有其他版本" />
            ) : (
              <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                {alternativeVersions.map((version, index) => (
                  <Card
                    key={index}
                    size="small"
                    style={{ marginBottom: '12px' }}
                    title={
                      <Space>
                        <BranchesOutlined />
                        <span>版本 {version.version_number || index + 2}</span>
                        {version.angle && <Tag color="blue">{version.angle}</Tag>}
                      </Space>
                    }
                    extra={
                      <Button
                        type="primary"
                        size="small"
                        onClick={() => handleSelectVersion(version)}
                      >
                        選擇此版本
                      </Button>
                    }
                  >
                    <div style={{ marginBottom: '8px' }}>
                      <Text strong>標題：</Text>
                      <div style={{ marginTop: '4px', padding: '6px', backgroundColor: '#fafafa', borderRadius: '4px', fontSize: '13px' }}>
                        {version.title}
                      </div>
                    </div>
                    <div>
                      <Text strong>內容：</Text>
                      <div style={{
                        marginTop: '4px',
                        padding: '6px',
                        backgroundColor: '#fafafa',
                        borderRadius: '4px',
                        fontSize: '12px',
                        maxHeight: '120px',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {version.content}
                      </div>
                    </div>

                    {version.quality_score && (
                      <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #f0f0f0' }}>
                        <Space size="large">
                          <div>
                            <Text type="secondary" style={{ fontSize: '12px' }}>品質分數: </Text>
                            <Text strong style={{ fontSize: '12px' }}>{version.quality_score}</Text>
                          </div>
                          {version.ai_detection_score && (
                            <div>
                              <Text type="secondary" style={{ fontSize: '12px' }}>AI檢測: </Text>
                              <Text strong style={{ fontSize: '12px' }}>{version.ai_detection_score}</Text>
                            </div>
                          )}
                        </Space>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>
    </>
  );
};

export default ScheduleExecutionModal;
