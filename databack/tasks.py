from rearq import ReArq
from tortoise import Tortoise

from databack.discover import get_data_source, get_storage
from databack.models import Task
from databack.settings import settings

rearq = ReArq(
    db_url=settings.DB_URL,
    redis_url=settings.REDIS_URL,
    keep_job_days=7,
    job_retry=0,
    raise_job_error=True,
)


@rearq.on_startup
async def startup():
    await Tortoise.init(
        db_url=settings.DB_URL,
        modules={"models": ["databack.models"]},
    )
    await Tortoise.generate_schemas()


@rearq.on_shutdown
async def shutdown():
    await Tortoise.close_connections()


@rearq.task()
async def run_task(pk: int):
    task = await Task.get(pk=pk).select_related("data_source", "storage")
    data_source = task.data_source
    storage = task.storage
    data_source_cls = get_data_source(data_source.type)
    data_source_obj = data_source_cls(**data_source.options)  # type: ignore
    storage_cls = get_storage(storage.type)
    storage_obj = storage_cls(**storage.options)  # type: ignore
    backup = await data_source_obj.get_backup()
    await storage_obj.upload(backup)
