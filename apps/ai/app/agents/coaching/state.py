from typing import TypedDict

from app.agents.retrospective.state import WorkLogItem


class CoachingState(TypedDict):
    # 입력
    user_id: str

    # 중간 상태
    recent_logs: list[WorkLogItem]   # 최근 3개월 작업 로그
    rag_context: str                  # 벡터 검색 컨텍스트
    weak_stacks: list[str]            # 부족한 기술 스택 목록
    search_results: dict[str, str]    # stack -> 검색 결과

    # 출력
    roadmap: str                      # 개인화 학습 로드맵 (마크다운)

    # 저장 결과
    mongo_doc_id: str | None
    error: str | None
