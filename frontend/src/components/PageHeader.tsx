import React from 'react';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

interface PageHeaderProps {
  title: string;
  description?: string;
  extra?: React.ReactNode;
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, description, extra }) => (
  <div className="page-header">
    <div>
      <Title level={4} style={{ marginBottom: description ? 4 : 0 }}>
        {title}
      </Title>
      {description && (
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          {description}
        </Paragraph>
      )}
    </div>
    {extra && <div className="page-header-extra">{extra}</div>}
  </div>
);

export default PageHeader;
