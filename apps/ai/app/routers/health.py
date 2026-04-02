from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import AsyncSessionLocal, get_mongo_db, get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/health/detail")
async def health_detail():
    """각 DB 연결 상태를 개별 확인"""
    result: dict[str, str] = {}

    # PostgreSQL
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        result["postgres"] = "ok"
    except Exception as e:
        result["postgres"] = f"error: {e}"

    # MongoDB
    try:
        db = get_mongo_db()
        await db.command("ping")
        result["mongodb"] = "ok"
    except Exception as e:
        result["mongodb"] = f"error: {e}"

    # Redis
    try:
        redis = get_redis()
        await redis.ping()
        result["redis"] = "ok"
    except Exception as e:
        result["redis"] = f"error: {e}"

    overall = "ok" if all(v == "ok" for v in result.values()) else "degraded"
    return {"status": overall, "dependencies": result}
