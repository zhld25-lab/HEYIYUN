import React from 'react';
import { Tabs, Tag } from 'antd';
import { useQuery } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import PageHeader from '@/components/PageHeader';
import ResourceManager, { type FieldConfig } from '@/components/ResourceManager';
import MoneyText from '@/components/MoneyText';
import FinanceAnalysis from './FinanceAnalysis';
import { costApi, paymentApi, receiptApi, invoiceApi } from '@/api/finance';
import { listProjects } from '@/api/projects';
import { listContracts } from '@/api/contracts';
import type { CostRecord, Payment, Receipt, Invoice } from '@/types/finance';
import { useAuthStore } from '@/store/authStore';
import { hasPermission, PERMISSIONS } from '@/utils/permissions';
import { formatDate, formatPercent } from '@/utils/formatters';
import {
  COST_TYPES,
  PAYMENT_STATUSES,
  INVOICE_RECEIVE_STATUSES,
  APPROVAL_STATUSES,
  INVOICE_TYPES,
  INVOICE_DIRECTIONS,
  CERTIFICATION_STATUSES,
} from '@/utils/constants';

const money = (v: unknown) => <MoneyText value={v as never} />;
const sel = (arr: string[]) => arr.map((v) => ({ value: v, label: v }));

const CostFinanceCenter: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const canEdit = hasPermission(user, PERMISSIONS.FINANCE_EDIT);
  const canDelete = hasPermission(user, PERMISSIONS.FINANCE_DELETE);

  const projectsQuery = useQuery({
    queryKey: ['all-projects-opts'],
    queryFn: () => listProjects({ page: 1, page_size: 200 }),
  });
  const contractsQuery = useQuery({
    queryKey: ['all-contracts-opts'],
    queryFn: () => listContracts({ page: 1, page_size: 200 }),
  });

  const projectOptions = (projectsQuery.data?.items ?? []).map((p) => ({
    value: p.id,
    label: p.project_name,
  }));
  const contractOptions = (contractsQuery.data?.items ?? []).map((c) => ({
    value: c.id,
    label: c.contract_name,
  }));

  // ---------- Cost ledger ----------
  const costColumns: ColumnsType<CostRecord> = [
    { title: '成本编号', dataIndex: 'cost_code', width: 140 },
    { title: '成本类型', dataIndex: 'cost_type', width: 120 },
    { title: '所属项目', dataIndex: 'project_name', width: 200 },
    { title: '关联合同', dataIndex: 'contract_name', width: 180, render: (v) => v || '-' },
    { title: '供应商/分包商', dataIndex: 'supplier_name', width: 180, render: (v) => v || '-' },
    { title: '金额', dataIndex: 'amount', width: 130, render: money },
    { title: '发生日期', dataIndex: 'occurred_date', width: 110, render: formatDate },
    { title: '经办人', dataIndex: 'handler_name', width: 90 },
    { title: '审批状态', dataIndex: 'approval_status', width: 100, render: (v) => <Tag>{v}</Tag> },
    { title: '发票状态', dataIndex: 'invoice_status', width: 100, render: (v) => <Tag>{v}</Tag> },
    { title: '付款状态', dataIndex: 'payment_status', width: 100, render: (v) => <Tag>{v}</Tag> },
  ];
  const costFields: FieldConfig[] = [
    { name: 'cost_code', label: '成本编号', type: 'text', required: true, disabledOnEdit: true },
    { name: 'cost_type', label: '成本类型', type: 'select', options: sel(COST_TYPES), required: true },
    { name: 'project_id', label: '所属项目', type: 'select', options: projectOptions, required: true },
    { name: 'contract_id', label: '关联合同', type: 'select', options: contractOptions },
    { name: 'supplier_name', label: '供应商/分包商', type: 'text' },
    { name: 'amount', label: '金额(元)', type: 'number', required: true },
    { name: 'occurred_date', label: '发生日期', type: 'date' },
    { name: 'handler_name', label: '经办人', type: 'text' },
    { name: 'approval_status', label: '审批状态', type: 'select', options: sel(APPROVAL_STATUSES) },
    { name: 'invoice_status', label: '发票状态', type: 'select', options: sel(INVOICE_RECEIVE_STATUSES) },
    { name: 'payment_status', label: '付款状态', type: 'select', options: sel(PAYMENT_STATUSES) },
    { name: 'remarks', label: '备注', type: 'textarea' },
  ];

  // ---------- Payments ----------
  const paymentColumns: ColumnsType<Payment> = [
    { title: '付款编号', dataIndex: 'payment_code', width: 140 },
    { title: '所属项目', dataIndex: 'project_name', width: 200 },
    { title: '关联合同', dataIndex: 'contract_name', width: 180, render: (v) => v || '-' },
    { title: '收款单位', dataIndex: 'payee_name', width: 180, render: (v) => v || '-' },
    { title: '申请金额', dataIndex: 'requested_amount', width: 130, render: money },
    { title: '已付金额', dataIndex: 'paid_amount', width: 130, render: money },
    { title: '付款日期', dataIndex: 'payment_date', width: 110, render: formatDate },
    { title: '付款状态', dataIndex: 'payment_status', width: 100, render: (v) => <Tag>{v}</Tag> },
    { title: '审批状态', dataIndex: 'approval_status', width: 100, render: (v) => <Tag>{v}</Tag> },
  ];
  const paymentFields: FieldConfig[] = [
    { name: 'payment_code', label: '付款编号', type: 'text', required: true, disabledOnEdit: true },
    { name: 'project_id', label: '所属项目', type: 'select', options: projectOptions, required: true },
    { name: 'contract_id', label: '关联合同', type: 'select', options: contractOptions },
    { name: 'payee_name', label: '收款单位', type: 'text' },
    { name: 'requested_amount', label: '申请金额(元)', type: 'number' },
    { name: 'paid_amount', label: '已付金额(元)', type: 'number' },
    { name: 'payment_date', label: '付款日期', type: 'date' },
    { name: 'payment_status', label: '付款状态', type: 'select', options: sel(PAYMENT_STATUSES) },
    { name: 'approval_status', label: '审批状态', type: 'select', options: sel(APPROVAL_STATUSES) },
    { name: 'remarks', label: '备注', type: 'textarea' },
  ];

  // ---------- Receipts ----------
  const receiptColumns: ColumnsType<Receipt> = [
    { title: '回款编号', dataIndex: 'receipt_code', width: 140 },
    { title: '所属项目', dataIndex: 'project_name', width: 200 },
    { title: '关联合同', dataIndex: 'contract_name', width: 180, render: (v) => v || '-' },
    { title: '付款单位', dataIndex: 'payer_name', width: 180, render: (v) => v || '-' },
    { title: '回款金额', dataIndex: 'receipt_amount', width: 130, render: money },
    { title: '回款日期', dataIndex: 'receipt_date', width: 110, render: formatDate },
    { title: '计划回款日期', dataIndex: 'planned_receipt_date', width: 120, render: formatDate },
    {
      title: '是否逾期',
      dataIndex: 'is_overdue',
      width: 90,
      render: (v) => (v ? <Tag color="red">逾期</Tag> : <Tag color="green">正常</Tag>),
    },
  ];
  const receiptFields: FieldConfig[] = [
    { name: 'receipt_code', label: '回款编号', type: 'text', required: true, disabledOnEdit: true },
    { name: 'project_id', label: '所属项目', type: 'select', options: projectOptions, required: true },
    { name: 'contract_id', label: '关联合同', type: 'select', options: contractOptions },
    { name: 'payer_name', label: '付款单位', type: 'text' },
    { name: 'receipt_amount', label: '回款金额(元)', type: 'number' },
    { name: 'receipt_date', label: '回款日期', type: 'date' },
    { name: 'planned_receipt_date', label: '计划回款日期', type: 'date' },
    { name: 'is_overdue', label: '是否逾期', type: 'switch' },
    { name: 'remarks', label: '备注', type: 'textarea' },
  ];

  // ---------- Invoices ----------
  const invoiceColumns: ColumnsType<Invoice> = [
    { title: '发票编号', dataIndex: 'invoice_code', width: 140 },
    { title: '发票类型', dataIndex: 'invoice_type', width: 150 },
    {
      title: '进项/销项',
      dataIndex: 'invoice_direction',
      width: 90,
      render: (v) => <Tag color={v === '销项' ? 'blue' : 'gold'}>{v}</Tag>,
    },
    { title: '所属项目', dataIndex: 'project_name', width: 200 },
    { title: '关联合同', dataIndex: 'contract_name', width: 180, render: (v) => v || '-' },
    { title: '金额', dataIndex: 'amount', width: 130, render: money },
    {
      title: '税率',
      dataIndex: 'tax_rate',
      width: 80,
      render: (v) => (typeof v === 'string' ? v : formatPercent(v)),
    },
    { title: '开票日期', dataIndex: 'invoice_date', width: 110, render: formatDate },
    { title: '认证状态', dataIndex: 'certification_status', width: 100, render: (v) => <Tag>{v}</Tag> },
  ];
  const invoiceFields: FieldConfig[] = [
    { name: 'invoice_code', label: '发票编号', type: 'text', required: true, disabledOnEdit: true },
    { name: 'invoice_type', label: '发票类型', type: 'select', options: sel(INVOICE_TYPES) },
    { name: 'invoice_direction', label: '进项/销项', type: 'select', options: sel(INVOICE_DIRECTIONS), required: true },
    { name: 'project_id', label: '所属项目', type: 'select', options: projectOptions, required: true },
    { name: 'contract_id', label: '关联合同', type: 'select', options: contractOptions },
    { name: 'amount', label: '金额(元)', type: 'number' },
    { name: 'tax_rate', label: '税率(如0.13)', type: 'number', step: 0.01 },
    { name: 'invoice_date', label: '开票日期', type: 'date' },
    { name: 'certification_status', label: '认证状态', type: 'select', options: sel(CERTIFICATION_STATUSES) },
    { name: 'remarks', label: '备注', type: 'textarea' },
  ];

  const items = [
    {
      key: 'cost',
      label: '成本台账',
      children: (
        <ResourceManager<CostRecord>
          title="成本"
          queryKey={['costs']}
          fetchList={costApi.list}
          columns={costColumns}
          fields={costFields}
          dateFields={['occurred_date']}
          numberFields={['amount']}
          canCreate={canEdit}
          canEdit={canEdit}
          canDelete={canDelete}
          createFn={costApi.create}
          updateFn={costApi.update}
          removeFn={costApi.remove}
        />
      ),
    },
    {
      key: 'payment',
      label: '付款管理',
      children: (
        <ResourceManager<Payment>
          title="付款"
          queryKey={['payments']}
          fetchList={paymentApi.list}
          columns={paymentColumns}
          fields={paymentFields}
          dateFields={['payment_date']}
          numberFields={['requested_amount', 'paid_amount']}
          canCreate={canEdit}
          canEdit={canEdit}
          canDelete={canDelete}
          createFn={paymentApi.create}
          updateFn={paymentApi.update}
          removeFn={paymentApi.remove}
        />
      ),
    },
    {
      key: 'receipt',
      label: '回款管理',
      children: (
        <ResourceManager<Receipt>
          title="回款"
          queryKey={['receipts']}
          fetchList={receiptApi.list}
          columns={receiptColumns}
          fields={receiptFields}
          dateFields={['receipt_date', 'planned_receipt_date']}
          numberFields={['receipt_amount']}
          canCreate={canEdit}
          canEdit={canEdit}
          canDelete={canDelete}
          createFn={receiptApi.create}
          updateFn={receiptApi.update}
          removeFn={receiptApi.remove}
        />
      ),
    },
    {
      key: 'invoice',
      label: '发票管理',
      children: (
        <ResourceManager<Invoice>
          title="发票"
          queryKey={['invoices']}
          fetchList={invoiceApi.list}
          columns={invoiceColumns}
          fields={invoiceFields}
          dateFields={['invoice_date']}
          numberFields={['amount']}
          canCreate={canEdit}
          canEdit={canEdit}
          canDelete={canDelete}
          createFn={invoiceApi.create}
          updateFn={invoiceApi.update}
          removeFn={invoiceApi.remove}
        />
      ),
    },
    { key: 'analysis', label: '财务分析', children: <FinanceAnalysis /> },
  ];

  return (
    <div>
      <PageHeader
        title="成本资金中心"
        description="成本台账、付款、回款、发票与财务分析。任何财务记录变更都会实时回算项目财务汇总。"
      />
      <Tabs items={items} destroyInactiveTabPane />
    </div>
  );
};

export default CostFinanceCenter;
