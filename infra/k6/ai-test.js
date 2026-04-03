/**
 * AI 서버 성능 테스트 (k6)
 * 코칭 Agent 응답 시간 측정 (LangGraph 실행 포함)
 *
 * 실행:
 *   k6 run --env AI_URL=http://localhost:8000 \
 *           --env USER_ID=test-user-id \
 *           infra/k6/ai-test.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

const AI_URL = __ENV.AI_URL || "http://localhost:8000";
const USER_ID = __ENV.USER_ID || "test-user-id";

const coachingDuration = new Trend("coaching_agent_duration");
const errorRate = new Rate("error_rate");

export const options = {
  // AI Agent는 무거우므로 낮은 VU로 테스트
  stages: [
    { duration: "30s", target: 3 },
    { duration: "2m", target: 5 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    // 코칭 Agent는 LLM 호출이 포함되므로 여유 있게 설정
    coaching_agent_duration: ["p(95)<120000"], // 95%ile 2분 이내
    error_rate: ["rate<0.10"],
  },
};

export default function () {
  // 코칭 Agent 실행 (LangGraph + RAG + 웹 검색 포함)
  const res = http.post(
    `${AI_URL}/api/v1/agents/coaching`,
    JSON.stringify({ user_id: USER_ID }),
    {
      headers: { "Content-Type": "application/json" },
      timeout: "180s",  // Agent 최대 3분 허용
    },
  );

  coachingDuration.add(res.timings.duration);

  const ok = check(res, {
    "coaching 200": (r) => r.status === 200,
    "has roadmap": (r) => {
      try {
        return r.json("roadmap")?.length > 0;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!ok);

  // Agent 실행 간격 (서버 부하 방지)
  sleep(5);
}
