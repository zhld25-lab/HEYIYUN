import React from 'react';
import { Row, Col, Card, Statistic, Table, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { getSummary, getProjectStatus } from '@/api/dashboard';
import PageHeader from '@/components/PageHeader';
import MoneyText from '@/components/MoneyText';

const Dashboard: React.FC = () => {
  const summaryQuery = useQuery({ queryKey: ['dashboard-summary'], queryFn: getSummary });
  const statusQuery = useQuery({ queryKey: ['dashboard-status'], queryFn: getProjectStatus });

  const s = summaryQuery.data;

  return (
    <div>
      <PageHeader
        title="决策驾驶舱"
        description="围绕项目全生命周期的经营概览。普通员工角色下金额自动脱敏。"
      />
      <Spin spinning={summaryQuery.isLoading}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <Statistic title="项目总数" value={s?.project_count ?? 0} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <Statistic title="在建项目数" value={s?.active_project_count ?? 0} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <div className="ant-statistic-title">合同总额</div>
              <div className="kpi-money">
                <MoneyText value={s?.contract_amount} />
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <div className="ant-statistic-title">当前利润</div>
              <div className="kpi-money">
                <MoneyText value={s?.current_profit} />
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <div className="ant-statistic-title">累计回款</div>
              <div className="kpi-money">
                <MoneyText value={s?.received_amount} />
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <div className="ant-statistic-title">累计付款</div>
              <div className="kpi-money">
                <MoneyText value={s?.paid_amount} />
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="kpi-card">
              <Statistic
                title="高风险项目数"
                value={s?.high_risk_count ?? 0}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        <Card title="项目状态分布" style={{ marginTop: 16 }}>
          <Table
            size="small"
            pagination={false}
            loading={statusQuery.isLoading}
            rowKey="status"
            dataSource={statusQuery.data ?? []}
            columns={[
              { title: '项目状态', dataIndex: 'status' },
              { title: '数量', dataIndex: 'count' },
            ]}
          />
        </Card>
      </Spin>
    </div>
  );
};

export default Dashboard;
