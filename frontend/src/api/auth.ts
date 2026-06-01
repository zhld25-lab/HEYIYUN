import apiClient from './client';
import type { ApiResponse } from '@/types/common';
import type { LoginRequest, TokenData, User } from '@/types/auth';

export async function login(payload: LoginRequest): Promise<TokenData> {
  const { data } = await apiClient.post<ApiResponse<TokenData>>('/auth/login', payload);
  return data.data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<ApiResponse<User>>('/auth/me');
  return data.data;
}
