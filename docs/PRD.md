# Grovarc PRD
> 작성일: 2026-03-14  
> 최종 업데이트: 2026-04-03  
> 작성자: 정원용  
> 상태: **완성 (Phase 7 기준)**

---

## 1. Why — 왜 만드는가

### 배경
개발자는 매일 성장하지만 기록하지 않아서 자신의 성장을 인식하지 못한다.

### 핵심 문제
```
뭘 했는지 기억이 안 남
    ↓
회고를 쓰고 싶은데 시작이 막막함
    ↓
성장하고 있는지 체감이 안 됨
    ↓
열심히 하는데 쌓이는 느낌이 없음
```

### Grovarc의 답
> 기록의 허들을 낮추고, AI가 성장을 대신 보여준다.

---

## 2. 타겟 유저

### 페르소나
- 처음부터 끝까지 스스로 결정하며 성장하고 싶은 개발자
- 회고의 필요성은 알지만 매번 작성이 막막한 개발자
- 자신이 얼마나 성장했는지 객관적으로 보고 싶은 개발자

### 타겟 범위
- 주니어 ~ 미드레벨 개발자
- 사이드 프로젝트를 진행 중인 개발자
- 취업 준비 중인 개발자 (포트폴리오 정리 용도)

---

## 3. 핵심 지표 (KPI)

| 지표 | 목표 |
|------|------|
| MAU | 런칭 3개월 내 500명 |
| 로그 작성 주기 | 주 3회 이상 작성 유저 비율 40% |
| 회고 생성 후 수정율 | 60% 이상 (AI 초안이 유용하다는 지표) |
| D7 리텐션 | 30% 이상 |

---

## 4. 기능 목록 (MoSCoW)

### Must Have — 구현 완료 ✅
| 기능 | 설명 | 구현 |
|------|------|------|
| 작업 로그 입력 | 날짜·기분·태그와 함께 하루 작업 기록 | Phase 5 |
| AI 주간 회고 자동 생성 | Celery Beat + LangGraph로 매주 월요일 회고 초안 자동 작성 | Phase 3 |
| 성장 코칭 Agent | 최근 3개월 로그 분석 → 부족 기술 스택 → 8주 로드맵 | Phase 3 |
| 스트릭 & 통계 대시보드 | 연속 작성일, 주간 차트 시각화 | Phase 5 |
| 인증 (회원가입/로그인) | JWT + Refresh Token, 자동 갱신 | Phase 5 |

### Should Have — 구현 완료 ✅
| 기능 | 설명 | 구현 |
|------|------|------|
| RAG 기반 유사 패턴 검색 | pgvector로 과거 로그에서 유사 맥락 검색 | Phase 3 |
| Fine-tuned 모델 A/B | LLaMA 3 + LoRA / Claude API 전환 가능 | Phase 4 |
| MCP 서버 | Cursor / Claude Code / Codex CLI / Gemini CLI 연동 | Phase 6 |

### Could Have — 런칭 후
| 기능 | 설명 |
|------|------|
| 월간 리포트 공유 | 월간 성장 리포트를 링크로 공유 |
| 팀 대시보드 | 팀 단위 성장 현황 집계 |

### Won't Have — 이번 버전
- 소셜 피드 (다른 개발자 로그 구경)
- 모바일 앱
- 실시간 협업

---

## 5. 유저 스토리

### 핵심 플로우
```
1. 회원가입 / 로그인
2. 오늘의 작업 로그 입력
   - 날짜, 제목, 본문
   - 기분 (😊 GREAT ~ 😩 TERRIBLE)
   - 기술 태그
3. 주간 회고 자동 생성 (매주 월요일 AI가 자동 생성)
4. 회고 확인 및 수정 → 발행
5. 성장 코칭 요청 → 8주 학습 로드맵 확인
6. 대시보드에서 스트릭 & 통계 확인
```

### 유저 스토리 상세
| As a... | I want to... | So that... |
|---------|--------------|------------|
| 개발자 | 오늘 한 일을 빠르게 기록하고 싶다 | 나중에 회고할 때 맥락을 잃지 않을 수 있다 |
| 개발자 | 매주 회고를 자동으로 받고 싶다 | 직접 쓰는 부담 없이 회고를 유지할 수 있다 |
| 개발자 | 부족한 기술 스택을 파악하고 싶다 | 다음에 무엇을 공부할지 방향을 잡을 수 있다 |
| 개발자 | AI CLI에서 내 회고 데이터를 조회하고 싶다 | 개발 중 컨텍스트로 바로 활용할 수 있다 |
| 개발자 | 스트릭과 통계를 보고 싶다 | 성장하고 있다는 체감을 얻을 수 있다 |

---

## 6. 비즈니스 모델 (런칭 후)

| 플랜 | 가격 | 내용 |
|------|------|------|
| Free | 무료 | 로그 입력 + 기본 회고 (월 4회) |
| Pro | 월 9,900원 | 무제한 회고 + RAG 검색 + 성장 코칭 Agent |

---

## 7. 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Next.js 16, React 19, TypeScript, TailwindCSS, Zustand, Playwright |
| Backend | Kotlin, Spring Boot, JPA, Spring Security + JWT, Kafka |
| AI | Python, FastAPI, LangGraph, Celery + Beat, LLaMA 3 + LoRA, pgvector + RAG |
| MCP | TypeScript, @modelcontextprotocol/sdk, stdio transport |
| DB | PostgreSQL + pgvector, Redis, MongoDB |
| Infra | Kubernetes (EKS), Terraform, Docker, Prometheus + Grafana, GitHub Actions |

---

## 8. 마일스톤 (실제 완료 기준)

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 0 | 기획 & 설계 | 🔲 |
| Phase 1 | 인프라 & 환경 세팅 | 🔲 |
| Phase 2 | 백엔드 코어 (Kotlin Spring Boot, CRUD, Kafka) | ✅ 완료 |
| Phase 3 | AI 서버 코어 (FastAPI, LangGraph, RAG, Celery) | ✅ 완료 |
| Phase 4 | Fine-tuning (LLaMA 3 + LoRA, HuggingFace Hub) | ✅ 완료 |
| Phase 5 | 프론트엔드 (Next.js 16, React 19, Playwright) | ✅ 완료 |
| Phase 6 | MCP 서버 (Cursor / Claude Code / Codex CLI / Gemini CLI) | ✅ 완료 |
| Phase 7 | PM 산출물 & 블로그 | ✅ 완료 |
| Phase 8 | QA & 런칭 | ✅ 완료 |
