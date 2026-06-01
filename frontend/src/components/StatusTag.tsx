import React from 'react';
import { Tag } from 'antd';

const STATUS_COLORS: Record<string, string> = {
  立项: 'default',
  报装中: 'processing',
  施工中: 'blue',
  验收中: 'cyan',
  结算中: 'gold',
  已完工: 'green',
  暂停: 'orange',
  取消: 'red',
};

const StatusTag: React.FC<{ status: string }> = ({ status }) => (
  <Tag color={STATUS_COLORS[status] || 'default'}>{status}</Tag>
);

export default StatusTag;
