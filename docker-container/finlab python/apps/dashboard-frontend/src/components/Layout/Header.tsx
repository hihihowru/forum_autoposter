import React from 'react';
import { Layout, Button, Space, Typography, Badge, Tooltip } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ReloadOutlined,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

interface HeaderProps {
  collapsed: boolean;
  onToggle: () => void;
  onRefresh: () => void;
  lastUpdated?: string;
  loading?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  collapsed,
  onToggle,
  onRefresh,
  lastUpdated,
  loading = false,
}) => {
  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        height: '64px',
        lineHeight: '64px',
        position: 'fixed',
        top: 0,
        right: 0,
        left: collapsed ? '80px' : '280px',
        zIndex: 9,
        transition: 'left 0.2s',
      }}
    >
      <Space align="center" style={{ height: '100%' }}>
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={onToggle}
          style={{
            fontSize: '16px',
            width: 40,
            height: 40,
          }}
        />

        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minWidth: 0 }}>
          <Text strong style={{ fontSize: '18px', lineHeight: '1.2' }}>
            KOL 系統儀表板
          </Text>
          {lastUpdated && (
            <Text type="secondary" style={{ fontSize: '12px', lineHeight: '1.2' }}>
              更新: {dayjs(lastUpdated).format('MM-DD HH:mm')}
            </Text>
          )}
        </div>
      </Space>

      <Space size="small" style={{ flexShrink: 0, height: '100%', alignItems: 'center' }}>
        <Tooltip title="刷新數據">
          <Button
            type="text"
            icon={<ReloadOutlined spin={loading} />}
            onClick={onRefresh}
            loading={loading}
            style={{
              fontSize: '16px',
              width: 40,
              height: 40,
            }}
          />
        </Tooltip>

        <Tooltip title="通知">
          <Badge count={0} size="small">
            <Button
              type="text"
              icon={<BellOutlined />}
              style={{
                fontSize: '16px',
                width: 40,
                height: 40,
              }}
            />
          </Badge>
        </Tooltip>

        <Tooltip title="設置">
          <Button
            type="text"
            icon={<SettingOutlined />}
            style={{
              fontSize: '16px',
              width: 40,
              height: 40,
            }}
          />
        </Tooltip>

        <Tooltip title="用戶">
          <Button
            type="text"
            icon={<UserOutlined />}
            style={{
              fontSize: '16px',
              width: 40,
              height: 40,
            }}
          />
        </Tooltip>
      </Space>
    </AntHeader>
  );
};

export default Header;
