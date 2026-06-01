import apiClient from './client';
import type { ApiResponse, PageData } from '@/types/common';
import type {
  CostRecord,
  Invoice,
  Payment,
  ProjectFinanceSummary,
  Receipt,
} from '@/types/finance';
import type { Contract } from '@/types/finance';

/** Generic paginated list helper for a finance resource. */
function makeList<T>(path: string) {
  return async (params: Record<string, unknown>): Promise<PageData<T>> => {
    const { data } = await apiClient.get<ApiResponse<PageData<T>>>(path, { params });
    return data.data;
  };
}
function makeCreate<T>(path: string) {
  return async (payload: Record<string, unknown>): Promise<T> => {
    const { data } = await apiClient.post<ApiResponse<T>>(path, payload);
    return data.data;
  };
}
function makeUpdate<T>(path: string) {
  return async (id: number, payload: Record<string, unknown>): Promise<T> => {
    const { data } = await apiClient.put<ApiResponse<T>>(`${path}/${id}`, payload);
    return data.data;
  };
}
function makeDelete(path: string) {
  return async (id: number): Promise<void> => {
    await apiClient.delete(`${path}/${id}`);
  };
}

export const costApi = {
  list: makeList<CostRecord>('/costs'),
  create: makeCreate<CostRecord>('/costs'),
  update: makeUpdate<CostRecord>('/costs'),
  remove: makeDelete('/costs'),
};
export const paymentApi = {
  list: makeList<Payment>('/payments'),
  create: makeCreate<Payment>('/payments'),
  update: makeUpdate<Payment>('/payments'),
  remove: makeDelete('/payments'),
};
export const receiptApi = {
  list: makeList<Receipt>('/receipts'),
  create: makeCreate<Receipt>('/receipts'),
  update: makeUpdate<Receipt>('/receipts'),
  remove: makeDelete('/receipts'),
};
export const invoiceApi = {
  list: makeList<Invoice>('/invoices'),
  create: makeCreate<Invoice>('/invoices'),
  update: makeUpdate<Invoice>('/invoices'),
  remove: makeDelete('/invoices'),
};

// ----- project-scoped reads (for project detail page) -----
export async function getProjectContracts(projectId: number): Promise<Contract[]> {
  const { data } = await apiClient.get<ApiResponse<Contract[]>>(`/projects/${projectId}/contracts`);
  return data.data;
}
export async function getProjectCosts(projectId: number): Promise<CostRecord[]> {
  const { data } = await apiClient.get<ApiResponse<CostRecord[]>>(`/projects/${projectId}/costs`);
  return data.data;
}
export async function getProjectPayments(projectId: number): Promise<Payment[]> {
  const { data } = await apiClient.get<ApiResponse<Payment[]>>(`/projects/${projectId}/payments`);
  return data.data;
}
export async function getProjectReceipts(projectId: number): Promise<Receipt[]> {
  const { data } = await apiClient.get<ApiResponse<Receipt[]>>(`/projects/${projectId}/receipts`);
  return data.data;
}
export async function getProjectInvoices(projectId: number): Promise<Invoice[]> {
  const { data } = await apiClient.get<ApiResponse<Invoice[]>>(`/projects/${projectId}/invoices`);
  return data.data;
}
export async function getProjectFinanceSummary(projectId: number): Promise<ProjectFinanceSummary> {
  const { data } = await apiClient.get<ApiResponse<ProjectFinanceSummary>>(
    `/projects/${projectId}/finance-summary`,
  );
  return data.data;
}
