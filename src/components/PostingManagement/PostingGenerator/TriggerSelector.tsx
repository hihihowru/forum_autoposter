import React, { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Row,
  Col,
  Select,
  InputNumber,
  Switch,
  Form,
  Input,
  Button,
  Space,
  Divider,
  Alert,
  Tag,
  AutoComplete,
  Spin,
  message,
} from 'antd';
import {
  ArrowUpOutlined,
  FallOutlined,
  BarChartOutlined,
  RiseOutlined,
  FileTextOutlined,
  EditOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { companyInfoService, CompanySearchResult } from '../../../services/companyInfoService';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface TriggerConfig {
  triggerKey: string;
  stockFilter?: string;
  volumeFilter?: string;
  changeThreshold?: number;
  sectorSelection?: string[];
  stockCodes?: string[];
  customStocks?: string[];
}

interface TriggerSelectorProps {
  config: TriggerConfig;
  setConfig: (config: TriggerConfig) => void;
}

const TriggerSelector: React.FC<TriggerSelectorProps> = ({ config, setConfig }) => {
  const [value, setValue] = useState<TriggerConfig>(config);
  const [companySearchResults, setCompanySearchResults] = useState<CompanySearchResult[]>([]);
  const [companySearchLoading, setCompanySearchLoading] = useState(false);

  useEffect(() => {
    setValue(config);
  }, [config]);

  const handleConfigChange = (field: string, val: any) => {
    const newValue = { ...value, [field]: val };
    setValue(newValue);
    setConfig(newValue);
  };

  const handleTriggerConfigChange = (field: string, val: any) => {
    const newTriggerConfig = { ...value.triggerConfig, [field]: val };
    const newValue = { ...value, triggerConfig: newTriggerConfig };
    setValue(newValue);
    setConfig(newValue);
  };

  // 觸發器類型映射
  const triggerTypes = {
    individual: [
      {
        key: 'limit_up_after_hours',
        label: '盤後漲',
        icon: <ArrowUpOutlined />,
        description: '收盤上漲股票分析',
        stockFilter: 'limit_up_stocks',
        volumeFilter: 'high/low/normal'
      },
      {
        key: 'limit_down_after_hours',
        label: '盤後跌',
        icon: <FallOutlined />,
        description: '收盤下跌股票分析',
        stockFilter: 'limit_down_stocks'
      },
      {
        key: 'intraday_limit_up',
        label: '盤中漲停',
        icon: <ArrowUpOutlined />,
        description: '盤中漲停股票分析',
        stockFilter: 'intraday_limit_up_stocks',
        volumeFilter: 'high/low/normal'
      },
      {
        key: 'intraday_limit_down',
        label: '盤中跌停',
        icon: <FallOutlined />,
        description: '盤中跌停股票分析',
        stockFilter: 'intraday_limit_down_stocks',
        volumeFilter: 'high/low/normal'
      },
      {
        key: 'volume_surge',
        label: '成交量暴增',
        icon: <BarChartOutlined />,
        description: '成交量異常放大',
        stockFilter: 'volume_surge_stocks'
      },
      {
        key: 'price_breakthrough',
        label: '技術突破',
        icon: <RiseOutlined />,
        description: '價格突破重要位',
        stockFilter: 'breakthrough_stocks'
      },
      {
        key: 'earnings_surprise',
        label: '財報驚喜',
        icon: <FileTextOutlined />,
        description: '財報超預期',
        stockFilter: 'earnings_surprise_stocks'
      },
      {
        key: 'custom_stocks',
        label: '自定義股票',
        icon: <EditOutlined />,
        description: '手動輸入股票代號',
        stockFilter: 'custom_stocks'
      }
    ],
    batch: [
      {
        key: 'sector_selection',
        label: '產業選擇',
        icon: <ThunderboltOutlined />,
        description: '選擇特定產業進行分析',
        stockFilter: 'sector_stocks'
      },
      {
        key: 'market_overview',
        label: '市場概況',
        icon: <BarChartOutlined />,
        description: '整體市場分析',
        stockFilter: 'market_stocks'
      },
      {
        key: 'trending_topics',
        label: '熱門話題',
        icon: <ClockCircleOutlined />,
        description: '基於熱門話題生成內容',
        stockFilter: 'trending_stocks'
      }
    ]
  };

  // 檢查是否需要顯示漲跌幅設定
  const shouldShowChangeThreshold = () => {
    return value.triggerConfig?.triggerKey === 'limit_up_after_hours' || 
           value.triggerConfig?.triggerKey === 'limit_down_after_hours' ||
           value.triggerConfig?.triggerKey === 'intraday_limit_up' ||
           value.triggerConfig?.triggerKey === 'intraday_limit_down';
  };

  // 檢查是否需要顯示產業選擇設定
  const shouldShowSectorSelection = () => {
    return value.triggerConfig?.triggerKey === 'sector_selection';
  };

  // 處理公司搜尋
  const handleCompanySearch = async (searchValue: string) => {
    if (!searchValue || searchValue.length < 2) {
      setCompanySearchResults([]);
      return;
    }

    setCompanySearchLoading(true);
    try {
      const results = await companyInfoService.smartSearch(searchValue);
      setCompanySearchResults(results);
    } catch (error) {
      console.error('公司搜尋失敗:', error);
      message.error('公司搜尋失敗');
    } finally {
      setCompanySearchLoading(false);
    }
  };

  // 處理公司選擇
  const handleCompanySelect = (company: CompanySearchResult) => {
    // 將選中的公司添加到股票代號列表
    const currentCodes = value.stock_codes || [];
    if (!currentCodes.includes(company.stock_code)) {
      const newCodes = [...currentCodes, company.stock_code];
      handleConfigChange('stock_codes', newCodes);
    }
  };

  // 移除股票代號
  const removeStockCode = (codeToRemove: string) => {
    const currentCodes = value.stock_codes || [];
    const newCodes = currentCodes.filter(code => code !== codeToRemove);
    handleConfigChange('stock_codes', newCodes);
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={4}>
          <SettingOutlined style={{ marginRight: 8 }} />
          觸發器選擇
        </Title>
        <Paragraph type="secondary">
          選擇內容觸發器，決定發文的觸發條件和股票篩選邏輯
        </Paragraph>

        <Row gutter={24}>
          <Col span={12}>
            <Card title="個別觸發器" size="small">
              <Form.Item label="觸發器類型">
                <Select
                  value={value.triggerConfig?.triggerKey}
                  onChange={(val) => handleTriggerConfigChange('triggerKey', val)}
                  placeholder="選擇觸發器類型"
                  style={{ width: '100%' }}
                >
                  {triggerTypes.individual.map(trigger => (
                    <Option key={trigger.key} value={trigger.key}>
                      <Space>
                        {trigger.icon}
                        {trigger.label}
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              {value.triggerConfig?.triggerKey && (
                <Alert
                  message={triggerTypes.individual.find(t => t.key === value.triggerConfig?.triggerKey)?.description}
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}

              {shouldShowChangeThreshold() && (
                <Form.Item label="漲跌幅閾值 (%)">
                  <InputNumber
                    value={value.triggerConfig?.changeThreshold}
                    onChange={(val) => handleTriggerConfigChange('changeThreshold', val)}
                    min={0}
                    max={20}
                    step={0.1}
                    style={{ width: '100%' }}
                    placeholder="設定漲跌幅閾值"
                  />
                </Form.Item>
              )}

              {shouldShowSectorSelection() && (
                <Form.Item label="產業選擇">
                  <Select
                    mode="multiple"
                    value={value.triggerConfig?.sectorSelection}
                    onChange={(val) => handleTriggerConfigChange('sectorSelection', val)}
                    placeholder="選擇產業"
                    style={{ width: '100%' }}
                  >
                    <Option value="technology">科技業</Option>
                    <Option value="finance">金融業</Option>
                    <Option value="manufacturing">製造業</Option>
                    <Option value="healthcare">醫療保健</Option>
                    <Option value="energy">能源業</Option>
                    <Option value="consumer">消費品</Option>
                  </Select>
                </Form.Item>
              )}

              {value.triggerConfig?.triggerKey === 'custom_stocks' && (
                <Form.Item label="自定義股票代號">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <AutoComplete
                      options={companySearchResults.map(company => ({
                        value: company.stock_code,
                        label: `${company.stock_code} - ${company.company_name}`
                      }))}
                      onSearch={handleCompanySearch}
                      onSelect={handleCompanySelect}
                      placeholder="搜尋股票代號或公司名稱"
                      style={{ width: '100%' }}
                    >
                      <Input.Search
                        loading={companySearchLoading}
                        placeholder="搜尋股票代號或公司名稱"
                      />
                    </AutoComplete>
                    
                    {value.stock_codes && value.stock_codes.length > 0 && (
                      <div>
                        <Text strong>已選擇的股票：</Text>
                        <div style={{ marginTop: 8 }}>
                          {value.stock_codes.map(code => (
                            <Tag
                              key={code}
                              closable
                              onClose={() => removeStockCode(code)}
                              style={{ marginBottom: 4 }}
                            >
                              {code}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    )}
                  </Space>
                </Form.Item>
              )}
            </Card>
          </Col>

          <Col span={12}>
            <Card title="批量觸發器" size="small">
              <Form.Item label="批量觸發器類型">
                <Select
                  value={value.triggerConfig?.triggerKey}
                  onChange={(val) => handleTriggerConfigChange('triggerKey', val)}
                  placeholder="選擇批量觸發器類型"
                  style={{ width: '100%' }}
                >
                  {triggerTypes.batch.map(trigger => (
                    <Option key={trigger.key} value={trigger.key}>
                      <Space>
                        {trigger.icon}
                        {trigger.label}
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              {value.triggerConfig?.triggerKey && (
                <Alert
                  message={triggerTypes.batch.find(t => t.key === value.triggerConfig?.triggerKey)?.description}
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
            </Card>
          </Col>
        </Row>

        <Divider />

        <Row gutter={24}>
          <Col span={24}>
            <Card title="觸發器設定摘要" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>觸發器類型：</Text>
                  <Text code>
                    {value.triggerConfig?.triggerKey || '未選擇'}
                  </Text>
                </div>
                
                {value.triggerConfig?.changeThreshold && (
                  <div>
                    <Text strong>漲跌幅閾值：</Text>
                    <Text code>{value.triggerConfig.changeThreshold}%</Text>
                  </div>
                )}
                
                {value.triggerConfig?.sectorSelection && value.triggerConfig.sectorSelection.length > 0 && (
                  <div>
                    <Text strong>選擇產業：</Text>
                    {value.triggerConfig.sectorSelection.map(sector => (
                      <Tag key={sector} style={{ marginLeft: 4 }}>
                        {sector}
                      </Tag>
                    ))}
                  </div>
                )}
                
                {value.stock_codes && value.stock_codes.length > 0 && (
                  <div>
                    <Text strong>自定義股票：</Text>
                    {value.stock_codes.map(code => (
                      <Tag key={code} style={{ marginLeft: 4 }}>
                        {code}
                      </Tag>
                    ))}
                  </div>
                )}
              </Space>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default TriggerSelector;
