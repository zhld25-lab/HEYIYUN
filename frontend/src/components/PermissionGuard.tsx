import React from 'react';
import { useAuthStore } from '@/store/authStore';
import { hasPermission } from '@/utils/permissions';

interface PermissionGuardProps {
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/** Renders children only when the current user holds the required permission. */
const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  children,
  fallback = null,
}) => {
  const user = useAuthStore((s) => s.user);
  if (!hasPermission(user, permission)) {
    return <>{fallback}</>;
  }
  return <>{children}</>;
};

export default PermissionGuard;
