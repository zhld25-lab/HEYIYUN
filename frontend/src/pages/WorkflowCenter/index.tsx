import React, { useState } from 'react';
import { Tabs, Table, Button, Tag, Space, Empty, Card } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import {
  listWorkflows, getMyPendingWorkflows, getMyDoneWorkflows, getMyInitiatedWorkflows,
  type Workflow,
} from '@/api/workflows';
import PageHeader from '@/components/PageHeader';
import { WorkflowStatusTag } from './WorkflowStatusTag';
import WorkflowDetailDrawer from './WorkflowDetailDrawer';

const BUSINESS_TYPE_LABELS: Record<string, string> = {
  project: '项目',
  contract: '合同',
  cost: '成本',
  payment: '付款',
  invoice: '发票',
};

const WorkflowCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const pendingQ = useQuery({ queryKey: ['my-pending-workflows'], queryFn: getMyPendingWorkflows });
  const doneQ = useQuery({ queryKey: ['my-done-workflows'], queryFn: getMyDoneWorkflows });
  const initiatedQ = useQuery({ queryKey: ['my-initiated-workflows'], queryFn: getMyInitiatedWorkflows });
  const allQ = useQuery({ queryKey: ['workflows'], queryFn: () => listWorkflows() });

  const columns = (showActions = false) => [
    { title: '标题', dataIndex: 'title', ellipsis: true },
    { title: '流程类型', dataIndex: 'workflow_type', width: 120 },
    {
      title: '业务类型', dataIndex: 'business_type', width: 80,
      render: (v: string) => BUSINESS_TYPE_LABELS[v] ?? v,
    },
    { title: '发起人', dataIndex: 'initiator_name', width: 100 },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (v: string) => <WorkflowStatusTag status={v} />,
    },
    {
      title: '步骤', width: 80,
      render: (_: any, r: Workflow) => `${r.current_step}/${r.total_steps}`,
    },
    { title: '提交时间', dataIndex: 'submitted_at', width: 120, render: (v: string) => v?.slice(0, 10) ?? '-' },
    {
      title: '操作', width: 80,
      render: (_: any, r: Workflow) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => setSelectedId(r.id)}>
          详情
        </Button>
      ),
    },
  ];

  const tabs = [
    {
      key: 'pending',
      label: `我的待办 ${pendingQ.data?.length ? `(${pendingQ.data.length})` : ''}`,
      children: (
        <Table
          size="small" rowKey="id"
          loading={pendingQ.isLoading}
          dataSource={pendingQ.data ?? []}
          columns={columns()}
          pagination={{ pageSize: 10 }}
        />
      ),
    },
    {
      key: 'done',
      label: '我的已办',
      children: (
        <Table
          size="small" rowKey="id"
          loading={doneQ.isLoading}
          dataSource={doneQ.data ?? []}
          columns={columns()}
          pagination={{ pageSize: 10 }}
        />
      ),
    },
    {
      key: 'initiated',
      label: '我的发起',
      children: (
        <Table
          size="small" rowKey="id"
          loading={initiatedQ.isLoading}
          dataSource={initiatedQ.data ?? []}
          columns={columns()}
          pagination={{ pageSize: 10 }}
        />
      ),
    },
    {
      key: 'all',
      label: '全部流程',
      children: (
        <Table
          size="small" rowKey="id"
          loading={allQ.isLoading}
          dataSource={allQ.data ?? []}
          columns={columns()}
          pagination={{ pageSize: 20 }}
        />
      ),
    },
    {
      key: 'config',
      label: '流程配置',
      children: (
        <Card>
          <Empty description="流程模板配置（后续版本开放）" />
        </Card>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="审批中心" description="提交审批、处理待办、查看流程进度。" />
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabs} />
      </Card>
      <WorkflowDetailDrawer workflowId={selectedId} onClose={() => setSelectedId(null)} />
    </div>
  );
};

export default WorkflowCenter;
