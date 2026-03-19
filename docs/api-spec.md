# API 명세 초안

> Phase 0 산출물 — Kotlin Spring Boot REST API 기준.
> 인증: JWT Bearer Token (Authorization: Bearer {token})

---

## 기본 규칙

- Base URL: `https://api.grovarc.dev/api/v1`
- 응답 포맷: JSON
- 날짜 포맷: ISO 8601 (`2025-03-17T09:00:00Z`)
- 에러 응답:
```json
{
  "code": "LOG_NOT_FOUND",
  "message": "해당 로그를 찾을 수 없습니다."
}
```

---

## 인증 (Auth)

### POST /auth/signup
회원가입

**Request**
```json
{
  "email": "dev@example.com",
  "password": "password1234",
  "nickname": "원용"
}
```

**Response** `201`
```json
{
  "id": "uuid",
  "email": "dev@example.com",
  "nickname": "원용"
}
```

---

### POST /auth/login
로그인

**Request**
```json
{
  "email": "dev@example.com",
  "password": "password1234"
}
```

**Response** `200`
```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresIn": 3600
}
```

---

### POST /auth/refresh
액세스 토큰 갱신

**Request**
```json
{
  "refreshToken": "eyJ..."
}
```

**Response** `200`
```json
{
  "accessToken": "eyJ...",
  "expiresIn": 3600
}
```

---

### POST /auth/logout
로그아웃 (Refresh Token 무효화)

**Response** `204`

---

## 유저 (Users)

### GET /users/me
내 프로필 조회

**Response** `200`
```json
{
  "id": "uuid",
  "email": "dev@example.com",
  "nickname": "원용",
  "role": "fullstack",
  "careerYears": 2,
  "weeklyGoalHours": 40,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

---

### PATCH /users/me
프로필 수정

**Request** (변경할 필드만 포함)
```json
{
  "nickname": "원용",
  "role": "backend",
  "careerYears": 3,
  "weeklyGoalHours": 35
}
```

**Response** `200` — 수정된 프로필 반환

---

## 작업 로그 (Work Logs)

### POST /logs
로그 작성

**Request**
```json
{
  "title": "Spring Security JWT 구현",
  "content": "## 오늘 한 일\n- JWT 필터 구현\n- 토큰 검증 로직 작성",
  "durationMin": 180,
  "difficulty": 4,
  "mood": 3,
  "loggedAt": "2025-03-17",
  "tagIds": ["uuid-kotlin", "uuid-spring"]
}
```

**Response** `201`
```json
{
  "id": "uuid",
  "title": "Spring Security JWT 구현",
  "content": "...",
  "durationMin": 180,
  "difficulty": 4,
  "mood": 3,
  "loggedAt": "2025-03-17",
  "tags": [
    { "id": "uuid-kotlin", "name": "Kotlin", "color": "#7F52FF" }
  ],
  "aiSummary": null,
  "aiFeedback": null,
  "createdAt": "2025-03-17T10:00:00Z"
}
```

> AI 피드백(aiSummary, aiFeedback)은 비동기 처리 후 채워짐. 폴링 또는 WebSocket으로 수신.

---

### GET /logs
로그 목록 조회

**Query Parameters**
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| page | int | 페이지 번호 (default: 0) |
| size | int | 페이지 크기 (default: 20) |
| from | date | 시작 날짜 (YYYY-MM-DD) |
| to | date | 종료 날짜 (YYYY-MM-DD) |
| tagId | uuid | 태그 필터 |

**Response** `200`
```json
{
  "content": [ { ...log } ],
  "totalElements": 42,
  "totalPages": 3,
  "page": 0,
  "size": 20
}
```

---

### GET /logs/:id
로그 단건 조회

**Response** `200` — 단일 로그 객체

---

### PATCH /logs/:id
로그 수정

**Request** (변경할 필드만)
```json
{
  "content": "수정된 내용",
  "difficulty": 3
}
```

**Response** `200` — 수정된 로그 반환

---

### DELETE /logs/:id
로그 삭제

**Response** `204`

---

### GET /logs/stats/weekly
주간 통계

**Query Parameters**
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| weekStart | date | 주 시작일 (월요일) |

**Response** `200`
```json
{
  "weekStart": "2025-03-17",
  "totalLogs": 5,
  "totalDurationMin": 1200,
  "avgDifficulty": 3.4,
  "avgMood": 3.2,
  "tagFrequency": [
    { "tag": "Kotlin", "count": 4 },
    { "tag": "Spring", "count": 3 }
  ],
  "streak": 12
}
```

---

## 태그 (Tags)

### GET /tags
전체 태그 목록

**Response** `200`
```json
[
  { "id": "uuid", "name": "Kotlin", "color": "#7F52FF" },
  { "id": "uuid", "name": "React", "color": "#61DAFB" }
]
```

---

### POST /tags
태그 생성 (관리자 또는 유저 생성)

**Request**
```json
{
  "name": "LangGraph",
  "color": "#FF6B6B"
}
```

**Response** `201` — 생성된 태그

---

## 회고 (Retrospectives)

### GET /retrospectives
회고 목록

**Query Parameters**: `page`, `size`

**Response** `200` — 페이지네이션 형식

---

### GET /retrospectives/:id
회고 단건 조회

**Response** `200`
```json
{
  "id": "uuid",
  "weekStart": "2025-03-10",
  "weekEnd": "2025-03-16",
  "aiKeep": "이번 주 Kotlin 코루틴을 처음 적용해보며...",
  "aiProblem": "테스트 코드 작성이 다소 부족했습니다...",
  "aiTry": "다음 주엔 JUnit 통합 테스트를 3개 이상 작성해보세요.",
  "finalKeep": null,
  "finalProblem": null,
  "finalTry": null,
  "status": "draft",
  "generatedAt": "2025-03-16T18:00:00Z"
}
```

---

### PATCH /retrospectives/:id
회고 수정 (유저 검토 후 최종본 저장)

**Request**
```json
{
  "finalKeep": "코루틴 적용으로 비동기 처리 성능을 개선했습니다.",
  "finalProblem": "테스트 커버리지가 40%로 낮았습니다.",
  "finalTry": "다음 주엔 통합 테스트 5개 작성하기.",
  "status": "reviewed"
}
```

**Response** `200` — 수정된 회고 반환

---

### POST /retrospectives/:id/feedbacks
AI 초안 섹션별 피드백 저장

**Request**
```json
{
  "section": "keep",
  "accepted": true,
  "userComment": "정확히 맞아요"
}
```

**Response** `201`

---

## 성장 코칭 (Coaching)

### POST /coaching/sessions
코칭 세션 요청 (AI Agent 트리거)

**Response** `202`
```json
{
  "sessionId": "uuid",
  "status": "pending"
}
```

---

### GET /coaching/sessions/:id
코칭 세션 상태 / 결과 조회

**Response** `200`
```json
{
  "id": "uuid",
  "status": "done",
  "roadmapItems": [
    {
      "id": "uuid",
      "horizon": "short",
      "title": "Kotlin Coroutine 공식 문서 읽기",
      "description": "...",
      "resourceUrl": "https://kotlinlang.org/docs/coroutines-overview.html",
      "completed": false
    }
  ],
  "completedAt": "2025-03-17T10:05:00Z"
}
```

---

### PATCH /coaching/sessions/:id/roadmap-items/:itemId
로드맵 항목 완료 처리

**Request**
```json
{
  "completed": true
}
```

**Response** `200`

---

## 대시보드 (Dashboard)

### GET /dashboard
대시보드 종합 데이터

**Response** `200`
```json
{
  "streak": 12,
  "weeklyStats": { ... },
  "recentLogs": [ { ...log } ],
  "latestRetrospective": { ...retrospective },
  "topTags": [ { "tag": "Kotlin", "count": 15 } ]
}
```

---

## HTTP 상태 코드 정리

| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 202 | 요청 수락 (비동기 처리 시작) |
| 204 | 성공 (응답 바디 없음) |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 충돌 (중복 등) |
| 500 | 서버 에러 |
