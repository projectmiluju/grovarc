import logging
import uuid

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.work_log import WorkLog, WorkLogEmbedding

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

_openai_client: AsyncOpenAI | None = None


def _get_openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def _build_embed_text(work_log: WorkLog) -> str:
    """임베딩할 텍스트 구성 — 제목 + 내용 + 날짜"""
    return f"[{work_log.log_date}] {work_log.title}\n{work_log.content}"


async def generate_embedding(text: str) -> list[float]:
    response = await _get_openai().embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
    )
    return response.data[0].embedding


async def embed_work_log(work_log_id: uuid.UUID, db: AsyncSession) -> None:
    """WorkLog를 조회해 임베딩 생성 후 저장"""
    work_log = await db.get(WorkLog, work_log_id)
    if work_log is None:
        logger.warning("WorkLog 없음 workLogId=%s", work_log_id)
        return

    text = _build_embed_text(work_log)
    vector = await generate_embedding(text)

    # upsert: 이미 있으면 업데이트
    result = await db.execute(
        select(WorkLogEmbedding).where(WorkLogEmbedding.work_log_id == work_log_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.embedding = vector
    else:
        db.add(WorkLogEmbedding(work_log_id=work_log_id, embedding=vector))

    await db.commit()
    logger.info("임베딩 저장 완료 workLogId=%s", work_log_id)
