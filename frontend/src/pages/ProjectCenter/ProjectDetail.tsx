import React from 'react';
import { Card, Tabs, Descriptions, Empty, Table, Spin, Button, Space } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import { getProject, listProjectAuditLogs } from '@/api/projects';
import type { AuditLog } from '@/types/project';
import PageHeader from '@/components/PageHeader';
import StatusTag from '@/components/StatusTag';
import RiskTag from '@/components/RiskTag';
import MoneyText from '@/components/MoneyText';
import PermissionGuard from '@/components/PermissionGuard';
import { PERMISSIONS } from '@/utils/permissions';
import { formatPercent, formatDate } from '@/utils/formatters';
import { ContractsPanel, CostFinancePanel } from './ProjectFinancePanels';

const ACTION_LABEL: Record<string, string> = {
  CREATE: '创建',
  UPDATE: '更新',
  DELETE: '删除',
};

const Placeholder: React.FC<{ name: string }> = ({ name }) => (
  <Empty description={`${name}模块将在后续阶段实现`} image={Empty.PRESENTED_IMAGE_SIMPLE} />
);

const ProjectDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const projectId = Number(id);

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => getProject(projectId),
  });

  const { data: logs } = useQuery({
    queryKey: ['project-audit', id],
    queryFn: () => listProjectAuditLogs(projectId),
  });

  const logColumns: ColumnsType<AuditLog> = [
    { title: '时间', dataIndex: 'created_at', render: (v) => formatDate(v) || '-', width: 180 },
    { title: '操作人', dataIndex: 'username', width: 140 },
    { title: '操作', dataIndex: 'action', width: 100, render: (v) => ACTION_LABEL[v] || v },
    { title: '详情', dataIndex: 'detail', render: (v) => v || '-' },
    { title: 'IP', dataIndex: 'ip_address', width: 140 },
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!project) {
    return <Empty description="项目不存在" />;
  }

  const basicInfo = (
    <Descriptions bordered column={2} size="middle">
      <Descriptions.Item label="项目编号">{project.project_code}</Descriptions.Item>
      <Descriptions.Item label="项目名称">{project.project_name}</Descriptions.Item>
      <Descriptions.Item label="项目类型">{project.project_type}</Descriptions.Item>
      <Descriptions.Item label="电压等级">{project.voltage_level || '-'}</Descriptions.Item>
      <Descriptions.Item label="项目状态"><StatusTag status={project.project_status} /></Descriptions.Item>
      <Descriptions.Item label="风险等级"><RiskTag level={project.risk_level} /></Descriptions.Item>
      <Descriptions.Item label="所属区域">{project.region || '-'}</Descriptions.Item>
      <Descriptions.Item label="项目地址">{project.project_location || '-'}</Descriptions.Item>
      <Descriptions.Item label="建设单位">{project.owner_unit || '-'}</Descriptions.Item>
      <Descriptions.Item label="施工单位">{project.construction_unit || '-'}</Descriptions.Item>
      <Descriptions.Item label="设计单位">{project.design_unit || '-'}</Descriptions.Item>
      <Descriptions.Item label="监理单位">{project.supervision_unit || '-'}</Descriptions.Item>
      <Descriptions.Item label="项目经理">{project.project_manager_name || '-'}</Descriptions.Item>
      <Descriptions.Item label="计划工期">
        {formatDate(project.planned_start_date)} ~ {formatDate(project.planned_end_date)}
      </Descriptions.Item>
      <Descriptions.Item label="合同金额"><MoneyText value={project.contract_amount} /></Descriptions.Item>
      <Descriptions.Item label="目标成本"><MoneyText value={project.target_cost} /></Descriptions.Item>
      <Descriptions.Item label="实际成本"><MoneyText value={project.actual_cost} /></Descriptions.Item>
      <Descriptions.Item label="当前利润"><MoneyText value={project.profit} /></Descriptions.Item>
      <Descriptions.Item label="已收款"><MoneyText value={project.received_amount} /></Descriptions.Item>
      <Descriptions.Item label="已付款"><MoneyText value={project.paid_amount} /></Descriptions.Item>
      <Descriptions.Item label="产值进度">{formatPercent(project.production_progress)}</Descriptions.Item>
      <Descriptions.Item label="收款进度">{formatPercent(project.collection_progress)}</Descriptions.Item>
      <Descriptions.Item label="资料完整率">{formatPercent(project.document_completion_rate)}</Descriptions.Item>
      <Descriptions.Item label="利润率">
        {typeof project.profit_margin === 'string' ? project.profit_margin : formatPercent(project.profit_margin)}
      </Descriptions.Item>
      <Descriptions.Item label="项目描述" span={2}>{project.description || '-'}</Descriptions.Item>
      <Descriptions.Item label="备注" span={2}>{project.remarks || '-'}</Descriptions.Item>
    </Descriptions>
  );

  const items = [
    { key: 'basic', label: '基本信息', children: basicInfo },
    { key: 'contract', label: '合同记录', children: <ContractsPanel projectId={projectId} /> },
    { key: 'cost', label: '成本资金', children: <CostFinancePanel projectId={projectId} /> },
    { key: 'material', label: '采购物资', children: <Placeholder name="采购物资" /> },
    { key: 'safety', label: '安全质量', children: <Placeholder name="安全质量" /> },
    { key: 'document', label: '资料档案', children: <Placeholder name="资料档案" /> },
    { key: 'risk', label: '风险预警', children: <Placeholder name="风险预警" /> },
    { key: 'approval', label: '审批记录', children: <Placeholder name="审批记录" /> },
    {
      key: 'audit',
      label: '操作日志',
      children: (
        <Table<AuditLog>
          rowKey="id"
          size="small"
          columns={logColumns}
          dataSource={logs?.items ?? []}
          pagination={{ pageSize: 10 }}
        />
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title={project.project_name}
        description={`项目编号：${project.project_code}`}
        extra={
          <Space>
            <PermissionGuard permission={PERMISSIONS.PROJECT_UPDATE}>
              <Button type="primary" onClick={() => navigate(`/projects/${projectId}/edit`)}>
                编辑
              </Button>
            </PermissionGuard>
            <Button onClick={() => navigate('/projects')}>返回列表</Button>
          </Space>
        }
      />
      <Card>
        <Tabs items={items} />
      </Card>
    </div>
  );
};

export default ProjectDetail;
