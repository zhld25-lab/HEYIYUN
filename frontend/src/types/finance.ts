import type { MaskableNumber } from './common';

export interface Contract {
  id: number;
  contract_code: string;
  contract_name: string;
  contract_type: string;
  project_id: number;
  project_name: string | null;
  party_a: string | null;
  party_b: string | null;
  contract_amount: MaskableNumber;
  settlement_amount: MaskableNumber;
  invoiced_amount: MaskableNumber;
  received_amount: MaskableNumber;
  paid_amount: MaskableNumber;
  receivable_amount: MaskableNumber;
  payable_amount: MaskableNumber;
  contract_status: string;
  approval_status: string;
  archive_status: string;
  signed_date: string | null;
  description: string | null;
  remarks: string | null;
}

export interface CostRecord {
  id: number;
  cost_code: string;
  cost_type: string;
  project_id: number;
  project_name: string | null;
  contract_id: number | null;
  contract_name: string | null;
  supplier_name: string | null;
  amount: MaskableNumber;
  occurred_date: string | null;
  handler_name: string | null;
  approval_status: string;
  invoice_status: string;
  payment_status: string;
  remarks: string | null;
}

export interface Payment {
  id: number;
  payment_code: string;
  project_id: number;
  project_name: string | null;
  contract_id: number | null;
  contract_name: string | null;
  payee_name: string | null;
  requested_amount: MaskableNumber;
  paid_amount: MaskableNumber;
  payment_date: string | null;
  payment_status: string;
  approval_status: string;
  remarks: string | null;
}

export interface Receipt {
  id: number;
  receipt_code: string;
  project_id: number;
  project_name: string | null;
  contract_id: number | null;
  contract_name: string | null;
  payer_name: string | null;
  receipt_amount: MaskableNumber;
  receipt_date: string | null;
  planned_receipt_date: string | null;
  is_overdue: boolean;
  remarks: string | null;
}

export interface Invoice {
  id: number;
  invoice_code: string;
  invoice_type: string;
  invoice_direction: string;
  project_id: number;
  project_name: string | null;
  contract_id: number | null;
  contract_name: string | null;
  amount: MaskableNumber;
  tax_rate: MaskableNumber;
  invoice_date: string | null;
  certification_status: string;
  remarks: string | null;
}

export interface ProjectFinanceSummary {
  project_id: number;
  contract_amount: MaskableNumber;
  target_cost: MaskableNumber;
  actual_cost: MaskableNumber;
  received_amount: MaskableNumber;
  paid_amount: MaskableNumber;
  receivable_amount: MaskableNumber;
  payable_amount: MaskableNumber;
  profit: MaskableNumber;
  profit_margin: MaskableNumber;
  collection_progress: number;
  cost_ratio: number;
}
