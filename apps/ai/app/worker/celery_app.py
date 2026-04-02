from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "grovarc_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    # Beat 스케줄: 매주 일요일 23:00 KST (= 14:00 UTC)
    beat_schedule={
        "weekly-retrospective": {
            "task": "app.worker.tasks.run_weekly_retrospective_for_all_users",
            "schedule": crontab(hour=14, minute=0, day_of_week="sunday"),
        },
    },
)
