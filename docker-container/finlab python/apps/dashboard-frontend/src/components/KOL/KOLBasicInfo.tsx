import React from 'react';
import { Card, Row, Col, Statistic, Tag, Descriptions, Space, Input, Select, Switch, InputNumber } from 'antd';
import { 
  UserOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  FileTextOutlined,
  RiseOutlined,
  LikeOutlined,
  MessageOutlined
} from '@ant-design/icons';
import { KOLBasicInfoProps } from '../../types/kol-types';

const { TextArea } = Input;
const { Option } = Select;

const KOLBasicInfo: React.FC<KOLBasicInfoProps> = ({ 
  kolInfo, 
  statistics, 
  loading, 
  error,
  isEditMode = false,
  onKolInfoChange
}) => {
  if (loading) {
    return (
      <Card title="KOL 基本資訊" size="small">
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div>載入中...</div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="KOL 基本資訊" size="small">
        <div style={{ color: '#ff4d4f' }}>載入失敗: {error}</div>
      </Card>
    );
  }

  return (
    <Row gutter={[16, 16]}>
      {/* KOL 基本資料 */}
      <Col span={8}>
        <Card title="KOL 基本資料" size="small">
          <Descriptions column={1} size="small">
            <Descriptions.Item label="暱稱">
              {isEditMode ? (
                <Input
                  value={kolInfo.nickname}
                  onChange={(e) => onKolInfoChange?.('nickname', e.target.value)}
                  placeholder="輸入暱稱"
                />
              ) : (
                <Space>
                  <UserOutlined />
                  {kolInfo.nickname}
                </Space>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Member ID">
              {kolInfo.member_id}
            </Descriptions.Item>
            <Descriptions.Item label="人設">
              {isEditMode ? (
                <Select
                  value={kolInfo.persona}
                  onChange={(value) => onKolInfoChange?.('persona', value)}
                  style={{ width: '100%' }}
                >
                  <Option value="技術派">技術派</Option>
                  <Option value="總經派">總經派</Option>
                  <Option value="新聞派">新聞派</Option>
                  <Option value="籌碼派">籌碼派</Option>
                  <Option value="情緒派">情緒派</Option>
                  <Option value="價值派">價值派</Option>
                </Select>
              ) : (
                <Tag color="blue">{kolInfo.persona}</Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="狀態">
              {isEditMode ? (
                <Select
                  value={kolInfo.status}
                  onChange={(value) => onKolInfoChange?.('status', value)}
                  style={{ width: '100%' }}
                >
                  <Option value="active">啟用</Option>
                  <Option value="inactive">停用</Option>
                </Select>
              ) : (
                <Tag 
                  color={kolInfo.status === 'active' ? 'green' : 'red'}
                  icon={kolInfo.status === 'active' ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
                >
                  {kolInfo.status === 'active' ? '啟用' : '停用'}
                </Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="認領人">
              {isEditMode ? (
                <Input
                  value={kolInfo.owner}
                  onChange={(e) => onKolInfoChange?.('owner', e.target.value)}
                  placeholder="輸入認領人"
                />
              ) : (
                kolInfo.owner
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Email">
              {isEditMode ? (
                <Input
                  value={kolInfo.email}
                  onChange={(e) => onKolInfoChange?.('email', e.target.value)}
                  placeholder="輸入 Email"
                />
              ) : (
                kolInfo.email
              )}
            </Descriptions.Item>
            <Descriptions.Item label="加白名單">
              {isEditMode ? (
                <Switch
                  checked={kolInfo.whitelist}
                  onChange={(checked) => onKolInfoChange?.('whitelist', checked)}
                />
              ) : (
                <Tag color={kolInfo.whitelist ? 'green' : 'red'}>
                  {kolInfo.whitelist ? '是' : '否'}
                </Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="備註">
              {isEditMode ? (
                <TextArea
                  value={kolInfo.notes}
                  onChange={(e) => onKolInfoChange?.('notes', e.target.value)}
                  placeholder="輸入備註"
                  rows={2}
                />
              ) : (
                kolInfo.notes || '-'
              )}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Col>

      {/* 發文設定 */}
      <Col span={8}>
        <Card title="發文設定" size="small">
          <Descriptions column={1} size="small">
            <Descriptions.Item label="發文時間">
              {isEditMode ? (
                <Input
                  value={kolInfo.post_times}
                  onChange={(e) => onKolInfoChange?.('post_times', e.target.value)}
                  placeholder="例如: 08:00,14:30"
                />
              ) : (
                kolInfo.post_times || '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="目標受眾">
              {isEditMode ? (
                <Input
                  value={kolInfo.target_audience}
                  onChange={(e) => onKolInfoChange?.('target_audience', e.target.value)}
                  placeholder="例如: active_traders"
                />
              ) : (
                kolInfo.target_audience || '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="互動閾值">
              {isEditMode ? (
                <InputNumber
                  value={kolInfo.interaction_threshold}
                  onChange={(value) => onKolInfoChange?.('interaction_threshold', value)}
                  min={0}
                  max={1}
                  step={0.1}
                  style={{ width: '100%' }}
                />
              ) : (
                kolInfo.interaction_threshold
              )}
            </Descriptions.Item>
            <Descriptions.Item label="內容類型">
              {isEditMode ? (
                <Select
                  mode="multiple"
                  value={kolInfo.content_types}
                  onChange={(value) => onKolInfoChange?.('content_types', value)}
                  style={{ width: '100%' }}
                  placeholder="選擇內容類型"
                >
                  <Option value="technical">technical</Option>
                  <Option value="chart">chart</Option>
                  <Option value="macro">macro</Option>
                  <Option value="policy">policy</Option>
                  <Option value="news">news</Option>
                  <Option value="trending">trending</Option>
                  <Option value="investment">investment</Option>
                </Select>
              ) : (
                <Space wrap>
                  {(kolInfo.content_types || []).map((type, index) => (
                    <Tag key={index} color="purple">
                      {type.trim()}
                    </Tag>
                  ))}
                </Space>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="專長領域">
              {isEditMode ? (
                <Input
                  value={kolInfo.expertise}
                  onChange={(e) => onKolInfoChange?.('expertise', e.target.value)}
                  placeholder="例如: 技術分析,圖表解讀"
                />
              ) : (
                kolInfo.expertise || '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="數據源">
              {isEditMode ? (
                <Input
                  value={kolInfo.data_source}
                  onChange={(e) => onKolInfoChange?.('data_source', e.target.value)}
                  placeholder="例如: ohlc,indicators"
                />
              ) : (
                kolInfo.data_source || '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="創建時間">
              {kolInfo.created_time || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="最後更新">
              {kolInfo.last_updated || '-'}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Col>

      {/* 統計概覽 */}
      <Col span={8}>
        <Card title="統計概覽" size="small">
          <Row gutter={[8, 8]}>
            <Col span={12}>
              <Statistic
                title="總發文數"
                value={statistics.total_posts}
                prefix={<FileTextOutlined />}
                valueStyle={{ fontSize: '18px' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="已發布"
                value={statistics.published_posts}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ fontSize: '18px', color: '#52c41a' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="草稿"
                value={statistics.draft_posts}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ fontSize: '18px', color: '#faad14' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="平均互動率"
                value={statistics.avg_interaction_rate}
                suffix="%"
                prefix={<RiseOutlined />}
                precision={2}
                valueStyle={{ fontSize: '18px', color: '#1890ff' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="總互動數"
                value={statistics.total_interactions}
                prefix={<LikeOutlined />}
                valueStyle={{ fontSize: '18px' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="平均按讚"
                value={statistics.avg_likes_per_post}
                prefix={<LikeOutlined />}
                precision={1}
                valueStyle={{ fontSize: '18px', color: '#52c41a' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="平均留言"
                value={statistics.avg_comments_per_post}
                prefix={<MessageOutlined />}
                precision={1}
                valueStyle={{ fontSize: '18px', color: '#1890ff' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="最佳表現"
                value={statistics.best_performing_post}
                valueStyle={{ fontSize: '14px', color: '#722ed1' }}
              />
            </Col>
          </Row>
        </Card>
      </Col>
    </Row>
  );
};

export default KOLBasicInfo;
