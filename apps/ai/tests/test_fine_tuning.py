import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from fine_tuning.schema import SYSTEM_PROMPT, TrainingSample, build_sample


# ── schema 테스트 ──────────────────────────────────────────────────────────────

def test_build_sample_structure():
    sample = build_sample(
        logs_text="[2026-01-06] FastAPI 구현\n내용입니다.",
        period_from="2026-01-06",
        period_to="2026-01-10",
        retrospective="## 이번 주 회고\n열심히 했다.",
        source="real",
    )

    assert isinstance(sample, TrainingSample)
    assert len(sample.messages) == 3
    assert sample.messages[0].role == "system"
    assert sample.messages[1].role == "user"
    assert sample.messages[2].role == "assistant"
    assert sample.source == "real"


def test_build_sample_to_dict():
    sample = build_sample(
        logs_text="[2026-01-06] 작업\n내용",
        period_from="2026-01-06",
        period_to="2026-01-10",
        retrospective="## 회고\n내용",
        source="synthetic",
    )
    d = sample.to_dict()

    assert "messages" in d
    assert d["source"] == "synthetic"
    assert d["messages"][0]["role"] == "system"
    assert d["messages"][0]["content"] == SYSTEM_PROMPT
    assert "2026-01-06" in d["messages"][1]["content"]
    assert "## 회고" in d["messages"][2]["content"]


def test_build_sample_includes_period_in_user_prompt():
    sample = build_sample(
        logs_text="작업 내용",
        period_from="2026-03-01",
        period_to="2026-03-07",
        retrospective="회고 내용",
    )
    user_content = sample.messages[1].content
    assert "2026-03-01" in user_content
    assert "2026-03-07" in user_content


# ── build_dataset 테스트 ───────────────────────────────────────────────────────

def _make_valid_sample(assistant_text: str = "## 회고\n" + "내용 " * 50, source: str = "real") -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "작업 로그 내용"},
            {"role": "assistant", "content": assistant_text},
        ],
        "source": source,
    }


def test_validate_sample_valid():
    from fine_tuning.build_dataset import validate_sample
    assert validate_sample(_make_valid_sample()) is True


def test_validate_sample_wrong_roles():
    from fine_tuning.build_dataset import validate_sample
    sample = _make_valid_sample()
    sample["messages"][0]["role"] = "user"  # system → user로 변경
    assert validate_sample(sample) is False


def test_validate_sample_too_short():
    from fine_tuning.build_dataset import validate_sample
    sample = _make_valid_sample(assistant_text="짧음")
    assert validate_sample(sample) is False


def test_validate_sample_missing_messages():
    from fine_tuning.build_dataset import validate_sample
    assert validate_sample({}) is False
    assert validate_sample({"messages": []}) is False


def test_build_final_dataset_train_val_split():
    from fine_tuning.build_dataset import build_final_dataset

    samples = [_make_valid_sample(f"## 회고{i}\n" + "내용 " * 50) for i in range(20)]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        real_path = tmp_path / "real.jsonl"
        synthetic_path = tmp_path / "synthetic.jsonl"

        with real_path.open("w") as f:
            for s in samples[:10]:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

        with synthetic_path.open("w") as f:
            for s in samples[10:]:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

        train_count, val_count = build_final_dataset(
            real_path=real_path,
            synthetic_path=synthetic_path,
            output_dir=tmp_path,
            val_ratio=0.2,
            seed=42,
        )

        assert train_count + val_count == 20
        assert val_count == 4  # 20 * 0.2

        assert (tmp_path / "train.jsonl").exists()
        assert (tmp_path / "val.jsonl").exists()


def test_build_final_dataset_deduplication():
    from fine_tuning.build_dataset import build_final_dataset

    same_content = "## 중복 회고\n" + "내용 " * 50
    samples = [_make_valid_sample(same_content) for _ in range(5)]
    unique_sample = _make_valid_sample("## 유니크 회고\n" + "다른 내용 " * 50)
    samples.append(unique_sample)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        real_path = tmp_path / "real.jsonl"
        synthetic_path = tmp_path / "synthetic.jsonl"

        with real_path.open("w") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        synthetic_path.write_text("")

        train_count, val_count = build_final_dataset(
            real_path=real_path,
            synthetic_path=synthetic_path,
            output_dir=tmp_path,
            val_ratio=0.1,
        )

        assert train_count + val_count == 2  # 중복 5개 → 1개, 유니크 1개


# ── generate_synthetic 테스트 ─────────────────────────────────────────────────

async def test_generate_one_sample_success(mocker):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "logs": [
            {"date": "2026-01-06", "title": "작업1", "content": "내용1입니다. 열심히 했습니다."},
            {"date": "2026-01-07", "title": "작업2", "content": "내용2입니다. 계속했습니다."},
        ],
        "retrospective": "## 이번 주 회고\n" + "내용 " * 100,
    }))]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    from fine_tuning.generate_synthetic import generate_one_sample, _PERSONAS, _PERIOD_WEEKS

    result = await generate_one_sample(mock_client, _PERSONAS[0], _PERIOD_WEEKS[0])

    assert result is not None
    assert "messages" in result
    assert result["source"] == "synthetic"


async def test_generate_one_sample_too_short(mocker):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "logs": [{"date": "2026-01-06", "title": "작업", "content": "내용"}],
        "retrospective": "짧음",
    }))]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    from fine_tuning.generate_synthetic import generate_one_sample, _PERSONAS, _PERIOD_WEEKS

    result = await generate_one_sample(mock_client, _PERSONAS[0], _PERIOD_WEEKS[0])
    assert result is None
