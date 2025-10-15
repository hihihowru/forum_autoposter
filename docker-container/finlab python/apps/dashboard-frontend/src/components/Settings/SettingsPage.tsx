import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Text } = Typography;

const SettingsPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>系統設置</Title>
        <Text type="secondary">系統設置功能開發中...</Text>
      </Card>
    </div>
  );
};

export default SettingsPage;
