import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  Row,
  Col,
  Card,
  Typography,
  Space,
  Button,
  Divider,
  message,
  TimePicker,
  DatePicker,
  Switch
} from 'antd';
import {
  ClockCircleOutlined,
  CalendarOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  UserOutlined,
  BarChartOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = TimePicker;

interface BatchRecord {
  session_id: string;
  created_at: string;
  status: string | null;
  trigger_type: string;
  kol_assignment: string;
  total_posts: number;
  published_posts: number;
  success_rate: number;
  stock_codes: string[];
  kol_names: string[];
  posts: Array<{
    post_id: string;
    title: string;
    content: string;
    kol_nickname: string;
    status: string;
    generation_config: any;
  }>;
}

interface BatchScheduleModalProps {
  visible: boolean;
  onCancel: () => void;
  onConfirm: (scheduleConfig: any) => void;
  batchData: BatchRecord | null;
}

const BatchScheduleModal: React.FC<BatchScheduleModalProps> = ({
  visible,
  onCancel,
  onConfirm,
  batchData
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [kolAssignment, setKolAssignment] = useState<string>('random');
  const [availableKols, setAvailableKols] = useState<Array<{serial: string, nickname: string}>>([]);
  const [selectedKols, setSelectedKols] = useState<string[]>([]);

  // 🔥 Fetch available KOLs from API
  useEffect(() => {
    const fetchKols = async () => {
      try {
        const response = await fetch('/api/kol/list');
        const result = await response.json();
        console.log('🔍 KOL list API response:', result);
        // 🔥 FIX: API returns 'data' not 'kols'
        if (result.success && result.data) {
          const kols = result.data.map((kol: any) => ({
            serial: kol.serial?.toString() || kol.kol_serial?.toString(),
            nickname: kol.nickname || kol.kol_nickname || `KOL-${kol.serial}`
          }));
          console.log('🔍 Parsed KOLs:', kols);
          setAvailableKols(kols);
        }
      } catch (error) {
        console.error('Failed to fetch KOLs:', error);
      }
    };
    if (visible) {
      fetchKols();
    }
  }, [visible]);

  // 🔥 Helper function to resolve KOL names to serial numbers
  const resolveKolNamesToSerials = (kolNames: string[], kols: Array<{serial: string, nickname: string}>): string[] => {
    return kolNames.map(name => {
      // If name matches "KOL-{serial}" format, extract the serial
      const kolMatch = name.match(/^KOL-(\d+)$/);
      if (kolMatch) {
        return kolMatch[1]; // Return just the serial number
      }
      // If it's already a numeric serial, return as-is
      if (/^\d+$/.test(name)) {
        return name;
      }
      // Otherwise try to find by nickname
      const matchingKol = kols.find(k => k.nickname === name);
      if (matchingKol) {
        return matchingKol.serial;
      }
      return name; // Return as-is if no match found
    });
  };

  // 🔥 Initialize selected KOLs from batch data when KOLs are loaded
  useEffect(() => {
    if (visible && batchData?.kol_names && availableKols.length > 0) {
      const resolvedSerials = resolveKolNamesToSerials(batchData.kol_names, availableKols);
      setSelectedKols(resolvedSerials);
      // Also update the form value
      form.setFieldValue(['generation_config', 'selected_kols'], resolvedSerials);
    }
  }, [visible, batchData, availableKols, form]);

  // 生成排程名稱的函數
  const generateScheduleName = (triggerType: string, stockSorting: string, sessionId: string) => {
    // 觸發器類型映射
    const triggerMap: { [key: string]: string } = {
      'limit_up_after_hours': '盤後漲',
      'limit_down_after_hours': '盤後跌',
      'intraday_limit_up': '盤中漲',
      'intraday_limit_down': '盤中跌',
      'news_hot': '熱門新聞'
    };
    
    // 股票排序映射
    const sortingMap: { [key: string]: string } = {
      'five_day_change_desc': '五日漲幅',
      'change_percent_desc': '漲跌幅',
      'volume_desc': '成交量',
      'current_price_desc': '股價',
      'market_cap_desc': '市值'
    };
    
    const triggerName = triggerMap[triggerType] || '未知觸發';
    const sortingName = sortingMap[stockSorting] || '未知排序';
    
    return `${triggerName}_${sortingName}_${sessionId}`;
  };

  // 初始化表單
  useEffect(() => {
    if (visible && batchData) {
      // 🔥 修復：從 batchData 的 posts 中提取原始配置
      const originalConfig = batchData.posts?.[0]?.generation_config || {};
      
      // 🔥 修復：從 batchData 獲取實際的 trigger_type
      const defaultTriggerType = originalConfig.trigger_type || 
                                originalConfig.settings?.trigger_type || 
                                batchData.trigger_type || 
                                'limit_up_after_hours';
      const defaultStockSorting = originalConfig.stock_sorting || 
                                 originalConfig.settings?.stock_sorting || 
                                 'five_day_change_desc';
      // 🔥 修復：提取原始的最大股票數量設定
      const originalMaxStocks = originalConfig.settings?.max_stocks_per_post || 
                               originalConfig.max_stocks_per_post || 
                               batchData.stock_codes?.length || 1;
      
      const scheduleName = generateScheduleName(defaultTriggerType, defaultStockSorting, batchData.session_id);
      
      // 🔥 添加詳細日誌記錄
      console.log('🔍 批次數據分析:');
      console.log('  - batchData:', batchData);
      console.log('  - originalConfig:', originalConfig);
      console.log('  - defaultTriggerType:', defaultTriggerType);
      console.log('  - defaultStockSorting:', defaultStockSorting);
      console.log('  - originalMaxStocks:', originalMaxStocks);
      
      form.setFieldsValue({
        schedule_name: scheduleName,
        schedule_description: `基於批次 ${batchData.session_id} 的工作日自動排程`,
        schedule_type: 'weekday_daily', // 排程類型：工作日每日執行
        daily_execution_time: originalConfig.settings?.posting_time_slots?.[0] || null,
        weekdays_only: true,
        interval_seconds: 300, // 5分鐘間隔
        enabled: true,
        max_posts_per_hour: 2,
        timezone: 'Asia/Taipei',
        generation_config: {
          trigger_type: defaultTriggerType, // 觸發器類型：從 batchData 獲取
          posting_type: originalConfig.posting_type || 'analysis', // 🔥 修復：從 batchData 獲取 posting_type
          stock_sorting: defaultStockSorting,
          max_stocks: originalMaxStocks, // 🔥 修復：使用原始配置的最大股票數量
          // 🔥 修復：只使用有效的 kol_assignment 值，否則默認為 'random'
          // batchData.kol_assignment 可能是 KOL serial (如 "208") 而不是分配策略
          kol_assignment: ['fixed', 'random', 'pool_random'].includes(batchData.kol_assignment)
            ? batchData.kol_assignment
            : 'random',
          // 🔥 FIX: Don't set selected_kols here - let the separate useEffect handle it
          // after availableKols is loaded to properly resolve names to serials
          selected_kols: [],
          content_style: originalConfig.content_style || originalConfig.settings?.content_style || 'technical',
          content_length: originalConfig.content_length || originalConfig.settings?.content_length || 'medium',
          max_words: originalConfig.max_words || originalConfig.settings?.max_words || 1000,
          news_max_links: originalConfig.news_max_links || originalConfig.news?.max_links || 5,
          generation_mode: originalConfig.generation_mode || originalConfig.batchMode?.generation_mode || 'high_quality',
          include_risk_warning: originalConfig.include_risk_warning !== false,
          include_charts: originalConfig.include_charts || false
        }
      });

      // 🔥 Also update state for conditional rendering
      const initialKolAssignment = ['fixed', 'random', 'pool_random'].includes(batchData.kol_assignment)
        ? batchData.kol_assignment
        : 'random';
      setKolAssignment(initialKolAssignment);
      // 🔥 FIX: Don't set selectedKols here - the separate useEffect will handle it
      // after availableKols is loaded
    }
  }, [visible, batchData, form]);

  // 處理確認
  const handleConfirm = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      if (!batchData) {
        message.error('批次數據不存在');
        return;
      }

      // 處理時間格式轉換
      let dailyExecutionTime = null;
      if (values.daily_execution_time) {
        // 將 TimePicker 的 moment 對象轉換為 HH:mm 格式
        if (values.daily_execution_time.format) {
          dailyExecutionTime = values.daily_execution_time.format('HH:mm');
        } else if (typeof values.daily_execution_time === 'string') {
          dailyExecutionTime = values.daily_execution_time;
        }
      }

      // 🔥 FIX: Extract full trigger configuration from the batch
      const originalConfig = batchData.posts?.[0]?.generation_config || {};
      const fullTriggersConfig = originalConfig.full_triggers_config || {};

      console.log('🔍 originalConfig:', originalConfig);
      console.log('🔍 fullTriggersConfig:', fullTriggersConfig);
      console.log('🔍 fullTriggersConfig type:', typeof fullTriggersConfig);
      console.log('🔍 fullTriggersConfig keys:', Object.keys(fullTriggersConfig));
      console.log('🔍 fullTriggersConfig JSON:', JSON.stringify(fullTriggersConfig, null, 2).substring(0, 300));

      // 🔥 FIX: Build comprehensive trigger_config for schedule execution using stored full config
      const triggerConfig = fullTriggersConfig.triggerConfig ? {
        triggerType: fullTriggersConfig.triggerConfig.triggerType || "individual",
        triggerKey: fullTriggersConfig.trigger_type || fullTriggersConfig.triggerConfig.triggerKey || values.generation_config.trigger_type,
        stockFilter: fullTriggersConfig.triggerConfig.stockFilter || "limit_up_stocks",
        stock_sorting: fullTriggersConfig.stock_sorting || fullTriggersConfig.stockSorting,
        max_stocks: fullTriggersConfig.stockCountLimit || values.generation_config.max_stocks,
        kol_assignment: values.generation_config.kol_assignment || 'random',
        filters: fullTriggersConfig.filters || {},
        threshold: fullTriggersConfig.threshold || 20,
        // Include all filter details
        volumeFilter: fullTriggersConfig.filters?.volumeFilter,
        priceFilter: fullTriggersConfig.filters?.priceFilter,
        marketCapFilter: fullTriggersConfig.filters?.marketCapFilter,
        sectorFilter: fullTriggersConfig.filters?.sectorFilter,
        technicalFilter: fullTriggersConfig.filters?.technicalFilter
      } : {
        // Fallback if no full_triggers_config
        triggerType: "individual",
        triggerKey: values.generation_config.trigger_type,
        stockFilter: "limit_up_stocks",
        stock_sorting: values.generation_config.stock_sorting,
        max_stocks: values.generation_config.max_stocks,
        kol_assignment: values.generation_config.kol_assignment || 'random',
        filters: {},
        threshold: 20
      };

      // 🔥 FIX: Build comprehensive schedule_config
      // 🔥 FIX: Use selectedKols from state (user-selected) for fixed/pool_random modes
      const kolAssignmentMode = values.generation_config.kol_assignment;
      const kolsToUse = (kolAssignmentMode === 'fixed' || kolAssignmentMode === 'pool_random')
        ? (values.generation_config.selected_kols || selectedKols || [])
        : []; // random mode doesn't need selected_kols

      const scheduleConfigData = {
        posting_type: originalConfig.posting_type || values.generation_config.posting_type,
        content_style: originalConfig.content_style || values.generation_config.content_style,
        content_length: originalConfig.content_length || values.generation_config.content_length,
        max_words: originalConfig.max_words || values.generation_config.max_words,
        generation_mode: values.generation_config.generation_mode,
        include_risk_warning: values.generation_config.include_risk_warning,
        include_charts: values.generation_config.include_charts,
        enable_news_links: values.generation_config.enable_news_links,
        news_max_links: values.generation_config.news_max_links,
        kol_assignment: kolAssignmentMode,
        // 🔥 FIX: Use user-selected KOLs for fixed/pool_random modes
        selected_kols: Array.isArray(kolsToUse) ? kolsToUse : [kolsToUse],
        stock_codes: batchData.stock_codes || [],
        // Store full triggers config for later use
        full_triggers_config: fullTriggersConfig,
        // 🔥 FIX: Pass data_sources (DTNO settings) from original batch config
        data_sources: originalConfig.data_sources || {}
      };

      const scheduleConfig = {
        session_id: parseInt(batchData.session_id),
        post_ids: batchData.posts.map(post => post.post_id),
        schedule_name: values.schedule_name,
        schedule_description: values.schedule_description,
        schedule_type: values.schedule_type,
        interval_seconds: values.interval_seconds,
        batch_duration_hours: values.batch_duration_hours,
        start_time: values.start_time,
        enabled: values.enabled,
        max_posts_per_hour: values.max_posts_per_hour,
        timezone: values.timezone,
        // 新增：發文時段設定 (轉換為 HH:mm 格式)
        daily_execution_time: dailyExecutionTime,
        weekdays_only: values.weekdays_only,
        // 新增：生成配置參數
        generation_config: values.generation_config,
        // 🔥 FIX: Add trigger_config and schedule_config
        trigger_config: triggerConfig,
        schedule_config: scheduleConfigData,
        batch_info: {
          total_posts: batchData.total_posts,
          published_posts: batchData.published_posts,
          success_rate: batchData.success_rate,
          stock_codes: batchData.stock_codes,
          kol_names: batchData.kol_names
        }
      };

      // 🔥 DEBUG: Log what we're sending
      console.log('🚀 Sending scheduleConfig to API:', scheduleConfig);
      console.log('🔍 batchData.posts[0]?.generation_config:', originalConfig);
      console.log('🔍 triggerConfig:', triggerConfig);
      console.log('🔍 scheduleConfigData:', scheduleConfigData);

      onConfirm(scheduleConfig);
    } catch (error) {
      console.error('表單驗證失敗:', error);
      message.error('請檢查表單輸入');
    } finally {
      setLoading(false);
    }
  };

  if (!batchData) {
    return null;
  }

  return (
    <Modal
      title={
        <Space>
          <CalendarOutlined />
          <span>批次排程設定</span>
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      width={800}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button key="confirm" type="primary" loading={loading} onClick={handleConfirm}>
          確認加入排程
        </Button>
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          schedule_type: '24hour_batch',
          interval_seconds: 300,
          batch_duration_hours: 24,
          enabled: true,
          max_posts_per_hour: 2,
          timezone: 'Asia/Taipei'
        }}
      >
        {/* 批次資訊 */}
        <Card size="small" title="📋 批次資訊" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Text strong>批次 ID:</Text>
              <br />
              <Text code>{batchData.session_id}</Text>
            </Col>
            <Col span={8}>
              <Text strong>總貼文數:</Text>
              <br />
              <Text>{batchData.total_posts} 篇</Text>
            </Col>
            <Col span={8}>
              <Text strong>成功率:</Text>
              <br />
              <Text style={{ color: batchData.success_rate >= 80 ? '#52c41a' : '#faad14' }}>
                {batchData.success_rate}%
              </Text>
            </Col>
          </Row>
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={24}>
              <Text type="secondary">
                <strong>注意：</strong>排程將根據下方設定重新篩選股票，不會使用原始批次的具體股票代碼。
                每日會根據市場情況動態選取符合條件的股票。
              </Text>
            </Col>
          </Row>
        </Card>

        {/* 排程設定 */}
        <Card size="small" title="⏰ 排程設定" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="schedule_name"
                label="排程名稱"
                rules={[{ required: true, message: '請輸入排程名稱' }]}
              >
                <Input placeholder="輸入排程名稱" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="schedule_description"
                label="排程描述"
              >
                <Input.TextArea placeholder="輸入排程描述" rows={2} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="schedule_type"
                label="排程類型"
                rules={[{ required: true, message: '請選擇排程類型' }]}
              >
                <Select>
                  <Option value="weekday_daily">工作日每日執行</Option>
                  <Option value="immediate">立即執行</Option>
                  <Option value="24hour_batch">24小時批次</Option>
                  <Option value="5min_batch">5分鐘批次</Option>
                  <Option value="custom">自定義</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="daily_execution_time"
                label="每日執行時間"
                rules={[{ required: true, message: '請選擇每日執行時間' }]}
              >
                <TimePicker 
                  style={{ width: '100%' }}
                  placeholder="選擇執行時間"
                  format="HH:mm"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="weekdays_only"
                label="僅工作日執行"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="工作日" unCheckedChildren="每日" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="interval_seconds"
                label="發文間隔 (秒)"
                rules={[{ required: true, message: '請輸入發文間隔' }]}
              >
                <InputNumber min={30} max={3600} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="max_posts_per_hour"
                label="每小時最大發文數"
                rules={[{ required: true, message: '請輸入每小時最大發文數' }]}
              >
                <InputNumber min={1} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="timezone"
                label="時區"
                rules={[{ required: true, message: '請選擇時區' }]}
              >
                <Select>
                  <Option value="Asia/Taipei">台北時間 (UTC+8)</Option>
                  <Option value="UTC">UTC時間</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="enabled"
                label="啟用排程"
                valuePropName="checked"
              >
                <Switch checkedChildren="啟用" unCheckedChildren="停用" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 股票篩選設定 */}
        <Card size="small" title="📊 股票篩選設定" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'trigger_type']}
                label="觸發器類型"
                initialValue="limit_up_after_hours"
                rules={[{ required: true, message: '請選擇觸發器類型' }]}
              >
                <Select onChange={(value) => {
                  // 當觸發器類型改變時，更新排程名稱
                  const currentValues = form.getFieldsValue();
                  const stockSorting = currentValues.generation_config?.stock_sorting || 'five_day_change_desc';
                  const newScheduleName = generateScheduleName(value, stockSorting, batchData?.session_id || '');
                  form.setFieldValue('schedule_name', newScheduleName);
                }}>
                  <Option value="limit_up_after_hours">盤後漲停</Option>
                  <Option value="limit_down_after_hours">盤後跌停</Option>
                  <Option value="volume_surge_after_hours">盤後爆量</Option>
                  <Option value="news_hot_after_hours">盤後新聞</Option>
                  <Option value="foreign_buy_after_hours">盤後外資買超</Option>
                  <Option value="institutional_buy_after_hours">盤後投信買超</Option>
                  <Option value="intraday_limit_up">盤中漲停</Option>
                  <Option value="intraday_limit_down">盤中跌停</Option>
                  <Option value="intraday_volume_surge">盤中爆量</Option>
                  <Option value="intraday_news_hot">盤中新聞</Option>
                  <Option value="intraday_foreign_buy">盤中外資買超</Option>
                  <Option value="intraday_institutional_buy">盤中投信買超</Option>
                  <Option value="trending_topics">熱門話題</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'posting_type']}
                label="發文類型"
                initialValue="analysis"
                rules={[{ required: true, message: '請選擇發文類型' }]}
              >
                <Select>
                  <Option value="interaction">互動發問</Option>
                  <Option value="analysis">發表分析</Option>
                  <Option value="personalized">個人化內容</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'stock_sorting']}
                label="股票排序方式"
                initialValue="five_day_change_desc"
                rules={[{ required: true, message: '請選擇排序方式' }]}
              >
                <Select onChange={(value) => {
                  // 當股票排序改變時，更新排程名稱
                  const currentValues = form.getFieldsValue();
                  const triggerType = currentValues.generation_config?.trigger_type || 'limit_up_after_hours';
                  const newScheduleName = generateScheduleName(triggerType, value, batchData?.session_id || '');
                  form.setFieldValue('schedule_name', newScheduleName);
                }}>
                  <Option value="five_day_change_desc">五日漲幅最高</Option>
                  <Option value="change_percent_desc">漲跌幅最高</Option>
                  <Option value="volume_desc">成交量最高</Option>
                  <Option value="current_price_desc">股價最高</Option>
                  <Option value="market_cap_desc">市值最高</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'max_stocks']}
                label="最大選取檔數"
                initialValue={batchData?.stock_codes?.length || 1}
                rules={[{ required: true, message: '請輸入最大檔數' }]}
              >
                <InputNumber min={1} max={50} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 生成參數設定 */}
        <Card size="small" title="⚙️ 生成參數設定" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'kol_assignment']}
                label="KOL分配方式"
                initialValue="random"
                rules={[{ required: true, message: '請選擇KOL分配方式' }]}
              >
                <Select onChange={(value) => setKolAssignment(value)}>
                  <Option value="fixed">固定指派（單一KOL）</Option>
                  <Option value="random">隨機指派（從所有KOL）</Option>
                  <Option value="pool_random">角色池指派（從選定KOL隨機）</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'content_style']}
                label="內容風格"
                initialValue="technical"
                rules={[{ required: true, message: '請選擇內容風格' }]}
              >
                <Select>
                  <Option value="professional">專業商務</Option>
                  <Option value="technical">技術分析</Option>
                  <Option value="casual">輕鬆隨性</Option>
                  <Option value="humorous">幽默風趣</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'content_length']}
                label="內容長度"
                initialValue="medium"
                rules={[{ required: true, message: '請選擇內容長度' }]}
              >
                <Select>
                  <Option value="short">簡短</Option>
                  <Option value="medium">中等</Option>
                  <Option value="detailed">詳細</Option>
                  <Option value="comprehensive">全面</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          {/* 🔥 KOL Selector - show when fixed or pool_random is selected */}
          {(kolAssignment === 'fixed' || kolAssignment === 'pool_random') && (
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item
                  name={['generation_config', 'selected_kols']}
                  label={kolAssignment === 'fixed' ? '選擇指定KOL' : '選擇KOL角色池'}
                  rules={[{ required: true, message: kolAssignment === 'fixed' ? '請選擇一個KOL' : '請至少選擇一個KOL' }]}
                >
                  {/* 🔥 FIX: Don't set value prop - let Form.Item manage it. Only use onChange to sync state */}
                  <Select
                    mode={kolAssignment === 'fixed' ? undefined : 'multiple'}
                    placeholder={kolAssignment === 'fixed' ? '選擇一個KOL' : '選擇多個KOL'}
                    onChange={(value) => {
                      // Sync to state for use in schedule config
                      if (kolAssignment === 'fixed') {
                        setSelectedKols(value ? [value as string] : []);
                      } else {
                        setSelectedKols(value as string[] || []);
                      }
                    }}
                    showSearch
                    optionFilterProp="children"
                    notFoundContent={availableKols.length === 0 ? '載入中...' : '無此資料'}
                  >
                    {availableKols.map(kol => (
                      <Option key={kol.serial} value={kol.serial}>
                        {kol.nickname} (#{kol.serial})
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          )}

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'max_words']}
                label="最大字數"
                initialValue={1000}
                rules={[{ required: true, message: '請輸入最大字數' }]}
              >
                <InputNumber min={100} max={5000} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'enable_news_links']}
                label="啟用新聞連結"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch checkedChildren="啟用" unCheckedChildren="停用" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'news_max_links']}
                label="新聞連結數量"
                initialValue={5}
                rules={[{ required: true, message: '請輸入新聞連結數量' }]}
              >
                <InputNumber min={0} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'generation_mode']}
                label="生成模式"
                initialValue="high_quality"
                rules={[{ required: true, message: '請選擇生成模式' }]}
              >
                <Select>
                  <Option value="high_quality">高品質</Option>
                  <Option value="fast">快速</Option>
                  <Option value="balanced">平衡</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'include_risk_warning']}
                label="包含風險警告"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['generation_config', 'include_charts']}
                label="包含圖表說明"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 發文策略 */}
        <Card size="small" title="📊 發文策略">
          <Row gutter={16}>
            <Col span={24}>
              <Text type="secondary">
                系統將根據設定的間隔時間，按順序發布批次中的 {batchData.total_posts} 篇貼文。
                預計總耗時: {Math.ceil((batchData.total_posts * form.getFieldValue('interval_seconds') || 300) / 3600)} 小時
              </Text>
            </Col>
          </Row>
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={24}>
              <Text type="secondary">
                <strong>工作日排程:</strong> 系統將在每個工作日（週一到週五）的指定時間自動執行批次腳本，
                根據股票篩選條件重新選取股票，使用上述生成參數重新生成並發布貼文。
              </Text>
            </Col>
          </Row>
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={24}>
              <Text type="secondary">
                <strong>執行流程:</strong> 觸發器 → 股票篩選 → KOL分配 → 內容生成 → 定時發布
              </Text>
            </Col>
          </Row>
        </Card>
      </Form>
    </Modal>
  );
};

export default BatchScheduleModal;
