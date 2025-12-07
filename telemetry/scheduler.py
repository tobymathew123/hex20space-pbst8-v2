# telemetry/scheduler.py
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone

from .nightly_job import run_nightly_job

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

_scheduler: BackgroundScheduler | None = None


def start_scheduler(hour: int = 2, minute: int = 0) -> BackgroundScheduler:
    """
    Start a background scheduler that runs run_nightly_job every day
    at the given hour/minute in IST.
    """
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(timezone=IST)
    scheduler.add_job(
        run_nightly_job,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="nightly_job",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    now = datetime.now(IST).isoformat()
    print(
        f"[{now}] Nightly scheduler started "
        f"(daily at {hour:02d}:{minute:02d} IST)."
    )
    return scheduler


def get_scheduler() -> BackgroundScheduler | None:
    return _scheduler
