import React from 'react';
import { Row, Col, Card, Empty } from 'antd';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import {
  getCashflow,
  getCostBreakdown,
  getProjectProfitTop,
  getFinanceSummary,
} from '@/api/dashboard';
import { isMasked } from '@/utils/formatters';

const toWan = (v: number | string): number =>
  typeof v === 'string' ? 0 : Math.round((v / 10000) * 100) / 100;

const MaskedNotice: React.FC = () => (
  <Empty description="当前角色无权查看金额明细" image={Empty.PRESENTED_IMAGE_SIMPLE} />
);

const FinanceAnalysis: React.FC = () => {
  const cashflow = useQuery({ queryKey: ['fin-cashflow'], queryFn: getCashflow });
  const breakdown = useQuery({ queryKey: ['fin-breakdown'], queryFn: getCostBreakdown });
  const profitTop = useQuery({ queryKey: ['fin-profit-top'], queryFn: getProjectProfitTop });
  const summary = useQuery({ queryKey: ['fin-summary'], queryFn: getFinanceSummary });

  const masked = isMasked(summary.data?.total_profit);

  if (masked) return <MaskedNotice />;

  const cashflowOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['回款', '付款', '净现金流'] },
    xAxis: { type: 'category', data: (cashflow.data ?? []).map((d) => d.month) },
    yAxis: { type: 'value', name: '万元' },
    series: [
      { name: '回款', type: 'bar', data: (cashflow.data ?? []).map((d) => toWan(d.received)) },
      { name: '付款', type: 'bar', data: (cashflow.data ?? []).map((d) => toWan(d.paid)) },
      { name: '净现金流', type: 'line', smooth: true, data: (cashflow.data ?? []).map((d) => toWan(d.net)) },
    ],
  };

  const breakdownOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 万 ({d}%)' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: (breakdown.data ?? []).map((d) => ({ name: d.cost_type, value: toWan(d.amount) })),
      },
    ],
  };

  const profitOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 140 },
    xAxis: { type: 'value', name: '万元' },
    yAxis: {
      type: 'category',
      data: (profitTop.data ?? []).map((d) => d.project_name).reverse(),
    },
    series: [
      {
        type: 'bar',
        data: (profitTop.data ?? []).map((d) => toWan(d.profit)).reverse(),
        itemStyle: { color: '#1d4ed8' },
      },
    ],
  };

  const arapOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['应收款', '应付款'] },
    xAxis: { type: 'category', data: ['合计'] },
    yAxis: { type: 'value', name: '万元' },
    series: [
      { name: '应收款', type: 'bar', data: [toWan(summary.data?.total_receivable ?? 0)] },
      { name: '应付款', type: 'bar', data: [toWan(summary.data?.total_payable ?? 0)] },
    ],
  };

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <Card title="成本构成">
          <ReactECharts option={breakdownOption} style={{ height: 320 }} />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="回款 / 付款趋势">
          <ReactECharts option={cashflowOption} style={{ height: 320 }} />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="项目利润 Top 10">
          <ReactECharts option={profitOption} style={{ height: 320 }} />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="应收 / 应付对比">
          <ReactECharts option={arapOption} style={{ height: 320 }} />
        </Card>
      </Col>
    </Row>
  );
};

export default FinanceAnalysis;
