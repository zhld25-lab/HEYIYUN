import React, { useState } from 'react';
import { Card, Tabs, Table, Descriptions } from 'antd';
import { useQuery } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import apiClient from '@/api/client';
import type { ApiResponse, PageData } from '@/types/common';
import type { AuditLog } from '@/types/project';
import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { PERMISSIONS } from '@/utils/permissions';
import { useAuthStore } from '@/store/authStore';
import { formatDate } from '@/utils/formatters';

const ACTION_LABEL: Record<string, string> = { CREATE: '创建', UPDATE: '更新', DELETE: '删除' };

async function fetchAuditLogs(page: number, pageSize: number): Promise<PageData<AuditLog>> {
  const { data } = await apiClient.get<ApiResponse<PageData<AuditLog>>>('/system/audit-logs', {
    params: { page, page_size: pageSize },
  });
  return data.data;
}

const AuditLogPanel: React.FC = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs', page, pageSize],
    queryFn: () => fetchAuditLogs(page, pageSize),
  });

  const columns: ColumnsType<AuditLog> = [
    { title: '时间', dataIndex: 'created_at', render: (v) => formatDate(v), width: 180 },
    { title: '操作人', dataIndex: 'username', width: 140 },
    { title: '操作', dataIndex: 'action', width: 90, render: (v) => ACTION_LABEL[v] || v },
    { title: '资源类型', dataIndex: 'resource_type', width: 120 },
    { title: '资源ID', dataIndex: 'resource_id', width: 100 },
    { title: '详情', dataIndex: 'detail' },
    { title: 'IP', dataIndex: 'ip_address', width: 140 },
  ];

  return (
    <Table<AuditLog>
      rowKey="id"
      loading={isLoading}
      columns={columns}
      dataSource={data?.items ?? []}
      pagination={{
        current: page,
        pageSize,
        total: data?.total ?? 0,
        showSizeChanger: true,
        onChange: (p, ps) => {
          setPage(p);
          setPageSize(ps);
        },
      }}
    />
  );
};

const SystemSettings: React.FC = () => {
  const user = useAuthStore((s) => s.user);

  const items = [
    {
      key: 'profile',
      label: '当前账户',
      children: (
        <Descriptions bordered column={1} size="middle" style={{ maxWidth: 520 }}>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="姓名">{user?.full_name}</Descriptions.Item>
          <Descriptions.Item label="角色">{user?.role_name}</Descriptions.Item>
          <Descriptions.Item label="权限数量">{user?.permission_codes.length}</Descriptions.Item>
        </Descriptions>
      ),
    },
    {
      key: 'audit',
      label: '操作日志',
      children: (
        <PermissionGuard
          permission={PERMISSIONS.AUDIT_VIEW}
          fallback={<div style={{ color: '#999' }}>当前角色无权查看操作日志。</div>}
        >
          <AuditLogPanel />
        </PermissionGuard>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="系统设置" description="账户信息与系统操作审计日志。" />
      <Card>
        <Tabs items={items} />
      </Card>
    </div>
  );
};

export default SystemSettings;
