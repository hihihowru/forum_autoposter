import React, { useState, useEffect } from 'react';
import { Card, Typography, Radio, Space, Select, Button, Tag, Divider, Row, Col, Avatar, message, Spin } from 'antd';
import { UserOutlined, SettingOutlined, ReloadOutlined } from '@ant-design/icons';
import KOLService, { KOLProfile } from '../../../services/kolService';

const { Title, Text } = Typography;
const { Option } = Select;

interface KOLConfig {
  assignment_mode: 'fixed' | 'dynamic' | 'random' | 'pool_random';
  selected_kols: number[];
  dynamic_criteria: {
    style_preference: string[];
    expertise_match: boolean;
    activity_level: string;
  };
  max_kols_per_post: number;
  random_pool?: boolean; // 標記是否為隨機池模式
}

interface KOLSelectorProps {
  value: KOLConfig;
  onChange: (value: KOLConfig) => void;
}

const KOLSelector: React.FC<KOLSelectorProps> = ({ value, onChange }) => {
  const [availableKOLs, setAvailableKOLs] = useState<KOLProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedKOLs, setSelectedKOLs] = useState<number[]>(value?.selected_kols || []);
  const [dynamicCriteria, setDynamicCriteria] = useState(value?.dynamic_criteria || {
    style_preference: [],
    expertise_match: true,
    activity_level: 'high'
  });

  // 載入KOL資料
  useEffect(() => {
    loadKOLs();
  }, []);

  const loadKOLs = async () => {
    try {
      setLoading(true);
      
      // 從真實API獲取KOL資料
      const kols = await KOLService.getActiveKOLs();
      
      if (kols.length === 0) {
        message.warning('API沒有返回KOL資料');
        setAvailableKOLs([]);
      } else {
        setAvailableKOLs(kols);
        message.success(`載入 ${kols.length} 個KOL資料`);
      }
      
    } catch (error) {
      console.error('載入KOL資料失敗:', error);
      message.error('載入KOL資料失敗，請檢查後端服務');
      setAvailableKOLs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignmentModeChange = (mode: 'fixed' | 'dynamic' | 'random' | 'pool_random') => {
    onChange({
      ...value,
      assignment_mode: mode,
      selected_kols: mode === 'dynamic' || mode === 'random' ? [] : value.selected_kols,
      random_pool: mode === 'pool_random', // 🔥 NEW: Mark pool_random mode
      dynamic_criteria: mode === 'fixed' || mode === 'pool_random' ? value.dynamic_criteria : {
        style_preference: [],
        expertise_match: true,
        activity_level: 'high'
      }
    });
  };

  const handleKOLSelection = (kolSerials: number[]) => {
    try {
      console.log('KOL選擇變更:', kolSerials);
      setSelectedKOLs(kolSerials);
      
      const newConfig = {
        ...value,
        selected_kols: kolSerials
      };
      
      console.log('更新KOL配置:', newConfig);
      onChange(newConfig);
    } catch (error) {
      console.error('KOL選擇處理錯誤:', error);
      message.error('KOL選擇處理失敗');
    }
  };

  const handleDynamicCriteriaChange = (key: keyof KOLConfig['dynamic_criteria'], newValue: any) => {
    const newCriteria = {
      ...value.dynamic_criteria,
      [key]: newValue
    };
    setDynamicCriteria(newCriteria);
    onChange({
      ...value,
      dynamic_criteria: newCriteria
    });
  };

  const getPersonaColor = (persona: string) => {
    const colors: Record<string, string> = {
      '技術派': 'blue',
      '總經派': 'green',
      '消息派': 'orange',
      '籌碼派': 'purple',
      '基本面派': 'cyan'
    };
    return colors[persona] || 'default';
  };

  const getSelectedKOLs = () => {
    return availableKOLs.filter(kol => selectedKOLs.includes(kol.serial));
  };

  return (
    <Card title="KOL選擇設定" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <Title level={5}>指派模式</Title>
          <Radio.Group
            value={value?.assignment_mode || 'random'}
            onChange={(e) => handleAssignmentModeChange(e.target.value)}
          >
            <Space direction="vertical">
              <Radio value="fixed">固定指派</Radio>
              <Radio value="dynamic">動態派發</Radio>
              <Radio value="random">完全隨機（所有KOL）</Radio>
              <Radio value="pool_random">🎯 池子隨機（自選KOL池）</Radio>
            </Space>
          </Radio.Group>
        </div>

        {value?.assignment_mode === 'fixed' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <Title level={5}>選擇KOL</Title>
              <Button 
                icon={<ReloadOutlined />} 
                size="small" 
                onClick={loadKOLs}
                loading={loading}
              >
                重新載入
              </Button>
            </div>
            
            <Spin spinning={loading}>
              <Select
                mode="multiple"
                placeholder="選擇要指派的KOL"
                value={selectedKOLs}
                onChange={handleKOLSelection}
                style={{ width: '100%' }}
                optionLabelProp="label"
              >
                {availableKOLs.map((kol) => (
                  <Option key={kol.serial} value={kol.serial} label={kol.nickname}>
                    <Space>
                      <Avatar size="small" icon={<UserOutlined />} />
                      <span>{kol.nickname}</span>
                      <Tag color={getPersonaColor(kol.persona)}>
                        {kol.persona}
                      </Tag>
                    </Space>
                  </Option>
                ))}
              </Select>
            </Spin>

            {getSelectedKOLs().length > 0 && (
              <div style={{ marginTop: '12px' }}>
                <Text strong>已選擇的KOL:</Text>
                <Space wrap style={{ marginTop: '8px' }}>
                  {getSelectedKOLs().map((kol) => (
                    <Card key={kol.serial} size="small" style={{ width: '300px' }}>
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Space>
                            <Avatar size="small" icon={<UserOutlined />} />
                            <Text strong>{kol.nickname}</Text>
                            <Tag color={getPersonaColor(kol.persona)}>
                              {kol.persona}
                            </Tag>
                          </Space>
                          <Text type="secondary">#{kol.serial}</Text>
                        </div>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {kol.tone_style} • {kol.target_audience}
                        </Text>
                        <div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            專長: {kol.content_types.join(', ')}
                          </Text>
                        </div>
                        <div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            活躍度: {kol.status} • 互動閾值: {kol.interaction_threshold}
                          </Text>
                        </div>
                      </Space>
                    </Card>
                  ))}
                </Space>
              </div>
            )}
          </div>
        )}

        {value?.assignment_mode === 'dynamic' && (
          <div>
            <Title level={5}>動態派發條件</Title>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <Text>人設偏好</Text>
                <Select
                  mode="multiple"
                  placeholder="選擇偏好的人設"
                  value={dynamicCriteria.style_preference}
                  onChange={(value) => handleDynamicCriteriaChange('style_preference', value)}
                  style={{ width: '100%', marginTop: '8px' }}
                >
                  <Option value="技術派">技術派</Option>
                  <Option value="總經派">總經派</Option>
                  <Option value="消息派">消息派</Option>
                  <Option value="籌碼派">籌碼派</Option>
                  <Option value="基本面派">基本面派</Option>
                </Select>
              </div>

              <div>
                <Text>專業匹配度</Text>
                <Radio.Group
                  value={dynamicCriteria.expertise_match}
                  onChange={(e) => handleDynamicCriteriaChange('expertise_match', e.target.value)}
                  style={{ marginTop: '8px' }}
                >
                  <Radio value={true}>高匹配</Radio>
                  <Radio value={false}>一般匹配</Radio>
                </Radio.Group>
              </div>

              <div>
                <Text>活躍程度</Text>
                <Select
                  value={dynamicCriteria.activity_level}
                  onChange={(value) => handleDynamicCriteriaChange('activity_level', value)}
                  style={{ width: '100%', marginTop: '8px' }}
                >
                  <Option value="high">高活躍</Option>
                  <Option value="medium">中等活躍</Option>
                  <Option value="low">低活躍</Option>
                </Select>
              </div>
            </Space>
          </div>
        )}

        {value?.assignment_mode === 'random' && (
          <div>
            <Title level={5}>隨機模式設定</Title>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div style={{ backgroundColor: '#f6ffed', padding: '12px', borderRadius: '6px', border: '1px solid #b7eb8f' }}>
                <Text type="secondary">
                  🎲 隨機模式會從所有可用的KOL中隨機選擇，確保發文的多樣性和公平性
                </Text>
              </div>
              <div>
                <Text>可用KOL數量: {availableKOLs.length}</Text>
              </div>
              <div>
                <Button 
                  type="primary" 
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    if (availableKOLs.length === 0) {
                      message.warning('沒有可用的KOL，請先載入KOL資料');
                      return;
                    }
                    
                    // 創建隨機池子：選擇所有可用的KOL作為隨機分配池，並打亂順序
                    const allKOLSerials = availableKOLs.map(kol => kol.serial);
                    // 使用 Fisher-Yates 洗牌算法打亂順序
                    for (let i = allKOLSerials.length - 1; i > 0; i--) {
                      const j = Math.floor(Math.random() * (i + 1));
                      [allKOLSerials[i], allKOLSerials[j]] = [allKOLSerials[j], allKOLSerials[i]];
                    }
                    
                    onChange({
                      ...value,
                      selected_kols: allKOLSerials, // 所有KOL都加入隨機池
                      random_pool: true // 標記為隨機池模式
                    });
                    
                    message.success(`已創建隨機池子，包含 ${allKOLSerials.length} 個KOL，系統將隨機分配給不同貼文`);
                  }}
                  disabled={availableKOLs.length === 0}
                >
                  創建隨機池子
                </Button>
              </div>
              
              {/* 顯示隨機池中的KOL */}
              {value?.selected_kols && value.selected_kols.length > 0 && (
                <div>
                  <Text strong>
                    {value?.random_pool ? '隨機池中的KOL:' : '已選擇的隨機KOL:'}
                  </Text>
                  {value?.random_pool && (
                    <div style={{ marginTop: '8px', marginBottom: '8px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        💡 系統將從這個池子中隨機選擇不同的KOL分配給同一批次中的不同貼文
                      </Text>
                    </div>
                  )}
                  <Space wrap style={{ marginTop: '8px' }}>
                    {value.selected_kols.map((kolSerial) => {
                      const kol = availableKOLs.find(k => k.serial === kolSerial);
                      if (!kol) return null;
                      
                      return (
                        <Card key={kol.serial} size="small" style={{ width: '300px' }}>
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Space>
                                <Avatar size="small" icon={<UserOutlined />} />
                                <Text strong>{kol.nickname}</Text>
                                <Tag color={getPersonaColor(kol.persona)}>
                                  {kol.persona}
                                </Tag>
                              </Space>
                              <Text type="secondary">#{kol.serial}</Text>
                            </div>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              {kol.tone_style} • {kol.target_audience}
                            </Text>
                            <div>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                專長: {kol.content_types.join(', ')}
                              </Text>
                            </div>
                          </Space>
                        </Card>
                      );
                    })}
                  </Space>
                </div>
              )}
            </Space>
          </div>
        )}

        {value?.assignment_mode === 'pool_random' && (
          <div>
            <Title level={5}>🎯 自選KOL池（池子隨機模式）</Title>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div style={{ backgroundColor: '#e6f7ff', padding: '12px', borderRadius: '6px', border: '1px solid #91d5ff' }}>
                <Text type="secondary">
                  💡 <strong>池子隨機模式：</strong>只從你選擇的KOL中隨機分配，避免使用到其他人管理的KOL
                </Text>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <Text strong>選擇KOL加入隨機池</Text>
                  <Button
                    icon={<ReloadOutlined />}
                    size="small"
                    onClick={loadKOLs}
                    loading={loading}
                  >
                    重新載入
                  </Button>
                </div>

                <Spin spinning={loading}>
                  <Select
                    mode="multiple"
                    placeholder="拖拉或點選KOL加入隨機池（可多選）"
                    value={selectedKOLs}
                    onChange={handleKOLSelection}
                    style={{ width: '100%' }}
                    optionLabelProp="label"
                    maxTagCount="responsive"
                    showSearch
                    filterOption={(input, option) =>
                      ((option?.label as string) ?? '').toLowerCase().includes(input.toLowerCase())
                    }
                  >
                    {availableKOLs.map((kol) => (
                      <Option key={kol.serial} value={kol.serial} label={kol.nickname}>
                        <Space>
                          <Avatar size="small" icon={<UserOutlined />} />
                          <span>{kol.nickname}</span>
                          <Tag color={getPersonaColor(kol.persona)}>
                            {kol.persona}
                          </Tag>
                          <Text type="secondary" style={{ fontSize: '11px' }}>
                            #{kol.serial}
                          </Text>
                        </Space>
                      </Option>
                    ))}
                  </Select>
                </Spin>
              </div>

              {getSelectedKOLs().length > 0 && (
                <div>
                  <Text strong>已選擇 {getSelectedKOLs().length} 個KOL加入隨機池:</Text>
                  <div style={{ marginTop: '8px', marginBottom: '8px' }}>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      🎲 系統將從這 {getSelectedKOLs().length} 個KOL中隨機選擇不同的KOL分配給同一批次中的不同貼文
                    </Text>
                  </div>
                  <Space wrap style={{ marginTop: '8px' }}>
                    {getSelectedKOLs().map((kol) => (
                      <Card key={kol.serial} size="small" style={{ width: '280px' }}>
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Space>
                              <Avatar size="small" icon={<UserOutlined />} />
                              <Text strong>{kol.nickname}</Text>
                              <Tag color={getPersonaColor(kol.persona)}>
                                {kol.persona}
                              </Tag>
                            </Space>
                            <Text type="secondary">#{kol.serial}</Text>
                          </div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {kol.tone_style} • {kol.target_audience}
                          </Text>
                          <div>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              專長: {kol.content_types.join(', ')}
                            </Text>
                          </div>
                        </Space>
                      </Card>
                    ))}
                  </Space>
                </div>
              )}

              {getSelectedKOLs().length === 0 && (
                <div style={{ backgroundColor: '#fff7e6', padding: '12px', borderRadius: '6px', border: '1px solid #ffd591' }}>
                  <Text type="warning">
                    ⚠️ 請至少選擇 1 個KOL加入隨機池
                  </Text>
                </div>
              )}
            </Space>
          </div>
        )}

        <Divider />

        <div>
          <Title level={5}>發文設定</Title>
          <Row gutter={16}>
            <Col span={12}>
              <Text>每篇發文最大KOL數</Text>
              <Select
                value={value?.max_kols_per_post || 3}
                onChange={(maxKols) => onChange({ ...value, max_kols_per_post: maxKols })}
                style={{ width: '100%', marginTop: '8px' }}
              >
                <Option value={1}>1個KOL</Option>
                <Option value={2}>2個KOL</Option>
                <Option value={3}>3個KOL</Option>
                <Option value={5}>5個KOL</Option>
              </Select>
            </Col>
          </Row>
        </div>

        <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '6px' }}>
          <Text type="secondary">
            <SettingOutlined /> <strong>模式說明：</strong>
          </Text>
          <ul style={{ marginTop: '8px', marginBottom: 0, paddingLeft: '20px' }}>
            <li><Text type="secondary">固定指派：使用指定的KOL發文</Text></li>
            <li><Text type="secondary">動態派發：根據條件自動選擇最適合的KOL</Text></li>
            <li><Text type="secondary">完全隨機：從所有可用KOL中隨機分配</Text></li>
            <li><Text type="secondary" strong>池子隨機：只從你選擇的KOL池中隨機分配（推薦）</Text></li>
          </ul>
        </div>
      </Space>
    </Card>
  );
};

export default KOLSelector;