import React from 'react';
import { Card, Typography, Button } from 'antd';

const { Title, Text } = Typography;

const TestPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <Card title="測試頁面">
        <Space direction="vertical" size="large">
          <div>
            <Title level={2}>發文管理系統測試</Title>
            <Text>如果你能看到這個頁面，說明React組件正常運作</Text>
          </div>
          
          <div>
            <Title level={3}>KOL資料整合測試</Title>
            <Text>KOL資料已經成功整合到系統中</Text>
          </div>
          
          <div>
            <Title level={3}>觸發器測試</Title>
            <Text>盤後漲停觸發器已經準備就緒</Text>
          </div>
          
          <Button type="primary" size="large">
            測試按鈕
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default TestPage;
