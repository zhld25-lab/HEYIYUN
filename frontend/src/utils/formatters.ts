import type { MaskableNumber } from '@/types/common';

export const MASK = '***';

/** Format a (possibly masked) money value in 万元. */
export function formatMoney(value: MaskableNumber | null | undefined): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'string') return value; // already masked as ***
  if (Number.isNaN(value)) return '-';
  const wan = value / 10000;
  return `¥${wan.toLocaleString('zh-CN', { maximumFractionDigits: 2 })} 万`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '-';
  return `${(value * 100).toFixed(1)}%`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return '-';
  return value.slice(0, 10);
}

export function isMasked(value: MaskableNumber | null | undefined): boolean {
  return typeof value === 'string';
}
