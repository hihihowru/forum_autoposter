import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Typography,
  message,
  Spin,
  Tooltip,
  Switch,
  Row,
  Col,
  Statistic,
  Badge,
  Descriptions,
  Timeline,
  Modal
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  UserOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  SendOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import ScheduleConfigModal from './ScheduleConfigModal';
import ScheduleExecutionModal from './ScheduleExecutionModal';
import { getApiBaseUrl } from '../../../config/api';

const { Title, Text } = Typography;
const API_BASE_URL = getApiBaseUrl();

interface ScheduleTask {
  task_id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  created_at: string;
  last_run: string | null;
  next_run: string | null;
  run_count: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  interval_seconds?: number;
  schedule_type?: string;
  auto_posting?: boolean;
  daily_execution_time?: string;  // 🔥 ADD: Root-level execution time
  schedule_config: {
    enabled: boolean;
    posting_time_slots: string[];
    timezone: string;
    daily_execution_time?: string;  // 🔥 ADD: Nested execution time
  };
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
  stock_sorting_display?: {  // 🔥 ADD: Backend-provided display helper
    method: string;
    direction: string;
    label: string;
  };
  batch_info?: {
    session_id: string;
    total_posts: number;
    published_posts: number;
  };
}

const ScheduleManagementPage: React.FC = () => {
  const [schedules, setSchedules] = useState<ScheduleTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<ScheduleTask | undefined>(undefined);
  const [dailyStats, setDailyStats] = useState<any>(null);
  const [schedulerEnabled, setSchedulerEnabled] = useState<boolean | null>(null); // null = loading, true/false = actual state

  // Execution modal state
  const [executionModalVisible, setExecutionModalVisible] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [executionLoading, setExecutionLoading] = useState(false);

  // 控制背景排程器開關
  const handleSchedulerToggle = async (enabled: boolean) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/schedule/scheduler/${enabled ? 'start' : 'stop'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        setSchedulerEnabled(enabled);
        message.success(`背景排程器已${enabled ? '啟動' : '停止'}`);
      } else {
        const errorData = await response.json();
        message.error(`操作失敗: ${errorData.detail || '未知錯誤'}`);
      }
    } catch (error) {
      console.error('控制背景排程器失敗:', error);
      message.error('控制背景排程器失敗');
    } finally {
      setLoading(false);
    }
  };

  // 獲取背景排程器狀態
  const fetchSchedulerStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedule/scheduler/status`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSchedulerEnabled(data.data.scheduler_running);
        }
      }
    } catch (error) {
      console.error('獲取背景排程器狀態失敗:', error);
    }
  };

  // 計算統計數據
  const getStatistics = () => {
    const runningCount = schedules.filter(s => s.status === 'active').length;
    const failedCount = schedules.filter(s => s.status === 'failed').length;
    
    // 計算即將執行的排程（下次執行時間在未來1小時內）
    const now = new Date();
    const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);
    const upcomingSchedules = schedules.filter(s => {
      if (!s.next_run) return false;
      const nextRun = new Date(s.next_run);
      return nextRun > now && nextRun <= oneHourLater;
    });
    
    // 找出最近的執行時間
    const nextExecution = upcomingSchedules.length > 0 
      ? upcomingSchedules.reduce((earliest, current) => {
          const currentTime = new Date(current.next_run!);
          const earliestTime = new Date(earliest.next_run!);
          return currentTime < earliestTime ? current : earliest;
        })
      : null;
    
    // 計算今日執行次數
    const today = new Date().toDateString();
    const todayExecutionCount = schedules.reduce((sum, s) => {
      if (s.last_run && new Date(s.last_run).toDateString() === today) {
        return sum + 1;
      }
      return sum;
    }, 0);
    
    return {
      runningCount,
      upcomingCount: upcomingSchedules.length,
      nextExecution: nextExecution?.next_run || null,
      nextScheduleType: nextExecution?.schedule_type || null,
      todayExecutionCount,
      failedCount
    };
  };

  // 計算下一個工作日
  const getNextWeekday = (scheduleTime: string) => {
    const now = new Date();
    const [hours, minutes] = scheduleTime.split(':').map(Number);
    const today = new Date();
    today.setHours(hours, minutes, 0, 0);
    
    // 如果今天的執行時間還沒到，就返回今天的時間
    if (today.getTime() > now.getTime()) {
      return today;
    }
    
    // 否則找到下一個工作日
    let nextRun = new Date(today);
    nextRun.setDate(nextRun.getDate() + 1);
    
    // 跳過週末，找到下一個工作日 (週一到週五)
    while (nextRun.getDay() === 0 || nextRun.getDay() === 6) {
      nextRun.setDate(nextRun.getDate() + 1);
    }
    
    return nextRun;
  };

  // 計算倒計時
  const getCountdown = (nextRun: string | null | undefined, scheduleType: string = '', scheduleConfig: any = null) => {
    if (!nextRun) return '';

    // 🔥 FIX: Properly handle UTC time conversion
    let dateStr = nextRun;
    if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('T00:00:00')) {
      dateStr = dateStr + 'Z'; // Mark as UTC if not already marked
    }

    const now = new Date();
    const target = new Date(dateStr);
    const diff = target.getTime() - now.getTime();
    
    // 對於工作日每日排程，需要特別處理
    if (scheduleType === 'weekday_daily' && scheduleConfig?.daily_execution_time) {
      const nextWorkday = getNextWeekday(scheduleConfig.daily_execution_time);
      const workdayDiff = nextWorkday.getTime() - now.getTime();
      
      if (workdayDiff < 0) {
        return '即將執行'; // 這應該不會發生
      }
      
      const minutes = Math.floor(workdayDiff / 60000);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      
      if (days > 0) return `${days}天後`;
      if (hours > 0) return `${hours}小時後`;
      if (minutes > 0) return `${minutes}分鐘後`;
      return '即將執行';
    }
    
    // 一般情況：如果時間已過
    if (diff < 0) {
      // 如果排程類型是每日相關，不顯示"已過期"，而是計算下次執行
      if (scheduleType?.includes('daily') || scheduleType?.includes('daily_batch')) {
        const minutes = Math.floor(Math.abs(diff) / 60000);
        
        if (minutes < 24 * 60) { // 24小時內
          const nextDay = new Date(target);
          nextDay.setDate(nextDay.getDate() + 1);
          const nextDayDiff = nextDay.getTime() - now.getTime();
          const nextHours = Math.floor(nextDayDiff / (1000 * 60 * 60));
          const nextDays = Math.floor(nextHours / 24);
          
          if (nextDays > 0) return `${nextDays}天後`;
          return `${nextHours}小時後`;
        }
        return '1天後';
      }
      
      // 非每日排程才顯示已過期
      return '已過期';
    }
    
    // 未來的時間
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}天後`;
    if (hours > 0) return `${hours}小時後`;
    if (minutes > 0) return `${minutes}分鐘後`;
    return '即將執行';
  };

  const statistics = getStatistics();

  // 將 UTC 時間字串轉換為台灣時間顯示
  const formatUtcToTaiwanTime = (utcTimeString: string | null | undefined): string => {
    if (!utcTimeString) return '未設定';

    // API 返回的時間格式: "2025-10-21T07:14:14.115996" (UTC但沒有Z標記)
    // 需要手動加上Z來標記為UTC，然後轉換為台灣時間
    let dateStr = utcTimeString;
    if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('T00:00:00')) {
      dateStr = dateStr + 'Z'; // 標記為UTC
    }

    const date = new Date(dateStr);

    return date.toLocaleString('zh-TW', {
      timeZone: 'Asia/Taipei',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  // 轉換 API 數據結構到前端期望的格式
  const transformApiTask = (apiTask: any): ScheduleTask => {
    //  Backend already provides schedule_config and trigger_config
    // Just use them directly instead of extracting from generation_config

    // 🔥 FIX: Ensure daily_execution_time is properly merged into schedule_config
    const scheduleConfig = apiTask.schedule_config || {
      enabled: apiTask.status === 'active',
      posting_time_slots: apiTask.daily_execution_time ? [apiTask.daily_execution_time] : [],
      timezone: apiTask.timezone || 'Asia/Taipei'
    };

    // Merge daily_execution_time into schedule_config if it exists at root level
    if (apiTask.daily_execution_time && !scheduleConfig.daily_execution_time) {
      scheduleConfig.daily_execution_time = apiTask.daily_execution_time;
    }

    return {
      task_id: apiTask.schedule_id || apiTask.task_id,
      name: apiTask.schedule_name || apiTask.name || '未命名排程',
      description: apiTask.schedule_description || apiTask.description || '',
      status: apiTask.status || 'active',
      created_at: apiTask.created_at,
      last_run: apiTask.last_run,
      next_run: apiTask.next_run,
      run_count: apiTask.run_count || 0,
      success_count: apiTask.success_count || 0,
      failure_count: apiTask.failure_count || 0,
      success_rate: apiTask.success_rate || (apiTask.run_count > 0
        ? ((apiTask.success_count || 0) / apiTask.run_count) * 100
        : 0),
      interval_seconds: apiTask.interval_seconds || 300,
      schedule_type: apiTask.schedule_type || 'weekday_daily',
      auto_posting: apiTask.auto_posting || false,
      daily_execution_time: apiTask.daily_execution_time,  // 🔥 FIX: Add at root level
      schedule_config: scheduleConfig,
      trigger_config: apiTask.trigger_config || {
        trigger_type: 'custom_stocks',
        stock_codes: [],
        kol_assignment: 'random',
        max_stocks: 10,
        stock_sorting: {}
      },
      stock_sorting_display: apiTask.stock_sorting_display,  // 🔥 FIX: Pass through stock_sorting_display
      batch_info: apiTask.batch_info ?
        (typeof apiTask.batch_info === 'string' ? JSON.parse(apiTask.batch_info) : apiTask.batch_info)
        : {
          session_id: apiTask.session_id?.toString() || '',
          total_posts: apiTask.total_posts_generated || 0,
          published_posts: apiTask.success_count || 0
        }
    };
  };

  // 獲取排程列表
  const loadSchedules = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedule/tasks`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      // API 返回的數據結構是 {success: true, tasks: [...]}
      const tasks = result.tasks || [];

      // 轉換 API 數據到前端期望的格式
      const transformedTasks = tasks.map(transformApiTask);

      // 按創建時間降序排序，最新的排在最前面
      const sortedTasks = transformedTasks.sort((a: ScheduleTask, b: ScheduleTask) => {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      setSchedules(sortedTasks);
    } catch (error) {
      console.error('獲取排程列表失敗:', error);
      message.error('獲取排程列表失敗');
      // 如果API失敗，使用空陣列
      setSchedules([]);
    } finally {
      setLoading(false);
    }
  };

  // 獲取每日統計數據
  const loadDailyStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedule/daily-stats`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      // 轉換 API 數據格式以匹配前端期望的結構
      const transformedData = {
        date: new Date().toISOString().split('T')[0],
        totals: {
          generated: result.data?.total_tasks || 0,
          published: result.data?.completed_tasks || 0,
          successful: result.data?.completed_tasks || 0,
          failed: result.data?.failed_tasks || 0,
          active: result.data?.active_tasks || 0
        },
        manual: result.data?.manual_tasks || 0,
        self_learning: result.data?.self_learning_tasks || 0,
        success_rate: result.data?.success_rate || 0
      };
      setDailyStats(transformedData);
    } catch (error) {
      console.warn('⚠️ 每日統計API暫不可用，使用預設數據:', error instanceof Error ? error.message : String(error));
      // 設置默認值（包含新的統計欄位）
      setDailyStats({
        date: new Date().toISOString().split('T')[0],
        totals: {
          generated: 0,
          published: 0,
          successful: 0,
          draft: 0,
          pending_review: 0
        },
        success_rate: 0
      });
    }
  };

  // 切換排程狀態
  const handleToggleEnabled = async (scheduleId: string, enabled: boolean) => {
    try {
      // 不設置全局 loading，避免影響表格顯示
      
      let response;
      if (enabled) {
        // 啟用排程 - 調用 start API
        response = await fetch(`${API_BASE_URL}/api/schedule/start/${scheduleId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        });
      } else {
        // 暫停排程 - 調用 cancel API
        response = await fetch(`${API_BASE_URL}/api/schedule/cancel/${scheduleId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        });
      }
      
      const result = await response.json();
      
      if (result.success) {
        message.success(`排程已${enabled ? '啟用' : '暫停'}`);
        // 重新載入排程列表
        await loadSchedules();
      } else {
        message.error(result.message || '更新排程狀態失敗');
      }
    } catch (error) {
      console.error('更新排程狀態失敗:', error);
      message.error('更新排程狀態失敗');
    }
  };

  // 切換自動發文開關（不影響任務運行狀態，只更新欄位）
  const handleToggleAutoPosting = async (record: ScheduleTask, autoPosting: boolean) => {
    try {
      // 不設置全局 loading，避免影響表格顯示
      const response = await fetch(`${API_BASE_URL}/api/schedule/${record.task_id}/auto-posting`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: autoPosting })
      });
      const result = await response.json();
      if (result.success) {
        message.success(`自動發文已${autoPosting ? '開啟' : '關閉'}`);
        // 直接更新本地狀態，不需要重新載入整個列表
        setSchedules(prevSchedules =>
          prevSchedules.map(s =>
            s.task_id === record.task_id
              ? { ...s, auto_posting: autoPosting }
              : s
          )
        );
      } else {
        message.error(result.message || '更新自動發文設定失敗');
      }
    } catch (e) {
      message.error('更新自動發文設定失敗');
    }
  };

  // 立即執行排程
  const handleExecuteNow = async (scheduleId: string) => {
    try {
      // Open modal immediately with loading state
      setExecutionModalVisible(true);
      setExecutionLoading(true);
      setExecutionResult(null);

      const response = await fetch(`${API_BASE_URL}/api/schedule/execute/${scheduleId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();

      // Store execution result
      setExecutionResult(result);
      setExecutionLoading(false);

      if (result.success) {
        message.success(`排程執行成功！生成 ${result.generated_count} 篇貼文`);
        loadSchedules();  // Refresh schedule list
      } else {
        message.error(result.error || result.message || '執行排程失敗');
      }
    } catch (error) {
      console.error('執行排程失敗:', error);
      setExecutionLoading(false);
      setExecutionResult({
        success: false,
        message: '執行排程失敗',
        error: error instanceof Error ? error.message : String(error)
      });
      message.error('執行排程失敗');
    }
  };

  // 刪除排程
  const handleDeleteSchedule = async (scheduleId: string, scheduleName: string) => {
    Modal.confirm({
      title: '確認刪除',
      content: `確定要刪除排程「${scheduleName}」嗎？此操作無法復原。`,
      okText: '確認刪除',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          setLoading(true);

          const response = await fetch(`${API_BASE_URL}/api/schedule/tasks/${scheduleId}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            }
          });

          const result = await response.json();

          if (result.success) {
            message.success('排程已刪除');
            await loadSchedules();
          } else {
            message.error(result.message || '刪除排程失敗');
          }
        } catch (error) {
          console.error('刪除排程失敗:', error);
          message.error('刪除排程失敗');
        } finally {
          setLoading(false);
        }
      }
    });
  };

  // 編輯排程配置
  const handleEditScheduleConfig = (schedule: ScheduleTask) => {
    setEditingSchedule(schedule);
    setConfigModalVisible(true);
  };

  // 創建新排程
  const handleCreateSchedule = () => {
    setEditingSchedule(undefined);
    setConfigModalVisible(true);
  };

  // 處理保存配置
  const handleSaveConfig = (config: any) => {
    console.log('保存排程配置:', config);
    setConfigModalVisible(false);
    loadSchedules();
  };

  // 獲取狀態顏色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'paused': return 'orange';
      case 'completed': return 'blue';
      case 'failed': return 'red';
      default: return 'default';
    }
  };

  // 獲取狀態文字
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '運行中';
      case 'paused': return '已暫停';
      case 'completed': return '已完成';
      case 'failed': return '失敗';
      default: return '未知';
    }
  };

  // 表格列定義
  const columns: ColumnsType<ScheduleTask> = [
    {
      title: '排程名稱',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text: string, record: ScheduleTask) => (
        <div>
          <Text strong>{text}</Text>
          <div style={{ fontSize: '10px', color: '#666' }}>
            ID: {record.task_id}
          </div>
        </div>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string, record: ScheduleTask) => (
        <div>
          <Tag color={getStatusColor(status)}>
            {getStatusText(status)}
          </Tag>
          {status === 'active' && (
            <div style={{ marginTop: 4, fontSize: '12px', color: '#666' }}>
              ID: {record.task_id?.slice(-8) || 'N/A'}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '發文時間',
      dataIndex: 'schedule_config',
      key: 'posting_time',
      width: 140,
      render: (_: any, record: ScheduleTask) => {
        // 🔥 FIX: Check multiple sources for daily_execution_time
        const startTime = record.daily_execution_time
          || record.schedule_config?.daily_execution_time
          || record.schedule_config?.posting_time_slots?.[0];
        const intervalSec = record.interval_seconds || 300;

        return (
          <div>
            <div style={{ fontSize: '11px', marginBottom: 2 }}>
              <ClockCircleOutlined style={{ marginRight: 4 }} />
              開始: {startTime || '未設定'}
            </div>
            <div style={{ fontSize: '10px', color: '#666' }}>
              間隔: {intervalSec}秒 ({Math.round(intervalSec / 60)}分鐘)
            </div>
            <div style={{ fontSize: '10px', color: '#999' }}>
              {record.schedule_config?.timezone || 'Asia/Taipei'}
            </div>
          </div>
        );
      },
    },
    {
      title: '發文間隔',
      dataIndex: 'interval_seconds',
      key: 'interval_seconds',
      width: 100,
      render: (intervalSeconds: number) => (
        <div>
          <Text style={{ fontSize: '11px' }}>
            {intervalSeconds ? `${intervalSeconds}秒` : '300秒'}
          </Text>
          <div style={{ fontSize: '10px', color: '#666' }}>
            {intervalSeconds ? `約${Math.round(intervalSeconds / 60)}分鐘` : '約5分鐘'}
          </div>
        </div>
      ),
    },
    {
      title: '排程類型',
      dataIndex: 'schedule_type',
      key: 'schedule_type',
      width: 120,
      render: (scheduleType: string) => {
        const scheduleTypeMap: Record<string, { text: string; color: string }> = {
          'weekday_daily': { text: '工作日每日', color: 'blue' },
          'daily': { text: '每日執行', color: 'green' },
          'immediate': { text: '立即執行', color: 'red' },
          '24hour_batch': { text: '24小時批次', color: 'orange' },
          '5min_batch': { text: '5分鐘批次', color: 'purple' }
        };
        const mapped = scheduleTypeMap[scheduleType] || { text: scheduleType || '未設定', color: 'default' };
        return <Tag color={mapped.color}>{mapped.text}</Tag>;
      },
    },
    {
      title: '觸發器類型',
      dataIndex: 'trigger_config',
      key: 'trigger_type',
      width: 120,
      render: (triggerConfig: any, record: ScheduleTask) => {
        // 🔥 觸發器類型映射 - 與發文生成器步驟一保持一致（共14種觸發器）
        const triggerTypeMap: Record<string, { text: string; color: string }> = {
          // ========== 熱門話題 (1個) ==========
          'trending_topics': { text: 'CMoney熱門話題', color: 'orange' },

          // ========== 個股觸發器 - 盤後 (6個) ==========
          'limit_up_after_hours': { text: '盤後漲', color: 'red' },
          'limit_down_after_hours': { text: '盤後跌', color: 'green' },
          'volume_amount_high': { text: '成交金額高', color: 'orange' },
          'volume_amount_low': { text: '成交金額低', color: 'blue' },
          'volume_change_rate_high': { text: '成交金額變化率高', color: 'volcano' },
          'volume_change_rate_low': { text: '成交金額變化率低', color: 'cyan' },

          // ========== 盤中觸發器 (6個) ==========
          'intraday_gainers_by_amount': { text: '強勢股', color: 'volcano' },
          'intraday_volume_leaders': { text: '成交量高', color: 'orange' },
          'intraday_amount_leaders': { text: '成交額高', color: 'gold' },
          'intraday_limit_down': { text: '跌停股', color: 'green' },
          'intraday_limit_up': { text: '漲停股', color: 'red' },
          'intraday_limit_down_by_amount': { text: '弱勢股', color: 'cyan' },

          // ========== 自定義 (1個) ==========
          'custom_stocks': { text: '自選股票', color: 'purple' },

          // ========== 舊觸發器名稱（向後兼容） ==========
          'after_hours_volume_amount_high': { text: '成交金額高', color: 'orange' },
          'after_hours_volume_amount_low': { text: '成交金額低', color: 'blue' },
          'after_hours_volume_change_rate_high': { text: '成交金額變化率高', color: 'gold' },
          'after_hours_volume_change_rate_low': { text: '成交金額變化率低', color: 'cyan' },
          'intraday_limit_up_by_amount': { text: '強勢股', color: 'magenta' }
        };
        // 🔥 FIX: Support both old and new trigger_config structures
        // New structure: triggerConfig.triggerKey
        // Old structure: triggerConfig.trigger_type
        const triggerType = triggerConfig?.triggerKey || triggerConfig?.trigger_type || record.trigger_config?.triggerKey || record.trigger_config?.trigger_type || 'N/A';
        const mapped = triggerTypeMap[triggerType] || { text: triggerType, color: 'default' };
        return <Tag color={mapped.color}>{mapped.text}</Tag>;
      },
    },
    {
      title: '股票設定',
      dataIndex: 'trigger_config',
      key: 'stock_settings',
      width: 150,
      render: (triggerConfig: any, record: ScheduleTask) => {
        // 🔥 FIX: Use full_triggers_config as source of truth
        const fullTriggersConfig = record.schedule_config?.full_triggers_config;

        // Get stockCountLimit (correct source)
        const stockCount = fullTriggersConfig?.stockCountLimit
          || triggerConfig?.max_stocks
          || record.trigger_config?.max_stocks
          || 'N/A';

        // Get stockFilterCriteria (correct source)
        const stockFilterCriteria = fullTriggersConfig?.stockFilterCriteria;

        // Map stockFilterCriteria to Chinese labels
        let sortingDisplay = null;
        if (stockFilterCriteria && Array.isArray(stockFilterCriteria) && stockFilterCriteria.length > 0) {
          const criteriaMap: Record<string, string> = {
            'five_day_gain': '五日漲幅',
            'five_day_loss': '五日跌幅',
            'daily_gain': '單日漲幅',
            'daily_loss': '單日跌幅',
            'volume_high': '成交量大',
            'volume_low': '成交量小',
          };
          sortingDisplay = criteriaMap[stockFilterCriteria[0]] || stockFilterCriteria[0];
        } else {
          // Fallback to backend-provided stock_sorting_display.label
          sortingDisplay = record.stock_sorting_display?.label;
        }

        return (
          <div>
            <Text style={{ fontSize: '11px' }}>
              最多 {stockCount} 檔
            </Text>
            {sortingDisplay && (
              <div style={{ fontSize: '10px', color: '#666' }}>
                排序: {sortingDisplay}
              </div>
            )}
          </div>
        );
      },
    },
    {
      title: 'KOL分配',
      dataIndex: 'trigger_config',
      key: 'kol_assignment',
      width: 120,
      render: (triggerConfig: any, record: ScheduleTask) => {
        const kolAssignmentMap: Record<string, { text: string; color: string }> = {
          'random': { text: '隨機指派', color: 'blue' },
          'pool_random': { text: '角色池指派', color: 'cyan' },
          'fixed': { text: '固定指派', color: 'green' },
        };
        const kolAssignment = triggerConfig?.kol_assignment || record.trigger_config?.kol_assignment || 'random';
        const mapped = kolAssignmentMap[kolAssignment] || { text: kolAssignment, color: 'default' };

        // 🔥 Get selected KOLs from schedule_config
        const scheduleConfig = record.schedule_config as any;
        const selectedKols = scheduleConfig?.selected_kols || [];

        return (
          <div>
            <Space>
              <UserOutlined />
              <Tag color={mapped.color}>{mapped.text}</Tag>
            </Space>
            {/* 🔥 Show selected KOLs for fixed/pool_random modes */}
            {(kolAssignment === 'fixed' || kolAssignment === 'pool_random') && selectedKols.length > 0 && (
              <div style={{ fontSize: '11px', marginTop: 4, color: '#666' }}>
                {selectedKols.slice(0, 3).join(', ')}
                {selectedKols.length > 3 && ` +${selectedKols.length - 3}更多`}
              </div>
            )}
          </div>
        );
      },
    },
    {
      title: '今日統計',
      key: 'today_stats',
      width: 150,
      render: (_, record: ScheduleTask) => (
        <div>
          <div style={{ fontSize: '11px' }}>
            預計生成: {record.batch_info?.total_posts || 0}篇
          </div>
          <div style={{ fontSize: '11px' }}>
            已生成: {record.batch_info?.published_posts || 0}篇
          </div>
          <div style={{ fontSize: '11px', color: record.success_rate >= 80 ? '#52c41a' : '#faad14' }}>
            成功率: {record.success_rate}%
          </div>
        </div>
      ),
    },
    {
      title: '創建時間',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 140,
      sorter: (a: ScheduleTask, b: ScheduleTask) => {
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      },
      render: (createdAt: string) => (
        <div>
          <Text style={{ fontSize: '11px' }}>
            {formatUtcToTaiwanTime(createdAt)}
          </Text>
        </div>
      ),
    },
    {
      title: '下次執行',
      dataIndex: 'next_run',
      key: 'next_run',
      width: 140,
      render: (nextRun: string | null, record: ScheduleTask) => (
        <div>
          {nextRun ? (
            <>
              <Space style={{ marginBottom: 4 }}>
                <CalendarOutlined />
                <Text style={{ fontSize: '11px' }}>
                  {formatUtcToTaiwanTime(nextRun)}
                </Text>
              </Space>
              <div>
                <Text
                  type="secondary"
                  style={{
                    fontSize: '11px',
                    color: '#1890ff',
                    fontWeight: 500
                  }}
                >
                  {getCountdown(nextRun || undefined, record.schedule_type, record.schedule_config)}
                </Text>
              </div>
            </>
          ) : (
            <Text style={{ fontSize: '11px', color: '#666' }}>
              {record.status === 'paused' ? '已暫停' : '未排程'}
            </Text>
          )}
          <div style={{ fontSize: '10px', color: '#666', marginTop: 4 }}>
            執行次數: {record.run_count}
          </div>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: ScheduleTask) => (
        <Space>
          <Tooltip title={record.status === 'active' ? '暫停' : '啟用'}>
            <Switch
              checked={record.status === 'active'}
              onChange={(checked) => handleToggleEnabled(record.task_id, checked)}
              loading={loading}
            />
          </Tooltip>
          <Tooltip title={`自動發文：${record.auto_posting ? '開啟' : '關閉'}`}>
            <Switch
              checked={!!record.auto_posting}
              onChange={(checked) => handleToggleAutoPosting(record, checked)}
              loading={loading}
            />
          </Tooltip>
          <Tooltip title="立即執行">
            <Button
              type="link"
              icon={<ThunderboltOutlined />}
              onClick={() => handleExecuteNow(record.task_id)}
              disabled={record.status === 'active'}
            />
          </Tooltip>
          <Tooltip title="編輯配置">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEditScheduleConfig(record)}
            />
          </Tooltip>
          <Tooltip title="刪除">
            <Button
              type="link"
              icon={<DeleteOutlined />}
              danger
              onClick={() => handleDeleteSchedule(record.task_id, record.name)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    loadSchedules();
    loadDailyStats();
    fetchSchedulerStatus();
  }, []);

  // 獲取當前系統時間
  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleString('zh-TW', {
      timeZone: 'Asia/Taipei',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  const [currentTime, setCurrentTime] = useState(getCurrentTime());

  // 每秒更新時間
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(getCurrentTime());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <Title level={2} style={{ margin: 0 }}>
            <SettingOutlined style={{ marginRight: 8 }} />
            排程管理
          </Title>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Text style={{ fontSize: '14px', color: '#666' }}>
              背景排程器:
            </Text>
            <Switch
              checked={schedulerEnabled === true}
              onChange={handleSchedulerToggle}
              checkedChildren="開啟"
              unCheckedChildren="關閉"
              loading={loading || schedulerEnabled === null}
              disabled={schedulerEnabled === null}
              style={{ minWidth: '60px' }}
            />
            <Badge
              status={schedulerEnabled === true ? "success" : schedulerEnabled === false ? "default" : "processing"}
              text={schedulerEnabled === true ? "運行中" : schedulerEnabled === false ? "已停止" : "載入中..."}
              style={{ fontSize: '12px' }}
            />
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text type="secondary">管理自動發文排程和執行狀態</Text>
          <div style={{ 
            background: '#f0f2f5', 
            padding: '8px 12px', 
            borderRadius: '6px',
            border: '1px solid #d9d9d9'
          }}>
            <Text style={{ fontSize: '12px', color: '#666' }}>
              <ClockCircleOutlined style={{ marginRight: 4 }} />
              系統時間: {currentTime} (台灣時間)
            </Text>
          </div>
        </div>
      </div>

      {/* 統計卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="運行中排程" 
              value={statistics.runningCount} 
              prefix={<PlayCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="即將執行" 
              value={statistics.upcomingCount}
              suffix="個"
              prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
            {statistics.nextExecution && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                最近: {getCountdown(statistics.nextExecution || undefined, statistics.nextScheduleType || undefined, null)}
              </Text>
            )}
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="今日執行" 
              value={statistics.todayExecutionCount}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="失敗" 
              value={statistics.failedCount}
              valueStyle={{ color: '#cf1322' }}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 今日發文統計 */}
      {dailyStats && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Card title={`今日發文統計 (${dailyStats.date})`} extra={<Badge count={dailyStats.totals.generated} />}>
              <Row gutter={16}>
                <Col span={4}>
                  <Statistic 
                    title="總生成" 
                    value={dailyStats.totals.generated}
                    suffix="篇"
                    prefix={<ThunderboltOutlined style={{ color: '#1890ff' }} />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
                <Col span={4}>
                  <Statistic 
                    title="已發布" 
                    value={dailyStats.totals.published}
                    suffix="篇"
                    prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
                <Col span={4}>
                  <Statistic 
                    title="成功發布" 
                    value={dailyStats.totals.successful || 0}
                    suffix="篇"
                    prefix={<SendOutlined style={{ color: '#722ed1' }} />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Col>
                <Col span={4}>
                  <Statistic 
                    title="草稿中" 
                    value={dailyStats.totals.draft}
                    suffix="篇"
                    prefix={<EyeOutlined style={{ color: '#faad14' }} />}
                    valueStyle={{ color: '#faad14' }}
                  />
                </Col>
                <Col span={4}>
                  <Statistic 
                    title="待審查" 
                    value={dailyStats.totals.pending_review}
                    suffix="篇"
                    prefix={<ExclamationCircleOutlined style={{ color: '#fa8c16' }} />}
                    valueStyle={{ color: '#fa8c16' }}
                  />
                </Col>
                <Col span={4}>
                  <Statistic 
                    title="成功率" 
                    value={dailyStats.success_rate?.toFixed(1) || 0}
                    suffix="%"
                    valueStyle={{ color: dailyStats.success_rate > 80 ? '#52c41a' : dailyStats.success_rate > 50 ? '#faad14' : '#cf1322' }}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}

      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateSchedule}
          >
            創建新排程
          </Button>
          <Button
            icon={<ClockCircleOutlined />}
            onClick={loadSchedules}
            loading={loading}
          >
            刷新列表
          </Button>
        </div>

        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={schedules}
            rowKey="task_id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 條，共 ${total} 條`,
            }}
            scroll={{ x: 1200 }}
            size="small"
            expandable={{
              expandedRowRender: (record) => (
                <div style={{ padding: 16, background: '#fafafa' }}>
                  <Row gutter={16}>
                    <Col span={8}>
                      <Title level={5}>執行歷史</Title>
                      <Timeline>
                        {record.last_run && (
                          <Timeline.Item color="green">
                            {formatUtcToTaiwanTime(record.last_run)} - ✅ 最後執行
                          </Timeline.Item>
                        )}
                        <Timeline.Item color={record.success_count > 0 ? 'green' : 'gray'}>
                          成功: {record.success_count} 次
                        </Timeline.Item>
                        {record.failure_count > 0 && (
                          <Timeline.Item color="red">
                            失敗: {record.failure_count} 次
                          </Timeline.Item>
                        )}
                      </Timeline>
                    </Col>
                    <Col span={8}>
                      <Title level={5}>配置摘要</Title>
                      <Descriptions column={1} size="small">
                        <Descriptions.Item label="排程類型">
                          {(record as any).stock_settings?.trigger_type || record.trigger_config.trigger_type || 'N/A'}
                        </Descriptions.Item>
                        <Descriptions.Item label="股票數">
                          最多 {record.trigger_config?.max_stocks || 'N/A'} 檔
                        </Descriptions.Item>
                        <Descriptions.Item label="發文間隔">
                          {record.interval_seconds || 0} 秒
                        </Descriptions.Item>
                        <Descriptions.Item label="時區">
                          {record.schedule_config.timezone}
                        </Descriptions.Item>
                        <Descriptions.Item label="工作日執行">
                          {record.schedule_config.posting_time_slots?.[0] || '未設定'}
                        </Descriptions.Item>
                      </Descriptions>
                    </Col>
                    <Col span={8}>
                      <Title level={5}>快速操作</Title>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Button 
                          block
                          icon={<ThunderboltOutlined />}
                          onClick={() => handleExecuteNow(record.task_id)}
                          disabled={record.status !== 'active'}
                        >
                          立即執行測試
                        </Button>
                        <Button 
                          block
                          icon={<EditOutlined />}
                          onClick={() => handleEditScheduleConfig(record)}
                        >
                          編輯配置
                        </Button>
                      </Space>
                    </Col>
                  </Row>
                </div>
              ),
            }}
          />
        </Spin>
      </Card>

      {/* 排程配置Modal */}
      <ScheduleConfigModal
        visible={configModalVisible}
        onCancel={() => {
          setConfigModalVisible(false);
          setEditingSchedule(undefined);
        }}
        onSave={handleSaveConfig}
        initialData={editingSchedule as any}
      />

      {/* Schedule Execution Result Modal */}
      <ScheduleExecutionModal
        visible={executionModalVisible}
        executionResult={executionResult}
        loading={executionLoading}
        onClose={() => {
          setExecutionModalVisible(false);
          setExecutionResult(null);
        }}
      />
    </div>
  );
};

export default ScheduleManagementPage;