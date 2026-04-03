# Grovarc

> **Grow + Arc** — 개발자의 성장 곡선을 기록하는 공간

매일 작업 로그를 기록하면, AI Agent가 패턴을 분석해 **회고 초안 생성 · 성장 리포트 · 학습 로드맵**을 자동으로 제공하는 개발자 특화 생산성 서비스

[![CI](https://github.com/projectmiluju/grovarc/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/projectmiluju/grovarc/actions/workflows/ci.yml)
🌐 [grovarc.dev](https://grovarc.dev)

---

## 핵심 기능

| 기능 | 설명 |
|------|------|
| 📝 **작업 로그** | 날짜·기분·태그와 함께 하루 작업을 기록 |
| 🤖 **AI 주간 회고** | Celery Beat가 매주 자동으로 LangGraph Agent 실행, 회고 초안 생성 |
| 📈 **성장 코칭** | 최근 3개월 로그 분석 → 부족 기술 스택 → 8주 학습 로드맵 |
| 🔌 **MCP 서버** | Cursor / Claude Code / Codex CLI / Gemini CLI에서 데이터 직접 조회 |
| 📊 **대시보드** | 스트릭 캘린더, 주간 작성 차트, 성장 통계 |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Frontend** | Next.js 16, React 19, TypeScript, TailwindCSS, Zustand, Playwright |
| **Backend** | Kotlin, Spring Boot, JPA, Spring Security + JWT, Kafka, JUnit |
| **AI** | Python, FastAPI, LangGraph, Celery + Beat, LLaMA 3 + LoRA, pgvector + RAG |
| **MCP** | TypeScript, @modelcontextprotocol/sdk, stdio transport |
| **DB** | PostgreSQL + pgvector, Redis, MongoDB |
| **Infra** | Kubernetes (EKS), Terraform, Docker, Prometheus + Grafana, GitHub Actions |

---

## 아키텍처

```
[Next.js 16]  ──REST──►  [Kotlin Spring Boot]  ──►  [PostgreSQL + pgvector]
                                  │                   [Redis]
                          Kafka 이벤트
                                  ▼
                    [Python FastAPI AI 서버]
                     LangGraph Agent (주간 회고 / 성장 코칭)
                     Celery Beat (매주 자동 스케줄)
                     Fine-tuned LLaMA 3 / Claude API (A/B 전환)
                     RAG (pgvector 유사도 검색)
                                  ▼
                    [pgvector + MongoDB]

[TypeScript MCP 서버]  ◄──  Cursor / Claude Code / Codex CLI / Gemini CLI
                              (stdio transport, MCP 표준 프로토콜)

[Prometheus + Grafana]  /  [Kubernetes EKS]  /  [Terraform]  /  [GitHub Actions]
```

---

## 레포 구조

```
/
├── apps/
│   ├── web/        # Next.js 16 프론트엔드
│   ├── api/        # Kotlin Spring Boot 백엔드
│   ├── ai/         # Python FastAPI AI 서버
│   └── mcp/        # TypeScript MCP 서버
├── infra/
│   ├── terraform/  # AWS 인프라 코드 (IaC)
│   └── k8s/        # Kubernetes 매니페스트
└── docs/
    ├── PRD.md
    ├── architecture.md
    └── adr/        # 기술 결정 기록 (ADR-001 ~ ADR-007)
```

---

## 로컬 실행

### 프론트엔드 (Next.js)
```bash
cd apps/web
bun install
bun dev         # http://localhost:3000
```

### AI 서버 (FastAPI)
```bash
cd apps/ai
pip install uv && uv pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

### MCP 서버
```bash
cd apps/mcp
bun install && bun run build

# Claude Code 연동 예시
claude mcp add grovarc \
  --command "node" \
  --args "$(pwd)/dist/index.js" \
  --env GROVARC_API_URL=http://localhost:8080
```

→ Cursor / Codex CLI / Gemini CLI 설정: [apps/mcp/README.md](apps/mcp/README.md)

---

## 개발 현황

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 0 | 기획 & 설계 | 🔲 |
| Phase 1 | 인프라 & 환경 세팅 | 🔲 |
| Phase 2 | 백엔드 코어 (Kotlin Spring Boot) | ✅ |
| Phase 3 | AI 서버 코어 (FastAPI, LangGraph, RAG) | ✅ |
| Phase 4 | Fine-tuning (LLaMA 3 + LoRA) | ✅ |
| Phase 5 | 프론트엔드 (Next.js 16, Playwright) | ✅ |
| Phase 6 | MCP 서버 (4개 AI CLI 연동) | ✅ |
| Phase 7 | PM 산출물 & 블로그 | 🔄 |
| Phase 8 | QA & 런칭 | 🔲 |

---

## 개발 방식

Cursor Agent + Claude Code를 활용한 AI-assisted 개발 (바이브코딩)  
개발 과정 → [기술 블로그](https://projectmiluju.github.io)

## 개발자

**정원용** · 1인 풀스택  
[GitHub](https://github.com/projectmiluju) · [블로그](https://projectmiluju.github.io)
