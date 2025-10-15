import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Alert, Tag, Typography, Space, Button, Popconfirm } from 'antd';
import { BarChartOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import PostingManagementAPI from '../../../services/postingManagementAPI';

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
        const mapping = await PostingManagementAPI.getStockMapping();
        setStockMapping(mapping);
      } catch (err) {
        console.error('載入股票映射表失敗:', err);
      }
    };

    loadStockMapping();
  }, []);

  // 載入股票詳細資料
  useEffect(() => {
    if (stockCodes.length === 0) {
      setStockData([]);
      return;
    }

    const loadStockData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await PostingManagementAPI.getStockDetails(stockCodes);
        setStockData(data);
      } catch (err) {
        setError('載入股票資料失敗');
        console.error('載入股票資料失敗:', err);
      } finally {
        setLoading(false);
      }
    };

    loadStockData();
  }, [stockCodes]);

  const columns = [
    {
      title: '股票代號',
      dataIndex: 'stock_code',
      key: 'stock_code',
      width: 100,
      render: (code: string) => (
        <Text strong style={{ color: '#1890ff' }}>{code}</Text>
      )
    },
    {
      title: '股票名稱',
      dataIndex: 'stock_name',
      key: 'stock_name',
      width: 120,
      render: (name: string, record: StockData) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {stockMapping[record.stock_code]?.industry || '未知產業'}
          </Text>
        </Space>
      )
    },
    {
      title: '當前價格',
      dataIndex: 'current_price',
      key: 'current_price',
      width: 100,
      align: 'right' as const,
      render: (price: number) => (
        <Text strong>${price?.toFixed(2) || 'N/A'}</Text>
      )
    },
    {
      title: '漲跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      width: 100,
      align: 'right' as const,
      render: (percent: number) => {
        const isPositive = percent >= 0;
        return (
          <Text style={{ color: isPositive ? '#52c41a' : '#ff4d4f' }}>
            {isPositive ? '+' : ''}{percent?.toFixed(2) || 'N/A'}%
          </Text>
        );
      }
    },
    {
      title: '成交量排名',
      dataIndex: 'volume_rank',
      key: 'volume_rank',
      width: 100,
      align: 'center' as const,
      render: (rank: number) => (
        <Tag color={rank <= 10 ? 'red' : rank <= 50 ? 'orange' : 'default'}>
          #{rank || 'N/A'}
        </Tag>
      )
    },
    {
      title: '五日漲跌',
      dataIndex: 'five_day_change_percent',
      key: 'five_day_change_percent',
      width: 100,
      align: 'right' as const,
      render: (percent: number) => {
        const isPositive = percent >= 0;
        return (
          <Text style={{ color: isPositive ? '#52c41a' : '#ff4d4f' }}>
            {isPositive ? '+' : ''}{percent?.toFixed(2) || 'N/A'}%
          </Text>
        );
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      align: 'center' as const,
      render: (_, record: StockData) => (
        <Space size="small">
          {onStockView && (
            <Button
              type="text"
              icon={<EyeOutlined />}
              size="small"
              onClick={() => onStockView(record.stock_code)}
              title="查看詳情"
            />
          )}
          {onStockRemove && (
            <Popconfirm
              title="確定要移除這支股票嗎？"
              onConfirm={() => onStockRemove(record.stock_code)}
              okText="確定"
              cancelText="取消"
            >
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                size="small"
                title="移除股票"
              />
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  if (stockCodes.length === 0) {
    return (
      <Card>
        <Alert
          message="尚未選擇股票"
          description="請先在觸發器選擇步驟中選擇要分析的股票"
          type="info"
          showIcon
        />
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <BarChartOutlined />
          <span>已選擇股票 ({stockCodes.length} 支)</span>
        </Space>
      }
      extra={
        <Text type="secondary">
          共 {stockCodes.length} 支股票
        </Text>
      }
    >
      {error && (
        <Alert
          message="載入失敗"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={stockData}
          rowKey="stock_code"
          pagination={false}
          size="small"
          scroll={{ x: 800 }}
        />
      </Spin>
    </Card>
  );
};

export default StockFilterDisplay;
