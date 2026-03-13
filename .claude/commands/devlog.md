# devlog-agent

개발 작업이 끝난 후 실행하는 subagent.
오늘 작업 내용을 바탕으로 아래 5가지를 자동으로 처리한다.

1. CLAUDE.md 진행 상황 업데이트
2. 개발일지 MDX 파일 생성 (템플릿 기반)
3. 오늘 작업 요약 기록
4. git commit 메시지 생성
5. ADR 작성 (기술 결정이 있었을 경우)

---

## 사용법

```bash
# 작업 끝난 후 Claude Code에서 실행
claude devlog-agent.md

# 또는 .claude/commands/ 에 넣고
/devlog
```

---

## 실행 프롬프트

아래 내용을 Claude Code에 그대로 붙여넣기:

```
아래 순서대로 실행해줘.

## STEP 1 — 오늘 작업 파악
CLAUDE.md를 읽고 현재 Phase와 마지막 작업을 확인해.
그다음 git diff HEAD 또는 git status로 오늘 변경된 파일 목록을 파악해.

## STEP 2 — 나에게 질문
오늘 작업을 파악한 후, 개발일지 작성에 필요한 것들을 한 번에 물어봐.
(여러 번 나눠서 묻지 말고 한 번에 질문 목록으로)

질문 항목:
- 오늘 한 일 (핵심만)
- 막혔던 것과 해결 방법 (없으면 없다고)
- 기술 결정이 있었는지 (ADR 작성 여부 판단용)
- 다음에 할 것

## STEP 3 — CLAUDE.md 업데이트
답변을 바탕으로 CLAUDE.md의 "현재 진행 상황" 섹션을 업데이트해.

## STEP 4 — 개발일지 MDX 생성
아래 템플릿 형식으로 docs/devlog/ 디렉토리에 MDX 파일을 생성해.
파일명: YYYY-MM-DD-grovarc-devlog-{번호}.mdx

템플릿:
---
title: "Grovarc 개발기 #{번호} — {제목}"
date: {오늘날짜}
summary: "{한 줄 요약}"
tags: [{관련태그}]
category: "til"
series: "Grovarc 개발기"
---

# Grovarc 개발기 #{번호} — {제목}

{오늘 작업의 배경과 목적을 2~3줄로}

---

## 목표

- {목표1}
- {목표2}

---

## 핵심 구현 포인트

### 1) {포인트 제목}

{설명}

```{언어}
{코드 스니펫 (있을 경우)}
```

### 2) {포인트 제목}

{설명}

---

## 트러블슈팅 / 고민 포인트

### {이슈 제목} (없으면 이 섹션 생략)

- **원인**: {원인}
- **해결**: {해결}

---

## 결과

- {결과1}
- {결과2}

---

## 다음 개선 아이디어

- {다음 할 것1}
- {다음 할 것2}

## STEP 5 — ADR 작성 (기술 결정이 있었을 경우에만)
기술 결정이 있었다면 docs/adr/ 디렉토리에 아래 형식으로 작성해.
파일명: ADR-{번호}-{제목}.md

---
title: "ADR-{번호} | {기술 결정 제목}"
date: {오늘날짜}
status: 결정됨
---

## 컨텍스트
{왜 이 결정이 필요했는가}

## 선택지
- 옵션 A:
- 옵션 B:

## 결정
{무엇을 선택했는가}

## 이유
{왜 선택했는가}

## 트레이드오프
{포기한 것}

## STEP 6 — git commit 메시지 생성
오늘 변경된 파일들을 분석해서 Conventional Commits 형식으로
커밋 메시지를 생성해. 파일별로 커밋을 나눠야 한다면 여러 개 제안해줘.

형식:
{type}({scope}): {description}

type: feat / fix / docs / chore / refactor / test / infra
scope: web / api / ai / mcp / infra / docs

예시:
docs(docs): add PRD and architecture docs
chore(root): init monorepo structure with apps and infra dirs
```

---

## .claude/commands/ 에 등록하는 법

Claude Code에서 `/` 커맨드로 바로 실행하려면:

```bash
# 레포 루트에서
mkdir -p .claude/commands
cp devlog-agent.md .claude/commands/devlog.md
```

그러면 Claude Code에서 `/devlog` 로 바로 실행 가능.

---

## 실행 예시

```
나: /devlog

Claude: CLAUDE.md와 git status 확인했어요. 오늘 변경된 파일들이에요.
        - infra/terraform/main.tf (신규)
        - infra/terraform/variables.tf (신규)
        - infra/k8s/namespace.yaml (신규)

        개발일지 작성을 위해 한 번에 물어볼게요:
        1. 오늘 한 일 핵심이 뭐예요?
        2. 막혔던 것과 해결 방법이 있었나요?
        3. 기술 결정(ADR 남길 것)이 있었나요?
        4. 다음에 할 것은 뭔가요?

나: Terraform으로 EKS 클러스터 세팅했어.
    IAM 권한 문제로 막혔는데 AssumeRole 정책 추가해서 해결했어.
    Terraform vs AWS CDK 고민했는데 Terraform으로 결정했어.
    다음은 GitHub Actions CI/CD 연결이야.

Claude: [CLAUDE.md 업데이트]
        [docs/devlog/2026-03-15-grovarc-devlog-02.mdx 생성]
        [docs/adr/ADR-005-terraform-vs-cdk.md 생성]
        
        커밋 메시지 제안:
        infra(terraform): add EKS cluster and IAM role configuration
        docs(adr): add ADR-005 Terraform vs AWS CDK decision
```
