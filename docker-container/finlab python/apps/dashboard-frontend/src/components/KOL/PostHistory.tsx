import React, { useState } from 'react';
import { Table, Button, Tag, Space, Pagination, message, Modal, Descriptions } from 'antd';
import { 
  EyeOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  LinkOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { PostHistoryProps, PostHistory as PostHistoryType } from '../../types/kol-types';

const PostHistory: React.FC<PostHistoryProps> = ({
  posts,
  loading,
  error,
  pagination,
  onPageChange,
  onViewDetail
}) => {
  const [selectedPost, setSelectedPost] = useState<PostHistoryType | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [deletingPost, setDeletingPost] = useState<PostHistoryType | null>(null);

  // 處理平台 URL 點擊
  const handlePlatformUrlClick = (url: string) => {
    if (!url || url.trim() === '') {
      message.warning('該貼文尚未發布或無平台 URL');
      return;
    }

    try {
      // 驗證 URL 格式
      new URL(url);
      
      // 在新視窗中打開連結
      const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
      
      if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
        message.error('無法打開連結，請檢查瀏覽器設定');
      } else {
        message.success('正在打開平台連結...');
      }
    } catch (error) {
      message.error('無效的 URL 格式');
      console.error('URL validation error:', error);
    }
  };

  // 查看貼文詳情
  const handleViewDetail = (post: PostHistoryType) => {
    setSelectedPost(post);
    setModalVisible(true);
  };

  // 顯示刪除確認對話框
  const handleDeleteClick = (post: PostHistoryType) => {
    setDeletingPost(post);
    setDeleteModalVisible(true);
  };

  // 執行刪除貼文
  const handleDeleteConfirm = async () => {
    if (!deletingPost) return;
    
    try {
      const response = await fetch(`/api/dashboard/posts/${deletingPost.post_id}/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        message.success('貼文已成功刪除');
        setDeleteModalVisible(false);
        setDeletingPost(null);
        // 刷新頁面數據
        window.location.reload();
      } else {
        const errorData = await response.json();
        message.error(errorData.message || '刪除貼文失敗');
      }
    } catch (error) {
      console.error('刪除貼文錯誤:', error);
      message.error('刪除貼文時發生錯誤');
    }
  };

  // 表格列定義
  const columns = [
    {
      title: '貼文 ID',
      dataIndex: 'post_id',
      key: 'post_id',
      width: 120,
      render: (text: string) => (
        <Button 
          type="link" 
          size="small"
          onClick={() => onViewDetail(text)}
        >
          {text}
        </Button>
      ),
    },
    {
      title: '話題標題',
      dataIndex: 'topic_title',
      key: 'topic_title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '內容預覽',
      dataIndex: 'content',
      key: 'content',
      width: 300,
      ellipsis: true,
      render: (text: string) => (
        <div style={{ maxWidth: '280px' }}>
          {text ? `${text.substring(0, 50)}...` : '-'}
        </div>
      ),
    },
    {
      title: '發文時間',
      dataIndex: 'post_time',
      key: 'post_time',
      width: 150,
      render: (time: string) => {
        if (!time || time.trim() === '') return '-';
        try {
          return new Date(time).toLocaleString('zh-TW');
        } catch {
          return time;
        }
      },
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusConfig = {
          '已發布': { color: 'green', icon: <CheckCircleOutlined /> },
          '草稿': { color: 'orange', icon: <ClockCircleOutlined /> },
          '待發布': { color: 'blue', icon: <ClockCircleOutlined /> },
          '發布失敗': { color: 'red', icon: <ExclamationCircleOutlined /> }
        };
        
        const config = statusConfig[status as keyof typeof statusConfig] || { 
          color: 'default', 
          icon: <ClockCircleOutlined /> 
        };
        
        return (
          <Tag color={config.color} icon={config.icon}>
            {status}
          </Tag>
        );
      },
    },
    {
      title: '互動數據',
      key: 'interactions',
      width: 120,
      render: (record: PostHistoryType) => {
        const interactions = record.interactions?.['7days'];
        if (!interactions) return '-';
        
        return (
          <div style={{ fontSize: '12px' }}>
            <div>👍 {interactions.likes_count}</div>
            <div>💬 {interactions.comments_count}</div>
            <div>📊 {interactions.total_interactions}</div>
          </div>
        );
      },
    },
    {
      title: 'CMoney文章ID',
      dataIndex: 'platform_post_id',
      key: 'platform_post_id',
      width: 120,
      render: (articleId: string, record: PostHistoryType) => {
        if (record.status !== '已發布') {
          return <Tag color="orange">未發布</Tag>;
        }
        
        if (!articleId || articleId.trim() === '') {
          return <Tag color="red">無ID</Tag>;
        }
        
        return (
          <Text code style={{ fontSize: '12px', backgroundColor: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
            {articleId}
          </Text>
        );
      },
    },
    {
      title: 'CMoney連結',
      dataIndex: 'platform_post_url',
      key: 'platform_post_url',
      width: 100,
      render: (url: string, record: PostHistoryType) => {
        if (record.status !== '已發布') {
          return <Tag color="orange">未發布</Tag>;
        }
        
        if (!url || url.trim() === '') {
          return <Tag color="red">無URL</Tag>;
        }
        
        return (
          <Button 
            type="link" 
            size="small"
            onClick={() => handlePlatformUrlClick(url)}
            icon={<LinkOutlined />}
            style={{ padding: '4px 8px' }}
          >
            查看
          </Button>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (record: PostHistoryType) => (
        <Space>
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            詳情
          </Button>
          <Button 
            type="link" 
            size="small" 
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteClick(record)}
            disabled={record.status === '已刪除' || record.status !== '已發布' || !record.platform_post_id}
          >
            刪除
          </Button>
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div>載入發文歷史中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ color: '#ff4d4f' }}>載入失敗: {error}</div>
    );
  }

  return (
    <div>
      <Table
        columns={columns}
        dataSource={posts}
        rowKey="post_id"
        size="small"
        pagination={false}
        scroll={{ x: 1200 }}
        style={{ marginBottom: '16px' }}
      />
      
      {pagination.total_items > 0 && (
        <div style={{ textAlign: 'right' }}>
          <Pagination
            current={pagination.current_page}
            pageSize={pagination.page_size}
            total={pagination.total_items}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
            }
            onChange={(page, pageSize) => onPageChange(page, pageSize || 10)}
            onShowSizeChange={(_, size) => onPageChange(1, size)}
          />
        </div>
      )}

      {/* 貼文詳情彈窗 */}
      <Modal
        title={`貼文詳情 - ${selectedPost?.post_id}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            關閉
          </Button>,
          selectedPost?.platform_post_url && selectedPost?.status === '已發布' && (
            <Button 
              key="view" 
              type="primary"
              icon={<LinkOutlined />}
              onClick={() => handlePlatformUrlClick(selectedPost.platform_post_url)}
            >
              查看原文
            </Button>
          )
        ]}
      >
        {selectedPost && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="貼文ID" span={2}>
              {selectedPost.post_id}
            </Descriptions.Item>
            <Descriptions.Item label="話題標題" span={2}>
              {selectedPost.topic_title}
            </Descriptions.Item>
            <Descriptions.Item label="話題關鍵詞" span={2}>
              {selectedPost.topic_keywords}
            </Descriptions.Item>
            <Descriptions.Item label="發文狀態">
              <Tag color={selectedPost.status === '已發布' ? 'green' : 'orange'}>
                {selectedPost.status}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="發文時間">
              {selectedPost.post_time ? new Date(selectedPost.post_time).toLocaleString('zh-TW') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="排程時間">
              {selectedPost.scheduled_time ? new Date(selectedPost.scheduled_time).toLocaleString('zh-TW') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="平台發文ID">
              {selectedPost.platform_post_id || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="平台URL" span={2}>
              {selectedPost.platform_post_url ? (
                <a 
                  href={selectedPost.platform_post_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ wordBreak: 'break-all' }}
                >
                  {selectedPost.platform_post_url}
                </a>
              ) : (
                <span style={{ color: '#999' }}>無</span>
              )}
            </Descriptions.Item>
            {selectedPost.error_message && (
              <Descriptions.Item label="錯誤訊息" span={2}>
                <span style={{ color: '#ff4d4f' }}>{selectedPost.error_message}</span>
              </Descriptions.Item>
            )}
            <Descriptions.Item label="內容" span={2}>
              <div style={{ 
                maxHeight: '200px', 
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                backgroundColor: '#f5f5f5',
                padding: '12px',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                {selectedPost.content}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="互動數據" span={2}>
              <div style={{ display: 'flex', gap: '16px' }}>
                <div>
                  <strong>1小時:</strong> 👍 {selectedPost.interactions?.['1hr']?.likes_count || 0} 
                  💬 {selectedPost.interactions?.['1hr']?.comments_count || 0}
                </div>
                <div>
                  <strong>1天:</strong> 👍 {selectedPost.interactions?.['1day']?.likes_count || 0} 
                  💬 {selectedPost.interactions?.['1day']?.comments_count || 0}
                </div>
                <div>
                  <strong>7天:</strong> 👍 {selectedPost.interactions?.['7days']?.likes_count || 0} 
                  💬 {selectedPost.interactions?.['7days']?.comments_count || 0}
                </div>
              </div>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
      
      {/* 刪除確認對話框 */}
      <Modal
        title="確認刪除貼文"
        open={deleteModalVisible}
        onOk={handleDeleteConfirm}
        onCancel={() => {
          setDeleteModalVisible(false);
          setDeletingPost(null);
        }}
        okText="確認刪除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <p>您確定要刪除這篇貼文嗎？</p>
        {deletingPost && (
          <>
            <p><strong>貼文 ID:</strong> {deletingPost.post_id}</p>
            <p><strong>KOL:</strong> {deletingPost.kol_nickname}</p>
            <p><strong>話題標題:</strong> {deletingPost.topic_title}</p>
            <p><strong>狀態:</strong> {deletingPost.status}</p>
          </>
        )}
        <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff7e6', border: '1px solid #ffd591', borderRadius: '4px' }}>
          <p style={{ margin: 0, color: '#d46b08' }}>
            <strong>⚠️ 注意：</strong>此操作將從CMoney平台實際刪除貼文，並在我們的系統中標記為已刪除。此操作不可逆轉！
          </p>
        </div>
      </Modal>
    </div>
  );
};

export default PostHistory;
