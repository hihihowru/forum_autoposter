import React from 'react';
import { Layout, Menu, Typography, Space } from 'antd';
import {
  DashboardOutlined,
  MonitorOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  ReloadOutlined,
  EditOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  PlayCircleOutlined,
  SendOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
// import type { MenuItem } from '../../types';

const { Sider } = Layout;
const { Title } = Typography;

interface SidebarProps {
  collapsed: boolean;
  onRefresh: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onRefresh }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      label: '儀表板總覽',
      icon: <DashboardOutlined />,
    },
    {
      key: 'system-monitoring',
      label: '系統監控',
      icon: <MonitorOutlined />,
      children: [
        {
          key: '/system-monitoring',
          label: '系統狀態',
        },
        {
          key: '/system-monitoring/services',
          label: '微服務監控',
        },
        {
          key: '/system-monitoring/tasks',
          label: '任務執行',
        },
      ],
    },
    {
      key: 'content-management',
      label: '內容管理',
      icon: <FileTextOutlined />,
      children: [
        {
          key: '/content-management',
          label: '內容總覽',
        },
        {
          key: '/content-management/kols',
          label: 'KOL 管理',
        },
        {
          key: '/content-management/posts',
          label: '貼文管理',
        },
      ],
    },
    {
      key: 'posting-management',
      label: '發文管理',
      icon: <EditOutlined />,
      children: [
        {
          key: '/posting-management',
          label: '發文總覽',
        },
        {
          key: '/posting-management/dashboard',
          label: '發文儀表板',
        },
        {
          key: '/posting-management/generator',
          label: '發文生成器',
        },
        {
          key: '/posting-management/review',
          label: '發文審核',
        },
        {
          key: '/posting-management/published',
          label: '已發布貼文',
          icon: <SendOutlined />,
        },
        {
          key: '/posting-management/test-after-hours',
          label: '盤後漲停測試',
        },
        {
          key: '/posting-management/batch-history',
          label: '批次歷史',
          icon: <CheckCircleOutlined />,
        },
        {
          key: '/posting-management/schedule',
          label: '排程管理',
          icon: <PlayCircleOutlined />,
        },
        {
          key: '/posting-management/self-learning',
          label: '自我學習',
          icon: <RocketOutlined />,
        },
        {
          key: '/posting-management/interaction-analysis',
          label: '互動分析',
          icon: <BarChartOutlined />,
        },
        {
          key: '/posting-management/performance-analysis',
          label: '成效分析',
          icon: <TrophyOutlined />,
        },
        {
          key: '/posting-management/manual-posting',
          label: '手動發文',
          icon: <EditOutlined />,
        },
      ],
    },
    {
      key: 'interaction-analysis',
      label: '互動分析',
      icon: <BarChartOutlined />,
      children: [
        {
          key: '/interaction-analysis',
          label: '互動總覽',
        },
        {
          key: '/interaction-analysis/features',
          label: '內容特徵分析',
        },
        {
          key: '/interaction-analysis/1hr',
          label: '1小時數據',
        },
        {
          key: '/interaction-analysis/1day',
          label: '1日數據',
        },
        {
          key: '/interaction-analysis/7days',
          label: '7日數據',
        },
      ],
    },
    {
      key: 'system-settings',
      label: '系統設置',
      icon: <SettingOutlined />,
      children: [
        {
          key: '/settings',
          label: '基本設置',
        },
        {
          key: '/settings/api',
          label: 'API 設置',
        },
        {
          key: '/settings/data',
          label: '數據源設置',
        },
      ],
    },
    {
      key: 'user-management',
      label: '用戶管理',
      icon: <UserOutlined />,
      children: [
        {
          key: '/users',
          label: '用戶列表',
        },
        {
          key: '/users/roles',
          label: '角色權限',
        },
      ],
    }
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const getSelectedKeys = () => {
    const path = location.pathname;
    if (path === '/') return ['/'];
    
    // 找到匹配的菜單項
    for (const item of menuItems) {
      if (item.children) {
        for (const child of item.children) {
          if (child.key === path) {
            return [child.key];
          }
        }
      } else if (item.key === path) {
        return [item.key];
      }
    }
    
    return [];
  };

  const getOpenKeys = () => {
    const path = location.pathname;
    const openKeys: string[] = [];
    
    for (const item of menuItems) {
      if (item.children) {
        for (const child of item.children) {
          if (child.key === path) {
            openKeys.push(item.key);
            break;
          }
        }
      }
    }
    
    return openKeys;
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={collapsed}
      width={280}
      style={{
        background: '#fff',
        borderRight: '1px solid #f0f0f0',
        boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
        overflow: 'hidden',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 10,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: collapsed ? '16px 8px' : '24px 16px',
          borderBottom: '1px solid #f0f0f0',
          textAlign: collapsed ? 'center' : 'left',
          flexShrink: 0,
        }}
      >
        {!collapsed && (
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
              虛擬 KOL 系統
            </Title>
            <div style={{ fontSize: '12px', color: '#666' }}>
              儀表板管理平台
            </div>
          </Space>
        )}
        {collapsed && (
          <div style={{ fontSize: '20px', color: '#1890ff', fontWeight: 'bold' }}>
            KOL
          </div>
        )}
      </div>

      {/* Scrollable Menu */}
      <div
        style={{
          padding: '8px',
          overflowY: 'auto',
          overflowX: 'hidden',
          height: 'calc(100vh - 180px)',
          scrollBehavior: 'smooth',
        }}
      >
        <Menu
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={getOpenKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          style={{
            border: 'none',
            background: 'transparent',
          }}
        />
      </div>

      {/* Fixed Bottom Refresh Button */}
      {!collapsed && (
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '16px',
            background: '#fff',
            borderTop: '1px solid #f0f0f0',
          }}
        >
          <div
            style={{
              padding: '12px',
              background: '#f5f5f5',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px',
              color: '#666',
              transition: 'all 0.3s',
            }}
            onClick={onRefresh}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#e6f7ff';
              e.currentTarget.style.color = '#1890ff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#f5f5f5';
              e.currentTarget.style.color = '#666';
            }}
          >
            <ReloadOutlined />
            刷新數據
          </div>
        </div>
      )}
    </Sider>
  );
};

export default Sidebar;
