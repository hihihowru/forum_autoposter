import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Typography, 
  Row, 
  Col, 
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
  Descriptions,
  Tag,
  Space,
  Avatar,
  Breadcrumb,
  Table,
  Statistic,
  List
} from 'antd';
import { 
  UserOutlined, 
  EditOutlined, 
  SaveOutlined, 
  ReloadOutlined,
  SettingOutlined,
  BarChartOutlined,
  ArrowLeftOutlined,
  HomeOutlined,
  EyeOutlined,
  LikeOutlined,
  MessageOutlined,
  ShareAltOutlined,
  HeartOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Line, Column } from '@ant-design/plots';

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

const KOLDetailPage: React.FC = () => {
  const { serial } = useParams<{ serial: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [trendsLoading, setTrendsLoading] = useState(false);
  const [kolProfile, setKolProfile] = useState<KOLProfile | null>(null);
  const [trendsData, setTrendsData] = useState<any>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'personalization' | 'basic' | 'prompt' | 'model'>('personalization');
  const [form] = Form.useForm();

  // 載入KOL詳細資料
  const loadKOLProfile = async () => {
    if (!serial) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8001/kol-profiles/${serial}`);
      setKolProfile(response.data);
      form.setFieldsValue(response.data);
    } catch (error) {
      console.error('載入KOL詳細資料失敗:', error);
      message.error('載入KOL詳細資料失敗');
    } finally {
      setLoading(false);
    }
  };

  // 載入KOL趨勢數據
  const loadTrendsData = async () => {
    if (!serial) return;
    
    setTrendsLoading(true);
    try {
      const response = await axios.get(`http://localhost:8001/kol-profiles/${serial}/trends`);
      setTrendsData(response.data);
    } catch (error) {
      console.error('載入KOL趨勢數據失敗:', error);
      message.error('載入KOL趨勢數據失敗');
    } finally {
      setTrendsLoading(false);
    }
  };

  // 保存KOL設定
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      
      let endpoint = '';
      let data = {};
      
      switch (modalType) {
        case 'personalization':
          endpoint = `/kol-profiles/${serial}/personalization`;
          data = {
            content_style_probabilities: values.content_style_probabilities,
            analysis_depth_probabilities: values.analysis_depth_probabilities,
            content_length_probabilities: values.content_length_probabilities,
            question_ratio: values.question_ratio,
            tone_interaction: values.tone_interaction,
            tone_confidence: values.tone_confidence,
            tone_formal: values.tone_formal,
            interaction_starters: values.interaction_starters
          };
          break;
        case 'basic':
          endpoint = `/kol-profiles/${serial}/basic`;
          data = values;
          break;
        case 'prompt':
          endpoint = `/kol-profiles/${serial}/prompt`;
          data = values;
          break;
        case 'model':
          endpoint = `/kol-profiles/${serial}/model`;
          data = values;
          break;
        default:
          throw new Error('未知的Modal類型');
      }
      
      await axios.put(`http://localhost:8001${endpoint}`, data);
      
      message.success('KOL設定已保存');
      setModalVisible(false);
      await loadKOLProfile();
    } catch (error) {
      console.error('保存KOL設定失敗:', error);
      message.error('保存KOL設定失敗');
    } finally {
      setSaving(false);
    }
  };

  // 打開編輯Modal
  const handleEdit = (type: 'personalization' | 'basic' | 'prompt' | 'model') => {
    setModalType(type);
    setModalVisible(true);
    
    // 根據類型設置表單初始值
    if (kolProfile) {
      switch (type) {
        case 'personalization':
          form.setFieldsValue({
            content_style_probabilities: kolProfile.content_style_probabilities,
            analysis_depth_probabilities: kolProfile.analysis_depth_probabilities,
            content_length_probabilities: kolProfile.content_length_probabilities,
            question_ratio: kolProfile.question_ratio || 0.3,
            tone_interaction: kolProfile.tone_interaction || 6,
            tone_confidence: kolProfile.tone_confidence || 7,
            tone_formal: kolProfile.tone_formal || 5,
            interaction_starters: kolProfile.interaction_starters || []
          });
          break;
        case 'basic':
          form.setFieldsValue({
            nickname: kolProfile.nickname,
            persona: kolProfile.persona,
            status: kolProfile.status,
            owner: kolProfile.owner,
            email: kolProfile.email,
            member_id: kolProfile.member_id,
            target_audience: kolProfile.target_audience,
            whitelist: kolProfile.whitelist,
            notes: kolProfile.notes,
            tone_style: kolProfile.tone_style,
            typing_habit: kolProfile.typing_habit,
            backstory: kolProfile.backstory,
            expertise: kolProfile.expertise,
            common_terms: kolProfile.common_terms,
            colloquial_terms: kolProfile.colloquial_terms,
            interaction_starters: kolProfile.interaction_starters,
            require_finlab_api: kolProfile.require_finlab_api,
            allow_hashtags: kolProfile.allow_hashtags,
            data_source: kolProfile.data_source,
            interaction_threshold: kolProfile.interaction_threshold,
            post_times: kolProfile.post_times,
            content_types: kolProfile.content_types
          });
          break;
        case 'prompt':
          form.setFieldsValue({
            prompt_persona: kolProfile.prompt_persona,
            prompt_style: kolProfile.prompt_style,
            prompt_guardrails: kolProfile.prompt_guardrails,
            prompt_skeleton: kolProfile.prompt_skeleton,
            prompt_cta: kolProfile.prompt_cta,
            prompt_hashtags: kolProfile.prompt_hashtags
          });
          break;
        case 'model':
          form.setFieldsValue({
            model_id: kolProfile.model_id,
            model_temp: kolProfile.model_temp,
            max_tokens: kolProfile.max_tokens,
            template_variant: kolProfile.template_variant,
            signature: kolProfile.signature,
            emoji_pack: kolProfile.emoji_pack,
            title_openers: kolProfile.title_openers,
            title_signature_patterns: kolProfile.title_signature_patterns,
            title_tail_word: kolProfile.title_tail_word,
            title_banned_words: kolProfile.title_banned_words,
            title_style_examples: kolProfile.title_style_examples,
            title_retry_max: kolProfile.title_retry_max,
            tone_formal: kolProfile.tone_formal,
            tone_emotion: kolProfile.tone_emotion,
            tone_confidence: kolProfile.tone_confidence,
            tone_urgency: kolProfile.tone_urgency,
            tone_interaction: kolProfile.tone_interaction,
            question_ratio: kolProfile.question_ratio,
            humor_probability: kolProfile.humor_probability,
            humor_enabled: kolProfile.humor_enabled
          });
          break;
      }
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

  // 發文量每日趨勢圖表配置
  const dailyPostsChartConfig = {
    data: trendsData?.daily_posts_trend || [],
    xField: 'date',
    yField: 'count',
    point: {
      size: 5,
      shape: 'diamond',
    },
    label: {
      style: {
        fill: '#aaa',
      },
    },
  };

  // 互動趨勢圖表配置
  const interactionChartConfig = {
    data: trendsData?.interaction_trend || [],
    xField: 'date',
    yField: 'total_interactions',
    seriesField: 'status',
    point: {
      size: 4,
    },
  };

  // 發文列表表格列配置
  const postsColumns = [
    {
      title: '標題',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '股票',
      key: 'stock',
      width: 120,
      render: (_, record: any) => (
        <Tag color="blue">{record.stock_code} {record.stock_name}</Tag>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={
          status === 'published' ? 'green' : 
          status === 'draft' ? 'orange' : 
          status === 'deleted' ? 'red' : 'blue'
        }>
          {status === 'published' ? '已發布' : 
           status === 'draft' ? '草稿' : 
           status === 'deleted' ? '已刪除' : status}
        </Tag>
      ),
    },
    {
      title: '創建時間',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => date ? new Date(date).toLocaleString('zh-TW') : '-',
    },
    {
      title: '發布時間',
      dataIndex: 'published_at',
      key: 'published_at',
      width: 150,
      render: (date: string) => date ? new Date(date).toLocaleString('zh-TW') : '-',
    },
    {
      title: '互動數據',
      key: 'interactions',
      width: 200,
      render: (_, record: any) => (
        <Space size="small">
          <span><EyeOutlined /> {record.views}</span>
          <span><LikeOutlined /> {record.likes}</span>
          <span><MessageOutlined /> {record.comments}</span>
          <span><ShareAltOutlined /> {record.shares}</span>
        </Space>
      ),
    },
    {
      title: '總互動',
      dataIndex: 'total_interactions',
      key: 'total_interactions',
      width: 100,
      sorter: (a: any, b: any) => a.total_interactions - b.total_interactions,
      render: (total: number) => (
        <Text strong style={{ color: total > 100 ? '#52c41a' : total > 50 ? '#faad14' : '#d9d9d9' }}>
          {total}
        </Text>
      ),
    },
  ];

  useEffect(() => {
    loadKOLProfile();
    loadTrendsData();
  }, [serial]);

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>載入KOL資料中...</div>
      </div>
    );
  }

  if (!kolProfile) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Alert message="找不到指定的KOL" type="error" />
        <Button 
          style={{ marginTop: 16 }} 
          onClick={() => navigate('/content-management/kols')}
        >
          返回KOL列表
        </Button>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 麵包屑導航 */}
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item>
          <HomeOutlined />
          <span onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>首頁</span>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <span onClick={() => navigate('/content-management/kols')} style={{ cursor: 'pointer' }}>KOL管理</span>
        </Breadcrumb.Item>
        <Breadcrumb.Item>{kolProfile.nickname}</Breadcrumb.Item>
      </Breadcrumb>

      <Card>
        {/* KOL基本資訊標題 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Avatar 
              size={64} 
              icon={<UserOutlined />} 
              style={{ backgroundColor: kolProfile.status === 'active' ? '#52c41a' : '#d9d9d9', marginRight: 16 }}
            />
            <div>
              <Title level={2} style={{ margin: 0 }}>
                {kolProfile.nickname} ({kolProfile.serial})
              </Title>
              <Space>
                <Tag color="blue">{kolProfile.persona}</Tag>
                <Tag color={kolProfile.status === 'active' ? 'green' : 'red'}>
                  {kolProfile.status === 'active' ? '啟用' : '停用'}
                </Tag>
                <Text type="secondary">擁有者: {kolProfile.owner}</Text>
              </Space>
            </div>
          </div>
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/content-management/kols')}
            >
              返回列表
            </Button>
            <Button 
              type="primary" 
              icon={<EditOutlined />}
              onClick={() => handleEdit('personalization')}
            >
              編輯個人化設定
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadKOLProfile}
              loading={loading}
            >
              刷新
            </Button>
          </Space>
        </div>


        {/* 詳細資訊標籤頁 */}
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
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>技術分析</Text>
                      <Text style={{ color: '#1890ff' }}>{(kolProfile.content_style_probabilities.technical * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.content_style_probabilities.technical * 100)} 
                      strokeColor="#1890ff"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>輕鬆隨性</Text>
                      <Text style={{ color: '#52c41a' }}>{(kolProfile.content_style_probabilities.casual * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.content_style_probabilities.casual * 100)} 
                      strokeColor="#52c41a"
                    />
                  </div>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="📝 內容風格機率 (續)" size="small">
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>專業商務</Text>
                      <Text style={{ color: '#faad14' }}>{(kolProfile.content_style_probabilities.professional * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.content_style_probabilities.professional * 100)} 
                      strokeColor="#faad14"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>幽默風趣</Text>
                      <Text style={{ color: '#f5222d' }}>{(kolProfile.content_style_probabilities.humorous * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.content_style_probabilities.humorous * 100)} 
                      strokeColor="#f5222d"
                    />
                  </div>
                </Card>
              </Col>
            </Row>

            <Row gutter={24} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Card title="🔍 分析深度機率" size="small">
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>基礎分析</Text>
                      <Text style={{ color: '#722ed1' }}>{(kolProfile.analysis_depth_probabilities.basic * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.analysis_depth_probabilities.basic * 100)} 
                      strokeColor="#722ed1"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>詳細分析</Text>
                      <Text style={{ color: '#13c2c2' }}>{(kolProfile.analysis_depth_probabilities.detailed * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.analysis_depth_probabilities.detailed * 100)} 
                      strokeColor="#13c2c2"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>全面分析</Text>
                      <Text style={{ color: '#eb2f96' }}>{(kolProfile.analysis_depth_probabilities.comprehensive * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={Math.round(kolProfile.analysis_depth_probabilities.comprehensive * 100)} 
                      strokeColor="#eb2f96"
                    />
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card title="🎭 語氣參數" size="small">
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>正式程度</Text>
                      <Text style={{ color: '#1890ff' }}>{kolProfile.tone_formal || 0}/10</Text>
                    </div>
                    <Progress 
                      percent={(kolProfile.tone_formal || 0) * 10} 
                      strokeColor="#1890ff"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>情感程度</Text>
                      <Text style={{ color: '#52c41a' }}>{kolProfile.tone_emotion || 0}/10</Text>
                    </div>
                    <Progress 
                      percent={(kolProfile.tone_emotion || 0) * 10} 
                      strokeColor="#52c41a"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>自信程度</Text>
                      <Text style={{ color: '#faad14' }}>{kolProfile.tone_confidence || 0}/10</Text>
                    </div>
                    <Progress 
                      percent={(kolProfile.tone_confidence || 0) * 10} 
                      strokeColor="#faad14"
                    />
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card title="💬 互動參數" size="small">
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>緊急程度</Text>
                      <Text style={{ color: '#f5222d' }}>{kolProfile.tone_urgency || 0}/10</Text>
                    </div>
                    <Progress 
                      percent={(kolProfile.tone_urgency || 0) * 10} 
                      strokeColor="#f5222d"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>互動程度</Text>
                      <Text style={{ color: '#722ed1' }}>{kolProfile.tone_interaction || 0}/10</Text>
                    </div>
                    <Progress 
                      percent={(kolProfile.tone_interaction || 0) * 10} 
                      strokeColor="#722ed1"
                    />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text strong>問題比例</Text>
                      <Text style={{ color: '#13c2c2' }}>{((kolProfile.question_ratio || 0) * 100).toFixed(1)}%</Text>
                    </div>
                    <Progress 
                      percent={(kolProfile.question_ratio || 0) * 100} 
                      strokeColor="#13c2c2"
                    />
                  </div>
                </Card>
              </Col>
              <Col span={16}>
                <Card title="📏 文章長度機率" size="small">
                  <Row gutter={16}>
                    <Col span={12}>
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>簡短 (100字)</Text>
                          <Text style={{ color: '#fa8c16' }}>{(kolProfile.content_length_probabilities.short * 100).toFixed(1)}%</Text>
                        </div>
                        <Progress 
                          percent={Math.round(kolProfile.content_length_probabilities.short * 100)} 
                          strokeColor="#fa8c16"
                          size="small"
                        />
                      </div>
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>中等 (200字)</Text>
                          <Text style={{ color: '#52c41a' }}>{(kolProfile.content_length_probabilities.medium * 100).toFixed(1)}%</Text>
                        </div>
                        <Progress 
                          percent={Math.round(kolProfile.content_length_probabilities.medium * 100)} 
                          strokeColor="#52c41a"
                          size="small"
                        />
                      </div>
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>詳細 (400字)</Text>
                          <Text style={{ color: '#1890ff' }}>{(kolProfile.content_length_probabilities.long * 100).toFixed(1)}%</Text>
                        </div>
                        <Progress 
                          percent={Math.round(kolProfile.content_length_probabilities.long * 100)} 
                          strokeColor="#1890ff"
                          size="small"
                        />
                      </div>
                    </Col>
                    <Col span={12}>
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>深度 (600字)</Text>
                          <Text style={{ color: '#722ed1' }}>{(kolProfile.content_length_probabilities.extended * 100).toFixed(1)}%</Text>
                        </div>
                        <Progress 
                          percent={Math.round(kolProfile.content_length_probabilities.extended * 100)} 
                          strokeColor="#722ed1"
                          size="small"
                        />
                      </div>
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>全面 (800字)</Text>
                          <Text style={{ color: '#eb2f96' }}>{(kolProfile.content_length_probabilities.comprehensive * 100).toFixed(1)}%</Text>
                        </div>
                        <Progress 
                          percent={Math.round(kolProfile.content_length_probabilities.comprehensive * 100)} 
                          strokeColor="#eb2f96"
                          size="small"
                        />
                      </div>
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>徹底 (1000字)</Text>
                          <Text style={{ color: '#f5222d' }}>{(kolProfile.content_length_probabilities.thorough * 100).toFixed(1)}%</Text>
                        </div>
                        <Progress 
                          percent={Math.round(kolProfile.content_length_probabilities.thorough * 100)} 
                          strokeColor="#f5222d"
                          size="small"
                        />
                      </div>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* 基本設定 */}
          <TabPane 
            tab={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                基本設定
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EditOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit('basic');
                  }}
                />
              </div>
            } 
            key="basic"
          >
            <Descriptions column={2} bordered>
              <Descriptions.Item label="暱稱">{kolProfile.nickname}</Descriptions.Item>
              <Descriptions.Item label="人設">{kolProfile.persona}</Descriptions.Item>
              <Descriptions.Item label="狀態">
                <Tag color={kolProfile.status === 'active' ? 'green' : 'red'}>
                  {kolProfile.status === 'active' ? '啟用' : '停用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="擁有者">{kolProfile.owner}</Descriptions.Item>
              <Descriptions.Item label="Email">{kolProfile.email}</Descriptions.Item>
              <Descriptions.Item label="會員ID">{kolProfile.member_id}</Descriptions.Item>
              <Descriptions.Item label="目標受眾">{kolProfile.target_audience}</Descriptions.Item>
              <Descriptions.Item label="白名單">
                <Tag color={kolProfile.whitelist ? 'green' : 'red'}>
                  {kolProfile.whitelist ? '是' : '否'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="備註" span={2}>
                {kolProfile.notes || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="語氣風格" span={2}>
                {kolProfile.tone_style || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="打字習慣" span={2}>
                {kolProfile.typing_habit || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="背景故事" span={2}>
                {kolProfile.backstory || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="專業領域" span={2}>
                {kolProfile.expertise || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="常用術語" span={2}>
                {kolProfile.common_terms || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="口語化用詞" span={2}>
                {kolProfile.colloquial_terms || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="互動開場白" span={2}>
                {kolProfile.interaction_starters ? kolProfile.interaction_starters.join(', ') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="需要FinLab API">
                <Tag color={kolProfile.require_finlab_api ? 'green' : 'red'}>
                  {kolProfile.require_finlab_api ? '是' : '否'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="允許Hashtag">
                <Tag color={kolProfile.allow_hashtags ? 'green' : 'red'}>
                  {kolProfile.allow_hashtags ? '是' : '否'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="數據源">{kolProfile.data_source || '-'}</Descriptions.Item>
              <Descriptions.Item label="互動閾值">{kolProfile.interaction_threshold || '-'}</Descriptions.Item>
              <Descriptions.Item label="發文時間">{kolProfile.post_times || '-'}</Descriptions.Item>
              <Descriptions.Item label="內容類型" span={2}>
                {kolProfile.content_types ? kolProfile.content_types.join(', ') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="創建時間">{kolProfile.created_time || '-'}</Descriptions.Item>
              <Descriptions.Item label="最後更新">{kolProfile.last_updated || '-'}</Descriptions.Item>
            </Descriptions>
          </TabPane>

          {/* Prompt設定 */}
          <TabPane 
            tab={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                Prompt設定
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EditOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit('prompt');
                  }}
                />
              </div>
            } 
            key="prompt"
          >
            <Row gutter={24}>
              <Col span={12}>
                <Card title="Prompt人設" size="small">
                  <Paragraph>{kolProfile.prompt_persona || '-'}</Paragraph>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Prompt風格" size="small">
                  <Paragraph>{kolProfile.prompt_style || '-'}</Paragraph>
                </Card>
              </Col>
            </Row>
            <Row gutter={24} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Card title="Prompt守則" size="small">
                  <Paragraph>{kolProfile.prompt_guardrails || '-'}</Paragraph>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Prompt骨架" size="small">
                  <Paragraph>{kolProfile.prompt_skeleton || '-'}</Paragraph>
                </Card>
              </Col>
            </Row>
            <Row gutter={24} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Card title="Prompt CTA" size="small">
                  <Paragraph>{kolProfile.prompt_cta || '-'}</Paragraph>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Prompt Hashtags" size="small">
                  <Paragraph>{kolProfile.prompt_hashtags || '-'}</Paragraph>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* 模型設定 */}
          <TabPane 
            tab={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                模型設定
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EditOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit('model');
                  }}
                />
              </div>
            } 
            key="model"
          >
            <Descriptions column={2} bordered>
              <Descriptions.Item label="模型ID">{kolProfile.model_id || '-'}</Descriptions.Item>
              <Descriptions.Item label="溫度">{kolProfile.model_temp || '-'}</Descriptions.Item>
              <Descriptions.Item label="最大Token數">{kolProfile.max_tokens || '-'}</Descriptions.Item>
              <Descriptions.Item label="模板變體">{kolProfile.template_variant || '-'}</Descriptions.Item>
              <Descriptions.Item label="簽名">{kolProfile.signature || '-'}</Descriptions.Item>
              <Descriptions.Item label="表情包">{kolProfile.emoji_pack || '-'}</Descriptions.Item>
              <Descriptions.Item label="標題開場白" span={2}>
                {kolProfile.title_openers ? kolProfile.title_openers.join(', ') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="標題簽名模式" span={2}>
                {kolProfile.title_signature_patterns ? kolProfile.title_signature_patterns.join(', ') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="標題結尾詞">{kolProfile.title_tail_word || '-'}</Descriptions.Item>
              <Descriptions.Item label="標題重試次數">{kolProfile.title_retry_max || '-'}</Descriptions.Item>
              <Descriptions.Item label="標題禁用詞" span={2}>
                {kolProfile.title_banned_words ? kolProfile.title_banned_words.join(', ') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="標題風格範例" span={2}>
                {kolProfile.title_style_examples ? kolProfile.title_style_examples.join(', ') : '-'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>


          {/* 統計資料 */}
          <TabPane tab="統計資料" key="stats">
            {/* 基本統計 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Card size="small">
                  <Statistic 
                    title="總貼文數" 
                    value={kolProfile.total_posts || 0} 
                    prefix={<BarChartOutlined />}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic 
                    title="已發布貼文" 
                    value={kolProfile.published_posts || 0} 
                    prefix={<BarChartOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic 
                    title="平均互動率" 
                    value={kolProfile.avg_interaction_rate ? (kolProfile.avg_interaction_rate * 100).toFixed(1) : 0} 
                    suffix="%"
                    prefix={<HeartOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic 
                    title="最佳表現貼文" 
                    value={kolProfile.best_performing_post ? '有' : '無'} 
                    prefix={<BarChartOutlined />}
                    valueStyle={{ color: '#faad14' }}
                  />
                </Card>
              </Col>
            </Row>

            {/* 趨勢圖表 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={12}>
                <Card title="📈 發文量每日趨勢" size="small" loading={trendsLoading}>
                  {trendsData?.daily_posts_trend?.length > 0 ? (
                    <Line {...dailyPostsChartConfig} height={300} />
                  ) : (
                    <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
                      暫無數據
                    </div>
                  )}
                </Card>
              </Col>
              <Col span={12}>
                <Card title="📊 互動趨勢" size="small" loading={trendsLoading}>
                  {trendsData?.interaction_trend?.length > 0 ? (
                    <Line {...interactionChartConfig} height={300} />
                  ) : (
                    <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
                      暫無數據
                    </div>
                  )}
                </Card>
              </Col>
            </Row>

            {/* 發文列表 */}
            <Card title="📝 發文列表" size="small" loading={trendsLoading}>
              <Table
                columns={postsColumns}
                dataSource={trendsData?.published_posts_list || []}
                rowKey="post_id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 篇貼文`,
                }}
                scroll={{ x: 1200 }}
                size="small"
              />
            </Card>
          </TabPane>
        </Tabs>
      </Card>

      {/* 編輯Modal */}
      <Modal
        title={`編輯${modalType === 'personalization' ? '個人化設定' : 
                        modalType === 'basic' ? '基本設定' : 
                        modalType === 'prompt' ? 'Prompt設定' : '模型設定'}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={800}
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
          {modalType === 'personalization' && (
            <Alert
              message="調整KOL的內容生成機率參數"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}
          {modalType === 'basic' && (
            <Alert
              message="編輯KOL的基本資訊和設定"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}
          {modalType === 'prompt' && (
            <Alert
              message="編輯KOL的Prompt相關設定"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}
          {modalType === 'model' && (
            <Alert
              message="編輯KOL的模型和標題相關設定"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}
          
          {modalType === 'personalization' && (
            <>
              <Row gutter={24}>
                <Col span={12}>
                  <Card title="📝 內容風格機率" size="small">
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'technical']}
                      label="技術分析"
                      value={kolProfile?.content_style_probabilities?.technical || 0.3}
                      color="#1890ff"
                    />
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'casual']}
                      label="輕鬆隨性"
                      value={kolProfile?.content_style_probabilities?.casual || 0.4}
                      color="#52c41a"
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="📝 內容風格機率 (續)" size="small">
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'professional']}
                      label="專業商務"
                      value={kolProfile?.content_style_probabilities?.professional || 0.2}
                      color="#faad14"
                    />
                    <ProbabilitySlider
                      name={['content_style_probabilities', 'humorous']}
                      label="幽默風趣"
                      value={kolProfile?.content_style_probabilities?.humorous || 0.1}
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
                      value={kolProfile?.analysis_depth_probabilities?.basic || 0.2}
                      color="#722ed1"
                    />
                    <ProbabilitySlider
                      name={['analysis_depth_probabilities', 'detailed']}
                      label="詳細分析"
                      value={kolProfile?.analysis_depth_probabilities?.detailed || 0.5}
                      color="#13c2c2"
                    />
                    <ProbabilitySlider
                      name={['analysis_depth_probabilities', 'comprehensive']}
                      label="全面分析"
                      value={kolProfile?.analysis_depth_probabilities?.comprehensive || 0.3}
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
                          value={kolProfile?.content_length_probabilities?.short || 0.1}
                          color="#fa8c16"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'medium']}
                          label="中等 (200字)"
                          value={kolProfile?.content_length_probabilities?.medium || 0.4}
                          color="#52c41a"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'long']}
                          label="詳細 (400字)"
                          value={kolProfile?.content_length_probabilities?.long || 0.3}
                          color="#1890ff"
                        />
                      </Col>
                      <Col span={12}>
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'extended']}
                          label="深度 (600字)"
                          value={kolProfile?.content_length_probabilities?.extended || 0.15}
                          color="#722ed1"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'comprehensive']}
                          label="全面 (800字)"
                          value={kolProfile?.content_length_probabilities?.comprehensive || 0.05}
                          color="#eb2f96"
                        />
                        <ProbabilitySlider
                          name={['content_length_probabilities', 'thorough']}
                          label="徹底 (1000字)"
                          value={kolProfile?.content_length_probabilities?.thorough || 0.0}
                          color="#f5222d"
                        />
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>

              <Row gutter={24} style={{ marginTop: 16 }}>
                <Col span={24}>
                  <Card title="💬 發文形態隨機性" size="small">
                    <Alert
                      message="控制KOL發文時的提問vs發表看法比例"
                      type="info"
                      showIcon
                      style={{ marginBottom: 16 }}
                    />
                    <Row gutter={24}>
                      <Col span={12}>
                        <Form.Item 
                          label="提問比例" 
                          name="question_ratio"
                          tooltip="0.0 = 總是發表看法, 1.0 = 總是提問"
                        >
                          <Slider
                            min={0}
                            max={1}
                            step={0.1}
                            marks={{
                              0: '0%',
                              0.2: '20%',
                              0.4: '40%',
                              0.6: '60%',
                              0.8: '80%',
                              1.0: '100%'
                            }}
                            tipFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                          />
                        </Form.Item>
                        <Form.Item 
                          label="互動語調" 
                          name="tone_interaction"
                          tooltip="提問時的互動語調強度 (1-10)"
                        >
                          <Slider
                            min={1}
                            max={10}
                            marks={{
                              1: '1',
                              3: '3',
                              5: '5',
                              7: '7',
                              10: '10'
                            }}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item 
                          label="自信程度" 
                          name="tone_confidence"
                          tooltip="發表看法時的自信程度 (1-10)"
                        >
                          <Slider
                            min={1}
                            max={10}
                            marks={{
                              1: '1',
                              3: '3',
                              5: '5',
                              7: '7',
                              10: '10'
                            }}
                          />
                        </Form.Item>
                        <Form.Item 
                          label="正式程度" 
                          name="tone_formal"
                          tooltip="發文的正式程度 (1-10)"
                        >
                          <Slider
                            min={1}
                            max={10}
                            marks={{
                              1: '1',
                              3: '3',
                              5: '5',
                              7: '7',
                              10: '10'
                            }}
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                    <Row gutter={24}>
                      <Col span={24}>
                        <Form.Item 
                          label="互動開場白" 
                          name="interaction_starters"
                          tooltip="提問時使用的開場白，系統會隨機選擇"
                        >
                          <Select 
                            mode="tags" 
                            placeholder="輸入互動開場白，按Enter添加"
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>
            </>
          )}

          {modalType === 'basic' && (
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item label="暱稱" name="nickname">
                  <Input />
                </Form.Item>
                <Form.Item label="人設" name="persona">
                  <Input />
                </Form.Item>
                <Form.Item label="狀態" name="status">
                  <Select>
                    <Option value="active">啟用</Option>
                    <Option value="inactive">停用</Option>
                  </Select>
                </Form.Item>
                <Form.Item label="擁有者" name="owner">
                  <Input />
                </Form.Item>
                <Form.Item label="Email" name="email">
                  <Input />
                </Form.Item>
                <Form.Item label="會員ID" name="member_id">
                  <Input />
                </Form.Item>
                <Form.Item label="目標受眾" name="target_audience">
                  <Input />
                </Form.Item>
                <Form.Item label="白名單" name="whitelist" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="備註" name="notes">
                  <TextArea rows={3} />
                </Form.Item>
                <Form.Item label="語氣風格" name="tone_style">
                  <TextArea rows={2} />
                </Form.Item>
                <Form.Item label="打字習慣" name="typing_habit">
                  <TextArea rows={2} />
                </Form.Item>
                <Form.Item label="背景故事" name="backstory">
                  <TextArea rows={2} />
                </Form.Item>
                <Form.Item label="專業領域" name="expertise">
                  <TextArea rows={2} />
                </Form.Item>
                <Form.Item label="常用術語" name="common_terms">
                  <TextArea rows={2} />
                </Form.Item>
                <Form.Item label="口語化用詞" name="colloquial_terms">
                  <TextArea rows={2} />
                </Form.Item>
                <Form.Item label="互動開場白" name="interaction_starters">
                  <Select mode="tags" placeholder="輸入互動開場白，按Enter添加" />
                </Form.Item>
                <Form.Item label="需要FinLab API" name="require_finlab_api" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item label="允許Hashtag" name="allow_hashtags" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item label="數據源" name="data_source">
                  <Input />
                </Form.Item>
                <Form.Item label="互動閾值" name="interaction_threshold">
                  <InputNumber min={0} max={1} step={0.1} />
                </Form.Item>
                <Form.Item label="發文時間" name="post_times">
                  <Input placeholder="例如: 09:00,15:00" />
                </Form.Item>
                <Form.Item label="內容類型" name="content_types">
                  <Select mode="tags" placeholder="輸入內容類型，按Enter添加" />
                </Form.Item>
              </Col>
            </Row>
          )}

          {modalType === 'prompt' && (
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item label="Prompt人設" name="prompt_persona">
                  <TextArea rows={4} />
                </Form.Item>
                <Form.Item label="Prompt風格" name="prompt_style">
                  <TextArea rows={4} />
                </Form.Item>
                <Form.Item label="Prompt守則" name="prompt_guardrails">
                  <TextArea rows={4} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Prompt骨架" name="prompt_skeleton">
                  <TextArea rows={4} />
                </Form.Item>
                <Form.Item label="Prompt CTA" name="prompt_cta">
                  <TextArea rows={4} />
                </Form.Item>
                <Form.Item label="Prompt Hashtags" name="prompt_hashtags">
                  <TextArea rows={4} />
                </Form.Item>
              </Col>
            </Row>
          )}

          {modalType === 'model' && (
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item label="模型ID" name="model_id">
                  <Input />
                </Form.Item>
                <Form.Item label="溫度" name="model_temp">
                  <InputNumber min={0} max={2} step={0.1} />
                </Form.Item>
                <Form.Item label="最大Token數" name="max_tokens">
                  <InputNumber min={1} max={4000} />
                </Form.Item>
                <Form.Item label="模板變體" name="template_variant">
                  <Input />
                </Form.Item>
                <Form.Item label="簽名" name="signature">
                  <Input />
                </Form.Item>
                <Form.Item label="表情包" name="emoji_pack">
                  <Input />
                </Form.Item>
                <Form.Item label="標題開場白" name="title_openers">
                  <Select mode="tags" placeholder="輸入標題開場白，按Enter添加" />
                </Form.Item>
                <Form.Item label="標題簽名模式" name="title_signature_patterns">
                  <Select mode="tags" placeholder="輸入標題簽名模式，按Enter添加" />
                </Form.Item>
                <Form.Item label="標題結尾詞" name="title_tail_word">
                  <Input />
                </Form.Item>
                <Form.Item label="標題重試次數" name="title_retry_max">
                  <InputNumber min={1} max={10} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="標題禁用詞" name="title_banned_words">
                  <Select mode="tags" placeholder="輸入標題禁用詞，按Enter添加" />
                </Form.Item>
                <Form.Item label="標題風格範例" name="title_style_examples">
                  <Select mode="tags" placeholder="輸入標題風格範例，按Enter添加" />
                </Form.Item>
                <Form.Item label="正式程度" name="tone_formal">
                  <Slider min={0} max={10} step={1} />
                </Form.Item>
                <Form.Item label="情感程度" name="tone_emotion">
                  <Slider min={0} max={10} step={1} />
                </Form.Item>
                <Form.Item label="自信程度" name="tone_confidence">
                  <Slider min={0} max={10} step={1} />
                </Form.Item>
                <Form.Item label="緊急程度" name="tone_urgency">
                  <Slider min={0} max={10} step={1} />
                </Form.Item>
                <Form.Item label="互動程度" name="tone_interaction">
                  <Slider min={0} max={10} step={1} />
                </Form.Item>
                <Form.Item label="問題比例" name="question_ratio">
                  <Slider min={0} max={1} step={0.1} />
                </Form.Item>
                <Form.Item label="幽默機率" name="humor_probability">
                  <Slider min={0} max={1} step={0.1} />
                </Form.Item>
                <Form.Item label="啟用幽默" name="humor_enabled" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </Col>
            </Row>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default KOLDetailPage;
