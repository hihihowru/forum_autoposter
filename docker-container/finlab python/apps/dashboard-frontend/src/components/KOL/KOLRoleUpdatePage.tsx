import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Tag, 
  Space, 
  Typography, 
  Row, 
  Col, 
  Modal, 
  Form, 
  Input, 
  Select, 
  Switch, 
  InputNumber,
  Tabs,
  Divider,
  message,
  Popconfirm,
  Tooltip,
  Badge,
  Alert
} from 'antd';
import { 
  EditOutlined, 
  SaveOutlined, 
  CloseOutlined, 
  ReloadOutlined,
  UserOutlined,
  SettingOutlined,
  RobotOutlined,
  BarChartOutlined,
  CopyOutlined,
  DeleteOutlined,
  PlusOutlined,
  ExportOutlined,
  ImportOutlined
} from '@ant-design/icons';
import { KOLInfo } from '../../types/kol-types';
import api from '../../services/api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface KOLRoleUpdatePageProps {
  onBack?: () => void;
}

const KOLRoleUpdatePage: React.FC<KOLRoleUpdatePageProps> = ({ onBack }) => {
  // 狀態管理
  const [loading, setLoading] = useState(false);
  const [kols, setKols] = useState<KOLInfo[]>([]);
  const [selectedKOLs, setSelectedKOLs] = useState<string[]>([]);
  const [editingKOL, setEditingKOL] = useState<KOLInfo | null>(null);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [batchModalVisible, setBatchModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [batchForm] = Form.useForm();

  // 載入KOL列表
  const loadKOLs = async () => {
    setLoading(true);
    try {
      const response = await api.get('/dashboard/content-management');
      if (response.data?.kol_list) {
        setKols(response.data.kol_list);
      }
    } catch (error) {
      console.error('載入KOL列表失敗:', error);
      message.error('載入KOL列表失敗');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKOLs();
  }, []);

  // 編輯單個KOL
  const handleEditKOL = (kol: KOLInfo) => {
    setEditingKOL(kol);
    form.setFieldsValue(kol);
    setEditModalVisible(true);
  };

  // 保存KOL編輯
  const handleSaveKOL = async () => {
    try {
      const values = await form.validateFields();
      if (editingKOL) {
        const response = await api.put(`/dashboard/kols/${editingKOL.member_id}`, {
          ...editingKOL,
          ...values
        });
        
        if (response.data?.success) {
          message.success('KOL設定已更新');
          setEditModalVisible(false);
          loadKOLs();
        }
      }
    } catch (error) {
      console.error('更新KOL失敗:', error);
      message.error('更新KOL失敗');
    }
  };

  // 批量更新KOL
  const handleBatchUpdate = async () => {
    try {
      const values = await batchForm.validateFields();
      const updateData = {
        selected_kols: selectedKOLs,
        update_fields: values
      };
      
      const response = await api.post('/dashboard/kols/batch-update', updateData);
      
      if (response.data?.success) {
        message.success(`已批量更新 ${selectedKOLs.length} 個KOL`);
        setBatchModalVisible(false);
        setSelectedKOLs([]);
        loadKOLs();
      }
    } catch (error) {
      console.error('批量更新失敗:', error);
      message.error('批量更新失敗');
    }
  };

  // 複製KOL設定
  const handleCopyKOL = (sourceKOL: KOLInfo) => {
    Modal.confirm({
      title: '複製KOL設定',
      content: '請選擇要複製設定的目標KOL',
      onOk: () => {
        // 實現複製邏輯
        message.info('複製功能開發中...');
      }
    });
  };

  // 表格列定義
  const columns = [
    {
      title: '序號',
      dataIndex: 'serial',
      key: 'serial',
      width: 80,
      render: (serial: string) => (
        <Badge count={serial} style={{ backgroundColor: '#52c41a' }} />
      )
    },
    {
      title: '暱稱',
      dataIndex: 'nickname',
      key: 'nickname',
      width: 120,
      render: (nickname: string, record: KOLInfo) => (
        <Space>
          <UserOutlined />
          <span>{nickname}</span>
          <Tag color="blue">{record.persona}</Tag>
        </Space>
      )
    },
    {
      title: '人設',
      dataIndex: 'persona',
      key: 'persona',
      width: 100,
      render: (persona: string) => {
        const colors = {
          '技術派': 'blue',
          '基本面派': 'green',
          '籌碼派': 'orange',
          '情緒派': 'red',
          '題材派': 'purple'
        };
        return <Tag color={colors[persona as keyof typeof colors] || 'default'}>{persona}</Tag>;
      }
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const statusConfig = {
          'active': { color: 'green', text: '啟用' },
          'inactive': { color: 'red', text: '停用' },
          'testing': { color: 'orange', text: '測試' }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '目標受眾',
      dataIndex: 'target_audience',
      key: 'target_audience',
      width: 120,
      render: (audience: string) => (
        <Text type="secondary">{audience || '未設定'}</Text>
      )
    },
    {
      title: '互動閾值',
      dataIndex: 'interaction_threshold',
      key: 'interaction_threshold',
      width: 100,
      render: (threshold: number) => (
        <Text>{threshold || 0}</Text>
      )
    },
    {
      title: '發文統計',
      key: 'stats',
      width: 120,
      render: (record: KOLInfo) => (
        <Space direction="vertical" size="small">
          <Text type="secondary">總發文: {record.total_posts || 0}</Text>
          <Text type="secondary">已發布: {record.published_posts || 0}</Text>
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (record: KOLInfo) => (
        <Space>
          <Tooltip title="編輯設定">
            <Button
              type="primary"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEditKOL(record)}
            />
          </Tooltip>
          <Tooltip title="複製設定">
            <Button
              size="small"
              icon={<CopyOutlined />}
              onClick={() => handleCopyKOL(record)}
            />
          </Tooltip>
          <Tooltip title="查看詳情">
            <Button
              size="small"
              icon={<BarChartOutlined />}
              onClick={() => window.open(`/content-management/kols/${record.member_id}`, '_blank')}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  // 人設設定表單
  const PersonaSettingsForm = () => (
    <Form form={form} layout="vertical">
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="persona"
            label="人設類型"
            rules={[{ required: true, message: '請選擇人設類型' }]}
          >
            <Select placeholder="選擇人設類型">
              <Option value="技術派">技術派</Option>
              <Option value="基本面派">基本面派</Option>
              <Option value="籌碼派">籌碼派</Option>
              <Option value="情緒派">情緒派</Option>
              <Option value="題材派">題材派</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="target_audience"
            label="目標受眾"
            rules={[{ required: true, message: '請選擇目標受眾' }]}
          >
            <Select placeholder="選擇目標受眾">
              <Option value="active_traders">活躍交易者</Option>
              <Option value="long_term_investors">長期投資者</Option>
              <Option value="beginner_investors">投資新手</Option>
              <Option value="professional_traders">專業交易員</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>
      
      <Form.Item
        name="common_terms"
        label="常用詞彙"
        tooltip="用逗號分隔多個詞彙"
      >
        <TextArea
          rows={3}
          placeholder="例如：技術分析,突破,支撐,壓力"
        />
      </Form.Item>
      
      <Form.Item
        name="colloquial_terms"
        label="口語化用詞"
        tooltip="用逗號分隔多個詞彙"
      >
        <TextArea
          rows={3}
          placeholder="例如：超猛的,超讚的,超強的"
        />
      </Form.Item>
      
      <Form.Item
        name="tone_style"
        label="語氣風格"
      >
        <Select placeholder="選擇語氣風格">
          <Option value="專業嚴謹">專業嚴謹</Option>
          <Option value="親切友善">親切友善</Option>
          <Option value="活潑熱情">活潑熱情</Option>
          <Option value="冷靜理性">冷靜理性</Option>
        </Select>
      </Form.Item>
    </Form>
  );

  // Prompt設定表單
  const PromptSettingsForm = () => (
    <Form form={form} layout="vertical">
      <Form.Item
        name="prompt_persona"
        label="Prompt人設"
        tooltip="定義AI的角色和身份"
      >
        <TextArea
          rows={4}
          placeholder="例如：你是一位專業的技術分析師，擅長圖表分析和技術指標..."
        />
      </Form.Item>
      
      <Form.Item
        name="prompt_style"
        label="Prompt風格"
        tooltip="定義內容的寫作風格"
      >
        <TextArea
          rows={4}
          placeholder="例如：使用專業術語，但保持易懂，加入圖表分析..."
        />
      </Form.Item>
      
      <Form.Item
        name="prompt_guardrails"
        label="Prompt守則"
        tooltip="定義內容的邊界和限制"
      >
        <TextArea
          rows={3}
          placeholder="例如：不提供具體投資建議，不預測股價，僅提供分析..."
        />
      </Form.Item>
      
      <Form.Item
        name="prompt_skeleton"
        label="Prompt骨架"
        tooltip="定義內容的基本結構"
      >
        <TextArea
          rows={4}
          placeholder="例如：1. 技術分析 2. 關鍵指標 3. 操作建議 4. 風險提醒"
        />
      </Form.Item>
      
      <Form.Item
        name="prompt_cta"
        label="Prompt行動呼籲"
        tooltip="定義結尾的呼籲內容"
      >
        <TextArea
          rows={2}
          placeholder="例如：歡迎分享你的看法，記得按讚追蹤！"
        />
      </Form.Item>
    </Form>
  );

  // 批量更新表單
  const BatchUpdateForm = () => (
    <Form form={batchForm} layout="vertical">
      <Alert
        message={`已選擇 ${selectedKOLs.length} 個KOL進行批量更新`}
        type="info"
        style={{ marginBottom: 16 }}
      />
      
      <Form.Item
        name="persona"
        label="人設類型"
      >
        <Select placeholder="選擇要批量更新的人設類型" allowClear>
          <Option value="技術派">技術派</Option>
          <Option value="基本面派">基本面派</Option>
          <Option value="籌碼派">籌碼派</Option>
          <Option value="情緒派">情緒派</Option>
          <Option value="題材派">題材派</Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        name="target_audience"
        label="目標受眾"
      >
        <Select placeholder="選擇要批量更新的目標受眾" allowClear>
          <Option value="active_traders">活躍交易者</Option>
          <Option value="long_term_investors">長期投資者</Option>
          <Option value="beginner_investors">投資新手</Option>
          <Option value="professional_traders">專業交易員</Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        name="status"
        label="狀態"
      >
        <Select placeholder="選擇要批量更新的狀態" allowClear>
          <Option value="active">啟用</Option>
          <Option value="inactive">停用</Option>
          <Option value="testing">測試</Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        name="interaction_threshold"
        label="互動閾值"
      >
        <InputNumber
          placeholder="設定互動閾值"
          min={0}
          max={100}
          style={{ width: '100%' }}
        />
      </Form.Item>
    </Form>
  );

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>
            <SettingOutlined /> KOL角色管理
          </Title>
          <Text type="secondary">管理KOL人設、Prompt設定和批量調整</Text>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadKOLs}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setBatchModalVisible(true)}
              disabled={selectedKOLs.length === 0}
            >
              批量更新 ({selectedKOLs.length})
            </Button>
            <Button
              icon={<ExportOutlined />}
              onClick={() => message.info('匯出功能開發中...')}
            >
              匯出設定
            </Button>
            <Button
              icon={<ImportOutlined />}
              onClick={() => message.info('匯入功能開發中...')}
            >
              匯入設定
            </Button>
          </Space>
        </Col>
      </Row>

      {/* KOL列表表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={kols}
          loading={loading}
          rowKey="member_id"
          rowSelection={{
            selectedRowKeys: selectedKOLs,
            onChange: setSelectedKOLs,
            type: 'checkbox'
          }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 個KOL`
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 編輯KOL Modal */}
      <Modal
        title={
          <Space>
            <RobotOutlined />
            <span>編輯KOL設定 - {editingKOL?.nickname}</span>
          </Space>
        }
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setEditModalVisible(false)}>
            取消
          </Button>,
          <Button key="save" type="primary" onClick={handleSaveKOL}>
            保存
          </Button>
        ]}
      >
        <Tabs defaultActiveKey="persona">
          <TabPane tab="人設設定" key="persona">
            <PersonaSettingsForm />
          </TabPane>
          <TabPane tab="Prompt設定" key="prompt">
            <PromptSettingsForm />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 批量更新 Modal */}
      <Modal
        title="批量更新KOL設定"
        open={batchModalVisible}
        onCancel={() => setBatchModalVisible(false)}
        width={600}
        footer={[
          <Button key="cancel" onClick={() => setBatchModalVisible(false)}>
            取消
          </Button>,
          <Button key="update" type="primary" onClick={handleBatchUpdate}>
            批量更新
          </Button>
        ]}
      >
        <BatchUpdateForm />
      </Modal>
    </div>
  );
};

export default KOLRoleUpdatePage;
