# Grovarc 🌱

> 개발자의 성장을 기록하는 공간

개발자가 매일 작업 로그를 기록하면, AI Agent가 패턴을 분석해서
회고 초안 생성, 성장 리포트, 학습 로드맵을 자동으로 제공하는 서비스입니다.

🌐 [grovarc.dev](https://grovarc.dev)

## 서비스 구조

```
apps/
├── web/    # Next.js 프론트엔드
├── api/    # Kotlin Spring Boot 백엔드
├── ai/     # Python FastAPI AI 서버
└── mcp/    # TypeScript MCP 서버

infra/
├── terraform/    # AWS 인프라 코드
└── k8s/          # Kubernetes 매니페스트

docs/
├── PRD.md
├── architecture.md
└── adr/          # 기술 결정 기록
```

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Next.js, TypeScript, TailwindCSS, Zustand |
| Backend | Kotlin, Spring Boot, Kafka, JUnit |
| AI | Python, FastAPI, LangGraph, LLaMA 3, RAG |
| MCP | TypeScript MCP SDK |
| Infra | Kubernetes, Terraform, Prometheus, Grafana |
| DB | PostgreSQL, Redis, MongoDB |

## 개발 방식
Cursor Agent + Claude를 활용한 AI-assisted 개발 (바이브코딩)
개발 과정 → [기술 블로그](https://projectmiluju.github.io)

## 개발 단계

- [ ] Phase 0 — 기획 & 설계
- [ ] Phase 1 — 인프라 & 환경 세팅
- [ ] Phase 2 — 백엔드 코어
- [ ] Phase 3 — AI 서버 코어
- [ ] Phase 4 — Fine-tuning
- [ ] Phase 5 — 프론트엔드
- [ ] Phase 6 — MCP 서버
- [ ] Phase 7 — PM 산출물 & 블로그
- [ ] Phase 8 — QA & 런칭
