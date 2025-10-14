import React from 'react';
import { Card, Row, Col, Checkbox, Space, Typography, Tag, Divider } from 'antd';
import { 
  ApiOutlined, 
  DatabaseOutlined, 
  SearchOutlined,
  BarChartOutlined,
  DollarOutlined,
  GlobalOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface DataSourceSelection {
  stock_price_api: boolean;
  monthly_revenue_api: boolean;
  financial_report_api: boolean;
  technical_indicators: string[];
  fundamental_data: string[];
  news_sources: string[];
  custom_data: string;
}

interface DataSourceSelectorProps {
  value: DataSourceSelection;
  onChange: (value: DataSourceSelection) => void;
}

const DataSourceSelector: React.FC<DataSourceSelectorProps> = ({ value, onChange }) => {
  const dataSourceOptions = [
    {
      key: 'stock_price_api',
      label: '個股股價 API',
      icon: <ApiOutlined />,
      description: '即時股價、歷史價格、技術指標',
      color: '#52c41a'
    },
    {
      key: 'monthly_revenue_api',
      label: '月營收 API',
      icon: <BarChartOutlined />,
      description: '營收數據、成長率、年增率',
      color: '#1890ff'
    },
    {
      key: 'financial_report_api',
      label: '財報 API',
      icon: <DatabaseOutlined />,
      description: '季報、年報財務數據、EPS',
      color: '#faad14'
    }
  ];

  const technicalIndicators = [
    'MACD', 'RSI', 'KDJ', '布林帶', '移動平均線', '成交量', '威廉指標', 'CCI'
  ];

  const fundamentalData = [
    '營收', '財報', '產業', '市場', 'PE比', 'PB比', 'ROE', '負債比'
  ];

  const newsSources = [
    '工商時報', '經濟日報', '中央社', '鉅亨網', 'MoneyDJ', 'Yahoo財經',
    '中時電子報', '聯合新聞網', '自由時報', '蘋果日報', 'ETtoday', '東森新聞',
    'TVBS', '三立新聞', '民視新聞', '中天新聞', '台視新聞', '華視新聞',
    '非凡新聞', '財訊', '今周刊', '天下雜誌'
  ];

  const handleDataSourceChange = (key: keyof DataSourceSelection, checked: boolean) => {
    onChange({
      ...value,
      [key]: checked
    });
  };

  const handleArrayChange = (key: 'technical_indicators' | 'fundamental_data' | 'news_sources', item: string, checked: boolean) => {
    const currentArray = value[key] || [];
    const newArray = checked 
      ? [...currentArray, item]
      : currentArray.filter(i => i !== item);
    
    onChange({
      ...value,
      [key]: newArray
    });
  };

  const handleCustomDataChange = (customData: string) => {
    onChange({
      ...value,
      custom_data: customData
    });
  };

  const handleSelectAllNewsSources = (checked: boolean) => {
    onChange({
      ...value,
      news_sources: checked ? [...newsSources] : []
    });
  };

  return (
    <div>
      <Title level={4}>選擇數據源</Title>
      <Text type="secondary">
        選擇需要的數據來源，系統將整合這些數據來生成內容
      </Text>

      {/* 主要數據源 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>主要數據源</Title>
        <Row gutter={[16, 16]}>
          {dataSourceOptions.map((option) => (
            <Col xs={24} sm={8} key={option.key}>
              <Card 
                size="small" 
                hoverable
                style={{ 
                  height: '100%',
                  border: value[option.key as keyof DataSourceSelection] ? '2px solid #1890ff' : '1px solid #d9d9d9'
                }}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', color: option.color, marginBottom: '8px' }}>
                      {option.icon}
                    </div>
                    <Checkbox
                      checked={value[option.key as keyof DataSourceSelection] as boolean}
                      onChange={(e) => handleDataSourceChange(option.key as keyof DataSourceSelection, e.target.checked)}
                      style={{ fontSize: '16px', fontWeight: 'bold' }}
                    >
                      {option.label}
                    </Checkbox>
                  </div>
                  <Text type="secondary" style={{ fontSize: '12px', textAlign: 'center' }}>
                    {option.description}
                  </Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 技術指標 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>技術指標</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          選擇需要的技術分析指標
        </Text>
        <div style={{ marginTop: '8px' }}>
          <Space wrap>
            {technicalIndicators.map((indicator) => (
              <Checkbox
                key={indicator}
                checked={value.technical_indicators?.includes(indicator) || false}
                onChange={(e) => handleArrayChange('technical_indicators', indicator, e.target.checked)}
              >
                <Tag color="blue">{indicator}</Tag>
              </Checkbox>
            ))}
          </Space>
        </div>
      </Card>

      {/* 基本面數據 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>基本面數據</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          選擇需要的基本面分析數據
        </Text>
        <div style={{ marginTop: '8px' }}>
          <Space wrap>
            {fundamentalData.map((data) => (
              <Checkbox
                key={data}
                checked={value.fundamental_data?.includes(data) || false}
                onChange={(e) => handleArrayChange('fundamental_data', data, e.target.checked)}
              >
                <Tag color="green">{data}</Tag>
              </Checkbox>
            ))}
          </Space>
        </div>
      </Card>

      {/* 新聞來源 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>新聞來源</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          選擇需要的新聞來源 (共{newsSources.length}個來源)
        </Text>
        <div style={{ marginTop: '8px' }}>
          <Space wrap>
            <Checkbox
              checked={value.news_sources?.length === newsSources.length}
              indeterminate={value.news_sources?.length > 0 && value.news_sources?.length < newsSources.length}
              onChange={(e) => handleSelectAllNewsSources(e.target.checked)}
            >
              <Tag color="red">全選</Tag>
            </Checkbox>
            {newsSources.map((source) => (
              <Checkbox
                key={source}
                checked={value.news_sources?.includes(source) || false}
                onChange={(e) => handleArrayChange('news_sources', source, e.target.checked)}
              >
                <Tag color="orange">{source}</Tag>
              </Checkbox>
            ))}
          </Space>
        </div>
      </Card>

      {/* 自定義數據 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>自定義數據</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          輸入自定義的數據或關鍵字
        </Text>
        <div style={{ marginTop: '8px' }}>
          <input
            type="text"
            placeholder="輸入自定義數據..."
            value={value.custom_data || ''}
            onChange={(e) => handleCustomDataChange(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #d9d9d9',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>
      </Card>

      {/* 選擇摘要 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>數據源摘要</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>主要數據源: </Text>
            <Space wrap>
              {Object.entries(value).slice(0, 3).map(([key, checked]) => {
                if (checked) {
                  const option = dataSourceOptions.find(opt => opt.key === key);
                  return (
                    <Tag key={key} color="blue">
                      {option?.icon} {option?.label}
                    </Tag>
                  );
                }
                return null;
              })}
            </Space>
          </div>
          
          {value.technical_indicators && value.technical_indicators.length > 0 && (
            <div>
              <Text strong>技術指標: </Text>
              <Space wrap>
                {value.technical_indicators.map((indicator) => (
                  <Tag key={indicator} color="blue">{indicator}</Tag>
                ))}
              </Space>
            </div>
          )}
          
          {value.fundamental_data && value.fundamental_data.length > 0 && (
            <div>
              <Text strong>基本面數據: </Text>
              <Space wrap>
                {value.fundamental_data.map((data) => (
                  <Tag key={data} color="green">{data}</Tag>
                ))}
              </Space>
            </div>
          )}
          
          {value.news_sources && value.news_sources.length > 0 && (
            <div>
              <Text strong>新聞來源: </Text>
              <Space wrap>
                {value.news_sources.map((source) => (
                  <Tag key={source} color="orange">{source}</Tag>
                ))}
              </Space>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default DataSourceSelector;
