#!/bin/bash

# ============================================
# Grovarc 레포 초기 구조 세팅 스크립트
# 사용법: GitHub에서 grovarc 레포 생성 후
#         클론한 디렉토리 안에서 실행
# ============================================

echo "🌱 Grovarc 레포 구조 세팅 시작..."

# ── 앱 디렉토리 ──────────────────────────────
mkdir -p apps/web      # Next.js 프론트엔드
mkdir -p apps/api      # Kotlin Spring Boot
mkdir -p apps/ai       # Python FastAPI AI 서버
mkdir -p apps/mcp      # TypeScript MCP 서버

# ── 인프라 디렉토리 ──────────────────────────
mkdir -p infra/terraform
mkdir -p infra/k8s

# ── 문서 디렉토리 ────────────────────────────
mkdir -p docs/adr

# ── GitHub 디렉토리 ──────────────────────────
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p .github/workflows

# ============================================
# 각 앱 README 생성
# ============================================

cat > apps/web/README.md << 'EOF'
# Grovarc Web

Next.js + TypeScript 기반 프론트엔드

## 기술 스택
- Next.js + TypeScript
- TailwindCSS
- Zustand
- Playwright (E2E 테스트)

## 시작하기
```bash
pnpm install
pnpm dev
```
EOF

cat > apps/api/README.md << 'EOF'
# Grovarc API

Kotlin + Spring Boot 기반 메인 백엔드 서버

## 기술 스택
- Kotlin + Spring Boot
- Spring Data JPA
- Spring Security + JWT
- Kafka
- JUnit

## 시작하기
```bash
./gradlew bootRun
```
EOF

cat > apps/ai/README.md << 'EOF'
# Grovarc AI

Python + FastAPI 기반 AI 마이크로서비스

## 기술 스택
- Python + FastAPI
- LangGraph + LangChain
- Celery + Beat
- OpenAI / Anthropic API
- Hugging Face + PyTorch + LoRA

## 시작하기
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
EOF

cat > apps/mcp/README.md << 'EOF'
# Grovarc MCP

TypeScript 기반 MCP 서버
Cursor / Claude에서 Grovarc 데이터를 직접 조회할 수 있습니다.

## 기술 스택
- TypeScript
- MCP SDK

## 시작하기
```bash
pnpm install
pnpm dev
```
EOF

# ============================================
# GitHub Issue 템플릿
# ============================================

cat > .github/ISSUE_TEMPLATE/feature.md << 'EOF'
---
name: ✨ Feature
about: 새로운 기능 요청
title: '[FEAT] '
labels: feature
---

## 개요
<!-- 어떤 기능인지 간단히 설명 -->

## 배경 / Why
<!-- 왜 이 기능이 필요한가 -->

## 구현 내용
<!-- 구체적으로 무엇을 만들 것인가 -->

## 완료 조건
- [ ] 
- [ ] 
EOF

cat > .github/ISSUE_TEMPLATE/bug.md << 'EOF'
---
name: 🐛 Bug
about: 버그 리포트
title: '[BUG] '
labels: bug
---

## 버그 설명
<!-- 어떤 버그인지 설명 -->

## 재현 방법
1. 
2. 

## 예상 동작
<!-- 어떻게 동작해야 하는가 -->

## 실제 동작
<!-- 실제로 어떻게 동작하는가 -->
EOF

# ============================================
# PR 템플릿
# ============================================

cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## 관련 이슈
closes #

## 변경 내용
<!-- 무엇을 왜 변경했는지 -->

## 체크리스트
- [ ] 테스트 코드 작성
- [ ] 로컬에서 동작 확인
- [ ] CLAUDE.md 진행 상황 업데이트
EOF

# ============================================
# .gitignore
# ============================================

cat > .gitignore << 'EOF'
# 환경변수
.env
.env.local
.env.*.local

# Node
node_modules/
.next/
dist/
.pnpm-store/

# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/

# Kotlin / Java
build/
*.jar
*.class
.gradle/

# IDE
.idea/
.vscode/
*.iml

# OS
.DS_Store
Thumbs.db

# Terraform
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars

# K8s 시크릿
*-secret.yaml
EOF

# ============================================
# 루트 README
# ============================================

cat > README.md << 'EOF'
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
EOF

# ============================================
# docs 기본 파일
# ============================================

cat > docs/PRD.md << 'EOF'
# Grovarc PRD

> 작성 중 — Phase 0에서 완성 예정

## Why
## 타겟 유저
## 핵심 지표
## 기능 목록 (MoSCoW)
## 유저 스토리
EOF

cat > docs/architecture.md << 'EOF'
# Grovarc 아키텍처

> 작성 중 — Phase 0에서 완성 예정
EOF

cat > docs/adr/.gitkeep << 'EOF'
EOF

# ============================================
# 각 앱 .gitkeep (빈 디렉토리 유지)
# ============================================

touch infra/terraform/.gitkeep
touch infra/k8s/.gitkeep
touch .github/workflows/.gitkeep

# ============================================
# 완료
# ============================================

echo ""
echo "✅ Grovarc 레포 구조 세팅 완료!"
echo ""
echo "📁 생성된 구조:"
find . -not -path './.git/*' -not -name '.git' | sort | sed 's|[^/]*/|  |g'
echo ""
echo "🚀 다음 단계:"
echo "  1. CLAUDE.md를 루트에 복사"
echo "  2. git add . && git commit -m 'chore: init project structure'"
echo "  3. git push"
