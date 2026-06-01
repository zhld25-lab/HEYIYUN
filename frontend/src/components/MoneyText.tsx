import React from 'react';
import { Tooltip } from 'antd';
import type { MaskableNumber } from '@/types/common';
import { formatMoney, isMasked } from '@/utils/formatters';

const MoneyText: React.FC<{ value: MaskableNumber | null | undefined }> = ({ value }) => {
  if (isMasked(value)) {
    return (
      <Tooltip title="当前角色无权查看金额明细">
        <span style={{ color: '#bfbfbf', letterSpacing: 2 }}>***</span>
      </Tooltip>
    );
  }
  return <span>{formatMoney(value)}</span>;
};

export default MoneyText;
