# DB 스키마 초안

> Phase 0 산출물 — PostgreSQL 기준으로 작성. pgvector 확장 포함.

---

## ERD 개요

```
users
  └─< work_logs
        └─< log_tags (work_log ↔ tags 연결)
  └─< retrospectives
        └─< retrospective_feedbacks
  └─< coaching_sessions
        └─< roadmap_items

tags (전체 공유 태그 풀)
```

---

## 테이블 정의

### users

```sql
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255),                      -- OAuth 사용자는 NULL
  nickname      VARCHAR(100) NOT NULL,
  role          VARCHAR(50) NOT NULL DEFAULT 'developer',  -- 직군
  career_years  SMALLINT DEFAULT 0,                -- 경력 연차
  weekly_goal_hours SMALLINT DEFAULT 0,            -- 주간 목표 시간
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### work_logs

```sql
CREATE TABLE work_logs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title         VARCHAR(200),
  content       TEXT NOT NULL,                     -- Markdown
  duration_min  INTEGER DEFAULT 0,                 -- 소요 시간 (분)
  difficulty    SMALLINT CHECK (difficulty BETWEEN 1 AND 5),
  mood          SMALLINT CHECK (mood BETWEEN 1 AND 5),
  logged_at     DATE NOT NULL DEFAULT CURRENT_DATE,-- 실제 작업 날짜
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- AI 피드백 (비동기로 채워짐)
  ai_summary    TEXT,
  ai_feedback   TEXT,
  embedding     vector(1536)                       -- pgvector: RAG용
);

CREATE INDEX ON work_logs (user_id, logged_at DESC);
CREATE INDEX ON work_logs USING ivfflat (embedding vector_cosine_ops);
```

### tags

```sql
CREATE TABLE tags (
  id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name  VARCHAR(100) NOT NULL UNIQUE,    -- 예: "Kotlin", "React", "회의"
  color VARCHAR(7)                       -- HEX 색상 코드
);
```

### log_tags (work_logs ↔ tags 다대다)

```sql
CREATE TABLE log_tags (
  log_id UUID NOT NULL REFERENCES work_logs(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (log_id, tag_id)
);
```

### retrospectives

```sql
CREATE TABLE retrospectives (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  week_start      DATE NOT NULL,                    -- 해당 주 월요일
  week_end        DATE NOT NULL,                    -- 해당 주 일요일

  -- AI 생성 초안
  ai_keep         TEXT,                             -- 잘한 점
  ai_problem      TEXT,                             -- 개선할 점
  ai_try          TEXT,                             -- 다음 주 시도

  -- 유저 최종본 (수정 후 저장)
  final_keep      TEXT,
  final_problem   TEXT,
  final_try       TEXT,

  status          VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft | reviewed | published
  generated_at    TIMESTAMPTZ,
  reviewed_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE (user_id, week_start)
);

CREATE INDEX ON retrospectives (user_id, week_start DESC);
```

### retrospective_feedbacks

```sql
-- 유저가 AI 초안의 각 섹션에 수용/거부 피드백을 남긴 것
CREATE TABLE retrospective_feedbacks (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  retrospective_id    UUID NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
  section             VARCHAR(20) NOT NULL,    -- keep | problem | try
  accepted            BOOLEAN NOT NULL,        -- AI 제안 수용 여부
  user_comment        TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### coaching_sessions

```sql
CREATE TABLE coaching_sessions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status      VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | processing | done | failed
  requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);
```

### roadmap_items

```sql
CREATE TABLE roadmap_items (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coaching_session_id UUID NOT NULL REFERENCES coaching_sessions(id) ON DELETE CASCADE,
  horizon             VARCHAR(20) NOT NULL,    -- short | mid | long
  title               VARCHAR(200) NOT NULL,
  description         TEXT,
  resource_url        TEXT,
  completed           BOOLEAN NOT NULL DEFAULT FALSE,
  completed_at        TIMESTAMPTZ,
  sort_order          SMALLINT NOT NULL DEFAULT 0
);
```

---

## MongoDB 컬렉션 (AI 분석 결과 저장)

```js
// ai_analysis_results
{
  _id: ObjectId,
  user_id: "UUID",
  type: "weekly_pattern" | "coaching_report",
  reference_id: "UUID",  // retrospective_id 또는 coaching_session_id
  payload: {
    // LangGraph Agent가 생성한 비정형 분석 결과
    // 예: 기술 스택 빈도, 시간 분포, 감정 트렌드 등
  },
  created_at: ISODate
}
```

---

## Redis 키 설계

```
grovarc:user:{user_id}:streak          → 연속 기록일 수 (TTL: 48시간)
grovarc:user:{user_id}:weekly_summary  → 주간 요약 캐시 (TTL: 1시간)
grovarc:retro:{retro_id}:status        → 회고 생성 진행 상태 (TTL: 24시간)
grovarc:coaching:{session_id}:status   → 코칭 세션 진행 상태 (TTL: 24시간)
```

---

## 인덱스 전략

| 테이블 | 컬럼 | 이유 |
|--------|------|------|
| work_logs | (user_id, logged_at DESC) | 유저별 최근 로그 조회 |
| work_logs | embedding (ivfflat) | RAG 유사도 검색 |
| retrospectives | (user_id, week_start DESC) | 유저별 회고 목록 |
| log_tags | (tag_id) | 태그별 로그 집계 |

---

## 마이그레이션 전략

- 마이그레이션 도구: Flyway (Kotlin Spring Boot와 통합)
- 파일 위치: `apps/api/src/main/resources/db/migration/`
- 네이밍: `V1__create_users.sql`, `V2__create_work_logs.sql` ...
