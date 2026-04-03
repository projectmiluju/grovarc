# Grovarc MCP Server

Grovarc의 작업 로그, 회고, 코칭 데이터를 AI CLI에서 직접 조회할 수 있는 MCP(Model Context Protocol) 서버입니다.

**지원 클라이언트**: Cursor / Claude Code / Codex CLI / Gemini CLI

---

## 제공 도구 (Tools)

| Tool | 설명 |
|------|------|
| `get_work_logs` | 작업 로그 목록 조회 (페이지네이션) |
| `get_work_log` | 특정 작업 로그 상세 조회 |
| `get_retrospectives` | 회고 목록 조회 (ALL / DRAFT / PUBLISHED 필터) |
| `get_retrospective` | 특정 회고 전체 내용 조회 |
| `get_coaching_result` | 최신 성장 코칭 결과 및 8주 로드맵 조회 |
| `get_dashboard_stats` | 스트릭·주간 통계 조회 |

---

## 빠른 시작

### 1. 빌드

```bash
cd apps/mcp
bun install
bun run build   # → dist/index.js 생성
```

### 2. 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `GROVARC_API_URL` | `http://localhost:8080` | Grovarc API 서버 주소 |
| `GROVARC_API_TOKEN` | _(없음)_ | JWT 액세스 토큰 |

---

## 클라이언트별 연동 설정

### Cursor

`.cursor/mcp.json` (프로젝트 루트 또는 `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "grovarc": {
      "command": "node",
      "args": ["/절대경로/apps/mcp/dist/index.js"],
      "env": {
        "GROVARC_API_URL": "http://localhost:8080",
        "GROVARC_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

> Cursor 재시작 후 MCP 패널에서 `grovarc` 서버가 연결된 것을 확인하세요.

---

### Claude Code (Claude CLI)

```bash
claude mcp add grovarc \
  --command "node" \
  --args "/절대경로/apps/mcp/dist/index.js" \
  --env GROVARC_API_URL=http://localhost:8080 \
  --env GROVARC_API_TOKEN=your-jwt-token
```

또는 `~/.claude.json`에 직접 추가:

```json
{
  "mcpServers": {
    "grovarc": {
      "command": "node",
      "args": ["/절대경로/apps/mcp/dist/index.js"],
      "env": {
        "GROVARC_API_URL": "http://localhost:8080",
        "GROVARC_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

> `/grovarc:get_work_logs` 형태로 Claude Code 대화에서 바로 호출 가능합니다.

---

### Codex CLI (OpenAI)

`~/.codex/config.json`:

```json
{
  "mcpServers": {
    "grovarc": {
      "command": "node",
      "args": ["/절대경로/apps/mcp/dist/index.js"],
      "env": {
        "GROVARC_API_URL": "http://localhost:8080",
        "GROVARC_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

---

### Gemini CLI (Google)

`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "grovarc": {
      "command": "node",
      "args": ["/절대경로/apps/mcp/dist/index.js"],
      "env": {
        "GROVARC_API_URL": "http://localhost:8080",
        "GROVARC_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

---

## bun으로 직접 실행 (빌드 없이)

빌드 없이 바로 실행하려면 `node` 대신 `bun`을 사용합니다:

```json
{
  "command": "bun",
  "args": ["run", "/절대경로/apps/mcp/src/index.ts"]
}
```

---

## 개발

```bash
bun run dev      # watch 모드로 실행
bun run test     # vitest 단위 테스트
bun run build    # dist/ 빌드
```

---

## 동작 원리

```
AI CLI (Cursor / Claude Code / Codex CLI / Gemini CLI)
  ↕ stdio (JSON-RPC, MCP 표준 프로토콜)
Grovarc MCP Server (apps/mcp)
  ↕ HTTP REST API
Grovarc API Server (apps/api, :8080)
  ↕
PostgreSQL + MongoDB
```

모든 클라이언트가 동일한 **stdio transport**를 사용하므로 하나의 서버 바이너리로 어떤 MCP 호환 클라이언트에서도 동작합니다.
