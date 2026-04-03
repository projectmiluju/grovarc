"""실제 DB 데이터로 Fine-tuning 데이터셋 생성.

WorkLog + Retrospective 페어를 PostgreSQL에서 읽어 ChatML JSONL로 변환합니다.

사용법:
    python -m fine_tuning.prepare_dataset --output fine_tuning/data/real.jsonl
"""

import argparse
import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path

from sqlalchemy import Date, String, Text, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AsyncSessionLocal, Base
from app.models.work_log import WorkLog
from fine_tuning.schema import build_sample

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# Retrospective 읽기 전용 모델 (Spring Boot가 관리하는 테이블)
class Retrospective(Base):
    __tablename__ = "retrospectives"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    period_from: Mapped[str] = mapped_column(Date, nullable=False)
    period_to: Mapped[str] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PUBLISHED")


async def export_real_samples(output_path: Path, min_log_count: int = 3) -> int:
    """실제 DB에서 (WorkLog 묶음, Retrospective) 페어를 추출해 JSONL로 저장.

    Returns:
        저장된 샘플 수
    """
    samples = []

    async with AsyncSessionLocal() as db:
        # PUBLISHED 상태 회고만 추출
        retros_result = await db.execute(
            select(Retrospective).where(Retrospective.status == "PUBLISHED")
        )
        retrospectives = retros_result.scalars().all()
        logger.info("PUBLISHED 회고 %d건 조회", len(retrospectives))

        for retro in retrospectives:
            # 해당 기간의 WorkLog 수집
            logs_result = await db.execute(
                select(WorkLog)
                .where(
                    WorkLog.user_id == retro.user_id,
                    WorkLog.log_date >= retro.period_from,
                    WorkLog.log_date <= retro.period_to,
                )
                .order_by(WorkLog.log_date)
            )
            logs = logs_result.scalars().all()

            if len(logs) < min_log_count:
                logger.debug("로그 부족으로 스킵 retroId=%s count=%d", retro.id, len(logs))
                continue

            logs_text = "\n\n".join(
                f"[{log.log_date}] {log.title}\n{log.content}" for log in logs
            )

            sample = build_sample(
                logs_text=logs_text,
                period_from=str(retro.period_from),
                period_to=str(retro.period_to),
                retrospective=retro.content,
                source="real",
            )
            samples.append(sample)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample.to_dict(), ensure_ascii=False) + "\n")

    logger.info("실제 데이터 %d건 저장 → %s", len(samples), output_path)
    return len(samples)


def main() -> None:
    parser = argparse.ArgumentParser(description="DB → Fine-tuning 데이터셋 변환")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("fine_tuning/data/real.jsonl"),
        help="출력 JSONL 파일 경로",
    )
    parser.add_argument(
        "--min-logs",
        type=int,
        default=3,
        help="샘플로 사용할 최소 WorkLog 수 (기본: 3)",
    )
    args = parser.parse_args()

    count = asyncio.run(export_real_samples(args.output, args.min_logs))
    if count == 0:
        logger.warning("추출된 샘플이 없습니다. DB에 PUBLISHED 회고가 있는지 확인하세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
