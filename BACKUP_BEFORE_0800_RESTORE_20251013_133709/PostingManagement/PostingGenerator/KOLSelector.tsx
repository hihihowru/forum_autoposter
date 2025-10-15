import React, { useState, useEffect } from 'react';
import { Card, Typography, Radio, Space, Select, Button, Tag, Divider, Row, Col, Avatar, message, Spin } from 'antd';
import { UserOutlined, SettingOutlined, ReloadOutlined } from '@ant-design/icons';
import KOLService, { KOLProfile } from '../../../services/kolService';

const { Title, Text } = Typography;
const { Option } = Select;

interface KOLConfig {
  assignment_mode: 'fixed' | 'dynamic';
  selected_kols: number[];
  dynamic_criteria: {
    style_preference: string[];
    expertise_match: boolean;
    activity_level: string;
  };
  max_kols_per_post: number;
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

  const handleAssignmentModeChange = (mode: 'fixed' | 'dynamic') => {
    onChange({
      ...value,
      assignment_mode: mode,
      selected_kols: mode === 'dynamic' ? [] : value.selected_kols,
      dynamic_criteria: mode === 'fixed' ? value.dynamic_criteria : {
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
            value={value?.assignment_mode || 'dynamic'}
            onChange={(e) => handleAssignmentModeChange(e.target.value)}
          >
            <Radio value="fixed">固定指派</Radio>
            <Radio value="dynamic">動態派發</Radio>
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
            <SettingOutlined /> 提示：固定指派模式會使用指定的KOL，動態派發模式會根據條件自動選擇最適合的KOL
          </Text>
        </div>
      </Space>
    </Card>
  );
};

export default KOLSelector;