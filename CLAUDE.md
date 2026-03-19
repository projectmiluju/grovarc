# CLAUDE.md — AI 기반 개발자 회고 & 성장 트래커

> 이 파일은 Cursor / Claude Code에서 프로젝트 컨텍스트를 즉시 복원하기 위한 문서입니다.
> 어느 환경에서 열어도 이 파일 하나로 지금까지의 결정과 진행 상황을 파악할 수 있어야 합니다.

---

## 프로젝트 개요

**서비스명**: Grovarc
**도메인**: grovarc.dev (또는 grovarc.io / grovarc.app)
**한 줄 설명**: 개발자가 매일 작업 로그를 기록하면, AI Agent가 패턴을 분석해서 회고 초안 생성, 성장 리포트, 학습 로드맵을 자동으로 제공하는 개발자 특화 생산성 서비스
**네이밍 의미**: Grow(성장) + Arc(성장 곡선) — 개발자의 성장을 기록하는 공간
**목표**: 포트폴리오 + 실제 런칭
**타겟 유저**: 성장을 기록하고 싶은 개발자
**개발자**: 정원용 (1인 풀스택)
**개발 방식**: Cursor Agent + Claude를 활용한 AI-assisted 개발 (바이브코딩)

---

## 기술 스택

### 프론트엔드
| 기술 | 용도 |
|------|------|
| Next.js + TypeScript | 메인 웹 클라이언트 |
| TailwindCSS | 스타일링 |
| Zustand | 클라이언트 상태관리 |
| Playwright | E2E 테스트 |

### 백엔드 메인
| 기술 | 용도 |
|------|------|
| Kotlin + Spring Boot | REST API 서버 |
| Spring Data JPA | ORM |
| Spring Security + JWT | 인증/인가 |
| JUnit | 단위/통합 테스트 |
| Kafka | 로그 저장 이벤트 → AI 서버 비동기 전달 |

### 백엔드 AI 마이크로서비스
| 기술 | 용도 |
|------|------|
| Python + FastAPI | AI 전담 서버 |
| LangGraph + LangChain | AI Agent 구현 |
| Celery + Beat | 주간 회고 Agent 자동 스케줄링 |
| OpenAI / Anthropic API | 회고 초안 생성, 패턴 분석 |
| Hugging Face + PyTorch + LoRA | LLaMA 3 Fine-tuning |
| pgvector + RAG | 과거 로그 벡터화 → 유사 패턴 검색 |

### MCP 서버
| 기술 | 용도 |
|------|------|
| TypeScript MCP SDK | Cursor/Claude에서 회고 데이터 직접 조회 가능한 MCP 서버 |

### 데이터베이스
| 기술 | 용도 |
|------|------|
| PostgreSQL + pgvector | 메인 DB + 벡터 저장 |
| Redis | 캐싱 |
| MongoDB | 비정형 AI 분석 결과 저장 |

### 인프라
| 기술 | 용도 |
|------|------|
| Kubernetes (EKS) | 전체 서비스 오케스트레이션 |
| Terraform | AWS 인프라 코드화 (IaC) |
| Prometheus + Grafana | 모니터링 |
| GitHub Actions | CI/CD |
| Docker | 컨테이너화 |
| AWS (EKS, S3, RDS, CloudFront, Route53) | 클라우드 인프라 |

---

## 아키텍처

```
[Next.js + TypeScript]
        ↓ REST API
[Kotlin + Spring Boot] ──→ [PostgreSQL + pgvector]
        │                → [Redis]
        ↓ Kafka 이벤트
[Python FastAPI AI 서버]
        │ LangGraph Agent
        │ Celery + Beat (스케줄링)
        │ Fine-tuned LLaMA 3
        ↓ RAG
   [pgvector + MongoDB]
        ↓
   [OpenAI / Anthropic API]

[TypeScript MCP 서버] ← Cursor/Claude에서 직접 조회

[Prometheus + Grafana] ← 전체 모니터링
[Kubernetes (EKS)]    ← 전체 오케스트레이션
[Terraform]           ← 인프라 프로비저닝
[GitHub Actions]      ← CI/CD
```

---

## AI Agent 설계

### 주간 회고 Agent (자동 실행 — Celery Beat)
```
1. 지난주 로그 수집
2. 패턴 분석 (LangGraph)
3. 회고 초안 생성 (Fine-tuned LLaMA 3)
4. 다음 주 목표 제안
5. 유저에게 알림 발송
6. 피드백 반영 → 다음 회고에 학습
```

### 성장 코칭 Agent (유저 요청 시)
```
1. 최근 3개월 로그 분석
2. 부족한 기술 스택 파악 (RAG)
3. 학습 리소스 검색 (web search tool)
4. 개인화된 학습 로드맵 생성
```

---

## 개발 단계 (Phase)

- [ ] **Phase 0** — 기획 & 설계 (PRD, 유저 스토리, 아키텍처 설계, GitHub 세팅, Kotlin 문법)
- [ ] **Phase 1** — 인프라 & 환경 세팅 (Terraform, k8s, Docker, CI/CD, 모니터링)
- [ ] **Phase 2** — 백엔드 코어 (Kotlin Spring Boot, CRUD API, JUnit, Kafka)
- [ ] **Phase 3** — AI 서버 코어 (FastAPI, LangGraph Agent, RAG, MongoDB, Celery)
- [ ] **Phase 4** — Fine-tuning (학습 데이터 준비, LLaMA 3 + LoRA, Hugging Face Hub)
- [ ] **Phase 5** — 프론트엔드 (Next.js UI, 대시보드, 시각화, Playwright)
- [ ] **Phase 6** — MCP 서버 (TypeScript MCP SDK, Cursor 연동)
- [ ] **Phase 7** — PM 산출물 & 블로그 (PRD 공개, README, 블로그 시리즈)
- [ ] **Phase 8** — QA & 런칭 (성능 테스트, 배포, 커뮤니티 공유)

---

## 현재 진행 상황

```
현재 Phase: 1 (완료) → Phase 2 시작
마지막 작업: Phase 1 인프라 & 환경 세팅 전체 완료
  - #8  apps/{web,api,ai,mcp}/Dockerfile — 멀티 스테이지 빌드
  - #9  docker-compose.yml — 로컬 개발 환경 (PostgreSQL, Redis, MongoDB, Kafka)
  - #10 .github/workflows/ci.yml — GitHub Actions CI
  - #11 infra/terraform/ — AWS 인프라 코드 (VPC, EKS, RDS, Redis, Kafka, MongoDB, S3)
  - #12 infra/k8s/ — Kubernetes 매니페스트 (Deployment, Service, Ingress, HPA)
  - #13 infra/monitoring/ — Prometheus + Grafana 모니터링
다음 할 일: Phase 2 — 백엔드 코어 (Kotlin Spring Boot, CRUD API, JUnit, Kafka)
블로커: -
```

> ✅ 이 섹션을 작업할 때마다 업데이트하세요.

---

## 기술 결정 기록 (ADR)

### ADR-001 | Java → Kotlin
- **결정**: Spring Boot 메인 서버를 Kotlin으로 작성
- **이유**: Java 경험 기반으로 진입 장벽 낮음, 한국 스타트업에서 빠르게 늘어나는 스택, coroutine 비동기 처리 강점
- **트레이드오프**: 초기 문법 적응 비용 1~2주

### ADR-002 | LangChain → LangGraph
- **결정**: 단순 체이닝 대신 LangGraph로 Agent 구현
- **이유**: 단순 프롬프트 체이닝이 아니라 상태 기반 Agent 흐름이 필요, 주간 회고/성장 코칭 Agent가 판단-행동 루프를 가져야 함
- **트레이드오프**: 학습 곡선이 LangChain보다 높음

### ADR-003 | Fine-tuning 방식
- **결정**: OpenAI Fine-tuning API가 아닌 LLaMA 3 + LoRA
- **이유**: 오픈소스라 비용 없음, Hugging Face 생태계 경험 추가, Google Colab으로 GPU 없이 가능
- **트레이드오프**: OpenAI API보다 초기 셋업 복잡

### ADR-004 | MCP 서버 직접 구현
- **결정**: 이 서비스의 MCP 서버를 TypeScript로 직접 구현
- **이유**: MCP를 쓰는 것이 아니라 MCP 서버 제공자가 되는 것이 포트폴리오 차별점
- **트레이드오프**: 추가 개발 공수

### ADR-006 | develop 브랜치를 default로 설정
- **결정**: GitHub default 브랜치를 `main` → `develop`으로 변경
- **이유**: `feature → develop` PR 머지 시 `Closes #이슈` 자동 닫기가 동작하려면 default 브랜치에 머지되어야 함. 1인 프로젝트에서 실질적 작업 종착점이 `develop`이므로 자연스러운 선택
- **트레이드오프**: 레포 기본 화면에 `develop` 코드 노출, 배포 PR 시 base를 `main`으로 명시 필요

### ADR-005 | 패키지 매니저 → bun
- **결정**: 루트 패키지 매니저를 bun으로 채택
- **이유**: npm/pnpm 대비 설치 속도 빠름, 런타임 내장, 모노레포 워크스페이스 지원
- **트레이드오프**: 생태계가 npm/pnpm보다 덜 성숙, 일부 패키지 호환 이슈 가능성

> ✅ 새로운 기술 결정이 생길 때마다 여기에 추가하세요.

---

## GitHub 이슈 & 프로젝트 관리

### 이슈 구조
- **에픽**: Phase 단위 묶음 이슈 (`[Epic] Phase N — 설명`), 레이블: `epic`, `phase-N`, 영역
- **태스크**: 실제 작업 단위 이슈 (`[Task] 작업명`), 레이블: `task`, `phase-N`, 영역
- 에픽은 이미 Phase 0~6 생성 완료. 새 에픽은 원칙적으로 추가 없음
- 태스크는 해당 Phase 시작 시 에픽 하위에 추가

### 태스크 이슈 생성 절차 (신규 태스크 추가 시)

1. **이슈 생성**
```bash
gh issue create \
  --title "[Task] 작업명" \
  --body "## 상위 에픽\n#에픽번호\n\n## 작업 내용\n- [ ] 항목\n\n## 브랜치\n\`feature/이슈번호-설명\`" \
  --label "task,phase-N,영역" \
  --repo projectmiluju/grovarc
```

2. **Sub-issue 연결** (이슈 ID 필요 — 번호 아님)
```bash
# 이슈 ID 조회
gh api /repos/projectmiluju/grovarc/issues/이슈번호 --jq '.id'

# 에픽에 sub-issue 연결
gh api --method POST \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/projectmiluju/grovarc/issues/에픽번호/sub_issues \
  --input - <<< '{"sub_issue_id": 이슈ID}'
```

3. **GitHub Project 추가 & 날짜 설정**
```bash
# Project에 추가
gh project item-add 14 --owner projectmiluju --url https://github.com/projectmiluju/grovarc/issues/이슈번호

# Start/Target Date 설정 (field ID는 고정)
# Start Date field: PVTF_lAHOBni4vc4BSOUbzg_0mcU
# Target Date field: PVTF_lAHOBni4vc4BSOUbzg_0mcY
gh project item-edit --project-id PVT_kwHOBni4vc4BSOUb --id ITEM_ID \
  --field-id PVTF_lAHOBni4vc4BSOUbzg_0mcU --date YYYY-MM-DD
```

4. **브랜치 생성**
```bash
git checkout develop
git checkout -b feature/이슈번호-설명
```

### 레이블 목록
| 레이블 | 용도 |
|--------|------|
| `epic` | 에픽 이슈 |
| `task` | 태스크 이슈 |
| `phase-0` ~ `phase-6` | 페이즈 구분 |
| `infra` | 인프라 |
| `backend` | 백엔드 (Kotlin) |
| `frontend` | 프론트엔드 (Next.js) |
| `ai` | AI 서버 (Python) |
| `mcp` | MCP 서버 |

### GitHub Project
- **프로젝트**: Grovarc 개발 로드맵 (Project #14)
- **URL**: https://github.com/users/projectmiluju/projects/14
- **Project ID**: PVT_kwHOBni4vc4BSOUb

---

## 코드 컨벤션

### 공통
- 브랜치 전략: `main` / `develop` / `feature/이슈번호-설명`
- 커밋 컨벤션: Conventional Commits (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`, `perf:`, `ci:`, `revert:`)
- 커밋 메시지 검사: commitlint + husky (`commit-msg` 훅) — 형식 불일치 시 커밋 차단
- PR: 이슈 연결 필수, 셀프 리뷰 후 머지

### Kotlin
- (세팅 후 작성)

### Python
- (세팅 후 작성)

### TypeScript
- (세팅 후 작성)

---

## 레포 구조 (예정)

```
/
├── apps/
│   ├── web/          # Next.js 프론트엔드
│   ├── api/          # Kotlin Spring Boot 백엔드
│   ├── ai/           # Python FastAPI AI 서버
│   └── mcp/          # TypeScript MCP 서버
├── infra/
│   ├── terraform/    # AWS 인프라 코드
│   └── k8s/          # Kubernetes 매니페스트
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   └── adr/          # 기술 결정 기록
└── CLAUDE.md         # 이 파일
```

---

## 환경변수 목록

```env
# API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Database
DATABASE_URL=
REDIS_URL=
MONGODB_URL=

# Kafka
KAFKA_BOOTSTRAP_SERVERS=

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=

# Auth
JWT_SECRET=
```

> ✅ 실제 값은 절대 이 파일에 넣지 마세요. `.env.local`에 별도 관리.

---

## 블로그 포스팅 계획

- [ ] "Claude와 함께 PRD 작성한 과정"
- [ ] "Cursor Agent로 Kafka 처음 구현한 과정"
- [ ] "LangGraph Agent 설계기"
- [ ] "LLaMA 3 Fine-tuning 처음 해본 후기"
- [ ] "MCP 서버 직접 만들어보기"
- [ ] "이 프로젝트의 프롬프트 엔지니어링 전략"

---

## 참고 링크

- GitHub: https://github.com/projectmiluju/grovarc (생성 후 확인)
- 서비스 URL: https://grovarc.dev (배포 후 확인)
- Notion PRD: (작성 후 추가)
- Hugging Face 모델: (업로드 후 추가)
- 기술 블로그: https://projectmiluju.github.io
