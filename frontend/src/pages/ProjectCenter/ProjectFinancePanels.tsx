import React from 'react';
import { Table, Tag, Card, Row, Col, Statistic, Divider } from 'antd';
import { useQuery } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import {
  getProjectContracts,
  getProjectCosts,
  getProjectPayments,
  getProjectReceipts,
  getProjectInvoices,
  getProjectFinanceSummary,
} from '@/api/finance';
import type { Contract, CostRecord, Payment, Receipt, Invoice } from '@/types/finance';
import MoneyText from '@/components/MoneyText';
import { formatDate, formatPercent } from '@/utils/formatters';

const money = (v: unknown) => <MoneyText value={v as never} />;

export const ContractsPanel: React.FC<{ projectId: number }> = ({ projectId }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['project-contracts', projectId],
    queryFn: () => getProjectContracts(projectId),
  });
  const columns: ColumnsType<Contract> = [
    { title: '合同编号', dataIndex: 'contract_code', width: 150 },
    { title: '合同名称', dataIndex: 'contract_name', width: 220 },
    { title: '合同类型', dataIndex: 'contract_type', width: 110 },
    { title: '甲方', dataIndex: 'party_a', render: (v) => v || '-' },
    { title: '乙方', dataIndex: 'party_b', render: (v) => v || '-' },
    { title: '合同金额', dataIndex: 'contract_amount', width: 130, render: money },
    { title: '已收款', dataIndex: 'received_amount', width: 120, render: money },
    { title: '已付款', dataIndex: 'paid_amount', width: 120, render: money },
    { title: '合同状态', dataIndex: 'contract_status', width: 90, render: (v) => <Tag>{v}</Tag> },
  ];
  return (
    <Table<Contract>
      rowKey="id"
      size="small"
      loading={isLoading}
      columns={columns}
      dataSource={data ?? []}
      scroll={{ x: 'max-content' }}
      pagination={{ pageSize: 10 }}
    />
  );
};

const FinanceSummaryCard: React.FC<{ projectId: number }> = ({ projectId }) => {
  const { data: s } = useQuery({
    queryKey: ['project-finance-summary', projectId],
    queryFn: () => getProjectFinanceSummary(projectId),
  });
  if (!s) return null;
  return (
    <Card size="small" title="项目财务汇总" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}><div className="ant-statistic-title">合同金额</div><MoneyText value={s.contract_amount} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">目标成本</div><MoneyText value={s.target_cost} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">实际成本</div><MoneyText value={s.actual_cost} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">利润</div><MoneyText value={s.profit} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">已收款</div><MoneyText value={s.received_amount} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">已付款</div><MoneyText value={s.paid_amount} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">应收款</div><MoneyText value={s.receivable_amount} /></Col>
        <Col xs={12} md={6}><div className="ant-statistic-title">应付款</div><MoneyText value={s.payable_amount} /></Col>
        <Col xs={12} md={6}>
          <Statistic title="利润率" value={typeof s.profit_margin === 'string' ? s.profit_margin : formatPercent(s.profit_margin)} />
        </Col>
        <Col xs={12} md={6}>
          <Statistic title="收款进度" value={formatPercent(s.collection_progress)} />
        </Col>
        <Col xs={12} md={6}>
          <Statistic title="成本占比" value={formatPercent(s.cost_ratio)} />
        </Col>
      </Row>
    </Card>
  );
};

export const CostFinancePanel: React.FC<{ projectId: number }> = ({ projectId }) => {
  const costs = useQuery({ queryKey: ['project-costs', projectId], queryFn: () => getProjectCosts(projectId) });
  const payments = useQuery({ queryKey: ['project-payments', projectId], queryFn: () => getProjectPayments(projectId) });
  const receipts = useQuery({ queryKey: ['project-receipts', projectId], queryFn: () => getProjectReceipts(projectId) });
  const invoices = useQuery({ queryKey: ['project-invoices', projectId], queryFn: () => getProjectInvoices(projectId) });

  const costCols: ColumnsType<CostRecord> = [
    { title: '成本编号', dataIndex: 'cost_code' },
    { title: '成本类型', dataIndex: 'cost_type' },
    { title: '供应商', dataIndex: 'supplier_name', render: (v) => v || '-' },
    { title: '金额', dataIndex: 'amount', render: money },
    { title: '发生日期', dataIndex: 'occurred_date', render: formatDate },
    { title: '付款状态', dataIndex: 'payment_status', render: (v) => <Tag>{v}</Tag> },
  ];
  const payCols: ColumnsType<Payment> = [
    { title: '付款编号', dataIndex: 'payment_code' },
    { title: '收款单位', dataIndex: 'payee_name', render: (v) => v || '-' },
    { title: '申请金额', dataIndex: 'requested_amount', render: money },
    { title: '已付金额', dataIndex: 'paid_amount', render: money },
    { title: '付款日期', dataIndex: 'payment_date', render: formatDate },
  ];
  const recCols: ColumnsType<Receipt> = [
    { title: '回款编号', dataIndex: 'receipt_code' },
    { title: '付款单位', dataIndex: 'payer_name', render: (v) => v || '-' },
    { title: '回款金额', dataIndex: 'receipt_amount', render: money },
    { title: '回款日期', dataIndex: 'receipt_date', render: formatDate },
    { title: '是否逾期', dataIndex: 'is_overdue', render: (v) => (v ? <Tag color="red">逾期</Tag> : <Tag color="green">正常</Tag>) },
  ];
  const invCols: ColumnsType<Invoice> = [
    { title: '发票编号', dataIndex: 'invoice_code' },
    { title: '进项/销项', dataIndex: 'invoice_direction', render: (v) => <Tag color={v === '销项' ? 'blue' : 'gold'}>{v}</Tag> },
    { title: '金额', dataIndex: 'amount', render: money },
    { title: '开票日期', dataIndex: 'invoice_date', render: formatDate },
    { title: '认证状态', dataIndex: 'certification_status', render: (v) => <Tag>{v}</Tag> },
  ];

  const block = (title: string, node: React.ReactNode) => (
    <>
      <Divider orientation="left" orientationMargin={0}>{title}</Divider>
      {node}
    </>
  );

  return (
    <div>
      <FinanceSummaryCard projectId={projectId} />
      {block('成本记录', <Table<CostRecord> rowKey="id" size="small" loading={costs.isLoading} columns={costCols} dataSource={costs.data ?? []} scroll={{ x: 'max-content' }} pagination={{ pageSize: 5 }} />)}
      {block('付款记录', <Table<Payment> rowKey="id" size="small" loading={payments.isLoading} columns={payCols} dataSource={payments.data ?? []} scroll={{ x: 'max-content' }} pagination={{ pageSize: 5 }} />)}
      {block('回款记录', <Table<Receipt> rowKey="id" size="small" loading={receipts.isLoading} columns={recCols} dataSource={receipts.data ?? []} scroll={{ x: 'max-content' }} pagination={{ pageSize: 5 }} />)}
      {block('发票记录', <Table<Invoice> rowKey="id" size="small" loading={invoices.isLoading} columns={invCols} dataSource={invoices.data ?? []} scroll={{ x: 'max-content' }} pagination={{ pageSize: 5 }} />)}
    </div>
  );
};
