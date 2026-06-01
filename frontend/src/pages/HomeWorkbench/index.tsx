import React from 'react';
import { Card, Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import PageHeader from '@/components/PageHeader';

/** Phase 1 placeholder home workbench. Redirects users to the dashboard. */
const HomeWorkbench: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div>
      <PageHeader title="首页工作台" description="个人待办与经营概览入口（后续阶段完善）。" />
      <Card>
        <Result
          status="info"
          title="工作台建设中"
          subTitle="当前阶段请前往决策驾驶舱与项目中心。"
          extra={
            <Button type="primary" onClick={() => navigate('/dashboard')}>
              前往决策驾驶舱
            </Button>
          }
        />
      </Card>
    </div>
  );
};

export default HomeWorkbench;
