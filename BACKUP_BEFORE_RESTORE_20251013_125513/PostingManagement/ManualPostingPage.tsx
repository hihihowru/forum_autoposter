import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Input, Button, Select, message, Space, Typography, Spin, List, Tag, Divider } from 'antd';
import { 
  SendOutlined, 
  ClearOutlined, 
  UserOutlined,
  HistoryOutlined,
  ClockCircleOutlined,
  StockOutlined,
  TagOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 類型定義
interface KOLInfo {
  serial: string;
  nickname: string;
  persona: string;
  status: string;
}

interface StockInfo {
  code: string;
  name: string;
  industry: string;
}

interface TopicInfo {
  id: string;
  title: string;
  name: string;
}


interface ManualPostingFormData {
  title: string;
  content: string;
  selectedStocks: string[];
  selectedTopics: string[];
}

interface RecentPost {
  post_id: string;
  kol_nickname: string;
  title: string;
  created_at: string;
  stock_name: string;
  topic_title: string;
}

interface BatchRecord {
  session_id: string;
  created_at: string;
  total_posts: number;
  success_posts: number;
  success_rate: number;
  trigger_type: string;
  kol_names: string[];
  stock_names: string[];
  posts: Array<{
    post_id: string;
    title: string;
    kol_nickname: string;
    stock_name: string;
    status: string;
    created_at: string;
  }>;
}

const ManualPostingPage: React.FC = () => {
  // 狀態管理
  const [kols, setKols] = useState<KOLInfo[]>([]);
  const [stocks, setStocks] = useState<StockInfo[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<TopicInfo[]>([]);
  const [recentPosts, setRecentPosts] = useState<RecentPost[]>([]);
  const [batchHistory, setBatchHistory] = useState<BatchRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<{ [key: string]: boolean }>({});
  const [stockSearchResults, setStockSearchResults] = useState<StockInfo[]>([]);
  
  // 表單狀態
  const [formData, setFormData] = useState<{ [key: string]: ManualPostingFormData }>({});
  
  // API 基礎 URL
  const API_BASE = 'http://localhost:8001/api/manual-posting';

  // 初始化
  useEffect(() => {
    initializeData();
  }, []);

  // 初始化資料
  const initializeData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadKOLs(),
        loadStocks(),
        loadTrendingTopics(),
        loadRecentPosts(),
        loadBatchHistory()
      ]);
    } catch (error) {
      console.error('初始化失敗:', error);
      message.error('初始化失敗: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 載入 KOL 列表
  const loadKOLs = async () => {
    try {
      const response = await fetch(`${API_BASE}/kols`);
      if (!response.ok) throw new Error('載入 KOL 失敗');
      const kolsData = await response.json();
      setKols(kolsData);
      
      // 初始化表單資料
      const initialFormData: { [key: string]: ManualPostingFormData } = {};
      kolsData.forEach((kol: KOLInfo) => {
        initialFormData[kol.serial] = {
          title: '',
          content: '',
          selectedStocks: [],
          selectedTopics: []
        };
      });
      setFormData(initialFormData);
    } catch (error) {
      console.error('載入 KOL 失敗:', error);
      throw error;
    }
  };

  // 載入股票列表
  const loadStocks = async () => {
    try {
      const response = await fetch(`${API_BASE}/stocks`);
      if (!response.ok) throw new Error('載入股票失敗');
      const stocksData = await response.json();
      setStocks(stocksData);
      setStockSearchResults(stocksData); // 初始化搜尋結果
    } catch (error) {
      console.error('載入股票失敗:', error);
      throw error;
    }
  };

  // 載入熱門話題
  const loadTrendingTopics = async () => {
    try {
      const response = await fetch(`${API_BASE}/trending-topics`);
      if (!response.ok) throw new Error('載入熱門話題失敗');
      const topicsData = await response.json();
      setTrendingTopics(topicsData);
    } catch (error) {
      console.error('載入熱門話題失敗:', error);
      throw error;
    }
  };

  // 載入最近發文
  const loadRecentPosts = async () => {
    try {
      const response = await fetch(`${API_BASE}/recent-posts?limit=10`);
      if (!response.ok) throw new Error('載入最近發文失敗');
      const data = await response.json();
      setRecentPosts(data.posts || []);
    } catch (error) {
      console.error('載入最近發文失敗:', error);
      throw error;
    }
  };

  // 載入批次歷史
  const loadBatchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/batch-history?limit=10`);
      if (!response.ok) throw new Error('載入批次歷史失敗');
      const data = await response.json();
      setBatchHistory(data.batches || []);
    } catch (error) {
      console.error('載入批次歷史失敗:', error);
      throw error;
    }
  };


  // 搜尋股票
  const searchStocks = async (query: string) => {
    if (!query) {
      setStockSearchResults(stocks);
      return stocks;
    }
    
    try {
      const response = await fetch(`${API_BASE}/stocks/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('搜尋股票失敗');
      const data = await response.json();
      setStockSearchResults(data);
      return data;
    } catch (error) {
      console.error('搜尋股票失敗:', error);
      setStockSearchResults(stocks);
      return stocks;
    }
  };

  // 更新表單資料
  const updateFormData = (kolSerial: string, field: keyof ManualPostingFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [kolSerial]: {
        ...prev[kolSerial],
        [field]: value
      }
    }));
  };

  // 提交發文
  const submitPost = async (kolSerial: string) => {
    const data = formData[kolSerial];
    
    if (!data.title.trim()) {
      message.error('請輸入標題');
      return;
    }
    
    if (!data.content.trim()) {
      message.error('請輸入內容');
      return;
    }

    try {
      setSubmitting(prev => ({ ...prev, [kolSerial]: true }));
      
      const response = await fetch(`${API_BASE}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          kol_serial: parseInt(kolSerial),
          title: data.title,
          content: data.content,
          stock_codes: data.selectedStocks,
          communityTopics: data.selectedTopics
        })
      });

      const result = await response.json();
      
      if (result.success) {
        message.success(`發文成功！Post ID: ${result.post_id}`);
        clearForm(kolSerial);
        // 重新載入最近發文和批次歷史
        await Promise.all([loadRecentPosts(), loadBatchHistory()]);
      } else {
        message.error(`發文失敗: ${result.message}`);
      }
    } catch (error) {
      console.error('提交發文失敗:', error);
      message.error('提交發文失敗: ' + (error as Error).message);
    } finally {
      setSubmitting(prev => ({ ...prev, [kolSerial]: false }));
    }
  };

  // 清空表單
  const clearForm = (kolSerial: string) => {
    updateFormData(kolSerial, 'title', '');
    updateFormData(kolSerial, 'content', '');
    updateFormData(kolSerial, 'selectedStocks', []);
    updateFormData(kolSerial, 'selectedTopics', []);
  };


  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>載入中...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 頁面標題 */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <SendOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
          手動發文管理
        </Title>
        <Text type="secondary">類似水軍操作軟體，支援多KOL同時發文</Text>
      </Card>

      {/* 已發佈貼文列表 */}
      <Card 
        title={
          <Space>
            <HistoryOutlined />
            <Text strong>已發佈貼文</Text>
            <Tag color="blue">{recentPosts.length} 筆</Tag>
          </Space>
        }
        style={{ marginBottom: '24px' }}
        extra={
          <Button 
            type="link" 
            icon={<ClockCircleOutlined />}
            onClick={loadRecentPosts}
          >
            重新整理
          </Button>
        }
      >
        {recentPosts.length > 0 ? (
          <List
            dataSource={recentPosts}
            renderItem={(post) => (
              <List.Item>
                <Card size="small" style={{ width: '100%' }}>
                  <Row gutter={[16, 8]}>
                    <Col span={6}>
                      <Space>
                        <UserOutlined />
                        <Text strong>{post.kol_nickname}</Text>
                      </Space>
                    </Col>
                    <Col span={12}>
                      <Text strong ellipsis={{ tooltip: post.title }}>
                        {post.title}
                      </Text>
                    </Col>
                    <Col span={6}>
                      <Space>
                        <ClockCircleOutlined />
                        <Text type="secondary">
                          {new Date(post.created_at).toLocaleString('zh-TW')}
                        </Text>
                      </Space>
                    </Col>
                  </Row>
                  <Row gutter={[16, 8]} style={{ marginTop: 8 }}>
                    <Col span={12}>
                      <Space>
                        <StockOutlined />
                        <Tag color="green">{post.stock_name}</Tag>
                      </Space>
                    </Col>
                    <Col span={12}>
                      <Space>
                        <TagOutlined />
                        <Text type="secondary" ellipsis={{ tooltip: post.topic_title }}>
                          {post.topic_title}
                        </Text>
                      </Space>
                    </Col>
                  </Row>
                  <Row style={{ marginTop: 8 }}>
                    <Col span={24}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        Post ID: {post.post_id}
                      </Text>
                    </Col>
                  </Row>
                </Card>
              </List.Item>
            )}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            <HistoryOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>暫無發文記錄</div>
          </div>
        )}
      </Card>

      {/* 批次歷史 */}
      <Card 
        title={
          <Space>
            <HistoryOutlined />
            <Text strong>批次歷史</Text>
            <Tag color="purple">{batchHistory.length} 批次</Tag>
          </Space>
        }
        style={{ marginBottom: '24px' }}
        extra={
          <Button 
            type="link" 
            icon={<ClockCircleOutlined />}
            onClick={loadBatchHistory}
          >
            重新整理
          </Button>
        }
      >
        {batchHistory.length > 0 ? (
          <List
            dataSource={batchHistory}
            renderItem={(batch) => (
              <List.Item>
                <Card size="small" style={{ width: '100%' }}>
                  <Row gutter={[16, 8]}>
                    <Col span={6}>
                      <Space>
                        <Text strong>Session #{batch.session_id}</Text>
                      </Space>
                    </Col>
                    <Col span={6}>
                      <Space>
                        <ClockCircleOutlined />
                        <Text type="secondary">
                          {new Date(batch.created_at).toLocaleString('zh-TW')}
                        </Text>
                      </Space>
                    </Col>
                    <Col span={6}>
                      <Space>
                        <Tag color={batch.trigger_type === 'manual' ? 'blue' : 'green'}>
                          {batch.trigger_type === 'manual' ? '手動' : batch.trigger_type}
                        </Tag>
                        <Text strong>{batch.total_posts} 篇</Text>
                      </Space>
                    </Col>
                    <Col span={6}>
                      <Space>
                        <Text type="secondary">成功率: </Text>
                        <Text strong style={{ color: batch.success_rate >= 80 ? '#52c41a' : batch.success_rate >= 60 ? '#faad14' : '#ff4d4f' }}>
                          {batch.success_rate}%
                        </Text>
                      </Space>
                    </Col>
                  </Row>
                  <Row gutter={[16, 8]} style={{ marginTop: 8 }}>
                    <Col span={12}>
                      <Space wrap>
                        <Text type="secondary">KOL: </Text>
                        {batch.kol_names.map((name, index) => (
                          <Tag key={index} color="blue">{name}</Tag>
                        ))}
                      </Space>
                    </Col>
                    <Col span={12}>
                      <Space wrap>
                        <Text type="secondary">股票: </Text>
                        {batch.stock_names.slice(0, 3).map((name, index) => (
                          <Tag key={index} color="green">{name}</Tag>
                        ))}
                        {batch.stock_names.length > 3 && (
                          <Tag color="default">+{batch.stock_names.length - 3}</Tag>
                        )}
                      </Space>
                    </Col>
                  </Row>
                </Card>
              </List.Item>
            )}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            <HistoryOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>暫無批次記錄</div>
          </div>
        )}
      </Card>

      {/* KOL 發文區域 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {kols.map(kol => (
          <Card
            key={kol.serial}
            title={
              <Space>
                <UserOutlined />
                <Text strong>{kol.nickname}</Text>
                <Text type="secondary">(KOL-{kol.serial}) - {kol.persona}</Text>
              </Space>
            }
            extra={
              <Space>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  loading={submitting[kol.serial]}
                  onClick={() => submitPost(kol.serial)}
                >
                  送出
                </Button>
                <Button
                  icon={<ClearOutlined />}
                  onClick={() => clearForm(kol.serial)}
                >
                  清空
                </Button>
              </Space>
            }
          >
            <Row gutter={[16, 16]}>
              {/* 標題 */}
              <Col span={24}>
                <Text strong>標題:</Text>
                <Input
                  value={formData[kol.serial]?.title || ''}
                  onChange={(e) => updateFormData(kol.serial, 'title', e.target.value)}
                  placeholder="輸入標題..."
                  style={{ marginTop: '8px' }}
                />
              </Col>

              {/* 內容 */}
              <Col span={24}>
                <Text strong>內容:</Text>
                <TextArea
                  value={formData[kol.serial]?.content || ''}
                  onChange={(e) => updateFormData(kol.serial, 'content', e.target.value)}
                  placeholder="輸入內容..."
                  rows={4}
                  style={{ marginTop: '8px' }}
                />
              </Col>

              {/* 股票標籤 */}
              <Col span={12}>
                <Text strong>股票標籤:</Text>
                <Select
                  mode="multiple"
                  value={formData[kol.serial]?.selectedStocks || []}
                  onChange={(value) => updateFormData(kol.serial, 'selectedStocks', value)}
                  placeholder="搜尋股票代號或名稱..."
                  style={{ width: '100%', marginTop: '8px' }}
                  showSearch
                  filterOption={false}
                  onSearch={searchStocks}
                  options={stockSearchResults.map(stock => ({
                    value: stock.code,
                    label: `${stock.code} ${stock.name}`
                  }))}
                />
              </Col>

              {/* 熱門話題 */}
              <Col span={12}>
                <Text strong>熱門話題:</Text>
                <Select
                  mode="multiple"
                  value={formData[kol.serial]?.selectedTopics || []}
                  onChange={(value) => updateFormData(kol.serial, 'selectedTopics', value)}
                  placeholder="選擇熱門話題..."
                  style={{ width: '100%', marginTop: '8px' }}
                  options={trendingTopics.map(topic => ({
                    value: topic.id,
                    label: topic.title
                  }))}
                />
              </Col>
            </Row>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ManualPostingPage;
