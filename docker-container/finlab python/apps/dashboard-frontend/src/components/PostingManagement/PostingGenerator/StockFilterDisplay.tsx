import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Alert, Tag, Typography, Space, Button, Popconfirm } from 'antd';
import { BarChartOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface StockData {
  stock_code: string;
  stock_name: string;
  industry: string;
  current_price: number;
  change_percent: number;
  transaction_amount: number;
  volume_rank: number;
  five_day_up_days: number;
  five_day_change_percent: number;
}

interface StockFilterDisplayProps {
  stockCodes: string[];
  onStockRemove?: (stockCode: string) => void;
  onStockView?: (stockCode: string) => void;
}

const StockFilterDisplay: React.FC<StockFilterDisplayProps> = ({
  stockCodes,
  onStockRemove,
  onStockView
}) => {
  const [loading, setLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [stockMapping, setStockMapping] = useState<any>({});

  // 載入股票映射表
  useEffect(() => {
    const loadStockMapping = async () => {
      try {
        const response = await fetch('/stock_mapping.json');
        const mapping = await response.json();
        setStockMapping(mapping);
        console.log('📋 [股票映射] 載入成功:', Object.keys(mapping).length, '支股票');
      } catch (error) {
        console.error('❌ [股票映射] 載入失敗:', error);
      }
    };
    
    loadStockMapping();
  }, []);

  useEffect(() => {
    if (stockCodes.length > 0 && Object.keys(stockMapping).length > 0) {
      fetchStockData();
    } else if (stockCodes.length === 0) {
      setStockData([]);
    }
  }, [stockCodes, stockMapping]);

  const fetchStockData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 這裡可以調用多個 API 來獲取完整的股票數據
      const promises = stockCodes.map(async (code) => {
        // 獲取基本 OHLC 數據
        const ohlcResponse = await fetch(`${import.meta.env.DEV ? 'http://localhost:8005' : import.meta.env.VITE_RAILWAY_URL || 'https://forumautoposter-production.up.railway.app'}/get_ohlc?stock_id=${code}`);
        const ohlcData = await ohlcResponse.json();
        
        if (ohlcData.error) {
          throw new Error(ohlcData.error);
        }
        
        const latest = ohlcData[ohlcData.length - 1];
        
        // 從股票映射表獲取真實股票名稱和產業
        const stockInfo = stockMapping[code] || {};
        const stockName = stockInfo.company_name || `股票${code}`;
        const industry = stockInfo.industry || '未知產業';
        
        // 模擬其他數據（實際應該調用相應的 API）
        return {
          stock_code: code,
          stock_name: stockName,
          industry: industry,
          current_price: latest.close,
          change_percent: ((latest.close - latest.open) / latest.open) * 100,
          transaction_amount: latest.volume * latest.close, // 成交金額
          volume_rank: Math.floor(Math.random() * 100) + 1, // 成交量排名（模擬）
          five_day_up_days: Math.floor(Math.random() * 6), // 五日上漲天數（模擬）
          five_day_change_percent: (Math.random() - 0.5) * 20 // 五日漲跌幅（模擬）
        };
      });
      
      const results = await Promise.all(promises);
      setStockData(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : '獲取數據失敗');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '股票代號',
      dataIndex: 'stock_code',
      key: 'stock_code',
      render: (code: string) => (
        <Tag color="blue" style={{ fontSize: '14px', padding: '4px 8px' }}>
          {code}
        </Tag>
      )
    },
    {
      title: '股票名稱',
      dataIndex: 'stock_name',
      key: 'stock_name',
      render: (name: string) => <Text strong>{name}</Text>
    },
    {
      title: '產業類別',
      dataIndex: 'industry',
      key: 'industry',
      render: (industry: string) => (
        <Tag color="green">{industry}</Tag>
      )
    },
    {
      title: '當前價格',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: number) => `$${price.toFixed(2)}`
    },
    {
      title: '漲跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      render: (percent: number) => (
        <Tag color={percent >= 0 ? 'green' : 'red'}>
          {percent >= 0 ? '+' : ''}{percent.toFixed(2)}%
        </Tag>
      )
    },
    {
      title: '成交金額',
      dataIndex: 'transaction_amount',
      key: 'transaction_amount',
      render: (amount: number) => `$${(amount / 1000000).toFixed(1)}M`
    },
    {
      title: '成交量排名',
      dataIndex: 'volume_rank',
      key: 'volume_rank',
      render: (rank: number) => `#${rank}`
    },
    {
      title: '五日上漲天數',
      dataIndex: 'five_day_up_days',
      key: 'five_day_up_days',
      render: (days: number) => `${days}/5`
    },
    {
      title: '五日漲跌幅',
      dataIndex: 'five_day_change_percent',
      key: 'five_day_change_percent',
      render: (percent: number) => (
        <Tag color={percent >= 0 ? 'green' : 'red'}>
          {percent >= 0 ? '+' : ''}{percent.toFixed(2)}%
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record: StockData) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => onStockView?.(record.stock_code)}
            size="small"
          >
            查看
          </Button>
          <Popconfirm
            title="確定要移除這支股票嗎？"
            onConfirm={() => onStockRemove?.(record.stock_code)}
            okText="確定"
            cancelText="取消"
          >
            <Button
              type="link"
              icon={<DeleteOutlined />}
              danger
              size="small"
            >
              移除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  if (stockCodes.length === 0) {
    return null;
  }

  return (
    <Card 
      title={
        <Space>
          <BarChartOutlined style={{ color: '#1890ff' }} />
          <span>股票篩選列表</span>
          <Tag color="blue">{stockCodes.length} 支股票</Tag>
        </Space>
      }
      size="small"
    >
      {error && (
        <Alert
          message="數據獲取錯誤"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      <Spin spinning={loading}>
        <Table
          dataSource={stockData}
          columns={columns}
          pagination={false}
          size="small"
          rowKey="stock_code"
          scroll={{ x: 1200 }}
        />
      </Spin>
    </Card>
  );
};

export default StockFilterDisplay;
