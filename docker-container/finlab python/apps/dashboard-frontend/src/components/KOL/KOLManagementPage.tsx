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
import { getApiBaseUrl } from '../../config/api';

const API_BASE_URL = getApiBaseUrl();
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
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [reviewModalVisible, setReviewModalVisible] = useState(false);
  const [aiGeneratedProfile, setAiGeneratedProfile] = useState<any>(null);
  const [form] = Form.useForm();
  const [createForm] = Form.useForm();

  // 測試狀態
  const [testingLogin, setTestingLogin] = useState(false);
  const [testLoginResult, setTestLoginResult] = useState<{ success: boolean; message: string } | null>(null);
  const [testingNickname, setTestingNickname] = useState(false);
  const [testNicknameResult, setTestNicknameResult] = useState<{ success: boolean; message: string } | null>(null);

  // 載入KOL列表
  const loadKOLProfiles = async () => {
    setLoading(true);
    try {
      // 使用 Railway API URL
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

      await axios.put(`${API_BASE_URL}/api/kol/${selectedKOL?.serial}/personalization`, {
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

  // 打開創建 KOL Modal
  const handleOpenCreateModal = () => {
    createForm.resetFields();
    setAiGeneratedProfile(null);
    setCreateModalVisible(true);
    setTestLoginResult(null);
    setTestNicknameResult(null);
    console.log('📝 打開創建 KOL Modal');
  };

  // 測試 Bearer Token（登入驗證）
  const handleTestLogin = async () => {
    try {
      const email = createForm.getFieldValue('email');
      const password = createForm.getFieldValue('password');

      if (!email || !password) {
        message.warning('請先填寫郵箱和密碼');
        return;
      }

      setTestingLogin(true);
      setTestLoginResult(null);
      console.log('🔐 測試登入:', { email, password: '***' });

      const response = await axios.post(`${API_BASE_URL}/api/kol/test-login`, {
        email,
        password
      });

      console.log('🔐 測試登入響應:', response.data);

      if (response.data.success) {
        setTestLoginResult({
          success: true,
          message: `✅ 登入成功！Bearer Token: ${response.data.token.substring(0, 20)}...`
        });
        message.success('登入成功！Bearer Token 已獲取');
      } else {
        setTestLoginResult({
          success: false,
          message: `❌ 登入失敗: ${response.data.error}`
        });
        message.error(`登入失敗: ${response.data.error}`);
      }
    } catch (error: any) {
      console.error('❌ 測試登入異常:', error);
      const errorMsg = error.response?.data?.error || error.message || '未知錯誤';
      setTestLoginResult({
        success: false,
        message: `❌ 測試失敗: ${errorMsg}`
      });
      message.error(`測試失敗: ${errorMsg}`);
    } finally {
      setTestingLogin(false);
    }
  };

  // 測試暱稱是否可用
  const handleTestNickname = async () => {
    try {
      const email = createForm.getFieldValue('email');
      const password = createForm.getFieldValue('password');
      const nickname = createForm.getFieldValue('nickname');

      if (!email || !password) {
        message.warning('請先填寫郵箱和密碼');
        return;
      }

      if (!nickname) {
        message.warning('請先填寫暱稱');
        return;
      }

      setTestingNickname(true);
      setTestNicknameResult(null);
      console.log('📝 測試暱稱:', { email, password: '***', nickname });

      const response = await axios.post(`${API_BASE_URL}/api/kol/test-nickname`, {
        email,
        password,
        nickname
      });

      console.log('📝 測試暱稱響應:', response.data);

      if (response.data.success) {
        setTestNicknameResult({
          success: true,
          message: `✅ 暱稱可用！更新後的暱稱: ${response.data.new_nickname}`
        });
        message.success('暱稱可用！');
      } else {
        setTestNicknameResult({
          success: false,
          message: `❌ 暱稱不可用: ${response.data.error}`
        });
        message.error(`暱稱不可用: ${response.data.error}`);
      }
    } catch (error: any) {
      console.error('❌ 測試暱稱異常:', error);
      const errorMsg = error.response?.data?.error || error.message || '未知錯誤';
      setTestNicknameResult({
        success: false,
        message: `❌ 測試失敗: ${errorMsg}`
      });
      message.error(`測試失敗: ${errorMsg}`);
    } finally {
      setTestingNickname(false);
    }
  };

  // 確認創建 KOL（顯示確認對話框）
  const handleCreateKOL = async () => {
    try {
      const values = await createForm.validateFields();
      console.log('📝 表單驗證通過，準備顯示確認對話框');

      // 檢查是否已通過測試
      const hasTestedLogin = testLoginResult?.success === true;
      const hasTestedNickname = testNicknameResult?.success === true;

      // 構建確認訊息
      let confirmMessage = '確定要創建此 KOL 嗎？\n\n';
      confirmMessage += `郵箱: ${values.email}\n`;
      confirmMessage += `暱稱: ${values.nickname}\n`;
      confirmMessage += `會員ID: ${values.member_id || '(自動獲取)'}\n\n`;

      if (hasTestedLogin && hasTestedNickname) {
        confirmMessage += '✅ 登入測試: 通過\n';
        confirmMessage += '✅ 暱稱測試: 通過\n\n';
        confirmMessage += '所有驗證已通過，可以安全創建。';
      } else {
        confirmMessage += '⚠️ 建議:\n';
        if (!hasTestedLogin) {
          confirmMessage += '• 尚未測試登入，建議先點擊密碼旁的「測試」按鈕\n';
        }
        if (!hasTestedNickname) {
          confirmMessage += '• 尚未測試暱稱，建議先點擊暱稱旁的「測試」按鈕\n';
        }
        confirmMessage += '\n確定要繼續創建嗎？（未測試可能導致創建失敗）';
      }

      // 顯示確認對話框
      Modal.confirm({
        title: '確認創建 KOL',
        content: confirmMessage,
        okText: '確認創建',
        cancelText: '取消',
        onOk: async () => {
          await proceedWithCreation(values);
        },
        okButtonProps: {
          danger: !hasTestedLogin || !hasTestedNickname
        }
      });

    } catch (error) {
      console.error('❌ 表單驗證失敗:', error);
      message.error('請填寫所有必填欄位');
    }
  };

  // 實際執行創建（確認後）
  const proceedWithCreation = async (values: any) => {
    try {
      setSaving(true);
      console.log('🚀 開始創建 KOL...');
      console.log('📝 收集到的值:', values);

      const payload = {
        email: values.email,
        password: values.password,
        nickname: values.nickname,
        member_id: values.member_id || '',  // 新增 member_id 欄位
        ai_description: values.ai_description || ''
      };

      console.log('📤 發送到後端的 payload:', {
        ...payload,
        password: '***'  // 隱藏密碼
      });

      const response = await axios.post(`${API_BASE_URL}/api/kol/create`, payload);
      console.log('📥 後端響應:', response.data);

      if (response.data.success) {
        console.log('✅ KOL 創建成功!', {
          serial: response.data.data.serial,
          nickname: response.data.data.nickname,
          member_id: response.data.data.member_id,
          email: response.data.data.email,
          ai_generated: response.data.data.ai_generated
        });

        message.success(`KOL 創建成功！Serial: ${response.data.data.serial}`);

        // 如果有 AI 生成的資料，顯示審查 modal
        if (response.data.data.ai_generated && response.data.data.ai_profile) {
          console.log('🤖 有 AI 生成的個性化資料，打開審查 Modal');
          setAiGeneratedProfile({
            ...response.data.data.ai_profile,
            serial: response.data.data.serial,
            nickname: response.data.data.nickname,
            email: response.data.data.email,
            member_id: response.data.data.member_id
          });
          setCreateModalVisible(false);
          setReviewModalVisible(true);
        } else {
          console.log('📋 無 AI 生成資料，直接刷新列表');
          // 沒有 AI 生成，直接關閉並刷新列表
          setCreateModalVisible(false);
          await loadKOLProfiles();
        }
      } else {
        // 處理錯誤
        const errorMsg = response.data.error || '創建失敗';
        const phase = response.data.phase;

        console.error('❌ 創建失敗:', {
          error: errorMsg,
          phase: phase,
          detail: response.data.detail
        });

        if (phase === 'login') {
          message.error(`登入失敗: ${errorMsg}`);
        } else if (phase === 'nickname_update') {
          message.error(`暱稱更新失敗: ${errorMsg}。${response.data.detail || ''}`);
        } else {
          message.error(errorMsg);
        }
      }
    } catch (error: any) {
      console.error('❌ 創建 KOL 異常:', error);
      console.error('❌ 錯誤詳情:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });

      const errorMsg = error.response?.data?.error || error.message || '創建 KOL 失敗';
      message.error(errorMsg);
    } finally {
      setSaving(false);
      console.log('🔚 創建 KOL 流程結束');
    }
  };

  // 確認 AI 生成的資料
  const handleConfirmAIProfile = async () => {
    try {
      message.success('AI 生成的資料已確認');
      setReviewModalVisible(false);
      await loadKOLProfiles();
    } catch (error) {
      message.error('確認失敗');
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
          <Space>
            <Button
              type="primary"
              icon={<UserOutlined />}
              onClick={handleOpenCreateModal}
            >
              創建KOL角色
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadKOLProfiles}
              loading={loading}
            >
              刷新
            </Button>
          </Space>
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
              <Form.Item
                name="prompt_persona"
                label="Prompt人設"
                tooltip="定義 KOL 的角色人設，例如：專業分析師、技術派達人、鄉民代表等"
              >
                <Select
                  mode="tags"
                  placeholder="選擇範本或自訂輸入"
                  maxTagCount={1}
                  style={{ width: '100%' }}
                  dropdownRender={(menu) => (
                    <>
                      {menu}
                      <Divider style={{ margin: '8px 0' }} />
                      <div style={{ padding: '0 8px 4px', fontSize: '12px', color: '#999' }}>
                        💡 可選擇範本後編輯，或直接輸入自訂內容
                      </div>
                    </>
                  )}
                >
                  <Option value="技術分析師：專精於技術指標、K線、均線、KD、MACD等分析，善於從圖表找出買賣時機點">技術分析師 (技術派)</Option>
                  <Option value="總經分析師：關注宏觀經濟、GDP、利率、匯率、國際局勢，從大環境判斷市場走向">總經分析師 (總經派)</Option>
                  <Option value="籌碼分析師：專精於分析主力動向、法人買賣、融資融券、股東結構，找出主力布局的股票">籌碼分析師 (籌碼派)</Option>
                  <Option value="價值投資者：著重基本面分析、EPS、ROE、本益比，尋找被低估的優質公司長期持有">價值投資者 (基本面派)</Option>
                  <Option value="新聞解讀者：專門追蹤產業新聞、公司公告、政策變化，從新聞事件挖掘投資機會">新聞解讀者 (新聞派)</Option>
                  <Option value="鄉民風格：輕鬆幽默的論壇用語，常用PTT/Dcard風格，親切接地氣，樂於分享投資經驗">鄉民風格 (論壇派)</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="prompt_style"
                label="Prompt風格"
                tooltip="定義分析風格和寫作方式"
              >
                <Select
                  mode="tags"
                  placeholder="選擇範本或自訂輸入"
                  maxTagCount={1}
                  style={{ width: '100%' }}
                >
                  <Option value="數據導向：所有論述基於數據和指標，提供量化分析，用圖表輔助說明">數據導向 (量化風格)</Option>
                  <Option value="邏輯清晰：論述結構嚴謹，層次分明，因果關係明確，結論有理有據">邏輯清晰 (理性風格)</Option>
                  <Option value="專業術語：使用專業術語和技術名詞，適合有一定投資經驗的讀者">專業術語 (學術風格)</Option>
                  <Option value="白話易懂：避免艱深術語，用生活化的比喻，讓新手也能看懂">白話易懂 (親民風格)</Option>
                  <Option value="簡潔扼要：重點式說明，不冗贅，快速傳遞核心觀點">簡潔扼要 (精簡風格)</Option>
                  <Option value="詳細分析：深入剖析，提供完整背景資訊，多角度探討">詳細分析 (深度風格)</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="prompt_guardrails"
                label="Prompt守則"
                tooltip="設定限制和規範，確保內容合規"
              >
                <Select
                  mode="tags"
                  placeholder="選擇範本或自訂輸入"
                  maxTagCount={1}
                  style={{ width: '100%' }}
                >
                  <Option value="不提供具體買賣建議，不明示買進賣出價位，不保證獲利，僅供參考">標準守則 (合規)</Option>
                  <Option value="強調風險管理，提醒投資有風險，建議分散投資，不建議重押單一標的">風險警示 (保守)</Option>
                  <Option value="基於數據分析，不依賴主觀判斷，避免情緒化用詞，理性客觀">理性客觀 (中性)</Option>
                  <Option value="尊重不同觀點，不批評其他分析方法，鼓勵多元思考">開放態度 (包容)</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="prompt_skeleton"
                label="Prompt骨架"
                tooltip="定義文章結構模板"
              >
                <Select
                  mode="tags"
                  placeholder="選擇範本或自訂輸入"
                  maxTagCount={1}
                  style={{ width: '100%' }}
                >
                  <Option value="【標題】\n1. 當前狀況\n2. 技術分析\n3. 買賣策略\n4. 風險提醒">技術分析骨架</Option>
                  <Option value="【標題】\n1. 總經背景\n2. 產業現況\n3. 個股分析\n4. 投資建議">總經分析骨架</Option>
                  <Option value="【標題】\n1. 主力動向\n2. 法人買賣\n3. 籌碼解讀\n4. 操作策略">籌碼分析骨架</Option>
                  <Option value="【標題】\n1. 新聞事件\n2. 影響分析\n3. 相關個股\n4. 短期看法">新聞解讀骨架</Option>
                  <Option value="【標題】\n觀點分享...\n大家覺得呢？">鄉民互動骨架</Option>
                </Select>
              </Form.Item>
            </TabPane>

            {/* 模型設定 */}
            <TabPane tab="模型設定" key="model">
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="model_id"
                    label="模型ID"
                    tooltip="選擇此 KOL 預設使用的 AI 模型，生成貼文時可選擇是否覆蓋"
                  >
                    <Select placeholder="選擇模型 (預設: gpt-4o-mini)" allowClear>
                      <Option value="gpt-4o-mini">
                        <Space>
                          <span>gpt-4o-mini</span>
                          <Tag color="green">推薦</Tag>
                          <Text type="secondary" style={{ fontSize: '11px' }}>快速、經濟</Text>
                        </Space>
                      </Option>
                      <Option value="gpt-4o">
                        <Space>
                          <span>gpt-4o</span>
                          <Tag color="blue">高品質</Tag>
                          <Text type="secondary" style={{ fontSize: '11px' }}>最新模型</Text>
                        </Space>
                      </Option>
                      <Option value="gpt-4-turbo">
                        <Space>
                          <span>gpt-4-turbo</span>
                          <Tag color="purple">進階</Tag>
                          <Text type="secondary" style={{ fontSize: '11px' }}>較貴、強大</Text>
                        </Space>
                      </Option>
                      <Option value="gpt-4">
                        <Space>
                          <span>gpt-4</span>
                          <Tag color="orange">穩定</Tag>
                          <Text type="secondary" style={{ fontSize: '11px' }}>經典版本</Text>
                        </Space>
                      </Option>
                      <Option value="gpt-3.5-turbo">
                        <Space>
                          <span>gpt-3.5-turbo</span>
                          <Tag color="default">基礎</Tag>
                          <Text type="secondary" style={{ fontSize: '11px' }}>低成本</Text>
                        </Space>
                      </Option>
                    </Select>
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

      {/* 創建 KOL Modal */}
      <Modal
        title={
          <div>
            <UserOutlined style={{ marginRight: 8 }} />
            創建KOL角色
          </div>
        }
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setCreateModalVisible(false)}>
            取消
          </Button>,
          <Button
            key="create"
            type="primary"
            onClick={handleCreateKOL}
            loading={saving}
            icon={<SaveOutlined />}
          >
            創建 KOL
          </Button>,
        ]}
      >
        <Form form={createForm} layout="vertical">
          <Alert
            message="創建新的 KOL 角色"
            description="請填寫 CMoney 登入資訊、KOL 基本資料，並選擇性提供 AI 個性化描述"
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="email"
                label="CMoney 登入郵箱"
                rules={[
                  { required: true, message: '請輸入郵箱' },
                  { type: 'email', message: '請輸入有效的郵箱' }
                ]}
              >
                <Input placeholder="example@email.com" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="password"
                label="CMoney 登入密碼"
                rules={[{ required: true, message: '請輸入密碼' }]}
              >
                <Space.Compact style={{ width: '100%' }}>
                  <Input.Password placeholder="請輸入密碼" style={{ width: 'calc(100% - 80px)' }} />
                  <Button
                    onClick={handleTestLogin}
                    loading={testingLogin}
                    type={testLoginResult?.success ? 'primary' : 'default'}
                    danger={testLoginResult?.success === false}
                    style={{ width: '80px' }}
                  >
                    {testLoginResult?.success === true ? '✅' : testLoginResult?.success === false ? '❌' : '測試'}
                  </Button>
                </Space.Compact>
              </Form.Item>
              {testLoginResult && (
                <Alert
                  message={testLoginResult.message}
                  type={testLoginResult.success ? 'success' : 'error'}
                  showIcon
                  closable
                  style={{ marginTop: -16, marginBottom: 16, fontSize: '12px' }}
                />
              )}
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="nickname"
                label="期望的 KOL 暱稱"
                rules={[{ required: true, message: '請輸入暱稱' }]}
                tooltip="系統將嘗試在 CMoney 更新此暱稱，如果暱稱已被使用將會失敗"
              >
                <Space.Compact style={{ width: '100%' }}>
                  <Input placeholder="例如：股市達人小明" style={{ width: 'calc(100% - 80px)' }} />
                  <Button
                    onClick={handleTestNickname}
                    loading={testingNickname}
                    type={testNicknameResult?.success ? 'primary' : 'default'}
                    danger={testNicknameResult?.success === false}
                    style={{ width: '80px' }}
                  >
                    {testNicknameResult?.success === true ? '✅' : testNicknameResult?.success === false ? '❌' : '測試'}
                  </Button>
                </Space.Compact>
              </Form.Item>
              {testNicknameResult && (
                <Alert
                  message={testNicknameResult.message}
                  type={testNicknameResult.success ? 'success' : 'error'}
                  showIcon
                  closable
                  style={{ marginTop: -16, marginBottom: 16, fontSize: '12px' }}
                />
              )}
            </Col>
            <Col span={12}>
              <Form.Item
                name="member_id"
                label="CMoney 會員 ID (選填)"
                tooltip="如果知道會員 ID 可填寫，留空系統會嘗試自動獲取"
              >
                <Input placeholder="例如：9505546" />
              </Form.Item>
            </Col>
          </Row>

          <Divider>AI 個性化生成 (選填)</Divider>

          <Form.Item
            name="ai_description"
            label="KOL 描述"
            tooltip="提供 KOL 的個性、專業領域、風格等描述，AI 將自動生成完整的個性化設定"
          >
            <TextArea
              rows={8}
              maxLength={1000}
              showCount
              placeholder="例如：&#10;這是一位專注於價值投資的 KOL，擅長基本面分析...&#10;個性：友善、專業、喜歡用數據說話&#10;專業領域：財務報表分析、產業趨勢研究&#10;風格：正式但不失幽默，常用圖表輔助說明"
            />
          </Form.Item>

          <Alert
            message="提示"
            description="填寫 AI 描述後，系統將自動生成人設類型、語氣風格、專業領域等完整資料。若留空，則使用預設值。創建後可在列表中編輯調整。"
            type="success"
            showIcon
          />
        </Form>
      </Modal>

      {/* AI 生成資料審查 Modal */}
      <Modal
        title={
          <div>
            <BarChartOutlined style={{ marginRight: 8 }} />
            AI 生成的 KOL 資料審查
          </div>
        }
        open={reviewModalVisible}
        onCancel={() => setReviewModalVisible(false)}
        width={900}
        footer={[
          <Button key="cancel" onClick={() => setReviewModalVisible(false)}>
            取消
          </Button>,
          <Button key="confirm" type="primary" onClick={handleConfirmAIProfile}>
            確認並完成
          </Button>,
        ]}
      >
        {aiGeneratedProfile && (
          <>
            <Alert
              message="KOL 創建成功！"
              description={`Serial: ${aiGeneratedProfile.serial} | 暱稱: ${aiGeneratedProfile.nickname} | Email: ${aiGeneratedProfile.email}`}
              type="success"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Divider>AI 生成的個性化資料</Divider>

            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="人設類型">{aiGeneratedProfile.persona || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="目標受眾">{aiGeneratedProfile.target_audience || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="專業領域" span={2}>{aiGeneratedProfile.expertise || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="背景故事" span={2}>{aiGeneratedProfile.backstory || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="語氣風格" span={2}>{aiGeneratedProfile.tone_style || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="打字習慣">{aiGeneratedProfile.typing_habit || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="內容長度偏好">{aiGeneratedProfile.content_length || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="常用術語" span={2}>{aiGeneratedProfile.common_terms || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="口語用詞" span={2}>{aiGeneratedProfile.colloquial_terms || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="個人簽名" span={2}>{aiGeneratedProfile.signature || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="常用表情符號" span={2}>{aiGeneratedProfile.emoji_pack || 'N/A'}</Descriptions.Item>
            </Descriptions>

            <Divider>語氣參數</Divider>

            <Row gutter={16}>
              <Col span={8}>
                <Progress
                  type="circle"
                  percent={(aiGeneratedProfile.tone_formal || 5) * 10}
                  format={() => `${aiGeneratedProfile.tone_formal || 5}/10`}
                  strokeColor="#1890ff"
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>正式程度</div>
              </Col>
              <Col span={8}>
                <Progress
                  type="circle"
                  percent={(aiGeneratedProfile.tone_emotion || 5) * 10}
                  format={() => `${aiGeneratedProfile.tone_emotion || 5}/10`}
                  strokeColor="#52c41a"
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>情感程度</div>
              </Col>
              <Col span={8}>
                <Progress
                  type="circle"
                  percent={(aiGeneratedProfile.tone_confidence || 7) * 10}
                  format={() => `${aiGeneratedProfile.tone_confidence || 7}/10`}
                  strokeColor="#faad14"
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>自信程度</div>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={8}>
                <Progress
                  type="circle"
                  percent={(aiGeneratedProfile.tone_urgency || 5) * 10}
                  format={() => `${aiGeneratedProfile.tone_urgency || 5}/10`}
                  strokeColor="#eb2f96"
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>緊急程度</div>
              </Col>
              <Col span={8}>
                <Progress
                  type="circle"
                  percent={(aiGeneratedProfile.tone_interaction || 7) * 10}
                  format={() => `${aiGeneratedProfile.tone_interaction || 7}/10`}
                  strokeColor="#722ed1"
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>互動程度</div>
              </Col>
              <Col span={8}>
                <Progress
                  type="circle"
                  percent={(aiGeneratedProfile.question_ratio || 0.3) * 100}
                  format={() => `${((aiGeneratedProfile.question_ratio || 0.3) * 100).toFixed(0)}%`}
                  strokeColor="#13c2c2"
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>問題比例</div>
              </Col>
            </Row>

            <Alert
              message="注意"
              description="如果需要調整這些參數，請點擊確認後，在 KOL 列表中編輯該 KOL。"
              type="info"
              showIcon
              style={{ marginTop: 24 }}
            />
          </>
        )}
      </Modal>
    </div>
  );
};

export default KOLManagementPage;
