"""upload_to_hub 테스트 — HF API는 모킹하여 실제 업로드 없이 검증."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fine_tuning.upload_to_hub import MODEL_CARD_TEMPLATE, create_model_card, upload_model


def test_create_model_card_writes_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "README.md"
        create_model_card(path)

        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "grovarc-llama3-8b" in content
        assert "QLoRA" in content
        assert "meta-llama/Meta-Llama-3-8B-Instruct" in content


def test_create_model_card_with_extra_info():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "README.md"
        create_model_card(path, extra_info={"train_samples": 500, "val_samples": 55})

        content = path.read_text(encoding="utf-8")
        assert "train_samples" in content
        assert "500" in content


def test_model_card_template_has_required_sections():
    assert "## 모델 설명" in MODEL_CARD_TEMPLATE
    assert "## 사용법" in MODEL_CARD_TEMPLATE
    assert "## 학습 하이퍼파라미터" in MODEL_CARD_TEMPLATE
    assert "## 한계" in MODEL_CARD_TEMPLATE
    assert "pipeline_tag: text-generation" in MODEL_CARD_TEMPLATE


@patch("fine_tuning.upload_to_hub.HfApi")
def test_upload_model_creates_repo_and_uploads(mock_hf_api_cls):
    mock_api = MagicMock()
    mock_hf_api_cls.return_value = mock_api

    with tempfile.TemporaryDirectory() as tmp:
        model_dir = Path(tmp)
        # 더미 모델 파일 생성
        (model_dir / "config.json").write_text("{}", encoding="utf-8")

        url = upload_model(
            model_dir=model_dir,
            repo_id="projectmiluju/grovarc-llama3-8b",
            hf_token="dummy-token",
            private=True,
        )

    mock_api.create_repo.assert_called_once_with(
        repo_id="projectmiluju/grovarc-llama3-8b",
        repo_type="model",
        private=True,
        exist_ok=True,
    )
    mock_api.upload_folder.assert_called_once()
    assert "huggingface.co/projectmiluju/grovarc-llama3-8b" in url


@patch("fine_tuning.upload_to_hub.HfApi")
def test_upload_model_auto_creates_model_card(mock_hf_api_cls):
    """README.md 없으면 자동 생성 확인"""
    mock_api = MagicMock()
    mock_hf_api_cls.return_value = mock_api

    with tempfile.TemporaryDirectory() as tmp:
        model_dir = Path(tmp)
        assert not (model_dir / "README.md").exists()

        upload_model(
            model_dir=model_dir,
            repo_id="projectmiluju/grovarc-llama3-8b",
            hf_token="dummy-token",
        )

        assert (model_dir / "README.md").exists()


@patch("fine_tuning.upload_to_hub.HfApi")
def test_upload_model_adapter_commit_message(mock_hf_api_cls):
    """adapter_only=True일 때 커밋 메시지 확인"""
    mock_api = MagicMock()
    mock_hf_api_cls.return_value = mock_api

    with tempfile.TemporaryDirectory() as tmp:
        upload_model(
            model_dir=Path(tmp),
            repo_id="projectmiluju/grovarc-llama3-8b-adapter",
            hf_token="dummy-token",
            adapter_only=True,
        )

    call_kwargs = mock_api.upload_folder.call_args.kwargs
    assert "adapter" in call_kwargs["commit_message"].lower()
