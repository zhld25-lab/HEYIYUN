import React, { useMemo, useState } from 'react';
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  Switch,
  Space,
  Modal,
  Popconfirm,
  Divider,
  message,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import EnterpriseTable from './EnterpriseTable';
import type { PageData } from '@/types/common';

const { TextArea } = Input;

export interface FieldConfig {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'date' | 'textarea' | 'switch';
  options?: { value: string | number; label: string }[];
  required?: boolean;
  section?: string;
  disabledOnEdit?: boolean;
  step?: number;
}

interface ResourceManagerProps<T extends { id: number }> {
  title: string;
  queryKey: unknown[];
  fetchList: (params: Record<string, unknown>) => Promise<PageData<T>>;
  columns: ColumnsType<T>;
  fields: FieldConfig[];
  dateFields?: string[];
  numberFields?: string[];
  canCreate?: boolean;
  canEdit?: boolean;
  canDelete?: boolean;
  createFn?: (payload: Record<string, unknown>) => Promise<T>;
  updateFn?: (id: number, payload: Record<string, unknown>) => Promise<T>;
  removeFn?: (id: number) => Promise<void>;
  /** Fixed params merged into every request and into new-record defaults. */
  fixedParams?: Record<string, unknown>;
  filtersSlot?: React.ReactNode;
  filterParams?: Record<string, unknown>;
  /** Extra per-row actions (e.g. a 查看 link), rendered before edit/delete. */
  rowActions?: (record: T) => React.ReactNode;
}

function ResourceManager<T extends { id: number }>(props: ResourceManagerProps<T>) {
  const {
    title,
    queryKey,
    fetchList,
    columns,
    fields,
    dateFields = [],
    numberFields = [],
    canCreate,
    canEdit,
    canDelete,
    createFn,
    updateFn,
    removeFn,
    fixedParams = {},
    filtersSlot,
    filterParams = {},
    rowActions,
  } = props;

  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<T | null>(null);
  const [form] = Form.useForm();

  const params = { ...fixedParams, ...filterParams, page, page_size: pageSize };
  const { data, isLoading } = useQuery({
    queryKey: [...queryKey, params],
    queryFn: () => fetchList(params),
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey });

  const saveMutation = useMutation({
    mutationFn: async (values: Record<string, unknown>) => {
      const payload: Record<string, unknown> = { ...values };
      dateFields.forEach((f) => {
        payload[f] = values[f] ? (values[f] as dayjs.Dayjs).format('YYYY-MM-DD') : null;
      });
      if (editing && updateFn) return updateFn(editing.id, payload);
      if (!editing && createFn) return createFn({ ...fixedParams, ...payload });
      throw new Error('操作不被允许');
    },
    onSuccess: () => {
      message.success(editing ? '更新成功' : '创建成功');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      invalidate();
    },
  });

  const removeMutation = useMutation({
    mutationFn: (id: number) => removeFn!(id),
    onSuccess: () => {
      message.success('删除成功');
      invalidate();
    },
  });

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setOpen(true);
  };

  const openEdit = (record: T) => {
    setEditing(record);
    const values: Record<string, unknown> = { ...record };
    dateFields.forEach((f) => {
      const v = (record as Record<string, unknown>)[f];
      values[f] = v ? dayjs(v as string) : null;
    });
    // masked amounts ('***') must not be written back to number inputs
    numberFields.forEach((f) => {
      if (typeof values[f] === 'string') values[f] = undefined;
    });
    form.setFieldsValue(values);
    setOpen(true);
  };

  const actionColumn: ColumnsType<T>[number] = {
    title: '操作',
    key: 'action',
    fixed: 'right',
    width: 150,
    render: (_, record) => (
      <Space size="small">
        {rowActions?.(record)}
        {canEdit && updateFn && (
          <Button type="link" size="small" onClick={() => openEdit(record)}>
            编辑
          </Button>
        )}
        {canDelete && removeFn && (
          <Popconfirm title="确认删除？" onConfirm={() => removeMutation.mutate(record.id)}>
            <Button type="link" size="small" danger>
              删除
            </Button>
          </Popconfirm>
        )}
      </Space>
    ),
  };

  const hasActions = Boolean(rowActions) || (canEdit && updateFn) || (canDelete && removeFn);
  const allColumns = hasActions ? [...columns, actionColumn] : columns;

  const sections = useMemo(() => {
    const order: string[] = [];
    const map: Record<string, FieldConfig[]> = {};
    fields.forEach((f) => {
      const s = f.section || '';
      if (!(s in map)) {
        map[s] = [];
        order.push(s);
      }
      map[s].push(f);
    });
    return order.map((s) => ({ name: s, fields: map[s] }));
  }, [fields]);

  const renderField = (f: FieldConfig) => {
    switch (f.type) {
      case 'number':
        return <InputNumber style={{ width: '100%' }} step={f.step ?? 10000} />;
      case 'select':
        return <Select allowClear options={f.options} />;
      case 'date':
        return <DatePicker style={{ width: '100%' }} />;
      case 'textarea':
        return <TextArea rows={2} />;
      case 'switch':
        return <Switch />;
      default:
        return <Input />;
    }
  };

  return (
    <Card bodyStyle={{ paddingTop: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
        <div>{filtersSlot}</div>
        {canCreate && createFn && (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            新增{title}
          </Button>
        )}
      </div>
      <EnterpriseTable<T>
        rowKey="id"
        loading={isLoading}
        columns={allColumns}
        dataSource={data?.items ?? []}
        pagination={{
          current: page,
          pageSize,
          total: data?.total ?? 0,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
        }}
      />
      <Modal
        title={editing ? `编辑${title}` : `新增${title}`}
        open={open}
        onOk={() => form.submit()}
        confirmLoading={saveMutation.isPending}
        onCancel={() => {
          setOpen(false);
          setEditing(null);
        }}
        width={720}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={(v) => saveMutation.mutate(v)}>
          {sections.map((section) => (
            <React.Fragment key={section.name || 'default'}>
              {section.name && (
                <Divider orientation="left" orientationMargin={0}>
                  {section.name}
                </Divider>
              )}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0 16px' }}>
                {section.fields.map((f) => (
                  <Form.Item
                    key={f.name}
                    name={f.name}
                    label={f.label}
                    valuePropName={f.type === 'switch' ? 'checked' : undefined}
                    rules={f.required ? [{ required: true, message: `请填写${f.label}` }] : undefined}
                  >
                    {React.cloneElement(renderField(f), {
                      disabled: f.disabledOnEdit && Boolean(editing),
                    })}
                  </Form.Item>
                ))}
              </div>
            </React.Fragment>
          ))}
        </Form>
      </Modal>
    </Card>
  );
}

export default ResourceManager;
