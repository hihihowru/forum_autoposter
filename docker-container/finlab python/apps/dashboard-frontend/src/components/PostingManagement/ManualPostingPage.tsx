import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Input, Button, Select, message, Space, Typography, Spin, Table, Tag } from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  UserOutlined,
  EditOutlined,
  CloseOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;

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
  stock_ids?: string[];  // Related stock codes from trending topic
}


interface ManualPostingFormData {
  title: string;
  content: string;
  selectedStocks: string[];
  selectedTopics: string[];
}

const ManualPostingPage: React.FC = () => {
  // 狀態管理
  const [kols, setKols] = useState<KOLInfo[]>([]);
  const [stocks, setStocks] = useState<StockInfo[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<TopicInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<{ [key: string]: boolean }>({});
  const [stockSearchResults, setStockSearchResults] = useState<StockInfo[]>([]);

  // 表單狀態
  const [formData, setFormData] = useState<{ [key: string]: ManualPostingFormData }>({});

  // 當前展開的 KOL (只允許一個展開)
  const [expandedKolSerial, setExpandedKolSerial] = useState<string | null>(null);

  // API 基礎 URL - 使用統一的 API 配置
  const API_BASE = import.meta.env.DEV ? 'http://localhost:8001' : 'https://forumautoposter-production.up.railway.app';

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
        loadTrendingTopics()
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
      const response = await fetch(`${API_BASE}/api/kol/list`);
      if (!response.ok) throw new Error('載入 KOL 失敗');
      const result = await response.json();

      // 🔥 FIX: Extract data array from response object
      const kolsData = result.data || [];
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
      const response = await fetch(`${API_BASE}/api/stock_mapping.json`);
      if (!response.ok) throw new Error('載入股票失敗');
      const result = await response.json();
      // 轉換 stock_mapping 格式為陣列
      const stocksArray = Object.entries(result.data || {}).map(([code, info]: [string, any]) => ({
        code,
        name: info.company_name || code,
        industry: info.industry || '未分類'
      }));

      // 🔥 FIX: Add TWA00 大盤 at the beginning
      const allStocks = [
        { code: 'TWA00', name: '台灣加權指數 (大盤)', industry: '指數' },
        ...stocksArray
      ];

      setStocks(allStocks);
      setStockSearchResults(allStocks); // 初始化搜尋結果包含所有股票
      console.log(`✅ Loaded ${allStocks.length} stocks (including TWA00)`);
    } catch (error) {
      console.error('載入股票失敗:', error);
      throw error;
    }
  };

  // 載入熱門話題
  const loadTrendingTopics = async () => {
    try {
      // 🔥 FIX: Use Railway backend's trending API (includes stock_ids)
      const response = await fetch(`${API_BASE}/api/trending?limit=20`);
      if (!response.ok) {
        console.warn('Trending API failed, using empty list');
        setTrendingTopics([]);
        return;
      }
      const result = await response.json();
      const topicsArray = result.topics || result.data || [];

      // Transform to expected format with stock_ids
      const formattedTopics = topicsArray.map((topic: any) => ({
        id: topic.id || topic.topicId || topic.topic_id || '',
        title: topic.title || topic.name || '',
        name: topic.name || topic.title || '',
        stock_ids: topic.stock_ids || []  // Include related stock codes
      }));

      setTrendingTopics(formattedTopics);
      console.log(`✅ Loaded ${formattedTopics.length} trending topics`);

      // Log topics with stock_ids for debugging
      formattedTopics.forEach((topic: TopicInfo) => {
        if (topic.stock_ids && topic.stock_ids.length > 0) {
          console.log(`   📊 ${topic.title} → Stocks: ${topic.stock_ids.join(', ')}`);
        }
      });
    } catch (error) {
      console.error('載入熱門話題失敗:', error);
      setTrendingTopics([]); // Set empty array instead of throwing
    }
  };


  // 搜尋股票
  const searchStocks = async (query: string) => {
    // 🔥 FIX: If empty query, show all stocks
    if (!query || query.trim().length === 0) {
      setStockSearchResults(stocks);
      return stocks;
    }

    const trimmedQuery = query.trim().toLowerCase();

    // 🔥 FIX: Use local search for better UX (immediate results)
    // Search by code or name
    const localResults = stocks.filter(stock =>
      stock.code.toLowerCase().includes(trimmedQuery) ||
      stock.name.toLowerCase().includes(trimmedQuery)
    );

    setStockSearchResults(localResults);
    console.log(`🔍 Local search: "${query}" → ${localResults.length} results`);

    // 🔥 Optional: Try API search in background (for more results)
    if (trimmedQuery.length >= 2) {
      try {
        const response = await fetch(`${API_BASE}/api/search-stocks-by-keywords?keyword=${encodeURIComponent(trimmedQuery)}`);

        if (response.ok) {
          const result = await response.json();
          const apiResults = result.data || [];

          // Merge API results with local results (deduplicate)
          const mergedResults = [...localResults];
          apiResults.forEach((apiStock: StockInfo) => {
            if (!mergedResults.some(s => s.code === apiStock.code)) {
              mergedResults.push(apiStock);
            }
          });

          setStockSearchResults(mergedResults);
          console.log(`✅ API search: "${query}" → ${mergedResults.length} total results`);
        }
      } catch (error) {
        // Keep local results if API fails
        console.warn('API search failed, using local results:', error);
      }
    }

    return localResults;
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

      // 🔥 FIX: Format commodityTags correctly for CMoney API
      const commodityTags = data.selectedStocks.map(stockCode => ({
        type: "Stock",
        key: stockCode,
        bullOrBear: 0  // 0 = neutral, 1 = bullish, -1 = bearish
      }));

      // 🔥 FIX: Format communityTopic correctly (single object, use first selected)
      const communityTopic = data.selectedTopics.length > 0
        ? { id: data.selectedTopics[0] }
        : undefined;

      console.log('📤 Step 1: Creating draft post...');

      // Step 1: Create draft post
      const draftResponse = await fetch(`${API_BASE}/api/manual-posting`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          kol_serial: parseInt(kolSerial),
          title: data.title,
          content: data.content,
          text: data.content,  // CMoney uses "text" field
          commodityTags: commodityTags.length > 0 ? commodityTags : undefined,
          communityTopic: communityTopic
        })
      });

      const draftResult = await draftResponse.json();

      if (!draftResult.success || !draftResult.post_id) {
        message.error(`建立草稿失敗: ${draftResult.message || '未知錯誤'}`);
        return;
      }

      console.log(`✅ Draft created: ${draftResult.post_id}`);
      message.loading({ content: '正在發布到 CMoney...', key: 'publishing', duration: 0 });

      // Step 2: Publish draft to CMoney
      console.log('📤 Step 2: Publishing to CMoney...');
      const publishResponse = await fetch(`${API_BASE}/api/posts/${draftResult.post_id}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const publishResult = await publishResponse.json();

      message.destroy('publishing');

      if (publishResult.success && publishResult.post_url) {
        message.success({
          content: (
            <div>
              <div>發文成功！</div>
              <a href={publishResult.post_url} target="_blank" rel="noopener noreferrer">
                查看文章
              </a>
            </div>
          ),
          duration: 5
        });
        clearForm(kolSerial);
        console.log(`✅ Published to CMoney: ${publishResult.post_url}`);
      } else {
        message.error(`發布到 CMoney 失敗: ${publishResult.error || publishResult.message || '未知錯誤'}`);
        console.error('Publish error:', publishResult);
      }
    } catch (error) {
      console.error('提交發文失敗:', error);
      message.destroy('publishing');
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

  // 切換 KOL 表單展開/收起
  const toggleKolForm = (kolSerial: string) => {
    if (expandedKolSerial === kolSerial) {
      setExpandedKolSerial(null); // 收起
    } else {
      setExpandedKolSerial(kolSerial); // 展開
    }
  };

  // 獲取人設標籤顏色
  const getPersonaColor = (persona: string) => {
    const colorMap: { [key: string]: string } = {
      '技術派': 'blue',
      '總經派': 'green',
      '消息派': 'orange',
      '散戶派': 'purple',
      '地方派': 'cyan',
      '八卦派': 'magenta',
      '爆料派': 'red',
      '新聞派': 'geekblue',
      '數據派': 'lime',
      '短線派': 'gold',
      '價值派': 'volcano'
    };
    return colorMap[persona] || 'default';
  };


  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>載入中...</div>
      </div>
    );
  }

  // 表格列定義
  const columns = [
    {
      title: 'Serial',
      dataIndex: 'serial',
      key: 'serial',
      width: 80,
      render: (serial: string) => <Text strong>#{serial}</Text>
    },
    {
      title: 'KOL 名稱',
      dataIndex: 'nickname',
      key: 'nickname',
      render: (nickname: string) => (
        <Space>
          <UserOutlined />
          <Text>{nickname}</Text>
        </Space>
      )
    },
    {
      title: '人設',
      dataIndex: 'persona',
      key: 'persona',
      render: (persona: string) => (
        <Tag color={getPersonaColor(persona)}>{persona}</Tag>
      )
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'default'}>
          {status === 'active' ? '啟用' : '停用'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: KOLInfo) => (
        <Button
          type={expandedKolSerial === record.serial ? 'default' : 'primary'}
          icon={expandedKolSerial === record.serial ? <CloseOutlined /> : <EditOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            toggleKolForm(record.serial);
          }}
        >
          {expandedKolSerial === record.serial ? '收起' : '發文'}
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 頁面標題 */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <SendOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
          手動發文管理
        </Title>
        <Text type="secondary">
          點擊「發文」按鈕展開編輯區，類似水軍操作工具
        </Text>
      </Card>

      {/* KOL 列表表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={kols}
          rowKey="serial"
          pagination={{ pageSize: 10, showSizeChanger: true }}
          onRow={(record) => ({
            onClick: () => toggleKolForm(record.serial),
            style: {
              cursor: 'pointer',
              background: expandedKolSerial === record.serial ? '#e6f7ff' : undefined
            }
          })}
        />
      </Card>

      {/* 展開的發文表單 */}
      {expandedKolSerial && formData[expandedKolSerial] && (
        <Card
          style={{ marginTop: '24px' }}
          title={
            <Space>
              <EditOutlined style={{ color: '#1890ff' }} />
              <Text strong>
                {kols.find(k => k.serial === expandedKolSerial)?.nickname || ''}
                {' '}的發文編輯區
              </Text>
              <Tag color={getPersonaColor(kols.find(k => k.serial === expandedKolSerial)?.persona || '')}>
                {kols.find(k => k.serial === expandedKolSerial)?.persona || ''}
              </Tag>
            </Space>
          }
          extra={
            <Space>
              <Button
                type="primary"
                icon={<SendOutlined />}
                loading={submitting[expandedKolSerial]}
                onClick={() => submitPost(expandedKolSerial)}
                size="large"
              >
                送出發文
              </Button>
              <Button
                icon={<ClearOutlined />}
                onClick={() => clearForm(expandedKolSerial)}
              >
                清空
              </Button>
              <Button
                icon={<CloseOutlined />}
                onClick={() => setExpandedKolSerial(null)}
              >
                收起
              </Button>
            </Space>
          }
        >
          <Row gutter={[16, 16]}>
            {/* 標題 */}
            <Col span={24}>
              <Text strong style={{ fontSize: '14px' }}>標題:</Text>
              <Input
                value={formData[expandedKolSerial]?.title || ''}
                onChange={(e) => updateFormData(expandedKolSerial, 'title', e.target.value)}
                placeholder="輸入標題..."
                size="large"
                style={{ marginTop: '8px' }}
              />
            </Col>

            {/* 內容 */}
            <Col span={24}>
              <Text strong style={{ fontSize: '14px' }}>內容:</Text>
              <TextArea
                value={formData[expandedKolSerial]?.content || ''}
                onChange={(e) => updateFormData(expandedKolSerial, 'content', e.target.value)}
                placeholder="輸入內容..."
                rows={6}
                style={{ marginTop: '8px' }}
              />
            </Col>

            {/* 股票標籤 */}
            <Col span={12}>
              <Text strong style={{ fontSize: '14px' }}>股票標籤:</Text>
              <Select
                mode="multiple"
                value={formData[expandedKolSerial]?.selectedStocks || []}
                onChange={(value) => updateFormData(expandedKolSerial, 'selectedStocks', value)}
                placeholder="搜尋股票代號或名稱..."
                style={{ width: '100%', marginTop: '8px' }}
                size="large"
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
              <Text strong style={{ fontSize: '14px' }}>熱門話題:</Text>
              <Select
                mode="multiple"
                value={formData[expandedKolSerial]?.selectedTopics || []}
                onChange={(value) => updateFormData(expandedKolSerial, 'selectedTopics', value)}
                placeholder="選擇熱門話題..."
                style={{ width: '100%', marginTop: '8px' }}
                size="large"
                options={trendingTopics.map(topic => ({
                  value: topic.id,
                  label: topic.stock_ids && topic.stock_ids.length > 0
                    ? `${topic.title} (${topic.stock_ids.join(', ')})`
                    : topic.title
                }))}
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
};

export default ManualPostingPage;
