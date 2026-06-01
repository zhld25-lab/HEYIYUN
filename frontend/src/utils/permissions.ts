import type { User } from '@/types/auth';

export const PERMISSIONS = {
  PROJECT_VIEW: 'project:view',
  PROJECT_CREATE: 'project:create',
  PROJECT_UPDATE: 'project:update',
  PROJECT_DELETE: 'project:delete',
  DASHBOARD_VIEW: 'dashboard:view',
  FINANCE_VIEW: 'finance:view',
  CONTRACT_VIEW: 'contract:view',
  CONTRACT_CREATE: 'contract:create',
  CONTRACT_UPDATE: 'contract:update',
  CONTRACT_DELETE: 'contract:delete',
  FINANCE_EDIT: 'finance:edit',
  FINANCE_DELETE: 'finance:delete',
  AUDIT_VIEW: 'audit:view',
  USER_VIEW: 'user:view',
  SYSTEM_MANAGE: 'system:manage',
  WORKFLOW_VIEW: 'workflow:view',
  WORKFLOW_CREATE: 'workflow:create',
  WORKFLOW_APPROVE: 'workflow:approve',
} as const;

export function hasPermission(user: User | null, code: string): boolean {
  if (!user) return false;
  return user.permission_codes.includes(code);
}

export function canViewFinance(user: User | null): boolean {
  return hasPermission(user, PERMISSIONS.FINANCE_VIEW);
}
