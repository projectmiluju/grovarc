/**
 * Grovarc 부하 테스트 (k6)
 *
 * 실행:
 *   k6 run --env BASE_URL=http://localhost:8080 \
 *           --env EMAIL=test@grovarc.dev \
 *           --env PASSWORD=Test1234! \
 *           infra/k6/load-test.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const EMAIL = __ENV.EMAIL || "test@grovarc.dev";
const PASSWORD = __ENV.PASSWORD || "Test1234!";

// 커스텀 메트릭
const loginDuration = new Trend("login_duration");
const logListDuration = new Trend("log_list_duration");
const logCreateDuration = new Trend("log_create_duration");
const coachingDuration = new Trend("coaching_duration");
const errorRate = new Rate("error_rate");

export const options = {
  stages: [
    { duration: "30s", target: 10 },   // 워밍업: 10명까지 증가
    { duration: "1m", target: 50 },    // 부하: 50명 유지
    { duration: "30s", target: 100 },  // 스파이크: 100명
    { duration: "1m", target: 50 },    // 안정화: 50명
    { duration: "30s", target: 0 },    // 쿨다운
  ],
  thresholds: {
    http_req_duration: ["p(95)<2000"],  // 95%ile 2초 이내
    http_req_failed: ["rate<0.05"],     // 실패율 5% 미만
    login_duration: ["p(95)<1000"],     // 로그인 1초 이내
    log_list_duration: ["p(95)<500"],   // 목록 조회 500ms 이내
    log_create_duration: ["p(95)<1000"], // 로그 작성 1초 이내
    error_rate: ["rate<0.05"],
  },
};

// 로그인 후 토큰 반환
function login() {
  const res = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({ email: EMAIL, password: PASSWORD }),
    { headers: { "Content-Type": "application/json" } },
  );

  loginDuration.add(res.timings.duration);
  const ok = check(res, { "login 200": (r) => r.status === 200 });
  errorRate.add(!ok);

  if (!ok) return null;
  return res.json("accessToken");
}

export default function () {
  // 1. 로그인
  const token = login();
  if (!token) return;

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  sleep(0.5);

  // 2. 작업 로그 목록 조회
  const listRes = http.get(`${BASE_URL}/api/v1/work-logs`, { headers });
  logListDuration.add(listRes.timings.duration);
  check(listRes, { "log list 200": (r) => r.status === 200 });
  errorRate.add(listRes.status !== 200);

  sleep(0.5);

  // 3. 작업 로그 작성
  const createRes = http.post(
    `${BASE_URL}/api/v1/work-logs`,
    JSON.stringify({
      title: `k6 부하 테스트 로그 ${Date.now()}`,
      content: "k6로 자동 생성된 테스트 로그입니다.",
      logDate: new Date().toISOString().split("T")[0],
      mood: "GOOD",
    }),
    { headers },
  );
  logCreateDuration.add(createRes.timings.duration);
  check(createRes, { "log create 201": (r) => r.status === 201 });
  errorRate.add(createRes.status !== 201);

  sleep(0.5);

  // 4. 회고 목록 조회
  const retroRes = http.get(`${BASE_URL}/api/v1/retrospectives`, { headers });
  check(retroRes, { "retro list 200": (r) => r.status === 200 });
  errorRate.add(retroRes.status !== 200);

  sleep(1);
}
