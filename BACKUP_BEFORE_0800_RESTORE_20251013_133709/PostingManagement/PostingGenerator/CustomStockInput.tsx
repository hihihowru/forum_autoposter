import React, { useState } from 'react';
import { Card, Input, Button, Space, Tag, Typography, Row, Col, message, Select, AutoComplete } from 'antd';
import { PlusOutlined, DeleteOutlined, StockOutlined, SearchOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface CustomStockInputProps {
  value?: string[];
  onChange: (stockCodes: string[]) => void;
  onStockNamesChange?: (stockNames: string[]) => void;
}

const CustomStockInput: React.FC<CustomStockInputProps> = ({ value = [], onChange, onStockNamesChange }) => {
  const [inputValue, setInputValue] = useState('');
  const [searchValue, setSearchValue] = useState('');

  // 常見股票選項
  const stockOptions = [
    { value: '2330', label: '2330 台積電' },
    { value: '2454', label: '2454 聯發科' },
    { value: '2317', label: '2317 鴻海' },
    { value: '6505', label: '6505 台塑化' },
    { value: '2881', label: '2881 富邦金' },
    { value: '2882', label: '2882 國泰金' },
    { value: '2308', label: '2308 台達電' },
    { value: '3711', label: '3711 日月光投控' },
    { value: '1303', label: '1303 南亞' },
    { value: '2002', label: '2002 中鋼' },
    { value: '1101', label: '1101 台泥' },
    { value: '1102', label: '1102 亞泥' },
    { value: '1216', label: '1216 統一' },
    { value: '1326', label: '1326 台化' },
    { value: '1402', label: '1402 遠東新' },
    { value: '2207', label: '2207 和泰車' },
    { value: '2303', label: '2303 聯電' },
    { value: '2327', label: '2327 國巨' },
    { value: '2377', label: '2377 微星' },
    { value: '2382', label: '2382 廣達' },
    { value: '2408', label: '2408 南亞科' },
    { value: '2474', label: '2474 可成' },
    { value: '2498', label: '2498 宏達電' },
    { value: '3008', label: '3008 大立光' },
    { value: '3034', label: '3034 聯詠' },
    { value: '3045', label: '3045 台灣大' },
    { value: '3231', label: '3231 緯創' },
    { value: '3443', label: '3443 創意' },
    { value: '3714', label: '3714 富采' },
    { value: '4938', label: '4938 和碩' },
    { value: '5871', label: '5871 中租-KY' },
    { value: '6505', label: '6505 台塑化' },
    { value: '6669', label: '6669 緯穎' },
    { value: '6770', label: '6770 力積電' },
    { value: '8046', label: '8046 南電' },
    { value: '8454', label: '8454 富邦媒' },
    { value: '9910', label: '9910 豐泰' }
  ];

  // 獲取股票名稱的函數
  const getStockName = (stockCode: string): string => {
    const stockInfo = stockOptions.find(option => option.value === stockCode);
    return stockInfo?.label.split(' ')[1] || `股票${stockCode}`;
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

  const handleSelectStock = (stockCode: string) => {
    if (value.includes(stockCode)) {
      message.warning('該股票代號已存在');
      return;
    }
    const newStockCodes = [...value, stockCode];
    onChange(newStockCodes);
    updateStockNames(newStockCodes);
    setSearchValue('');
    message.success(`已添加股票代號: ${stockCode}`);
  };

  const handleClearAll = () => {
    onChange([]);
    updateStockNames([]);
    message.success('已清空所有股票代號');
  };

  // 過濾選項
  const filteredOptions = stockOptions.filter(option =>
    option.label.toLowerCase().includes(searchValue.toLowerCase()) ||
    option.value.includes(searchValue)
  );

  return (
    <Card title="自定義股票選擇" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          手動選擇特定股票進行分析，支援搜尋和直接輸入
        </Text>

        {/* 搜尋添加 */}
        <div>
          <Title level={5}>搜尋添加</Title>
          <AutoComplete
            style={{ width: '100%' }}
            options={filteredOptions}
            value={searchValue}
            onChange={setSearchValue}
            onSelect={handleSelectStock}
            placeholder="搜尋股票代號或名稱..."
            filterOption={(inputValue, option) =>
              option?.label.toLowerCase().includes(inputValue.toLowerCase()) ||
              option?.value.includes(inputValue)
            }
          />
        </div>

        {/* 直接輸入 */}
        <div>
          <Title level={5}>直接輸入</Title>
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
              {value.map((stockCode) => {
                const stockInfo = stockOptions.find(option => option.value === stockCode);
                return (
                  <Tag
                    key={stockCode}
                    closable
                    onClose={() => handleRemoveStock(stockCode)}
                    color="blue"
                  >
                    <StockOutlined /> {stockCode} {stockInfo?.label.split(' ')[1]}
                  </Tag>
                );
              })}
            </Space>
          )}
        </div>

        {/* 統計資訊 */}
        {value.length > 0 && (
          <Card size="small" style={{ backgroundColor: '#e6f7ff', border: '1px solid #91d5ff' }}>
            <Row gutter={16}>
              <Col span={8}>
                <Text strong>總股票數</Text>
                <div style={{ fontSize: '18px', color: '#1890ff' }}>{value.length}</div>
              </Col>
              <Col span={8}>
                <Text strong>預估發文數</Text>
                <div style={{ fontSize: '18px', color: '#52c41a' }}>{value.length}</div>
              </Col>
              <Col span={8}>
                <Text strong>預估時間</Text>
                <div style={{ fontSize: '18px', color: '#faad14' }}>{Math.ceil(value.length * 0.5)} 分鐘</div>
              </Col>
            </Row>
          </Card>
        )}

        {/* 快速選擇建議 */}
        <div>
          <Title level={5}>熱門股票快速選擇</Title>
          <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: '8px' }}>
            點擊下方標籤快速添加熱門股票
          </Text>
          <Space wrap>
            {stockOptions.slice(0, 10).map((stock) => (
              <Tag
                key={stock.value}
                color="green"
                style={{ cursor: 'pointer' }}
                onClick={() => handleSelectStock(stock.value)}
              >
                <StockOutlined /> {stock.value} {stock.label.split(' ')[1]}
              </Tag>
            ))}
          </Space>
        </div>
      </Space>
    </Card>
  );
};

export default CustomStockInput;
