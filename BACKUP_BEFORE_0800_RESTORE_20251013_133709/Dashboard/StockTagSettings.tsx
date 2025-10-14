/**
 * 簡化的股票標籤設定組件
 * 基於已知的貼文-熱門話題對應關係
 */

import React, { useState, useEffect } from 'react';
import { Card, Radio, Button, Tag, Space, Divider, Typography } from 'antd';
import { StockOutlined, FireOutlined, SettingOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface StockTag {
  code: string;
  name: string;
  type: 'trending' | 'manual' | 'mixed';
}

interface StockTagSettingsProps {
  topicTitle: string;
  topicId: string;
  onTagsChange: (tags: StockTag[]) => void;
}

const StockTagSettings: React.FC<StockTagSettingsProps> = ({
  topicTitle,
  topicId,
  onTagsChange
}) => {
  const [mode, setMode] = useState<'trending' | 'manual' | 'mixed'>('trending');
  const [trendingStocks, setTrendingStocks] = useState<StockTag[]>([]);
  const [manualStocks, setManualStocks] = useState<StockTag[]>([]);
  const [selectedManualStocks, setSelectedManualStocks] = useState<string[]>([]);

  // 常用股票列表
  const commonStocks = [
    { code: '2330', name: '台積電' },
    { code: '2317', name: '鴻海' },
    { code: '2454', name: '聯發科' },
    { code: '2308', name: '台達電' },
    { code: '2412', name: '中華電' },
    { code: '2882', name: '國泰金' },
    { code: '2881', name: '富邦金' },
    { code: '2603', name: '長榮' },
    { code: '2609', name: '陽明' },
    { code: '2002', name: '中鋼' }
  ];

  // 根據話題標題自動提取股票
  useEffect(() => {
    const extractStocksFromTopic = (title: string): StockTag[] => {
      const stocks: StockTag[] = [];
      
      // 台積電相關
      if (title.includes('台積電') || title.includes('TSMC') || title.includes('2330')) {
        stocks.push({ code: '2330', name: '台積電', type: 'trending' });
      }
      
      // 鴻海相關
      if (title.includes('鴻海') || title.includes('2317')) {
        stocks.push({ code: '2317', name: '鴻海', type: 'trending' });
      }
      
      // 聯發科相關
      if (title.includes('聯發科') || title.includes('2454')) {
        stocks.push({ code: '2454', name: '聯發科', type: 'trending' });
      }
      
      // 大盤相關
      if (title.includes('台股') || title.includes('大盤') || title.includes('指數')) {
        stocks.push({ code: '2330', name: '台積電', type: 'trending' });
        stocks.push({ code: '2317', name: '鴻海', type: 'trending' });
        stocks.push({ code: '2454', name: '聯發科', type: 'trending' });
      }
      
      // 航運相關
      if (title.includes('航運') || title.includes('長榮') || title.includes('陽明')) {
        stocks.push({ code: '2603', name: '長榮', type: 'trending' });
        stocks.push({ code: '2609', name: '陽明', type: 'trending' });
      }
      
      // 金融相關
      if (title.includes('金融') || title.includes('金控')) {
        stocks.push({ code: '2882', name: '國泰金', type: 'trending' });
        stocks.push({ code: '2881', name: '富邦金', type: 'trending' });
      }
      
      return stocks;
    };

    const extractedStocks = extractStocksFromTopic(topicTitle);
    setTrendingStocks(extractedStocks);
  }, [topicTitle]);

  // 更新標籤
  useEffect(() => {
    let finalTags: StockTag[] = [];
    
    switch (mode) {
      case 'trending':
        finalTags = trendingStocks;
        break;
      case 'manual':
        finalTags = commonStocks
          .filter(stock => selectedManualStocks.includes(stock.code))
          .map(stock => ({ ...stock, type: 'manual' }));
        break;
      case 'mixed':
        const manualTags = commonStocks
          .filter(stock => selectedManualStocks.includes(stock.code))
          .map(stock => ({ ...stock, type: 'manual' }));
        finalTags = [...trendingStocks, ...manualTags];
        break;
    }
    
    onTagsChange(finalTags);
  }, [mode, trendingStocks, selectedManualStocks, onTagsChange]);

  const handleManualStockToggle = (stockCode: string) => {
    setSelectedManualStocks(prev => 
      prev.includes(stockCode) 
        ? prev.filter(code => code !== stockCode)
        : [...prev, stockCode]
    );
  };

  return (
    <Card 
      title={
        <Space>
          <StockOutlined />
          <span>股票標籤設定</span>
        </Space>
      }
      size="small"
    >
      {/* 話題信息 */}
      <div style={{ marginBottom: 16 }}>
        <Text strong>話題標題：</Text>
        <Text>{topicTitle}</Text>
        <br />
        <Text type="secondary">話題ID：{topicId}</Text>
      </div>

      <Divider />

      {/* 模式選擇 */}
      <div style={{ marginBottom: 16 }}>
        <Title level={5}>選擇標籤模式</Title>
        <Radio.Group 
          value={mode} 
          onChange={(e) => setMode(e.target.value)}
          buttonStyle="solid"
        >
          <Radio.Button value="trending">
            <FireOutlined /> 熱門話題
          </Radio.Button>
          <Radio.Button value="manual">
            <StockOutlined /> 股標
          </Radio.Button>
          <Radio.Button value="mixed">
            <SettingOutlined /> 混合模式
          </Radio.Button>
        </Radio.Group>
      </div>

      {/* 熱門話題模式 */}
      {mode === 'trending' && (
        <div>
          <Title level={5}>自動提取的股票標籤</Title>
          <Space wrap>
            {trendingStocks.length > 0 ? (
              trendingStocks.map(stock => (
                <Tag key={stock.code} color="red" icon={<FireOutlined />}>
                  {stock.name} ({stock.code})
                </Tag>
              ))
            ) : (
              <Text type="secondary">未檢測到相關股票</Text>
            )}
          </Space>
        </div>
      )}

      {/* 手動選擇模式 */}
      {(mode === 'manual' || mode === 'mixed') && (
        <div>
          <Title level={5}>手動選擇股票</Title>
          <Space wrap>
            {commonStocks.map(stock => (
              <Button
                key={stock.code}
                type={selectedManualStocks.includes(stock.code) ? 'primary' : 'default'}
                size="small"
                onClick={() => handleManualStockToggle(stock.code)}
              >
                {stock.name} ({stock.code})
              </Button>
            ))}
          </Space>
        </div>
      )}

      {/* 混合模式預覽 */}
      {mode === 'mixed' && (
        <div style={{ marginTop: 16 }}>
          <Title level={5}>最終標籤組合</Title>
          <Space wrap>
            {trendingStocks.map(stock => (
              <Tag key={`trending-${stock.code}`} color="red" icon={<FireOutlined />}>
                {stock.name} ({stock.code})
              </Tag>
            ))}
            {commonStocks
              .filter(stock => selectedManualStocks.includes(stock.code))
              .map(stock => (
                <Tag key={`manual-${stock.code}`} color="blue" icon={<StockOutlined />}>
                  {stock.name} ({stock.code})
                </Tag>
              ))
            }
          </Space>
        </div>
      )}
    </Card>
  );
};

export default StockTagSettings;
