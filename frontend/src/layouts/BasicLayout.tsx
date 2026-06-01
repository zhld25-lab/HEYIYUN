import React, { useEffect } from 'react';
import { Layout, Menu, Dropdown, Avatar, Breadcrumb, Tag, Spin } from 'antd';
import {
  DashboardOutlined,
  ProjectOutlined,
  SettingOutlined,
  HomeOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { fetchMe } from '@/api/auth';
import { APP_NAME_CN } from '@/utils/constants';

const { Header, Sider, Content } = Layout;

const MENU_ITEMS = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '决策驾驶舱' },
  { key: '/projects', icon: <ProjectOutlined />, label: '项目中心' },
  { key: '/system', icon: <SettingOutlined />, label: '系统设置' },
];

const BREADCRUMB_MAP: Record<string, string> = {
  dashboard: '决策驾驶舱',
  projects: '项目中心',
  create: '新建项目',
  edit: '编辑项目',
  system: '系统设置',
};

const BasicLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, token, setUser, logout } = useAuthStore();

  useEffect(() => {
    if (token && !user) {
      fetchMe()
        .then(setUser)
        .catch(() => logout());
    }
  }, [token, user, setUser, logout]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!user) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  const selectedKey =
    MENU_ITEMS.find((item) => location.pathname.startsWith(item.key))?.key || '/dashboard';

  const crumbs = location.pathname.split('/').filter(Boolean);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={232} className="app-sider" theme="dark">
        <div className="app-logo">电力工程 ERP</div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={MENU_ITEMS}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <div className="app-header-title">{APP_NAME_CN}</div>
          <Dropdown
            menu={{
              items: [
                { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', onClick: handleLogout },
              ],
            }}
          >
            <div className="app-header-user">
              <Avatar size="small" icon={<UserOutlined />} />
              <span className="app-header-username">{user.full_name}</span>
              <Tag color="blue">{user.role_name}</Tag>
            </div>
          </Dropdown>
        </Header>
        <div className="app-breadcrumb">
          <Breadcrumb
            items={[
              { title: <HomeOutlined /> },
              ...crumbs.map((c) => ({ title: BREADCRUMB_MAP[c] || c })),
            ]}
          />
        </div>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default BasicLayout;
