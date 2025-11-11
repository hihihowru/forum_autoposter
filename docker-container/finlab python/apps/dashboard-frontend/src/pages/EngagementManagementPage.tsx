/**
 * Engagement Management Page (互動管理)
 * Comprehensive reaction bot control panel with all settings in one page
 *
 * Created: 2025-11-10
 * Author: Claude Code
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Switch,
  Slider,
  Select,
  Button,
  Statistic,
  Table,
  Tag,
  message,
  Space,
  Typography,
  Divider,
  InputNumber,
  Alert,
  Progress,
  Tooltip,
  Modal,
  Spin,
} from 'antd';
import {
  RocketOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  BarChartOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import { getApiBaseUrl } from '../config/api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const API_BASE_URL = getApiBaseUrl();

// ============================================
// TypeScript Interfaces
// ============================================

interface ReactionBotConfig {
  enabled: boolean;
  reaction_percentage: number;
  selected_kol_serials: number[];
  distribution_algorithm: string;
  min_delay_seconds: number;
  max_delay_seconds: number;
  max_reactions_per_kol_per_hour: number;
  created_at?: string;
  updated_at?: string;
}

interface KOLProfile {
  serial: number;
  nickname: string;
  persona?: string;
  status?: string;
}

interface BatchRecord {
  id: number;
  batch_id: string;
  article_count: number;
  total_reactions: number;
  reactions_sent: number;
  reactions_failed: number;
  status: string;
  created_at: string;
  completed_at?: string;
}

interface ReactionLog {
  id: number;
  article_id: string;
  kol_serial: number;
  reaction_type: string;
  success: boolean;
  timestamp: string;
  error_message?: string;
}

interface DailyStats {
  date: string;
  total_batches: number;
  total_articles_processed: number;
  total_reactions_sent: number;
  total_reactions_failed: number;
  avg_reactions_per_article: number;
  success_rate: number;
}

// ============================================
// Main Component
// ============================================

const EngagementManagementPage: React.FC = () => {
  // ========== State Management ==========
  const [config, setConfig] = useState<ReactionBotConfig>({
    enabled: false,
    reaction_percentage: 100,
    selected_kol_serials: [],
    distribution_algorithm: 'poisson',
    min_delay_seconds: 0.5,
    max_delay_seconds: 2.0,
    max_reactions_per_kol_per_hour: 100,
  });

  const [kolProfiles, setKolProfiles] = useState<KOLProfile[]>([]);
  const [batches, setBatches] = useState<BatchRecord[]>([]);
  const [logs, setLogs] = useState<ReactionLog[]>([]);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [processing, setProcessing] = useState(false);

  const [testModalVisible, setTestModalVisible] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  // ========== Data Fetching ==========

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadConfig(),
        loadKOLProfiles(),
        loadBatches(),
        loadLogs(),
        loadStats(),
      ]);
    } catch (error) {
      console.error('Error loading data:', error);
      message.error('載入數據失敗');
    } finally {
      setLoading(false);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reaction-bot/config`);
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const loadKOLProfiles = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/kols`);
      if (response.ok) {
        const data = await response.json();
        setKolProfiles(data.kols || []);
      }
    } catch (error) {
      console.error('Error loading KOL profiles:', error);
    }
  };

  const loadBatches = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reaction-bot/batches?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setBatches(data.batches || []);
      }
    } catch (error) {
      console.error('Error loading batches:', error);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reaction-bot/logs?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error loading logs:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reaction-bot/stats?days=7`);
      if (response.ok) {
        const data = await response.json();
        setDailyStats(data.daily_stats || []);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  // ========== Config Updates ==========

  const saveConfig = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/reaction-bot/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        message.success('配置已保存');
        await loadConfig();
      } else {
        const error = await response.json();
        message.error(error.detail || '保存失敗');
      }
    } catch (error) {
      console.error('Error saving config:', error);
      message.error('保存失敗');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleEnabled = async (enabled: boolean) => {
    setConfig({ ...config, enabled });
    await saveConfigField({ enabled });
  };

  const saveConfigField = async (updates: Partial<ReactionBotConfig>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/reaction-bot/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        message.success('設置已更新');
        await loadConfig();
      }
    } catch (error) {
      console.error('Error updating config:', error);
      message.error('更新失敗');
    }
  };

  // ========== Test Distribution ==========

  const testDistribution = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/reaction-bot/test-distribution?article_count=1000&reaction_percentage=${config.reaction_percentage}`
      );

      if (response.ok) {
        const result = await response.json();
        setTestResult(result);
        setTestModalVisible(true);
      } else {
        message.error('測試失敗');
      }
    } catch (error) {
      console.error('Error testing distribution:', error);
      message.error('測試失敗');
    }
  };

  // ========== Calculate Stats ==========

  const calculateOverallStats = () => {
    const totalBatches = batches.length;
    const totalReactions = batches.reduce((sum, b) => sum + b.reactions_sent, 0);
    const totalFailed = batches.reduce((sum, b) => sum + b.reactions_failed, 0);
    const successRate = totalReactions + totalFailed > 0
      ? (totalReactions / (totalReactions + totalFailed) * 100).toFixed(1)
      : '0.0';

    return { totalBatches, totalReactions, totalFailed, successRate };
  };

  const overallStats = calculateOverallStats();

  // ========== Table Columns ==========

  const batchColumns = [
    {
      title: '批次 ID',
      dataIndex: 'batch_id',
      key: 'batch_id',
      width: 200,
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: '文章數',
      dataIndex: 'article_count',
      key: 'article_count',
      width: 100,
    },
    {
      title: '反應總數',
      dataIndex: 'total_reactions',
      key: 'total_reactions',
      width: 120,
    },
    {
      title: '已發送',
      dataIndex: 'reactions_sent',
      key: 'reactions_sent',
      width: 100,
      render: (value: number) => <Text type="success">{value}</Text>,
    },
    {
      title: '失敗',
      dataIndex: 'reactions_failed',
      key: 'reactions_failed',
      width: 100,
      render: (value: number) => value > 0 ? <Text type="danger">{value}</Text> : <Text>{value}</Text>,
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          completed: 'success',
          processing: 'processing',
          pending: 'default',
          failed: 'error',
        };
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: '創建時間',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => new Date(text).toLocaleString('zh-TW'),
    },
  ];

  const logColumns = [
    {
      title: '文章 ID',
      dataIndex: 'article_id',
      key: 'article_id',
      width: 150,
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: 'KOL',
      dataIndex: 'kol_serial',
      key: 'kol_serial',
      width: 100,
      render: (serial: number) => {
        const kol = kolProfiles.find(k => k.serial === serial);
        return kol ? kol.nickname : `KOL ${serial}`;
      },
    },
    {
      title: '反應類型',
      dataIndex: 'reaction_type',
      key: 'reaction_type',
      width: 100,
    },
    {
      title: '狀態',
      dataIndex: 'success',
      key: 'success',
      width: 100,
      render: (success: boolean) =>
        success ? (
          <Tag icon={<CheckCircleOutlined />} color="success">成功</Tag>
        ) : (
          <Tag icon={<CloseCircleOutlined />} color="error">失敗</Tag>
        ),
    },
    {
      title: '時間',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (text: string) => new Date(text).toLocaleString('zh-TW'),
    },
  ];

  // ========== Render ==========

  if (loading && batches.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>載入中...</Text>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <RocketOutlined /> 互動管理 - 自動按讚機器人
        </Title>
        <Paragraph type="secondary">
          自動化反應系統，使用 Poisson 分佈演算法隨機分配按讚，模擬自然互動行為
        </Paragraph>
      </div>

      {/* Main Enable/Disable Switch & Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="機器人狀態"
              value={config.enabled ? '運行中' : '已停止'}
              prefix={config.enabled ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
              valueStyle={{ color: config.enabled ? '#3f8600' : '#cf1322' }}
            />
            <div style={{ marginTop: 16 }}>
              <Switch
                checked={config.enabled}
                onChange={handleToggleEnabled}
                checkedChildren="啟用"
                unCheckedChildren="停用"
                style={{ width: '100%' }}
              />
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="總批次"
              value={overallStats.totalBatches}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="總反應數"
              value={overallStats.totalReactions}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="成功率"
              value={overallStats.successRate}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: parseFloat(overallStats.successRate) > 90 ? '#3f8600' : '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Configuration Panel */}
      <Card
        title={
          <Space>
            <SettingOutlined />
            <span>機器人配置</span>
          </Space>
        }
        extra={
          <Button type="primary" onClick={saveConfig} loading={saving}>
            保存配置
          </Button>
        }
        style={{ marginBottom: 24 }}
      >
        <Row gutter={[24, 24]}>
          {/* KOL Pool Selection */}
          <Col xs={24} lg={12}>
            <div>
              <Space style={{ marginBottom: 12 }}>
                <TeamOutlined />
                <Text strong>KOL 選擇池</Text>
                <Tooltip title="選擇可以執行按讚的 KOL 帳號">
                  <InfoCircleOutlined style={{ color: '#1890ff' }} />
                </Tooltip>
              </Space>
              <Select
                mode="multiple"
                placeholder="選擇 KOL 帳號"
                value={config.selected_kol_serials}
                onChange={(value) => setConfig({ ...config, selected_kol_serials: value })}
                style={{ width: '100%' }}
                maxTagCount="responsive"
              >
                {kolProfiles.map((kol) => (
                  <Option key={kol.serial} value={kol.serial}>
                    {kol.nickname} (#{kol.serial})
                  </Option>
                ))}
              </Select>
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">
                  已選擇 {config.selected_kol_serials.length} 個 KOL
                </Text>
              </div>
            </div>
          </Col>

          {/* Reaction Percentage */}
          <Col xs={24} lg={12}>
            <div>
              <Space style={{ marginBottom: 12 }}>
                <LineChartOutlined />
                <Text strong>反應倍數</Text>
                <Tooltip title="100% = 1倍反應, 200% = 2倍反應">
                  <InfoCircleOutlined style={{ color: '#1890ff' }} />
                </Tooltip>
              </Space>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <Slider
                  min={0}
                  max={300}
                  step={10}
                  value={config.reaction_percentage}
                  onChange={(value) => setConfig({ ...config, reaction_percentage: value })}
                  style={{ flex: 1 }}
                  marks={{
                    0: '0%',
                    100: '100%',
                    200: '200%',
                    300: '300%',
                  }}
                />
                <InputNumber
                  min={0}
                  max={1000}
                  value={config.reaction_percentage}
                  onChange={(value) => setConfig({ ...config, reaction_percentage: value || 100 })}
                  formatter={(value) => `${value}%`}
                  parser={(value) => value?.replace('%', '') || '100'}
                  style={{ width: 100 }}
                />
              </div>
              <Alert
                message={`範例：6000 篇文章 × ${config.reaction_percentage}% = ${Math.round((6000 * config.reaction_percentage) / 100)} 個反應`}
                type="info"
                showIcon
                style={{ marginTop: 12 }}
              />
            </div>
          </Col>

          {/* Delay Settings */}
          <Col xs={24} lg={12}>
            <div>
              <Space style={{ marginBottom: 12 }}>
                <ThunderboltOutlined />
                <Text strong>反應延遲 (秒)</Text>
              </Space>
              <Row gutter={12}>
                <Col span={12}>
                  <Text type="secondary" style={{ fontSize: 12 }}>最小延遲</Text>
                  <InputNumber
                    min={0.1}
                    max={10}
                    step={0.1}
                    value={config.min_delay_seconds}
                    onChange={(value) => setConfig({ ...config, min_delay_seconds: value || 0.5 })}
                    style={{ width: '100%' }}
                    addonAfter="秒"
                  />
                </Col>
                <Col span={12}>
                  <Text type="secondary" style={{ fontSize: 12 }}>最大延遲</Text>
                  <InputNumber
                    min={0.1}
                    max={10}
                    step={0.1}
                    value={config.max_delay_seconds}
                    onChange={(value) => setConfig({ ...config, max_delay_seconds: value || 2.0 })}
                    style={{ width: '100%' }}
                    addonAfter="秒"
                  />
                </Col>
              </Row>
            </div>
          </Col>

          {/* Rate Limit */}
          <Col xs={24} lg={12}>
            <div>
              <Space style={{ marginBottom: 12 }}>
                <InfoCircleOutlined />
                <Text strong>每 KOL 每小時反應上限</Text>
              </Space>
              <InputNumber
                min={1}
                max={1000}
                value={config.max_reactions_per_kol_per_hour}
                onChange={(value) => setConfig({ ...config, max_reactions_per_kol_per_hour: value || 100 })}
                style={{ width: '100%' }}
                addonAfter="個反應"
              />
            </div>
          </Col>

          {/* Distribution Algorithm */}
          <Col xs={24} lg={12}>
            <div>
              <Space style={{ marginBottom: 12 }}>
                <BarChartOutlined />
                <Text strong>分佈演算法</Text>
              </Space>
              <Select
                value={config.distribution_algorithm}
                onChange={(value) => setConfig({ ...config, distribution_algorithm: value })}
                style={{ width: '100%' }}
              >
                <Option value="poisson">Poisson 分佈 (推薦)</Option>
                <Option value="uniform">均勻分佈</Option>
                <Option value="weighted">加權分佈</Option>
              </Select>
              <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
                Poisson 分佈模擬自然互動行為，部分文章獲得更多反應
              </Text>
            </div>
          </Col>

          {/* Test Distribution Button */}
          <Col xs={24} lg={12}>
            <div>
              <Space style={{ marginBottom: 12 }}>
                <ThunderboltOutlined />
                <Text strong>測試分佈</Text>
              </Space>
              <Button
                block
                icon={<LineChartOutlined />}
                onClick={testDistribution}
              >
                測試 Poisson 分佈 (1000 篇文章)
              </Button>
            </div>
          </Col>
        </Row>
      </Card>

      {/* Batch History */}
      <Card
        title={
          <Space>
            <ThunderboltOutlined />
            <span>批次執行記錄</span>
          </Space>
        }
        extra={
          <Button onClick={loadBatches} icon={<ThunderboltOutlined />}>
            刷新
          </Button>
        }
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={batchColumns}
          dataSource={batches}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          scroll={{ x: 1000 }}
          size="small"
        />
      </Card>

      {/* Activity Logs */}
      <Card
        title={
          <Space>
            <BarChartOutlined />
            <span>活動日誌 (最近 50 筆)</span>
          </Space>
        }
        extra={
          <Button onClick={loadLogs} icon={<ThunderboltOutlined />}>
            刷新
          </Button>
        }
      >
        <Table
          columns={logColumns}
          dataSource={logs}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          scroll={{ x: 800 }}
          size="small"
        />
      </Card>

      {/* Test Distribution Modal */}
      <Modal
        title="Poisson 分佈測試結果"
        visible={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTestModalVisible(false)}>
            關閉
          </Button>,
        ]}
        width={700}
      >
        {testResult && (
          <div>
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Statistic title="文章總數" value={testResult.article_count} />
              </Col>
              <Col span={8}>
                <Statistic title="反應總數" value={testResult.total_reactions} />
              </Col>
              <Col span={8}>
                <Statistic
                  title="反應倍數"
                  value={testResult.reaction_percentage}
                  suffix="%"
                />
              </Col>
            </Row>

            <Divider />

            <Title level={5}>統計數據</Title>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text>零反應文章：{testResult.statistics.zero_reactions}</Text>
              </Col>
              <Col span={12}>
                <Text>有反應文章：{testResult.statistics.with_reactions}</Text>
              </Col>
              <Col span={12}>
                <Text>最大反應數：{testResult.statistics.max_reactions}</Text>
              </Col>
              <Col span={12}>
                <Text>最小反應數：{testResult.statistics.min_reactions}</Text>
              </Col>
              <Col span={12}>
                <Text>平均反應數：{testResult.statistics.avg_reactions}</Text>
              </Col>
            </Row>

            <Divider />

            <Title level={5}>反應數分佈直方圖</Title>
            <div>
              {Object.entries(testResult.histogram || {}).map(([count, freq]: any) => (
                <div key={count} style={{ marginBottom: 8 }}>
                  <Text>{count} 個反應：</Text>
                  <Progress
                    percent={(freq / testResult.article_count) * 100}
                    format={() => `${freq} 篇`}
                    strokeColor="#1890ff"
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default EngagementManagementPage;
