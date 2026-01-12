from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import update

from ...db import database, profiles
from ...core.repositories.profile_repository import AbstractProfileRepository


def start_scheduler(repo: AbstractProfileRepository) -> AsyncIOScheduler:
    """
    Планировщик проверяет каждый день:
    - активен ли пользователь
    - прошли ли 14 дней с последней проверки BMI
    Если да — ставим needs_bmi_update = True
    """

    scheduler = AsyncIOScheduler()

    async def job_mark_bmi_needed():
        now = datetime.now(timezone.utc)
        two_weeks_ago = now - timedelta(days=14)

        query = (
            update(profiles)
            .where(
                profiles.c.is_active == True,
                profiles.c.last_bmi_check_at.isnot(None),
                profiles.c.last_bmi_check_at <= two_weeks_ago,
            )
            .values(needs_bmi_update=True)
        )

        await database.execute(query)
        print("[SCHEDULER] Отмечены профили, которым пора обновить BMI")

    scheduler.add_job(
        job_mark_bmi_needed,
        trigger=IntervalTrigger(days=1),  # проверка раз в день
        id="mark_bmi_needed",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler
