import React, { useState } from 'react';
import { Card, Typography, Space, Button, Input, Select, Divider, Tag, Row, Col, Modal, Form, Checkbox, Radio, Tooltip } from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SettingOutlined,
  FileTextOutlined,
  BarChartOutlined,
  DollarOutlined,
  DatabaseOutlined,
  EyeOutlined,
  CopyOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  data_source: string;
  template: string;
  variables: string[];
  technical_indicators: string[];
  is_active: boolean;
}

interface ExplainabilityConfig {
  summarizer_enabled: boolean;
  data_extractor_enabled: boolean;
  prompt_templates: PromptTemplate[];
  selected_template: string;
  technical_indicators: string[];
  custom_prompt: string;
  explainability_level: 'basic' | 'detailed' | 'comprehensive';
}

interface ExplainabilityConfigProps {
  value: ExplainabilityConfig;
  onChange: (value: ExplainabilityConfig) => void;
}

const ExplainabilityConfig: React.FC<ExplainabilityConfigProps> = ({ value, onChange }) => {
  const [isTemplateModalVisible, setIsTemplateModalVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PromptTemplate | null>(null);
  const [form] = Form.useForm();

  // 預設的prompting模板
  const defaultTemplates: PromptTemplate[] = [
    {
      id: 'stock_price_basic',
      name: '股價基礎分析',
      description: '針對股價數據的基礎技術分析',
      data_source: 'stock_price_api',
      template: '請分析{stock_name}({stock_code})的技術指標：\n\n1. MACD指標：{macd_signal}\n2. RSI指標：{rsi_value}\n3. 移動平均線：{ma_alignment}\n4. 成交量：{volume_trend}\n\n請提供簡潔的技術分析結論。',
      variables: ['stock_name', 'stock_code', 'macd_signal', 'rsi_value', 'ma_alignment', 'volume_trend'],
      technical_indicators: ['MACD', 'RSI', 'MA', 'Volume'],
      is_active: true
    },
    {
      id: 'revenue_analysis',
      name: '營收分析模板',
      description: '針對月營收數據的深度分析',
      data_source: 'monthly_revenue_api',
      template: '分析{stock_name}的營收表現：\n\n1. 月營收：{monthly_revenue}億元\n2. 年增率：{yoy_growth}%\n3. 月增率：{mom_growth}%\n4. 累計營收：{cumulative_revenue}億元\n\n請評估營收趨勢並提供投資建議。',
      variables: ['stock_name', 'monthly_revenue', 'yoy_growth', 'mom_growth', 'cumulative_revenue'],
      technical_indicators: ['Revenue', 'YoY', 'MoM'],
      is_active: true
    },
    {
      id: 'financial_comprehensive',
      name: '財報綜合分析',
      description: '結合財報數據的全面分析',
      data_source: 'financial_report_api',
      template: '綜合分析{stock_name}的財務狀況：\n\n1. EPS：{eps}元\n2. ROE：{roe}%\n3. 負債比：{debt_ratio}%\n4. 本益比：{pe_ratio}倍\n5. 股價淨值比：{pb_ratio}倍\n\n請提供完整的財務評估。',
      variables: ['stock_name', 'eps', 'roe', 'debt_ratio', 'pe_ratio', 'pb_ratio'],
      technical_indicators: ['EPS', 'ROE', 'Debt Ratio', 'PE', 'PB'],
      is_active: true
    }
  ];

  const technicalIndicators = [
    'MACD', 'RSI', 'KDJ', '布林帶', '移動平均線', '成交量', '威廉指標', 'CCI',
    'DMI', 'TRIX', 'ROC', 'MTM', 'BIAS', 'PSY', 'ARBR', 'CR'
  ];

  const handleSummarizerToggle = (enabled: boolean) => {
    onChange({
      ...value,
      summarizer_enabled: enabled
    });
  };

  const handleDataExtractorToggle = (enabled: boolean) => {
    onChange({
      ...value,
      data_extractor_enabled: enabled
    });
  };

  const handleTemplateSelect = (templateId: string) => {
    onChange({
      ...value,
      selected_template: templateId
    });
  };

  const handleTechnicalIndicatorChange = (indicators: string[]) => {
    onChange({
      ...value,
      technical_indicators: indicators
    });
  };

  const handleExplainabilityLevelChange = (level: 'basic' | 'detailed' | 'comprehensive') => {
    onChange({
      ...value,
      explainability_level: level
    });
  };

  const handleCustomPromptChange = (prompt: string) => {
    onChange({
      ...value,
      custom_prompt: prompt
    });
  };

  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    form.resetFields();
    setIsTemplateModalVisible(true);
  };

  const handleEditTemplate = (template: PromptTemplate) => {
    setEditingTemplate(template);
    form.setFieldsValue(template);
    setIsTemplateModalVisible(true);
  };

  const handleDeleteTemplate = (templateId: string) => {
    const newTemplates = value.prompt_templates.filter(t => t.id !== templateId);
    onChange({
      ...value,
      prompt_templates: newTemplates,
      selected_template: value.selected_template === templateId ? '' : value.selected_template
    });
  };

  const handleSaveTemplate = async () => {
    try {
      const values = await form.validateFields();
      const template: PromptTemplate = {
        id: editingTemplate?.id || Date.now().toString(),
        name: values.name,
        description: values.description,
        data_source: values.data_source,
        template: values.template,
        variables: values.variables || [],
        technical_indicators: values.technical_indicators || [],
        is_active: true
      };

      const newTemplates = editingTemplate
        ? value.prompt_templates.map(t => t.id === editingTemplate.id ? template : t)
        : [...value.prompt_templates, template];

      onChange({
        ...value,
        prompt_templates: newTemplates
      });

      setIsTemplateModalVisible(false);
      setEditingTemplate(null);
      form.resetFields();
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const getCurrentTemplate = () => {
    return value.prompt_templates.find(t => t.id === value.selected_template) || defaultTemplates[0];
  };

  return (
    <Card title="可解釋層設定" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          根據選擇的數據源管理prompting模板，設定數據萃取和可解釋性層級
        </Text>

        {/* 數據處理層設定 */}
        <Card size="small" style={{ backgroundColor: '#e6f7ff', border: '1px solid #91d5ff' }}>
          <Title level={5} style={{ color: '#1890ff', margin: 0 }}>數據處理層</Title>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <Space>
                <input
                  type="checkbox"
                  checked={value.summarizer_enabled}
                  onChange={(e) => handleSummarizerToggle(e.target.checked)}
                />
                <Text strong>數據摘要器</Text>
                <Tag color="blue">建議</Tag>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                自動摘要和整理原始數據，提取關鍵資訊
              </Text>
            </div>
            
            <div>
              <Space>
                <input
                  type="checkbox"
                  checked={value.data_extractor_enabled}
                  onChange={(e) => handleDataExtractorToggle(e.target.checked)}
                />
                <Text strong>數據價值萃取器</Text>
                <Tag color="green">必要</Tag>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                從數據中萃取有價值的投資洞察和趨勢
              </Text>
            </div>
          </Space>
        </Card>

        <Divider />

        {/* Prompting模板管理 */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <Title level={5} style={{ margin: 0 }}>Prompting模板管理</Title>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateTemplate}>
              新增模板
            </Button>
          </div>

          <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: '12px' }}>
            選擇或創建適合的prompting模板，系統會根據數據源自動應用
          </Text>

          {/* 模板選擇 */}
          <Select
            value={value.selected_template}
            onChange={handleTemplateSelect}
            style={{ width: '100%', marginBottom: '12px' }}
            placeholder="選擇prompting模板..."
          >
            {[...defaultTemplates, ...value.prompt_templates].map((template) => (
              <Option key={template.id} value={template.id}>
                <Space>
                  <FileTextOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>{template.name}</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {template.description}
                    </Text>
                  </Space>
                </Space>
              </Option>
            ))}
          </Select>

          {/* 當前模板預覽 */}
          {value.selected_template && (
            <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
              <Title level={5} style={{ color: '#52c41a', margin: 0 }}>當前模板預覽</Title>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Text strong>{getCurrentTemplate().name}</Text>
                <Text type="secondary">{getCurrentTemplate().description}</Text>
                <Text code style={{ fontSize: '12px', whiteSpace: 'pre-wrap' }}>
                  {getCurrentTemplate().template}
                </Text>
                <Space wrap>
                  {getCurrentTemplate().technical_indicators.map(indicator => (
                    <Tag key={indicator} color="blue">{indicator}</Tag>
                  ))}
                </Space>
              </Space>
            </Card>
          )}

          {/* 自定義模板列表 */}
          {value.prompt_templates.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <Text strong>自定義模板</Text>
              <div style={{ marginTop: '8px' }}>
                {value.prompt_templates.map((template) => (
                  <Card key={template.id} size="small" style={{ marginBottom: '8px' }}>
                    <Row justify="space-between" align="middle">
                      <Col>
                        <Space direction="vertical" size={0}>
                          <Text strong>{template.name}</Text>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {template.description}
                          </Text>
                          <Space wrap>
                            {template.technical_indicators.map(indicator => (
                              <Tag key={indicator} color="blue" style={{ fontSize: '10px' }}>
                                {indicator}
                              </Tag>
                            ))}
                          </Space>
                        </Space>
                      </Col>
                      <Col>
                        <Space>
                          <Button
                            type="text"
                            size="small"
                            icon={<EditOutlined />}
                            onClick={() => handleEditTemplate(template)}
                          />
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => handleDeleteTemplate(template.id)}
                          />
                        </Space>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>

        <Divider />

        {/* 技術指標選擇 */}
        <div>
          <Title level={5}>技術指標選擇</Title>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            選擇要包含在分析中的技術指標
          </Text>
          <div style={{ marginTop: '8px' }}>
            <Space wrap>
              {technicalIndicators.map((indicator) => (
                <Checkbox
                  key={indicator}
                  checked={value.technical_indicators.includes(indicator)}
                  onChange={(e) => {
                    const newIndicators = e.target.checked
                      ? [...value.technical_indicators, indicator]
                      : value.technical_indicators.filter(i => i !== indicator);
                    handleTechnicalIndicatorChange(newIndicators);
                  }}
                >
                  <Tag color="blue">{indicator}</Tag>
                </Checkbox>
              ))}
            </Space>
          </div>
        </div>

        <Divider />

        {/* 可解釋性層級 */}
        <div>
          <Title level={5}>可解釋性層級</Title>
          <Radio.Group
            value={value.explainability_level}
            onChange={(e) => handleExplainabilityLevelChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="basic" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>基礎層級</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    提供基本的數據解釋和簡單分析
                  </Text>
                </Space>
              </Radio>
              <Radio value="detailed" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>詳細層級</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    提供詳細的技術分析和數據解讀
                  </Text>
                </Space>
              </Radio>
              <Radio value="comprehensive" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>全面層級</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    提供全面的分析，包含多個維度的深度解讀
                  </Text>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 自定義Prompt */}
        <div>
          <Title level={5}>自定義Prompt</Title>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            可以覆蓋模板設定，使用自定義的prompt
          </Text>
          <TextArea
            rows={4}
            placeholder="輸入自定義的prompt模板..."
            value={value.custom_prompt}
            onChange={(e) => handleCustomPromptChange(e.target.value)}
            style={{ marginTop: '8px' }}
          />
        </div>

        {/* 設定摘要 */}
        <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
          <Title level={5} style={{ color: '#52c41a', margin: 0 }}>可解釋層摘要</Title>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Text type="secondary">
              • 數據摘要器：{value.summarizer_enabled ? '啟用' : '停用'}
            </Text>
            <Text type="secondary">
              • 數據價值萃取器：{value.data_extractor_enabled ? '啟用' : '停用'}
            </Text>
            <Text type="secondary">
              • 當前模板：{getCurrentTemplate().name}
            </Text>
            <Text type="secondary">
              • 技術指標：{value.technical_indicators.length}個
            </Text>
            <Text type="secondary">
              • 可解釋性層級：{value.explainability_level}
            </Text>
            <Text type="secondary">
              • 自定義Prompt：{value.custom_prompt ? '已設定' : '未設定'}
            </Text>
          </Space>
        </Card>
      </Space>

      {/* 模板編輯模態框 */}
      <Modal
        title={editingTemplate ? '編輯模板' : '新增模板'}
        open={isTemplateModalVisible}
        onOk={handleSaveTemplate}
        onCancel={() => {
          setIsTemplateModalVisible(false);
          setEditingTemplate(null);
          form.resetFields();
        }}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="模板名稱"
            name="name"
            rules={[{ required: true, message: '請輸入模板名稱' }]}
          >
            <Input placeholder="輸入模板名稱..." />
          </Form.Item>
          
          <Form.Item
            label="模板描述"
            name="description"
            rules={[{ required: true, message: '請輸入模板描述' }]}
          >
            <Input placeholder="輸入模板描述..." />
          </Form.Item>
          
          <Form.Item
            label="適用數據源"
            name="data_source"
            rules={[{ required: true, message: '請選擇數據源' }]}
          >
            <Select placeholder="選擇數據源...">
              <Option value="stock_price_api">個股股價 API</Option>
              <Option value="monthly_revenue_api">月營收 API</Option>
              <Option value="financial_report_api">財報 API</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            label="Prompt模板"
            name="template"
            rules={[{ required: true, message: '請輸入prompt模板' }]}
          >
            <TextArea
              rows={6}
              placeholder="輸入prompt模板，使用{變數名}來引用數據..."
            />
          </Form.Item>
          
          <Form.Item
            label="技術指標"
            name="technical_indicators"
          >
            <Select
              mode="multiple"
              placeholder="選擇技術指標..."
              style={{ width: '100%' }}
            >
              {technicalIndicators.map(indicator => (
                <Option key={indicator} value={indicator}>{indicator}</Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default ExplainabilityConfig;
