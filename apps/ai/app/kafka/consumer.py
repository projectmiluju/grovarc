import asyncio
import json
import logging
import uuid

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.kafka.schemas import WorkLogSavedEvent
from app.services.embedding_service import embed_work_log

logger = logging.getLogger(__name__)

TOPIC_WORK_LOG_SAVED = "work-log.saved"

_consumer: AIOKafkaConsumer | None = None
_consumer_task: asyncio.Task | None = None


async def _handle_work_log_saved(event: WorkLogSavedEvent) -> None:
    """work-log.saved 이벤트 처리 — 임베딩 생성"""
    logger.info(
        "WorkLog 수신 workLogId=%s userId=%s logDate=%s",
        event.workLogId,
        event.userId,
        event.logDate,
    )
    async with AsyncSessionLocal() as db:
        await embed_work_log(uuid.UUID(event.workLogId), db)


async def _consume_loop(consumer: AIOKafkaConsumer) -> None:
    try:
        async for msg in consumer:
            try:
                payload = json.loads(msg.value.decode("utf-8"))
                event = WorkLogSavedEvent(**payload)
                await _handle_work_log_saved(event)
            except Exception as e:
                logger.error("이벤트 처리 실패 offset=%s: %s", msg.offset, e)
    except asyncio.CancelledError:
        logger.info("Kafka Consumer 루프 종료")
    except Exception as e:
        logger.error("Kafka Consumer 예외: %s", e)
    finally:
        await consumer.stop()


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
async def _create_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        TOPIC_WORK_LOG_SAVED,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=None,  # raw bytes — _consume_loop에서 직접 파싱
    )
    await consumer.start()
    logger.info("Kafka Consumer 시작 topic=%s", TOPIC_WORK_LOG_SAVED)
    return consumer


async def start_consumer() -> None:
    global _consumer, _consumer_task
    try:
        _consumer = await _create_consumer()
        _consumer_task = asyncio.create_task(_consume_loop(_consumer))
    except KafkaConnectionError as e:
        logger.error("Kafka 연결 실패 — Consumer 시작 안 됨: %s", e)
    except Exception as e:
        logger.error("Kafka Consumer 초기화 실패: %s", e)


async def stop_consumer() -> None:
    global _consumer, _consumer_task
    if _consumer_task:
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
        _consumer_task = None
    if _consumer:
        await _consumer.stop()
        _consumer = None
    logger.info("Kafka Consumer 종료")
