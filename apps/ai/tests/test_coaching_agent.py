import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest


async def test_collect_recent_logs_empty(mocker):
    """작업 로그가 없는 경우 빈 리스트 반환"""
    user_id = str(uuid.uuid4())

    mocker.patch(
        "app.agents.coaching.nodes.AsyncSessionLocal",
        return_value=AsyncMock(
            __aenter__=AsyncMock(
                return_value=AsyncMock(
                    execute=AsyncMock(
                        return_value=AsyncMock(scalars=lambda: AsyncMock(all=lambda: []))
                    )
                )
            ),
            __aexit__=AsyncMock(return_value=False),
        ),
    )

    from app.agents.coaching.nodes import collect_recent_logs
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=user_id,
        recent_logs=[],
        rag_context="",
        weak_stacks=[],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await collect_recent_logs(state)
    assert result["recent_logs"] == []


async def test_analyze_weak_stacks_no_logs(mocker):
    """로그 없을 때 빈 weak_stacks 반환"""
    from app.agents.coaching.nodes import analyze_weak_stacks
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=str(uuid.uuid4()),
        recent_logs=[],
        rag_context="",
        weak_stacks=[],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await analyze_weak_stacks(state)
    assert result["weak_stacks"] == []
    assert result["rag_context"] == ""


async def test_analyze_weak_stacks_with_logs(mocker):
    """로그 있을 때 LLM이 반환한 스택 목록 파싱"""
    user_id = str(uuid.uuid4())

    mocker.patch(
        "app.agents.coaching.nodes.AsyncSessionLocal",
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=AsyncMock()),
            __aexit__=AsyncMock(return_value=False),
        ),
    )
    mocker.patch(
        "app.agents.coaching.nodes.build_rag_context",
        new=AsyncMock(return_value=""),
    )
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=MagicMock(content='["Kubernetes", "Redis", "JUnit"]')
    )
    mocker.patch("app.agents.coaching.nodes._get_llm", return_value=mock_llm)

    from app.agents.coaching.nodes import analyze_weak_stacks
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=user_id,
        recent_logs=[
            {"id": "1", "title": "FastAPI 구현", "content": "...", "log_date": "2026-01-01", "mood": None}
        ],
        rag_context="",
        weak_stacks=[],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await analyze_weak_stacks(state)
    assert result["weak_stacks"] == ["Kubernetes", "Redis", "JUnit"]


async def test_search_resources_empty_stacks():
    """스택 없으면 검색 스킵"""
    from app.agents.coaching.nodes import search_resources
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=str(uuid.uuid4()),
        recent_logs=[],
        rag_context="",
        weak_stacks=[],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await search_resources(state)
    assert result["search_results"] == {}


async def test_search_resources_with_stacks(mocker):
    """스택별 DuckDuckGo 검색 수행"""
    mock_search = MagicMock()
    mock_search.run = MagicMock(return_value="검색 결과 텍스트")
    mocker.patch("app.agents.coaching.nodes._get_search", return_value=mock_search)

    from app.agents.coaching.nodes import search_resources
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=str(uuid.uuid4()),
        recent_logs=[],
        rag_context="",
        weak_stacks=["Kubernetes", "Redis"],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await search_resources(state)
    assert "Kubernetes" in result["search_results"]
    assert "Redis" in result["search_results"]
    assert result["search_results"]["Kubernetes"] == "검색 결과 텍스트"


async def test_generate_roadmap_no_stacks():
    """스택 없으면 기본 메시지 반환"""
    from app.agents.coaching.nodes import generate_roadmap
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=str(uuid.uuid4()),
        recent_logs=[],
        rag_context="",
        weak_stacks=[],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await generate_roadmap(state)
    assert result["roadmap"] == "분석할 작업 로그가 없습니다."


async def test_generate_roadmap_with_stacks(mocker):
    """스택 있을 때 LLM으로 로드맵 생성"""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="# 8주 학습 로드맵\n..."))
    mocker.patch("app.agents.coaching.nodes._get_llm", return_value=mock_llm)

    from app.agents.coaching.nodes import generate_roadmap
    from app.agents.coaching.state import CoachingState

    state = CoachingState(
        user_id=str(uuid.uuid4()),
        recent_logs=[],
        rag_context="",
        weak_stacks=["Kubernetes"],
        search_results={"Kubernetes": "검색 결과"},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )

    result = await generate_roadmap(state)
    assert "8주" in result["roadmap"]


async def test_run_coaching_agent_full(mocker):
    """전체 그래프 실행 통합 테스트"""
    user_id = str(uuid.uuid4())

    mocker.patch(
        "app.agents.coaching.nodes.AsyncSessionLocal",
        return_value=AsyncMock(
            __aenter__=AsyncMock(
                return_value=AsyncMock(
                    execute=AsyncMock(
                        return_value=AsyncMock(scalars=lambda: AsyncMock(all=lambda: []))
                    )
                )
            ),
            __aexit__=AsyncMock(return_value=False),
        ),
    )
    mocker.patch(
        "app.agents.coaching.nodes.build_rag_context",
        new=AsyncMock(return_value=""),
    )
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        side_effect=[
            MagicMock(content='["Kubernetes", "Redis"]'),       # analyze_weak_stacks
            MagicMock(content="# 8주 학습 로드맵\n내용"),        # generate_roadmap
        ]
    )
    mocker.patch("app.agents.coaching.nodes._get_llm", return_value=mock_llm)

    mock_search = MagicMock()
    mock_search.run = MagicMock(return_value="검색 결과")
    mocker.patch("app.agents.coaching.nodes._get_search", return_value=mock_search)

    mocker.patch(
        "app.agents.coaching.nodes.get_mongo_db",
        return_value=MagicMock(
            **{
                "__getitem__": lambda s, k: AsyncMock(
                    insert_one=AsyncMock(
                        return_value=MagicMock(inserted_id="mongo123")
                    )
                )
            }
        ),
    )

    from app.agents.coaching.graph import run_coaching_agent

    result = await run_coaching_agent(user_id=user_id)

    assert result["user_id"] == user_id
    assert isinstance(result["weak_stacks"], list)
    assert isinstance(result["roadmap"], str)
    assert result["mongo_doc_id"] == "mongo123"
