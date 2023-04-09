import asyncio

from crontab import CronTab
from loguru import logger
from tortoise import timezone

from databack.constants import SCHEDULER_SLEEP_SECONDS
from databack.models import Task
from databack.tasks import run_backup


class Scheduler:
    _wait_task = None
    _stop = False

    @classmethod
    async def start(cls):
        while not cls._stop:
            wait_seconds = []
            try:
                tasks = (
                    await Task.filter(enabled=True).only("id", "cron", "name", "next_run_at").all()
                )
                for task in tasks:
                    if not task.next_run_at:
                        await task.refresh_next_run_at()
                    if task.next_run_at <= timezone.now():
                        logger.info(f"Run task {task.name} now!")
                        await run_backup.delay(task.id)
                        await task.refresh_next_run_at()
                    cron = CronTab(task.cron)
                    seconds = cron.next(default_utc=True)
                    wait_seconds.append(seconds)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            min_wait_seconds = min(wait_seconds) if wait_seconds else SCHEDULER_SLEEP_SECONDS
            logger.info(f"Scheduler will sleep {int(min_wait_seconds)} seconds for next task")
            cls._wait_task = asyncio.create_task(asyncio.sleep(min_wait_seconds))
            try:
                await cls._wait_task
            except asyncio.CancelledError:
                pass

    @classmethod
    async def refresh(cls):
        if cls._wait_task:
            cls._wait_task.cancel()
            cls._wait_task = None

    @classmethod
    async def stop(cls):
        cls._stop = True
        await cls.refresh()
