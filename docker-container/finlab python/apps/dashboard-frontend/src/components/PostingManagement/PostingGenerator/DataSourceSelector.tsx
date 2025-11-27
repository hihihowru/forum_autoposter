import React, { useState } from 'react';
import { Card, Checkbox, Space, Typography, Tag, Collapse, Tooltip, Badge } from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  DollarOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Panel } = Collapse;

// ============================================
// DTNO 三層數據結構定義
// ============================================

interface DTNOColumn {
  id: string;
  name: string;
  table_id: string;
}

interface DTNOSubCategory {
  id: string;
  name: string;
  columns: DTNOColumn[];
}

interface DTNOCategory {
  id: 'fundamental' | 'technical' | 'chip';
  name: string;
  icon: React.ReactNode;
  color: string;
  subCategories: DTNOSubCategory[];
}

// 完整的 DTNO 數據結構
const DTNO_DATA_STRUCTURE: DTNOCategory[] = [
  {
    id: 'fundamental',
    name: '基本面',
    icon: <BarChartOutlined />,
    color: '#52c41a',
    subCategories: [
      {
        id: 'revenue',
        name: '營收統計',
        columns: [
          { id: 'monthly_revenue', name: '單月合併營收(千)', table_id: '115694491' },
          { id: 'revenue_yoy', name: '單月合併營收年成長(%)', table_id: '115694491' },
          { id: 'revenue_mom', name: '單月合併營收月變動(%)', table_id: '115694491' },
          { id: 'revenue_cumulative', name: '累計合併營收成長(%)', table_id: '115694491' },
          { id: 'revenue_3m_yoy', name: '近三月合併營收年成長(%)', table_id: '115694491' },
          { id: 'revenue_12m', name: '近12月營收合併成長(%)', table_id: '115694491' },
          { id: 'revenue_ath', name: '單月營收創歷史新高', table_id: '115694276' },
          { id: 'revenue_streak', name: '單月營收連N個月遞增', table_id: '115694276' },
        ]
      },
      {
        id: 'eps',
        name: 'EPS與盈餘',
        columns: [
          { id: 'eps', name: '每股稅後盈餘(元)', table_id: '115694323' },
          { id: 'eps_streak', name: 'EPS連N季遞增', table_id: '115694323' },
          { id: 'eps_nth_high', name: 'EPS創N季新高', table_id: '115694323' },
          { id: 'eps_ath', name: 'EPS創歷史新高', table_id: '115694323' },
          { id: 'est_eps', name: '機構估稅後EPS(元)', table_id: '115694449' },
          { id: 'est_eps_optimistic', name: '最樂觀估稅後EPS', table_id: '115694449' },
          { id: 'est_eps_pessimistic', name: '最悲觀估稅後EPS', table_id: '115694449' },
          { id: 'est_eps_growth', name: '預估年稅後EPS成長(%)', table_id: '115694449' },
          { id: 'next_year_eps', name: '明年機構估稅後EPS', table_id: '115694449' },
        ]
      },
      {
        id: 'profitability',
        name: '獲利能力',
        columns: [
          { id: 'gross_margin', name: '毛利率(%)', table_id: '115694323' },
          { id: 'gross_margin_streak', name: '毛利率連N季遞增', table_id: '115694323' },
          { id: 'op_margin', name: '營業利益率(%)', table_id: '115694323' },
          { id: 'op_margin_streak', name: '營益率連N季遞增', table_id: '115694323' },
          { id: 'net_margin', name: '稅後純益率(%)', table_id: '115694323' },
          { id: 'net_margin_streak', name: '純益率連N季遞增', table_id: '115694323' },
          { id: 'roe', name: 'ROE(%)', table_id: '115694602' },
          { id: 'roe_streak', name: 'ROE連N季遞增', table_id: '115694323' },
        ]
      },
      {
        id: 'financial_health',
        name: '財務健康',
        columns: [
          { id: 'debt_ratio', name: '負債比率(%)', table_id: '115694602' },
          { id: 'current_ratio', name: '流動比率(%)', table_id: '115694602' },
          { id: 'quick_ratio', name: '速動比率(%)', table_id: '115694602' },
          { id: 'interest_coverage', name: '利息保障倍數', table_id: '115694602' },
          { id: 'inventory_days', name: '存貨週轉天數', table_id: '115694602' },
          { id: 'cash_flow_ratio', name: '現金流量比率(%)', table_id: '115694602' },
        ]
      },
      {
        id: 'dividend',
        name: '股利政策',
        columns: [
          { id: 'dividend_frequency', name: '盈餘分派頻率', table_id: '115394894' },
          { id: 'dividend_total', name: '股利合計(元)', table_id: '115394894' },
          { id: 'dividend_yield', name: '現金股利殖利率(%)', table_id: '115394894' },
          { id: 'payout_ratio', name: '股利發放率(%)', table_id: '115394894' },
          { id: 'ex_dividend_date', name: '除權息日期', table_id: '115394894' },
        ]
      },
      {
        id: 'analyst_rating',
        name: '機構評等',
        columns: [
          { id: 'target_price', name: '目標價', table_id: '115694873' },
          { id: 'analyst_eps', name: '預估EPS', table_id: '115694873' },
          { id: 'rating', name: '多空評等', table_id: '115694873' },
          { id: 'analyst_count', name: '預測機構數', table_id: '115694449' },
          { id: 'pe_high', name: '最高本益比', table_id: '115694449' },
          { id: 'pe_low', name: '最低本益比', table_id: '115694449' },
        ]
      },
    ]
  },
  {
    id: 'technical',
    name: '技術面',
    icon: <LineChartOutlined />,
    color: '#1890ff',
    subCategories: [
      {
        id: 'momentum',
        name: '價格動能',
        columns: [
          { id: 'return_1d', name: '日報酬率(%)', table_id: '115695101' },
          { id: 'return_1w', name: '週報酬率(%)', table_id: '115695101' },
          { id: 'return_1m', name: '月報酬率(%)', table_id: '115695101' },
          { id: 'return_3m', name: '季報酬率(%)', table_id: '115695101' },
          { id: 'return_6m', name: '半年報酬率(%)', table_id: '115695101' },
          { id: 'return_1y', name: '年報酬率(%)', table_id: '115695101' },
          { id: 'vs_market', name: '與大盤比報酬率(%)', table_id: '115695101' },
        ]
      },
      {
        id: 'ma',
        name: '均線系統',
        columns: [
          { id: 'ma5', name: '週線(5MA)', table_id: '115694997' },
          { id: 'ma20', name: '月線(20MA)', table_id: '115694997' },
          { id: 'ma60', name: '季線(60MA)', table_id: '115694997' },
          { id: 'ma120', name: '半年線(120MA)', table_id: '115694997' },
          { id: 'ma240', name: '年線(240MA)', table_id: '115694997' },
          { id: 'ma_3y', name: '3年線', table_id: '115694997' },
          { id: 'ma_5y', name: '5年線', table_id: '115694997' },
        ]
      },
      {
        id: 'kd',
        name: 'KD指標',
        columns: [
          { id: 'k_daily', name: '日K(9)', table_id: '115695868' },
          { id: 'd_daily', name: '日D(9)', table_id: '115695868' },
          { id: 'k_weekly', name: '週K(9)', table_id: '115695868' },
          { id: 'd_weekly', name: '週D(9)', table_id: '115695868' },
          { id: 'k_monthly', name: '月K(9)', table_id: '115695868' },
          { id: 'd_monthly', name: '月D(9)', table_id: '115695868' },
        ]
      },
      {
        id: 'rsi',
        name: 'RSI指標',
        columns: [
          { id: 'rsi5_daily', name: '日RSI(5)', table_id: '115695868' },
          { id: 'rsi10_daily', name: '日RSI(10)', table_id: '115695868' },
          { id: 'rsi5_weekly', name: '週RSI(5)', table_id: '115695868' },
          { id: 'rsi10_weekly', name: '週RSI(10)', table_id: '115695868' },
          { id: 'rsi5_monthly', name: '月RSI(5)', table_id: '115695868' },
          { id: 'rsi10_monthly', name: '月RSI(10)', table_id: '115695868' },
        ]
      },
      {
        id: 'macd',
        name: 'MACD指標',
        columns: [
          { id: 'dif_daily', name: '日DIF', table_id: '115695868' },
          { id: 'macd_daily', name: '日MACD', table_id: '115695868' },
          { id: 'osc_daily', name: 'DIF-MACD', table_id: '115695868' },
          { id: 'dif_weekly', name: '週DIF', table_id: '115695868' },
          { id: 'macd_weekly', name: '週MACD', table_id: '115695868' },
          { id: 'dif_monthly', name: '月DIF', table_id: '115695868' },
          { id: 'macd_monthly', name: '月MACD', table_id: '115695868' },
        ]
      },
      {
        id: 'bias',
        name: '乖離率',
        columns: [
          { id: 'bias_20', name: '乖離率(20日)', table_id: '115695868' },
          { id: 'bias_60', name: '乖離率(60日)', table_id: '115695868' },
          { id: 'bias_250', name: '乖離率(250日)', table_id: '115695868' },
        ]
      },
      {
        id: 'volatility',
        name: '波動率',
        columns: [
          { id: 'volatility_21d', name: '年化波動度(21D)', table_id: '115695868' },
          { id: 'volatility_250d', name: '年化波動度(250D)', table_id: '115695868' },
          { id: 'beta_21d', name: 'Beta係數(21D)', table_id: '115695868' },
          { id: 'beta_250d', name: 'Beta係數(250D)', table_id: '115695868' },
          { id: 'alpha_250d', name: 'Alpha(250D)', table_id: '115695868' },
          { id: 'hist_vol_1m', name: '近一月歷史波動率(%)', table_id: '115695868' },
          { id: 'hist_vol_3m', name: '近三月歷史波動率(%)', table_id: '115695868' },
        ]
      },
    ]
  },
  {
    id: 'chip',
    name: '籌碼面',
    icon: <DollarOutlined />,
    color: '#faad14',
    subCategories: [
      {
        id: 'institutional',
        name: '三大法人',
        columns: [
          { id: 'foreign_net', name: '外資買賣超(張)', table_id: '115696346' },
          { id: 'trust_net', name: '投信買賣超(張)', table_id: '115696346' },
          { id: 'dealer_net', name: '自營商買賣超(張)', table_id: '115696346' },
          { id: 'inst_total', name: '三大法人合計', table_id: '115696346' },
          { id: 'foreign_pct', name: '外資持股比率(%)', table_id: '115696346' },
          { id: 'trust_pct', name: '投信持股比率(%)', table_id: '115696346' },
          { id: 'dealer_pct', name: '自營商持股比率(%)', table_id: '115696346' },
          { id: 'inst_pct', name: '法人持股比率(%)', table_id: '115696346' },
        ]
      },
      {
        id: 'foreign_detail',
        name: '外資詳細',
        columns: [
          { id: 'foreign_buy', name: '外資買張', table_id: '115696245' },
          { id: 'foreign_sell', name: '外資賣張', table_id: '115696245' },
          { id: 'foreign_holdings', name: '外資持股張數', table_id: '115696245' },
          { id: 'foreign_value', name: '外資持股市值(百萬)', table_id: '115696245' },
          { id: 'foreign_avg_buy', name: '外資買均價', table_id: '115696245' },
          { id: 'foreign_avg_sell', name: '外資賣均價', table_id: '115696245' },
          { id: 'foreign_cost', name: '外資持股成本', table_id: '115696245' },
        ]
      },
      {
        id: 'trust_detail',
        name: '投信詳細',
        columns: [
          { id: 'trust_buy', name: '投信買張', table_id: '115696307' },
          { id: 'trust_sell', name: '投信賣張', table_id: '115696307' },
          { id: 'trust_inventory', name: '投信庫存', table_id: '115696307' },
          { id: 'trust_value', name: '投信持股市值(百萬)', table_id: '115696307' },
          { id: 'trust_cost', name: '投信持股成本', table_id: '115696307' },
        ]
      },
      {
        id: 'concentration',
        name: '籌碼集中度',
        columns: [
          { id: 'conc_1d', name: '近1日籌碼集中度', table_id: '115085458' },
          { id: 'conc_5d', name: '近5日籌碼集中度', table_id: '115085458' },
          { id: 'conc_10d', name: '近10日籌碼集中度', table_id: '115085458' },
          { id: 'conc_20d', name: '近20日籌碼集中度', table_id: '115085458' },
          { id: 'conc_60d', name: '近60日籌碼集中度', table_id: '115085458' },
          { id: 'conc_120d', name: '近120日籌碼集中度', table_id: '115085458' },
        ]
      },
      {
        id: 'major_trading',
        name: '主力買賣超',
        columns: [
          { id: 'major_1d', name: '近1日主力買賣超', table_id: '115696668' },
          { id: 'major_5d', name: '近5日主力買賣超', table_id: '115696668' },
          { id: 'major_10d', name: '近10日主力買賣超', table_id: '115696668' },
          { id: 'major_20d', name: '近20日主力買賣超', table_id: '115696668' },
          { id: 'major_60d', name: '近60日主力買賣超', table_id: '115696668' },
          { id: 'major_pct', name: '主力買賣超佔成交量(%)', table_id: '115696668' },
          { id: 'major_cost', name: '主力成本線', table_id: '115696668' },
        ]
      },
      {
        id: 'broker',
        name: '券商分點',
        columns: [
          { id: 'top1_buy', name: '第一大券商買超(張)', table_id: '115696587' },
          { id: 'top5_buy', name: '前五大券商買超(張)', table_id: '115696587' },
          { id: 'top1_sell', name: '第一大券商賣超(張)', table_id: '115696587' },
          { id: 'top5_sell', name: '前五大券商賣超(張)', table_id: '115696587' },
          { id: 'buy_broker_count', name: '買超券商家數', table_id: '115696587' },
          { id: 'sell_broker_count', name: '賣超券商家數', table_id: '115696587' },
          { id: 'abnormal_broker', name: '籌碼異常券商', table_id: '115085458' },
        ]
      },
      {
        id: 'major_streak',
        name: '主力連續買賣',
        columns: [
          { id: 'top1_streak', name: 'Top1主力連N日買', table_id: '115696523' },
          { id: 'top5_streak', name: 'Top5主力連N日買', table_id: '115696523' },
          { id: 'top10_streak', name: 'Top10主力連N日買', table_id: '115696523' },
          { id: 'major_new_high', name: '主力買賣超創N日新高', table_id: '115696523' },
          { id: 'buy_sell_diff', name: '買賣家數差', table_id: '115696523' },
        ]
      },
      {
        id: 'winner_loser',
        name: '贏家/輸家統計',
        columns: [
          { id: 'winner_1d', name: '近1日贏家買賣超', table_id: '115085952' },
          { id: 'winner_5d', name: '近5日贏家買賣超', table_id: '115085952' },
          { id: 'winner_20d', name: '近20日贏家買賣超', table_id: '115085952' },
          { id: 'loser_1d', name: '近1日輸家買賣超', table_id: '115085952' },
          { id: 'loser_5d', name: '近5日輸家買賣超', table_id: '115085952' },
          { id: 'loser_20d', name: '近20日輸家買賣超', table_id: '115085952' },
        ]
      },
    ]
  }
];

// ============================================
// Interface 定義
// ============================================

interface DataSourceSelection {
  // 第一層：大分類
  categories: string[];  // ['fundamental', 'technical', 'chip']
  // 第二層：小分類 (選擇小分類會自動包含該分類下所有欄位)
  subCategories: string[];  // ['revenue', 'eps', 'ma', 'kd', 'institutional']
  // 新聞來源 (保留)
  news_sources: string[];
}

interface DataSourceSelectorProps {
  value: DataSourceSelection;
  onChange: (value: DataSourceSelection) => void;
}

// ============================================
// Component
// ============================================

const DataSourceSelector: React.FC<DataSourceSelectorProps> = ({ value, onChange }) => {
  const [expandedCategories, setExpandedCategories] = useState<string[]>(['fundamental', 'technical', 'chip']);

  const newsSources = [
    '工商時報', '經濟日報', '中央社', '鉅亨網', 'MoneyDJ', 'Yahoo財經',
    '中時電子報', '聯合新聞網', '自由時報', 'ETtoday', '東森新聞',
    'TVBS', '三立新聞', '非凡新聞', '財訊', '今周刊', '天下雜誌'
  ];

  // 檢查小分類是否被選中
  const isSubCategorySelected = (subCategoryId: string): boolean => {
    return value.subCategories?.includes(subCategoryId) || false;
  };

  // 檢查大分類是否全選
  const isCategoryFullySelected = (categoryId: string): boolean => {
    const category = DTNO_DATA_STRUCTURE.find(c => c.id === categoryId);
    if (!category) return false;
    return category.subCategories.every(sub => isSubCategorySelected(sub.id));
  };

  // 檢查大分類是否部分選中
  const isCategoryPartiallySelected = (categoryId: string): boolean => {
    const category = DTNO_DATA_STRUCTURE.find(c => c.id === categoryId);
    if (!category) return false;
    const selectedCount = category.subCategories.filter(sub => isSubCategorySelected(sub.id)).length;
    return selectedCount > 0 && selectedCount < category.subCategories.length;
  };

  // 處理大分類選擇
  const handleCategoryChange = (categoryId: string, checked: boolean) => {
    const category = DTNO_DATA_STRUCTURE.find(c => c.id === categoryId);
    if (!category) return;

    const subCategoryIds = category.subCategories.map(sub => sub.id);

    let newSubCategories: string[];
    if (checked) {
      // 全選該分類下所有小分類
      newSubCategories = [...new Set([...(value.subCategories || []), ...subCategoryIds])];
    } else {
      // 取消該分類下所有小分類
      newSubCategories = (value.subCategories || []).filter(id => !subCategoryIds.includes(id));
    }

    onChange({
      ...value,
      subCategories: newSubCategories
    });
  };

  // 處理小分類選擇
  const handleSubCategoryChange = (subCategoryId: string, checked: boolean) => {
    let newSubCategories: string[];
    if (checked) {
      newSubCategories = [...(value.subCategories || []), subCategoryId];
    } else {
      newSubCategories = (value.subCategories || []).filter(id => id !== subCategoryId);
    }

    onChange({
      ...value,
      subCategories: newSubCategories
    });
  };

  // 處理新聞來源選擇
  const handleNewsSourceChange = (source: string, checked: boolean) => {
    let newSources: string[];
    if (checked) {
      newSources = [...(value.news_sources || []), source];
    } else {
      newSources = (value.news_sources || []).filter(s => s !== source);
    }

    onChange({
      ...value,
      news_sources: newSources
    });
  };

  const handleSelectAllNewsSources = (checked: boolean) => {
    onChange({
      ...value,
      news_sources: checked ? [...newsSources] : []
    });
  };

  // 計算選中的小分類數量
  const getSelectedSubCategoryCount = (categoryId: string): number => {
    const category = DTNO_DATA_STRUCTURE.find(c => c.id === categoryId);
    if (!category) return 0;
    return category.subCategories.filter(sub => isSubCategorySelected(sub.id)).length;
  };

  // 獲取小分類的欄位數量
  const getColumnCount = (subCategory: DTNOSubCategory): number => {
    return subCategory.columns.length;
  };

  return (
    <div>
      <Title level={4}>選擇數據源 (DTNO)</Title>
      <Text type="secondary">
        選擇需要的數據分類，系統將自動獲取該分類下的所有欄位數據
      </Text>

      {/* DTNO 三層數據結構 */}
      <Collapse
        activeKey={expandedCategories}
        onChange={(keys) => setExpandedCategories(keys as string[])}
        style={{ marginTop: '16px' }}
      >
        {DTNO_DATA_STRUCTURE.map((category) => (
          <Panel
            key={category.id}
            header={
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Space>
                  <span style={{ color: category.color, fontSize: '18px' }}>
                    {category.icon}
                  </span>
                  <Text strong style={{ fontSize: '16px' }}>{category.name}</Text>
                  <Badge
                    count={`${getSelectedSubCategoryCount(category.id)}/${category.subCategories.length}`}
                    style={{
                      backgroundColor: getSelectedSubCategoryCount(category.id) > 0 ? category.color : '#d9d9d9'
                    }}
                  />
                </Space>
                <Checkbox
                  checked={isCategoryFullySelected(category.id)}
                  indeterminate={isCategoryPartiallySelected(category.id)}
                  onChange={(e) => {
                    e.stopPropagation();
                    handleCategoryChange(category.id, e.target.checked);
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  全選
                </Checkbox>
              </Space>
            }
          >
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '8px'
            }}>
              {category.subCategories.map((sub) => (
                <Card
                  key={sub.id}
                  size="small"
                  style={{
                    border: isSubCategorySelected(sub.id)
                      ? `2px solid ${category.color}`
                      : '1px solid #f0f0f0',
                    backgroundColor: isSubCategorySelected(sub.id) ? `${category.color}08` : '#fff',
                    cursor: 'pointer'
                  }}
                  onClick={() => handleSubCategoryChange(sub.id, !isSubCategorySelected(sub.id))}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Checkbox
                        checked={isSubCategorySelected(sub.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleSubCategoryChange(sub.id, e.target.checked);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <Tag color={category.color} style={{ margin: 0 }}>{sub.name}</Tag>
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        ({getColumnCount(sub)})
                      </Text>
                    </div>
                    <Tooltip
                      title={
                        <div>
                          <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>包含欄位：</div>
                          {sub.columns.map(col => (
                            <div key={col.id} style={{ fontSize: '12px' }}>• {col.name}</div>
                          ))}
                        </div>
                      }
                      placement="left"
                    >
                      <InfoCircleOutlined
                        style={{ color: '#999', cursor: 'pointer' }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Tooltip>
                  </div>
                </Card>
              ))}
            </div>
          </Panel>
        ))}
      </Collapse>

      {/* 新聞來源 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>新聞來源</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          選擇需要的新聞來源 (共{newsSources.length}個來源)
        </Text>
        <div style={{ marginTop: '8px' }}>
          <Space wrap>
            <Checkbox
              checked={value.news_sources?.length === newsSources.length}
              indeterminate={value.news_sources?.length > 0 && value.news_sources?.length < newsSources.length}
              onChange={(e) => handleSelectAllNewsSources(e.target.checked)}
            >
              <Tag color="red">全選</Tag>
            </Checkbox>
            {newsSources.map((source) => (
              <Checkbox
                key={source}
                checked={value.news_sources?.includes(source) || false}
                onChange={(e) => handleNewsSourceChange(source, e.target.checked)}
              >
                <Tag color="orange">{source}</Tag>
              </Checkbox>
            ))}
          </Space>
        </div>
      </Card>

      {/* 選擇摘要 */}
      <Card size="small" style={{ marginTop: '16px' }}>
        <Title level={5}>數據源摘要</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          {DTNO_DATA_STRUCTURE.map((category) => {
            const selectedSubs = category.subCategories.filter(sub => isSubCategorySelected(sub.id));
            if (selectedSubs.length === 0) return null;

            return (
              <div key={category.id}>
                <Text strong style={{ color: category.color }}>
                  {category.icon} {category.name}:
                </Text>
                <Space wrap style={{ marginLeft: '8px' }}>
                  {selectedSubs.map((sub) => (
                    <Tag key={sub.id} color={category.color}>{sub.name}</Tag>
                  ))}
                </Space>
              </div>
            );
          })}

          {value.news_sources && value.news_sources.length > 0 && (
            <div>
              <Text strong>新聞來源: </Text>
              <Text type="secondary">({value.news_sources.length} 個來源)</Text>
            </div>
          )}

          {(!value.subCategories || value.subCategories.length === 0) &&
           (!value.news_sources || value.news_sources.length === 0) && (
            <Text type="secondary">尚未選擇任何數據源</Text>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default DataSourceSelector;
