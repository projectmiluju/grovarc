import { z } from "zod";
import { grovarc } from "./client.js";

/**
 * MCP Tool 정의 목록
 * 각 tool은 name, description, inputSchema, handler로 구성
 */

export const tools = [
  {
    name: "get_work_logs",
    description:
      "Grovarc에 저장된 작업 로그 목록을 조회합니다. 특정 유저의 최근 작업 내역, 날짜별 로그, 기술 스택 사용 패턴을 확인할 수 있습니다.",
    inputSchema: z.object({
      user_id: z.string().describe("조회할 유저 ID"),
      page: z.string().optional().default("0").describe("페이지 번호 (0부터 시작)"),
      size: z.string().optional().default("20").describe("페이지당 항목 수"),
    }),
    async handler(input: { user_id: string; page?: string; size?: string }) {
      const data = await grovarc.getWorkLogs(input.user_id, input.page ?? "0", input.size ?? "20");
      return {
        totalElements: data.totalElements,
        totalPages: data.totalPages,
        currentPage: data.number,
        logs: data.content.map((log) => ({
          id: log.id,
          title: log.title,
          content: log.content,
          logDate: log.logDate,
          mood: log.mood,
          tags: log.tags.map((t) => t.name),
          createdAt: log.createdAt,
        })),
      };
    },
  },

  {
    name: "get_work_log",
    description: "특정 작업 로그의 상세 내용을 조회합니다.",
    inputSchema: z.object({
      id: z.string().describe("작업 로그 ID"),
    }),
    async handler(input: { id: string }) {
      const log = await grovarc.getWorkLog(input.id);
      return {
        id: log.id,
        title: log.title,
        content: log.content,
        logDate: log.logDate,
        mood: log.mood,
        tags: log.tags.map((t) => t.name),
        createdAt: log.createdAt,
      };
    },
  },

  {
    name: "get_retrospectives",
    description:
      "회고 목록을 조회합니다. AI가 생성한 주간 회고 초안과 발행된 회고를 확인할 수 있습니다.",
    inputSchema: z.object({
      user_id: z.string().describe("조회할 유저 ID"),
      status: z
        .enum(["ALL", "DRAFT", "PUBLISHED"])
        .optional()
        .default("ALL")
        .describe("회고 상태 필터"),
    }),
    async handler(input: { user_id: string; status?: string }) {
      const status = input.status === "ALL" ? undefined : input.status;
      const data = await grovarc.getRetrospectives(input.user_id, status);
      return {
        totalElements: data.totalElements,
        retrospectives: data.content.map((r) => ({
          id: r.id,
          title: r.title,
          status: r.status,
          periodFrom: r.periodFrom,
          periodTo: r.periodTo,
          createdAt: r.createdAt,
        })),
      };
    },
  },

  {
    name: "get_retrospective",
    description: "특정 회고의 전체 내용을 조회합니다. 마크다운 형식의 회고 본문이 포함됩니다.",
    inputSchema: z.object({
      id: z.string().describe("회고 ID"),
    }),
    async handler(input: { id: string }) {
      return grovarc.getRetrospective(input.id);
    },
  },

  {
    name: "get_coaching_result",
    description:
      "성장 코칭 결과를 조회합니다. 최근 3개월 작업 로그 분석을 통해 생성된 부족 기술 스택과 8주 학습 로드맵을 포함합니다.",
    inputSchema: z.object({
      user_id: z.string().describe("조회할 유저 ID"),
    }),
    async handler(input: { user_id: string }) {
      const history = await grovarc.getCoachingHistory(input.user_id);
      if (history.length === 0) {
        return { message: "코칭 결과가 없습니다. 코칭 페이지에서 분석을 먼저 실행하세요." };
      }
      const latest = history[0];
      return {
        weakStacks: latest.weakStacks,
        roadmap: latest.roadmap,
        createdAt: latest.createdAt,
        historyCount: history.length,
      };
    },
  },

  {
    name: "get_dashboard_stats",
    description:
      "대시보드 통계를 조회합니다. 총 로그 수, 현재 스트릭, 최장 스트릭, 주간 작성 현황을 확인할 수 있습니다.",
    inputSchema: z.object({
      user_id: z.string().describe("조회할 유저 ID"),
    }),
    async handler(input: { user_id: string }) {
      return grovarc.getDashboardStats(input.user_id);
    },
  },
] as const;

export type ToolName = (typeof tools)[number]["name"];
