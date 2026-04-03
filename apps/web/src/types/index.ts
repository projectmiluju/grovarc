// ── Auth ──────────────────────────────────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  nickname: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
}

export interface User {
  id: string;
  email: string;
  nickname: string;
  createdAt: string;
}

// ── WorkLog ───────────────────────────────────────────────────────────────────

export type Mood = "GREAT" | "GOOD" | "NEUTRAL" | "BAD" | "TERRIBLE";

export interface WorkLog {
  id: string;
  title: string;
  content: string;
  logDate: string;    // "YYYY-MM-DD"
  mood: Mood | null;
  tags: Tag[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateWorkLogRequest {
  title: string;
  content: string;
  logDate: string;
  mood?: Mood;
  tagIds?: string[];
}

// ── Tag ───────────────────────────────────────────────────────────────────────

export interface Tag {
  id: string;
  name: string;
}

// ── Retrospective ─────────────────────────────────────────────────────────────

export type RetroStatus = "DRAFT" | "PUBLISHED";

export interface Retrospective {
  id: string;
  title: string;
  content: string;
  periodFrom: string;
  periodTo: string;
  status: RetroStatus;
  createdAt: string;
  updatedAt: string;
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export interface DashboardStats {
  totalLogs: number;
  totalRetrospectives: number;
  currentStreak: number;
  longestStreak: number;
  weeklyLogCounts: { date: string; count: number }[];
}

// ── Coaching ──────────────────────────────────────────────────────────────────

export interface CoachingResult {
  weakStacks: string[];
  roadmap: string;
  mongoDocId: string | null;
  createdAt: string;
}

// ── Pagination ────────────────────────────────────────────────────────────────

export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
}
