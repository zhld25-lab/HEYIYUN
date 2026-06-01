import React, { useState } from 'react';
import {
  Drawer, Descriptions, Timeline, Button, Space, Modal, Input, Typography, Tag, Divider, message,
} from 'antd';
import {
  CheckCircleOutlined, CloseCircleOutlined, RollbackOutlined, BellOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getWorkflow, approveWorkflow, rejectWorkflow, withdrawWorkflow, urgeWorkflow,
  type Workflow,
} from '@/api/workflows';
import { WorkflowStatusTag, WorkflowActionTag } from './WorkflowStatusTag';
import { useAuthStore } from '@/store/authStore';
import { hasPermission } from '@/utils/permissions';
import { PERMISSIONS } from '@/utils/permissions';

const { Text } = Typography;
const { TextArea } = Input;

interface Props {
  workflowId: number | null;
  onClose: () => void;
}

type ActionType = 'approve' | 'reject' | 'withdraw' | 'urge';

const WorkflowDetailDrawer: React.FC<Props> = ({ workflowId, onClose }) => {
  const { user } = useAuthStore();
  const qc = useQueryClient();
  const [actionModal, setActionModal] = useState<ActionType | null>(null);
  const [comment, setComment] = useState('');

  const { data: wf, isLoading } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => getWorkflow(workflowId!),
    enabled: !!workflowId,
  });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['workflow', workflowId] });
    qc.invalidateQueries({ queryKey: ['workflows'] });
    qc.invalidateQueries({ queryKey: ['my-pending-workflows'] });
  };

  const approveMut = useMutation({
    mutationFn: (c: string) => approveWorkflow(workflowId!, c),
    onSuccess: () => { message.success('审批通过'); invalidate(); setActionModal(null); },
    onError: (e: any) => message.error(e?.response?.data?.detail || '操作失败'),
  });
  const rejectMut = useMutation({
    mutationFn: (c: string) => rejectWorkflow(workflowId!, c),
    onSuccess: () => { message.success('已驳回'); invalidate(); setActionModal(null); },
    onError: (e: any) => message.error(e?.response?.data?.detail || '操作失败'),
  });
  const withdrawMut = useMutation({
    mutationFn: (c: string) => withdrawWorkflow(workflowId!, c),
    onSuccess: () => { message.success('已撤回'); invalidate(); setActionModal(null); },
    onError: (e: any) => message.error(e?.response?.data?.detail || '操作失败'),
  });
  const urgeMut = useMutation({
    mutationFn: (c: string) => urgeWorkflow(workflowId!, c),
    onSuccess: () => { message.success('催办通知已发送'); invalidate(); setActionModal(null); },
    onError: (e: any) => message.error(e?.response?.data?.detail || '操作失败'),
  });

  const handleAction = () => {
    if (actionModal === 'approve') approveMut.mutate(comment);
    else if (actionModal === 'reject') rejectMut.mutate(comment);
    else if (actionModal === 'withdraw') withdrawMut.mutate(comment);
    else if (actionModal === 'urge') urgeMut.mutate(comment || '请尽快处理');
  };

  const canApprove = user && hasPermission(user, PERMISSIONS.WORKFLOW_APPROVE);
  const canWithdraw = user && wf?.initiator_id === user.id;

  const stepItems = wf?.steps?.map(s => ({
    color: s.status === 'approved' ? 'green' : s.status === 'rejected' ? 'red' : s.status === 'pending' ? 'blue' : 'gray',
    children: (
      <div>
        <b>步骤 {s.step_order}：{s.step_name}</b>
        <Tag style={{ marginLeft: 8 }} color={s.status === 'approved' ? 'green' : s.status === 'rejected' ? 'red' : s.status === 'pending' ? 'processing' : 'default'}>
          {s.status === 'approved' ? '已通过' : s.status === 'rejected' ? '已驳回' : s.status === 'pending' ? '待审批' : '等待中'}
        </Tag>
        {s.approver_name && <Text type="secondary"> 审批人：{s.approver_name}</Text>}
        {s.acted_at && <Text type="secondary"> · {s.acted_at.slice(0, 10)}</Text>}
        {s.comment && <div><Text type="secondary">{s.comment}</Text></div>}
      </div>
    ),
  })) ?? [];

  const actionItems = wf?.actions?.map(a => ({
    color: a.action === 'approve' ? 'green' : a.action === 'reject' ? 'red' : 'blue',
    children: (
      <div>
        <WorkflowActionTag action={a.action} />
        <Text style={{ marginLeft: 8 }}>{a.actor_name}</Text>
        <Text type="secondary" style={{ marginLeft: 8 }}>{a.created_at?.slice(0, 16)}</Text>
        {a.comment && <div><Text type="secondary">{a.comment}</Text></div>}
      </div>
    ),
  })) ?? [];

  return (
    <>
      <Drawer
        title="审批流详情"
        open={!!workflowId}
        onClose={onClose}
        width={600}
        loading={isLoading}
        extra={
          wf && (
            <Space>
              {canApprove && wf.status === 'pending' && (
                <>
                  <Button type="primary" icon={<CheckCircleOutlined />} onClick={() => { setComment(''); setActionModal('approve'); }}>
                    审批通过
                  </Button>
                  <Button danger icon={<CloseCircleOutlined />} onClick={() => { setComment(''); setActionModal('reject'); }}>
                    驳回
                  </Button>
                  <Button icon={<BellOutlined />} onClick={() => { setComment(''); setActionModal('urge'); }}>
                    催办
                  </Button>
                </>
              )}
              {canWithdraw && wf.status === 'pending' && (
                <Button icon={<RollbackOutlined />} onClick={() => { setComment(''); setActionModal('withdraw'); }}>
                  撤回
                </Button>
              )}
            </Space>
          )
        }
      >
        {wf && (
          <>
            <Descriptions column={2} size="small" bordered>
              <Descriptions.Item label="标题" span={2}>{wf.title}</Descriptions.Item>
              <Descriptions.Item label="流程类型">{wf.workflow_type}</Descriptions.Item>
              <Descriptions.Item label="状态"><WorkflowStatusTag status={wf.status} /></Descriptions.Item>
              <Descriptions.Item label="发起人">{wf.initiator_name}</Descriptions.Item>
              <Descriptions.Item label="提交时间">{wf.submitted_at?.slice(0, 16) ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="当前步骤">{wf.current_step} / {wf.total_steps}</Descriptions.Item>
              <Descriptions.Item label="完成时间">{wf.completed_at?.slice(0, 16) ?? '-'}</Descriptions.Item>
              {wf.remarks && <Descriptions.Item label="备注" span={2}>{wf.remarks}</Descriptions.Item>}
            </Descriptions>

            <Divider>审批步骤</Divider>
            <Timeline items={stepItems} />

            <Divider>操作记录</Divider>
            <Timeline items={actionItems} />
          </>
        )}
      </Drawer>

      <Modal
        open={!!actionModal}
        title={
          actionModal === 'approve' ? '确认审批通过'
          : actionModal === 'reject' ? '驳回原因'
          : actionModal === 'withdraw' ? '确认撤回'
          : '催办备注'
        }
        onOk={handleAction}
        onCancel={() => setActionModal(null)}
        okButtonProps={{ danger: actionModal === 'reject' }}
      >
        <TextArea
          rows={3}
          value={comment}
          onChange={e => setComment(e.target.value)}
          placeholder={actionModal === 'reject' ? '请说明驳回原因（必填）' : '备注（可选）'}
        />
      </Modal>
    </>
  );
};

export default WorkflowDetailDrawer;
