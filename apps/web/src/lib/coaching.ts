import api from "./api";
import type { CoachingResult } from "@/types";

export async function requestCoaching(userId: string): Promise<CoachingResult> {
  const { data } = await api.post<{
    weak_stacks: string[];
    roadmap: string;
    mongo_doc_id: string | null;
  }>("/api/v1/agents/coaching", { user_id: userId });

  return {
    weakStacks: data.weak_stacks,
    roadmap: data.roadmap,
    mongoDocId: data.mongo_doc_id,
    createdAt: new Date().toISOString(),
  };
}

export async function getCoachingHistory(userId: string): Promise<CoachingResult[]> {
  const { data } = await api.get<CoachingResult[]>("/api/v1/coaching/history", {
    params: { userId },
  });
  return data;
}
