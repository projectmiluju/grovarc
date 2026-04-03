import { describe, it, expect, vi, beforeEach } from "vitest";
import { tools } from "../tools.js";

// grovarc API 클라이언트 모킹
vi.mock("../client.js", () => ({
  grovarc: {
    getWorkLogs: vi.fn(),
    getWorkLog: vi.fn(),
    getRetrospectives: vi.fn(),
    getRetrospective: vi.fn(),
    getCoachingHistory: vi.fn(),
    getDashboardStats: vi.fn(),
  },
}));

import { grovarc } from "../client.js";

const findTool = (name: string) => tools.find((t) => t.name === name)!;

describe("MCP Tools", () => {
  beforeEach(() => vi.clearAllMocks());

  describe("get_work_logs", () => {
    it("작업 로그 목록을 반환한다", async () => {
      vi.mocked(grovarc.getWorkLogs).mockResolvedValue({
        content: [
          { id: "1", title: "테스트", content: "내용", logDate: "2026-04-01", tags: [], createdAt: "2026-04-01T00:00:00Z" },
        ],
        totalElements: 1,
        totalPages: 1,
        number: 0,
      });

      const tool = findTool("get_work_logs");
      const result = await tool.handler({ user_id: "u1" });

      expect(result).toMatchObject({ totalElements: 1, currentPage: 0 });
      expect((result as any).logs).toHaveLength(1);
      expect(grovarc.getWorkLogs).toHaveBeenCalledWith("u1", "0", "20");
    });
  });

  describe("get_work_log", () => {
    it("단일 작업 로그를 반환한다", async () => {
      vi.mocked(grovarc.getWorkLog).mockResolvedValue({
        id: "1", title: "제목", content: "내용", logDate: "2026-04-01",
        mood: "GOOD", tags: [{ id: "t1", name: "React" }], createdAt: "2026-04-01T00:00:00Z",
      });

      const tool = findTool("get_work_log");
      const result = await tool.handler({ id: "1" });

      expect((result as any).title).toBe("제목");
      expect((result as any).tags).toEqual(["React"]);
    });
  });

  describe("get_retrospectives", () => {
    it("회고 목록을 반환한다", async () => {
      vi.mocked(grovarc.getRetrospectives).mockResolvedValue({
        content: [
          { id: "r1", title: "4월 1주차 회고", content: "...", status: "PUBLISHED",
            periodFrom: "2026-03-25", periodTo: "2026-03-31", createdAt: "2026-04-01T00:00:00Z" },
        ],
        totalElements: 1, totalPages: 1, number: 0,
      });

      const tool = findTool("get_retrospectives");
      const result = await tool.handler({ user_id: "u1", status: "PUBLISHED" });

      expect((result as any).totalElements).toBe(1);
      expect(grovarc.getRetrospectives).toHaveBeenCalledWith("u1", "PUBLISHED");
    });

    it("status=ALL이면 필터 없이 조회한다", async () => {
      vi.mocked(grovarc.getRetrospectives).mockResolvedValue({
        content: [], totalElements: 0, totalPages: 0, number: 0,
      });

      const tool = findTool("get_retrospectives");
      await tool.handler({ user_id: "u1", status: "ALL" });

      expect(grovarc.getRetrospectives).toHaveBeenCalledWith("u1", undefined);
    });
  });

  describe("get_coaching_result", () => {
    it("최신 코칭 결과를 반환한다", async () => {
      vi.mocked(grovarc.getCoachingHistory).mockResolvedValue([
        { weakStacks: ["Docker", "K8s"], roadmap: "## 1주차\n...", mongoDocId: "abc", createdAt: "2026-04-01T00:00:00Z" },
        { weakStacks: ["Redis"], roadmap: "...", mongoDocId: "def", createdAt: "2026-03-01T00:00:00Z" },
      ]);

      const tool = findTool("get_coaching_result");
      const result = await tool.handler({ user_id: "u1" });

      expect((result as any).weakStacks).toEqual(["Docker", "K8s"]);
      expect((result as any).historyCount).toBe(2);
    });

    it("코칭 기록이 없으면 안내 메시지를 반환한다", async () => {
      vi.mocked(grovarc.getCoachingHistory).mockResolvedValue([]);

      const tool = findTool("get_coaching_result");
      const result = await tool.handler({ user_id: "u1" });

      expect((result as any).message).toContain("코칭 결과가 없습니다");
    });
  });

  describe("get_dashboard_stats", () => {
    it("대시보드 통계를 반환한다", async () => {
      const mockStats = {
        totalLogs: 42, currentStreak: 7, longestStreak: 14,
        weeklyData: [], recentRetrospectives: [],
      };
      vi.mocked(grovarc.getDashboardStats).mockResolvedValue(mockStats);

      const tool = findTool("get_dashboard_stats");
      const result = await tool.handler({ user_id: "u1" });

      expect(result).toEqual(mockStats);
    });
  });

  describe("tool 목록", () => {
    it("6개 tool이 등록되어 있다", () => {
      expect(tools).toHaveLength(6);
    });

    it("모든 tool이 name, description, inputSchema, handler를 가진다", () => {
      for (const tool of tools) {
        expect(tool.name).toBeTruthy();
        expect(tool.description).toBeTruthy();
        expect(tool.inputSchema).toBeTruthy();
        expect(typeof tool.handler).toBe("function");
      }
    });
  });
});
