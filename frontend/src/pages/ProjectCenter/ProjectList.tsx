import React, { useState } from 'react';
import { Card, Form, Input, Select, Button, Space, Popconfirm, message } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import { listProjects, deleteProject } from '@/api/projects';
import type { Project, ProjectListParams } from '@/types/project';
import PageHeader from '@/components/PageHeader';
import EnterpriseTable from '@/components/EnterpriseTable';
import StatusTag from '@/components/StatusTag';
import RiskTag from '@/components/RiskTag';
import MoneyText from '@/components/MoneyText';
import PermissionGuard from '@/components/PermissionGuard';
import { PERMISSIONS } from '@/utils/permissions';
import { formatPercent } from '@/utils/formatters';
import { PROJECT_TYPES, VOLTAGE_LEVELS, PROJECT_STATUSES, RISK_LEVELS } from '@/utils/constants';

const ProjectList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<ProjectListParams>({ page: 1, page_size: 10 });
  const [form] = Form.useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['projects', filters],
    queryFn: () => listProjects(filters),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      message.success('删除成功');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const onSearch = () => {
    const values = form.getFieldsValue();
    setFilters({ ...values, page: 1, page_size: filters.page_size });
  };

  const onReset = () => {
    form.resetFields();
    setFilters({ page: 1, page_size: 10 });
  };

  const columns: ColumnsType<Project> = [
    { title: '项目编号', dataIndex: 'project_code', fixed: 'left', width: 130 },
    { title: '项目名称', dataIndex: 'project_name', fixed: 'left', width: 220 },
    { title: '项目类型', dataIndex: 'project_type', width: 150 },
    { title: '电压等级', dataIndex: 'voltage_level', width: 90 },
    { title: '项目经理', dataIndex: 'project_manager_name', width: 110, render: (v) => v || '-' },
    { title: '项目状态', dataIndex: 'project_status', width: 90, render: (v) => <StatusTag status={v} /> },
    { title: '合同金额', dataIndex: 'contract_amount', width: 130, render: (v) => <MoneyText value={v} /> },
    { title: '目标成本', dataIndex: 'target_cost', width: 130, render: (v) => <MoneyText value={v} /> },
    { title: '实际成本', dataIndex: 'actual_cost', width: 130, render: (v) => <MoneyText value={v} /> },
    { title: '已收款', dataIndex: 'received_amount', width: 130, render: (v) => <MoneyText value={v} /> },
    { title: '已付款', dataIndex: 'paid_amount', width: 130, render: (v) => <MoneyText value={v} /> },
    { title: '产值进度', dataIndex: 'production_progress', width: 90, render: (v) => formatPercent(v) },
    { title: '收款进度', dataIndex: 'collection_progress', width: 90, render: (v) => formatPercent(v) },
    { title: '利润率', dataIndex: 'profit_margin', width: 90, render: (v) => (typeof v === 'string' ? v : formatPercent(v)) },
    { title: '资料完整率', dataIndex: 'document_completion_rate', width: 100, render: (v) => formatPercent(v) },
    { title: '风险等级', dataIndex: 'risk_level', width: 90, render: (v) => <RiskTag level={v} /> },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => navigate(`/projects/${record.id}`)}>
            查看
          </Button>
          <PermissionGuard permission={PERMISSIONS.PROJECT_UPDATE}>
            <Button type="link" size="small" onClick={() => navigate(`/projects/${record.id}/edit`)}>
              编辑
            </Button>
          </PermissionGuard>
          <PermissionGuard permission={PERMISSIONS.PROJECT_DELETE}>
            <Popconfirm
              title="确认删除该项目？"
              onConfirm={() => deleteMutation.mutate(record.id)}
            >
              <Button type="link" size="small" danger>
                删除
              </Button>
            </Popconfirm>
          </PermissionGuard>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="项目中心"
        description="项目是系统主线，所有合同、成本、资金、采购、资料、审批和风险均围绕项目关联。"
        extra={
          <PermissionGuard permission={PERMISSIONS.PROJECT_CREATE}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/projects/create')}>
              新建立项
            </Button>
          </PermissionGuard>
        }
      />
      <Card style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline" className="filter-form">
          <Form.Item name="project_name" label="项目名称">
            <Input placeholder="项目名称" allowClear style={{ width: 160 }} />
          </Form.Item>
          <Form.Item name="project_code" label="项目编号">
            <Input placeholder="项目编号" allowClear style={{ width: 140 }} />
          </Form.Item>
          <Form.Item name="project_type" label="项目类型">
            <Select placeholder="全部" allowClear style={{ width: 160 }} options={PROJECT_TYPES.map((t) => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item name="voltage_level" label="电压等级">
            <Select placeholder="全部" allowClear style={{ width: 110 }} options={VOLTAGE_LEVELS.map((t) => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item name="project_status" label="项目状态">
            <Select placeholder="全部" allowClear style={{ width: 110 }} options={PROJECT_STATUSES.map((t) => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item name="risk_level" label="风险等级">
            <Select placeholder="全部" allowClear style={{ width: 100 }} options={RISK_LEVELS.map((t) => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={onSearch}>
                查询
              </Button>
              <Button onClick={onReset}>重置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
      <Card>
        <EnterpriseTable<Project>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={data?.items ?? []}
          pagination={{
            current: filters.page,
            pageSize: filters.page_size,
            total: data?.total ?? 0,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (page, page_size) => setFilters((f) => ({ ...f, page, page_size })),
          }}
        />
      </Card>
    </div>
  );
};

export default ProjectList;
