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
  Radio,
  Tabs,
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
  FileTextOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { getApiBaseUrl } from '../config/api';
import { Line } from '@ant-design/charts';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

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
  kol_nickname: string;
  reaction_type: number;
  success: boolean;
  http_status_code: number | null;
  error_message: string | null;
  attempted_at: string;
  response_time_ms: number;
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

interface ArticleStats {
  hour_1: number;
  hour_2: number;
  hour_3: number;
  hour_6: number;
  hour_12: number;
  hour_24: number;
}

interface ArticleDetail {
  article_id: string;
  create_time: string;
  hour_bucket: number;
}

interface HourlyChartData {
  hour: string;
  count: number;
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
  const [logs, setLogs] = useState<ReactionLog[]>([]);
  const [articleStats, setArticleStats] = useState<ArticleStats | null>(null);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingArticles, setLoadingArticles] = useState(false);

  const [lastRunTime, setLastRunTime] = useState<string | null>(null);

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
        loadLogs(),
        loadArticleStats(),
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
      const response = await fetch(`${API_BASE_URL}/api/reaction-bot/config`);
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
      const response = await fetch(`${API_BASE_URL}/api/kols`);
      if (response.ok) {
        const data = await response.json();
        setKolProfiles(data.kols || []);
      }
    } catch (error) {
      console.error('Error loading KOL profiles:', error);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reaction-bot/logs?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error loading logs:', error);
    }
  };

  const loadArticleStats = async () => {
    setLoadingArticles(true);
    try {
      // Fetch stats for each time period using summary endpoint
      const timeRanges = [1, 2, 3, 6, 12, 24];
      const stats: ArticleStats = {
        hour_1: 0,
        hour_2: 0,
        hour_3: 0,
        hour_6: 0,
        hour_12: 0,
        hour_24: 0,
      };

      // Fetch all time ranges in parallel
      const responses = await Promise.all(
        timeRanges.map(hours =>
          fetch(`${API_BASE_URL}/api/reaction-bot/hourly-stats/summary?hours=${hours}`)
        )
      );

      // Process responses
      for (let i = 0; i < timeRanges.length; i++) {
        const response = responses[i];
        const hours = timeRanges[i];

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.summary) {
            const key = `hour_${hours}` as keyof ArticleStats;
            stats[key] = data.summary.total_new_articles || 0;
          }
        }
      }

      setArticleStats(stats);

      // Get last run time from 1-hour summary
      const lastHourResponse = await fetch(`${API_BASE_URL}/api/reaction-bot/hourly-stats/summary?hours=1`);
      if (lastHourResponse.ok) {
        const lastHourData = await lastHourResponse.json();
        if (lastHourData.success && lastHourData.summary && lastHourData.summary.latest_hour) {
          setLastRunTime(lastHourData.summary.latest_hour);
        }
      }
    } catch (error) {
      console.error('Error loading article stats:', error);
      message.error('載入文章統計失敗');
    } finally {
      setLoadingArticles(false);
    }
  };

  // ========== Config Updates ==========

  const saveConfig = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/reaction-bot/config`, {
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
      const response = await fetch(`${API_BASE_URL}/api/reaction-bot/config`, {
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

  // ========== Calculate Stats from Logs ==========

  const calculateOverallStats = () => {
    const totalReactions = logs.length;
    const successfulReactions = logs.filter(log => log.success).length;
    const failedReactions = logs.filter(log => !log.success).length;
    const successRate = totalReactions > 0
      ? ((successfulReactions / totalReactions) * 100).toFixed(1)
      : '0.0';

    return {
      totalBatches: 0, // Not used anymore
      totalReactions: successfulReactions,
      totalFailed: failedReactions,
      successRate
    };
  };

  const overallStats = calculateOverallStats();

  // ========== Table Columns ==========

  const logColumns = [
    {
      title: '文章 ID',
      dataIndex: 'article_id',
      key: 'article_id',
      width: 120,
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: 'KOL',
      dataIndex: 'kol_nickname',
      key: 'kol_nickname',
      width: 120,
      render: (nickname: string, record: ReactionLog) => (
        <Text>{nickname || `KOL ${record.kol_serial}`}</Text>
      ),
    },
    {
      title: '反應類型',
      dataIndex: 'reaction_type',
      key: 'reaction_type',
      width: 80,
      render: (type: number) => {
        const types: Record<number, string> = { 1: '讚', 2: '噓' };
        return types[type] || `類型 ${type}`;
      },
    },
    {
      title: '狀態',
      dataIndex: 'success',
      key: 'success',
      width: 80,
      render: (success: boolean) =>
        success ? (
          <Tag icon={<CheckCircleOutlined />} color="success">成功</Tag>
        ) : (
          <Tag icon={<CloseCircleOutlined />} color="error">失敗</Tag>
        ),
    },
    {
      title: '時間',
      dataIndex: 'attempted_at',
      key: 'attempted_at',
      width: 160,
      render: (text: string) => new Date(text).toLocaleString('zh-TW'),
    },
    {
      title: '回應時間',
      dataIndex: 'response_time_ms',
      key: 'response_time_ms',
      width: 90,
      render: (ms: number) => <Text>{ms} ms</Text>,
    },
    {
      title: '錯誤',
      dataIndex: 'error_message',
      key: 'error_message',
      width: 200,
      render: (error: string | null) =>
        error ? <Text type="danger" style={{ fontSize: 12 }}>{error}</Text> : <Text type="secondary">-</Text>,
    },
  ];

  // ========== Render ==========

  if (loading && logs.length === 0) {
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
            {lastRunTime && (
              <div style={{ marginTop: 8 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  最後執行: {new Date(lastRunTime).toLocaleString('zh-TW')}
                </Text>
              </div>
            )}
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

      {/* Article Statistics from CMoney */}
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>文章數據統計 (從資料庫)</span>
          </Space>
        }
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={loadArticleStats}
            loading={loadingArticles}
            size="small"
          >
            刷新
          </Button>
        }
        style={{ marginBottom: 24 }}
        loading={loadingArticles}
      >
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} sm={8} md={4}>
            <Statistic
              title="過去 1 小時"
              value={articleStats?.hour_1 || 0}
              suffix="篇"
              valueStyle={{ fontSize: '20px' }}
            />
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Statistic
              title="過去 2 小時"
              value={articleStats?.hour_2 || 0}
              suffix="篇"
              valueStyle={{ fontSize: '20px' }}
            />
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Statistic
              title="過去 3 小時"
              value={articleStats?.hour_3 || 0}
              suffix="篇"
              valueStyle={{ fontSize: '20px' }}
            />
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Statistic
              title="過去 6 小時"
              value={articleStats?.hour_6 || 0}
              suffix="篇"
              valueStyle={{ fontSize: '20px' }}
            />
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Statistic
              title="過去 12 小時"
              value={articleStats?.hour_12 || 0}
              suffix="篇"
              valueStyle={{ fontSize: '20px' }}
            />
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Statistic
              title="過去 24 小時"
              value={articleStats?.hour_24 || 0}
              suffix="篇"
              valueStyle={{ fontSize: '20px' }}
            />
          </Col>
        </Row>
        <Alert
          message="數據來源"
          description="文章數據由本地 Mac 每小時從 CMoney 抓取並儲存至 PostgreSQL 資料庫，顯示指定時間範圍內的新增文章數量。"
          type="info"
          showIcon
          icon={<InfoCircleOutlined />}
        />
      </Card>

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
        </Row>
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
    </div>
  );
};

export default EngagementManagementPage;
