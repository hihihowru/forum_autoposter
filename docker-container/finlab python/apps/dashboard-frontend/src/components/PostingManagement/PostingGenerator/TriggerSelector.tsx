import React, { useState } from 'react';
import { Card, Row, Col, Radio, Space, Typography, InputNumber, Select, Divider, Button, message, Spin, Alert, Statistic, Table, Tag, AutoComplete, Input } from 'antd';
import { 
  FireOutlined, 
  RiseOutlined, 
  StockOutlined, 
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  ArrowUpOutlined,
  FallOutlined,
  SearchOutlined,
  InfoCircleOutlined,
  GlobalOutlined,
  BankOutlined,
  ThunderboltOutlined,
  AppstoreOutlined,
  EditOutlined
} from '@ant-design/icons';
import StockCodeListInput from './StockCodeListInput';
import CustomStockInput from './CustomStockInput';
import TrendingTopicsDisplay from './TrendingTopicsDisplay';
import { PostingManagementAPI } from '../../../services/postingManagementAPI';
import companyInfoService, { CompanySearchResult } from '../../../services/companyInfoService';

const { Title, Text } = Typography;
const { Option } = Select;

// 產業類別選項
const INDUSTRY_OPTIONS = [
  '光電業', '其他', '其他電子業', '化學工業', '化學生技醫療', '半導體業',
  '塑膠工業', '存託憑證', '居家生活', '建材營造', '數位雲端', '文化創意業',
  '橡膠工業', '水泥工業', '汽車工業', '油電燃氣業', '玻璃陶瓷', '生技醫療業',
  '紡織纖維', '綠能環保', '航運業', '觀光餐旅', '貿易百貨', '食品工業',
  '電機機械', '電器電纜', '電子零組件業', '電子通路業', '電腦及週邊設備業',
  '通信網路業', '鋼鐵工業', '金融業', '資訊服務業', '農業科技', '運動休閒'
];

// 新的觸發器配置接口
interface TriggerConfig {
  triggerType: 'individual' | 'sector' | 'macro' | 'news' | 'intraday' | 'volume' | 'custom';
  triggerKey: string;
  stockFilter: string;
  volumeFilter?: string;
  sectorFilter?: string;
  macroFilter?: string;
  newsFilter?: string;
  customFilters?: Record<string, any>;
}

interface TriggerSelection {
  triggerConfig?: TriggerConfig;
  threshold: number;
  changeThreshold?: {
    type: 'up' | 'down';
    percentage: number;
  };
  sectorSelection?: {
    selectedSectors: string[];
    volumeThreshold?: number;
    volumePercentile?: number;
  };
  industrySelection?: {
    enabled: boolean;
    selectedIndustries: string[];
  };
  filters?: {
    volumeFilter?: {
      type: 'high' | 'low' | 'normal' | 'custom';
      threshold?: number;
      percentile?: number;
    };
    priceFilter?: {
      type: 'above' | 'below' | 'range';
      minPrice?: number;
      maxPrice?: number;
    };
    marketCapFilter?: {
      type: 'large' | 'mid' | 'small' | 'custom';
      threshold?: number;
    };
    sectorFilter?: {
      sectors: string[];
      exclude?: boolean;
    };
  };
  stock_codes?: string[];
  stock_names?: string[];
  // 新增：股票篇數限制和篩選依據
  stockCountLimit?: number;
  stockFilterCriteria?: string[];
}

interface TriggerSelectorProps {
  value: TriggerSelection;
  onChange: (value: TriggerSelection) => void;
  onNewsConfigChange?: (newsKeywords: string[]) => void;
}

const TriggerSelector: React.FC<TriggerSelectorProps> = ({ value, onChange, onNewsConfigChange }) => {
  const [stockCountLoading, setStockCountLoading] = useState(false);
  const [stockCountResult, setStockCountResult] = useState<any>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [companySearchResults, setCompanySearchResults] = useState<CompanySearchResult[]>([]);
  const [companySearchLoading, setCompanySearchLoading] = useState(false);
  const [companySearchValue, setCompanySearchValue] = useState('');
  const [companyNameMapping, setCompanyNameMapping] = useState<Record<string, string>>({});
  const [selectedStocksForBatch, setSelectedStocksForBatch] = useState<string[]>([]);

  // 添加 highlight 樣式
  const highlightStyle = `
    .highlighted-row {
      background-color: #e6f7ff !important;
      border-left: 3px solid #1890ff !important;
    }
    .highlighted-row:hover {
      background-color: #bae7ff !important;
    }
    .selected-row {
      background-color: #f6ffed !important;
      border-left: 3px solid #52c41a !important;
    }
    .selected-row:hover {
      background-color: #d9f7be !important;
    }
  `;

  // 預設值設定 - 移除限制，使用篩選機制
  const DEFAULT_THRESHOLD = 20;  // 預設查詢 20 檔股票
  const MIN_THRESHOLD = 5;
  const MAX_THRESHOLD = 100;

  // 篩選預設值 - 增強篩選功能
  const FILTER_DEFAULTS = {
    volumeFilter: {
      type: 'high' as const,
      threshold: 50000000,
      percentile: 70
    },
    priceFilter: {
      type: 'above' as const,
      minPrice: 50,
      maxPrice: 1000
    },
    marketCapFilter: {
      type: 'large' as const,
      threshold: 10000000000
    },
    sectorFilter: {
      sectors: ['半導體', '電子', '金融'],
      exclude: false
    },
    // 新增：技術指標篩選
    technicalFilter: {
      rsi: { enabled: false, min: 30, max: 70 },
      macd: { enabled: false, bullish: true },
      bollinger: { enabled: false, breakout: true }
    },
    // 新增：基本面篩選
    fundamentalFilter: {
      pe: { enabled: false, min: 10, max: 50 },
      pb: { enabled: false, min: 1, max: 5 },
      roe: { enabled: false, min: 10 }
    },
    // 新增：討論熱度篩選
    discussionFilter: {
      newsCount: { enabled: false, min: 3 },
      socialMention: { enabled: false, min: 10 },
      analystRating: { enabled: false, min: 3 }
    },
    // 新增：成交金額篩選
    volumeAmountFilter: {
      enabled: false,
      minVolume: 10000000,  // 最小成交金額（股數）
      maxVolume: 1000000000, // 最大成交金額（股數）
      volumePercentile: 50   // 成交金額百分位
    }
  };

  // 觸發器分類配置
  const triggerCategories = [
    {
      key: 'trending',
      label: '熱門話題',
      icon: <FireOutlined />,
      color: '#f5222d',
      triggers: [
        {
          key: 'trending_topics',
          label: 'CMoney熱門話題',
          icon: <FireOutlined />,
          description: '獲取CMoney平台熱門話題',
          apiEndpoint: '/trending'
        }
      ]
    },
    {
      key: 'individual',
      label: '個股觸發器',
      icon: <StockOutlined />,
      color: '#1890ff',
      triggers: [
        {
          key: 'limit_up_after_hours',
          label: '盤後漲',
          icon: <ArrowUpOutlined />,
          description: '收盤上漲股票分析',
          stockFilter: 'limit_up_stocks',
          newsKeywords: ['上漲', '漲停', '突破', '強勢']
        },
        {
          key: 'limit_down_after_hours',
          label: '盤後跌',
          icon: <FallOutlined />,
          description: '收盤下跌股票分析',
          stockFilter: 'limit_down_stocks',
          newsKeywords: ['下跌', '跌停', '弱勢', '回檔']
        },
        {
          key: 'volume_amount_high',
          label: '成交金額高',
          icon: <BarChartOutlined />,
          description: '成交金額絕對值排序（由大到小）',
          stockFilter: 'volume_amount_high_stocks',
          newsKeywords: ['成交量', '爆量', '大量', '活躍']
        },
        {
          key: 'volume_amount_low',
          label: '成交金額低',
          icon: <BarChartOutlined />,
          description: '成交金額絕對值排序（由小到大）',
          stockFilter: 'volume_amount_low_stocks',
          newsKeywords: ['量縮', '清淡', '觀望']
        },
        {
          key: 'volume_change_rate_high',
          label: '成交金額變化率高',
          icon: <RiseOutlined />,
          description: '成交金額變化率排序（由大到小）',
          stockFilter: 'volume_change_rate_high_stocks',
          newsKeywords: ['放量', '增量', '活躍']
        },
        {
          key: 'volume_change_rate_low',
          label: '成交金額變化率低',
          icon: <FallOutlined />,
          description: '成交金額變化率排序（由小到大）',
          stockFilter: 'volume_change_rate_low_stocks',
          newsKeywords: ['縮量', '量縮', '觀望']
        }
      ]
    },
    {
      key: 'intraday',
      label: '盤中觸發器',
      icon: <ThunderboltOutlined />,
      color: '#fa8c16',
      triggers: [
        {
          key: 'intraday_gainers_by_amount',
          label: '漲幅排序+成交額',
          icon: <RiseOutlined />,
          description: '按成交額排序的漲幅股票',
          triggerType: 'intraday',
          newsKeywords: ['上漲', '漲幅', '強勢', '飆漲']
        },
        {
          key: 'intraday_volume_leaders',
          label: '成交量排序',
          icon: <BarChartOutlined />,
          description: '按成交量排序的熱門股票',
          triggerType: 'intraday',
          newsKeywords: ['成交量', '爆量', '熱門', '活躍']
        },
        {
          key: 'intraday_amount_leaders',
          label: '成交額排序',
          icon: <GlobalOutlined />,
          description: '按成交額排序的熱門股票',
          triggerType: 'intraday',
          newsKeywords: ['成交額', '大戶', '熱絡', '交投']
        },
        {
          key: 'intraday_limit_down',
          label: '跌停篩選',
          icon: <FallOutlined />,
          description: '篩選跌停股票',
          triggerType: 'intraday',
          newsKeywords: ['跌停', '重挫', '暴跌', '弱勢']
        },
        {
          key: 'intraday_limit_up',
          label: '漲停篩選',
          icon: <ArrowUpOutlined />,
          description: '篩選漲停股票',
          triggerType: 'intraday',
          newsKeywords: ['漲停', '強漲', '飆漲', '突破']
        },
        {
          key: 'intraday_limit_down_by_amount',
          label: '跌停篩選+成交額',
          icon: <FallOutlined />,
          description: '按成交額排序的跌停股票',
          triggerType: 'intraday',
          newsKeywords: ['跌停', '大跌', '賣壓', '弱勢']
        }
      ]
    },
    {
      key: 'sector',
      label: '產業',
      icon: <BankOutlined />,
      color: '#52c41a',
      triggers: [
        {
          key: 'sector_rotation',
          label: '類股輪動',
          icon: <BarChartOutlined />,
          description: '領漲類股分析',
          stockFilter: 'sector_leaders',
          sectorFilter: 'technology/finance/biotech'
        },
        {
          key: 'sector_momentum',
          label: '產業動能',
          icon: <ThunderboltOutlined />,
          description: '產業趨勢分析',
          stockFilter: 'sector_momentum_stocks',
          sectorFilter: 'ai/semiconductor/ev'
        },
        {
          key: 'sector_selection',
          label: '產業選擇',
          icon: <AppstoreOutlined />,
          description: '按產業選擇股票',
          stockFilter: 'sector_stocks',
          sectorFilter: 'multi_select'
        },
        {
          key: 'sector_news',
          label: '產業新聞',
          icon: <FileTextOutlined />,
          description: '產業政策影響',
          stockFilter: 'sector_news_stocks',
          newsFilter: 'policy/regulation/innovation'
        }
      ]
    },
    {
      key: 'macro',
      label: '總經',
      icon: <GlobalOutlined />,
      color: '#fa8c16',
      triggers: [
        {
          key: 'fed_policy',
          label: 'Fed政策',
          icon: <BankOutlined />,
          description: '聯準會政策影響',
          stockFilter: 'TWA00',
          macroFilter: 'interest_rate/inflation'
        },
        {
          key: 'economic_data',
          label: '經濟數據',
          icon: <BarChartOutlined />,
          description: '重要經濟指標',
          stockFilter: 'TWA00',
          macroFilter: 'gdp/cpi/unemployment'
        },
        {
          key: 'currency_movement',
          label: '匯率變動',
          icon: <RiseOutlined />,
          description: '匯率波動影響',
          stockFilter: 'TWA00',
          macroFilter: 'usd_twd/euro_yen'
        },
        {
          key: 'commodity_prices',
          label: '商品價格',
          icon: <FireOutlined />,
          description: '原物料價格變動',
          stockFilter: 'TWA00',
          macroFilter: 'oil/gold/copper'
        }
      ]
    },
    {
      key: 'news',
      label: '新聞',
      icon: <FileTextOutlined />,
      color: '#722ed1',
      triggers: [
        {
          key: 'company_news',
          label: '公司新聞',
          icon: <FileTextOutlined />,
          description: '個股重大消息',
          stockFilter: 'news_related_stocks',
          newsFilter: 'merger/acquisition/partnership'
        },
        {
          key: 'regulatory_news',
          label: '監管新聞',
          icon: <SettingOutlined />,
          description: '監管政策變化',
          stockFilter: 'regulated_stocks',
          newsFilter: 'approval/warning/investigation'
        },
        {
          key: 'market_news',
          label: '市場新聞',
          icon: <BarChartOutlined />,
          description: '市場情緒變化',
          stockFilter: 'TWA00',
          newsFilter: 'market_sentiment/volatility'
        },
        {
          key: 'global_news',
          label: '國際新聞',
          icon: <GlobalOutlined />,
          description: '國際事件影響',
          stockFilter: 'global_impact_stocks',
          newsFilter: 'geopolitical/trade_war'
        }
      ]
    }
  ];

  // 自定義股票獨立區塊
  const customStockSection = {
    key: 'custom',
    label: '自定義股票',
    icon: <EditOutlined />,
    color: '#722ed1',
    description: '手動輸入股票代號，包含股票搜尋功能'
  };

  // 處理觸發器選擇
  const handleTriggerSelect = (categoryKey: string, triggerKey: string) => {
    const category = triggerCategories.find(c => c.key === categoryKey);
    const trigger = category?.triggers.find(t => t.key === triggerKey);

    if (trigger) {
      const triggerConfig: TriggerConfig = {
        triggerType: categoryKey as any,
        triggerKey: triggerKey,
        stockFilter: trigger.stockFilter,
        volumeFilter: trigger.volumeFilter,
        sectorFilter: trigger.sectorFilter,
        macroFilter: trigger.macroFilter,
        newsFilter: trigger.newsFilter
      };

      // 更新觸發器配置
      onChange({
        ...value,
        triggerConfig,
        threshold: value.threshold || DEFAULT_THRESHOLD,
        filters: value.filters || FILTER_DEFAULTS
      });

      // 智能更新新聞搜尋關鍵字
      if (trigger.newsKeywords && onNewsConfigChange) {
        onNewsConfigChange(trigger.newsKeywords);
        console.log(`🎯 觸發器 "${trigger.label}" 已選擇，自動更新新聞搜尋關鍵字:`, trigger.newsKeywords);
      }
    }
  };

  // 處理自定義股票選擇
  const handleCustomStockSelect = () => {
    const triggerConfig: TriggerConfig = {
      triggerType: 'custom',
      triggerKey: 'custom_stocks',
      stockFilter: 'custom_stocks'
    };
    
    onChange({
      ...value,
      triggerConfig,
      threshold: value.threshold || DEFAULT_THRESHOLD,
      filters: value.filters || FILTER_DEFAULTS
    });
  };

  // 處理閾值變更
  const handleThresholdChange = (newThreshold: number) => {
    onChange({
      ...value,
      threshold: newThreshold
    });
  };

  // 處理漲跌幅設定變更
  const handleChangeThresholdChange = (type: 'up' | 'down', percentage: number) => {
    onChange({
      ...value,
      changeThreshold: { type, percentage }
    });
  };

  // 檢查是否需要顯示漲跌幅設定
  const shouldShowChangeThreshold = () => {
    return value.triggerConfig?.triggerKey === 'limit_up_after_hours' || 
           value.triggerConfig?.triggerKey === 'limit_down_after_hours';
  };

  // 檢查是否需要顯示產業選擇設定
  const shouldShowSectorSelection = () => {
    return value.triggerConfig?.triggerKey === 'sector_selection';
  };

  // 處理公司搜尋
  const handleCompanySearch = async (searchValue: string) => {
    if (!searchValue || searchValue.length < 2) {
      setCompanySearchResults([]);
      return;
    }

    setCompanySearchLoading(true);
    try {
      const results = await companyInfoService.smartSearch(searchValue);
      setCompanySearchResults(results);
    } catch (error) {
      console.error('公司搜尋失敗:', error);
      message.error('公司搜尋失敗');
    } finally {
      setCompanySearchLoading(false);
    }
  };

  // 處理公司選擇
  const handleCompanySelect = (company: CompanySearchResult) => {
    // 將選中的公司添加到股票代號列表
    const currentCodes = value.stock_codes || [];
    if (!currentCodes.includes(company.stock_code)) {
      onChange({
        ...value,
        stock_codes: [...currentCodes, company.stock_code],
        stock_names: [...(value.stock_names || []), company.company_name]
      });
      message.success(`已添加 ${company.company_name}(${company.stock_code})`);
    } else {
      message.info(`${company.company_name}(${company.stock_code}) 已存在`);
    }
    
    // 清空搜尋
    setCompanySearchValue('');
    setCompanySearchResults([]);
  };

  // 獲取篩選條件標籤
  const getCriterionLabel = (criterion: string): string => {
    const labels: Record<string, string> = {
      'five_day_gain': '五日漲幅篩選',
      'five_day_loss': '五日跌幅篩選',
      'daily_gain': '單日漲幅篩選',
      'daily_loss': '單日跌幅篩選',
      'volume': '成交量篩選',
      'volume_amount': '成交金額篩選',
      'market_cap': '市值篩選',
      'pe_ratio': '本益比篩選',
      'pb_ratio': '股價淨值比篩選',
      'roe': 'ROE篩選',
      'technical_indicators': '技術指標篩選',
      'news_heat': '新聞熱度篩選',
      'discussion_heat': '討論熱度篩選'
    };
    return labels[criterion] || criterion;
  };

  // 渲染篩選條件
  const renderCriterionFilter = (criterion: string) => {
    switch (criterion) {
      case 'five_day_gain':
      case 'five_day_loss':
      case 'daily_gain':
      case 'daily_loss':
        return (
          <Space>
            <Text>最小漲跌幅：</Text>
            <InputNumber
              min={0}
              max={20}
              step={0.1}
              placeholder="0"
              style={{ width: 100 }}
            />
            <Text>%</Text>
            <Text type="secondary">(篩選漲跌幅超過此值的股票)</Text>
          </Space>
        );
      
      case 'volume':
      case 'volume_amount':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Text>最小成交量：</Text>
              <InputNumber
                min={0}
                placeholder="1000000"
                style={{ width: 120 }}
              />
              <Text>股</Text>
            </Space>
            <Space>
              <Text>成交量百分位：</Text>
              <InputNumber
                min={0}
                max={100}
                placeholder="50"
                style={{ width: 100 }}
              />
              <Text>%</Text>
            </Space>
          </Space>
        );
      
      case 'market_cap':
        return (
          <Space>
            <Text>最小市值：</Text>
            <InputNumber
              min={0}
              placeholder="1000000000"
              style={{ width: 150 }}
            />
            <Text>元</Text>
          </Space>
        );
      
      case 'pe_ratio':
        return (
          <Space>
            <Text>本益比範圍：</Text>
            <InputNumber
              min={0}
              placeholder="10"
              style={{ width: 80 }}
            />
            <Text>~</Text>
            <InputNumber
              min={0}
              placeholder="50"
              style={{ width: 80 }}
            />
          </Space>
        );
      
      case 'pb_ratio':
        return (
          <Space>
            <Text>股價淨值比範圍：</Text>
            <InputNumber
              min={0}
              placeholder="1"
              style={{ width: 80 }}
            />
            <Text>~</Text>
            <InputNumber
              min={0}
              placeholder="5"
              style={{ width: 80 }}
            />
          </Space>
        );
      
      case 'roe':
        return (
          <Space>
            <Text>最小ROE：</Text>
            <InputNumber
              min={0}
              max={100}
              placeholder="10"
              style={{ width: 80 }}
            />
            <Text>%</Text>
          </Space>
        );
      
      case 'technical_indicators':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Text>RSI範圍：</Text>
              <InputNumber
                min={0}
                max={100}
                placeholder="30"
                style={{ width: 80 }}
              />
              <Text>~</Text>
              <InputNumber
                min={0}
                max={100}
                placeholder="70"
                style={{ width: 80 }}
              />
            </Space>
            <Space>
              <Text>MACD：</Text>
              <Select placeholder="選擇" style={{ width: 100 }}>
                <Option value="bullish">看多</Option>
                <Option value="bearish">看空</Option>
              </Select>
            </Space>
          </Space>
        );
      
      case 'news_heat':
        return (
          <Space>
            <Text>最小新聞數量：</Text>
            <InputNumber
              min={0}
              placeholder="3"
              style={{ width: 80 }}
            />
            <Text>篇</Text>
          </Space>
        );
      
      case 'discussion_heat':
        return (
          <Space>
            <Text>最小討論次數：</Text>
            <InputNumber
              min={0}
              placeholder="10"
              style={{ width: 80 }}
            />
            <Text>次</Text>
          </Space>
        );
      
      default:
        return <Text type="secondary">暫無詳細設定</Text>;
    }
  };

  // 單個股票選擇
  const handleStockSelection = (stockCode: string, isSelected: boolean) => {
    const currentStocks = value.stock_codes || [];
    let newSelectedStocks: string[];
    
    if (isSelected) {
      // 檢查是否已達到最大選擇數量
      const maxSelection = value.stockCountLimit || 20;
      if (currentStocks.length >= maxSelection) {
        message.warning(`最多只能選擇 ${maxSelection} 支股票`);
        return;
      }
      
      // 添加股票
      if (!currentStocks.includes(stockCode)) {
        newSelectedStocks = [...currentStocks, stockCode];
        message.success(`已選擇: ${stockCode}`);
      } else {
        newSelectedStocks = currentStocks;
        message.info(`股票 ${stockCode} 已經被選擇`);
      }
    } else {
      // 移除股票
      newSelectedStocks = currentStocks.filter(code => code !== stockCode);
      message.info(`已取消選擇: ${stockCode}`);
    }
    
    // 更新配置
    onChange({
      ...value,
      stock_codes: newSelectedStocks
    });
  };

  // 批量選擇股票 - 自動更新配置
  const handleBatchStockSelection = (action: 'select_all' | 'select_highlighted' | 'clear_all') => {
    if (!stockCountResult?.stocks) return;
    
    const threshold = value.threshold || DEFAULT_THRESHOLD;
    const maxSelection = 10; // 限制最多選擇10支股票
    let newSelectedStocks: string[] = [];
    
    switch (action) {
      case 'select_all':
        // 限制全選數量，避免選擇過多股票
        newSelectedStocks = stockCountResult.stocks
          .slice(0, Math.min(maxSelection, stockCountResult.stocks.length))
          .map((stock: any) => stock.stock_code);
        message.info(`已選擇前 ${newSelectedStocks.length} 支股票（限制最多 ${maxSelection} 支）`);
        break;
      case 'select_highlighted':
        newSelectedStocks = stockCountResult.stocks
          .slice(0, Math.min(threshold, maxSelection))
          .map((stock: any) => stock.stock_code);
        message.info(`已選擇前 ${newSelectedStocks.length} 支高亮股票`);
        break;
      case 'clear_all':
        newSelectedStocks = [];
        message.info('已清空所有選擇');
        break;
    }
    
    setSelectedStocksForBatch(newSelectedStocks);
    
    // 自動更新配置
    if (newSelectedStocks.length > 0) {
      const selectedStockNames = newSelectedStocks.map(code => 
        companyNameMapping[code] || `股票${code}`
      );
      
      const newValue = {
        ...value,
        stock_codes: newSelectedStocks,
        stock_names: selectedStockNames
      };
      
      onChange(newValue);
    } else {
      // 清空配置
      const newValue = {
        ...value,
        stock_codes: [],
        stock_names: []
      };
      onChange(newValue);
    }
  };

  // 更新選中的股票到配置中
  const updateSelectedStocksToConfig = () => {
    console.log('🔄 更新選中的股票到配置:', {
      selectedStocksForBatch,
      currentValue: value
    });
    
    if (selectedStocksForBatch.length > 0) {
      const selectedStockNames = selectedStocksForBatch.map(code => 
        companyNameMapping[code] || `股票${code}`
      );
      
      const newValue = {
        ...value,
        stock_codes: selectedStocksForBatch,
        stock_names: selectedStockNames
      };
      
      console.log('✅ 更新後的配置:', newValue);
      
      onChange(newValue);
      
      message.success(`已選擇 ${selectedStocksForBatch.length} 支股票用於批量生成`);
    } else {
      message.warning('請先選擇股票');
    }
  };

  // 處理產業成交金額閾值變更
  const handleSectorVolumeThresholdChange = (volumeThreshold: number) => {
    onChange({
      ...value,
      sectorSelection: {
        ...value.sectorSelection,
        volumeThreshold
      }
    });
  };

  // 處理產業成交金額百分位變更
  const handleSectorVolumePercentileChange = (volumePercentile: number) => {
    onChange({
      ...value,
      sectorSelection: {
        ...value.sectorSelection,
        volumePercentile
      }
    });
  };

  // 寫死的股票名稱對應表
  const getStockNameMapping = () => {
    return {
      "2330": "台積電",
      "2454": "聯發科", 
      "2317": "鴻海",
      "2881": "富邦金",
      "2882": "國泰金",
      "1101": "台泥",
      "1102": "亞泥",
      "1216": "統一",
      "1303": "南亞",
      "1326": "台化",
      "2002": "中鋼",
      "2308": "台達電",
      "2377": "微星",
      "2382": "廣達",
      "2408": "南亞科",
      "2474": "可成",
      "2498": "宏達電",
      "3008": "大立光",
      "3034": "聯詠",
      "3231": "緯創",
      "3711": "日月光投控",
      "4938": "和碩",
      "6505": "台塑化",
      "8046": "南電",
      "9910": "豐泰",
      "2412": "中華電",
      "1301": "台塑",
      "2603": "長榮",
      "2609": "陽明",
      "2615": "萬海",
      "2891": "中信金",
      "2886": "兆豐金",
      "2880": "華南金",
      "2884": "玉山金",
      "2885": "元大金",
      "2887": "台新金",
      "2888": "新光金",
      "2889": "國票金",
      "2890": "永豐金",
      "2892": "第一金",
      "2897": "王道銀行",
      "5871": "中租-KY",
      "5876": "上海商銀",
      "5880": "合庫金",
      "5881": "合庫",
      "5889": "合庫金控",
      "5905": "南茂",
      "5906": "台南",
      "5907": "大洋-KY",
      "5908": "康普",
      "5909": "全科",
      "5910": "泰博",
      "5911": "中租-KY",
      "5912": "中租-KY",
      "5913": "中租-KY",
      "5914": "中租-KY",
      "5915": "中租-KY",
      "5916": "中租-KY",
      "5917": "中租-KY",
      "5918": "中租-KY",
      "5919": "中租-KY",
      "5920": "中租-KY"
    };
  };

  // 獲取公司名稱對應表（使用 API 返回的數據）
  const loadCompanyNameMapping = (stocks: any[]) => {
    const mapping: Record<string, string> = {};
    
    stocks.forEach(stock => {
      if (stock.stock_code && stock.stock_name) {
        mapping[stock.stock_code] = stock.stock_name;
      }
    });
    
    setCompanyNameMapping(mapping);
  };

  // 查詢觸發股票數
  const handleQueryStockCount = async () => {
    if (!value.triggerConfig) {
      message.warning('請先選擇觸發器');
      return;
    }

    setStockCountLoading(true);
    try {
      // 構建查詢參數
      const queryParams: any = {
        ...value.triggerConfig,
        threshold: value.threshold,
        filters: value.filters
      };

      // 如果是盤後漲/跌觸發器，添加漲跌幅設定
      if (shouldShowChangeThreshold() && value.changeThreshold) {
        queryParams.changeThreshold = value.changeThreshold;
      }

      // 如果是產業選擇觸發器，添加產業選擇設定
      if (shouldShowSectorSelection() && value.sectorSelection) {
        queryParams.sectorSelection = value.sectorSelection;
      }
      
      // 如果有產業類別篩選，添加到參數中
      if (value.industrySelection?.enabled && value.industrySelection.selectedIndustries.length > 0) {
        queryParams.selectedIndustries = value.industrySelection.selectedIndustries;
      }

      // 調用真實的 API - 根據觸發器類型選擇不同的端點
      let result;
      const triggerKey = value.triggerConfig?.triggerKey;

      switch (triggerKey) {
        // After-hours triggers
        case 'limit_down_after_hours':
          result = await PostingManagementAPI.getAfterHoursLimitDownStocks(queryParams);
          break;
        case 'limit_up_after_hours':
          result = await PostingManagementAPI.getAfterHoursLimitUpStocks(queryParams);
          break;
        case 'volume_amount_high':
          result = await PostingManagementAPI.getAfterHoursVolumeAmountHigh(queryParams);
          break;
        case 'volume_amount_low':
          result = await PostingManagementAPI.getAfterHoursVolumeAmountLow(queryParams);
          break;
        case 'volume_change_rate_high':
          result = await PostingManagementAPI.getAfterHoursVolumeChangeRateHigh(queryParams);
          break;
        case 'volume_change_rate_low':
          result = await PostingManagementAPI.getAfterHoursVolumeChangeRateLow(queryParams);
          break;

        // Intraday triggers
        case 'intraday_gainers_by_amount':
          result = await PostingManagementAPI.getIntradayGainersByAmount(value.stockCountLimit || 20);
          break;
        case 'intraday_volume_leaders':
          result = await PostingManagementAPI.getIntradayVolumeLeaders(value.stockCountLimit || 20);
          break;
        case 'intraday_amount_leaders':
          result = await PostingManagementAPI.getIntradayAmountLeaders(value.stockCountLimit || 20);
          break;
        case 'intraday_limit_down':
          result = await PostingManagementAPI.getIntradayLimitDown(value.stockCountLimit || 20);
          break;
        case 'intraday_limit_up':
          result = await PostingManagementAPI.getIntradayLimitUp(value.stockCountLimit || 20);
          break;
        case 'intraday_limit_down_by_amount':
          result = await PostingManagementAPI.getIntradayLimitDownByAmount(value.stockCountLimit || 20);
          break;

        default:
          result = await PostingManagementAPI.getAfterHoursLimitUpStocks(queryParams);
      }
      
      setStockCountResult(result);
      
      // 獲取公司名稱對應表（僅用於顯示，不自動選取）
      if (result.stocks && result.stocks.length > 0) {
        loadCompanyNameMapping(result.stocks);
      }
      
      if (result.total_count > value.threshold) {
        message.warning(`股票數量 ${result.total_count} 超過設定閥值 ${value.threshold} 檔，可考慮使用篩選機制`);
      } else {
        message.success(`找到 ${result.total_count} 檔符合條件的股票`);
      }
    } catch (error) {
      message.error('查詢失敗，請稍後再試');
      console.error('Query stock count error:', error);
    } finally {
      setStockCountLoading(false);
    }
  };

  // 應用篩選
  const handleApplyFilters = async () => {
    if (!value.triggerConfig) return;
    
    setStockCountLoading(true);
    try {
      // 準備 API 參數，包含股票數量限制和篩選依據
      const apiParams = {
        ...value.triggerConfig,
        threshold: value.threshold,
        filters: value.filters,
        // 新增：股票數量限制和篩選依據
        stockCountLimit: value.stockCountLimit || 20,
        stockFilterCriteria: value.stockFilterCriteria || []
      };
      
      console.log('應用篩選參數:', apiParams);
      
      // 根據觸發器類型選擇不同的端點
      let result;
      const triggerKey = value.triggerConfig?.triggerKey;

      switch (triggerKey) {
        // After-hours triggers
        case 'limit_down_after_hours':
          result = await PostingManagementAPI.getAfterHoursLimitDownStocks(apiParams);
          break;
        case 'limit_up_after_hours':
          result = await PostingManagementAPI.getAfterHoursLimitUpStocks(apiParams);
          break;
        case 'volume_amount_high':
          result = await PostingManagementAPI.getAfterHoursVolumeAmountHigh(apiParams);
          break;
        case 'volume_amount_low':
          result = await PostingManagementAPI.getAfterHoursVolumeAmountLow(apiParams);
          break;
        case 'volume_change_rate_high':
          result = await PostingManagementAPI.getAfterHoursVolumeChangeRateHigh(apiParams);
          break;
        case 'volume_change_rate_low':
          result = await PostingManagementAPI.getAfterHoursVolumeChangeRateLow(apiParams);
          break;

        // Intraday triggers
        case 'intraday_gainers_by_amount':
          result = await PostingManagementAPI.getIntradayGainersByAmount(apiParams.stockCountLimit);
          break;
        case 'intraday_volume_leaders':
          result = await PostingManagementAPI.getIntradayVolumeLeaders(apiParams.stockCountLimit);
          break;
        case 'intraday_amount_leaders':
          result = await PostingManagementAPI.getIntradayAmountLeaders(apiParams.stockCountLimit);
          break;
        case 'intraday_limit_down':
          result = await PostingManagementAPI.getIntradayLimitDown(apiParams.stockCountLimit);
          break;
        case 'intraday_limit_up':
          result = await PostingManagementAPI.getIntradayLimitUp(apiParams.stockCountLimit);
          break;
        case 'intraday_limit_down_by_amount':
          result = await PostingManagementAPI.getIntradayLimitDownByAmount(apiParams.stockCountLimit);
          break;

        default:
          result = await PostingManagementAPI.getAfterHoursLimitUpStocks(apiParams);
      }
      
      setStockCountResult(result);
      
      // 根據股票數量限制截取結果
      let stocksToUse = result.stocks || [];
      if (value.stockCountLimit && stocksToUse.length > value.stockCountLimit) {
        stocksToUse = stocksToUse.slice(0, value.stockCountLimit);
        console.log(`根據限制截取前 ${value.stockCountLimit} 檔股票`);
      }
      
      // 更新篩選後的股票代號和名稱，並自動選取
      if (stocksToUse.length > 0) {
        const stockCodes = stocksToUse.map((stock: any) => stock.stock_code);
        const stockNames = stocksToUse.map((stock: any) => stock.stock_name);
        
        // 自動選取所有篩選出的股票
        onChange({
          ...value,
          stock_codes: stockCodes,
          stock_names: stockNames
        });
        
        loadCompanyNameMapping(stocksToUse);
        
        // 顯示自動選取的信息
        message.success(`已自動選取 ${stockCodes.length} 檔股票`);
      }
      
      const finalCount = stocksToUse.length;
      const totalCount = result.stocks?.length || 0;
      
      if (value.stockCountLimit && totalCount > value.stockCountLimit) {
        message.success(`篩選後找到 ${totalCount} 檔股票，已選擇前 ${finalCount} 檔`);
      } else {
        message.success(`篩選後找到 ${finalCount} 檔股票`);
      }
    } catch (error) {
      message.error('篩選失敗，請稍後再試');
      console.error('Apply filters error:', error);
    } finally {
      setStockCountLoading(false);
    }
  };

  // 渲染觸發器分類
  const renderTriggerCategory = (category: any) => (
    <Card
      key={category.key}
      title={
        <Space>
          <span style={{ color: category.color }}>{category.icon}</span>
          <span>{category.label}</span>
        </Space>
      }
      size="small"
      style={{ marginBottom: 16 }}
    >
      <Row gutter={[16, 16]}>
        {category.triggers.map((trigger: any) => (
          <Col span={8} key={trigger.key}>
            <Card
              hoverable
              size="small"
              onClick={() => handleTriggerSelect(category.key, trigger.key)}
              style={{
                border: value.triggerConfig?.triggerKey === trigger.key ? `2px solid ${category.color}` : '1px solid #d9d9d9',
                backgroundColor: value.triggerConfig?.triggerKey === trigger.key ? `${category.color}10` : '#fff'
              }}
            >
              <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }}>
                <span style={{ color: category.color, fontSize: '20px' }}>{trigger.icon}</span>
                <Text strong>{trigger.label}</Text>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {trigger.description}
                </Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  );


  return (
    <div>
      <style>{highlightStyle}</style>
      <Title level={4}>選擇觸發器</Title>
      <Text type="secondary">
        選擇一個觸發器來生成相關的股票分析內容
      </Text>
      
      <Divider />
      
      {/* 觸發器分類 */}
      {triggerCategories.map(renderTriggerCategory)}
      
      {/* 自定義股票獨立區塊 */}
      <Card
        title={
          <Space>
            <span style={{ color: customStockSection.color }}>{customStockSection.icon}</span>
            <span>{customStockSection.label}</span>
          </Space>
        }
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text type="secondary">{customStockSection.description}</Text>
          <Button
            type={value.triggerConfig?.triggerKey === 'custom_stocks' ? 'primary' : 'default'}
            icon={customStockSection.icon}
            onClick={handleCustomStockSelect}
            style={{ width: '100%' }}
          >
            啟用自定義股票
          </Button>
        </Space>
      </Card>
      
      {/* 篩選設定 */}
      <Card title="篩選設定" size="small" style={{ marginTop: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={12}>
            <Button 
              type="primary" 
              icon={<SearchOutlined />}
              onClick={handleQueryStockCount}
              loading={stockCountLoading}
              disabled={!value.triggerConfig}
            >
              查詢觸發股票數
            </Button>
          </Col>
          <Col span={12}>
            <Button 
              type="default" 
              icon={<SettingOutlined />}
              onClick={() => setShowFilters(!showFilters)}
              disabled={!stockCountResult}
            >
              {showFilters ? '隱藏篩選條件' : '顯示篩選條件'}
            </Button>
          </Col>
        </Row>
        
        {/* 漲跌幅設定 */}
        {shouldShowChangeThreshold() && (
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={24}>
              <Divider orientation="left" plain>
                <Text strong>漲跌幅設定</Text>
              </Divider>
            </Col>
            <Col span={12}>
              <Space>
                <Text strong>
                  {value.triggerConfig?.triggerKey === 'limit_up_after_hours' ? '上漲' : '下跌'}超過：
                </Text>
                <InputNumber
                  min={0.1}
                  max={20}
                  step={0.1}
                  value={value.changeThreshold?.percentage || 9.5}
                  onChange={(val) => handleChangeThresholdChange(
                    value.triggerConfig?.triggerKey === 'limit_up_after_hours' ? 'up' : 'down',
                    val || 9.5
                  )}
                  addonAfter="%"
                  style={{ width: 120 }}
                />
                <Text type="secondary">
                  (預設: 9.5%)
                </Text>
              </Space>
            </Col>
            <Col span={12}>
              <Alert
                message={`將查詢${value.triggerConfig?.triggerKey === 'limit_up_after_hours' ? '上漲' : '下跌'}超過 ${value.changeThreshold?.percentage || 9.5}% 的股票`}
                type="info"
                showIcon
                style={{ fontSize: '12px' }}
              />
            </Col>
          </Row>
        )}
        
        {/* 股票篇數限制和篩選依據 */}
        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={24}>
            <Divider orientation="left" plain>
              <Text strong>股票篇數限制與篩選依據</Text>
            </Divider>
          </Col>
          <Col span={12}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>股票篇數限制：</Text>
                <InputNumber
                  min={1}
                  max={50}
                  value={value.stockCountLimit || 20}
                  onChange={(val) => onChange({
                    ...value,
                    stockCountLimit: val || 20
                  })}
                  addonAfter="篇"
                  style={{ width: 120, marginTop: 8 }}
                />
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  (限制最多生成的股票分析篇數)
                </Text>
              </div>
            </Space>
          </Col>
          <Col span={12}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>篩選依據：</Text>
                <Select
                  mode="multiple"
                  placeholder="選擇篩選條件"
                  style={{ width: '100%', marginTop: 8 }}
                  value={value.stockFilterCriteria || []}
                  onChange={(criteria) => onChange({
                    ...value,
                    stockFilterCriteria: criteria
                  })}
                  options={[
                    { label: '五日漲幅', value: 'five_day_gain' },
                    { label: '五日跌幅', value: 'five_day_loss' },
                    { label: '單日漲幅', value: 'daily_gain' },
                    { label: '單日跌幅', value: 'daily_loss' },
                    { label: '成交量', value: 'volume' },
                    { label: '成交金額', value: 'volume_amount' },
                    { label: '市值', value: 'market_cap' },
                    { label: '本益比', value: 'pe_ratio' },
                    { label: '股價淨值比', value: 'pb_ratio' },
                    { label: 'ROE', value: 'roe' },
                    { label: '技術指標', value: 'technical_indicators' },
                    { label: '新聞熱度', value: 'news_heat' },
                    { label: '討論熱度', value: 'discussion_heat' }
                  ]}
                />
              </div>
            </Space>
          </Col>
        </Row>
        
        {/* 詳細篩選條件 */}
        {value.stockFilterCriteria && value.stockFilterCriteria.length > 0 && (
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={24}>
              <Divider orientation="left" plain>
                <Text strong>詳細篩選條件</Text>
              </Divider>
            </Col>
            {value.stockFilterCriteria.map((criterion: string) => (
              <Col span={24} key={criterion} style={{ marginBottom: 16 }}>
                <Card size="small" title={getCriterionLabel(criterion)}>
                  {renderCriterionFilter(criterion)}
                </Card>
              </Col>
            ))}
          </Row>
        )}

        {/* 產業選擇設定 */}
        {shouldShowSectorSelection() && (
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={24}>
              <Divider orientation="left" plain>
                <Text strong>產業選擇設定</Text>
              </Divider>
            </Col>
            <Col span={24}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>選擇產業：</Text>
                  <Select
                    mode="multiple"
                    placeholder="請選擇產業"
                    style={{ width: '100%', marginTop: 8 }}
                    value={value.sectorSelection?.selectedSectors || []}
                    onChange={handleSectorSelectionChange}
                    options={[
                      // 電子工業（8大類）
                      { label: '半導體業', value: 'semiconductor' },
                      { label: '電腦及週邊設備業', value: 'computer_peripheral' },
                      { label: '光電業', value: 'optoelectronics' },
                      { label: '通信網路業', value: 'communications' },
                      { label: '電子零組件業', value: 'electronic_components' },
                      { label: '電子通路業', value: 'electronic_distribution' },
                      { label: '資訊服務業', value: 'information_services' },
                      { label: '其他電子業', value: 'other_electronics' },
                      
                      // 傳統產業
                      { label: '鋼鐵工業', value: 'steel_iron' },
                      { label: '塑膠工業', value: 'petrochemical' },
                      { label: '紡織纖維', value: 'textile' },
                      { label: '食品工業', value: 'food' },
                      { label: '建材營造', value: 'construction' },
                      { label: '航運業', value: 'shipping' },
                      { label: '航空業', value: 'aviation' },
                      { label: '觀光餐旅', value: 'tourism' },
                      { label: '貿易百貨', value: 'retail' },
                      { label: '金融保險', value: 'finance' },
                      { label: '證券業', value: 'securities' },
                      { label: '生技醫療', value: 'biotech' },
                      { label: '製藥業', value: 'pharmaceutical' },
                      { label: '化學工業', value: 'chemical' },
                      { label: '玻璃陶瓷', value: 'glass_ceramics' },
                      { label: '造紙工業', value: 'paper' },
                      { label: '橡膠工業', value: 'rubber' },
                      { label: '汽車工業', value: 'automotive' },
                      { label: '電機機械', value: 'machinery' },
                      { label: '電器電纜', value: 'electrical' },
                      
                      // 新興產業
                      { label: '綠能環保', value: 'green_energy' },
                      { label: '數位雲端', value: 'digital_cloud' },
                      { label: '運動休閒', value: 'sports_leisure' },
                      { label: '居家生活', value: 'home_living' },
                      { label: '其他', value: 'other' }
                    ]}
                  />
                </div>
                <div>
                  <Text strong>成交金額篩選：</Text>
                  <Row gutter={16} style={{ marginTop: 8 }}>
                    <Col span={12}>
                      <Space>
                        <Text>絕對閾值：</Text>
                        <InputNumber
                          min={0}
                          step={1000}
                          value={value.sectorSelection?.volumeThreshold}
                          onChange={handleSectorVolumeThresholdChange}
                          addonAfter="元"
                          style={{ width: 150 }}
                          placeholder="成交金額下限"
                        />
                      </Space>
                    </Col>
                    <Col span={12}>
                      <Space>
                        <Text>相對百分位：</Text>
                        <InputNumber
                          min={1}
                          max={100}
                          value={value.sectorSelection?.volumePercentile}
                          onChange={handleSectorVolumePercentileChange}
                          addonAfter="%"
                          style={{ width: 120 }}
                          placeholder="前N%"
                        />
                      </Space>
                    </Col>
                  </Row>
                </div>
                <Alert
                  message={`將查詢選定產業中成交金額${value.sectorSelection?.volumeThreshold ? `超過 ${value.sectorSelection.volumeThreshold.toLocaleString()} 元` : ''}${value.sectorSelection?.volumePercentile ? `或前 ${value.sectorSelection.volumePercentile}%` : ''}的股票`}
                  type="info"
                  showIcon
                  style={{ fontSize: '12px' }}
                />
              </Space>
            </Col>
          </Row>
        )}
        
        {/* 篩選條件面板 - 整合到同一個 section */}
        {showFilters && (
          <div style={{ marginTop: 16 }}>
            <Divider orientation="left" plain>
              <Text strong>篩選條件</Text>
            </Divider>
            <Alert
              message="篩選機制說明"
              description="當股票數量超過閥值時，可以使用以下篩選機制來優先選擇成交量高的股票，確保發文內容的相關性和時效性。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Row gutter={16}>
              {/* 成交量篩選 */}
              <Col span={8}>
                <Text strong>成交量篩選：</Text>
                <Select
                  value={value.filters?.volumeFilter?.type || 'high'}
                  onChange={(newValue) => onChange({
                    ...value,
                    filters: {
                      ...value.filters,
                      volumeFilter: { ...value.filters?.volumeFilter, type: newValue }
                    }
                  })}
                  style={{ width: '100%' }}
                >
                  <Option value="high">高成交量 (優先)</Option>
                  <Option value="low">低成交量</Option>
                  <Option value="normal">正常成交量</Option>
                  <Option value="custom">自定義</Option>
                </Select>
              </Col>
              
              {/* 價格篩選 */}
              <Col span={8}>
                <Text strong>價格篩選：</Text>
                <Select
                  value={value.filters?.priceFilter?.type || 'above'}
                  onChange={(newValue) => onChange({
                    ...value,
                    filters: {
                      ...value.filters,
                      priceFilter: { ...value.filters?.priceFilter, type: newValue }
                    }
                  })}
                  style={{ width: '100%' }}
                >
                  <Option value="above">高價股 (預設)</Option>
                  <Option value="below">低價股</Option>
                  <Option value="range">價格區間</Option>
                </Select>
              </Col>
              
              {/* 市值篩選 */}
              <Col span={8}>
                <Text strong>市值篩選：</Text>
                <Select
                  value={value.filters?.marketCapFilter?.type || 'large'}
                  onChange={(newValue) => onChange({
                    ...value,
                    filters: {
                      ...value.filters,
                      marketCapFilter: { ...value.filters?.marketCapFilter, type: newValue }
                    }
                  })}
                  style={{ width: '100%' }}
                >
                  <Option value="large">大型股 (預設)</Option>
                  <Option value="mid">中型股</Option>
                  <Option value="small">小型股</Option>
                  <Option value="custom">自定義</Option>
                </Select>
              </Col>
            </Row>
            
            {/* 第二行：技術指標和基本面篩選 */}
            <Row gutter={16} style={{ marginTop: 16 }}>
              {/* 技術指標篩選 */}
              <Col span={8}>
                <Text strong>技術指標：</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  <Space>
                    <Text>RSI 超買超賣：</Text>
                    <Select
                      placeholder="選擇RSI範圍"
                      style={{ width: 120 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          technicalFilter: { 
                            ...value.filters?.technicalFilter, 
                            rsi: { ...value.filters?.technicalFilter?.rsi, enabled: !!value }
                          }
                        }
                      })}
                    >
                      <Option value="oversold">超賣 (&lt; 30)</Option>
                      <Option value="neutral">中性 (30-70)</Option>
                      <Option value="overbought">超買 (&gt; 70)</Option>
                    </Select>
                  </Space>
                  <Space>
                    <Text>MACD 信號：</Text>
                    <Select
                      placeholder="選擇MACD信號"
                      style={{ width: 120 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          technicalFilter: { 
                            ...value.filters?.technicalFilter, 
                            macd: { ...value.filters?.technicalFilter?.macd, enabled: !!value }
                          }
                        }
                      })}
                    >
                      <Option value="bullish">多頭信號</Option>
                      <Option value="bearish">空頭信號</Option>
                      <Option value="neutral">中性信號</Option>
                    </Select>
                  </Space>
                </Space>
              </Col>
              
              {/* 基本面篩選 */}
              <Col span={8}>
                <Text strong>基本面指標：</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  <Space>
                    <Text>本益比 (PE)：</Text>
                    <InputNumber
                      placeholder="最小值"
                      style={{ width: 80 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          fundamentalFilter: { 
                            ...value.filters?.fundamentalFilter, 
                            pe: { ...value.filters?.fundamentalFilter?.pe, min: value, enabled: !!value }
                          }
                        }
                      })}
                    />
                    <Text>-</Text>
                    <InputNumber
                      placeholder="最大值"
                      style={{ width: 80 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          fundamentalFilter: { 
                            ...value.filters?.fundamentalFilter, 
                            pe: { ...value.filters?.fundamentalFilter?.pe, max: value, enabled: !!value }
                          }
                        }
                      })}
                    />
                  </Space>
                  <Space>
                    <Text>股價淨值比 (PB)：</Text>
                    <InputNumber
                      placeholder="最小值"
                      style={{ width: 80 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          fundamentalFilter: { 
                            ...value.filters?.fundamentalFilter, 
                            pb: { ...value.filters?.fundamentalFilter?.pb, min: value, enabled: !!value }
                          }
                        }
                      })}
                    />
                    <Text>-</Text>
                    <InputNumber
                      placeholder="最大值"
                      style={{ width: 80 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          fundamentalFilter: { 
                            ...value.filters?.fundamentalFilter, 
                            pb: { ...value.filters?.fundamentalFilter?.pb, max: value, enabled: !!value }
                          }
                        }
                      })}
                    />
                  </Space>
                </Space>
              </Col>
              
              {/* 新聞熱度篩選 */}
              <Col span={6}>
                <Text strong>新聞熱度：</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  <Space>
                    <Text>新聞數量：</Text>
                    <InputNumber
                      placeholder="最少新聞數"
                      min={1}
                      style={{ width: 100 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          discussionFilter: { 
                            ...value.filters?.discussionFilter, 
                            newsCount: { ...value.filters?.discussionFilter?.newsCount, min: value, enabled: !!value }
                          }
                        }
                      })}
                    />
                  </Space>
                  <Space>
                    <Text>社群提及：</Text>
                    <InputNumber
                      placeholder="最少提及數"
                      min={1}
                      style={{ width: 100 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          discussionFilter: { 
                            ...value.filters?.discussionFilter, 
                            socialMention: { ...value.filters?.discussionFilter?.socialMention, min: value, enabled: !!value }
                          }
                        }
                      })}
                    />
                  </Space>
                </Space>
              </Col>
              
              {/* 成交金額篩選 */}
              <Col span={6}>
                <Text strong>成交金額：</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  <Space>
                    <Text>最小成交：</Text>
                    <InputNumber
                      placeholder="最小股數"
                      min={0}
                      step={1000000}
                      style={{ width: 120 }}
                      formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={(value) => value!.replace(/\$\s?|(,*)/g, '')}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          volumeAmountFilter: { 
                            ...value.filters?.volumeAmountFilter, 
                            minVolume: value, 
                            enabled: !!value
                          }
                        }
                      })}
                    />
                  </Space>
                  <Space>
                    <Text>最大成交：</Text>
                    <InputNumber
                      placeholder="最大股數"
                      min={0}
                      step={1000000}
                      style={{ width: 120 }}
                      formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={(value) => value!.replace(/\$\s?|(,*)/g, '')}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          volumeAmountFilter: { 
                            ...value.filters?.volumeAmountFilter, 
                            maxVolume: value, 
                            enabled: !!value
                          }
                        }
                      })}
                    />
                  </Space>
                  <Space>
                    <Text>成交百分位：</Text>
                    <Select
                      placeholder="選擇百分位"
                      style={{ width: 120 }}
                      onChange={(value) => onChange({
                        ...value,
                        filters: {
                          ...value.filters,
                          volumeAmountFilter: { 
                            ...value.filters?.volumeAmountFilter, 
                            volumePercentile: value, 
                            enabled: !!value
                          }
                        }
                      })}
                    >
                      <Option value={90}>前10%</Option>
                      <Option value={80}>前20%</Option>
                      <Option value={70}>前30%</Option>
                      <Option value={60}>前40%</Option>
                      <Option value={50}>前50%</Option>
                    </Select>
                  </Space>
                </Space>
              </Col>
            </Row>
            
            <Button 
              type="primary" 
              onClick={handleApplyFilters}
              style={{ marginTop: 16 }}
              loading={stockCountLoading}
            >
              應用篩選
            </Button>
          </div>
        )}
      </Card>
      
      {/* 符合條件的股票列表 - 獨立 section */}
      {stockCountResult && (
        <Card title="符合條件的股票列表" size="small" style={{ marginTop: 16 }}>
          {/* 篩選閾值設定 */}
          <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Space>
                <Text strong>篩選閾值：</Text>
                <InputNumber
                  min={MIN_THRESHOLD}
                  max={MAX_THRESHOLD}
                  value={value.threshold || DEFAULT_THRESHOLD}
                  onChange={handleThresholdChange}
                  addonAfter="檔"
                  style={{ width: 120 }}
                />
                <Text type="secondary">
                  (預設: {DEFAULT_THRESHOLD}檔)
                </Text>
              </Space>
            </Col>
            <Col span={8}>
              <Space>
                <Text strong>已選擇：</Text>
                <Tag color="blue">{selectedStocksForBatch.length} 支股票</Tag>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  (選擇後自動更新配置)
                </Text>
              </Space>
            </Col>
            <Col span={8}>
              <Space>
                <Button 
                  size="small"
                  onClick={() => handleBatchStockSelection('select_highlighted')}
                >
                  選擇高亮股票
                </Button>
                <Button 
                  size="small"
                  onClick={() => handleBatchStockSelection('select_all')}
                >
                  全選
                </Button>
                <Button 
                  size="small"
                  onClick={() => handleBatchStockSelection('clear_all')}
                >
                  清空
                </Button>
              </Space>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={6}>
              <Statistic 
                title="符合條件的股票數量" 
                value={stockCountResult.total_count}
                suffix="檔"
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="篩選後數量" 
                value={stockCountResult.filtered_count || stockCountResult.total_count}
                suffix="檔"
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="當前閾值" 
                value={value.threshold || DEFAULT_THRESHOLD}
                suffix="檔"
                valueStyle={{ color: '#faad14' }}
              />
            </Col>
            <Col span={6}>
              <Card 
                size="small" 
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  textAlign: 'center'
                }}
              >
                <Statistic 
                  title={<span style={{ color: 'white' }}>已選擇股票</span>}
                  value={selectedStocksForBatch.length}
                  suffix="檔"
                  valueStyle={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text style={{ color: 'white', fontSize: '12px' }}>
                    選擇後自動更新配置
                  </Text>
                </div>
              </Card>
            </Col>
          </Row>
          
          {stockCountResult.total_count > (value.threshold || DEFAULT_THRESHOLD) && (
            <Alert
              message={`股票數量 ${stockCountResult.total_count} 超過設定閥值 ${value.threshold || DEFAULT_THRESHOLD} 檔，建議使用篩選機制`}
              type="warning"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
          
          {/* 股票列表顯示 */}
          {stockCountResult.stocks && stockCountResult.stocks.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Table
                size="small"
                rowKey="stock_code"
                dataSource={stockCountResult.stocks.slice(0, 50)} // 只顯示前50支股票
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total, range) => `顯示 ${range[0]}-${range[1]} 共 ${total} 支股票`
                }}
                rowClassName={(record, index) => {
                  // 根據篩選結果添加 highlight 樣式
                  const isHighlighted = index < (value.threshold || DEFAULT_THRESHOLD);
                  const isSelected = (value.stock_codes || []).includes(record.stock_code);
                  
                  if (isSelected) {
                    return 'selected-row';
                  } else if (isHighlighted) {
                    return 'highlighted-row';
                  }
                  return '';
                }}
                columns={[
                  {
                    title: '股票代號',
                    dataIndex: 'stock_code',
                    key: 'stock_code',
                    width: 100,
                    sorter: (a: any, b: any) => a.stock_code.localeCompare(b.stock_code),
                    render: (text) => <Text code>{text}</Text>
                  },
                  {
                    title: '股票名稱',
                    dataIndex: 'stock_code',
                    key: 'stock_name',
                    width: 150,
                    sorter: (a: any, b: any) => {
                      // 優先使用 API 返回的股票名稱進行排序
                      const nameA = a.stock_name || companyNameMapping[a.stock_code] || '';
                      const nameB = b.stock_name || companyNameMapping[b.stock_code] || '';
                      return nameA.localeCompare(nameB);
                    },
                    render: (stockCode: string, record: any) => {
                      // 優先使用 API 返回的股票名稱，其次使用映射表
                      const companyName = record.stock_name || companyNameMapping[stockCode] || `股票${stockCode}`;
                      return (
                        <div>
                          <div style={{ fontWeight: 'bold' }}>
                            {companyName}
                          </div>
                          <div style={{ fontSize: '12px', color: '#666' }}>
                            {stockCode}
                          </div>
                        </div>
                      );
                    }
                  },
                  {
                    title: '產業類別',
                    dataIndex: 'industry',
                    key: 'industry',
                    width: 120,
                    sorter: (a: any, b: any) => (a.industry || '').localeCompare(b.industry || ''),
                    render: (industry: string) => (
                      <Tag color="blue" style={{ fontSize: '11px' }}>
                        {industry || '未知'}
                      </Tag>
                    )
                  },
                  {
                    title: '當前價格',
                    dataIndex: 'current_price',
                    key: 'current_price',
                    width: 100,
                    sorter: (a: any, b: any) => a.current_price - b.current_price,
                    render: (price) => `${price}`  // 移除 $ 符號
                  },
                  {
                    title: '漲跌幅',
                    dataIndex: 'change_percent',
                    key: 'change_percent',
                    width: 100,
                    sorter: (a: any, b: any) => a.change_percent - b.change_percent,
                    render: (percent) => (
                      <Tag color={percent > 0 ? 'red' : 'green'}>
                        {percent > 0 ? '+' : ''}{percent}%
                      </Tag>
                    )
                  },
                  {
                    title: '成交金額',
                    dataIndex: 'volume',
                    key: 'volume',
                    width: 120,
                    sorter: (a: any, b: any) => (a.volume || 0) - (b.volume || 0),
                    render: (amount) => {
                      if (!amount || typeof amount !== 'number') {
                        return '0';
                      }
                      if (amount >= 100000000) {
                        return `${(amount / 100000000).toFixed(2)}億`;
                      } else if (amount >= 10000) {
                        return `${(amount / 10000).toFixed(0)}萬`;
                      }
                      return amount.toLocaleString();
                    }
                  },
                  {
                    title: '成交量排名',
                    dataIndex: 'volume_rank',
                    key: 'volume_rank',
                    width: 100,
                    sorter: (a: any, b: any) => (a.volume_rank || 999999) - (b.volume_rank || 999999),
                    render: (rank) => rank ? `#${rank}` : '-'
                  },
                  {
                    title: '五日上漲天數',
                    dataIndex: 'up_days_5',
                    key: 'up_days_5',
                    width: 120,
                    sorter: (a: any, b: any) => (a.up_days_5 || 0) - (b.up_days_5 || 0),
                    render: (upDays) => (
                      <Tag color={upDays >= 3 ? 'green' : upDays >= 2 ? 'orange' : 'red'}>
                        {upDays}/5 天
                      </Tag>
                    )
                  },
                  {
                    title: '五日漲跌幅',
                    dataIndex: 'five_day_change',
                    key: 'five_day_change',
                    width: 120,
                    sorter: (a: any, b: any) => (a.five_day_change || 0) - (b.five_day_change || 0),
                    render: (change) => (
                      <span style={{ 
                        color: change > 0 ? '#52c41a' : change < 0 ? '#f5222d' : '#666'
                      }}>
                        {change > 0 ? '+' : ''}{change}%
                      </span>
                    )
                  },
                  {
                    title: '操作',
                    key: 'action',
                    width: 120,
                    render: (_, record, index) => {
                      const isHighlighted = index < (value.threshold || DEFAULT_THRESHOLD);
                      const isSelected = (value.stock_codes || []).includes(record.stock_code);
                      const companyName = companyNameMapping[record.stock_code];
                      
                      return (
                        <Space>
                          <Button 
                            type={isSelected ? "primary" : "default"}
                            size="small"
                            onClick={() => handleStockSelection(record.stock_code, !isSelected)}
                          >
                            {isSelected ? '已選' : '選擇'}
                          </Button>
                          <Tag color={isHighlighted ? 'blue' : 'default'} size="small">
                            {isHighlighted ? '高亮' : '一般'}
                          </Tag>
                        </Space>
                      );
                    }
                  }
                ]}
                scroll={{ x: 700 }}
              />
              {stockCountResult.stocks.length > 50 && (
                <Alert
                  message={`僅顯示前50支股票，共找到 ${stockCountResult.stocks.length} 支符合條件的股票`}
                  type="info"
                  showIcon
                  style={{ marginTop: 8 }}
                />
              )}
            </div>
          )}
        </Card>
      )}
      
      {/* 自定義股票輸入 */}
      {value.triggerConfig?.triggerKey === 'custom_stocks' && (
        <Card title="自定義股票" size="small" style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {/* 公司搜尋 */}
            <div>
              <Text strong>公司名稱搜尋：</Text>
              <AutoComplete
                value={companySearchValue}
                onChange={handleCompanySearch}
                placeholder="輸入公司名稱或股票代號"
                style={{ width: '100%', marginTop: 8 }}
                loading={companySearchLoading}
                options={companySearchResults.map(company => ({
                  value: `${company.company_name}(${company.stock_code})`,
                  label: (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Text strong>{company.company_name}</Text>
                        <Text type="secondary" style={{ marginLeft: 8 }}>({company.stock_code})</Text>
                      </div>
                      <Tag color="blue">{company.industry}</Tag>
                    </div>
                  ),
                  company: company
                }))}
                onSelect={(value, option) => {
                  if (option.company) {
                    handleCompanySelect(option.company);
                  }
                }}
                filterOption={false}
              />
              {companySearchResults.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">找到 {companySearchResults.length} 個結果</Text>
                </div>
              )}
            </div>
            
            {/* 已選擇的股票 */}
            {(value.stock_codes && value.stock_codes.length > 0) && (
              <div>
                <Text strong>已選擇的股票：</Text>
                <div style={{ marginTop: 8 }}>
                  {value.stock_codes.map((code, index) => (
                    <Tag 
                      key={code} 
                      closable 
                      onClose={() => {
                        const newCodes = value.stock_codes?.filter(c => c !== code) || [];
                        const newNames = value.stock_names?.filter((_, i) => i !== index) || [];
                        onChange({
                          ...value,
                          stock_codes: newCodes,
                          stock_names: newNames
                        });
                      }}
                      style={{ marginBottom: 4 }}
                    >
                      {value.stock_names?.[index] || code} ({code})
                    </Tag>
                  ))}
                </div>
              </div>
            )}
            
            <CustomStockInput
              value={value.stock_codes || []}
              onChange={(codes) => onChange({
                ...value,
                stock_codes: codes
              })}
              onStockNamesChange={(names) => onChange({
                ...value,
                stock_names: names
              })}
            />
          </Space>
        </Card>
      )}
      

      {/* 股票代號列表輸入 */}
      {value.triggerConfig?.triggerKey === 'stock_code_list' && (
        <Card title="股票代號列表" size="small" style={{ marginTop: 16 }}>
          <StockCodeListInput
            value={value.stock_codes || []}
            onChange={(codes) => onChange({
              ...value,
              stock_codes: codes
            })}
            onStockNamesChange={(names) => onChange({
              ...value,
              stock_names: names
            })}
          />
        </Card>
      )}
    </div>
  );
};

export default TriggerSelector;