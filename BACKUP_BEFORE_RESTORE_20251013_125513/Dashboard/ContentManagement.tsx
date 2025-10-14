import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, Row, Col, Table, Tag, Statistic, Tabs, Button, Space, Input, Tooltip, Modal, Typography } from 'antd';
import { 
  UserOutlined, 
  FileTextOutlined, 
  CheckCircleOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import type { ContentManagementData, KOLData } from '../../types';

const { Search } = Input;
const { TabPane } = Tabs;
const { Text, Paragraph } = Typography;

interface ContentManagementProps {
  data: ContentManagementData | null;
  loading: boolean;
  error: string | null;
}

const ContentManagement: React.FC<ContentManagementProps> = ({ data, loading, error }) => {
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  // 顯示 KOL 權重設定詳情
  const showKolWeightSettings = (settings: string) => {
    if (!settings) {
      Modal.info({
        title: 'KOL 權重設定',
        content: '暫無權重設定資料',
      });
      return;
    }

    try {
      const parsedSettings = JSON.parse(settings);
      Modal.info({
        title: 'KOL 權重設定詳情',
        width: 600,
        content: (
          <div>
            <Paragraph>
              <Text strong>發文類型權重：</Text>
            </Paragraph>
            {parsedSettings.post_types && Object.entries(parsedSettings.post_types).map(([key, value]: [string, any]) => (
              <div key={key} style={{ marginBottom: '8px' }}>
                <Tag color="blue">{value.style}</Tag>
                <Text> 權重: {value.weight} - {value.description}</Text>
              </div>
            ))}
            
            <Paragraph style={{ marginTop: '16px' }}>
              <Text strong>內容長度權重：</Text>
            </Paragraph>
            {parsedSettings.content_lengths && Object.entries(parsedSettings.content_lengths).map(([key, value]: [string, any]) => (
              <div key={key} style={{ marginBottom: '8px' }}>
                <Tag color="green">{key}</Tag>
                <Text> 權重: {value.weight} - {value.description}</Text>
              </div>
            ))}
            
            {parsedSettings.version && (
              <Paragraph style={{ marginTop: '16px' }}>
                <Text strong>設定版本：</Text> {parsedSettings.version}
              </Paragraph>
            )}
          </div>
        ),
      });
    } catch (e) {
      Modal.info({
        title: 'KOL 權重設定',
        content: (
          <div>
            <Text>原始設定資料：</Text>
            <Paragraph code style={{ marginTop: '8px' }}>
              {settings}
            </Paragraph>
          </div>
        ),
      });
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div>載入內容管理數據中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ margin: '16px' }}>
        <div>載入失敗: {error}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ margin: '16px' }}>
        <div>暫無內容管理數據</div>
      </div>
    );
  }

  const { kol_list, post_list, statistics } = data;

  // KOL 表格列定義
  const kolColumns = [
    {
      title: '序號',
      dataIndex: 'serial',
      key: 'serial',
      width: 80,
    },
    {
      title: '暱稱',
      dataIndex: 'nickname',
      key: 'nickname',
      width: 120,
      render: (nickname: string, record: any) => (
        <Space>
          <span>{nickname}</span>
          <Tooltip title="查看 KOL 詳情">
            <Button
              type="link"
              size="small"
              icon={<UserOutlined />}
              onClick={() => navigate(`/content-management/kols/${record.member_id}`)}
            />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: 'Member ID',
      dataIndex: 'member_id',
      key: 'member_id',
      width: 120,
      render: (memberId: string) => (
        <Space>
          <span>{memberId}</span>
          <Tooltip title="查看會員主頁">
            <Button
              type="link"
              size="small"
              icon={<InfoCircleOutlined />}
              onClick={() => window.open(`https://www.cmoney.tw/forum/user/${memberId}`, '_blank')}
            />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '人設',
      dataIndex: 'persona',
      key: 'persona',
      width: 100,
      render: (persona: string) => (
        <Tag color="blue">{persona}</Tag>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === '啟用' ? 'green' : 'red'}>
          {status === '啟用' ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
          {status}
        </Tag>
      ),
    },
    {
      title: '內容類型',
      dataIndex: 'content_type',
      key: 'content_type',
      width: 150,
      render: (contentType: string) => (
        <div>
          {contentType.split(',').map((type, index) => (
            <Tag key={index} color="purple" style={{ marginBottom: '2px' }}>
              {type.trim()}
            </Tag>
          ))}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: any) => (
        <Space>
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => navigate(`/content-management/posts/${record.post_id}`)}
          >
            查看詳情
          </Button>
        </Space>
      ),
    },
  ];

  // 貼文表格列定義
  const postColumns = [
    {
      title: '貼文 ID',
      dataIndex: 'post_id',
      key: 'post_id',
      width: 120,
      render: (postId: string, record: any) => (
        <Space>
          <span>{postId}</span>
          {record.platform_post_url && (
            <Tooltip title="查看文章">
              <Button
                type="link"
                size="small"
                icon={<InfoCircleOutlined />}
                onClick={() => window.open(record.platform_post_url, '_blank')}
              />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: 'KOL',
      dataIndex: 'kol_nickname',
      key: 'kol_nickname',
      width: 100,
    },
    {
      title: '人設',
      dataIndex: 'persona',
      key: 'persona',
      width: 100,
      render: (persona: string) => (
        <Tag color="blue">{persona}</Tag>
      ),
    },
    {
      title: '話題標題',
      dataIndex: 'topic_title',
      key: 'topic_title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '內容',
      dataIndex: 'content',
      key: 'content',
      width: 300,
      ellipsis: true,
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === '已發布' ? 'green' : 'orange'}>
          {status === '已發布' ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
          {status}
        </Tag>
      ),
    },
    {
      title: '發文時間',
      dataIndex: 'post_time',
      key: 'post_time',
      width: 150,
      render: (time: string) => time ? new Date(time).toLocaleString('zh-TW') : '-',
    },
    {
      title: '發文類型',
      dataIndex: 'post_type',
      key: 'post_type',
      width: 100,
      render: (type: string) => {
        if (!type) return '-';
        const typeMap: { [key: string]: { color: string; text: string } } = {
          'question': { color: 'blue', text: '疑問型' },
          'opinion': { color: 'green', text: '觀點型' },
          '疑問型': { color: 'blue', text: '疑問型' },
          '發表觀點型': { color: 'green', text: '觀點型' }
        };
        const config = typeMap[type] || { color: 'default', text: type };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '文章長度',
      dataIndex: 'content_length',
      key: 'content_length',
      width: 100,
      render: (length: string) => {
        if (!length) return '-';
        const lengthMap: { [key: string]: { color: string; text: string } } = {
          'short': { color: 'orange', text: '短' },
          'medium': { color: 'blue', text: '中' },
          'long': { color: 'purple', text: '長' },
          '短': { color: 'orange', text: '短' },
          '中': { color: 'blue', text: '中' },
          '長': { color: 'purple', text: '長' }
        };
        const config = lengthMap[length] || { color: 'default', text: length };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '生成時間',
      dataIndex: 'content_generation_time',
      key: 'content_generation_time',
      width: 150,
      render: (time: string) => time ? new Date(time).toLocaleString('zh-TW') : '-',
    },
    {
      title: '設定版本',
      dataIndex: 'kol_settings_version',
      key: 'kol_settings_version',
      width: 100,
      render: (version: string) => version || '-',
    },
    {
      title: '權重設定',
      dataIndex: 'kol_weight_settings',
      key: 'kol_weight_settings',
      width: 100,
      render: (settings: string) => {
        if (!settings) return '-';
        return (
          <Tooltip title="點擊查看權重設定詳情">
            <Button 
              type="link" 
              size="small" 
              icon={<InfoCircleOutlined />}
              onClick={() => showKolWeightSettings(settings)}
            >
              查看
            </Button>
          </Tooltip>
        );
      },
    },
    {
      title: 'KOL 設定詳情',
      key: 'kol_settings_detail',
      width: 120,
      render: (_: any, record: any) => (
        <Tooltip title="點擊查看 KOL 完整設定">
          <Button 
            type="link" 
            size="small" 
            icon={<UserOutlined />}
            onClick={() => navigate(`/content-management/kols/${record.kol_id}`)}
          >
            查看設定
          </Button>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: () => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />}>
            查看
          </Button>
        </Space>
      ),
    },
  ];

  // 過濾數據
  const filteredKOLs = kol_list.filter(kol =>
    kol.nickname.toLowerCase().includes(searchText.toLowerCase()) ||
    kol.member_id.includes(searchText) ||
    kol.persona.toLowerCase().includes(searchText.toLowerCase())
  );

  const filteredPosts = post_list.filter(post =>
    post.kol_nickname.toLowerCase().includes(searchText.toLowerCase()) ||
    post.topic_title.toLowerCase().includes(searchText.toLowerCase()) ||
    post.content.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        {/* 統計概覽 */}
        <Col span={24}>
          <Card title="內容統計概覽" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="總 KOL 數"
                  value={statistics.kol_stats.total}
                  prefix={<UserOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="活躍 KOL 數"
                  value={statistics.kol_stats.active}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="總貼文數"
                  value={statistics.post_stats.total}
                  prefix={<FileTextOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="已發布貼文"
                  value={statistics.post_stats.published}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 搜索框 */}
        <Col span={24}>
          <Card size="small">
            <Search
              placeholder="搜索 KOL 或貼文..."
              allowClear
              enterButton="搜索"
              size="large"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ maxWidth: 400 }}
            />
          </Card>
        </Col>

        {/* 詳細數據 */}
        <Col span={24}>
          <Card size="small">
            <Tabs 
              defaultActiveKey={
                location.pathname.includes('/kols') ? 'kols' : 
                location.pathname.includes('/posts') ? 'posts' : 'kols'
              }
            >
              <TabPane tab={`KOL 管理 (${filteredKOLs.length})`} key="kols">
                <Table
                  columns={kolColumns}
                  dataSource={filteredKOLs}
                  rowKey="member_id"
                  size="small"
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total, range) =>
                      `第 ${range[0]}-${range[1]} 項，共 ${total} 項`,
                  }}
                />
              </TabPane>
              
              <TabPane tab={`貼文管理 (${filteredPosts.length})`} key="posts">
                <Table
                  columns={postColumns}
                  dataSource={filteredPosts}
                  rowKey="post_id"
                  size="small"
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total, range) =>
                      `第 ${range[0]}-${range[1]} 項，共 ${total} 項`,
                  }}
                />
              </TabPane>
            </Tabs>
          </Card>
        </Col>

        {/* 人設分布 */}
        <Col span={12}>
          <Card title="KOL 人設分布" size="small">
            <Row gutter={[8, 8]}>
              {Object.entries(statistics.kol_stats.by_persona).map(([persona, count]) => (
                <Col span={12} key={persona}>
                  <div style={{ textAlign: 'center', padding: '8px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1890ff' }}>
                      {count}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {persona}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* KOL 貼文分布 */}
        <Col span={12}>
          <Card title="KOL 貼文分布" size="small">
            <Row gutter={[8, 8]}>
              {Object.entries(statistics.post_stats.by_kol).map(([kol, count]) => (
                <Col span={12} key={kol}>
                  <div style={{ textAlign: 'center', padding: '8px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#52c41a' }}>
                      {count}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {kol}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ContentManagement;
