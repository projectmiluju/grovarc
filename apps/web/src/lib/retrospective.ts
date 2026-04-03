import api from "./api";
import type { Retrospective, PageResponse } from "@/types";

export async function getRetrospectives(params?: {
  page?: number;
  size?: number;
  status?: "DRAFT" | "PUBLISHED";
}): Promise<PageResponse<Retrospective>> {
  const { data } = await api.get<PageResponse<Retrospective>>("/api/v1/retrospectives", {
    params,
  });
  return data;
}

export async function getRetrospective(id: string): Promise<Retrospective> {
  const { data } = await api.get<Retrospective>(`/api/v1/retrospectives/${id}`);
  return data;
}

export async function updateRetrospective(
  id: string,
  body: { title?: string; content?: string },
): Promise<Retrospective> {
  const { data } = await api.put<Retrospective>(`/api/v1/retrospectives/${id}`, body);
  return data;
}

export async function publishRetrospective(id: string): Promise<Retrospective> {
  const { data } = await api.post<Retrospective>(`/api/v1/retrospectives/${id}/publish`);
  return data;
}

export async function triggerAiDraft(params: {
  userId: string;
  periodFrom: string;
  periodTo: string;
}): Promise<{ draftTitle: string; draftContent: string; goals: string[] }> {
  const { data } = await api.post("/api/v1/agents/retrospective", {
    user_id: params.userId,
    period_from: params.periodFrom,
    period_to: params.periodTo,
  });
  return data;
}
