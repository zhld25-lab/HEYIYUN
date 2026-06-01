import apiClient from './client';
import type { ApiResponse, PageData } from '@/types/common';
import type { AuditLog, Project, ProjectListParams } from '@/types/project';

export async function listProjects(params: ProjectListParams): Promise<PageData<Project>> {
  const { data } = await apiClient.get<ApiResponse<PageData<Project>>>('/projects', { params });
  return data.data;
}

export async function getProject(id: number): Promise<Project> {
  const { data } = await apiClient.get<ApiResponse<Project>>(`/projects/${id}`);
  return data.data;
}

export async function createProject(payload: Record<string, unknown>): Promise<Project> {
  const { data } = await apiClient.post<ApiResponse<Project>>('/projects', payload);
  return data.data;
}

export async function updateProject(
  id: number,
  payload: Record<string, unknown>,
): Promise<Project> {
  const { data } = await apiClient.put<ApiResponse<Project>>(`/projects/${id}`, payload);
  return data.data;
}

export async function deleteProject(id: number): Promise<void> {
  await apiClient.delete(`/projects/${id}`);
}

export async function listProjectAuditLogs(projectId: number): Promise<PageData<AuditLog>> {
  const { data } = await apiClient.get<ApiResponse<PageData<AuditLog>>>('/system/audit-logs', {
    params: { resource_type: 'project', resource_id: String(projectId), page_size: 100 },
  });
  return data.data;
}
