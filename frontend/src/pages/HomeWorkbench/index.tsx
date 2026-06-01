import React from 'react';
import { Row, Col, Card, List, Button, Badge, Tag, Typography, Empty, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { AuditOutlined, SendOutlined, WarningOutlined } from '@ant-design/icons';
import PageHeader from '@/components/PageHeader';
import { getMyPendingWorkflows, getMyInitiatedWorkflows, type Workflow } from '@/api/workflows';
import { WorkflowStatusTag } from '@/pages/WorkflowCenter/WorkflowStatusTag';

const { Text } = Typography;

const WorkflowCard: React.FC<{
  title: string;
  icon: React.ReactNode;
  loading: boolean;
  items: Workflow[];
  emptyText: string;
  badgeColor?: string;
}> = ({ title, icon, loading, items, emptyText, badgeColor = '#1677ff' }) => {
  const navigate = useNavigate();
  return (
    <Card
      title={
        <span>
          {icon}
          <span style={{ marginLeft: 8 }}>{title}</span>
          {items.length > 0 && (
            <Badge count={items.length} style={{ marginLeft: 8, backgroundColor: badgeColor }} />
          )}
        </span>
      }
      extra={<Button size="small" type="link" onClick={() => navigate('/workflows')}>查看全部</Button>}
    >
      <Spin spinning={loading}>
        {items.length === 0 ? (
          <Empty description={emptyText} image={Empty.PRESENTED_IMAGE_SIMPLE} />
        ) : (
          <List
            size="small"
            dataSource={items.slice(0, 5)}
            renderItem={(wf) => (
              <List.Item
                extra={<WorkflowStatusTag status={wf.status} />}
                style={{ cursor: 'pointer' }}
                onClick={() => navigate('/workflows')}
              >
                <List.Item.Meta
                  title={<Text ellipsis style={{ maxWidth: 200 }}>{wf.title}</Text>}
                  description={
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {wf.workflow_type} · {wf.submitted_at?.slice(0, 10) ?? '-'}
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Spin>
    </Card>
  );
};

const HomeWorkbench: React.FC = () => {
  const pendingQ = useQuery({ queryKey: ['my-pending-workflows'], queryFn: getMyPendingWorkflows });
  const initiatedQ = useQuery({ queryKey: ['my-initiated-workflows'], queryFn: getMyInitiatedWorkflows });

  const overdueItems = (initiatedQ.data ?? []).filter(
    w => w.status === 'pending' && w.submitted_at
      && Date.now() - new Date(w.submitted_at).getTime() > 7 * 86400_000,
  );

  return (
    <div>
      <PageHeader title="首页工作台" description="待处理审批、我发起的流程与超期预警。" />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <WorkflowCard
            title="我的待办"
            icon={<AuditOutlined style={{ color: '#1677ff' }} />}
            loading={pendingQ.isLoading}
            items={pendingQ.data ?? []}
            emptyText="暂无待办审批"
            badgeColor="#1677ff"
          />
        </Col>
        <Col xs={24} md={12}>
          <WorkflowCard
            title="我的发起"
            icon={<SendOutlined style={{ color: '#52c41a' }} />}
            loading={initiatedQ.isLoading}
            items={initiatedQ.data ?? []}
            emptyText="暂无发起的流程"
            badgeColor="#52c41a"
          />
        </Col>
        {overdueItems.length > 0 && (
          <Col xs={24}>
            <Card
              title={
                <span style={{ color: '#cf1322' }}>
                  <WarningOutlined style={{ marginRight: 8 }} />
                  超期预警（{overdueItems.length} 条）
                </span>
              }
            >
              <List
                size="small"
                dataSource={overdueItems}
                renderItem={(wf) => (
                  <List.Item extra={<Tag color="red">超期</Tag>}>
                    <List.Item.Meta
                      title={wf.title}
                      description={`${wf.workflow_type} · 提交于 ${wf.submitted_at?.slice(0, 10)}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
};

export default HomeWorkbench;
