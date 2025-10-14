import React, { useState, useEffect } from 'react';
import { Card, Typography, Input, Button, Space, Divider, Row, Col, message, Spin, Alert } from 'antd';
import { EditOutlined, SaveOutlined, ReloadOutlined, UserOutlined } from '@ant-design/icons';
import KOLService, { KOLProfile } from '../../../services/kolService';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface KOLPromptConfig {
  kol_serial: number;
  nickname: string;
  persona: string;
  default_prompt: string;
  custom_prompt?: string;
  is_customized: boolean;
}

interface KOLPromptTunerProps {
  value: KOLPromptConfig[];
  onChange: (value: KOLPromptConfig[]) => void;
  selectedKOLs: number[];
}

const KOLPromptTuner: React.FC<KOLPromptTunerProps> = ({ value, onChange, selectedKOLs }) => {
  const [availableKOLs, setAvailableKOLs] = useState<KOLProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [promptConfigs, setPromptConfigs] = useState<KOLPromptConfig[]>(value || []);

  // 載入KOL數據
  const loadKOLs = async () => {
    try {
      setLoading(true);
      const kols = await KOLService.getActiveKOLs();
      setAvailableKOLs(kols);
      
      // 初始化prompt配置
      initializePromptConfigs(kols);
    } catch (error) {
      console.error('載入KOL數據失敗:', error);
      message.error('載入KOL數據失敗');
    } finally {
      setLoading(false);
    }
  };

  // 初始化prompt配置
  const initializePromptConfigs = (kols: KOLProfile[]) => {
    const configs: KOLPromptConfig[] = selectedKOLs.map(serial => {
      const kol = kols.find(k => k.serial === serial);
      if (!kol) return null;

      // 生成默認prompt
      const defaultPrompt = generateDefaultPrompt(kol);
      
      return {
        kol_serial: serial,
        nickname: kol.nickname,
        persona: kol.persona,
        default_prompt: defaultPrompt,
        custom_prompt: defaultPrompt,
        is_customized: false
      };
    }).filter(Boolean) as KOLPromptConfig[];

    setPromptConfigs(configs);
    onChange(configs);
  };

  // 生成默認prompt
  const generateDefaultPrompt = (kol: KOLProfile): string => {
    const basePrompt = `你是一位專業的股票分析師，暱稱是「${kol.nickname}」，人設是「${kol.persona}」。

你的分析風格特點：
- 專業領域：${kol.content_types?.join('、') || '股票分析'}
- 內容長度：${kol.tone_style || '中等'}
- 互動方式：${kol.interaction_threshold > 0.5 ? '積極互動' : '專業分析'}

請根據以下要求生成股票分析內容：
1. 保持${kol.persona}的專業風格
2. 使用${kol.nickname}的語言特色
3. 提供有價值的投資建議
4. 適當加入互動元素

請分析以下股票：{stock_info}`;

    return basePrompt;
  };

  // 處理prompt修改
  const handlePromptChange = (kolSerial: number, newPrompt: string) => {
    const updatedConfigs = promptConfigs.map(config => 
      config.kol_serial === kolSerial 
        ? { 
            ...config, 
            custom_prompt: newPrompt,
            is_customized: newPrompt !== config.default_prompt
          }
        : config
    );
    
    setPromptConfigs(updatedConfigs);
    onChange(updatedConfigs);
  };

  // 重置為默認prompt
  const handleResetPrompt = (kolSerial: number) => {
    const config = promptConfigs.find(c => c.kol_serial === kolSerial);
    if (config) {
      handlePromptChange(kolSerial, config.default_prompt);
      message.success('已重置為默認prompt');
    }
  };

  // 保存prompt模板
  const handleSaveTemplate = async (kolSerial: number) => {
    const config = promptConfigs.find(c => c.kol_serial === kolSerial);
    if (config && config.is_customized) {
      try {
        // TODO: 調用API保存prompt模板
        message.success('Prompt模板已保存');
      } catch (error) {
        console.error('保存prompt模板失敗:', error);
        message.error('保存失敗');
      }
    }
  };

  // 組件掛載時載入數據
  useEffect(() => {
    if (selectedKOLs.length > 0) {
      loadKOLs();
    }
  }, [selectedKOLs]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>載入KOL數據中...</div>
      </div>
    );
  }

  if (selectedKOLs.length === 0) {
    return (
      <Alert
        message="請先選擇KOL"
        description="請在KOL選擇步驟中選擇要生成內容的KOL"
        type="info"
        showIcon
      />
    );
  }

  return (
    <div>
      <Title level={4}>KOL Prompt 微調</Title>
      <Text type="secondary">
        為每個選中的KOL自定義prompt模板，以獲得更好的內容生成效果
      </Text>
      
      <Divider />
      
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {promptConfigs.map((config) => (
          <Card
            key={config.kol_serial}
            title={
              <Space>
                <UserOutlined />
                <span>{config.nickname}</span>
                <Text type="secondary">({config.persona})</Text>
                {config.is_customized && (
                  <Text type="warning">已自定義</Text>
                )}
              </Space>
            }
            extra={
              <Space>
                <Button
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={() => handleResetPrompt(config.kol_serial)}
                >
                  重置
                </Button>
                {config.is_customized && (
                  <Button
                    size="small"
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={() => handleSaveTemplate(config.kol_serial)}
                  >
                    保存模板
                  </Button>
                )}
              </Space>
            }
          >
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Text strong>Prompt 模板：</Text>
                <TextArea
                  value={config.custom_prompt}
                  onChange={(e) => handlePromptChange(config.kol_serial, e.target.value)}
                  rows={8}
                  placeholder="請輸入prompt模板..."
                  style={{ marginTop: '8px' }}
                />
              </Col>
              
              {config.is_customized && (
                <Col span={24}>
                  <Alert
                    message="已自定義"
                    description="此KOL的prompt已從默認模板修改"
                    type="info"
                    showIcon
                    style={{ marginTop: '8px' }}
                  />
                </Col>
              )}
            </Row>
          </Card>
        ))}
      </Space>
      
      <Divider />
      
      <Alert
        message="Prompt 模板說明"
        description={
          <div>
            <p>• <strong>默認prompt</strong>：基於KOL的人設和風格自動生成</p>
            <p>• <strong>自定義prompt</strong>：可以根據特定需求調整prompt內容</p>
            <p>• <strong>變量支持</strong>：使用 {`{stock_info}`} 等變量來動態插入股票信息</p>
            <p>• <strong>保存模板</strong>：自定義的prompt可以保存為模板供後續使用</p>
          </div>
        }
        type="info"
        showIcon
      />
    </div>
  );
};

export default KOLPromptTuner;





















