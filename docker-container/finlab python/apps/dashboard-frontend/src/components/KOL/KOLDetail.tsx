import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Row, Col, Button, Breadcrumb, Spin, Alert, message, Space, Statistic } from 'antd';
import { ArrowLeftOutlined, ReloadOutlined, EditOutlined, SaveOutlined, CloseOutlined, FileTextOutlined, BarChartOutlined, LikeOutlined, MessageOutlined } from '@ant-design/icons';
import KOLBasicInfo from './KOLBasicInfo';
import KOLSettings from './KOLSettings';
import PostHistory from './PostHistory';
import InteractionChart from './InteractionChart';
import TrendChart from './TrendChart';
import { KOLInfo, KOLStatistics, PostHistory as PostHistoryType, InteractionTrend } from '../../types/kol-types';
import api from '../../services/api';
import axios from 'axios';

const KOLDetail: React.FC = () => {
  const { serial } = useParams<{ serial: string }>();
  const navigate = useNavigate();

  // 狀態管理
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [kolInfo, setKolInfo] = useState<KOLInfo | null>(null);
  const [statistics, setStatistics] = useState<KOLStatistics | null>(null);
  const [posts, setPosts] = useState<PostHistoryType[]>([]);
  const [, setInteractionTrend] = useState<InteractionTrend[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  // 編輯模式狀態
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingKolInfo, setEditingKolInfo] = useState<KOLInfo | null>(null);
  const [saving, setSaving] = useState(false);

  // 載入 KOL 詳情數據
  const fetchKOLDetail = async () => {
    if (!serial) return;

    setLoading(true);
    setError(null);

    try {
      // 使用 Vercel API proxy 或直接 Railway URL
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

      // 直接獲取 KOL 詳情
      const response = await axios.get(`${API_BASE_URL}/api/kol/${serial}`);

      if (response.data && !response.data.error) {
        // 直接使用 PostgreSQL API 返回的數據
        setKolInfo(response.data);
        // 創建統計數據結構
        setStatistics({
          total_posts: response.data.total_posts || 0,
          published_posts: response.data.published_posts || 0,
          avg_interaction_rate: response.data.avg_interaction_rate || 0,
          best_performing_post: response.data.best_performing_post || ''
        });
        setLastUpdated(new Date().toISOString());
      } else {
        setError(response.data.error || '獲取 KOL 詳情失敗');
      }
    } catch (err: any) {
      console.error('獲取 KOL 詳情失敗:', err);
      setError(err.response?.data?.error || err.response?.data?.detail || '獲取 KOL 詳情失敗');
    } finally {
      setLoading(false);
    }
  };

  // 載入發文歷史
  const fetchPosts = async (page: number = 1, pageSize: number = 10) => {
    if (!serial) return;

    try {
      const response = await api.get(`/dashboard/kols/${serial}/posts`, {
        params: { page, page_size: pageSize }
      });

      if (response.data && response.data.success && response.data.data) {
        setPosts(response.data.data.posts);
      }
    } catch (err: any) {
      console.error('獲取發文歷史失敗:', err);
      message.error('獲取發文歷史失敗');
    }
  };

  // 載入互動數據
  const fetchInteractions = async () => {
    if (!serial) return;

    try {
      const response = await api.get(`/dashboard/kols/${serial}/interactions`);

      if (response.data && response.data.success && response.data.data) {
        setInteractionTrend(response.data.data.interaction_trend);
      }
    } catch (err: any) {
      console.error('獲取互動數據失敗:', err);
    }
  };

  // 初始化載入
  useEffect(() => {
    if (serial) {
      fetchKOLDetail();
      fetchPosts();
      fetchInteractions();
    }
  }, [serial]);

  // 刷新數據
  const handleRefresh = () => {
    fetchKOLDetail();
    fetchPosts();
    fetchInteractions();
    message.success('數據已刷新');
  };

  // 返回 KOL 列表
  const handleBack = () => {
    navigate('/content-management');
  };

  // 查看貼文詳情
  const handleViewPostDetail = (postId: string) => {
    // 這裡可以實現貼文詳情彈窗或跳轉到詳情頁面
    message.info(`查看貼文詳情: ${postId}`);
  };

  // 分頁處理
  const handlePageChange = (page: number, pageSize: number) => {
    fetchPosts(page, pageSize);
  };

  // 編輯模式處理
  const handleEditMode = () => {
    if (kolInfo) {
      setEditingKolInfo({ ...kolInfo });
      setIsEditMode(true);
    }
  };

  const handleCancelEdit = () => {
    setEditingKolInfo(null);
    setIsEditMode(false);
  };

  const handleSaveEdit = async () => {
    if (!editingKolInfo || !serial) return;

    setSaving(true);
    try {
      const response = await api.put(`/dashboard/kols/${serial}`, editingKolInfo);

      if (response.data && response.data.success) {
        setKolInfo(editingKolInfo);
        setIsEditMode(false);
        setEditingKolInfo(null);
        message.success('KOL 設定已成功更新');
        // 重新載入數據以獲取最新狀態
        await fetchKOLDetail();
      } else {
        message.error('更新失敗，請重試');
      }
    } catch (err: any) {
      console.error('更新 KOL 設定失敗:', err);
      message.error(err.response?.data?.detail || '更新失敗，請重試');
    } finally {
      setSaving(false);
    }
  };

  const handleKolInfoChange = (field: keyof KOLInfo, value: any) => {
    if (editingKolInfo) {
      setEditingKolInfo({
        ...editingKolInfo,
        [field]: value
      });
    }
  };

  if (loading && !kolInfo) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>載入 KOL 詳情中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="載入失敗"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={handleRefresh}>
              重試
            </Button>
          }
        />
      </div>
    );
  }

  if (!kolInfo) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="KOL 不存在"
          description={`找不到 Serial: ${serial}`}
          type="warning"
          showIcon
        />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題和操作 */}
      <div style={{ marginBottom: '24px' }}>
        <Breadcrumb style={{ marginBottom: '16px' }}>
          <Breadcrumb.Item>
            <Button type="link" onClick={handleBack} style={{ padding: 0 }}>
              內容管理
            </Button>
          </Breadcrumb.Item>
          <Breadcrumb.Item>
            <Button type="link" onClick={handleBack} style={{ padding: 0 }}>
              KOL 管理
            </Button>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{kolInfo.nickname}</Breadcrumb.Item>
        </Breadcrumb>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
              KOL 個人詳情 - {kolInfo.nickname}
              {isEditMode && <span style={{ color: '#1890ff', fontSize: '16px', marginLeft: '8px' }}>(編輯模式)</span>}
            </h1>
            {lastUpdated && (
              <div style={{ color: '#666', fontSize: '14px', marginTop: '4px' }}>
                最後更新: {new Date(lastUpdated).toLocaleString('zh-TW')}
              </div>
            )}
          </div>
          
          <Space>
            {isEditMode ? (
              <>
                <Button 
                  icon={<CloseOutlined />} 
                  onClick={handleCancelEdit}
                  disabled={saving}
                >
                  取消
                </Button>
                <Button 
                  type="primary" 
                  icon={<SaveOutlined />} 
                  onClick={handleSaveEdit}
                  loading={saving}
                >
                  儲存
                </Button>
              </>
            ) : (
              <>
                <Button 
                  icon={<ArrowLeftOutlined />} 
                  onClick={handleBack}
                >
                  返回
                </Button>
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={handleRefresh}
                  loading={loading}
                >
                  刷新
                </Button>
                <Button 
                  icon={<EditOutlined />} 
                  onClick={handleEditMode}
                  type="primary"
                >
                  編輯
                </Button>
              </>
            )}
          </Space>
        </div>
      </div>

      {/* 基本資訊卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <KOLBasicInfo
            kolInfo={isEditMode ? (editingKolInfo || {} as KOLInfo) : (kolInfo || {} as KOLInfo)}
            statistics={statistics || {
              total_posts: 0,
              published_posts: 0,
              draft_posts: 0,
              avg_interaction_rate: 0,
              best_performing_post: '',
              total_interactions: 0,
              avg_likes_per_post: 0,
              avg_comments_per_post: 0,
              trend_data: [],
              monthly_stats: [],
              weekly_stats: [],
              daily_stats: []
            }}
            loading={loading}
            error={error}
            isEditMode={isEditMode}
            onKolInfoChange={handleKolInfoChange}
          />
        </Col>
      </Row>

      {/* 統計數據卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="📊 統計數據概覽" size="small">
            <Row gutter={[16, 16]}>
              <Col span={6}>
                <Statistic
                  title="發文總量"
                  value={statistics?.total_posts || 0}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="平均互動數"
                  value={statistics?.avg_interaction_rate || 0}
                  precision={3}
                  prefix={<BarChartOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="平均貼文按讚數"
                  value={statistics?.avg_likes_per_post || 0}
                  precision={1}
                  prefix={<LikeOutlined />}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="平均貼文留言數"
                  value={statistics?.avg_comments_per_post || 0}
                  precision={1}
                  prefix={<MessageOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 趨勢圖表卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <TrendChart
            monthlyStats={statistics?.monthly_stats || []}
            weeklyStats={statistics?.weekly_stats || []}
            dailyStats={statistics?.daily_stats || []}
            loading={loading}
          />
        </Col>
      </Row>

      {/* 人設設定卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <KOLSettings
            kolInfo={isEditMode ? (editingKolInfo || {} as KOLInfo) : (kolInfo || {} as KOLInfo)}
            loading={loading}
            error={error}
            isEditMode={isEditMode}
            onKolInfoChange={handleKolInfoChange}
          />
        </Col>
      </Row>

      {/* 發文歷史 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="發文歷史" size="small">
            <PostHistory
              posts={posts}
              loading={loading}
              error={error}
              pagination={{
                current_page: 1,
                page_size: 10,
                total_pages: Math.ceil(posts.length / 10),
                total_items: posts.length
              }}
              onPageChange={handlePageChange}
              onViewDetail={handleViewPostDetail}
            />
          </Card>
        </Col>
      </Row>

      {/* 互動分析 */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="互動表現分析" size="small">
            <InteractionChart
              memberId={serial || ''}
              loading={loading}
              error={error}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default KOLDetail;
