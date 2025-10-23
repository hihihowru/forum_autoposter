import React from 'react';
import { Card, Typography, Radio, Space, InputNumber, Select, Divider, Tag, Row, Col, Button, Steps } from 'antd';
import {
  PlayCircleOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  FileTextOutlined,
  SettingOutlined,
  ExperimentOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

interface BatchModeConfig {
  batch_type: 'test_mode' | 'review_mode' | 'auto_publish';
  max_posts_per_batch: number;
  generation_strategy: 'one_kol_one_stock' | 'one_kol_all_stocks' | 'mixed';
  review_required: boolean;
  auto_approve_threshold: number;
  publish_delay_minutes: number;
  quality_check_enabled: boolean;
  ai_detection_enabled: boolean;
  // 新增：生成模式 (🔥 FIX: 使用正確的值 manual/scheduled/self_learning)
  generation_mode: 'manual' | 'scheduled' | 'self_learning';
  // 新增：發文類型
  posting_type: 'interaction' | 'analysis' | 'personalized';
}

interface BatchModeSettingsProps {
  value: BatchModeConfig;
  onChange: (value: BatchModeConfig) => void;
  onStartBatchGeneration?: () => void;
  loading?: boolean;
}

const BatchModeSettings: React.FC<BatchModeSettingsProps> = ({ 
  value, 
  onChange, 
  onStartBatchGeneration,
  loading = false 
}) => {
  const handleBatchTypeChange = (type: 'test_mode' | 'review_mode' | 'auto_publish') => {
    onChange({
      ...value,
      batch_type: type,
      review_required: type !== 'auto_publish'
    });
  };

  const handleMaxPostsChange = (maxPosts: number) => {
    onChange({
      ...value,
      max_posts_per_batch: maxPosts
    });
  };

  const handleGenerationStrategyChange = (strategy: 'one_kol_one_stock' | 'one_kol_all_stocks' | 'mixed') => {
    onChange({
      ...value,
      generation_strategy: strategy
    });
  };

  const handleReviewRequiredChange = (required: boolean) => {
    onChange({
      ...value,
      review_required: required
    });
  };

  const handleAutoApproveThresholdChange = (threshold: number) => {
    onChange({
      ...value,
      auto_approve_threshold: threshold
    });
  };

  const handlePublishDelayChange = (delay: number) => {
    onChange({
      ...value,
      publish_delay_minutes: delay
    });
  };

  const handleQualityCheckChange = (enabled: boolean) => {
    onChange({
      ...value,
      quality_check_enabled: enabled
    });
  };

  const handleAIDetectionChange = (enabled: boolean) => {
    onChange({
      ...value,
      ai_detection_enabled: enabled
    });
  };

  const handleGenerationModeChange = (mode: 'simple' | 'trash' | 'high_quality') => {
    onChange({
      ...value,
      generation_mode: mode
    });
  };

  const handlePostingTypeChange = (postingType: 'interaction' | 'analysis') => {
    onChange({
      ...value,
      posting_type: postingType
    });
  };

  const getBatchTypeDescription = (type: string) => {
    switch (type) {
      case 'test_mode':
        return '測試模式：生成內容但不發布，用於測試和調試';
      case 'review_mode':
        return '審核模式：生成內容後需要人工審核才能發布';
      case 'auto_publish':
        return '自動發布：生成內容後自動發布（需要高品質設定）';
      default:
        return '';
    }
  };

  const getGenerationStrategyDescription = (strategy: string) => {
    switch (strategy) {
      case 'one_kol_one_stock':
        return '1個KOL對應1檔股票，適合精準分析';
      case 'one_kol_all_stocks':
        return '1個KOL對應所有股票，適合市場概覽';
      case 'mixed':
        return '混合模式：根據KOL特性動態分配';
      default:
        return '';
    }
  };

  const getCurrentStep = () => {
    switch (value.batch_type) {
      case 'test_mode':
        return 0;
      case 'review_mode':
        return 1;
      case 'auto_publish':
        return 2;
      default:
        return 0;
    }
  };

  const batchSteps = [
    {
      title: '測試發文',
      description: '生成內容但不發布',
      icon: <PlayCircleOutlined />
    },
    {
      title: '逐篇審核',
      description: '人工審核每篇內容',
      icon: <EyeOutlined />
    },
    {
      title: '手動發布',
      description: '審核通過後發布',
      icon: <CheckCircleOutlined />
    }
  ];

  return (
    <Card title="批量模式設定" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          配置批量生成的工作流程，支援測試發文 → 逐篇審核 → 手動發布的完整流程
        </Text>

        {/* 工作流程步驟 */}
        <div>
          <Title level={5}>工作流程</Title>
          <Steps
            current={getCurrentStep()}
            items={batchSteps.map((step, index) => ({
              title: step.title,
              description: step.description,
              icon: step.icon
            }))}
            style={{ marginBottom: '16px' }}
          />
        </div>

        <Divider />

        {/* 批量模式選擇 */}
        <div>
          <Title level={5}>批量模式</Title>
          <Radio.Group
            value={value.batch_type}
            onChange={(e) => handleBatchTypeChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="test_mode" style={{ width: '100%' }}>
                <Space>
                  <PlayCircleOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>測試模式</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getBatchTypeDescription('test_mode')}
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="review_mode" style={{ width: '100%' }}>
                <Space>
                  <EyeOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>審核模式</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getBatchTypeDescription('review_mode')}
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="auto_publish" style={{ width: '100%' }}>
                <Space>
                  <CheckCircleOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>自動發布</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {getBatchTypeDescription('auto_publish')}
                    </Text>
                  </Space>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 發文類型設定 */}
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

        {/* 生成策略設定 */}
        <div>
          <Title level={5}>生成策略</Title>
          <Radio.Group
            value={value.generation_strategy}
            onChange={(e) => handleGenerationStrategyChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="one_kol_one_stock" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>1 KOL → 1 股票</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getGenerationStrategyDescription('one_kol_one_stock')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="one_kol_all_stocks" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>1 KOL → 所有股票</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getGenerationStrategyDescription('one_kol_all_stocks')}
                  </Text>
                </Space>
              </Radio>
              <Radio value="mixed" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>混合模式</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {getGenerationStrategyDescription('mixed')}
                  </Text>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 批量參數設定 */}
        <div>
          <Title level={5}>批量參數</Title>
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>每批最大貼文數</Text>
                <Select
                  value={value.max_posts_per_batch}
                  onChange={handleMaxPostsChange}
                  style={{ width: '100%' }}
                >
                  <Option value={5}>5篇</Option>
                  <Option value={10}>10篇</Option>
                  <Option value={20}>20篇</Option>
                  <Option value={50}>50篇</Option>
                </Select>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  建議設定10-20篇，避免過多影響審核效率
                </Text>
              </Space>
            </Col>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>發布延遲</Text>
                <Select
                  value={value.publish_delay_minutes}
                  onChange={handlePublishDelayChange}
                  style={{ width: '100%' }}
                >
                  <Option value={0}>立即發布</Option>
                  <Option value={5}>5分鐘後</Option>
                  <Option value={15}>15分鐘後</Option>
                  <Option value={30}>30分鐘後</Option>
                </Select>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  避免短時間內大量發布
                </Text>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 審核模式設定 */}
        {value.batch_type === 'review_mode' && (
          <div>
            <Title level={5}>審核設定</Title>
            <Card size="small" style={{ backgroundColor: '#fff7e6', border: '1px solid #ffd591' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <div>
                  <Space>
                    <input
                      type="checkbox"
                      checked={value.review_required}
                      onChange={(e) => handleReviewRequiredChange(e.target.checked)}
                    />
                    <Text strong>需要人工審核</Text>
                    <Tag color="orange">必要</Tag>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                    每篇貼文都需要人工審核後才能發布
                  </Text>
                </div>

                <div>
                  <Space>
                    <Text>自動通過門檻：</Text>
                    <Select
                      value={value.auto_approve_threshold}
                      onChange={handleAutoApproveThresholdChange}
                      style={{ width: '120px' }}
                    >
                      <Option value={0}>不自動通過</Option>
                      <Option value={80}>80分以上</Option>
                      <Option value={90}>90分以上</Option>
                      <Option value={95}>95分以上</Option>
                    </Select>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                    品質分數達到門檻的貼文可自動通過審核
                  </Text>
                </div>
              </Space>
            </Card>
          </div>
        )}

        {/* 生成模式設定 */}
        <div>
          <Title level={5}>生成模式</Title>
          <Radio.Group
            value={value.generation_mode || 'simple'}
            onChange={(e) => handleGenerationModeChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="simple" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>簡易模式</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    快速生成，內容簡潔，適合日常發文
                  </Text>
                </Space>
              </Radio>
              <Radio value="trash" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>廢文模式</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    輕鬆幽默，增加互動，適合社群媒體
                  </Text>
                </Space>
              </Radio>
              <Radio value="high_quality" style={{ width: '100%' }}>
                <Space direction="vertical" size={0}>
                  <Text strong>高品質模式</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    深度分析，專業內容，適合投資建議
                  </Text>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 品質控制設定 */}
        <div>
          <Title level={5}>品質控制</Title>
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <input
                    type="checkbox"
                    checked={value.quality_check_enabled}
                    onChange={(e) => handleQualityCheckChange(e.target.checked)}
                  />
                  <Text strong>品質檢查</Text>
                  <Tag color="blue">建議</Tag>
                </Space>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  自動檢查內容品質和完整性
                </Text>
              </Space>
            </Col>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <input
                    type="checkbox"
                    checked={value.ai_detection_enabled}
                    onChange={(e) => handleAIDetectionChange(e.target.checked)}
                  />
                  <Text strong>AI檢測</Text>
                  <Tag color="red">必要</Tag>
                </Space>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  檢測內容是否過於AI化
                </Text>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 批量模式摘要 */}
        <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
          <Title level={5} style={{ color: '#52c41a', margin: 0 }}>批量模式摘要</Title>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Text type="secondary">
              • 批量模式：{value.batch_type === 'test_mode' ? '測試模式' : 
                value.batch_type === 'review_mode' ? '審核模式' : '自動發布'}
            </Text>
            <Text type="secondary">
              • 生成策略：{value.generation_strategy === 'one_kol_one_stock' ? '1 KOL → 1 股票' :
                value.generation_strategy === 'one_kol_all_stocks' ? '1 KOL → 所有股票' : '混合模式'}
            </Text>
            <Text type="secondary">
              • 生成模式：{value.generation_mode === 'simple' ? '簡易模式' :
                value.generation_mode === 'trash' ? '廢文模式' : '高品質模式'}
            </Text>
            <Text type="secondary">
              • 每批最大貼文數：{value.max_posts_per_batch}篇
            </Text>
            <Text type="secondary">
              • 發布延遲：{value.publish_delay_minutes}分鐘
            </Text>
            <Text type="secondary">
              • 審核要求：{value.review_required ? '是' : '否'}
              {value.review_required && ` (自動通過門檻: ${value.auto_approve_threshold}分)`}
            </Text>
            <Text type="secondary">
              • 品質控制：{value.quality_check_enabled ? '品質檢查' : ''} {value.ai_detection_enabled ? 'AI檢測' : ''}
            </Text>
          </Space>
        </Card>

        {/* 操作按鈕 */}
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <Space>
            <Button 
              type="primary" 
              size="large" 
              icon={<PlayCircleOutlined />}
              onClick={onStartBatchGeneration}
              loading={loading}
            >
              開始批量生成
            </Button>
            <Button size="large" icon={<SettingOutlined />}>
              保存設定
            </Button>
          </Space>
        </div>
      </Space>
    </Card>
  );
};

export default BatchModeSettings;
