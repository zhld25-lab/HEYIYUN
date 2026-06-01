import apiClient from './client';
import type { ApiResponse } from '@/types/common';
import type { MaskableNumber } from '@/types/common';

export interface DashboardSummary {
  project_count: number;
  active_project_count: number;
  contract_amount: MaskableNumber;
  received_amount: MaskableNumber;
  paid_amount: MaskableNumber;
  current_profit: MaskableNumber;
  high_risk_count: number;
}

export interface ProjectStatusItem {
  status: string;
  count: number;
}

export async function getSummary(): Promise<DashboardSummary> {
  const { data } = await apiClient.get<ApiResponse<DashboardSummary>>('/dashboard/summary');
  return data.data;
}

export async function getProjectStatus(): Promise<ProjectStatusItem[]> {
  const { data } = await apiClient.get<ApiResponse<ProjectStatusItem[]>>(
    '/dashboard/project-status',
  );
  return data.data;
}
