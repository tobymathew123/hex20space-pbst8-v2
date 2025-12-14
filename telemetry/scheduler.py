# telemetry/scheduler.py
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
from typing import Optional

from .nightly_job import run_nightly_job

# IST timezone (UTC +5:30)
IST = timezone(timedelta(hours=5, minutes=30))

_scheduler: Optional[BackgroundScheduler] = None


def start_scheduler(hour: int, minute: int) -> BackgroundScheduler:
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        return _scheduler

    scheduler = BackgroundScheduler(timezone=IST)

    scheduler.add_job(
        run_nightly_job,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="nightly_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
    _scheduler = scheduler

    now = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{now} IST] Nightly scheduler configured "
        f"(daily at {hour:02d}:{minute:02d} IST)"
    )

    return scheduler


def scheduler_status() -> dict:
    if _scheduler and _scheduler.running:
        job = _scheduler.get_job("nightly_job")
        return {
            "running": True,
            "next_run": job.next_run_time.astimezone(IST)
            if job and job.next_run_time
            else None,
        }

    return {"running": False, "next_run": None}
