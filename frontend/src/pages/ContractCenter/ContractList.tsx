import React, { useState } from 'react';
import { Tag, Input, Select, Space, Button } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import PageHeader from '@/components/PageHeader';
import ResourceManager, { type FieldConfig } from '@/components/ResourceManager';
import MoneyText from '@/components/MoneyText';
import { listContracts, createContract, updateContract, deleteContract } from '@/api/contracts';
import { listProjects } from '@/api/projects';
import type { Contract } from '@/types/finance';
import { useAuthStore } from '@/store/authStore';
import { hasPermission, PERMISSIONS } from '@/utils/permissions';
import { formatDate } from '@/utils/formatters';
import {
  CONTRACT_TYPES,
  CONTRACT_STATUSES,
  APPROVAL_STATUSES,
  ARCHIVE_STATUSES,
} from '@/utils/constants';

const money = (v: unknown) => <MoneyText value={v as never} />;
const sel = (arr: string[]) => arr.map((v) => ({ value: v, label: v }));

const ContractList: React.FC = () => {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [filters, setFilters] = useState<Record<string, unknown>>({});
  const [draft, setDraft] = useState<Record<string, unknown>>({});

  const projectsQuery = useQuery({
    queryKey: ['all-projects-opts'],
    queryFn: () => listProjects({ page: 1, page_size: 200 }),
  });
  const projectOptions = (projectsQuery.data?.items ?? []).map((p) => ({
    value: p.id,
    label: p.project_name,
  }));

  const columns: ColumnsType<Contract> = [
    { title: '合同编号', dataIndex: 'contract_code', fixed: 'left', width: 150 },
    { title: '合同名称', dataIndex: 'contract_name', fixed: 'left', width: 220 },
    { title: '合同类型', dataIndex: 'contract_type', width: 120 },
    { title: '所属项目', dataIndex: 'project_name', width: 200 },
    { title: '甲方', dataIndex: 'party_a', width: 160, render: (v) => v || '-' },
    { title: '乙方', dataIndex: 'party_b', width: 160, render: (v) => v || '-' },
    { title: '合同金额', dataIndex: 'contract_amount', width: 130, render: money },
    { title: '结算金额', dataIndex: 'settlement_amount', width: 130, render: money },
    { title: '已开票', dataIndex: 'invoiced_amount', width: 120, render: money },
    { title: '已收款', dataIndex: 'received_amount', width: 120, render: money },
    { title: '已付款', dataIndex: 'paid_amount', width: 120, render: money },
    { title: '应收款', dataIndex: 'receivable_amount', width: 120, render: money },
    { title: '应付款', dataIndex: 'payable_amount', width: 120, render: money },
    { title: '合同状态', dataIndex: 'contract_status', width: 90, render: (v) => <Tag>{v}</Tag> },
    { title: '审批状态', dataIndex: 'approval_status', width: 90, render: (v) => <Tag>{v}</Tag> },
    { title: '归档状态', dataIndex: 'archive_status', width: 90, render: (v) => <Tag>{v}</Tag> },
    { title: '签订日期', dataIndex: 'signed_date', width: 110, render: formatDate },
  ];

  const fields: FieldConfig[] = [
    { name: 'contract_code', label: '合同编号', type: 'text', required: true, section: '基本信息', disabledOnEdit: true },
    { name: 'contract_name', label: '合同名称', type: 'text', required: true, section: '基本信息' },
    { name: 'contract_type', label: '合同类型', type: 'select', options: sel(CONTRACT_TYPES), required: true, section: '基本信息' },
    { name: 'project_id', label: '所属项目', type: 'select', options: projectOptions, required: true, section: '基本信息' },
    { name: 'party_a', label: '甲方', type: 'text', section: '合同双方' },
    { name: 'party_b', label: '乙方', type: 'text', section: '合同双方' },
    { name: 'contract_amount', label: '合同金额(元)', type: 'number', section: '金额信息' },
    { name: 'settlement_amount', label: '结算金额(元)', type: 'number', section: '金额信息' },
    { name: 'contract_status', label: '合同状态', type: 'select', options: sel(CONTRACT_STATUSES), section: '状态信息' },
    { name: 'approval_status', label: '审批状态', type: 'select', options: sel(APPROVAL_STATUSES), section: '状态信息' },
    { name: 'archive_status', label: '归档状态', type: 'select', options: sel(ARCHIVE_STATUSES), section: '状态信息' },
    { name: 'signed_date', label: '签订日期', type: 'date', section: '状态信息' },
    { name: 'description', label: '合同说明', type: 'textarea', section: '说明备注' },
    { name: 'remarks', label: '备注', type: 'textarea', section: '说明备注' },
  ];

  const filtersSlot = (
    <Space wrap>
      <Input
        placeholder="合同编号"
        allowClear
        style={{ width: 130 }}
        onChange={(e) => setDraft((d) => ({ ...d, contract_code: e.target.value || undefined }))}
      />
      <Input
        placeholder="合同名称"
        allowClear
        style={{ width: 150 }}
        onChange={(e) => setDraft((d) => ({ ...d, contract_name: e.target.value || undefined }))}
      />
      <Select
        placeholder="合同类型"
        allowClear
        style={{ width: 140 }}
        options={sel(CONTRACT_TYPES)}
        onChange={(v) => setDraft((d) => ({ ...d, contract_type: v }))}
      />
      <Select
        placeholder="所属项目"
        allowClear
        style={{ width: 180 }}
        options={projectOptions}
        onChange={(v) => setDraft((d) => ({ ...d, project_id: v }))}
      />
      <Select
        placeholder="合同状态"
        allowClear
        style={{ width: 110 }}
        options={sel(CONTRACT_STATUSES)}
        onChange={(v) => setDraft((d) => ({ ...d, contract_status: v }))}
      />
      <Select
        placeholder="审批状态"
        allowClear
        style={{ width: 110 }}
        options={sel(APPROVAL_STATUSES)}
        onChange={(v) => setDraft((d) => ({ ...d, approval_status: v }))}
      />
      <Select
        placeholder="归档状态"
        allowClear
        style={{ width: 110 }}
        options={sel(ARCHIVE_STATUSES)}
        onChange={(v) => setDraft((d) => ({ ...d, archive_status: v }))}
      />
      <Button type="primary" onClick={() => setFilters({ ...draft })}>
        查询
      </Button>
      <Button onClick={() => { setDraft({}); setFilters({}); }}>重置</Button>
    </Space>
  );

  return (
    <div>
      <PageHeader
        title="合同中心"
        description="承包、分包、采购、租赁合同管理。合同金额、收付款、开票数据与项目财务汇总联动。"
      />
      <ResourceManager<Contract>
        title="合同"
        queryKey={['contracts']}
        fetchList={listContracts}
        columns={columns}
        fields={fields}
        dateFields={['signed_date']}
        numberFields={['contract_amount', 'settlement_amount']}
        canCreate={hasPermission(user, PERMISSIONS.CONTRACT_CREATE)}
        canEdit={hasPermission(user, PERMISSIONS.CONTRACT_UPDATE)}
        canDelete={hasPermission(user, PERMISSIONS.CONTRACT_DELETE)}
        createFn={createContract}
        updateFn={updateContract}
        removeFn={deleteContract}
        filtersSlot={filtersSlot}
        filterParams={filters}
        rowActions={(record) => (
          <Button type="link" size="small" onClick={() => navigate(`/contracts/${record.id}`)}>
            查看
          </Button>
        )}
      />
    </div>
  );
};

export default ContractList;
