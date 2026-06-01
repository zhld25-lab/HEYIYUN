import apiClient from './client';
import type { ApiResponse } from '@/types/common';

export interface WorkflowStep {
  id: number;
  step_order: number;
  step_name: string;
  approver_role: string | null;
  approver_id: number | null;
  approver_name: string | null;
  status: string;
  deadline_days: number | null;
  due_at: string | null;
  acted_at: string | null;
  comment: string | null;
}

export interface WorkflowAction {
  id: number;
  step_id: number | null;
  actor_id: number | null;
  actor_name: string | null;
  action: string;
  comment: string | null;
  created_at: string;
}

export interface Workflow {
  id: number;
  business_type: string;
  business_id: number;
  project_id: number | null;
  title: string;
  workflow_type: string;
  status: string;
  current_step: number;
  total_steps: number;
  initiator_id: number | null;
  initiator_name: string | null;
  submitted_at: string | null;
  completed_at: string | null;
  remarks: string | null;
  created_at: string;
  updated_at: string;
  steps?: WorkflowStep[];
  actions?: WorkflowAction[];
}

export async function listWorkflows(params?: { status?: string; business_type?: string }): Promise<Workflow[]> {
  const { data } = await apiClient.get<ApiResponse<Workflow[]>>('/workflows', { params });
  return data.data;
}

export async function getWorkflow(id: number): Promise<Workflow> {
  const { data } = await apiClient.get<ApiResponse<Workflow>>(`/workflows/${id}`);
  return data.data;
}

export async function createWorkflow(payload: {
  business_type: string;
  business_id: number;
  project_id?: number;
  title: string;
  workflow_type: string;
  remarks?: string;
}): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>('/workflows', payload);
  return data.data;
}

export async function submitWorkflow(id: number, comment?: string): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/workflows/${id}/submit`, { comment });
  return data.data;
}

export async function approveWorkflow(id: number, comment?: string): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/workflows/${id}/approve`, { comment });
  return data.data;
}

export async function rejectWorkflow(id: number, comment?: string): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/workflows/${id}/reject`, { comment });
  return data.data;
}

export async function withdrawWorkflow(id: number, comment?: string): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/workflows/${id}/withdraw`, { comment });
  return data.data;
}

export async function urgeWorkflow(id: number, comment?: string): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/workflows/${id}/urge`, { comment });
  return data.data;
}

export async function transferWorkflow(id: number, to_user_id: number, comment?: string): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/workflows/${id}/transfer`, { to_user_id, comment });
  return data.data;
}

export async function getMyPendingWorkflows(): Promise<Workflow[]> {
  const { data } = await apiClient.get<ApiResponse<Workflow[]>>('/workflows/my-pending');
  return data.data;
}

export async function getMyDoneWorkflows(): Promise<Workflow[]> {
  const { data } = await apiClient.get<ApiResponse<Workflow[]>>('/workflows/my-done');
  return data.data;
}

export async function getMyInitiatedWorkflows(): Promise<Workflow[]> {
  const { data } = await apiClient.get<ApiResponse<Workflow[]>>('/workflows/my-initiated');
  return data.data;
}

export async function getWorkflowsByBusiness(businessType: string, businessId: number): Promise<Workflow[]> {
  const { data } = await apiClient.get<ApiResponse<Workflow[]>>(`/workflows/business/${businessType}/${businessId}`);
  return data.data;
}

export async function getProjectWorkflows(projectId: number): Promise<Workflow[]> {
  const { data } = await apiClient.get<ApiResponse<Workflow[]>>(`/projects/${projectId}/workflows`);
  return data.data;
}

export async function submitProjectApproval(projectId: number): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/projects/${projectId}/submit-approval`);
  return data.data;
}

export async function submitContractApproval(contractId: number): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/contracts/${contractId}/submit-approval`);
  return data.data;
}

export async function submitPaymentApproval(paymentId: number): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/payments/${paymentId}/submit-approval`);
  return data.data;
}

export async function submitCostApproval(costId: number): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/costs/${costId}/submit-approval`);
  return data.data;
}

export async function submitInvoiceApproval(invoiceId: number): Promise<Workflow> {
  const { data } = await apiClient.post<ApiResponse<Workflow>>(`/invoices/${invoiceId}/submit-approval`);
  return data.data;
}
