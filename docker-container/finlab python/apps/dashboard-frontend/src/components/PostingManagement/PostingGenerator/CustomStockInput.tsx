import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Space, Tag, Typography, Row, Col, message, AutoComplete } from 'antd';
import { PlusOutlined, StockOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface CustomStockInputProps {
  value?: string[];
  onChange: (stockCodes: string[]) => void;
  onStockNamesChange?: (stockNames: string[]) => void;
}

interface StockMapping {
  [stockCode: string]: {
    company_name: string;
    industry?: string;
  };
}

const CustomStockInput: React.FC<CustomStockInputProps> = ({ value = [], onChange, onStockNamesChange }) => {
  const [inputValue, setInputValue] = useState('');
  const [stockMapping, setStockMapping] = useState<StockMapping>({});
  const [loading, setLoading] = useState(false);

  // 載入 stock_mapping
  useEffect(() => {
    const loadStockMapping = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/stock_mapping.json');
        const data = await response.json();
        if (data.success) {
          setStockMapping(data.data || {});
        }
      } catch (error) {
        console.error('載入股票映射表失敗:', error);
        message.error('無法載入股票資料');
      } finally {
        setLoading(false);
      }
    };
    loadStockMapping();
  }, []);

  // 獲取股票名稱的函數
  const getStockName = (stockCode: string): string => {
    return stockMapping[stockCode]?.company_name || `股票${stockCode}`;
  };

  // 更新股票名稱
  const updateStockNames = (stockCodes: string[]) => {
    if (onStockNamesChange) {
      const stockNames = stockCodes.map(code => getStockName(code));
      onStockNamesChange(stockNames);
    }
  };

  // 處理添加股票（支援搜尋選擇和直接輸入）
  const handleAddStock = (stockCode?: string) => {
    const code = (stockCode || inputValue).trim();

    if (!code) {
      message.warning('請輸入股票代號或搜尋股票名稱');
      return;
    }

    // 驗證股票代號格式 (4位數字)
    if (!/^\d{4}$/.test(code)) {
      message.error('股票代號格式不正確，請輸入4位數字');
      return;
    }

    if (value.includes(code)) {
      message.warning('該股票已存在於列表中');
      return;
    }

    const newStockCodes = [...value, code];
    onChange(newStockCodes);
    updateStockNames(newStockCodes);
    setInputValue('');

    const stockName = getStockName(code);
    message.success(`已添加: ${code} ${stockName}`);
  };

  const handleRemoveStock = (stockCode: string) => {
    const newStockCodes = value.filter(code => code !== stockCode);
    onChange(newStockCodes);
    updateStockNames(newStockCodes);
    message.success(`已移除: ${stockCode}`);
  };

  const handleClearAll = () => {
    onChange([]);
    updateStockNames([]);
    message.success('已清空所有股票');
  };

  // 準備 AutoComplete 選項（過濾已添加的股票）
  const autocompleteOptions = Object.keys(stockMapping)
    .filter(code => {
      if (!inputValue) return false;
      if (value.includes(code)) return false; // 過濾已添加的股票

      const stockInfo = stockMapping[code];
      const searchLower = inputValue.toLowerCase();

      // 搜尋股票代號或名稱
      return (
        code.includes(inputValue) ||
        stockInfo.company_name.toLowerCase().includes(searchLower)
      );
    })
    .slice(0, 20) // 限制顯示數量
    .map(code => ({
      value: code,
      label: `${code} ${stockMapping[code].company_name}`
    }));

  // 熱門股票快速選擇（前20支）
  const popularStocks = Object.keys(stockMapping)
    .slice(0, 20)
    .map(code => ({
      code,
      name: stockMapping[code].company_name
    }));

  return (
    <Card title="自定義股票選擇" size="small" loading={loading}>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          輸入股票代號（如：2330）或搜尋股票名稱（如：台積電）
        </Text>

        {/* 統一的輸入欄位：支援搜尋和直接輸入 */}
        <div>
          <Title level={5}>輸入或搜尋股票</Title>
          <Space.Compact style={{ width: '100%' }}>
            <AutoComplete
              style={{ flex: 1 }}
              options={autocompleteOptions}
              value={inputValue}
              onChange={setInputValue}
              onSelect={handleAddStock}
              placeholder="輸入股票代號或搜尋股票名稱（例：2330 或 台積電）"
              filterOption={false} // 手動過濾
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => handleAddStock()}
            >
              添加
            </Button>
          </Space.Compact>
          <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
            💡 可以直接輸入4位數股票代號，或搜尋股票名稱後選擇
          </Text>
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
                const stockName = getStockName(stockCode);
                return (
                  <Tag
                    key={stockCode}
                    closable
                    onClose={() => handleRemoveStock(stockCode)}
                    color="blue"
                  >
                    <StockOutlined /> {stockCode} {stockName}
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
        {popularStocks.length > 0 && (
          <div>
            <Title level={5}>熱門股票快速選擇</Title>
            <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: '8px' }}>
              點擊下方標籤快速添加熱門股票
            </Text>
            <Space wrap>
              {popularStocks.map((stock) => (
                <Tag
                  key={stock.code}
                  color="green"
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleAddStock(stock.code)}
                >
                  <StockOutlined /> {stock.code} {stock.name}
                </Tag>
              ))}
            </Space>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default CustomStockInput;
