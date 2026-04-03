import api from "./api";
import type { WorkLog, CreateWorkLogRequest, PageResponse } from "@/types";

export async function getWorkLogs(params?: {
  page?: number;
  size?: number;
  tagId?: string;
  from?: string;
  to?: string;
}): Promise<PageResponse<WorkLog>> {
  const { data } = await api.get<PageResponse<WorkLog>>("/api/v1/work-logs", { params });
  return data;
}

export async function getWorkLog(id: string): Promise<WorkLog> {
  const { data } = await api.get<WorkLog>(`/api/v1/work-logs/${id}`);
  return data;
}

export async function createWorkLog(body: CreateWorkLogRequest): Promise<WorkLog> {
  const { data } = await api.post<WorkLog>("/api/v1/work-logs", body);
  return data;
}

export async function updateWorkLog(
  id: string,
  body: Partial<CreateWorkLogRequest>,
): Promise<WorkLog> {
  const { data } = await api.put<WorkLog>(`/api/v1/work-logs/${id}`, body);
  return data;
}

export async function deleteWorkLog(id: string): Promise<void> {
  await api.delete(`/api/v1/work-logs/${id}`);
}

export async function getTags() {
  const { data } = await api.get<{ id: string; name: string }[]>("/api/v1/tags");
  return data;
}
