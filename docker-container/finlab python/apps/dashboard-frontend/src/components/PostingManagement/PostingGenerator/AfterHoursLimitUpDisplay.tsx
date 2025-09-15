import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Space, Typography, Button, message, Spin, Row, Col, Statistic } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  BarChartOutlined,
  DollarOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { PostingManagementAPI } from '../../../services/postingManagementAPI';

const { Title, Text } = Typography;

interface StockData {
  stock_code: string;
  stock_name: string;
  current_price: number;
  yesterday_close: number;
  change_amount: number;
  change_percent: number;
  volume: number;
  industry: string;
  date: string;
  previous_date: string;
  up_days_5: number;
  five_day_change: number;
}

interface AfterHoursLimitUpDisplayProps {
  triggerConfig: any;
  onStockSelect?: (stocks: StockData[]) => void;
}

const AfterHoursLimitUpDisplay: React.FC<AfterHoursLimitUpDisplayProps> = ({ 
  triggerConfig, 
  onStockSelect 
}) => {
  const [loading, setLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [selectedStocks, setSelectedStocks] = useState<StockData[]>([]);

  // 格式化成交金額顯示
  const formatVolumeAmount = (amount: number): string => {
    if (amount >= 100000000) { // 超過1億
      const yi = amount / 100000000;
      return `${yi.toFixed(2)}億`;
    } else if (amount >= 10000) { // 超過1萬
      const wan = amount / 10000;
      return `${wan.toFixed(0)}萬`;
    } else {
      return `${amount.toLocaleString()}`;
    }
  };

  useEffect(() => {
    if (triggerConfig && (triggerConfig.limit_up_after_hours_high_volume || triggerConfig.limit_up_after_hours_low_volume)) {
      fetchStockData();
    }
  }, [triggerConfig]);

  const fetchStockData = async () => {
    setLoading(true);
    try {
      const response = await PostingManagementAPI.getAfterHoursLimitUpStocks(triggerConfig);
      if (response.success) {
        setStockData(response.stocks);
        setSummary(response.summary);
        message.success(`成功獲取 ${response.total_count} 支盤後漲停股票`);
      } else {
        message.error('獲取股票數據失敗');
      }
    } catch (error) {
      console.error('獲取盤後漲停股票數據失敗:', error);
      message.error('獲取股票數據失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleStockSelect = (record: StockData, selected: boolean) => {
    if (selected) {
      setSelectedStocks(prev => [...prev, record]);
    } else {
      setSelectedStocks(prev => prev.filter(stock => stock.stock_code !== record.stock_code));
    }
  };

  const handleSelectAll = () => {
    setSelectedStocks(stockData);
    onStockSelect?.(stockData);
  };

  const handleConfirmSelection = () => {
    onStockSelect?.(selectedStocks);
    message.success(`已選擇 ${selectedStocks.length} 支股票`);
  };

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
      width: 120
    },
    {
      title: '當前價格',
      dataIndex: 'current_price',
      key: 'current_price',
      width: 100,
      render: (price: number) => (
        <Text strong>${price.toFixed(2)}</Text>
      )
    },
    {
      title: '昨日收盤',
      dataIndex: 'yesterday_close',
      key: 'yesterday_close',
      width: 100,
      render: (price: number) => (
        <Text>${price.toFixed(2)}</Text>
      )
    },
    {
      title: '漲跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      width: 100,
      render: (percent: number) => (
        <Text strong style={{ color: '#52c41a' }}>+{percent.toFixed(2)}%</Text>
      )
    },
    {
      title: '成交金額',
      dataIndex: 'volume',
      key: 'volume',
      width: 100,
      render: (volume: number) => (
        <Text>{formatVolumeAmount(volume)}</Text>
      )
    },
    {
      title: '產業',
      dataIndex: 'industry',
      key: 'industry',
      width: 100,
      render: (industry: string) => (
        <Tag color="purple">{industry}</Tag>
      )
    },
    {
      title: '五日漲幅',
      dataIndex: 'five_day_change',
      key: 'five_day_change',
      width: 100,
      render: (change: number) => (
        <Text style={{ color: change > 0 ? '#52c41a' : '#ff4d4f' }}>
          {change > 0 ? '+' : ''}{change.toFixed(2)}%
        </Text>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (record: StockData) => {
        const isSelected = selectedStocks.some(stock => stock.stock_code === record.stock_code);
        return (
          <Button
            type={isSelected ? 'primary' : 'default'}
            size="small"
            onClick={() => handleStockSelect(record, !isSelected)}
          >
            {isSelected ? '已選擇' : '選擇'}
          </Button>
        );
      }
    }
  ];

  const getVolumeTypeText = () => {
    if (triggerConfig.limit_up_after_hours_high_volume) {
      return '高成交量盤後漲停';
    } else if (triggerConfig.limit_up_after_hours_low_volume) {
      return '低成交量盤後漲停';
    }
    return '盤後漲停';
  };

  const getVolumeTypeIcon = () => {
    if (triggerConfig.limit_up_after_hours_high_volume) {
      return <ArrowUpOutlined style={{ color: '#ff4d4f' }} />;
    } else if (triggerConfig.limit_up_after_hours_low_volume) {
      return <ArrowDownOutlined style={{ color: '#1890ff' }} />;
    }
    return <BarChartOutlined />;
  };

  return (
    <div>
      <Card>
        <div style={{ marginBottom: '16px' }}>
          <Space>
            {getVolumeTypeIcon()}
            <Title level={4} style={{ margin: 0 }}>
              {getVolumeTypeText()}股票列表
            </Title>
          </Space>
          <Text type="secondary" style={{ marginLeft: '16px' }}>
            共 {stockData.length} 支股票
          </Text>
        </div>

        {/* 統計摘要 */}
        {stockData.length > 0 && (
          <Row gutter={16} style={{ marginBottom: '16px' }}>
            <Col span={6}>
              <Statistic
                title="總股票數"
                value={stockData.length}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均漲幅"
                value={stockData.reduce((sum, stock) => sum + stock.change_percent, 0) / stockData.length}
                suffix="%"
                prefix={<ArrowUpOutlined />}
                valueStyle={{ color: '#52c41a' }}
                precision={2}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="總成交金額"
                value={stockData.reduce((sum, stock) => sum + stock.volume, 0)}
                prefix={<DollarOutlined />}
                formatter={(value) => formatVolumeAmount(value as number)}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均五日漲幅"
                value={stockData.reduce((sum, stock) => sum + stock.five_day_change, 0) / stockData.length}
                suffix="%"
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#faad14' }}
                precision={2}
              />
            </Col>
          </Row>
        )}

        {/* 操作按鈕 */}
        <div style={{ marginBottom: '16px' }}>
          <Space>
            <Button onClick={handleSelectAll} disabled={loading}>
              全選
            </Button>
            <Button 
              type="primary" 
              onClick={handleConfirmSelection}
              disabled={selectedStocks.length === 0}
            >
              確認選擇 ({selectedStocks.length})
            </Button>
            <Button onClick={fetchStockData} loading={loading}>
              重新載入
            </Button>
          </Space>
        </div>

        {/* 股票表格 */}
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={stockData}
            rowKey="stock_code"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 支股票`
            }}
            scroll={{ x: 1200 }}
            size="small"
          />
        </Spin>
      </Card>
    </div>
  );
};

export default AfterHoursLimitUpDisplay;
