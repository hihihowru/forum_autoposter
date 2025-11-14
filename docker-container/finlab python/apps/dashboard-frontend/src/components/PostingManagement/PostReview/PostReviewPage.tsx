import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Input,
  Form,
  Alert
} from 'antd';
import {
  CheckOutlined,
  CloseOutlined,
  SendOutlined,
  EyeOutlined,
  EditOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined,
  SaveOutlined,
  CancelOutlined,
  DeleteOutlined,
  BranchesOutlined,
  FireOutlined
} from '@ant-design/icons';
import PostingManagementAPI from '../../../services/postingManagementAPI';
import { Post } from '../../../types/posting';

const { Title, Text, Paragraph } = Typography;
const { Column } = Table;
const { TextArea } = Input;

interface PostReviewPageProps {
  sessionId?: number;
  onBack?: () => void;
}

const PostReviewPage: React.FC<PostReviewPageProps> = ({ sessionId, onBack }) => {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [publishing, setPublishing] = useState<Set<string>>(new Set());
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [bodyMessageVisible, setBodyMessageVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingPost, setEditingPost] = useState<Post | null>(null);
  const [form] = Form.useForm();
  const [error, setError] = useState<string | null>(null);
  
  // 版本預覽相關狀態
  const [versionModalVisible, setVersionModalVisible] = useState(false);
  const [selectedPostForVersions, setSelectedPostForVersions] = useState<Post | null>(null);
  const [alternativeVersions, setAlternativeVersions] = useState<any[]>([]);

  // 錯誤處理
  const handleError = (error: any) => {
    console.error('PostReviewPage 錯誤:', error);
    setError(error.message || '發生未知錯誤');
  };

  // 如果發生錯誤，顯示錯誤頁面
  if (error) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Alert
          message="頁面載入失敗"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => window.location.reload()}>
              重新載入
            </Button>
          }
        />
      </div>
    );
  }

  // 載入待審核貼文
  const loadPosts = async () => {
    try {
      setLoading(true);
      setError(null); // 清除之前的錯誤
      console.log('🔍 開始載入貼文, sessionId:', sessionId);
      
      let response;
      
      if (sessionId) {
        // 載入特定session的貼文（包含所有狀態）
        console.log('📡 調用 getSessionPosts API...');
        // 不指定狀態，獲取該session的所有貼文
        response = await PostingManagementAPI.getSessionPosts(sessionId);
        console.log('✅ getSessionPosts 響應:', response);
      } else {
        // 載入所有貼文（包含所有狀態）
        console.log('📡 調用 getPosts API...');
        response = await PostingManagementAPI.getPosts(0, 5000);
        console.log('✅ getPosts 響應:', response);
      }
      
      const posts = response?.posts || [];
      console.log('📊 設置貼文數據:', posts.length, '篇貼文');
      console.log('📋 貼文詳情:', posts);
      
      // 檢查 alternative_versions 數據
      posts.forEach((post: any, index: number) => {
        console.log(`🔍 貼文 ${index + 1} alternative_versions:`, post.alternative_versions);
        console.log(`🔍 貼文 ${index + 1} alternative_versions 類型:`, typeof post.alternative_versions);
        
        // 嘗試解析 JSON 字符串
        let parsedVersions = post.alternative_versions;
        if (typeof post.alternative_versions === 'string') {
          try {
            parsedVersions = JSON.parse(post.alternative_versions);
            console.log(`✅ 貼文 ${index + 1} alternative_versions 解析成功:`, parsedVersions);
          } catch (e) {
            console.log(`❌ 貼文 ${index + 1} alternative_versions JSON 解析失敗:`, e);
            parsedVersions = [];
          }
        }
        
        if (parsedVersions && Array.isArray(parsedVersions)) {
          console.log(`✅ 貼文 ${index + 1} 有 ${parsedVersions.length} 個 alternative_versions`);
          // 更新 post 對象中的 alternative_versions
          post.alternative_versions = parsedVersions;
        } else {
          console.log(`❌ 貼文 ${index + 1} 沒有 alternative_versions 或不是數組`);
          post.alternative_versions = [];
        }
      });
      
      // 確保每個貼文都有必要的字段
      const safePosts = posts.map((post: any) => {
        try {
          return {
            ...post,
            id: post.id || post.post_id || 'unknown',
            stock_codes: post.stock_codes || [],
            stock_names: post.stock_names || [],
            technical_indicators: post.technical_indicators || [],
            commodity_tags: post.commodity_tags || [],
            generation_config: post.generation_config || {},
            stock_data: post.stock_data || {},
            views: post.views || 0,
            likes: post.likes || 0,
            comments: post.comments || 0,
            shares: post.shares || 0
          };
        } catch (postError) {
          console.error('❌ 處理貼文數據失敗:', postError, post);
          return null;
        }
      }).filter(Boolean);
      
      console.log('✅ 安全處理後的貼文:', safePosts);
      setPosts(safePosts);
    } catch (error) {
      console.error('❌ 載入貼文失敗:', error);
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  // 載入 sidebar 數據
  const loadSidebarData = async () => {
    try {
      const sidebarData = await PostingManagementAPI.getReviewSidebarData();
      console.log('✅ Sidebar 數據載入成功:', sidebarData);
      return sidebarData;
    } catch (error) {
      console.error('❌ 載入 sidebar 數據失敗:', error);
      return null;
    }
  };

  useEffect(() => {
    loadPosts();

    // 設置定時刷新，快速輪詢以立即顯示新生成的貼文
    // 只在頁面可見時才進行輪詢
    const interval = setInterval(() => {
      if (!document.hidden) {
        console.log('🔄 定時刷新貼文列表');
        loadPosts();
      }
    }, 5000); // 5秒輪詢，確保貼文生成後立即顯示

    return () => clearInterval(interval);
  }, [sessionId]);

  // 審核通過
  const handleApprove = async (postId: string, editedTitle?: string, editedContent?: string) => {
    try {
      const response = await PostingManagementAPI.approvePost(postId, '審核通過', 'system', editedTitle, editedContent);
      message.success('貼文審核通過');
      
      // 審核通過後不自動發文，繼續審核下一則
      loadPosts(); // 重新載入
    } catch (error) {
      console.error('審核失敗:', error);
      message.error('審核失敗');
    }
  };

  // 審核拒絕
  const handleReject = async (postId: string, reason: string) => {
    try {
      await PostingManagementAPI.rejectPost(postId, reason);
      message.success('貼文已拒絕');
      loadPosts(); // 重新載入
    } catch (error) {
      console.error('拒絕失敗:', error);
      message.error('拒絕失敗');
    }
  };

  // 發布到CMoney
  const handlePublish = async (post: Post) => {
    try {
      setPublishing(prev => new Set(prev).add(post.id.toString()));
      
      // 調用CMoney發布API
      const response = await PostingManagementAPI.publishToCMoney(post.id.toString());
      
      if (response.success) {
        message.success(`✅ ${post.stock_names && post.stock_names[0] ? post.stock_names[0] : '未知股票'}(${post.stock_codes && post.stock_codes[0] ? post.stock_codes[0] : '未知代碼'}) 發布成功！`);
        message.info(`文章ID: ${response.article_id}`);
        
        // 發佈成功後留在當前頁面繼續審核
        loadPosts(); // 重新載入，更新貼文狀態
        
        // 可選：顯示成功提示，但不跳轉
        // navigate(`/posting-management/publish-success?sessionId=${post.session_id}`);
      } else {
        message.error(`發布失敗: ${response.error}`);
      }
    } catch (error) {
      console.error('發布失敗:', error);
      message.error('發布失敗');
    } finally {
      setPublishing(prev => {
        const newSet = new Set(prev);
        newSet.delete(post.id.toString());
        return newSet;
      });
    }
  };

  // 預覽貼文
  const handlePreview = (post: Post) => {
    setSelectedPost(post);
    setPreviewVisible(true);
  };

  // 查看 Body Message
  const handleViewBodyMessage = (post: Post) => {
    setSelectedPost(post);
    setBodyMessageVisible(true);
  };

  // 打開編輯Modal
  const handleEditPost = (post: Post) => {
    setEditingPost(post);
    setEditModalVisible(true);
    form.setFieldsValue({
      title: post.title,
      content: post.content
    });
  };

  // 保存編輯 (只更新內容，不改變狀態)
  const handleSaveEdit = async () => {
    if (!editingPost) return;

    try {
      // 獲取表單值
      const formValues = form.getFieldsValue();
      const { title, content } = formValues;

      console.log('🔄 保存編輯:', { title, content });

      // 使用 updatePostContent API - 只更新內容，不改變狀態
      const result = await PostingManagementAPI.updatePostContent(
        editingPost.id.toString(),
        { title, content }
      );

      if (result.success) {
        message.success('貼文已保存');
        setEditModalVisible(false);
        setEditingPost(null);
        form.resetFields();
        loadPosts(); // 重新載入以顯示更新
      } else {
        message.error(result.error || '保存失敗');
      }
    } catch (error) {
      console.error('保存編輯失敗:', error);
      message.error('保存編輯失敗');
    }
  };

  const handleCancelEdit = () => {
    setEditModalVisible(false);
    setEditingPost(null);
    form.resetFields();
  };

  // 處理版本預覽
  const handleVersionPreview = (post: Post) => {
    console.log('🔍 處理版本預覽:', post);
    
    // 檢查是否有 alternative_versions
    if (post.alternative_versions && Array.isArray(post.alternative_versions)) {
      setAlternativeVersions(post.alternative_versions);
      setSelectedPostForVersions(post);
      setVersionModalVisible(true);
    } else {
      message.warning('此貼文沒有其他版本可供選擇');
    }
  };

  // 選擇版本並更新
  const handleSelectVersion = async (selectedVersion: any) => {
    if (!selectedPostForVersions) return;
    
    try {
      console.log('🔄 選擇版本:', selectedVersion);
      
      // 調用 API 更新貼文內容
      const response = await PostingManagementAPI.updatePostContent(
        selectedPostForVersions.id.toString(),
        {
          title: selectedVersion.title,
          content: selectedVersion.content,
          content_md: selectedVersion.content
        }
      );
      
      if (response.success) {
        message.success('版本已更新成功');
        setVersionModalVisible(false);
        setSelectedPostForVersions(null);
        setAlternativeVersions([]);
        loadPosts(); // 重新載入貼文列表
      } else {
        message.error('版本更新失敗');
      }
    } catch (error) {
      console.error('版本更新失敗:', error);
      message.error('版本更新失敗');
    }
  };

  // 刪除貼文
  const handleDelete = async (post: Post) => {
    try {
      // 檢查post.id是否存在
      if (!post.id) {
        console.error('❌ 貼文ID不存在:', post);
        message.error('無法刪除：貼文ID不存在');
        return;
      }
      
      console.log('🗑️ 準備刪除貼文:', {
        id: post.id,
        title: post.title,
        stock_names: post.stock_names,
        stock_codes: post.stock_codes
      });
      
      const response = await PostingManagementAPI.deleteFromCMoney(post.id);
      
      if (response.success) {
        message.success(`✅ ${post.stock_names && post.stock_names[0] ? post.stock_names[0] : '未知股票'}(${post.stock_codes && post.stock_codes[0] ? post.stock_codes[0] : '未知代碼'}) 刪除成功！`);
        loadPosts(); // 重新載入
      } else {
        message.error(`刪除失敗: ${response.error}`);
      }
    } catch (error) {
      console.error('刪除失敗:', error);
      message.error('刪除失敗');
    }
  };

  // 狀態標籤
  const getStatusTag = (status: string) => {
    const statusConfig = {
      'draft': { color: 'orange', text: '草稿', icon: <FileTextOutlined /> },
      'pending_review': { color: 'orange', text: '待審核', icon: <ClockCircleOutlined /> },
      'approved': { color: 'green', text: '已審核', icon: <CheckCircleOutlined /> },
      'rejected': { color: 'red', text: '已拒絕', icon: <CloseOutlined /> },
      'published': { color: 'blue', text: '已發布', icon: <SendOutlined /> },
      'deleted': { color: 'gray', text: '已刪除', icon: <DeleteOutlined /> },
      'failed': { color: 'red', text: '發布失敗', icon: <ExclamationCircleOutlined /> }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending_review;
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 統計數據
  const stats = {
    total: posts.length,
    draft: posts.filter(p => p.status === 'draft').length,
    pending: posts.filter(p => p.status === 'pending_review').length,
    approved: posts.filter(p => p.status === 'approved').length,
    published: posts.filter(p => p.status === 'published').length,
    rejected: posts.filter(p => p.status === 'rejected').length
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 標題和統計 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={2}>
              📝 貼文審核管理
              {sessionId && <Text type="secondary"> (Session: {sessionId})</Text>}
            </Title>
            {onBack && (
              <Button onClick={onBack} icon={<EditOutlined />}>
                返回生成器
              </Button>
            )}
          </div>
        </Col>
      </Row>

      {/* 統計卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="總貼文數" 
              value={stats.total} 
              prefix={<Badge count={stats.total} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="草稿" 
              value={stats.draft} 
              valueStyle={{ color: '#fa8c16' }}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="待審核" 
              value={stats.pending} 
              valueStyle={{ color: '#fa8c16' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已審核" 
              value={stats.approved} 
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已發布" 
              value={stats.published} 
              valueStyle={{ color: '#1890ff' }}
              prefix={<SendOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作按鈕區域 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card size="small">
            <Space>
              <Button 
                icon={<EyeOutlined />}
                onClick={loadPosts}
              >
                刷新列表
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 貼文列表 */}
      <Card title="📋 貼文列表" extra={<Button onClick={loadPosts}>刷新</Button>}>
        <Table
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
        >
          <Column
            title="股票"
            dataIndex="stock_codes"
            key="stock"
            width={120}
            render={(codes: string[], record: Post) => {
              const stockCode = codes && codes[0] ? codes[0] : '無';

              // 🔥 如果是純話題（stock_code 以 TOPIC_ 開頭），顯示 "-"
              if (stockCode.startsWith('TOPIC_')) {
                return <Text type="secondary">-</Text>;
              }

              const stockName = record.stock_names && record.stock_names[0] ? record.stock_names[0] : '無';
              return (
                <div>
                  <Text strong>{stockName}</Text>
                  <br />
                  <Text type="secondary">({stockCode})</Text>
                </div>
              );
            }}
          />

          <Column
            title="熱門話題"
            key="trending_topic"
            width={150}
            render={(_, record: Post) => {
              if (record.has_trending_topic && record.topic_title) {
                return (
                  <Tooltip title={record.topic_content || record.topic_title}>
                    <Tag color="orange" icon={<FireOutlined />}>
                      {record.topic_title.length > 20
                        ? `${record.topic_title.substring(0, 20)}...`
                        : record.topic_title}
                    </Tag>
                  </Tooltip>
                );
              }
              return <Text type="secondary">-</Text>;
            }}
          />

          <Column
            title="KOL"
            dataIndex="kol_nickname"
            key="kol"
            width={100}
            render={(nickname: string, record: Post) => (
              <div>
                <Text>{nickname}</Text>
                <br />
                <Text type="secondary">{record.kol_persona}</Text>
              </div>
            )}
          />
          
          <Column
            title="標題"
            dataIndex="title"
            key="title"
            width={200}
            render={(title: string) => (
              <Tooltip title={title}>
                <Text ellipsis={{ tooltip: title }}>{title}</Text>
              </Tooltip>
            )}
          />
          
          <Column
            title="狀態"
            dataIndex="status"
            key="status"
            width={100}
            render={(status: string) => getStatusTag(status)}
          />
          
          <Column
            title="CMoney 信息"
            key="cmoney_info"
            width={200}
            render={(_, record: Post) => {
              if (record.status === 'published' && record.cmoney_post_id) {
                return (
                  <div>
                    <div>
                      <Text strong>ID: </Text>
                      <Text code>{record.cmoney_post_id}</Text>
                    </div>
                    {record.cmoney_post_url && record.cmoney_post_url !== 'undefined' && (
                      <div style={{ marginTop: 4 }}>
                        <a 
                          href={record.cmoney_post_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{ fontSize: '12px' }}
                        >
                          查看文章
                        </a>
                      </div>
                    )}
                  </div>
                );
              }
              return <Text type="secondary">-</Text>;
            }}
          />
          
          <Column
            title="創建時間"
            dataIndex="created_at"
            key="created_at"
            width={150}
            render={(time: string) => new Date(time).toLocaleString('zh-TW')}
          />
          
          <Column
            title="操作"
            key="actions"
            width={250}
            render={(_, record: Post) => (
              <Space size="small">
                <Tooltip title="預覽">
                  <Button 
                    icon={<EyeOutlined />} 
                    size="small"
                    onClick={() => handlePreview(record)}
                  />
                </Tooltip>
                
                <Tooltip title="查看 Body Message">
                  <Button 
                    icon={<FileTextOutlined />} 
                    size="small"
                    onClick={() => handleViewBodyMessage(record)}
                  />
                </Tooltip>
                
                {/* 版本預覽按鈕 - 檢查是否有 alternative_versions */}
                {(() => {
                  console.log(`🔍 檢查貼文 ${record.id} 的 alternative_versions:`, record.alternative_versions);
                  const hasVersions = record.alternative_versions && Array.isArray(record.alternative_versions) && record.alternative_versions.length > 0;
                  console.log(`🔍 貼文 ${record.id} 是否有版本:`, hasVersions);
                  return hasVersions;
                })() && (
                  <Tooltip title="版本預覽">
                    <Button 
                      icon={<BranchesOutlined />} 
                      size="small"
                      onClick={() => handleVersionPreview(record)}
                      style={{ color: '#1890ff' }}
                    />
                  </Tooltip>
                )}
                
                {/* 編輯按鈕 - 所有狀態都顯示 */}
                <Tooltip title="編輯">
                  <Button 
                    icon={<EditOutlined />} 
                    size="small"
                    onClick={() => handleEditPost(record)}
                  />
                </Tooltip>

                {(record.status === 'pending_review' || record.status === 'draft') && (record.id || record.post_id) && (
                  <>
                    <Popconfirm
                      title="確定審核通過？"
                      onConfirm={() => handleApprove((record.id || record.post_id).toString())}
                    >
                      <Tooltip title="直接審核通過">
                        <Button 
                          icon={<CheckOutlined />} 
                          size="small" 
                          type="primary"
                        />
                      </Tooltip>
                    </Popconfirm>
                    
                    <Popconfirm
                      title="拒絕原因"
                      description="請輸入拒絕原因"
                      onConfirm={(e) => {
                        const reason = prompt('請輸入拒絕原因:');
                        if (reason) {
                          handleReject((record.id || record.post_id).toString(), reason);
                        }
                      }}
                    >
                      <Tooltip title="拒絕">
                        <Button 
                          icon={<CloseOutlined />} 
                          size="small" 
                          danger
                        />
                      </Tooltip>
                    </Popconfirm>
                  </>
                )}
                
                {/* 對於沒有 ID 的草稿，顯示提示 */}
                {(record.status === 'draft' && !record.id && !record.post_id) && (
                  <Tooltip title="此草稿尚未分配 ID，無法進行審核操作">
                    <Button 
                      icon={<ExclamationCircleOutlined />} 
                      size="small" 
                      disabled
                      style={{ color: '#faad14' }}
                    />
                  </Tooltip>
                )}
                
                {(record.status === 'approved' || record.status === 'draft') && (
                  <Popconfirm
                    title="確定發布到CMoney？"
                    onConfirm={() => handlePublish(record)}
                  >
                    <Tooltip title="發布">
                      <Button 
                        icon={<SendOutlined />} 
                        size="small" 
                        type="primary"
                        loading={publishing.has(record.id.toString())}
                      />
                    </Tooltip>
                  </Popconfirm>
                )}
                
                {/* 刪除按鈕 - 已發布或已刪除狀態顯示 */}
                {(record.status === 'published' || record.status === 'deleted') && (
                  <Popconfirm
                    title="確定刪除此貼文？"
                    description={record.status === 'deleted' ? 
                      "此貼文已從CMoney平台刪除" : 
                      "此操作將從CMoney平台刪除該貼文，且無法復原"
                    }
                    onConfirm={() => handleDelete(record)}
                  >
                    <Tooltip title={record.status === 'deleted' ? "已刪除" : "刪除貼文"}>
                      <Button 
                        icon={<DeleteOutlined />} 
                        size="small" 
                        danger={record.status === 'published'}
                        disabled={record.status === 'deleted'}
                      />
                    </Tooltip>
                  </Popconfirm>
                )}
                
                {/* 調試信息 */}
                {record.status === 'published' && (
                  <Tooltip title={`調試: status=${record.status}, cmoney_post_id=${record.cmoney_post_id}, id=${record.id}`}>
                    <Button 
                      size="small" 
                      style={{ backgroundColor: '#f0f0f0', color: '#666' }}
                      onClick={() => {
                        console.log('已發布貼文詳情:', {
                          id: record.id,
                          status: record.status,
                          cmoney_post_id: record.cmoney_post_id,
                          cmoney_post_url: record.cmoney_post_url,
                          title: record.title,
                          stock_names: record.stock_names
                        });
                      }}
                    >
                      D
                    </Button>
                  </Tooltip>
                )}
              </Space>
            )}
          />
        </Table>
      </Card>

      {/* 預覽Modal */}
      <Modal
        title={`預覽貼文 - ${selectedPost?.stock_names && selectedPost.stock_names[0] ? selectedPost.stock_names[0] : '未知股票'}(${selectedPost?.stock_codes && selectedPost.stock_codes[0] ? selectedPost.stock_codes[0] : '未知代碼'})`}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            關閉
          </Button>
        ]}
      >
        {selectedPost && (
          <div>
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={12}>
                <Text strong>KOL: </Text>
                <Text>{selectedPost.kol_nickname} ({selectedPost.kol_persona})</Text>
              </Col>
              <Col span={12}>
                <Text strong>狀態: </Text>
                {getStatusTag(selectedPost.status)}
              </Col>
            </Row>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>{selectedPost.title}</Title>
            </div>
            
            <div style={{ 
              maxHeight: '400px', 
              overflow: 'auto',
              border: '1px solid #f0f0f0',
              padding: '16px',
              borderRadius: '6px',
              backgroundColor: '#fafafa'
            }}>
              <div dangerouslySetInnerHTML={{ 
                __html: selectedPost.content.replace(/\n/g, '<br/>') 
              }} />
            </div>
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={8}>
                <Text strong>品質分數: </Text>
                <Text>{selectedPost.quality_score || '未評分'}</Text>
              </Col>
              <Col span={8}>
                <Text strong>AI檢測分數: </Text>
                <Text>{selectedPost.ai_detection_score || '未檢測'}</Text>
              </Col>
              <Col span={8}>
                <Text strong>風險等級: </Text>
                <Text>{selectedPost.risk_level || '未評估'}</Text>
              </Col>
            </Row>
            
            <Divider />
            
            {/* 生成參數 */}
            <div>
              <Title level={5}>生成參數</Title>
              <Row gutter={16}>
                <Col span={12}>
                  <Text strong>股票代碼: </Text>
                  <Text>{selectedPost.stock_codes && selectedPost.stock_codes[0] ? selectedPost.stock_codes[0] : '無'}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>股票名稱: </Text>
                  <Text>{selectedPost.stock_names && selectedPost.stock_names[0] ? selectedPost.stock_names[0] : '無'}</Text>
                </Col>
              </Row>
              <Row gutter={16} style={{ marginTop: '8px' }}>
                <Col span={12}>
                  <Text strong>KOL序號: </Text>
                  <Text>{selectedPost.kol_serial}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>KOL人設: </Text>
                  <Text>{selectedPost.kol_persona || '未設定'}</Text>
                </Col>
              </Row>
              <Row gutter={16} style={{ marginTop: '8px' }}>
                <Col span={12}>
                  <Text strong>技術指標: </Text>
                  <Text>{selectedPost.technical_indicators && selectedPost.technical_indicators.length > 0 ? selectedPost.technical_indicators.join(', ') : '無'}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>商品標籤: </Text>
                  <Text>{selectedPost.commodity_tags && selectedPost.commodity_tags.length > 0 ? selectedPost.commodity_tags.map(tag => tag.name || tag).join(', ') : '無'}</Text>
                </Col>
              </Row>
              {selectedPost.generation_config && (
                <Row gutter={16} style={{ marginTop: '8px' }}>
                  <Col span={24}>
                    <Text strong>生成配置: </Text>
                    <pre style={{ 
                      backgroundColor: '#f5f5f5', 
                      padding: '8px', 
                      borderRadius: '4px',
                      fontSize: '12px',
                      marginTop: '4px',
                      maxHeight: '200px',
                      overflow: 'auto'
                    }}>
                      {JSON.stringify(selectedPost.generation_config, null, 2)}
                    </pre>
                  </Col>
                </Row>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Body Message Modal */}
      <Modal
        title={`Body Message - ${selectedPost?.stock_names && selectedPost.stock_names[0] ? selectedPost.stock_names[0] : '未知股票'}(${selectedPost?.stock_codes && selectedPost.stock_codes[0] ? selectedPost.stock_codes[0] : '未知代碼'})`}
        open={bodyMessageVisible}
        onCancel={() => setBodyMessageVisible(false)}
        width={1000}
        footer={[
          <Button key="close" onClick={() => setBodyMessageVisible(false)}>
            關閉
          </Button>
        ]}
      >
        {selectedPost && (
          <div>
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={12}>
                <Text strong>KOL: </Text>
                <Text>{selectedPost.kol_nickname} ({selectedPost.kol_persona})</Text>
              </Col>
              <Col span={12}>
                <Text strong>狀態: </Text>
                {getStatusTag(selectedPost.status)}
              </Col>
            </Row>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>標題</Title>
              <Text>{selectedPost.title}</Text>
            </div>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>內容</Title>
              <div style={{ 
                backgroundColor: '#f5f5f5', 
                padding: '16px', 
                borderRadius: '6px',
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '14px',
                maxHeight: '400px',
                overflow: 'auto'
              }}>
                {selectedPost.content}
              </div>
            </div>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>股票標籤 (Commodity Tags)</Title>
              <div style={{ 
                backgroundColor: '#f0f8ff', 
                padding: '16px', 
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '14px'
              }}>
                {JSON.stringify(selectedPost.generation_config?.commodity_tags || [], null, 2)}
              </div>
            </div>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>生成配置</Title>
              <div style={{ 
                backgroundColor: '#f9f9f9', 
                padding: '16px', 
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
                maxHeight: '300px',
                overflow: 'auto'
              }}>
                {JSON.stringify(selectedPost.generation_config || {}, null, 2)}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* 編輯Modal */}
      <Modal
        title={`編輯貼文 - ${editingPost?.stock_names && editingPost.stock_names[0] ? editingPost.stock_names[0] : '未知股票'}(${editingPost?.stock_codes && editingPost.stock_codes[0] ? editingPost.stock_codes[0] : '未知代碼'})`}
        open={editModalVisible}
        onCancel={handleCancelEdit}
        width={1000}
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
                <Text strong>KOL: </Text>
                <Text>{editingPost.kol_nickname} ({editingPost.kol_persona})</Text>
              </Col>
              <Col span={12}>
                <Text strong>狀態: </Text>
                {getStatusTag(editingPost.status)}
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
                rows={12}
                showCount
                maxLength={2000}
              />
            </Form.Item>
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={8}>
                <Text strong>品質分數: </Text>
                <Text>{editingPost.quality_score}</Text>
              </Col>
              <Col span={8}>
                <Text strong>AI檢測分數: </Text>
                <Text>{editingPost.ai_detection_score}</Text>
              </Col>
              <Col span={8}>
                <Text strong>風險等級: </Text>
                <Text>{editingPost.risk_level}</Text>
              </Col>
            </Row>
          </Form>
        )}
      </Modal>

      {/* 版本預覽Modal */}
      <Modal
        title={`版本預覽 - ${selectedPostForVersions?.stock_names && selectedPostForVersions.stock_names[0] ? selectedPostForVersions.stock_names[0] : '未知股票'}(${selectedPostForVersions?.stock_codes && selectedPostForVersions.stock_codes[0] ? selectedPostForVersions.stock_codes[0] : '未知代碼'})`}
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
            取消
          </Button>
        ]}
      >
        {selectedPostForVersions && (
          <div>
            <Alert
              message="版本選擇"
              description={`當前貼文有 ${alternativeVersions.length} 個其他版本可供選擇。點擊「選擇此版本」來替換當前內容。`}
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />
            
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>當前版本</Title>
              <Card size="small" style={{ backgroundColor: '#f0f8ff' }}>
                <div style={{ marginBottom: '8px' }}>
                  <Text strong>標題：</Text>
                  <Text>{selectedPostForVersions.title}</Text>
                </div>
                <div>
                  <Text strong>內容：</Text>
                  <div style={{ 
                    marginTop: '8px',
                    padding: '8px',
                    backgroundColor: '#f9f9f9',
                    borderRadius: '4px',
                    fontSize: '12px',
                    maxHeight: '100px',
                    overflow: 'auto'
                  }}>
                    {selectedPostForVersions.content.substring(0, 200)}...
                  </div>
                </div>
              </Card>
            </div>
            
            <Divider />
            
            <Title level={4}>其他版本 ({alternativeVersions.length} 個)</Title>
            
            <div style={{ maxHeight: '500px', overflow: 'auto' }}>
              {alternativeVersions.map((version, index) => (
                <Card 
                  key={index} 
                  size="small" 
                  style={{ marginBottom: '12px' }}
                  title={`版本 ${version.version_number || index + 1} - ${version.angle || '分析型'}`}
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
                    <Text>{version.title}</Text>
                  </div>
                  <div>
                    <Text strong>內容：</Text>
                    <div style={{ 
                      marginTop: '8px',
                      padding: '8px',
                      backgroundColor: '#f9f9f9',
                      borderRadius: '4px',
                      fontSize: '12px',
                      maxHeight: '150px',
                      overflow: 'auto',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {version.content}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </Modal>

    </div>
  );
};

export default PostReviewPage;

