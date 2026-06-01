import type { MaskableNumber } from './common';

export interface Project {
  id: number;
  project_code: string;
  project_name: string;
  project_type: string;
  voltage_level: string | null;
  project_location: string | null;
  region: string | null;
  project_status: string;

  owner_unit: string | null;
  construction_unit: string | null;
  design_unit: string | null;
  supervision_unit: string | null;
  project_manager_id: number | null;
  project_manager_name: string | null;

  planned_start_date: string | null;
  planned_end_date: string | null;
  actual_start_date: string | null;
  actual_end_date: string | null;

  contract_amount: MaskableNumber;
  target_cost: MaskableNumber;
  actual_cost: MaskableNumber;
  received_amount: MaskableNumber;
  paid_amount: MaskableNumber;
  receivable_amount: MaskableNumber;
  payable_amount: MaskableNumber;
  profit: MaskableNumber;
  profit_margin: MaskableNumber;

  production_progress: number;
  collection_progress: number;
  cost_ratio: number;
  document_completion_rate: number;
  risk_level: string;

  description: string | null;
  remarks: string | null;

  created_at: string | null;
  updated_at: string | null;
}

export interface ProjectListParams {
  page?: number;
  page_size?: number;
  project_name?: string;
  project_code?: string;
  project_type?: string;
  voltage_level?: string;
  project_status?: string;
  risk_level?: string;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  username: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  detail: string | null;
  ip_address: string | null;
  created_at: string | null;
}
