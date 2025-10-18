import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Typography, 
  Row, 
  Col, 
  Table, 
  Tag, 
  Space, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  InputNumber, 
  Switch, 
  Slider,
  Progress,
  Divider,
  Alert,
  Spin,
  message,
  Tabs,
  Descriptions
} from 'antd';
import { 
  UserOutlined, 
  EditOutlined, 
  SaveOutlined, 
  ReloadOutlined,
  SettingOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface KOLProfile {
  id: number;
  serial: string;
  nickname: string;
  member_id: string;
  persona: string;
  status: string;
  owner: string;
  email: string;
  password: string;
  whitelist: boolean;
  notes: string;
  post_times: string;
  target_audience: string;
  interaction_threshold: number;
  content_types: string[];
  common_terms: string;
  colloquial_terms: string;
  tone_style: string;
  typing_habit: string;
  backstory: string;
  expertise: string;
  data_source: string;
  prompt_persona: string;
  prompt_style: string;
  prompt_guardrails: string;
  prompt_skeleton: string;
  prompt_cta: string;
  prompt_hashtags: string;
  signature: string;
  emoji_pack: string;
  model_id: string;
  template_variant: string;
  model_temp: number;
  max_tokens: number;
  title_openers: string[];
  title_signature_patterns: string[];
  title_tail_word: string;
  title_banned_words: string[];
  title_style_examples: string[];
  title_retry_max: number;
  tone_formal: number;
  tone_emotion: number;
  tone_confidence: number;
  tone_urgency: number;
  tone_interaction: number;
  question_ratio: number;
  content_length: string;
  interaction_starters: string[];
  require_finlab_api: boolean;
  allow_hashtags: boolean;
  created_time: string;
  last_updated: string;
  total_posts: number;
  published_posts: number;
  avg_interaction_rate: number;
  best_performing_post: string;
  humor_probability: number;
  humor_enabled: boolean;
  // 新增的機率欄位
  content_style_probabilities: {
    technical: number;
    casual: number;
    professional: number;
    humorous: number;
  };
  analysis_depth_probabilities: {
    basic: number;
    detailed: number;
    comprehensive: number;
  };
  content_length_probabilities: {
    short: number;
    medium: number;
    long: number;
    extended: number;
    comprehensive: number;
    thorough: number;
  };
}

const KOLManagementPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [kolProfiles, setKolProfiles] = useState<KOLProfile[]>([]);
  const [selectedKOL, setSelectedKOL] = useState<KOLProfile | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 載入KOL列表
  const loadKOLProfiles = async () => {
    setLoading(true);
    try {
      // 使用 Vercel API proxy 或直接 Railway URL
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
      const response = await axios.get(`${API_BASE_URL}/api/kol/list`);
      
      // 檢查響應結構
      if (response.data && response.data.success) {
        setKolProfiles(response.data.data || []);
        console.log('✅ KOL 列表載入成功:', response.data.data?.length || 0, '個 KOL');
      } else {
        console.error('❌ API 響應格式錯誤:', response.data);
        message.error('API 響應格式錯誤');
        setKolProfiles([]);
      }
    } catch (error) {
      console.error('❌ 載入KOL資料失敗:', error);
      message.error('載入KOL資料失敗: ' + (error.response?.data?.detail || error.message));
      setKolProfiles([]);
    } finally {
      setLoading(false);
    }
  };

  // 選擇KOL
  const handleSelectKOL = (kol: KOLProfile) => {
    setSelectedKOL(kol);
    form.setFieldsValue(kol);
    setModalVisible(true);
  };

  // 保存KOL設定
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      
      await axios.put(`http://localhost:8001/api/kol/${selectedKOL?.serial}/personalization`, {
        content_style_probabilities: values.content_style_probabilities,
        analysis_depth_probabilities: values.analysis_depth_probabilities,
        content_length_probabilities: values.content_length_probabilities
      });
      
      message.success('KOL設定已保存');
      setModalVisible(false);
      await loadKOLProfiles();
    } catch (error) {
      console.error('保存設定失敗:', error);
      message.error('保存設定失敗');
    } finally {
      setSaving(false);
    }
  };

  // 機率滑塊組件
  const ProbabilitySlider = ({ 
    name, 
    label, 
    value, 
    color 
  }: { 
    name: string; 
    label: string; 
    value: number; 
    color: string; 
  }) => (
    <Form.Item name={name} label={label}>
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <Text strong>{label}</Text>
          <Text style={{ color }}>{(value * 100).toFixed(1)}%</Text>
        </div>
        <Slider
          min={0}
          max={1}
          step={0.01}
          value={value}
          trackStyle={{ backgroundColor: color }}
          handleStyle={{ borderColor: color }}
        />
      </div>
    </Form.Item>
  );

  // 表格列定義
  const columns = [
    {
      title: 'KOL序號',
      dataIndex: 'serial',
      key: 'serial',
      width: 100,
    },
    {
      title: '暱稱',
      dataIndex: 'nickname',
      key: 'nickname',
      width: 120,
    },
    {
      title: '人設',
      dataIndex: 'persona',
      key: 'persona',
      width: 100,
      render: (persona: string) => (
        <Tag color="blue">{persona}</Tag>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '啟用' : '停用'}
        </Tag>
      ),
    },
    {
      title: '總貼文數',
      dataIndex: 'total_posts',
      key: 'total_posts',
      width: 100,
    },
    {
      title: '已發布',
      dataIndex: 'published_posts',
      key: 'published_posts',
      width: 100,
    },
    {
      title: '互動率',
      dataIndex: 'avg_interaction_rate',
      key: 'avg_interaction_rate',
      width: 100,
      render: (rate: number) => rate ? `${(rate * 100).toFixed(1)}%` : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record: KOLProfile) => (
        <Space>
          <Button 
            type="primary" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleSelectKOL(record)}
          >
            編輯
          </Button>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    loadKOLProfiles();
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>
              <UserOutlined style={{ marginRight: 8 }} />
              KOL 管理
            </Title>
            <Text type="secondary">管理所有KOL的設定和個人化參數</Text>
          </div>
          <Button 
            icon={<ReloadOutlined />}
            onClick={loadKOLProfiles}
            loading={loading}
          >
            刷新
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={kolProfiles}
          rowKey="serial"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 個KOL`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* KOL編輯Modal */}
      <Modal
        title={
          <div>
            <UserOutlined style={{ marginRight: 8 }} />
            {selectedKOL?.nickname} ({selectedKOL?.serial}) - {selectedKOL?.persona}
          </div>
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={1000}
        footer={[
          <Button key="cancel" onClick={() => setModalVisible(false)}>
            取消
          </Button>,
          <Button 
            key="save" 
            type="primary" 
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            保存設定
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical">
          <Tabs defaultActiveKey="personalization">
            {/* 個人化設定 */}
            <TabPane tab="個人化設定" key="personalization">
              <Alert
                message="調整KOL的內容生成機率參數"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
              
              <Row gutter={24}>
                <Col span={12}>
                  <Card title="📝 內容風格機率" size="small">
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'technical']}
                      label="技術分析"
                      value={selectedKOL?.content_style_probabilities?.technical || 0.3}
                      color="#1890ff"
                    />
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'casual']}
                      label="輕鬆隨性"
                      value={selectedKOL?.content_style_probabilities?.casual || 0.4}
                      color="#52c41a"
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="📝 內容風格機率 (續)" size="small">
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'professional']}
                      label="專業商務"
                      value={selectedKOL?.content_style_probabilities?.professional || 0.2}
                      color="#faad14"
                    />
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'humorous']}
                      label="幽默風趣"
                      value={selectedKOL?.content_style_probabilities?.humorous || 0.1}
                      color="#f5222d"
                    />
                  </Card>
                </Col>
              </Row>

              <Row gutter={24} style={{ marginTop: 16 }}>
                <Col span={8}>
                  <Card title="🔍 分析深度機率" size="small">
                    <ProbabilitySlider
                      name={['analysis_depth_probabilities', 'basic']}
                      label="基礎分析"
                      value={selectedKOL?.analysis_depth_probabilities?.basic || 0.2}
                      color="#722ed1"
                    />
                    <ProbabilitySlider
                      name={['analysis_depth_probabilities', 'detailed']}
                      label="詳細分析"
                      value={selectedKOL?.analysis_depth_probabilities?.detailed || 0.5}
                      color="#13c2c2"
                    />
                    <ProbabilitySlider
                      name={['analysis_depth_probabilities', 'comprehensive']}
                      label="全面分析"
                      value={selectedKOL?.analysis_depth_probabilities?.comprehensive || 0.3}
                      color="#eb2f96"
                    />
                  </Card>
                </Col>
                <Col span={16}>
                  <Card title="📏 文章長度機率" size="small">
                    <Row gutter={16}>
                      <Col span={12}>
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'short']}
                          label="簡短 (100字)"
                          value={selectedKOL?.content_length_probabilities?.short || 0.1}
                          color="#fa8c16"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'medium']}
                          label="中等 (200字)"
                          value={selectedKOL?.content_length_probabilities?.medium || 0.4}
                          color="#52c41a"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'long']}
                          label="詳細 (400字)"
                          value={selectedKOL?.content_length_probabilities?.long || 0.3}
                          color="#1890ff"
                        />
                      </Col>
                      <Col span={12}>
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'extended']}
                          label="深度 (600字)"
                          value={selectedKOL?.content_length_probabilities?.extended || 0.15}
                          color="#722ed1"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'comprehensive']}
                          label="全面 (800字)"
                          value={selectedKOL?.content_length_probabilities?.comprehensive || 0.05}
                          color="#eb2f96"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'thorough']}
                          label="徹底 (1000字)"
                          value={selectedKOL?.content_length_probabilities?.thorough || 0.0}
                          color="#f5222d"
                        />
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>
            </TabPane>

            {/* 基本設定 */}
            <TabPane tab="基本設定" key="basic">
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item name="nickname" label="暱稱">
                    <Input />
                  </Form.Item>
                  <Form.Item name="persona" label="人設">
                    <Input />
                  </Form.Item>
                  <Form.Item name="status" label="狀態">
                    <Select>
                      <Option value="active">啟用</Option>
                      <Option value="inactive">停用</Option>
                    </Select>
                  </Form.Item>
                  <Form.Item name="owner" label="擁有者">
                    <Input />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="email" label="Email">
                    <Input />
                  </Form.Item>
                  <Form.Item name="member_id" label="會員ID">
                    <Input />
                  </Form.Item>
                  <Form.Item name="target_audience" label="目標受眾">
                    <Input />
                  </Form.Item>
                  <Form.Item name="notes" label="備註">
                    <TextArea rows={3} />
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            {/* Prompt設定 */}
            <TabPane tab="Prompt設定" key="prompt">
              <Form.Item name="prompt_persona" label="Prompt人設">
                <TextArea rows={4} />
              </Form.Item>
              <Form.Item name="prompt_style" label="Prompt風格">
                <TextArea rows={4} />
              </Form.Item>
              <Form.Item name="prompt_guardrails" label="Prompt守則">
                <TextArea rows={3} />
              </Form.Item>
              <Form.Item name="prompt_skeleton" label="Prompt骨架">
                <TextArea rows={4} />
              </Form.Item>
            </TabPane>

            {/* 模型設定 */}
            <TabPane tab="模型設定" key="model">
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item name="model_id" label="模型ID">
                    <Input />
                  </Form.Item>
                  <Form.Item name="model_temp" label="溫度">
                    <InputNumber min={0} max={2} step={0.1} />
                  </Form.Item>
                  <Form.Item name="max_tokens" label="最大Token數">
                    <InputNumber min={100} max={2000} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="template_variant" label="模板變體">
                    <Input />
                  </Form.Item>
                  <Form.Item name="signature" label="簽名">
                    <Input />
                  </Form.Item>
                  <Form.Item name="emoji_pack" label="表情包">
                    <Input />
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            {/* 語氣設定 */}
            <TabPane tab="語氣設定" key="tone">
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item name="tone_formal" label="正式程度">
                    <Slider min={1} max={10} />
                  </Form.Item>
                  <Form.Item name="tone_emotion" label="情感程度">
                    <Slider min={1} max={10} />
                  </Form.Item>
                  <Form.Item name="tone_confidence" label="自信程度">
                    <Slider min={1} max={10} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="tone_urgency" label="緊急程度">
                    <Slider min={1} max={10} />
                  </Form.Item>
                  <Form.Item name="tone_interaction" label="互動程度">
                    <Slider min={1} max={10} />
                  </Form.Item>
                  <Form.Item name="question_ratio" label="問題比例">
                    <Slider min={0} max={1} step={0.1} />
                  </Form.Item>
                </Col>
              </Row>
            </TabPane>

            {/* 統計資料 */}
            <TabPane tab="統計資料" key="stats">
              <Descriptions column={2}>
                <Descriptions.Item label="總貼文數">
                  {selectedKOL?.total_posts || 0}
                </Descriptions.Item>
                <Descriptions.Item label="已發布貼文">
                  {selectedKOL?.published_posts || 0}
                </Descriptions.Item>
                <Descriptions.Item label="平均互動率">
                  {selectedKOL?.avg_interaction_rate ? `${(selectedKOL.avg_interaction_rate * 100).toFixed(1)}%` : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="最佳表現貼文">
                  {selectedKOL?.best_performing_post || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="創建時間">
                  {selectedKOL?.created_time || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="最後更新">
                  {selectedKOL?.last_updated || '-'}
                </Descriptions.Item>
              </Descriptions>
            </TabPane>
          </Tabs>
        </Form>
      </Modal>
    </div>
  );
};

export default KOLManagementPage;
