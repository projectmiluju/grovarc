import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.retrospective.state import RetrospectiveState


async def test_run_retrospective_agent(mocker):
    user_id = str(uuid.uuid4())

    # DB / LLM / MongoDB 모킹
    mocker.patch(
        "app.agents.retrospective.nodes.AsyncSessionLocal",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(
            execute=AsyncMock(return_value=AsyncMock(scalars=lambda: AsyncMock(all=lambda: [])))
        )), __aexit__=AsyncMock(return_value=False)),
    )
    mocker.patch(
        "app.agents.retrospective.nodes.build_rag_context",
        new=AsyncMock(return_value=""),
    )
    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(
        side_effect=[
            AsyncMock(content="## 이번 주 회고\n열심히 했다."),  # generate_draft
            AsyncMock(content='["목표1", "목표2", "목표3"]'),     # suggest_goals
        ]
    )
    mocker.patch("app.agents.retrospective.nodes._get_llm", return_value=mock_llm)
    mocker.patch(
        "app.agents.retrospective.nodes.get_mongo_db",
        return_value=AsyncMock(
            **{"__getitem__": lambda s, k: AsyncMock(
                insert_one=AsyncMock(return_value=AsyncMock(inserted_id="abc123"))
            )}
        ),
    )
    mocker.patch("app.agents.retrospective.nodes.httpx.AsyncClient", autospec=True)

    from app.agents.retrospective.graph import run_retrospective_agent

    result = await run_retrospective_agent(
        user_id=user_id,
        period_from="2026-03-28",
        period_to="2026-04-03",
    )

    assert result["user_id"] == user_id
    assert isinstance(result["goals"], list)
