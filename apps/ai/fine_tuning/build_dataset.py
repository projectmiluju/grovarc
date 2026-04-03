"""실제 데이터 + 합성 데이터를 병합하여 최종 학습 데이터셋(train/val) 생성.

사용법:
    python -m fine_tuning.build_dataset \
        --real fine_tuning/data/real.jsonl \
        --synthetic fine_tuning/data/synthetic.jsonl \
        --output-dir fine_tuning/data \
        --val-ratio 0.1
"""

import argparse
import json
import logging
import random
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        logger.warning("파일 없음: %s", path)
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def validate_sample(sample: dict) -> bool:
    """최소 품질 기준 검증"""
    messages = sample.get("messages", [])
    if len(messages) != 3:
        return False
    roles = [m.get("role") for m in messages]
    if roles != ["system", "user", "assistant"]:
        return False
    # assistant 응답이 너무 짧으면 제외
    assistant_content = messages[2].get("content", "")
    if len(assistant_content) < 200:
        return False
    return True


def build_final_dataset(
    real_path: Path,
    synthetic_path: Path,
    output_dir: Path,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> tuple[int, int]:
    """병합 → 정제 → train/val 분리 → 저장.

    Returns:
        (train_count, val_count)
    """
    real_samples = load_jsonl(real_path)
    synthetic_samples = load_jsonl(synthetic_path)

    logger.info("실제: %d건, 합성: %d건", len(real_samples), len(synthetic_samples))

    all_samples = real_samples + synthetic_samples

    # 품질 검증
    valid_samples = [s for s in all_samples if validate_sample(s)]
    dropped = len(all_samples) - len(valid_samples)
    if dropped:
        logger.warning("품질 기준 미달로 %d건 제외", dropped)

    # 중복 제거 (assistant content 기준)
    seen: set[str] = set()
    deduped = []
    for s in valid_samples:
        key = s["messages"][2]["content"][:100]
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    logger.info("중복 제거 후: %d건 → %d건", len(valid_samples), len(deduped))

    # 셔플 후 train/val 분리
    random.seed(seed)
    random.shuffle(deduped)

    val_count = max(1, int(len(deduped) * val_ratio))
    val_samples = deduped[:val_count]
    train_samples = deduped[val_count:]

    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / "train.jsonl"
    val_path = output_dir / "val.jsonl"

    with train_path.open("w", encoding="utf-8") as f:
        for s in train_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    with val_path.open("w", encoding="utf-8") as f:
        for s in val_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    logger.info("train: %d건 → %s", len(train_samples), train_path)
    logger.info("val:   %d건 → %s", len(val_samples), val_path)
    return len(train_samples), len(val_samples)


def main() -> None:
    parser = argparse.ArgumentParser(description="최종 학습 데이터셋(train/val) 생성")
    parser.add_argument("--real", type=Path, default=Path("fine_tuning/data/real.jsonl"))
    parser.add_argument("--synthetic", type=Path, default=Path("fine_tuning/data/synthetic.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("fine_tuning/data"))
    parser.add_argument("--val-ratio", type=float, default=0.1, help="검증 셋 비율 (기본: 0.1)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    build_final_dataset(args.real, args.synthetic, args.output_dir, args.val_ratio, args.seed)


if __name__ == "__main__":
    main()
