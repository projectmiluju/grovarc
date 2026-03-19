---
title: "ADR-006 | develop 브랜치를 default 브랜치로 설정"
date: 2026-03-20
status: 결정됨
---

## 컨텍스트

`feature → develop` PR 머지 시 `Closes #이슈` 키워드가 이슈를 자동으로 닫지 않는 문제가 발생했다. GitHub의 자동 이슈 닫기는 **default 브랜치에 머지될 때만** 동작하기 때문이다. 기존 default 브랜치는 `main`이었고, 실제 작업 흐름은 `feature → develop → main` 순서라 `feature → develop` 머지 시 자동 닫기가 동작하지 않았다.

## 선택지

- **옵션 A**: `main`을 default 유지 → `feature → develop` 머지 후 이슈를 수동으로 닫음
- **옵션 B**: `develop`을 default 브랜치로 변경 → `feature → develop` 머지 시 자동 닫기 동작

## 결정

**옵션 B** — `develop`을 default 브랜치로 변경

## 이유

- 1인 프로젝트 특성상 `develop → main` 머지는 배포 시점에만 발생함
- 실질적인 작업 흐름의 종착점이 `develop`이므로, `develop`이 default인 것이 더 자연스러움
- 이슈 자동 닫기 + GitHub Projects 상태 자동 업데이트를 온전히 활용 가능

## 트레이드오프

- `develop`이 default가 되면 GitHub 레포 기본 화면에서 `develop` 브랜치 코드가 노출됨
- 외부에 레포를 공개할 경우 `main`이 더 안정된 브랜치임을 명시적으로 알리기 어려울 수 있음
- 배포 시 `main`에 머지하는 PR 생성 시 base를 명시적으로 `main`으로 지정해야 함
