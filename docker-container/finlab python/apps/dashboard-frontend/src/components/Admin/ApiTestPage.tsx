import React, { useState } from 'react';
import {
  Card,
  Typography,
  Row,
  Col,
  Button,
  Space,
  Tag,
  Collapse,
  Input,
  Select,
  message,
  Spin,
  Divider,
  Alert
} from 'antd';
import {
  ApiOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const { TextArea } = Input;
const { Option } = Select;

interface ApiEndpoint {
  method: string;
  path: string;
  description: string;
  category: string;
}

interface TestResult {
  endpoint: string;
  status: 'success' | 'error' | 'loading';
  statusCode?: number;
  data?: any;
  error?: string;
  responseTime?: number;
}

const ApiTestPage: React.FC = () => {
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
  const [customEndpoint, setCustomEndpoint] = useState('');
  const [customMethod, setCustomMethod] = useState('GET');
  const [customBody, setCustomBody] = useState('');
  const [testing, setTesting] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

  // Define all your API endpoints
  const apiEndpoints: ApiEndpoint[] = [
    // System Health & Database
    { method: 'GET', path: '/api/health', description: 'Check API health status', category: 'System' },
    { method: 'GET', path: '/api/database/test', description: 'Test database connection and tables', category: 'System' },

    // KOL Management
    { method: 'GET', path: '/api/kol/list', description: 'Get all KOL profiles', category: 'KOL Management' },

    // Schedule Management
    { method: 'GET', path: '/api/schedule/tasks', description: 'Get schedule tasks', category: 'Schedule Management' },
    { method: 'GET', path: '/api/schedule/daily-stats', description: 'Get daily statistics', category: 'Schedule Management' },
    { method: 'GET', path: '/api/schedule/scheduler/status', description: 'Get scheduler status', category: 'Schedule Management' },

    // Posts Management
    { method: 'GET', path: '/api/posts', description: 'Get all posts', category: 'Posts Management' },

    // After Hours Triggers (6 endpoints)
    { method: 'GET', path: '/api/after_hours_limit_up', description: 'After-hours limit up stocks', category: 'After Hours Triggers' },
    { method: 'GET', path: '/api/after_hours_limit_down', description: 'After-hours limit down stocks', category: 'After Hours Triggers' },
    { method: 'GET', path: '/api/after_hours_volume_amount_high', description: 'After-hours high volume (amount)', category: 'After Hours Triggers' },
    { method: 'GET', path: '/api/after_hours_volume_amount_low', description: 'After-hours low volume (amount)', category: 'After Hours Triggers' },
    { method: 'GET', path: '/api/after_hours_volume_change_rate_high', description: 'After-hours high volume change rate', category: 'After Hours Triggers' },
    { method: 'GET', path: '/api/after_hours_volume_change_rate_low', description: 'After-hours low volume change rate', category: 'After Hours Triggers' },

    // Intraday Triggers (6 separate endpoints)
    { method: 'GET', path: '/api/intraday/gainers-by-amount', description: '漲幅排序+成交額', category: 'Intraday Triggers' },
    { method: 'GET', path: '/api/intraday/volume-leaders', description: '成交量排序', category: 'Intraday Triggers' },
    { method: 'GET', path: '/api/intraday/amount-leaders', description: '成交額排序', category: 'Intraday Triggers' },
    { method: 'GET', path: '/api/intraday/limit-down', description: '跌停篩選', category: 'Intraday Triggers' },
    { method: 'GET', path: '/api/intraday/limit-up', description: '漲停篩選', category: 'Intraday Triggers' },
    { method: 'GET', path: '/api/intraday/limit-down-by-amount', description: '跌停篩選+成交額', category: 'Intraday Triggers' },

    // Dashboard
    { method: 'GET', path: '/api/dashboard/system-monitoring', description: 'System monitoring data', category: 'Dashboard' },
    { method: 'GET', path: '/api/dashboard/content-management', description: 'Content management data', category: 'Dashboard' },
    { method: 'GET', path: '/api/dashboard/interaction-analysis', description: 'Interaction analysis data', category: 'Dashboard' },

    // Stock & Industry Data
    { method: 'GET', path: '/api/industries', description: 'Get all industries', category: 'Stock Data' },
    { method: 'GET', path: '/api/stocks_by_industry', description: 'Get stocks by industry', category: 'Stock Data' },
    { method: 'GET', path: '/api/get_ohlc', description: 'Get OHLC data', category: 'Stock Data' },
    { method: 'GET', path: '/api/stock_mapping.json', description: 'Get stock mapping', category: 'Stock Data' },

    // Content Generation
    { method: 'GET', path: '/api/trending', description: 'Get trending topics', category: 'Content' },
    { method: 'GET', path: '/api/extract-keywords', description: 'Extract keywords', category: 'Content' },
    { method: 'GET', path: '/api/search-stocks-by-keywords', description: 'Search stocks by keywords', category: 'Content' },
    { method: 'GET', path: '/api/analyze-topic', description: 'Analyze topic', category: 'Content' },
    { method: 'GET', path: '/api/generate-content', description: 'Generate content', category: 'Content' },
  ];

  const testEndpoint = async (endpoint: ApiEndpoint) => {
    const key = `${endpoint.method}-${endpoint.path}`;

    setTestResults(prev => ({
      ...prev,
      [key]: { endpoint: endpoint.path, status: 'loading' }
    }));

    const startTime = Date.now();

    try {
      const response = await axios({
        method: endpoint.method.toLowerCase(),
        url: `${API_BASE_URL}${endpoint.path}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      });

      const responseTime = Date.now() - startTime;

      setTestResults(prev => ({
        ...prev,
        [key]: {
          endpoint: endpoint.path,
          status: 'success',
          statusCode: response.status,
          data: response.data,
          responseTime
        }
      }));

      message.success(`${endpoint.path} - Success (${responseTime}ms)`);
    } catch (error: any) {
      const responseTime = Date.now() - startTime;

      setTestResults(prev => ({
        ...prev,
        [key]: {
          endpoint: endpoint.path,
          status: 'error',
          statusCode: error.response?.status,
          error: error.message,
          data: error.response?.data,
          responseTime
        }
      }));

      message.error(`${endpoint.path} - Error: ${error.message}`);
    }
  };

  const testAllEndpoints = async () => {
    setTesting(true);
    message.info('Testing all endpoints...');

    for (const endpoint of apiEndpoints) {
      await testEndpoint(endpoint);
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    setTesting(false);
    message.success('All endpoints tested!');
  };

  const testCustomEndpoint = async () => {
    if (!customEndpoint) {
      message.warning('Please enter an endpoint');
      return;
    }

    const key = `custom-${customMethod}-${customEndpoint}`;

    setTestResults(prev => ({
      ...prev,
      [key]: { endpoint: customEndpoint, status: 'loading' }
    }));

    const startTime = Date.now();

    try {
      let body = undefined;
      if (customBody && (customMethod === 'POST' || customMethod === 'PUT' || customMethod === 'PATCH')) {
        body = JSON.parse(customBody);
      }

      const response = await axios({
        method: customMethod.toLowerCase(),
        url: `${API_BASE_URL}${customEndpoint}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        data: body
      });

      const responseTime = Date.now() - startTime;

      setTestResults(prev => ({
        ...prev,
        [key]: {
          endpoint: customEndpoint,
          status: 'success',
          statusCode: response.status,
          data: response.data,
          responseTime
        }
      }));

      message.success(`Custom request - Success (${responseTime}ms)`);
    } catch (error: any) {
      const responseTime = Date.now() - startTime;

      setTestResults(prev => ({
        ...prev,
        [key]: {
          endpoint: customEndpoint,
          status: 'error',
          statusCode: error.response?.status,
          error: error.message,
          data: error.response?.data,
          responseTime
        }
      }));

      message.error(`Custom request - Error: ${error.message}`);
    }
  };

  const clearResults = () => {
    setTestResults({});
    message.info('Results cleared');
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'loading':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
    }
  };

  const getStatusTag = (statusCode?: number) => {
    if (!statusCode) return null;

    if (statusCode >= 200 && statusCode < 300) {
      return <Tag color="success">{statusCode}</Tag>;
    } else if (statusCode >= 400 && statusCode < 500) {
      return <Tag color="warning">{statusCode}</Tag>;
    } else if (statusCode >= 500) {
      return <Tag color="error">{statusCode}</Tag>;
    }
    return <Tag>{statusCode}</Tag>;
  };

  // Group endpoints by category
  const groupedEndpoints = apiEndpoints.reduce((acc, endpoint) => {
    if (!acc[endpoint.category]) {
      acc[endpoint.category] = [];
    }
    acc[endpoint.category].push(endpoint);
    return acc;
  }, {} as Record<string, ApiEndpoint[]>);

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Card>
        <Title level={2}>
          <ApiOutlined /> API Documentation
        </Title>
        <Alert
          message="Swagger UI Available"
          description={
            <div>
              <p>Visit the official <strong>Swagger UI</strong> for interactive API documentation:</p>
              <p>
                <a
                  href="https://forumautoposter-production.up.railway.app/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: '16px', fontWeight: 'bold' }}
                >
                  https://forumautoposter-production.up.railway.app/docs
                </a>
              </p>
              <p>You can test all API endpoints interactively with Swagger UI.</p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
        <Paragraph>
          Quick test endpoints below. Current API Base: <Tag color="blue">{API_BASE_URL || 'Vercel Proxy'}</Tag>
        </Paragraph>

        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={testAllEndpoints}
            loading={testing}
          >
            Test All Endpoints
          </Button>
          <Button onClick={clearResults}>Clear Results</Button>
        </Space>

        <Divider />

        {/* Custom Endpoint Tester */}
        <Card title="Custom Endpoint Test" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={4}>
              <Select
                value={customMethod}
                onChange={setCustomMethod}
                style={{ width: '100%' }}
              >
                <Option value="GET">GET</Option>
                <Option value="POST">POST</Option>
                <Option value="PUT">PUT</Option>
                <Option value="DELETE">DELETE</Option>
                <Option value="PATCH">PATCH</Option>
              </Select>
            </Col>
            <Col span={12}>
              <Input
                placeholder="/api/your-endpoint"
                value={customEndpoint}
                onChange={(e) => setCustomEndpoint(e.target.value)}
              />
            </Col>
            <Col span={8}>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={testCustomEndpoint}
              >
                Test
              </Button>
            </Col>
          </Row>
          {(customMethod === 'POST' || customMethod === 'PUT' || customMethod === 'PATCH') && (
            <div style={{ marginTop: 16 }}>
              <TextArea
                placeholder='{"key": "value"}'
                value={customBody}
                onChange={(e) => setCustomBody(e.target.value)}
                rows={4}
              />
            </div>
          )}
        </Card>

        {/* Endpoint Tests by Category */}
        {Object.entries(groupedEndpoints).map(([category, endpoints]) => (
          <Card
            key={category}
            title={category}
            style={{ marginBottom: 16 }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              {endpoints.map(endpoint => {
                const key = `${endpoint.method}-${endpoint.path}`;
                const result = testResults[key];

                return (
                  <Card
                    key={key}
                    size="small"
                    style={{
                      borderLeft: result?.status === 'success' ? '4px solid #52c41a' :
                                 result?.status === 'error' ? '4px solid #ff4d4f' :
                                 '4px solid #d9d9d9'
                    }}
                  >
                    <Row align="middle" gutter={16}>
                      <Col span={1}>
                        {result && getStatusIcon(result.status)}
                      </Col>
                      <Col span={2}>
                        <Tag color={endpoint.method === 'GET' ? 'blue' : 'green'}>
                          {endpoint.method}
                        </Tag>
                      </Col>
                      <Col span={8}>
                        <Text code>{endpoint.path}</Text>
                      </Col>
                      <Col span={6}>
                        <Text type="secondary">{endpoint.description}</Text>
                      </Col>
                      <Col span={3}>
                        {result && (
                          <>
                            {getStatusTag(result.statusCode)}
                            {result.responseTime && (
                              <Tag>{result.responseTime}ms</Tag>
                            )}
                          </>
                        )}
                      </Col>
                      <Col span={4}>
                        <Button
                          size="small"
                          icon={<PlayCircleOutlined />}
                          onClick={() => testEndpoint(endpoint)}
                        >
                          Test
                        </Button>
                      </Col>
                    </Row>

                    {result && result.status !== 'loading' && (
                      <Collapse ghost style={{ marginTop: 8 }}>
                        <Panel header="View Response" key="1">
                          {result.error && (
                            <Alert
                              message="Error"
                              description={result.error}
                              type="error"
                              showIcon
                              style={{ marginBottom: 8 }}
                            />
                          )}
                          <pre style={{
                            background: '#f5f5f5',
                            padding: 12,
                            borderRadius: 4,
                            maxHeight: 300,
                            overflow: 'auto'
                          }}>
                            {JSON.stringify(result.data, null, 2)}
                          </pre>
                        </Panel>
                      </Collapse>
                    )}
                  </Card>
                );
              })}
            </Space>
          </Card>
        ))}
      </Card>
    </div>
  );
};

export default ApiTestPage;
