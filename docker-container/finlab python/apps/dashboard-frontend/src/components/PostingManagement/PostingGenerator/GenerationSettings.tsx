import React from 'react';
import { Card, Typography, Radio, Space, InputNumber, Select, Divider, Tag, Row, Col } from 'antd';
import { OneToOneOutlined, ClusterOutlined, FileTextOutlined, ClockCircleOutlined, ExperimentOutlined } from '@ant-design/icons';

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
  // 新增：自定義字數
  custom_word_count?: number;
  // 新增：發文類型
  posting_type: 'interaction' | 'analysis' | 'personalized';
  // 新增：互動發問相關設定
  include_questions: boolean;
  include_emoji: boolean;
  include_hashtag: boolean;
  // 新增：模型 ID 覆蓋選項
  model_id_override?: string | null; // null = 使用 KOL 預設, string = 批量覆蓋
  use_kol_default_model: boolean; // true = 使用 KOL 預設, false = 使用批量覆蓋
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

  const handleCustomWordCountChange = (wordCount: number | null) => {
    onChange({
      ...value,
      custom_word_count: wordCount || undefined
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

  const handlePostingTypeChange = (postingType: 'interaction' | 'analysis') => {
    const newSettings = {
      ...value,
      posting_type: postingType
    };

    // 根據發文類型自動調整設定
    if (postingType === 'interaction') {
      // 互動發問類型：簡短內容，包含問句和表情符號
      newSettings.content_length = 'short';
      newSettings.max_words = 30;
      newSettings.include_questions = true;
      newSettings.include_emoji = true;
      newSettings.include_hashtag = true;
      newSettings.content_style = 'casual';
      newSettings.include_analysis_depth = 'basic';
    } else {
      // 發表分析類型：正常流程
      newSettings.content_length = 'medium';
      newSettings.max_words = 200;
      newSettings.include_questions = false;
      newSettings.include_emoji = false;
      newSettings.include_hashtag = true;
      newSettings.content_style = 'professional';
      newSettings.include_analysis_depth = 'detailed';
    }

    onChange(newSettings);
  };

  const handleIncludeQuestionsChange = (includeQuestions: boolean) => {
    onChange({
      ...value,
      include_questions: includeQuestions
    });
  };

  const handleIncludeEmojiChange = (includeEmoji: boolean) => {
    onChange({
      ...value,
      include_emoji: includeEmoji
    });
  };

  const handleIncludeHashtagChange = (includeHashtag: boolean) => {
    onChange({
      ...value,
      include_hashtag: includeHashtag
    });
  };

  const handleUseKOLDefaultModelChange = (useKOLDefault: boolean) => {
    onChange({
      ...value,
      use_kol_default_model: useKOLDefault,
      model_id_override: useKOLDefault ? null : value.model_id_override
    });
  };

  const handleModelIdOverrideChange = (modelId: string | null) => {
    onChange({
      ...value,
      model_id_override: modelId,
      use_kol_default_model: !modelId
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

        {/* 發文類型選擇 */}
        <div>
          <Title level={5}>發文類型</Title>
          <Radio.Group
            value={value.posting_type}
            onChange={(e) => handlePostingTypeChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="analysis" style={{ width: '100%' }}>
                <Space>
                  <FileTextOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>發表分析</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      專業分析內容，詳細解讀市場動態和技術指標
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="interaction" style={{ width: '100%' }}>
                <Space>
                  <ClockCircleOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>互動發問</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      簡短疑問句內容，促進用戶互動和參與
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="personalized" style={{ width: '100%' }}>
                <Space>
                  <ExperimentOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>個人化內容</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      使用個人化模組，生成5個不同角度版本供選擇
                    </Text>
                  </Space>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 互動發問類型設定 */}
        {value.posting_type === 'interaction' && (
          <div>
            <Title level={5}>互動發問設定</Title>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>包含問句：</Text>
                <Radio.Group
                  value={value.include_questions}
                  onChange={(e) => handleIncludeQuestionsChange(e.target.value)}
                  style={{ marginLeft: 16 }}
                >
                  <Radio value={true}>是</Radio>
                  <Radio value={false}>否</Radio>
                </Radio.Group>
              </div>
              <div>
                <Text>包含表情符號：</Text>
                <Radio.Group
                  value={value.include_emoji}
                  onChange={(e) => handleIncludeEmojiChange(e.target.value)}
                  style={{ marginLeft: 16 }}
                >
                  <Radio value={true}>是</Radio>
                  <Radio value={false}>否</Radio>
                </Radio.Group>
              </div>
              <div>
                <Text>包含標籤：</Text>
                <Radio.Group
                  value={value.include_hashtag}
                  onChange={(e) => handleIncludeHashtagChange(e.target.value)}
                  style={{ marginLeft: 16 }}
                >
                  <Radio value={true}>是</Radio>
                  <Radio value={false}>否</Radio>
                </Radio.Group>
              </div>
            </Space>
          </div>
        )}

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
                value={value.custom_word_count || value.max_words}
                onChange={handleCustomWordCountChange}
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

        <Divider />

        {/* 模型選擇設定 */}
        <div>
          <Title level={5}>AI 模型選擇</Title>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <Space>
                <input
                  type="radio"
                  checked={value.use_kol_default_model !== false}
                  onChange={() => handleUseKOLDefaultModelChange(true)}
                />
                <Text strong>使用 KOL 預設模型</Text>
                <Tag color="green">推薦</Tag>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px', marginLeft: '24px' }}>
                每個 KOL 使用其個人檔案中設定的預設 model_id（在 KOL 管理頁面設定）
              </Text>
            </div>

            <div>
              <Space>
                <input
                  type="radio"
                  checked={value.use_kol_default_model === false}
                  onChange={() => handleUseKOLDefaultModelChange(false)}
                />
                <Text strong>批量覆蓋模型</Text>
                <Tag color="orange">統一設定</Tag>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px', marginLeft: '24px' }}>
                本批次所有貼文統一使用指定的模型（忽略 KOL 預設值）
              </Text>

              {value.use_kol_default_model === false && (
                <div style={{ marginLeft: '24px', marginTop: '12px' }}>
                  <Select
                    value={value.model_id_override || undefined}
                    onChange={handleModelIdOverrideChange}
                    placeholder="選擇批量模型"
                    style={{ width: '300px' }}
                    allowClear
                  >
                    <Option value="gpt-4o-mini">
                      <Space>
                        <span>gpt-4o-mini</span>
                        <Tag color="green" style={{ marginLeft: 8 }}>推薦</Tag>
                        <Text type="secondary" style={{ fontSize: '11px' }}>快速、經濟</Text>
                      </Space>
                    </Option>
                    <Option value="gpt-4o">
                      <Space>
                        <span>gpt-4o</span>
                        <Tag color="blue" style={{ marginLeft: 8 }}>高品質</Tag>
                        <Text type="secondary" style={{ fontSize: '11px' }}>最新模型</Text>
                      </Space>
                    </Option>
                    <Option value="gpt-4-turbo">
                      <Space>
                        <span>gpt-4-turbo</span>
                        <Tag color="purple" style={{ marginLeft: 8 }}>進階</Tag>
                        <Text type="secondary" style={{ fontSize: '11px' }}>較貴、強大</Text>
                      </Space>
                    </Option>
                    <Option value="gpt-4">
                      <Space>
                        <span>gpt-4</span>
                        <Tag color="orange" style={{ marginLeft: 8 }}>穩定</Tag>
                        <Text type="secondary" style={{ fontSize: '11px' }}>經典版本</Text>
                      </Space>
                    </Option>
                    <Option value="gpt-3.5-turbo">
                      <Space>
                        <span>gpt-3.5-turbo</span>
                        <Tag color="default" style={{ marginLeft: 8 }}>基礎</Tag>
                        <Text type="secondary" style={{ fontSize: '11px' }}>低成本</Text>
                      </Space>
                    </Option>
                  </Select>
                  {value.model_id_override && (
                    <div style={{ marginTop: '8px' }}>
                      <Tag color="blue">
                        已選擇: {value.model_id_override}
                      </Tag>
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        此批次所有貼文將使用此模型
                      </Text>
                    </div>
                  )}
                </div>
              )}
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
            <Text type="secondary">
              • AI 模型：{value.use_kol_default_model !== false ? 'KOL 預設模型' : `批量覆蓋 (${value.model_id_override || '未指定'})`}
            </Text>
          </Space>
        </Card>
      </Space>
    </Card>
  );
};

export default GenerationSettings;
