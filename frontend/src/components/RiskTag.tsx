import React from 'react';
import { Tag } from 'antd';

const RISK_COLORS: Record<string, string> = {
  低: 'green',
  中: 'gold',
  高: 'orange',
  严重: 'red',
};

const RiskTag: React.FC<{ level: string }> = ({ level }) => (
  <Tag color={RISK_COLORS[level] || 'default'}>{level}</Tag>
);

export default RiskTag;
