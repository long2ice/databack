from databack.scheduler import Scheduler


async def refresh_scheduler():
    await Scheduler.refresh()
