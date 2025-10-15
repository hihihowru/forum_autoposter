import React, { useState } from 'react';
import { Card, Row, Col, Collapse, Tag, Typography, Space, Input, InputNumber } from 'antd';
import { 
  UserOutlined, 
  RobotOutlined
} from '@ant-design/icons';
import { KOLSettingsProps } from '../../types/kol-types';

const { TextArea } = Input;

const { Panel } = Collapse;
const { Text, Paragraph } = Typography;

const KOLSettings: React.FC<KOLSettingsProps> = ({ 
  kolInfo, 
  loading, 
  error,
  isEditMode = false,
  onKolInfoChange
}) => {
  const [activeKeys, setActiveKeys] = useState<string[]>(['persona', 'prompt']);

  if (loading) {
    return (
      <Card title="KOL 設定" size="small">
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div>載入中...</div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="KOL 設定" size="small">
        <div style={{ color: '#ff4d4f' }}>載入失敗: {error}</div>
      </Card>
    );
  }

  return (
    <Card title="KOL 設定" size="small">
      <Collapse 
        activeKey={activeKeys} 
        onChange={setActiveKeys}
        size="small"
      >
        {/* 人設設定 */}
        <Panel 
          header={
            <Space>
              <UserOutlined />
              <span>人設設定</span>
            </Space>
          } 
          key="persona"
        >
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card size="small" title="常用詞彙" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.common_terms}
                    onChange={(e) => onKolInfoChange?.('common_terms', e.target.value)}
                    placeholder="輸入常用詞彙，用逗號分隔"
                    rows={4}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.common_terms || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="口語化用詞" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.colloquial_terms}
                    onChange={(e) => onKolInfoChange?.('colloquial_terms', e.target.value)}
                    placeholder="輸入口語化用詞，用逗號分隔"
                    rows={4}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.colloquial_terms || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="語氣風格" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.tone_style}
                    onChange={(e) => onKolInfoChange?.('tone_style', e.target.value)}
                    placeholder="輸入語氣風格描述"
                    rows={4}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.tone_style || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="常用打字習慣" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.typing_habit}
                    onChange={(e) => onKolInfoChange?.('typing_habit', e.target.value)}
                    placeholder="輸入常用打字習慣"
                    rows={4}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.typing_habit || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="前導故事" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.backstory}
                    onChange={(e) => onKolInfoChange?.('backstory', e.target.value)}
                    placeholder="輸入前導故事"
                    rows={4}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.backstory || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="專長領域" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <Input
                    value={kolInfo.expertise}
                    onChange={(e) => onKolInfoChange?.('expertise', e.target.value)}
                    placeholder="例如: 技術分析,圖表解讀"
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Space wrap>
                    {kolInfo.expertise ? kolInfo.expertise.split(',').map((field, index) => (
                      <Tag key={index} color="blue">
                        {field.trim()}
                      </Tag>
                    )) : <Text type="secondary">無</Text>}
                  </Space>
                )}
              </Card>
            </Col>
          </Row>
        </Panel>

        {/* Prompt 設定 */}
        <Panel 
          header={
            <Space>
              <RobotOutlined />
              <span>Prompt 設定</span>
            </Space>
          } 
          key="prompt"
        >
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card size="small" title="PromptPersona" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.prompt_persona}
                    onChange={(e) => onKolInfoChange?.('prompt_persona', e.target.value)}
                    placeholder="輸入 Prompt Persona"
                    rows={3}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '100px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.prompt_persona || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={24}>
              <Card size="small" title="PromptStyle" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.prompt_style}
                    onChange={(e) => onKolInfoChange?.('prompt_style', e.target.value)}
                    placeholder="輸入 Prompt Style"
                    rows={3}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '100px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.prompt_style || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={24}>
              <Card size="small" title="PromptGuardrails" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.prompt_guardrails}
                    onChange={(e) => onKolInfoChange?.('prompt_guardrails', e.target.value)}
                    placeholder="輸入 Prompt Guardrails"
                    rows={3}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.prompt_guardrails || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={24}>
              <Card size="small" title="PromptSkeleton" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.prompt_skeleton}
                    onChange={(e) => onKolInfoChange?.('prompt_skeleton', e.target.value)}
                    placeholder="輸入 Prompt Skeleton"
                    rows={3}
                    style={{ fontSize: '12px', fontFamily: 'monospace' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px',
                      fontFamily: 'monospace'
                    }}
                  >
                    {kolInfo.prompt_skeleton || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="PromptCTA" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.prompt_cta}
                    onChange={(e) => onKolInfoChange?.('prompt_cta', e.target.value)}
                    placeholder="輸入 Prompt CTA"
                    rows={3}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '80px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.prompt_cta || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="PromptHashtags" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <TextArea
                    value={kolInfo.prompt_hashtags}
                    onChange={(e) => onKolInfoChange?.('prompt_hashtags', e.target.value)}
                    placeholder="輸入 Prompt Hashtags"
                    rows={3}
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Paragraph 
                    style={{ 
                      margin: 0, 
                      fontSize: '12px',
                      maxHeight: '80px',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: '8px',
                      borderRadius: '4px'
                    }}
                  >
                    {kolInfo.prompt_hashtags || '無'}
                  </Paragraph>
                )}
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="簽名" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <Input
                    value={kolInfo.signature}
                    onChange={(e) => onKolInfoChange?.('signature', e.target.value)}
                    placeholder="輸入簽名"
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Text>{kolInfo.signature || '無'}</Text>
                )}
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="表情包" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <Input
                    value={kolInfo.emoji_pack}
                    onChange={(e) => onKolInfoChange?.('emoji_pack', e.target.value)}
                    placeholder="輸入表情包"
                    style={{ fontSize: '12px' }}
                  />
                ) : (
                  <Text style={{ fontSize: '16px' }}>{kolInfo.emoji_pack || '無'}</Text>
                )}
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="模型設定" style={{ marginBottom: '16px' }}>
                {isEditMode ? (
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Input
                      value={kolInfo.model_id}
                      onChange={(e) => onKolInfoChange?.('model_id', e.target.value)}
                      placeholder="模型 ID"
                      style={{ fontSize: '12px' }}
                    />
                    <InputNumber
                      value={kolInfo.model_temp}
                      onChange={(value) => onKolInfoChange?.('model_temp', value)}
                      min={0}
                      max={2}
                      step={0.1}
                      placeholder="溫度"
                      style={{ width: '100%', fontSize: '12px' }}
                    />
                    <InputNumber
                      value={kolInfo.max_tokens}
                      onChange={(value) => onKolInfoChange?.('max_tokens', value)}
                      min={1}
                      max={4000}
                      placeholder="最大 Token"
                      style={{ width: '100%', fontSize: '12px' }}
                    />
                  </Space>
                ) : (
                  <Space direction="vertical" size="small">
                    <Text>模型: {kolInfo.model_id || '無'}</Text>
                    <Text>溫度: {kolInfo.model_temp}</Text>
                    <Text>最大 Token: {kolInfo.max_tokens}</Text>
                  </Space>
                )}
              </Card>
            </Col>
          </Row>
        </Panel>
      </Collapse>
    </Card>
  );
};

export default KOLSettings;
