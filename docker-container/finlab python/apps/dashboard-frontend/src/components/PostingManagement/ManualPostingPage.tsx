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
      setStocks(stocksArray);
      setStockSearchResults(stocksArray); // 初始化搜尋結果
    } catch (error) {
      console.error('載入股票失敗:', error);
      throw error;
    }
  };

  // 載入熱門話題
  const loadTrendingTopics = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/trending`);
      if (!response.ok) throw new Error('載入熱門話題失敗');
      const result = await response.json();
      const topicsData = result.data || [];
      setTrendingTopics(topicsData);
    } catch (error) {
      console.error('載入熱門話題失敗:', error);
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
      const response = await fetch(`${API_BASE}/api/search-stocks-by-keywords?keyword=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('搜尋股票失敗');
      const result = await response.json();
      const data = result.data || [];
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

      const response = await fetch(`${API_BASE}/api/manual-posting`, {
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
                  label: topic.title
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
