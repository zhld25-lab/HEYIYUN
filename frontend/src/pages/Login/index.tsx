import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Alert } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { login } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';
import { APP_NAME_CN, APP_NAME_EN } from '@/utils/constants';

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const data = await login(values);
      setAuth(data.access_token, data.user);
      message.success(`欢迎，${data.user.full_name}`);
      navigate('/dashboard');
    } catch {
      // error toast handled by axios interceptor
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <Card className="login-card" bordered={false}>
        <div className="login-header">
          <Title level={3} style={{ marginBottom: 4 }}>
            {APP_NAME_CN}
          </Title>
          <Text type="secondary">{APP_NAME_EN}</Text>
        </div>
        <Form layout="vertical" onFinish={onFinish} size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>
        <Alert
          type="info"
          showIcon
          message="演示账号"
          description="admin / Admin123456（系统管理员）、manager / Manager123456（总经理）、staff / Staff123456（普通员工，金额脱敏）"
        />
      </Card>
    </div>
  );
};

export default Login;
