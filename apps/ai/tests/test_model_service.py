"""ModelService A/B 백엔드 전환 테스트."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── ClaudeBackend ─────────────────────────────────────────────────────────────

async def test_claude_backend_generate(mocker):
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="## 회고\n내용입니다."))
    mocker.patch("app.services.model_service.ChatAnthropic", return_value=mock_llm)

    from app.services.model_service import ClaudeBackend
    backend = ClaudeBackend()
    result = await backend.generate("시스템 프롬프트", "유저 프롬프트")

    assert result == "## 회고\n내용입니다."
    mock_llm.ainvoke.assert_called_once()


# ── FinetunedBackend ──────────────────────────────────────────────────────────

def test_finetuned_backend_raises_without_transformers(mocker):
    """transformers 없을 때 ImportError 발생"""
    mocker.patch.dict("sys.modules", {"torch": None, "transformers": None})

    from app.services.model_service import FinetunedBackend
    backend = FinetunedBackend()

    with pytest.raises(ImportError, match="transformers"):
        backend._load()


async def test_finetuned_backend_generate(mocker):
    """transformers pipeline 모킹 후 추론"""
    mock_pipe = MagicMock(return_value=[
        {"generated_text": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "## Fine-tuned 회고\n내용"},
        ]}
    ])

    mock_torch = MagicMock()
    mock_torch.bfloat16 = "bfloat16"

    mock_transformers = MagicMock()
    mock_transformers.AutoTokenizer.from_pretrained.return_value = MagicMock()
    mock_transformers.AutoModelForCausalLM.from_pretrained.return_value = MagicMock()
    mock_transformers.pipeline.return_value = mock_pipe

    mocker.patch.dict("sys.modules", {
        "torch": mock_torch,
        "transformers": mock_transformers,
    })

    from app.services.model_service import FinetunedBackend
    backend = FinetunedBackend()
    result = await backend.generate("시스템", "유저")

    assert "Fine-tuned 회고" in result


# ── ModelService (통합) ───────────────────────────────────────────────────────

async def test_model_service_uses_claude_by_default(mocker):
    mocker.patch("app.services.model_service.settings.INFERENCE_BACKEND", "claude")
    mocker.patch("app.services.model_service.settings.ANTHROPIC_API_KEY", "dummy")

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="## 클로드 회고\n내용"))
    mocker.patch("app.services.model_service.ChatAnthropic", return_value=mock_llm)

    from app.services.model_service import ModelService
    service = ModelService()

    assert service.backend_name == "claude"

    result = await service.generate_retrospective_draft(
        logs_text="[2026-03-28] 작업\n내용",
        period_from="2026-03-28",
        period_to="2026-04-03",
    )
    assert "클로드 회고" in result


async def test_model_service_uses_finetuned_when_configured(mocker):
    mocker.patch("app.services.model_service.settings.INFERENCE_BACKEND", "finetuned")
    mocker.patch("app.services.model_service.settings.HF_MODEL_ID", "projectmiluju/grovarc-llama3-8b")
    mocker.patch("app.services.model_service.settings.HF_TOKEN", "dummy")

    mock_backend = AsyncMock()
    mock_backend.generate = AsyncMock(return_value="## Fine-tuned 회고\n내용")

    mocker.patch("app.services.model_service.FinetunedBackend", return_value=mock_backend)

    from app.services.model_service import ModelService
    service = ModelService()

    assert service.backend_name == "finetuned"

    result = await service.generate_retrospective_draft(
        logs_text="[2026-03-28] 작업\n내용",
        period_from="2026-03-28",
        period_to="2026-04-03",
        rag_context="관련 과거 패턴",
    )
    assert "Fine-tuned 회고" in result


async def test_model_service_prompt_includes_rag_context(mocker):
    """rag_context가 있을 때 유저 프롬프트에 포함되는지 확인"""
    mocker.patch("app.services.model_service.settings.INFERENCE_BACKEND", "claude")
    mocker.patch("app.services.model_service.settings.ANTHROPIC_API_KEY", "dummy")

    captured_prompt = {}

    async def capture_generate(system_prompt, user_prompt):
        captured_prompt["user"] = user_prompt
        return "## 회고\n내용"

    mock_backend = MagicMock()
    mock_backend.generate = capture_generate
    mocker.patch("app.services.model_service.ClaudeBackend", return_value=mock_backend)

    from app.services.model_service import ModelService
    service = ModelService()
    await service.generate_retrospective_draft(
        logs_text="로그 내용",
        period_from="2026-03-28",
        period_to="2026-04-03",
        rag_context="## 관련 작업 로그\n과거 패턴",
    )

    assert "관련 작업 로그" in captured_prompt["user"]


async def test_model_service_prompt_excludes_rag_when_empty(mocker):
    """rag_context 없을 때 프롬프트에 RAG 섹션 미포함 확인"""
    mocker.patch("app.services.model_service.settings.INFERENCE_BACKEND", "claude")
    mocker.patch("app.services.model_service.settings.ANTHROPIC_API_KEY", "dummy")

    captured_prompt = {}

    async def capture_generate(system_prompt, user_prompt):
        captured_prompt["user"] = user_prompt
        return "## 회고\n내용"

    mock_backend = MagicMock()
    mock_backend.generate = capture_generate
    mocker.patch("app.services.model_service.ClaudeBackend", return_value=mock_backend)

    from app.services.model_service import ModelService
    service = ModelService()
    await service.generate_retrospective_draft(
        logs_text="로그 내용",
        period_from="2026-03-28",
        period_to="2026-04-03",
        rag_context="",
    )

    assert "과거 유사 패턴" not in captured_prompt["user"]


# ── generate_draft 노드 연동 ──────────────────────────────────────────────────

async def test_generate_draft_node_uses_model_service(mocker):
    """retrospective nodes의 generate_draft가 model_service를 사용하는지 확인"""
    mock_service = AsyncMock()
    mock_service.backend_name = "claude"
    mock_service.generate_retrospective_draft = AsyncMock(
        return_value="## 노드 테스트 회고\n내용입니다."
    )
    mocker.patch("app.agents.retrospective.nodes.get_model_service", return_value=mock_service)

    from app.agents.retrospective.nodes import generate_draft
    from app.agents.retrospective.state import RetrospectiveState

    state = RetrospectiveState(
        user_id="user-123",
        period_from="2026-03-28",
        period_to="2026-04-03",
        work_logs=[
            {"id": "1", "title": "작업", "content": "내용", "log_date": "2026-03-28", "mood": None}
        ],
        rag_context="",
        analysis_summary="",
        draft_title="",
        draft_content="",
        goals=[],
        mongo_doc_id=None,
        error=None,
    )

    result = await generate_draft(state)

    assert result["draft_content"] == "## 노드 테스트 회고\n내용입니다."
    assert result["draft_title"] == "노드 테스트 회고"
    mock_service.generate_retrospective_draft.assert_called_once()
