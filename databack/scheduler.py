import asyncio

from crontab import CronTab
from loguru import logger

from databack.constants import SCHEDULER_SLEEP_SECONDS
from databack.models import Task
from databack.tasks import run_task


class Scheduler:
    _wait_task = None
    _stop = False

    @classmethod
    async def start(cls):
        while not cls._stop:
            wait_seconds = []
            try:
                tasks = await Task.filter(enabled=True).only("id", "cron").all()
                for task in tasks:
                    cron = CronTab(task.cron)
                    next_time = cron.next(default_utc=False)
                    if next_time <= 0:
                        logger.info(f"Run task {task.name} now!")
                        await run_task.delay(task.pk)
                        wait_seconds.append(next_time)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            min_wait_seconds = min(wait_seconds) if wait_seconds else SCHEDULER_SLEEP_SECONDS
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
