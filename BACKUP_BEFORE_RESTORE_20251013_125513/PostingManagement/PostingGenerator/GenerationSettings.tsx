import React from 'react';
import { Card, Typography, Radio, Space, InputNumber, Select, Divider, Tag, Row, Col } from 'antd';
import { OneToOneOutlined, ClusterOutlined, FileTextOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

interface GenerationSettings {
  post_mode: 'one_to_one' | 'one_to_many';
  content_length: 'short' | 'medium' | 'long' | 'extended' | 'comprehensive' | 'thorough';
  max_stocks_per_post: number;
  content_style: 'technical' | 'casual' | 'professional' | 'humorous';
  include_analysis_depth: 'basic' | 'detailed' | 'comprehensive';
  max_words: number;
  include_charts: boolean;
  include_risk_warning: boolean;
}

interface GenerationSettingsProps {
  value: GenerationSettings;
  onChange: (value: GenerationSettings) => void;
}

const GenerationSettings: React.FC<GenerationSettingsProps> = ({ value, onChange }) => {
  const handlePostModeChange = (mode: 'one_to_one' | 'one_to_many') => {
    onChange({
      ...value,
      post_mode: mode,
      max_stocks_per_post: mode === 'one_to_one' ? 1 : value.max_stocks_per_post
    });
  };

  const handleContentLengthChange = (length: 'short' | 'medium' | 'long' | 'extended' | 'comprehensive' | 'thorough') => {
    const maxWordsMap = {
      'short': 100,
      'medium': 200,
      'long': 400,
      'extended': 600,
      'comprehensive': 800,
      'thorough': 1000
    };
    
    onChange({
      ...value,
      content_length: length,
      max_words: maxWordsMap[length]
    });
  };

  const handleMaxStocksChange = (maxStocks: number) => {
    onChange({
      ...value,
      max_stocks_per_post: maxStocks
    });
  };

  const handleContentStyleChange = (style: 'technical' | 'casual' | 'professional' | 'humorous') => {
    onChange({
      ...value,
      content_style: style
    });
  };

  const handleAnalysisDepthChange = (depth: 'basic' | 'detailed' | 'comprehensive') => {
    onChange({
      ...value,
      include_analysis_depth: depth
    });
  };

  const handleMaxWordsChange = (maxWords: number | null) => {
    onChange({
      ...value,
      max_words: maxWords || 200
    });
  };

  const handleIncludeChartsChange = (includeCharts: boolean) => {
    onChange({
      ...value,
      include_charts: includeCharts
    });
  };

  const handleIncludeRiskWarningChange = (includeRiskWarning: boolean) => {
    onChange({
      ...value,
      include_risk_warning: includeRiskWarning
    });
  };

  const getPostModeDescription = (mode: string) => {
    switch (mode) {
      case 'one_to_one':
        return '一篇貼文專注分析一檔股票，內容詳細深入';
      case 'one_to_many':
        return '一篇貼文分析多檔股票，內容簡潔概要';
      default:
        return '';
    }
  };

  const getContentLengthDescription = (length: string) => {
    switch (length) {
      case 'short':
        return '簡短分析，約100字，適合快速閱讀';
      case 'medium':
        return '中等長度，約200字，平衡詳細度和可讀性';
      case 'long':
        return '詳細分析，約400字，包含完整技術分析';
      case 'extended':
        return '深度分析，約600字，全面技術與基本面分析';
      case 'comprehensive':
        return '完整分析，約800字，包含詳細市場解讀';
      case 'thorough':
        return '全面分析，約1000字，深度市場洞察與投資建議';
      default:
        return '';
    }
  };

  const getStyleDescription = (style: string) => {
    switch (style) {
      case 'technical':
        return '專業技術分析風格，使用專業術語';
      case 'casual':
        return '輕鬆隨性風格，貼近一般投資人';
      case 'professional':
        return '專業商務風格，適合機構投資人';
      case 'humorous':
        return '幽默風趣風格，增加閱讀趣味性';
      default:
        return '';
    }
  };

  return (
    <Card title="生成設定" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          配置內容生成的參數和品質要求，不同模式會影響prompting策略
        </Text>

        {/* 貼文模式選擇 */}
        <div>
          <Title level={5}>貼文模式</Title>
          <Radio.Group
            value={value.post_mode}
            onChange={(e) => handlePostModeChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="one_to_one" style={{ width: '100%' }}>
                <Space>
                  <OneToOneOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>一對一模式</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getPostModeDescription('one_to_one')}
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="one_to_many" style={{ width: '100%' }}>
                <Space>
                  <ClusterOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>一對多模式</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getPostModeDescription('one_to_many')}
                    </Text>
                  </Space>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 一對多模式的額外設定 */}
        {value.post_mode === 'one_to_many' && (
          <div>
            <Title level={5}>多股票設定</Title>
            <Space>
              <Text>最多分析</Text>
              <Select
                value={value.max_stocks_per_post}
                onChange={handleMaxStocksChange}
                style={{ width: '100px' }}
              >
                <Option value={2}>2檔</Option>
                <Option value={3}>3檔</Option>
                <Option value={5}>5檔</Option>
                <Option value={10}>10檔</Option>
              </Select>
              <Text>股票</Text>
            </Space>
            <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
              一對多模式下，每檔股票的分析會相對簡潔，建議不超過5檔
            </Text>
          </div>
        )}

        {/* 內容長度設定 */}
        <div>
          <Title level={5}>內容長度</Title>
          <Radio.Group
            value={value.content_length}
            onChange={(e) => handleContentLengthChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="short" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>簡短 (約100字)</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getContentLengthDescription('short')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="medium" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>中等 (約200字)</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getContentLengthDescription('medium')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="long" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>詳細 (約400字)</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getContentLengthDescription('long')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="extended" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>深度 (約600字)</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getContentLengthDescription('extended')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="comprehensive" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>完整 (約800字)</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getContentLengthDescription('comprehensive')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="thorough" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>全面 (約1000字)</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getContentLengthDescription('thorough')}
                  </Text>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>

          {/* 自定義字數 */}
          <div style={{ marginTop: '12px' }}>
            <Space>
              <Text>自定義字數：</Text>
              <InputNumber
                min={50}
                max={1500}
                value={value.max_words}
                onChange={handleMaxWordsChange}
                style={{ width: '100px' }}
                addonAfter="字"
              />
            </Space>
          </div>
        </div>

        <Divider />

        {/* 內容風格設定 */}
        <div>
          <Title level={5}>內容風格</Title>
          <Radio.Group
            value={value.content_style}
            onChange={(e) => handleContentStyleChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Radio value="technical" style={{ width: '100%' }}>
                  <Space direction="vertical" size={0}>
                    <Text strong>技術分析</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getStyleDescription('technical')}
                    </Text>
                  </Space>
                </Radio>
              </Col>
              <Col span={12}>
                <Radio value="casual" style={{ width: '100%' }}>
                  <Space direction="vertical" size={0}>
                    <Text strong>輕鬆隨性</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getStyleDescription('casual')}
                    </Text>
                  </Space>
                </Radio>
              </Col>
              <Col span={12}>
                <Radio value="professional" style={{ width: '100%' }}>
                  <Space direction="vertical" size={0}>
                    <Text strong>專業商務</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getStyleDescription('professional')}
                    </Text>
                  </Space>
                </Radio>
              </Col>
              <Col span={12}>
                <Radio value="humorous" style={{ width: '100%' }}>
                  <Space direction="vertical" size={0}>
                    <Text strong>幽默風趣</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getStyleDescription('humorous')}
                    </Text>
                  </Space>
                </Radio>
              </Col>
            </Row>
          </Radio.Group>
        </div>

        <Divider />

        {/* 分析深度設定 */}
        <div>
          <Title level={5}>分析深度</Title>
          <Radio.Group
            value={value.include_analysis_depth}
            onChange={(e) => handleAnalysisDepthChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="basic" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>基礎分析</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    包含基本技術指標和簡單分析
                  </Text>
                </Space>
              </Radio>
              <Radio value="detailed" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>詳細分析</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    包含多個技術指標和深入分析
                  </Text>
                </Space>
              </Radio>
              <Radio value="comprehensive" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>全面分析</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    包含技術面、基本面、籌碼面完整分析
                  </Text>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 額外功能設定 */}
        <div>
          <Title level={5}>額外功能</Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Space>
                <input
                  type="checkbox"
                  checked={value.include_charts}
                  onChange={(e) => handleIncludeChartsChange(e.target.checked)}
                />
                <Text>包含圖表說明</Text>
                <Tag color="blue">建議</Tag>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                在內容中加入技術圖表的文字描述
              </Text>
            </div>
            
            <div>
              <Space>
                <input
                  type="checkbox"
                  checked={value.include_risk_warning}
                  onChange={(e) => handleIncludeRiskWarningChange(e.target.checked)}
                />
                <Text>包含風險警告</Text>
                <Tag color="red">必要</Tag>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                在內容末尾加入投資風險提醒
              </Text>
            </div>
          </Space>
        </div>

        {/* 設定摘要 */}
        <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
          <Title level={5} style={{ color: '#52c41a', margin: 0 }}>設定摘要</Title>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Text type="secondary">
              • 貼文模式：{value.post_mode === 'one_to_one' ? '一對一' : '一對多'}
              {value.post_mode === 'one_to_many' && ` (最多${value.max_stocks_per_post}檔)`}
            </Text>
            <Text type="secondary">
              • 內容長度：{value.content_length} ({value.max_words}字)
            </Text>
            <Text type="secondary">
              • 內容風格：{value.content_style}
            </Text>
            <Text type="secondary">
              • 分析深度：{value.include_analysis_depth}
            </Text>
            <Text type="secondary">
              • 額外功能：{value.include_charts ? '圖表說明' : ''} {value.include_risk_warning ? '風險警告' : ''}
            </Text>
          </Space>
        </Card>
      </Space>
    </Card>
  );
};

export default GenerationSettings;
