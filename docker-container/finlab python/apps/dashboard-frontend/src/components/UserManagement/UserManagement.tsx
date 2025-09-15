import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Text } = Typography;

const UserManagement: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>用戶管理</Title>
        <Text type="secondary">用戶管理功能開發中...</Text>
      </Card>
    </div>
  );
};

export default UserManagement;
