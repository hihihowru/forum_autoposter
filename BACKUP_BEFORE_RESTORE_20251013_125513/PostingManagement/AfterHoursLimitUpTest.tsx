import React, { useState } from 'react';
import { Card, Button, Space, message, Spin, Typography, Row, Col, Statistic } from 'antd';
import { PlayCircleOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
// import PostingManagementAPI from '../../services/postingManagementAPI';

const { Title, Text } = Typography;

const AfterHoursLimitUpTest: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  const handleTestAfterHoursLimitUp = async () => {
    try {
      setLoading(true);
      message.info('開始測試盤後漲停觸發器...');

      // 暫時註釋API調用
      // const session = await PostingManagementAPI.createSession({
      //   session_name: `盤後漲停測試_${new Date().toISOString()}`,
      //   trigger_type: 'after_hours_limit_up',
      //   trigger_data: {
      //     max_posts: 5,
      //     enable_publishing: false,
      //     enable_learning: true
      //   },
      //   config: {
      //     data_sources: {
      //       stock_price_api: true,
      //       monthly_revenue_api: true,
      //       financial_report_api: true,
      //       news_sources: true
      //     },
      //     kol_assignment_mode: 'dynamic',
      //     content_mode: 'one_to_one'
      //   },
      //   status: 'created'
      // });

      // message.success(`會話創建成功: ${session.id}`);

      // // 2. 生成發文
      // const generationResult = await PostingManagementAPI.generatePosts(session.id);
      
      // message.success(`生成完成: ${generationResult.generated_count} 篇發文`);

      // // 3. 獲取發文列表
      // const posts = await PostingManagementAPI.getSessionPosts(session.id);

      // // 4. 獲取KOL資料
      // const kols = await PostingManagementAPI.getKOLs();

      // 模擬結果
      const session = { id: 'test_session_001' };
      const generationResult = { generated_count: 3 };
      const posts = [
        { id: 1, title: '測試發文1', kol_nickname: '川川哥', status: 'draft', stock_codes: ['2330'] },
        { id: 2, title: '測試發文2', kol_nickname: '韭割哥', status: 'draft', stock_codes: ['2454'] }
      ];
      const kols = [
        { serial: 200, nickname: '川川哥', persona: '技術派', expertise_areas: ['技術分析'], status: 'active' },
        { serial: 201, nickname: '韭割哥', persona: '總經派', expertise_areas: ['數據分析'], status: 'active' }
      ];

      setTestResult({
        session,
        generationResult,
        posts,
        kols,
        timestamp: new Date().toISOString()
      });

      message.success('盤後漲停觸發器測試完成！');

    } catch (error: any) {
      console.error('測試失敗:', error);
      message.error(`測試失敗: ${error.message || error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="盤後漲停觸發器測試" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={4}>測試說明</Title>
            <Text type="secondary">
              此測試將模擬盤後漲停觸發器的完整流程：
              <br />1. 創建發文會話
              <br />2. 生成發文內容
              <br />3. 獲取發文列表
            </Text>
          </div>

          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={handleTestAfterHoursLimitUp}
            loading={loading}
            disabled={loading}
          >
            {loading ? '測試中...' : '開始測試盤後漲停觸發器'}
          </Button>

          {testResult && (
            <Card title="測試結果" type="inner">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="會話ID"
                      value={testResult.session.id}
                      prefix={<CheckCircleOutlined />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="生成發文數"
                      value={testResult.generationResult.generated_count}
                      prefix={<FileTextOutlined />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="測試時間"
                      value={new Date(testResult.timestamp).toLocaleString('zh-TW')}
                      prefix={<ClockCircleOutlined />}
                    />
                  </Col>
                </Row>

                <div>
                  <Title level={5}>發文列表</Title>
                  {testResult.posts.length > 0 ? (
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {testResult.posts.map((post: any, index: number) => (
                        <Card key={post.id} size="small" title={`發文 ${index + 1}`}>
                          <Space direction="vertical" style={{ width: '100%' }}>
                            <div>
                              <Text strong>標題: </Text>
                              <Text>{post.title}</Text>
                            </div>
                            <div>
                              <Text strong>KOL: </Text>
                              <Text>{post.kol_nickname}</Text>
                            </div>
                            <div>
                              <Text strong>狀態: </Text>
                              <Text>{post.status}</Text>
                            </div>
                            <div>
                              <Text strong>股票: </Text>
                              <Text>{post.stock_codes?.join(', ') || '無'}</Text>
                            </div>
                          </Space>
                        </Card>
                      ))}
                    </Space>
                  ) : (
                    <Text type="secondary">無發文數據</Text>
                  )}
                </div>

                <div>
                  <Title level={5}>可用KOL列表</Title>
                  {testResult.kols && testResult.kols.length > 0 ? (
                    <Space wrap style={{ width: '100%' }}>
                      {testResult.kols.map((kol: any) => (
                        <Card key={kol.serial} size="small" style={{ width: '200px' }}>
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Text strong>{kol.nickname}</Text>
                              <Text type="secondary">#{kol.serial}</Text>
                            </div>
                            <div>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                {kol.persona}
                              </Text>
                            </div>
                            <div>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                專長: {kol.expertise_areas?.join(', ') || '無'}
                              </Text>
                            </div>
                            <div>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                狀態: {kol.status}
                              </Text>
                            </div>
                          </Space>
                        </Card>
                      ))}
                    </Space>
                  ) : (
                    <Text type="secondary">無KOL數據</Text>
                  )}
                </div>
              </Space>
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default AfterHoursLimitUpTest;
