import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  TimePicker,
  InputNumber,
  Row,
  Col,
  Card,
  Typography,
  Space,
  Button,
  Divider,
  message
} from 'antd';
import {
  SettingOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Text } = Typography;
const { Option } = Select;

interface ScheduleConfigData {
  task_id?: string;
  name: string;
  description: string;
  trigger_config: {
    trigger_type: string;
    stock_codes: string[];
    kol_assignment: string;
    max_stocks?: number;
    stock_sorting?: {
      primary_sort?: string;
      secondary_sort?: string;
      tertiary_sort?: string;
    };
  };
  schedule_config: {
    enabled: boolean;
    daily_execution_time?: string | null; // make optional to accept partial initialData
    timezone: string;
  };
  auto_posting?: boolean;
}

interface ScheduleConfigModalProps {
  visible: boolean;
  onCancel: () => void;
  onSave: (config: ScheduleConfigData) => void;
  initialData?: ScheduleConfigData;
}

const ScheduleConfigModal: React.FC<ScheduleConfigModalProps> = ({
  visible,
  onCancel,
  onSave,
  initialData
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // 當 initialData 改變時，更新表單
  useEffect(() => {
    if (visible && initialData) {
      // 編輯模式：載入現有數據
      form.setFieldsValue({
        name: initialData.name,
        description: initialData.description,
        trigger_config: {
          trigger_type: initialData.trigger_config?.trigger_type || 'limit_up_after_hours',
          kol_assignment: initialData.trigger_config?.kol_assignment || 'random',
          max_stocks: initialData.trigger_config?.max_stocks || 5,
          stock_sorting: initialData.trigger_config?.stock_sorting || {
            primary_sort: 'change_percent_desc',
            secondary_sort: 'volume_desc',
            tertiary_sort: 'current_price_desc'
          }
        },
        schedule_config: {
          enabled: initialData.schedule_config?.enabled || false,
          daily_execution_time: initialData.schedule_config?.daily_execution_time 
            ? dayjs(initialData.schedule_config.daily_execution_time, 'HH:mm') 
            : null,
          timezone: initialData.schedule_config?.timezone || 'Asia/Taipei'
        },
        auto_posting: (initialData as any).auto_posting ?? false
      });
    } else if (visible && !initialData) {
      // 創建模式：重置為預設值
      form.resetFields();
    }
  }, [visible, initialData, form]);

  // 排序選項
  const sortOptions = [
    { value: 'change_percent_desc', label: '漲跌幅最高' },
    { value: 'change_percent_asc', label: '漲跌幅最低' },
    { value: 'volume_desc', label: '成交量最高' },
    { value: 'volume_asc', label: '成交量最低' },
    { value: 'current_price_desc', label: '股價最高' },
    { value: 'current_price_asc', label: '股價最低' },
    { value: 'market_cap_desc', label: '市值最高' },
    { value: 'market_cap_asc', label: '市值最低' },
    { value: 'turnover_rate_desc', label: '換手率最高' },
    { value: 'turnover_rate_asc', label: '換手率最低' },
    { value: 'pe_ratio_desc', label: '本益比最高' },
    { value: 'pe_ratio_asc', label: '本益比最低' },
    { value: 'pb_ratio_desc', label: '股價淨值比最高' },
    { value: 'pb_ratio_asc', label: '股價淨值比最低' },
    { value: 'five_day_change_desc', label: '近五日漲幅最高' },
    { value: 'five_day_change_asc', label: '近五日跌幅最多' },
    { value: 'ten_day_change_desc', label: '近十日漲幅最高' },
    { value: 'ten_day_change_asc', label: '近十日跌幅最多' },
    { value: 'one_month_change_desc', label: '近一月漲幅最高' },
    { value: 'one_month_change_asc', label: '近一月跌幅最多' }
  ];

  // 初始化表單
  useEffect(() => {
    if (visible) {
      if (initialData) {
        form.setFieldsValue(initialData);
      } else {
        form.setFieldsValue({
          name: '',
          description: '',
        trigger_config: {
          trigger_type: 'limit_up_after_hours',
          stock_codes: [],
          kol_assignment: 'random',
          max_stocks: 5,
            stock_sorting: {
              primary_sort: 'change_percent_desc',
              secondary_sort: 'volume_desc',
              tertiary_sort: 'current_price_desc'
            }
          },
          schedule_config: {
            enabled: false,
            daily_execution_time: null,
            timezone: 'Asia/Taipei'
          },
          auto_posting: false
        });
      }
    }
  }, [visible, initialData, form]);

  // 處理保存
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // 處理時間格式轉換
      if (values.schedule_config?.daily_execution_time) {
        values.schedule_config.daily_execution_time = values.schedule_config.daily_execution_time.format('HH:mm');
      }
      // normalize auto_posting
      values.auto_posting = !!values.auto_posting;
      
      setLoading(true);
      
      if (initialData) {
        // 編輯模式：更新現有排程
        const response = await fetch(`/api/schedule/tasks/${initialData.task_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(values)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
          message.success('排程配置已更新');
          onSave(values);
        } else {
          message.error(result.message || '更新排程配置失敗');
        }
      } else {
        // 創建模式：創建新排程
        const response = await fetch('/api/schedule/tasks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(values)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
          message.success('排程配置已保存');
          onSave(values);
        } else {
          message.error(result.message || '保存排程配置失敗');
        }
      }
    } catch (error) {
      console.error('保存失敗:', error);
      message.error('保存失敗');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={
        <Space>
          <SettingOutlined />
          <span>{initialData ? '編輯排程配置' : '創建新排程'}</span>
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      width={800}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button key="save" type="primary" loading={loading} onClick={handleSave}>
          保存
        </Button>
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          trigger_config: {
            trigger_type: 'limit_up_after_hours',
            kol_assignment: 'random',
            max_stocks: 5,
            stock_sorting: {
              primary_sort: 'change_percent_desc',
              secondary_sort: 'volume_desc',
              tertiary_sort: 'current_price_desc'
            }
          },
          schedule_config: {
            enabled: false,
            daily_execution_time: null,
            timezone: 'Asia/Taipei'
          },
          auto_posting: false
        }}
      >
        {/* 基本資訊 */}
        <Card size="small" title="📋 基本資訊" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="排程名稱"
                rules={[{ required: true, message: '請輸入排程名稱' }]}
              >
                <Input placeholder="輸入排程名稱" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="description"
                label="描述"
              >
                <Input.TextArea placeholder="輸入排程描述" rows={2} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 觸發器配置 */}
        <Card size="small" title="⚡ 觸發器配置" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name={['trigger_config', 'trigger_type']}
                label="觸發器類型"
                rules={[{ required: true, message: '請選擇觸發器類型' }]}
              >
                <Select>
                  <Option value="limit_up_after_hours">盤後漲停</Option>
                  <Option value="limit_down_after_hours">盤後跌停</Option>
                  <Option value="intraday_limit_up">盤中漲停</Option>
                  <Option value="intraday_limit_down">盤中跌停</Option>
                  <Option value="volume_surge">成交量暴增</Option>
                  <Option value="news_hot">新聞熱股</Option>
                  <Option value="custom_stocks">自選股</Option>
                  <Option value="intraday_gainers_by_amount">漲幅排序+成交額</Option>
                  <Option value="intraday_volume_leaders">成交量排序</Option>
                  <Option value="intraday_amount_leaders">成交額排序</Option>
                  <Option value="intraday_limit_down">跌停篩選</Option>
                  <Option value="intraday_limit_up">漲停篩選</Option>
                  <Option value="intraday_limit_down_by_amount">跌停篩選+成交額</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['trigger_config', 'kol_assignment']}
                label="KOL分配方式"
                rules={[{ required: true, message: '請選擇KOL分配方式' }]}
              >
                <Select>
                  <Option value="random">隨機分配</Option>
                  <Option value="round_robin">輪流分配</Option>
                  <Option value="performance_based">基於表現</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name={['trigger_config', 'max_stocks']}
                label="最多選取股票數"
                rules={[{ required: true, message: '請輸入最多選取股票數' }]}
              >
                <InputNumber min={1} max={50} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Divider />

          {/* 股票排序設定 */}
          <div style={{ marginBottom: 16 }}>
            <Text strong>📊 股票排序設定</Text>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={8}>
                <Form.Item
                  name={['trigger_config', 'stock_sorting', 'primary_sort']}
                  label="主要排序"
                >
                  <Select placeholder="選擇主要排序">
                    {sortOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name={['trigger_config', 'stock_sorting', 'secondary_sort']}
                  label="次要排序"
                >
                  <Select placeholder="選擇次要排序">
                    {sortOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name={['trigger_config', 'stock_sorting', 'tertiary_sort']}
                  label="第三排序"
                >
                  <Select placeholder="選擇第三排序">
                    {sortOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </div>
        </Card>

        {/* 排程設定 */}
        <Card size="small" title="⏰ 排程設定">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={['schedule_config', 'daily_execution_time']}
                label="每日執行時間"
                rules={[{ required: true, message: '請選擇每日執行時間' }]}
              >
                <TimePicker
                  format="HH:mm"
                  placeholder="選擇執行時間"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name={['schedule_config', 'timezone']}
                label="時區"
                rules={[{ required: true, message: '請選擇時區' }]}
              >
                <Select>
                  <Option value="Asia/Taipei">台北時間 (UTC+8)</Option>
                  <Option value="UTC">UTC時間</Option>
                  <Option value="America/New_York">紐約時間 (UTC-5)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={['schedule_config', 'enabled']}
                label="啟用排程"
                valuePropName="checked"
              >
                <Input type="checkbox" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name={['auto_posting']}
                label="自動發文"
                valuePropName="checked"
              >
                <Input type="checkbox" />
              </Form.Item>
            </Col>
          </Row>
        </Card>
      </Form>
    </Modal>
  );
};

export default ScheduleConfigModal;