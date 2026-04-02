import asyncio
import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import select

from app.agents.retrospective.graph import run_retrospective_agent
from app.core.database import AsyncSessionLocal
from app.models.work_log import WorkLog
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_last_week_period() -> tuple[str, str]:
    """직전 월요일~일요일 기간 반환"""
    today = date.today()
    last_sunday = today - timedelta(days=today.weekday() + 1)
    last_monday = last_sunday - timedelta(days=6)
    return str(last_monday), str(last_sunday)


async def _fetch_active_user_ids() -> list[str]:
    """지난주에 WorkLog를 작성한 유저 ID 목록 조회"""
    period_from, period_to = _get_last_week_period()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WorkLog.user_id)
            .where(
                WorkLog.log_date >= date.fromisoformat(period_from),
                WorkLog.log_date <= date.fromisoformat(period_to),
            )
            .distinct()
        )
        return [str(row.user_id) for row in result.all()]


@celery_app.task(name="app.worker.tasks.run_retrospective_for_user", bind=True, max_retries=3)
def run_retrospective_for_user(self, user_id: str, period_from: str, period_to: str):
    """단일 유저 주간 회고 Agent 실행"""
    logger.info("주간 회고 시작 userId=%s %s~%s", user_id, period_from, period_to)
    try:
        asyncio.run(
            run_retrospective_agent(
                user_id=user_id,
                period_from=period_from,
                period_to=period_to,
            )
        )
        logger.info("주간 회고 완료 userId=%s", user_id)
    except Exception as exc:
        logger.error("주간 회고 실패 userId=%s: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(name="app.worker.tasks.run_weekly_retrospective_for_all_users")
def run_weekly_retrospective_for_all_users():
    """Beat가 호출하는 진입점 — 지난주 활성 유저 전체에 회고 태스크 발행"""
    period_from, period_to = _get_last_week_period()
    logger.info("주간 회고 스케줄러 실행 %s~%s", period_from, period_to)

    user_ids = asyncio.run(_fetch_active_user_ids())
    logger.info("대상 유저 수: %d", len(user_ids))

    for user_id in user_ids:
        run_retrospective_for_user.delay(user_id, period_from, period_to)

    return {"triggered": len(user_ids), "period_from": period_from, "period_to": period_to}
