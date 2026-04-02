from unittest.mock import AsyncMock, patch

import pytest

from app.kafka.consumer import _handle_work_log_saved
from app.kafka.schemas import WorkLogSavedEvent


async def test_handle_work_log_saved_logs(caplog):
    event = WorkLogSavedEvent(
        workLogId="aaaaaaaa-0000-0000-0000-000000000001",
        userId="bbbbbbbb-0000-0000-0000-000000000001",
        logDate="2026-04-03",
    )
    with caplog.at_level("INFO"):
        await _handle_work_log_saved(event)

    assert "aaaaaaaa-0000-0000-0000-000000000001" in caplog.text


async def test_work_log_saved_event_schema():
    raw = {
        "workLogId": "aaaaaaaa-0000-0000-0000-000000000001",
        "userId": "bbbbbbbb-0000-0000-0000-000000000001",
        "logDate": "2026-04-03",
    }
    event = WorkLogSavedEvent(**raw)
    assert event.workLogId == raw["workLogId"]
    assert event.userId == raw["userId"]
    assert event.logDate == raw["logDate"]
