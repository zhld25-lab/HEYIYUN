import { Table } from 'antd';
import type { TableProps } from 'antd';

/**
 * Thin wrapper around antd Table with enterprise defaults:
 * small size, horizontal scroll, bordered.
 */
function EnterpriseTable<RecordType extends object>(props: TableProps<RecordType>) {
  return (
    <Table<RecordType>
      size="middle"
      bordered
      scroll={{ x: 'max-content' }}
      {...props}
    />
  );
}

export default EnterpriseTable;
