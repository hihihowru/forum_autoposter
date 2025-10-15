import React, { useState } from 'react';
import { Card, Input, Button, Space, Tag, Typography, Row, Col, message, Divider } from 'antd';
import { PlusOutlined, DeleteOutlined, StockOutlined, SearchOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface StockCodeListInputProps {
  value?: string[];
  onChange: (stockCodes: string[]) => void;
  onStockNamesChange?: (stockNames: string[]) => void;
}

const StockCodeListInput: React.FC<StockCodeListInputProps> = ({ value = [], onChange, onStockNamesChange }) => {
  const [inputValue, setInputValue] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  // 預設的熱門股票代號
  const popularStocks = [
    { code: '2330', name: '台積電' },
    { code: '2454', name: '聯發科' },
    { code: '2317', name: '鴻海' },
    { code: '6505', name: '台塑化' },
    { code: '2881', name: '富邦金' },
    { code: '2882', name: '國泰金' },
    { code: '2308', name: '台達電' },
    { code: '3711', name: '日月光投控' },
    { code: '1303', name: '南亞' },
    { code: '2002', name: '中鋼' }
  ];

  // 獲取股票名稱的函數
  const getStockName = (stockCode: string): string => {
    const stockInfo = popularStocks.find(stock => stock.code === stockCode);
    return stockInfo?.name || `股票${stockCode}`;
  };

  // 更新股票名稱
  const updateStockNames = (stockCodes: string[]) => {
    if (onStockNamesChange) {
      const stockNames = stockCodes.map(code => getStockName(code));
      onStockNamesChange(stockNames);
    }
  };

  const handleAddStock = () => {
    const stockCode = inputValue.trim().toUpperCase();
    
    if (!stockCode) {
      message.warning('請輸入股票代號');
      return;
    }

    // 驗證股票代號格式 (4位數字)
    if (!/^\d{4}$/.test(stockCode)) {
      message.error('股票代號格式不正確，請輸入4位數字');
      return;
    }

    if (value.includes(stockCode)) {
      message.warning('該股票代號已存在');
      return;
    }

    const newStockCodes = [...value, stockCode];
    onChange(newStockCodes);
    updateStockNames(newStockCodes);
    setInputValue('');
    message.success(`已添加股票代號: ${stockCode}`);
  };

  const handleRemoveStock = (stockCode: string) => {
    const newStockCodes = value.filter(code => code !== stockCode);
    onChange(newStockCodes);
    updateStockNames(newStockCodes);
    message.success(`已移除股票代號: ${stockCode}`);
  };

  const handleAddPopularStock = (stockCode: string) => {
    if (value.includes(stockCode)) {
      message.warning('該股票代號已存在');
      return;
    }
    const newStockCodes = [...value, stockCode];
    onChange(newStockCodes);
    updateStockNames(newStockCodes);
    message.success(`已添加股票代號: ${stockCode}`);
  };

  const handleBatchAdd = () => {
    const lines = inputValue.split('\n').map(line => line.trim().toUpperCase()).filter(line => line);
    const validCodes: string[] = [];
    const invalidCodes: string[] = [];

    lines.forEach(code => {
      if (/^\d{4}$/.test(code) && !value.includes(code)) {
        validCodes.push(code);
      } else {
        invalidCodes.push(code);
      }
    });

    if (validCodes.length > 0) {
      const newStockCodes = [...value, ...validCodes];
      onChange(newStockCodes);
      updateStockNames(newStockCodes);
      message.success(`已批量添加 ${validCodes.length} 個股票代號`);
    }

    if (invalidCodes.length > 0) {
      message.warning(`以下股票代號格式不正確或已存在: ${invalidCodes.join(', ')}`);
    }

    setInputValue('');
  };

  const handleClearAll = () => {
    onChange([]);
    updateStockNames([]);
    message.success('已清空所有股票代號');
  };

  return (
    <Card title="股票代號列表設定" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          輸入股票代號列表，系統將為每支股票生成對應的分析內容
        </Text>

        {/* 單個添加 */}
        <div>
          <Title level={5}>單個添加</Title>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              placeholder="輸入股票代號 (例: 2330)"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPressEnter={handleAddStock}
              maxLength={4}
              style={{ textTransform: 'uppercase' }}
            />
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={handleAddStock}
            >
              添加
            </Button>
          </Space.Compact>
        </div>

        <Divider />

        {/* 批量添加 */}
        <div>
          <Title level={5}>批量添加</Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            <TextArea
              rows={4}
              placeholder="每行輸入一個股票代號&#10;例：&#10;2330&#10;2454&#10;2317"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <Space>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={handleBatchAdd}
              >
                批量添加
              </Button>
              <Button onClick={() => setInputValue('')}>
                清空輸入
              </Button>
            </Space>
          </Space>
        </div>

        <Divider />

        {/* 熱門股票快速添加 */}
        <div>
          <Title level={5}>熱門股票快速添加</Title>
          <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: '8px' }}>
            點擊下方標籤快速添加熱門股票
          </Text>
          <Space wrap>
            {popularStocks.map((stock) => (
              <Tag
                key={stock.code}
                color="blue"
                style={{ cursor: 'pointer' }}
                onClick={() => handleAddPopularStock(stock.code)}
              >
                <StockOutlined /> {stock.code} {stock.name}
              </Tag>
            ))}
          </Space>
        </div>

        <Divider />

        {/* 已選擇的股票列表 */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <Title level={5} style={{ margin: 0 }}>
              已選擇的股票 ({value.length} 支)
            </Title>
            {value.length > 0 && (
              <Button 
                type="text" 
                danger 
                size="small"
                onClick={handleClearAll}
              >
                清空全部
              </Button>
            )}
          </div>
          
          {value.length === 0 ? (
            <Text type="secondary">尚未選擇任何股票</Text>
          ) : (
            <Space wrap>
              {value.map((stockCode) => (
                <Tag
                  key={stockCode}
                  closable
                  onClose={() => handleRemoveStock(stockCode)}
                  color="green"
                >
                  <StockOutlined /> {stockCode}
                </Tag>
              ))}
            </Space>
          )}
        </div>

        {/* 統計資訊 */}
        {value.length > 0 && (
          <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
            <Row gutter={16}>
              <Col span={8}>
                <Text strong>總股票數</Text>
                <div style={{ fontSize: '18px', color: '#52c41a' }}>{value.length}</div>
              </Col>
              <Col span={8}>
                <Text strong>預估發文數</Text>
                <div style={{ fontSize: '18px', color: '#1890ff' }}>{value.length}</div>
              </Col>
              <Col span={8}>
                <Text strong>預估時間</Text>
                <div style={{ fontSize: '18px', color: '#faad14' }}>{Math.ceil(value.length * 0.5)} 分鐘</div>
              </Col>
            </Row>
          </Card>
        )}
      </Space>
    </Card>
  );
};

export default StockCodeListInput;
