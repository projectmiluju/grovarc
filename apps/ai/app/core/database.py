from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ── PostgreSQL (SQLAlchemy async) ─────────────────────────────────────────────

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# ── MongoDB ───────────────────────────────────────────────────────────────────

_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _mongo_client


def get_mongo_db():
    return get_mongo_client()[settings.MONGODB_DB]


# ── Redis ─────────────────────────────────────────────────────────────────────

_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


# ── Lifecycle ─────────────────────────────────────────────────────────────────

async def connect_all() -> None:
    """앱 시작 시 DB 연결 초기화"""
    # PostgreSQL — 첫 쿼리 시 자동 연결 (pool_pre_ping으로 검증)
    get_mongo_client()
    get_redis()


async def disconnect_all() -> None:
    """앱 종료 시 DB 연결 해제"""
    global _mongo_client, _redis_client

    await engine.dispose()

    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None

    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
