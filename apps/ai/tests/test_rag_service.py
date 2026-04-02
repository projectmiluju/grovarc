import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.rag_service import SimilarWorkLog, build_rag_context


async def test_build_rag_context_empty(mocker):
    mock_db = AsyncMock()
    mocker.patch(
        "app.services.rag_service.search_similar",
        return_value=[],
    )
    result = await build_rag_context("회고", uuid.uuid4(), mock_db)
    assert result == ""


async def test_build_rag_context_with_results(mocker):
    mock_db = AsyncMock()
    mock_logs = [
        SimilarWorkLog(
            work_log_id=uuid.uuid4(),
            title="FastAPI 공부",
            content="오늘 FastAPI 라우터를 구현했다.",
            log_date=date(2026, 4, 1),
            similarity=0.92,
        )
    ]
    mocker.patch(
        "app.services.rag_service.search_similar",
        return_value=mock_logs,
    )
    result = await build_rag_context("FastAPI", uuid.uuid4(), mock_db)
    assert "FastAPI 공부" in result
    assert "2026-04-01" in result
