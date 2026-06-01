import React from 'react';
import { Tag } from 'antd';

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: '草稿' },
  pending: { color: 'processing', label: '审批中' },
  approved: { color: 'success', label: '已批准' },
  rejected: { color: 'error', label: '已驳回' },
  withdrawn: { color: 'warning', label: '已撤回' },
};

const ACTION_LABELS: Record<string, { color: string; label: string }> = {
  submit: { color: 'blue', label: '提交' },
  approve: { color: 'green', label: '审批通过' },
  reject: { color: 'red', label: '驳回' },
  withdraw: { color: 'orange', label: '撤回' },
  urge: { color: 'gold', label: '催办' },
  transfer: { color: 'purple', label: '转办' },
};

export const WorkflowStatusTag: React.FC<{ status: string }> = ({ status }) => {
  const cfg = STATUS_CONFIG[status] ?? { color: 'default', label: status };
  return <Tag color={cfg.color}>{cfg.label}</Tag>;
};

export const WorkflowActionTag: React.FC<{ action: string }> = ({ action }) => {
  const cfg = ACTION_LABELS[action] ?? { color: 'default', label: action };
  return <Tag color={cfg.color}>{cfg.label}</Tag>;
};
