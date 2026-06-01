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

export interface DashboardFinanceSummary {
  total_contract_amount: MaskableNumber;
  total_actual_cost: MaskableNumber;
  total_received: MaskableNumber;
  total_paid: MaskableNumber;
  total_receivable: MaskableNumber;
  total_payable: MaskableNumber;
  total_profit: MaskableNumber;
}
export interface CashflowItem {
  month: string;
  received: MaskableNumber;
  paid: MaskableNumber;
  net: MaskableNumber;
}
export interface CostBreakdownItem {
  cost_type: string;
  amount: MaskableNumber;
}
export interface ProjectProfitItem {
  project_id: number;
  project_name: string;
  profit: MaskableNumber;
}

export async function getFinanceSummary(): Promise<DashboardFinanceSummary> {
  const { data } = await apiClient.get<ApiResponse<DashboardFinanceSummary>>(
    '/dashboard/finance-summary',
  );
  return data.data;
}
export async function getCashflow(): Promise<CashflowItem[]> {
  const { data } = await apiClient.get<ApiResponse<CashflowItem[]>>('/dashboard/cashflow');
  return data.data;
}
export async function getCostBreakdown(): Promise<CostBreakdownItem[]> {
  const { data } = await apiClient.get<ApiResponse<CostBreakdownItem[]>>('/dashboard/cost-breakdown');
  return data.data;
}
export async function getProjectProfitTop(): Promise<ProjectProfitItem[]> {
  const { data } = await apiClient.get<ApiResponse<ProjectProfitItem[]>>(
    '/dashboard/project-profit-top',
  );
  return data.data;
}
