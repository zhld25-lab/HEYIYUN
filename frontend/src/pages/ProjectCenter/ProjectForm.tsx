import React, { useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Space,
  Divider,
  message,
  Spin,
} from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { createProject, updateProject, getProject } from '@/api/projects';
import PageHeader from '@/components/PageHeader';
import { PROJECT_TYPES, VOLTAGE_LEVELS, PROJECT_STATUSES, RISK_LEVELS } from '@/utils/constants';

const { TextArea } = Input;
const sectionTitle = (t: string) => <Divider orientation="left" orientationMargin={0}>{t}</Divider>;

const DATE_FIELDS = ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date'];

const ProjectForm: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { id } = useParams();
  const isEdit = Boolean(id);
  const [form] = Form.useForm();

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => getProject(Number(id)),
    enabled: isEdit,
  });

  useEffect(() => {
    if (project) {
      const values: Record<string, unknown> = { ...project };
      DATE_FIELDS.forEach((f) => {
        values[f] = project[f as keyof typeof project] ? dayjs(project[f as keyof typeof project] as string) : null;
      });
      // Masked amounts (string "***") must not be written back into number fields.
      ['contract_amount', 'target_cost', 'actual_cost', 'received_amount', 'paid_amount'].forEach((f) => {
        if (typeof values[f] === 'string') values[f] = undefined;
      });
      form.setFieldsValue(values);
    }
  }, [project, form]);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      isEdit ? updateProject(Number(id), payload) : createProject(payload),
    onSuccess: () => {
      message.success(isEdit ? '项目更新成功' : '项目创建成功');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      navigate('/projects');
    },
  });

  const onFinish = (values: Record<string, unknown>) => {
    const payload = { ...values };
    DATE_FIELDS.forEach((f) => {
      payload[f] = values[f] ? (values[f] as dayjs.Dayjs).format('YYYY-MM-DD') : null;
    });
    mutation.mutate(payload);
  };

  return (
    <div>
      <PageHeader title={isEdit ? '编辑项目' : '新建立项'} description="电力工程项目立项与基础信息维护。" />
      <Spin spinning={isEdit && isLoading}>
        <Card>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            initialValues={{ project_status: '立项', risk_level: '低' }}
          >
            {sectionTitle('基本信息')}
            <div className="form-grid">
              <Form.Item name="project_code" label="项目编号" rules={[{ required: true, message: '请输入项目编号' }]}>
                <Input placeholder="如 PJ-2025-001" disabled={isEdit} />
              </Form.Item>
              <Form.Item name="project_name" label="项目名称" rules={[{ required: true, message: '请输入项目名称' }]}>
                <Input placeholder="项目名称" />
              </Form.Item>
              <Form.Item name="project_type" label="项目类型" rules={[{ required: true, message: '请选择项目类型' }]}>
                <Select options={PROJECT_TYPES.map((t) => ({ value: t, label: t }))} />
              </Form.Item>
              <Form.Item name="voltage_level" label="电压等级" rules={[{ required: true, message: '请选择电压等级' }]}>
                <Select options={VOLTAGE_LEVELS.map((t) => ({ value: t, label: t }))} />
              </Form.Item>
              <Form.Item name="project_location" label="项目地址">
                <Input placeholder="项目地址" />
              </Form.Item>
              <Form.Item name="region" label="所属区域">
                <Input placeholder="如 华东" />
              </Form.Item>
              <Form.Item name="project_status" label="项目状态">
                <Select options={PROJECT_STATUSES.map((t) => ({ value: t, label: t }))} />
              </Form.Item>
            </div>

            {sectionTitle('参建单位')}
            <div className="form-grid">
              <Form.Item name="owner_unit" label="建设单位">
                <Input />
              </Form.Item>
              <Form.Item name="construction_unit" label="施工单位">
                <Input />
              </Form.Item>
              <Form.Item name="design_unit" label="设计单位">
                <Input />
              </Form.Item>
              <Form.Item name="supervision_unit" label="监理单位">
                <Input />
              </Form.Item>
              <Form.Item name="project_manager_id" label="项目经理(用户ID)">
                <InputNumber style={{ width: '100%' }} min={1} placeholder="项目经理用户ID" />
              </Form.Item>
            </div>

            {sectionTitle('时间计划')}
            <div className="form-grid">
              <Form.Item name="planned_start_date" label="计划开始日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item
                name="planned_end_date"
                label="计划结束日期"
                dependencies={['planned_start_date']}
                rules={[
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      const start = getFieldValue('planned_start_date');
                      if (!value || !start || value.isAfter(start)) return Promise.resolve();
                      return Promise.reject(new Error('计划结束日期必须晚于计划开始日期'));
                    },
                  }),
                ]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="actual_start_date" label="实际开始日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="actual_end_date" label="实际结束日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </div>

            {sectionTitle('金额预算（单位：元）')}
            <div className="form-grid">
              <Form.Item name="contract_amount" label="合同金额" rules={[{ type: 'number', min: 0, message: '金额不能为负' }]}>
                <InputNumber style={{ width: '100%' }} min={0} step={10000} />
              </Form.Item>
              <Form.Item name="target_cost" label="目标成本" rules={[{ type: 'number', min: 0, message: '金额不能为负' }]}>
                <InputNumber style={{ width: '100%' }} min={0} step={10000} />
              </Form.Item>
              <Form.Item name="actual_cost" label="实际成本" rules={[{ type: 'number', min: 0, message: '金额不能为负' }]}>
                <InputNumber style={{ width: '100%' }} min={0} step={10000} />
              </Form.Item>
              <Form.Item name="received_amount" label="已收款">
                <InputNumber style={{ width: '100%' }} min={0} step={10000} />
              </Form.Item>
              <Form.Item name="paid_amount" label="已付款">
                <InputNumber style={{ width: '100%' }} min={0} step={10000} />
              </Form.Item>
            </div>

            {sectionTitle('进度资料')}
            <div className="form-grid">
              <Form.Item name="production_progress" label="产值进度 (0-1)">
                <InputNumber style={{ width: '100%' }} min={0} max={1} step={0.01} />
              </Form.Item>
              <Form.Item name="collection_progress" label="收款进度 (0-1)">
                <InputNumber style={{ width: '100%' }} min={0} max={1} step={0.01} />
              </Form.Item>
              <Form.Item name="document_completion_rate" label="资料完整率 (0-1)">
                <InputNumber style={{ width: '100%' }} min={0} max={1} step={0.01} />
              </Form.Item>
              <Form.Item name="risk_level" label="风险等级">
                <Select options={RISK_LEVELS.map((t) => ({ value: t, label: t }))} />
              </Form.Item>
            </div>

            {sectionTitle('项目说明')}
            <Form.Item name="description" label="项目描述">
              <TextArea rows={3} />
            </Form.Item>
            <Form.Item name="remarks" label="备注">
              <TextArea rows={2} />
            </Form.Item>

            <Space>
              <Button type="primary" htmlType="submit" loading={mutation.isPending}>
                保存
              </Button>
              <Button
                onClick={() => message.info('审批流引擎将在后续阶段实现')}
              >
                保存并提交审批
              </Button>
              <Button onClick={() => navigate('/projects')}>取消</Button>
            </Space>
          </Form>
        </Card>
      </Spin>
    </div>
  );
};

export default ProjectForm;
