import apiClient from './client';
import type { ApiResponse, PageData } from '@/types/common';
import type { Contract } from '@/types/finance';

export interface ContractListParams {
  page?: number;
  page_size?: number;
  contract_code?: string;
  contract_name?: string;
  contract_type?: string;
  project_id?: number;
  contract_status?: string;
  approval_status?: string;
  archive_status?: string;
}

export async function listContracts(params: ContractListParams): Promise<PageData<Contract>> {
  const { data } = await apiClient.get<ApiResponse<PageData<Contract>>>('/contracts', { params });
  return data.data;
}

export async function getContract(id: number): Promise<Contract> {
  const { data } = await apiClient.get<ApiResponse<Contract>>(`/contracts/${id}`);
  return data.data;
}

export async function createContract(payload: Record<string, unknown>): Promise<Contract> {
  const { data } = await apiClient.post<ApiResponse<Contract>>('/contracts', payload);
  return data.data;
}

export async function updateContract(id: number, payload: Record<string, unknown>): Promise<Contract> {
  const { data } = await apiClient.put<ApiResponse<Contract>>(`/contracts/${id}`, payload);
  return data.data;
}

export async function deleteContract(id: number): Promise<void> {
  await apiClient.delete(`/contracts/${id}`);
}
