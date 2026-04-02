from typing import TypedDict


class WorkLogItem(TypedDict):
    id: str
    title: str
    content: str
    log_date: str
    mood: str | None


class RetrospectiveState(TypedDict):
    # 입력
    user_id: str
    period_from: str  # ISO date: "2026-03-28"
    period_to: str    # ISO date: "2026-04-03"

    # 중간 상태
    work_logs: list[WorkLogItem]
    rag_context: str
    analysis_summary: str

    # 출력
    draft_title: str
    draft_content: str
    goals: list[str]

    # 저장 결과
    mongo_doc_id: str | None
    error: str | None
