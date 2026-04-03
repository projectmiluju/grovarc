# Grovarc 아키텍처

> 최종 업데이트: 2026-04-03 (Phase 6 완료 기준)

---

## 전체 구성도

```
[Next.js 16 + TypeScript]  ← 웹 클라이언트
        ↓ REST API (/api/v1/* rewrite)
[Kotlin + Spring Boot]  ───→ [PostgreSQL + pgvector]
        │                  → [Redis]
        ↓ Kafka (work-log.saved 이벤트)
[Python FastAPI AI 서버]
        │ LangGraph Agent (주간 회고 / 성장 코칭)
        │ Celery + Beat (주간 자동 스케줄링)
        │ Fine-tuned LLaMA 3 (INFERENCE_BACKEND=finetuned)
        │ Claude API (INFERENCE_BACKEND=claude, 기본값)
        ↓ RAG (pgvector 유사도 검색)
   [pgvector + MongoDB]  ← 벡터 + AI 분석 결과 저장

[TypeScript MCP 서버]  ← Cursor / Claude Code / Codex CLI / Gemini CLI에서 직접 조회
        ↓ HTTP (Grovarc REST API 호출)
[Kotlin + Spring Boot]

[Prometheus + Grafana]  ← 전체 모니터링
[Kubernetes (EKS)]      ← 전체 오케스트레이션
[Terraform]             ← AWS 인프라 코드화
[GitHub Actions]        ← CI/CD
```

---

## 서비스별 역할

| 서비스 | 기술 | 역할 |
|--------|------|------|
| `apps/web` | Next.js 16, React 19, TypeScript | 웹 클라이언트 — 로그 작성, 회고, 코칭, 대시보드 |
| `apps/api` | Kotlin, Spring Boot, JPA, Kafka | REST API 서버 — 인증, CRUD, 이벤트 발행 |
| `apps/ai` | Python, FastAPI, LangGraph, Celery | AI 마이크로서비스 — 회고 생성, 코칭, RAG |
| `apps/mcp` | TypeScript, MCP SDK | MCP 서버 — AI CLI에서 회고 데이터 직접 조회 |

---

## AI 서버 내부 흐름

### 주간 회고 Agent (Celery Beat — 매주 월요일 자동)
```
Celery Beat 트리거
  → collect_logs (지난주 로그 DB 조회)
  → analyze_patterns (LangGraph — 패턴 분석)
  → generate_draft (Fine-tuned LLaMA 3 or Claude API)
  → save_retrospective (MongoDB + PostgreSQL)
  → notify_user (알림 발송)
```

### 성장 코칭 Agent (유저 요청 시 — POST /api/v1/agents/coaching)
```
fetch_logs (최근 3개월 로그)
  → analyze_weaknesses (RAG — pgvector 유사도 검색)
  → search_resources (DuckDuckGoSearchRun — API 키 불필요)
  → generate_roadmap (8주 학습 로드맵 생성)
  → save_result (MongoDB)
```

### 모델 A/B 전환
```
INFERENCE_BACKEND=claude    → Anthropic Claude API (기본값)
INFERENCE_BACKEND=finetuned → HuggingFace 로컬 파이프라인 (LLaMA 3 + LoRA)
```

---

## 인증 흐름

```
클라이언트 → POST /api/v1/auth/login
  ← { accessToken, refreshToken }

accessToken: 메모리(Zustand)에만 저장 (보안)
refreshToken: HttpOnly 쿠키

요청마다: Authorization: Bearer {accessToken}
401 응답: refreshToken으로 자동 갱신 (axios interceptor + queue)

proxy.ts: 쿠키 없으면 /login으로 리다이렉트 (서버 사이드 가드)
```

---

## MCP 서버

```
AI CLI (Cursor / Claude Code / Codex CLI / Gemini CLI)
  ↕ stdio transport (JSON-RPC, MCP 표준 프로토콜)
apps/mcp (TypeScript MCP SDK)
  ↕ HTTP REST API
apps/api (Kotlin REST API, :8080)
  ↕
PostgreSQL + MongoDB
```

**제공 도구 (구현 완료):**
- `get_work_logs` — 작업 로그 목록 조회 (페이지네이션)
- `get_work_log` — 특정 작업 로그 상세 조회
- `get_retrospectives` — 회고 목록 조회 (ALL/DRAFT/PUBLISHED 필터)
- `get_retrospective` — 특정 회고 전체 내용 조회
- `get_coaching_result` — 최신 성장 코칭 결과 + 8주 로드맵
- `get_dashboard_stats` — 스트릭·주간 통계

**환경변수:**
- `GROVARC_API_URL` — API 서버 주소 (기본: `http://localhost:8080`)
- `GROVARC_API_TOKEN` — JWT 액세스 토큰
