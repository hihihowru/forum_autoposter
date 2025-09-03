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
        padding: '0 16px',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        minHeight: '64px',
        flexWrap: 'nowrap',
      }}
    >
      <Space>
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
        
        <div style={{ minWidth: 0, flex: 1 }}>
          <Text strong style={{ fontSize: '18px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            KOL 系統儀表板
          </Text>
          {lastUpdated && (
            <div style={{ fontSize: '12px', color: '#666', marginTop: '2px', whiteSpace: 'nowrap' }}>
              更新: {dayjs(lastUpdated).format('MM-DD HH:mm')}
            </div>
          )}
        </div>
      </Space>

      <Space size="small" style={{ flexShrink: 0 }}>
        <Tooltip title="刷新數據">
          <Button
            type="text"
            icon={<ReloadOutlined />}
            onClick={onRefresh}
            loading={loading}
            style={{
              fontSize: '16px',
              width: 36,
              height: 36,
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
                width: 36,
                height: 36,
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
              width: 36,
              height: 36,
            }}
          />
        </Tooltip>
        
        <Tooltip title="用戶">
          <Button
            type="text"
            icon={<UserOutlined />}
            style={{
              fontSize: '16px',
              width: 36,
              height: 36,
            }}
          />
        </Tooltip>
      </Space>
    </AntHeader>
  );
};

export default Header;
