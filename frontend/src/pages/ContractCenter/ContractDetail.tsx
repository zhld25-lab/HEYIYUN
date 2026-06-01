import React from 'react';
import { Card, Descriptions, Button, Space, Spin, Empty, Tag } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getContract } from '@/api/contracts';
import PageHeader from '@/components/PageHeader';
import MoneyText from '@/components/MoneyText';
import { formatDate } from '@/utils/formatters';

const ContractDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: c, isLoading } = useQuery({
    queryKey: ['contract', id],
    queryFn: () => getContract(Number(id)),
  });

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }
  if (!c) return <Empty description="合同不存在" />;

  return (
    <div>
      <PageHeader
        title={c.contract_name}
        description={`合同编号：${c.contract_code}`}
        extra={
          <Space>
            <Button onClick={() => navigate(`/projects/${c.project_id}`)}>查看所属项目</Button>
            <Button onClick={() => navigate('/contracts')}>返回列表</Button>
          </Space>
        }
      />
      <Card>
        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="合同编号">{c.contract_code}</Descriptions.Item>
          <Descriptions.Item label="合同名称">{c.contract_name}</Descriptions.Item>
          <Descriptions.Item label="合同类型">{c.contract_type}</Descriptions.Item>
          <Descriptions.Item label="所属项目">{c.project_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="甲方">{c.party_a || '-'}</Descriptions.Item>
          <Descriptions.Item label="乙方">{c.party_b || '-'}</Descriptions.Item>
          <Descriptions.Item label="合同金额"><MoneyText value={c.contract_amount} /></Descriptions.Item>
          <Descriptions.Item label="结算金额"><MoneyText value={c.settlement_amount} /></Descriptions.Item>
          <Descriptions.Item label="已开票"><MoneyText value={c.invoiced_amount} /></Descriptions.Item>
          <Descriptions.Item label="已收款"><MoneyText value={c.received_amount} /></Descriptions.Item>
          <Descriptions.Item label="已付款"><MoneyText value={c.paid_amount} /></Descriptions.Item>
          <Descriptions.Item label="应收款"><MoneyText value={c.receivable_amount} /></Descriptions.Item>
          <Descriptions.Item label="应付款"><MoneyText value={c.payable_amount} /></Descriptions.Item>
          <Descriptions.Item label="签订日期">{formatDate(c.signed_date)}</Descriptions.Item>
          <Descriptions.Item label="合同状态"><Tag>{c.contract_status}</Tag></Descriptions.Item>
          <Descriptions.Item label="审批状态"><Tag>{c.approval_status}</Tag></Descriptions.Item>
          <Descriptions.Item label="归档状态"><Tag>{c.archive_status}</Tag></Descriptions.Item>
          <Descriptions.Item label="合同说明" span={2}>{c.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="备注" span={2}>{c.remarks || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default ContractDetail;
