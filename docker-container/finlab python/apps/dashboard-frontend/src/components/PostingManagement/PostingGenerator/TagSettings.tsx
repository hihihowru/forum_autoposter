import React, { useState, useEffect } from 'react';
import { Card, Typography, Radio, Space, Tag, Button, Input, Divider, Row, Col, Select, Spin, message, Switch } from 'antd';
import { TagsOutlined, PlusOutlined, DeleteOutlined, StockOutlined, FireOutlined } from '@ant-design/icons';
import { getApiBaseUrl } from '../../../config/api';

const API_BASE_URL = getApiBaseUrl();
const { Title, Text } = Typography;
const { Option } = Select;

interface TrendingTopic {
  id: string;
  title: string;
  content: string;
  stock_ids: string[];
  category: string;
  engagement_score: number;
}

interface TagConfig {
  tag_mode: 'stock_tags' | 'topic_tags' | 'both';
  stock_tags: {
    enabled: boolean;
    auto_generate: boolean;
    custom_tags: string[];
    include_stock_code: boolean;
    include_stock_name: boolean;
    batch_shared_tags: boolean; // 新增：全貼同群股標
  };
  topic_tags: {
    enabled: boolean;
    auto_generate: boolean;
    custom_tags: string[];
    trending_topics: string[];
    selected_trending_topic?: TrendingTopic; // 新增：選中的熱門話題
    mixed_mode: boolean; // 新增：混和模式，自動使用 trending API 的 topic ID
  };
  max_tags_per_post: number;
}

interface TagSettingsProps {
  value: TagConfig;
  onChange: (value: TagConfig) => void;
  triggerData?: {
    stock_codes?: string[];
    stock_names?: string[];
  };
  kolData?: {
    kol_serials?: string[];
    kol_names?: string[];
  };
}

const TagSettings: React.FC<TagSettingsProps> = ({ value, onChange, triggerData, kolData }) => {
  const [newStockTag, setNewStockTag] = useState('');
  const [newTopicTag, setNewTopicTag] = useState('');
  const [trendingTopics, setTrendingTopics] = useState<TrendingTopic[]>([]);
  const [loadingTrendingTopics, setLoadingTrendingTopics] = useState(false);

  // 模擬熱門話題數據（備用）
  const mockTrendingTopics = [
    'AI概念股', '電動車', '半導體', '生技醫療', '綠能', '元宇宙',
    '5G', '區塊鏈', '金融科技', 'ESG', '通膨概念', '升息概念'
  ];

  // 獲取熱門話題
  const fetchTrendingTopics = async () => {
    setLoadingTrendingTopics(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/trending?limit=10`);
      const data = await response.json();
      
      if (data.topics) {
        setTrendingTopics(data.topics);
        message.success(`獲取到 ${data.topics.length} 個熱門話題`);
      } else {
        message.warning('未獲取到熱門話題數據');
      }
    } catch (error) {
      console.error('獲取熱門話題失敗:', error);
      message.error('獲取熱門話題失敗，請檢查服務是否正常運行');
    } finally {
      setLoadingTrendingTopics(false);
    }
  };

  // 組件載入時自動獲取熱門話題
  useEffect(() => {
    fetchTrendingTopics();
  }, []);

  const handleTagModeChange = (mode: 'stock_tags' | 'topic_tags' | 'both') => {
    onChange({
      ...value,
      tag_mode: mode,
      stock_tags: {
        ...value.stock_tags,
        enabled: mode === 'stock_tags' || mode === 'both'
      },
      topic_tags: {
        ...value.topic_tags,
        enabled: mode === 'topic_tags' || mode === 'both'
      }
    });
  };

  const handleStockTagToggle = (enabled: boolean) => {
    onChange({
      ...value,
      stock_tags: {
        ...value.stock_tags,
        enabled
      }
    });
  };

  const handleTopicTagToggle = (enabled: boolean) => {
    onChange({
      ...value,
      topic_tags: {
        ...value.topic_tags,
        enabled
      }
    });
  };

  const handleAddStockTag = () => {
    if (newStockTag.trim() && !value.stock_tags.custom_tags.includes(newStockTag.trim())) {
      onChange({
        ...value,
        stock_tags: {
          ...value.stock_tags,
          custom_tags: [...value.stock_tags.custom_tags, newStockTag.trim()]
        }
      });
      setNewStockTag('');
    }
  };

  const handleAddTopicTag = () => {
    if (newTopicTag.trim() && !value.topic_tags.custom_tags.includes(newTopicTag.trim())) {
      onChange({
        ...value,
        topic_tags: {
          ...value.topic_tags,
          custom_tags: [...value.topic_tags.custom_tags, newTopicTag.trim()]
        }
      });
      setNewTopicTag('');
    }
  };

  const handleRemoveStockTag = (tag: string) => {
    onChange({
      ...value,
      stock_tags: {
        ...value.stock_tags,
        custom_tags: value.stock_tags.custom_tags.filter(t => t !== tag)
      }
    });
  };

  const handleRemoveTopicTag = (tag: string) => {
    onChange({
      ...value,
      topic_tags: {
        ...value.topic_tags,
        custom_tags: value.topic_tags.custom_tags.filter(t => t !== tag)
      }
    });
  };

  const handleToggleTrendingTopic = (topic: string) => {
    const currentTopics = value.topic_tags.trending_topics;
    const newTopics = currentTopics.includes(topic)
      ? currentTopics.filter(t => t !== topic)
      : [...currentTopics, topic];

    onChange({
      ...value,
      topic_tags: {
        ...value.topic_tags,
        trending_topics: newTopics
      }
    });
  };

  // 處理熱門話題選擇（只能選一個）
  const handleSelectTrendingTopic = (topic: TrendingTopic) => {
    onChange({
      ...value,
      topic_tags: {
        ...value.topic_tags,
        selected_trending_topic: topic,
        trending_topics: [topic.title] // 只保留選中的話題
      }
    });
    message.success(`已選擇熱門話題: ${topic.title}`);
  };

  // 清除熱門話題選擇
  const handleClearTrendingTopic = () => {
    onChange({
      ...value,
      topic_tags: {
        ...value.topic_tags,
        selected_trending_topic: undefined,
        trending_topics: []
      }
    });
    message.info('已清除熱門話題選擇');
  };

  const handleMaxTagsChange = (maxTags: number) => {
    onChange({
      ...value,
      max_tags_per_post: maxTags
    });
  };

  const handleStockTagSettingChange = (key: keyof TagConfig['stock_tags'], newValue: any) => {
    onChange({
      ...value,
      stock_tags: {
        ...value.stock_tags,
        [key]: newValue
      }
    });
  };

  const handleTopicTagSettingChange = (key: keyof TagConfig['topic_tags'], newValue: any) => {
    onChange({
      ...value,
      topic_tags: {
        ...value.topic_tags,
        [key]: newValue
      }
    });
  };

  // 生成 body parameter 預覽
  const generateBodyParameterPreview = () => {
    if (!triggerData?.stock_codes?.length || !kolData?.kol_serials?.length) {
      return [];
    }

    const previews = [];
    
    // 為每個 KOL 生成預覽
    kolData.kol_serials.forEach((kolSerial, index) => {
      const kolName = kolData.kol_names?.[index] || `KOL-${kolSerial}`;
      
      // 生成 commodityTags
      const commodityTags = [];
      
      // 添加股票標籤
      if (value.stock_tags.enabled) {
        if (value.stock_tags.batch_shared_tags) {
          // 全貼同群股標：所有貼文都貼上相同的股票標籤（所有觸發器分配的股票）
          triggerData.stock_codes.forEach(stockCode => {
            commodityTags.push({
              type: "Stock",
              key: stockCode,
              bullOrBear: 0  // 預設中性
            });
          });
        } else {
          // 原本的邏輯：每個貼文只貼對應的股票標籤
          // 這裡假設每個 KOL 對應一個股票（實際邏輯可能需要根據具體需求調整）
          const stockIndex = index % triggerData.stock_codes.length;
          const stockCode = triggerData.stock_codes[stockIndex];
          commodityTags.push({
            type: "Stock",
            key: stockCode,
            bullOrBear: 0
          });
        }
      }
      
      // 添加熱門話題標籤（整合到 commodity tags 中）
      if (value.topic_tags.enabled && value.topic_tags.selected_trending_topic) {
        const selectedTopic = value.topic_tags.selected_trending_topic;
        
        // 添加熱門話題標籤
        commodityTags.push({
          type: "Topic",
          key: selectedTopic.id,
          bullOrBear: 0,
          topicTitle: selectedTopic.title,
          topicContent: selectedTopic.content,
          topicCategory: selectedTopic.category,
          topicEngagement: selectedTopic.engagement_score
        });
        
        // 如果有相關股票標籤，也一起添加
        if (selectedTopic.stock_ids && selectedTopic.stock_ids.length > 0) {
          selectedTopic.stock_ids.forEach(stockId => {
            commodityTags.push({
              type: "Stock",
              key: stockId,
              bullOrBear: 0,
              relatedTopic: selectedTopic.id
            });
          });
        }
      }
      
      // 添加其他話題標籤
      if (value.topic_tags.enabled && value.topic_tags.trending_topics.length > 0) {
        value.topic_tags.trending_topics.slice(0, 2).forEach(topic => {
          commodityTags.push({
            type: "Topic",
            key: topic,
            bullOrBear: 0
          });
        });
      }
      
      // 限制標籤數量
      const limitedTags = commodityTags.slice(0, value.max_tags_per_post);
      
      previews.push({
        kol_serial: kolSerial,
        kol_name: kolName,
        commodityTags: limitedTags,
        tagCount: limitedTags.length,
        isSharedTags: value.stock_tags.batch_shared_tags
      });
    });
    
    return previews;
  };

  return (
    <Card title="標籤設定" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Text type="secondary">
          設定貼文標籤類型，系統會根據設定自動生成或使用自定義標籤
        </Text>

        {/* 觸發器股票顯示 */}
        {triggerData && (triggerData.stock_codes?.length || triggerData.stock_names?.length) && (
          <Card size="small" style={{ background: '#f6ffed', border: '1px solid #b7eb8f' }}>
            <Text strong style={{ color: '#52c41a' }}>
              <StockOutlined /> 觸發器分配的股票：
            </Text>
            <div style={{ marginTop: '8px' }}>
              {/* 只顯示股票代號，避免重複 */}
              {triggerData.stock_codes?.map((code, index) => (
                <Tag key={`code-${index}`} color="green" style={{ margin: '2px' }}>
                  {code}
                </Tag>
              ))}
            </div>
          </Card>
        )}

        {/* 標籤模式選擇 */}
        <div>
          <Title level={5}>標籤模式</Title>
          <Radio.Group
            value={value.tag_mode}
            onChange={(e) => handleTagModeChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="stock_tags" style={{ width: '100%' }}>
                <Space>
                  <StockOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>股票標籤</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      使用股票相關標籤 (股票代號、股票名稱等)
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="topic_tags" style={{ width: '100%' }}>
                <Space>
                  <FireOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>熱門話題標籤</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      使用熱門話題和產業標籤
                    </Text>
                  </Space>
                </Space>
              </Radio>
              <Radio value="both" style={{ width: '100%' }}>
                <Space>
                  <TagsOutlined />
                  <Space direction="vertical" size={0}>
                    <Text strong>混合模式</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      同時使用股票標籤和熱門話題標籤
                    </Text>
                  </Space>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        <Divider />

        {/* 股票標籤設定 */}
        {(value.tag_mode === 'stock_tags' || value.tag_mode === 'both') && (
          <div>
            <Title level={5}>股票標籤設定</Title>
            
            <Card size="small" style={{ backgroundColor: '#e6f7ff', border: '1px solid #91d5ff' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {/* 自動生成設定 */}
                <div>
                  <Space>
                    <Switch
                      checked={value.stock_tags.auto_generate}
                      onChange={(checked) => handleStockTagSettingChange('auto_generate', checked)}
                    />
                    <Text strong>自動生成股票標籤</Text>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                    系統會根據股票資訊自動生成相關標籤
                  </Text>
                </div>

                {/* 包含股票代號 */}
                <div>
                  <Space>
                    <Switch
                      checked={value.stock_tags.include_stock_code}
                      onChange={(checked) => handleStockTagSettingChange('include_stock_code', checked)}
                    />
                    <Text>包含股票代號</Text>
                    <Tag color="blue">#2330</Tag>
                  </Space>
                </div>

                {/* 包含股票名稱 */}
                <div>
                  <Space>
                    <Switch
                      checked={value.stock_tags.include_stock_name}
                      onChange={(checked) => handleStockTagSettingChange('include_stock_name', checked)}
                    />
                    <Text>包含股票名稱</Text>
                    <Tag color="green">#台積電</Tag>
                  </Space>
                </div>

                {/* 全貼同群股標 */}
                <div>
                  <Space>
                    <Switch
                      checked={value.stock_tags.batch_shared_tags}
                      onChange={(checked) => handleStockTagSettingChange('batch_shared_tags', checked)}
                    />
                    <Text strong>全貼同群股標</Text>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                    同一個 batch 的所有貼文都會貼上相同的股票標籤（包含所有觸發器分配的股票）
                  </Text>
                </div>
              </Space>
            </Card>

            {/* 自定義股票標籤 */}
            <div style={{ marginTop: '12px' }}>
              <Text strong>自定義股票標籤</Text>
              <div style={{ marginTop: '8px' }}>
                <Space.Compact style={{ width: '100%' }}>
                  <Input
                    placeholder="輸入自定義股票標籤..."
                    value={newStockTag}
                    onChange={(e) => setNewStockTag(e.target.value)}
                    onPressEnter={handleAddStockTag}
                    style={{ flex: 1 }}
                  />
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAddStockTag}
                    disabled={!newStockTag.trim()}
                  >
                    添加
                  </Button>
                </Space.Compact>
              </div>
              
              {value.stock_tags.custom_tags.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <Space wrap>
                    {value.stock_tags.custom_tags.map((tag) => (
                      <Tag
                        key={tag}
                        closable
                        onClose={() => handleRemoveStockTag(tag)}
                        color="blue"
                      >
                        #{tag}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 熱門話題標籤設定 */}
        {(value.tag_mode === 'topic_tags' || value.tag_mode === 'both') && (
          <div>
            <Title level={5}>熱門話題標籤設定</Title>
            
            <Card size="small" style={{ backgroundColor: '#fff7e6', border: '1px solid #ffd591' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {/* 混和模式開關 */}
                <div>
                  <Space>
                    <Switch
                      checked={value.topic_tags.mixed_mode}
                      onChange={(checked) => handleTopicTagSettingChange('mixed_mode', checked)}
                    />
                    <Text strong>混和模式</Text>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                    啟用後，系統會自動使用 trending API 獲取到的 topic ID 來標記貼文，無需手動選擇
                  </Text>
                </div>

                {/* 自動生成設定 */}
                <div>
                  <Space>
                    <Switch
                      checked={value.topic_tags.auto_generate}
                      onChange={(checked) => handleTopicTagSettingChange('auto_generate', checked)}
                    />
                    <Text strong>自動生成話題標籤</Text>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                    系統會根據內容主題自動生成相關話題標籤
                  </Text>
                </div>
              </Space>
            </Card>

            {/* 熱門話題選擇 - 只在非混和模式下顯示 */}
            {!value.topic_tags.mixed_mode && (
              <div style={{ marginTop: '12px' }}>
                <Text strong>選擇熱門話題</Text>
                <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                  選擇要包含的熱門話題標籤（只能選擇一個）
                </Text>
              <div style={{ marginTop: '8px' }}>
                <Button 
                  icon={<FireOutlined />}
                  onClick={fetchTrendingTopics}
                  loading={loadingTrendingTopics}
                  size="small"
                  style={{ marginBottom: 8 }}
                >
                  重新獲取熱門話題
                </Button>
                
                {value.topic_tags.selected_trending_topic && (
                  <div style={{ marginBottom: 8 }}>
                    <Tag 
                      color="red" 
                      closable 
                      onClose={handleClearTrendingTopic}
                      style={{ fontSize: '12px' }}
                    >
                      <FireOutlined /> {value.topic_tags.selected_trending_topic.title}
                    </Tag>
                    <Text type="secondary" style={{ fontSize: '11px', marginLeft: 8 }}>
                      熱度: {(value.topic_tags.selected_trending_topic.engagement_score * 100).toFixed(0)}%
                    </Text>
                    {value.topic_tags.selected_trending_topic.stock_ids.length > 0 && (
                      <Text type="secondary" style={{ fontSize: '11px', marginLeft: 8 }}>
                        相關股票: {value.topic_tags.selected_trending_topic.stock_ids.join(', ')}
                      </Text>
                    )}
                  </div>
                )}
                
                <Spin spinning={loadingTrendingTopics}>
                  <Space wrap>
                    {trendingTopics.map((topic) => (
                      <Tag.CheckableTag
                        key={topic.id}
                        checked={value.topic_tags.selected_trending_topic?.id === topic.id}
                        onChange={() => handleSelectTrendingTopic(topic)}
                        style={{ 
                          fontSize: '11px',
                          marginBottom: '4px',
                          maxWidth: '200px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                      >
                        <FireOutlined /> {topic.title}
                        {topic.stock_ids.length > 0 && (
                          <Text type="secondary" style={{ fontSize: '10px' }}>
                            ({topic.stock_ids.length}股)
                          </Text>
                        )}
                      </Tag.CheckableTag>
                    ))}
                  </Space>
                </Spin>
                
                {trendingTopics.length === 0 && !loadingTrendingTopics && (
                  <Text type="secondary">暫無熱門話題數據</Text>
                )}
              </div>
            </div>
            )}

            {/* 自定義話題標籤 */}
            <div style={{ marginTop: '12px' }}>
              <Text strong>自定義話題標籤</Text>
              <div style={{ marginTop: '8px' }}>
                <Space.Compact style={{ width: '100%' }}>
                  <Input
                    placeholder="輸入自定義話題標籤..."
                    value={newTopicTag}
                    onChange={(e) => setNewTopicTag(e.target.value)}
                    onPressEnter={handleAddTopicTag}
                    style={{ flex: 1 }}
                  />
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAddTopicTag}
                    disabled={!newTopicTag.trim()}
                  >
                    添加
                  </Button>
                </Space.Compact>
              </div>
              
              {value.topic_tags.custom_tags.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <Space wrap>
                    {value.topic_tags.custom_tags.map((tag) => (
                      <Tag
                        key={tag}
                        closable
                        onClose={() => handleRemoveTopicTag(tag)}
                        color="orange"
                      >
                        #{tag}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}
            </div>
          </div>
        )}

        <Divider />

        {/* 每篇貼文最大標籤數量 */}
        <div>
          <Title level={5}>每篇貼文最大標籤數量</Title>
          <Space>
            <Text>最多</Text>
            <Select
              value={value.max_tags_per_post}
              onChange={handleMaxTagsChange}
              style={{ width: '100px' }}
            >
              <Option value={3}>3個</Option>
              <Option value={5}>5個</Option>
              <Option value={8}>8個</Option>
              <Option value={10}>10個</Option>
            </Select>
            <Text>個標籤</Text>
          </Space>
          <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
            建議設定5-8個標籤，避免過多影響閱讀體驗
          </Text>
        </div>

        {/* 標籤預覽 */}
        <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
          <Title level={5} style={{ color: '#52c41a', margin: 0 }}>標籤預覽</Title>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Text type="secondary">
              根據當前設定，貼文將包含以下類型的標籤：
            </Text>
            
            {(value.tag_mode === 'stock_tags' || value.tag_mode === 'both') && (
              <div>
                <Text strong>股票標籤：</Text>
                <Space wrap>
                  {value.stock_tags.include_stock_code && <Tag color="blue">#2330</Tag>}
                  {value.stock_tags.include_stock_name && <Tag color="green">#台積電</Tag>}
                  {value.stock_tags.custom_tags.map(tag => (
                    <Tag key={tag} color="blue">#{tag}</Tag>
                  ))}
                </Space>
              </div>
            )}
            
            {(value.tag_mode === 'topic_tags' || value.tag_mode === 'both') && (
              <div>
                <Text strong>話題標籤：</Text>
                <Space wrap>
                  {value.topic_tags.trending_topics.slice(0, 3).map(topic => (
                    <Tag key={topic} color="orange">#{topic}</Tag>
                  ))}
                  {value.topic_tags.custom_tags.map(tag => (
                    <Tag key={tag} color="orange">#{tag}</Tag>
                  ))}
                </Space>
              </div>
            )}
          </Space>
        </Card>

        {/* Body Parameter 預覽 */}
        {triggerData?.stock_codes?.length && kolData?.kol_serials?.length && (
          <Card size="small" style={{ backgroundColor: '#f0f5ff', border: '1px solid #adc6ff' }}>
            <Title level={5} style={{ color: '#1890ff', margin: 0 }}>
              <TagsOutlined /> Body Parameter 預覽
            </Title>
            <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: '12px' }}>
              每篇貼文預計送出的 commodityTags JSON 格式
            </Text>
            
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {generateBodyParameterPreview().map((preview, index) => (
                <Card key={index} size="small" style={{ backgroundColor: '#fff', border: '1px solid #d9d9d9' }}>
                  <div style={{ marginBottom: '8px' }}>
                    <Text strong style={{ color: '#1890ff' }}>
                      {preview.kol_name} ({preview.kol_serial})
                    </Text>
                    <Tag color="blue" style={{ marginLeft: '8px' }}>
                      {preview.tagCount} 個標籤
                    </Tag>
                    {preview.isSharedTags && (
                      <Tag color="green" style={{ marginLeft: '8px' }}>
                        全貼同群股標
                      </Tag>
                    )}
                  </div>
                  
                  <div style={{ backgroundColor: '#fafafa', padding: '8px', borderRadius: '4px', fontSize: '12px' }}>
                    <Text code style={{ fontSize: '11px', lineHeight: '1.4' }}>
                      {JSON.stringify(preview.commodityTags, null, 2)}
                    </Text>
                  </div>
                </Card>
              ))}
            </Space>
          </Card>
        )}
      </Space>
    </Card>
  );
};

export default TagSettings;
