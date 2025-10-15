import React, { useState } from 'react';
import { Card, Typography, InputNumber, Input, Space, Button, Tag, Divider, Row, Col, Tooltip, Select, Switch } from 'antd';
import { PlusOutlined, DeleteOutlined, DragOutlined, LinkOutlined, SearchOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface NewsSearchKeyword {
  id: string;
  keyword: string;
  type: 'stock_name' | 'trigger_keyword' | 'custom';
  description: string;
}

interface NewsConfig {
  max_links: number;
  search_keywords: NewsSearchKeyword[];
  use_realtime_news_api: boolean;
  search_templates: string[];
  time_range: string;  // 新增時間範圍設定
  enable_news_links: boolean;  // 新增新聞連結開關
}

interface NewsConfigProps {
  value: NewsConfig;
  onChange: (value: NewsConfig) => void;
  // 移除手動選擇熱門話題的功能
}

const DraggableKeyword: React.FC<{
  keyword: NewsSearchKeyword;
  index: number;
  onDelete: (id: string) => void;
  onUpdate: (id: string, keyword: NewsSearchKeyword) => void;
}> = ({ keyword, index, onDelete, onUpdate }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'keyword',
    item: { index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'stock_name': return 'blue';
      case 'trigger_keyword': return 'green';
      case 'custom': return 'orange';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'stock_name': return '📈';
      case 'trigger_keyword': return '⚡';
      case 'custom': return '✏️';
      default: return '📝';
    }
  };

  return (
    <div
      ref={drag}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
        padding: '8px',
        border: '1px solid #d9d9d9',
        borderRadius: '6px',
        marginBottom: '8px',
        backgroundColor: '#fff'
      }}
    >
      <Row align="middle" gutter={8}>
        <Col>
          <DragOutlined style={{ color: '#999' }} />
        </Col>
        <Col flex="auto">
          <Space>
            <Tag color={getTypeColor(keyword.type)}>
              {getTypeIcon(keyword.type)} {keyword.type === 'stock_name' ? '股票名稱' : 
               keyword.type === 'trigger_keyword' ? '觸發關鍵字' : '自定義'}
            </Tag>
            <Text strong>{keyword.keyword}</Text>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {keyword.description}
            </Text>
          </Space>
        </Col>
        <Col>
          <Button
            type="text"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => onDelete(keyword.id)}
          />
        </Col>
      </Row>
    </div>
  );
};

const NewsConfig: React.FC<NewsConfigProps> = ({ value, onChange }) => {
  const [newKeyword, setNewKeyword] = useState('');
  const [newKeywordType, setNewKeywordType] = useState<'stock_name' | 'trigger_keyword' | 'custom'>('custom');

  const handleMaxLinksChange = (maxLinks: number | null) => {
    onChange({
      ...value,
      max_links: maxLinks || 3
    });
  };

  const handleTimeRangeChange = (timeRange: string) => {
    onChange({
      ...value,
      time_range: timeRange
    });
  };

  const handleEnableNewsLinksChange = (enable: boolean) => {
    onChange({
      ...value,
      enable_news_links: enable
    });
  };

  const handleAddKeyword = () => {
    if (newKeyword.trim()) {
      const keyword: NewsSearchKeyword = {
        id: Date.now().toString(),
        keyword: newKeyword.trim(),
        type: newKeywordType,
        description: getKeywordDescription(newKeywordType, newKeyword.trim())
      };
      
      onChange({
        ...value,
        search_keywords: [...value.search_keywords, keyword]
      });
      
      setNewKeyword('');
    }
  };

  const handleDeleteKeyword = (id: string) => {
    onChange({
      ...value,
      search_keywords: value.search_keywords.filter(k => k.id !== id)
    });
  };

  const handleUpdateKeyword = (id: string, updatedKeyword: NewsSearchKeyword) => {
    onChange({
      ...value,
      search_keywords: value.search_keywords.map(k => k.id === id ? updatedKeyword : k)
    });
  };

  const getKeywordDescription = (type: string, keyword: string) => {
    switch (type) {
      case 'stock_name': return `股票名稱參數 (${keyword})`;
      case 'trigger_keyword': return `觸發關鍵字 (${keyword})`;
      case 'custom': return `自定義關鍵字 (${keyword})`;
      default: return keyword;
    }
  };

  const moveKeyword = (dragIndex: number, hoverIndex: number) => {
    const draggedKeyword = value.search_keywords[dragIndex];
    const newKeywords = [...value.search_keywords];
    newKeywords.splice(dragIndex, 1);
    newKeywords.splice(hoverIndex, 0, draggedKeyword);
    
    onChange({
      ...value,
      search_keywords: newKeywords
    });
  };

  const DropTarget: React.FC<{ index: number }> = ({ index }) => {
    const [{ isOver }, drop] = useDrop({
      accept: 'keyword',
      drop: (item: { index: number }) => {
        if (item.index !== index) {
          moveKeyword(item.index, index);
        }
      },
      collect: (monitor) => ({
        isOver: monitor.isOver(),
      }),
    });

    return (
      <div
        ref={drop}
        style={{
          height: '4px',
          backgroundColor: isOver ? '#1890ff' : 'transparent',
          borderRadius: '2px',
          margin: '2px 0'
        }}
      />
    );
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <Card title="新聞搜尋設定" size="small">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Text type="secondary">
            配置新聞搜尋參數，支援拖曳排序和動態關鍵字設定
          </Text>

          {/* 自動熱門話題關鍵字提取提示 */}
          <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <SearchOutlined style={{ color: '#52c41a' }} />
                <Text strong style={{ color: '#52c41a' }}>自動熱門話題關鍵字</Text>
              </Space>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                💡 系統會根據選擇的股票自動標記對應的熱門話題關鍵字，無需手動選擇
              </Text>
            </Space>
          </Card>

          {/* 即時新聞API設定 */}
          <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <LinkOutlined style={{ color: '#52c41a' }} />
                <Text strong style={{ color: '#52c41a' }}>即時新聞 API</Text>
                <Text type="secondary">已啟用即時新聞搜尋功能</Text>
              </Space>
              
              {/* 時間範圍設定 */}
              <div>
                <Space align="center">
                  <ClockCircleOutlined style={{ color: '#52c41a' }} />
                  <Text strong>新聞時間範圍：</Text>
                  <Select
                    value={value.time_range || 'd2'}
                    onChange={handleTimeRangeChange}
                    style={{ width: '120px' }}
                    size="small"
                  >
                    <Select.Option value="h1">過去1小時</Select.Option>
                    <Select.Option value="d1">過去1天</Select.Option>
                    <Select.Option value="d2">過去2天</Select.Option>
                    <Select.Option value="w1">過去1週</Select.Option>
                    <Select.Option value="m1">過去1個月</Select.Option>
                  </Select>
                </Space>
                <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                  限制搜尋結果的時間範圍，避免獲取過期的新聞資料
                </Text>
              </div>
            </Space>
          </Card>

          {/* 新聞連結開關控制 */}
          <div>
            <Title level={5}>新聞連結設定</Title>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Text>啟用新聞連結：</Text>
                <Switch
                  checked={value.enable_news_links !== false}
                  onChange={handleEnableNewsLinksChange}
                  checkedChildren="開啟"
                  unCheckedChildren="關閉"
                />
              </Space>
              {value.enable_news_links !== false && (
                <Space>
                  <Text>最多顯示</Text>
                  <InputNumber
                    min={1}
                    max={10}
                    value={value.max_links}
                    onChange={handleMaxLinksChange}
                    style={{ width: '80px' }}
                  />
                  <Text>個新聞連結</Text>
                </Space>
              )}
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                {value.enable_news_links !== false 
                  ? '建議設定3-5個連結，避免內容過於冗長'
                  : '關閉後將不會在貼文中包含新聞連結'
                }
              </Text>
            </Space>
          </div>

          <Divider />

          {/* 搜尋關鍵字管理 */}
          <div>
            <Title level={5}>搜尋關鍵字設定</Title>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              拖曳調整關鍵字順序，系統會依序搜尋並組合關鍵字
            </Text>

            {/* 添加新關鍵字 */}
            <Card size="small" style={{ marginTop: '12px', backgroundColor: '#fafafa' }}>
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  placeholder="輸入搜尋關鍵字..."
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onPressEnter={handleAddKeyword}
                  style={{ flex: 1 }}
                />
                <select
                  value={newKeywordType}
                  onChange={(e) => setNewKeywordType(e.target.value as any)}
                  style={{
                    padding: '4px 8px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '0',
                    backgroundColor: '#fff'
                  }}
                >
                  <option value="stock_name">股票名稱</option>
                  <option value="trigger_keyword">觸發關鍵字</option>
                  <option value="custom">自定義</option>
                </select>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAddKeyword}
                  disabled={!newKeyword.trim()}
                >
                  添加
                </Button>
              </Space.Compact>
            </Card>

            {/* 關鍵字列表 */}
            <div style={{ marginTop: '12px', maxHeight: '300px', overflowY: 'auto' }}>
              {value.search_keywords.map((keyword, index) => (
                <div key={keyword.id}>
                  <DropTarget index={index} />
                  <DraggableKeyword
                    keyword={keyword}
                    index={index}
                    onDelete={handleDeleteKeyword}
                    onUpdate={handleUpdateKeyword}
                  />
                </div>
              ))}
              <DropTarget index={value.search_keywords.length} />
            </div>

            {/* 搜尋模板說明 */}
            <Card size="small" style={{ marginTop: '12px', backgroundColor: '#e6f7ff', border: '1px solid #91d5ff' }}>
              <Title level={5} style={{ color: '#1890ff', margin: 0 }}>搜尋模板說明</Title>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Text type="secondary">
                  • <Text strong>股票名稱</Text>：會自動替換為實際股票名稱 (如：台積電)
                </Text>
                <Text type="secondary">
                  • <Text strong>觸發關鍵字</Text>：根據觸發器類型自動選擇 (如：漲停、跌停)
                </Text>
                <Text type="secondary">
                  • <Text strong>自定義</Text>：手動設定的固定關鍵字
                </Text>
                <Text type="secondary">
                  • 搜尋格式：{'{股票名稱}'} + {'{觸發關鍵字}'} + {'{自定義關鍵字}'}
                </Text>
              </Space>
            </Card>
          </div>

          {/* 搜尋預覽 */}
          {value.search_keywords.length > 0 && (
            <Card size="small" style={{ backgroundColor: '#fff7e6', border: '1px solid #ffd591' }}>
              <Title level={5} style={{ color: '#fa8c16', margin: 0 }}>搜尋預覽</Title>
              <Text type="secondary">
                實際搜尋關鍵字組合：
                <Text code style={{ marginLeft: '8px' }}>
                  {value.search_keywords.map(k => k.keyword).join(' + ')}
                </Text>
              </Text>
            </Card>
          )}
        </Space>
      </Card>
    </DndProvider>
  );
};

export default NewsConfig;
