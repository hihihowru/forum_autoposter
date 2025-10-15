/**
 * 簡化的股票標籤設定組件
 * 基於已知的貼文-熱門話題對應關係
 */

import React, { useState, useEffect, useCallback } from 'react';
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
  const [selectedManualStocks, setSelectedManualStocks] = useState<string[]>([]);

  // 常用股票列表
  const commonStocks: StockTag[] = [
    { code: '2330', name: '台積電', type: 'manual' },
    { code: '2317', name: '鴻海', type: 'manual' },
    { code: '2454', name: '聯發科', type: 'manual' },
    { code: '2308', name: '台達電', type: 'manual' },
    { code: '2412', name: '中華電', type: 'manual' },
    { code: '2882', name: '國泰金', type: 'manual' },
    { code: '2881', name: '富邦金', type: 'manual' },
    { code: '2603', name: '長榮', type: 'manual' },
    { code: '2609', name: '陽明', type: 'manual' },
    { code: '2002', name: '中鋼', type: 'manual' }
  ];

  // 根據話題標題自動提取股票
  const extractStocksFromTopic = useCallback((title: string): StockTag[] => {
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
      if (!stocks.some(s => s.code === '2330')) {
        stocks.push({ code: '2330', name: '台積電', type: 'trending' });
      }
      if (!stocks.some(s => s.code === '2317')) {
        stocks.push({ code: '2317', name: '鴻海', type: 'trending' });
      }
      if (!stocks.some(s => s.code === '2454')) {
        stocks.push({ code: '2454', name: '聯發科', type: 'trending' });
      }
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
  }, []);

  // 更新趨勢股票
  useEffect(() => {
    const extractedStocks = extractStocksFromTopic(topicTitle);
    setTrendingStocks(extractedStocks);
  }, [topicTitle, extractStocksFromTopic]);

  // 更新標籤
  useEffect(() => {
    let finalTags: StockTag[] = [];
    
    switch (mode) {
      case 'trending':
        finalTags = [...trendingStocks];
        break;
      case 'manual':
        finalTags = commonStocks
          .filter(stock => selectedManualStocks.includes(stock.code))
          .map(stock => ({ ...stock, type: 'manual' as const }));
        break;
      case 'mixed':
        const manualTags = commonStocks
          .filter(stock => selectedManualStocks.includes(stock.code))
          .map(stock => ({ ...stock, type: 'manual' as const }));
        finalTags = [...trendingStocks, ...manualTags];
        break;
    }
    
    onTagsChange(finalTags);
  }, [mode, trendingStocks, selectedManualStocks, onTagsChange, commonStocks]);

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
      extra={
        <Radio.Group 
          value={mode} 
          onChange={e => setMode(e.target.value as 'trending' | 'manual' | 'mixed')}
          buttonStyle="solid"
        >
          <Radio.Button value="trending">
            <FireOutlined /> 熱門標籤
          </Radio.Button>
          <Radio.Button value="manual">
            <SettingOutlined /> 手動選擇
          </Radio.Button>
          <Radio.Button value="mixed">
            <FireOutlined /> + <SettingOutlined /> 混合模式
          </Radio.Button>
        </Radio.Group>
      }
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">當前話題: </Text>
        <Text strong>{topicTitle}</Text>
      </div>

      {mode === 'trending' && (
        <div>
          <Text>根據話題自動識別的熱門股票標籤:</Text>
          <div style={{ marginTop: 8 }}>
            {trendingStocks.length > 0 ? (
              <Space wrap>
                {trendingStocks.map(stock => (
                  <Tag 
                    key={stock.code} 
                    color="blue"
                    style={{ padding: '4px 8px' }}
                  >
                    {stock.name} ({stock.code})
                  </Tag>
                ))}
              </Space>
            ) : (
              <Text type="secondary">未識別到相關股票</Text>
            )}
          </div>
        </div>
      )}

      {(mode === 'manual' || mode === 'mixed') && (
        <div style={{ marginTop: mode === 'manual' ? 0 : 16 }}>
          <Text>手動選擇股票標籤:</Text>
          <div style={{ marginTop: 8 }}>
            <Space wrap>
              {commonStocks.map(stock => (
                <Button
                  key={stock.code}
                  type={selectedManualStocks.includes(stock.code) ? 'primary' : 'default'}
                  size="small"
                  onClick={() => handleManualStockToggle(stock.code)}
                  style={{ marginBottom: 8 }}
                >
                  {stock.name} ({stock.code})
                </Button>
              ))}
            </Space>
          </div>
        </div>
      )}

      {mode === 'mixed' && (
        <div style={{ marginTop: 16 }}>
          <Text>合併後的標籤預覽:</Text>
          <div style={{ 
            marginTop: 8, 
            padding: '8px', 
            border: '1px dashed #d9d9d9',
            borderRadius: '4px',
            minHeight: '40px'
          }}>
            {trendingStocks.length > 0 || selectedManualStocks.length > 0 ? (
              <Space wrap>
                {trendingStocks.map(stock => (
                  <Tag 
                    key={`trending-${stock.code}`} 
                    color="blue"
                    style={{ marginBottom: '4px' }}
                  >
                    {stock.name} ({stock.code})
                  </Tag>
                ))}
                {selectedManualStocks.map(code => {
                  const stock = commonStocks.find(s => s.code === code);
                  return stock ? (
                    <Tag 
                      key={`manual-${stock.code}`} 
                      color="green"
                      style={{ marginBottom: '4px' }}
                    >
                      {stock.name} ({stock.code})
                    </Tag>
                  ) : null;
                })}
              </Space>
            ) : (
              <Text type="secondary">請選擇標籤或添加熱門標籤</Text>
            )}
          </div>
        </div>
      )}
    </Card>
  );
};

export default StockTagSettings;
