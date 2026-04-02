import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_log import WorkLog, WorkLogEmbedding
from app.services.embedding_service import generate_embedding


@dataclass
class SimilarWorkLog:
    work_log_id: uuid.UUID
    title: str
    content: str
    log_date: date
    similarity: float


async def search_similar(
    query: str,
    user_id: uuid.UUID,
    db: AsyncSession,
    top_k: int = 5,
) -> list[SimilarWorkLog]:
    """쿼리와 유사한 WorkLog를 코사인 유사도로 검색"""
    query_vector = await generate_embedding(query)

    # pgvector 코사인 유사도 (<=> 연산자: 거리, 1 - distance = similarity)
    stmt = (
        select(
            WorkLog.id,
            WorkLog.title,
            WorkLog.content,
            WorkLog.log_date,
            (1 - WorkLogEmbedding.embedding.cosine_distance(query_vector)).label(
                "similarity"
            ),
        )
        .join(WorkLogEmbedding, WorkLog.id == WorkLogEmbedding.work_log_id)
        .where(WorkLog.user_id == user_id)
        .order_by(text("similarity DESC"))
        .limit(top_k)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        SimilarWorkLog(
            work_log_id=row.id,
            title=row.title,
            content=row.content,
            log_date=row.log_date,
            similarity=float(row.similarity),
        )
        for row in rows
    ]


async def build_rag_context(
    query: str,
    user_id: uuid.UUID,
    db: AsyncSession,
    top_k: int = 5,
) -> str:
    """유사 WorkLog를 LLM 프롬프트에 삽입할 컨텍스트 문자열로 반환"""
    similar = await search_similar(query, user_id, db, top_k)
    if not similar:
        return ""

    lines = ["## 관련 작업 로그\n"]
    for i, log in enumerate(similar, 1):
        lines.append(f"### {i}. [{log.log_date}] {log.title}")
        lines.append(log.content)
        lines.append("")

    return "\n".join(lines)
