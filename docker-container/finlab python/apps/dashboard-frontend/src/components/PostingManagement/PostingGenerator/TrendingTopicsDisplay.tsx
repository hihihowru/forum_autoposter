import React, { useState } from 'react';
import { Card, Button, List, Tag, Space, Typography, message, Spin, Switch, Divider } from 'antd';
import { FireOutlined, StockOutlined } from '@ant-design/icons';
import { getApiBaseUrl } from '../../../config/api';


const API_BASE_URL = getApiBaseUrl();
const { Title, Text } = Typography;

interface TrendingTopic {
  id: string;
  title: string;
  content: string;
  stock_ids: string[];
  category: string;
  created_at: string;
  engagement_score: number;
}

interface StockInfo {
  code: string;
  name: string;
  industry?: string;
  source: 'manual' | 'trending';
}

interface TrendingTopicsDisplayProps {
  triggerConfig: any;
  onStockSelect: (stocks: StockInfo[]) => void;
  onTopicSelect: (topic: TrendingTopic) => void; // 新增：話題選擇回調
  onSelectedTopicsChange: (topics: TrendingTopic[]) => void; // 新增：選中話題變更回調
}

const TrendingTopicsDisplay: React.FC<TrendingTopicsDisplayProps> = ({
  triggerConfig,
  onStockSelect,
  onTopicSelect,
  onSelectedTopicsChange
}) => {
  const [topics, setTopics] = useState<TrendingTopic[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedStocks, setSelectedStocks] = useState<StockInfo[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]); // 選中的話題ID列表

  // 獲取股票名稱的函數
  const getStockName = async (stockCode: string): Promise<string> => {
    try {
      // 特殊處理 TWA00
      if (stockCode === 'TWA00') {
        return '台指期';
      }
      
      // 調用 OHLC API 獲取股票名稱
      const response = await fetch(`${API_BASE_URL}/get_stock_name?stock_id=${stockCode}`);
      if (response.ok) {
        const data = await response.json();
        return data.name || `股票${stockCode}`;
      }
    } catch (error) {
      console.warn(`獲取股票 ${stockCode} 名稱失敗:`, error);
    }
    
    // 備用硬編碼對應表
    const fallbackMapping: Record<string, string> = {
      "2330": "台積電",
      "2454": "聯發科", 
      "2317": "鴻海",
      "2881": "富邦金",
      "2882": "國泰金",
      "1101": "台泥",
      "1102": "亞泥",
      "1216": "統一",
      "1303": "南亞",
      "2002": "中鋼",
      "2308": "台達電",
      "2412": "中華電",
      "2603": "長榮",
      "2609": "陽明",
      "2615": "萬海",
      "2891": "中信金",
      "2886": "兆豐金",
      "2880": "華南金",
      "2884": "玉山金",
      "2885": "元大金",
      "TWA00": "台指期"
    };
    
    return fallbackMapping[stockCode] || `股票${stockCode}`;
  };


  // 獲取所有相關股票（去重）
  const getAllRelatedStocks = () => {
    const stockSet = new Set<string>();
    topics.forEach(topic => {
      topic.stock_ids.forEach(stockId => {
        stockSet.add(stockId);
      });
    });
    return Array.from(stockSet);
  };

  // 處理話題點擊（直接生成）
  const handleTopicClick = (topic: TrendingTopic) => {
    onTopicSelect(topic);
    message.success(`開始生成話題「${topic.title}」的貼文`);
  };

  // 處理話題選擇（添加到選擇列表）
  const handleTopicToggle = (topicId: string) => {
    const newSelectedTopics = selectedTopics.includes(topicId)
      ? selectedTopics.filter(id => id !== topicId)
      : [...selectedTopics, topicId];
    
    setSelectedTopics(newSelectedTopics);
    
    // 將選中的話題對象傳遞給父組件
    const selectedTopicObjects = topics.filter(topic => newSelectedTopics.includes(topic.id));
    onSelectedTopicsChange(selectedTopicObjects);
    
    const topic = topics.find(t => t.id === topicId);
    if (topic) {
      message.success(
        newSelectedTopics.includes(topicId) 
          ? `已選擇話題: ${topic.title}` 
          : `已取消選擇話題: ${topic.title}`
      );
    }
  };

  // 計算會生成的貼文數量（基於選中的話題）
  const calculatePostCount = () => {
    let totalPosts = 0;
    selectedTopics.forEach(topicId => {
      const topic = topics.find(t => t.id === topicId);
      if (topic) {
        if (topic.stock_ids && topic.stock_ids.length > 0) {
          // 有股票的話題：純話題 + 每個股票 = 1 + stock_ids.length
          totalPosts += 1 + topic.stock_ids.length;
        } else {
          // 純話題：只有1篇
          totalPosts += 1;
        }
      }
    });
    return totalPosts;
  };

  const totalPostCount = calculatePostCount();

  // 批量生成選中的話題
  const handleGenerateSelectedTopics = () => {
    if (selectedTopics.length === 0) {
      message.warning('請先選擇要生成的話題');
      return;
    }

    selectedTopics.forEach(topicId => {
      const topic = topics.find(t => t.id === topicId);
      if (topic) {
        onTopicSelect(topic);
      }
    });

    message.success(`開始生成 ${totalPostCount} 篇貼文`);
    setSelectedTopics([]); // 清空選擇
  };

  // 處理股票選擇
  const handleStockToggle = async (stockCode: string, isSelected: boolean) => {
    let newSelectedStocks: StockInfo[];
    
    if (isSelected) {
      const stockName = await getStockName(stockCode);
      const stockInfo: StockInfo = {
        code: stockCode,
        name: stockName,
        source: 'trending'
      };
      
      newSelectedStocks = [...selectedStocks, stockInfo];
      message.success(`已選擇: ${stockName}(${stockCode})`);
    } else {
      newSelectedStocks = selectedStocks.filter(s => s.code !== stockCode);
      const stockName = await getStockName(stockCode);
      message.info(`已取消選擇: ${stockName}(${stockCode})`);
    }
    
    setSelectedStocks(newSelectedStocks);
    onStockSelect(newSelectedStocks);
  };

  const fetchTrendingTopics = async () => {
    setLoading(true);
    try {
      // 呼叫現有的 trending-api (使用 Railway 後端)
      const response = await fetch(`${API_BASE_URL}/api/trending?limit=10`);
      const data = await response.json();
      
      if (data.topics) {
        setTopics(data.topics);
        message.success(`獲取到 ${data.topics.length} 個熱門話題`);
        
        // 打印每個話題的 topic_id
        console.log('🔥 獲取到的熱門話題列表:');
        data.topics.forEach((topic: TrendingTopic, index: number) => {
          console.log(`  ${index + 1}. Topic ID: ${topic.id}`);
          console.log(`     標題: ${topic.title}`);
          console.log(`     股票IDs: ${topic.stock_ids.join(', ') || '無'}`);
          console.log(`     類別: ${topic.category}`);
          console.log(`     熱度: ${(topic.engagement_score * 100).toFixed(0)}%`);
          console.log('     ---');
        });
      } else {
        message.warning('未獲取到熱門話題數據');
      }
    } catch (error) {
      console.error('獲取熱門話題失敗:', error);
      message.error('獲取熱門話題失敗，請檢查服務是否正常運行');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="熱門話題" size="small" style={{ marginTop: 16 }}>
      <Button 
        type="primary" 
        icon={<FireOutlined />}
        onClick={fetchTrendingTopics}
        loading={loading}
        style={{ marginBottom: 16 }}
      >
        獲取熱門話題
      </Button>
      
      {topics.length > 0 && (
        <div>
          {/* 選擇控制區域 */}
          <Card size="small" style={{ marginBottom: 16, backgroundColor: '#f0f8ff' }}>
            <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
              <Space>
                <Text strong>已選擇 {selectedTopics.length} 個話題</Text>
                {totalPostCount > 0 && (
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    💡 將生成 {totalPostCount} 篇貼文
                  </Text>
                )}
                {selectedTopics.length > 0 && (
                  <Button 
                    type="primary" 
                    size="small"
                    onClick={handleGenerateSelectedTopics}
                  >
                    批量生成選中話題
                  </Button>
                )}
              </Space>
              <Space>
                <Button
                  size="small"
                  type="primary"
                  onClick={() => {
                    const allTopicIds = topics.map(t => t.id);
                    setSelectedTopics(allTopicIds);
                    const selectedTopicObjects = topics;
                    onSelectedTopicsChange(selectedTopicObjects);
                    message.success(`已全選 ${topics.length} 個話題`);
                  }}
                  disabled={selectedTopics.length === topics.length}
                >
                  全選
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    setSelectedTopics([]);
                    onSelectedTopicsChange([]);
                  }}
                  disabled={selectedTopics.length === 0}
                >
                  清空選擇
                </Button>
              </Space>
            </Space>
          </Card>

          {/* 生成貼文詳情區域 */}
          {selectedTopics.length > 0 && (
            <Card
              title="📋 生成貼文詳情"
              size="small"
              style={{ marginBottom: 16, backgroundColor: '#fffbe6', borderColor: '#faad14' }}
            >
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <div>
                  <Text strong style={{ fontSize: '14px' }}>
                    總計將生成 {totalPostCount} 篇貼文
                  </Text>
                </div>

                <div>
                  <Text strong style={{ fontSize: '13px' }}>話題與股票組合:</Text>
                  <div style={{ marginTop: 8 }}>
                    {topics
                      .filter(topic => selectedTopics.includes(topic.id))
                      .map((topic, index) => {
                        const hasStocks = topic.stock_ids && topic.stock_ids.length > 0;
                        const postCount = hasStocks ? 1 + topic.stock_ids.length : 1;

                        return (
                          <Card
                            key={topic.id}
                            size="small"
                            style={{ marginBottom: 8, backgroundColor: '#fff' }}
                          >
                            <Space direction="vertical" style={{ width: '100%' }} size="small">
                              <div>
                                <Tag color="blue">話題 {index + 1}</Tag>
                                <Text strong>{topic.title}</Text>
                              </div>

                              {hasStocks ? (
                                <div>
                                  <Text type="secondary" style={{ fontSize: '12px' }}>
                                    📊 將生成 {postCount} 篇貼文:
                                  </Text>
                                  <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '12px' }}>
                                    <li>
                                      <Tag color="orange">純話題</Tag>
                                      {topic.title} (使用 serper 搜尋生成)
                                    </li>
                                    {topic.stock_ids.map(stockId => (
                                      <li key={stockId}>
                                        <Tag color="green">股票標籤</Tag>
                                        {topic.title} + {stockId === 'TWA00' ? '台指期' : stockId}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              ) : (
                                <div>
                                  <Text type="secondary" style={{ fontSize: '12px' }}>
                                    📊 將生成 {postCount} 篇貼文:
                                  </Text>
                                  <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '12px' }}>
                                    <li>
                                      <Tag color="orange">純話題</Tag>
                                      {topic.title} (無股票標籤，使用 serper 搜尋生成)
                                    </li>
                                  </ul>
                                </div>
                              )}
                            </Space>
                          </Card>
                        );
                      })}
                  </div>
                </div>

                <div style={{ paddingTop: 8, borderTop: '1px solid #d9d9d9' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    💡 提示: 點擊「批量生成選中話題」後，系統將按照上述組合生成 {totalPostCount} 篇貼文
                  </Text>
                </div>
              </Space>
            </Card>
          )}

          {/* 話題列表 - 可選擇 */}
          <Title level={5}>熱門話題列表</Title>
          <Text type="secondary" style={{ fontSize: '12px', marginBottom: '16px', display: 'block' }}>
            💡 點擊話題卡片選擇/取消選擇，選中後點擊「批量生成選中話題」
          </Text>
          <List
            size="small"
            dataSource={topics}
            renderItem={(topic) => {
              const hasStocks = topic.stock_ids.length > 0;
              const isSelected = selectedTopics.includes(topic.id);
              
              return (
                <List.Item>
                  <Card 
                    size="small" 
                    style={{ 
                      width: '100%',
                      backgroundColor: isSelected ? '#e6f7ff' : '#fafafa',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      border: isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9'
                    }}
                    hoverable
                    onClick={() => handleTopicToggle(topic.id)}
                  >
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div>
                        <Text strong>{topic.title}</Text>
                        {!hasStocks && <Tag color="orange">純話題</Tag>}
                        {isSelected && <Tag color="green">✅ 已選擇</Tag>}
                        {isSelected && (
                          <Tag color="cyan" style={{ marginLeft: 8 }}>
                            📊 生成 {hasStocks ? 1 + topic.stock_ids.length : 1} 篇貼文
                          </Tag>
                        )}
                      </div>
                      
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {topic.content.length > 100 ? `${topic.content.substring(0, 100)}...` : topic.content}
                      </Text>
                      
                      {hasStocks ? (
                        <div>
                          <Text strong style={{ fontSize: '12px' }}>相關股票: </Text>
                          {topic.stock_ids.map(stockId => (
                            <Tag 
                              key={stockId} 
                              color="green" 
                              style={{ fontSize: '11px', margin: '2px' }}
                            >
                              {stockId === 'TWA00' ? '台指期' : stockId}
                            </Tag>
                          ))}
                        </div>
                      ) : (
                        <div>
                          <Text type="secondary" style={{ fontSize: '11px' }}>
                            📰 此話題無股票標籤，將使用新聞搜尋 Agent 分析並生成內容
                          </Text>
                        </div>
                      )}
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text type="secondary" style={{ fontSize: '11px' }}>
                          {new Date(topic.created_at).toLocaleString('zh-TW')}
                        </Text>
                        <Button 
                          size="small" 
                          type={isSelected ? "default" : "primary"}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTopicToggle(topic.id);
                          }}
                        >
                          {isSelected ? '取消選擇' : '選擇'}
                        </Button>
                      </div>
                    </Space>
                  </Card>
                </List.Item>
              );
            }}
          />

          <Divider />

          {/* 股票選擇區域 */}
          <Card title="選擇相關股票" size="small">
            <Text type="secondary" style={{ fontSize: '12px', marginBottom: '16px', display: 'block' }}>
              💡 選擇股票後，系統會自動匹配相關的熱門話題並標記
            </Text>
            <Space wrap>
              {getAllRelatedStocks().map(stockCode => {
                const isSelected = selectedStocks.some(s => s.code === stockCode);
                const displayName = stockCode === 'TWA00' ? '台指期' : stockCode;
                
                return (
                  <Tag
                    key={stockCode}
                    color={isSelected ? "blue" : "default"}
                    style={{ 
                      cursor: 'pointer',
                      padding: '4px 8px',
                      fontSize: '12px'
                    }}
                    onClick={() => handleStockToggle(stockCode, !isSelected)}
                  >
                    <Space size="small">
                      <StockOutlined />
                      <span>{displayName}</span>
                      {isSelected && <span>✓</span>}
                    </Space>
                  </Tag>
                );
              })}
            </Space>
            
            {selectedStocks.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Text strong>已選擇的股票: </Text>
                <Space wrap>
                  {selectedStocks.map(stock => (
                    <Tag 
                      key={stock.code} 
                      color="blue" 
                      closable
                      onClose={() => handleStockToggle(stock.code, false)}
                    >
                      <Space size="small">
                        <StockOutlined />
                        <span>{stock.name}</span>
                        <span>({stock.code})</span>
                      </Space>
                    </Tag>
                  ))}
                </Space>
              </div>
            )}
          </Card>
        </div>
      )}
    </Card>
  );
};

export default TrendingTopicsDisplay;