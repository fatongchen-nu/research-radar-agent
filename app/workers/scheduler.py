from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    return scheduler


def start_scheduler() -> AsyncIOScheduler | None:
    if not settings.scheduler_enabled:
        return None
    scheduler = build_scheduler()
    scheduler.start()
    return scheduler
