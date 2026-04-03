/**
 * Grovarc REST API HTTP 클라이언트
 * GROVARC_API_URL 환경변수로 베이스 URL 설정 (기본: http://localhost:8080)
 * GROVARC_API_TOKEN 환경변수로 인증 토큰 설정
 */

const BASE_URL = process.env.GROVARC_API_URL ?? "http://localhost:8080";
const TOKEN = process.env.GROVARC_API_TOKEN ?? "";

async function request<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE_URL}/api/v1${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }

  const res = await fetch(url.toString(), {
    headers: {
      "Content-Type": "application/json",
      ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
    },
  });

  if (!res.ok) {
    throw new Error(`API 오류 ${res.status}: ${await res.text()}`);
  }

  return res.json() as Promise<T>;
}

export interface WorkLog {
  id: string;
  title: string;
  content: string;
  logDate: string;
  mood?: string;
  tags: { id: string; name: string }[];
  createdAt: string;
}

export interface Retrospective {
  id: string;
  title: string;
  content: string;
  status: "DRAFT" | "PUBLISHED";
  periodFrom: string;
  periodTo: string;
  createdAt: string;
}

export interface CoachingResult {
  weakStacks: string[];
  roadmap: string;
  mongoDocId: string | null;
  createdAt: string;
}

export interface DashboardStats {
  totalLogs: number;
  currentStreak: number;
  longestStreak: number;
  weeklyData: { date: string; count: number }[];
  recentRetrospectives: Retrospective[];
}

export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number;
}

export const grovarc = {
  getWorkLogs(userId: string, page = "0", size = "20") {
    return request<PageResponse<WorkLog>>("/work-logs", { userId, page, size });
  },

  getWorkLog(id: string) {
    return request<WorkLog>(`/work-logs/${id}`);
  },

  getRetrospectives(userId: string, status?: string) {
    return request<PageResponse<Retrospective>>("/retrospectives", {
      userId,
      ...(status ? { status } : {}),
    });
  },

  getRetrospective(id: string) {
    return request<Retrospective>(`/retrospectives/${id}`);
  },

  getCoachingHistory(userId: string) {
    return request<CoachingResult[]>("/coaching/history", { userId });
  },

  getDashboardStats(userId: string) {
    return request<DashboardStats>("/dashboard/stats", { userId });
  },
};
