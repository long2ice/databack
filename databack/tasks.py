from datetime import timedelta

from loguru import logger
from rearq import ReArq
from tortoise import Tortoise, timezone

from databack.discover import get_data_source, get_storage
from databack.enums import TaskStatus
from databack.models import Task, TaskLog
from databack.settings import settings
from databack.utils import get_file_size

rearq = ReArq(
    db_url=settings.DB_URL,
    redis_url=settings.REDIS_URL,
    keep_job_days=7,
    job_retry=0,
    raise_job_error=True,
    generate_schemas=True,
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
    started_at = timezone.now()
    task = await Task.get(pk=pk, enabled=True).select_related("data_source", "storage")
    task_log = await TaskLog.create(
        task=task,
        status=TaskStatus.running,
        start_at=started_at,
    )
    data_source = task.data_source
    storage = task.storage
    data_source_cls = get_data_source(data_source.type)
    data_source_obj = data_source_cls(compress=task.compress, **data_source.options)  # type: ignore
    storage_cls = get_storage(storage.type)
    storage_obj = storage_cls(storage.options_parsed)  # type: ignore
    try:
        backup = await data_source_obj.get_backup()
        await storage_obj.upload(backup)
        await storage_obj.delete(backup)
        task_log.status = TaskStatus.success
        task_log.path = backup
        task_log.size = await get_file_size(backup)
        task_log.end_at = timezone.now()
    except Exception as e:
        logger.exception(e)
        task_log.status = TaskStatus.failed
        task_log.message = str(e)
    await task_log.save()
    if task_log.status == TaskStatus.success:
        qs = TaskLog.filter(task=task, status=TaskStatus.success, is_deleted=False)
        total_success = await qs.count()
        if 0 < task.keep_num < total_success:
            if task.keep_days > 0:
                qs = qs.filter(end_at__lte=timezone.now() - timedelta(days=task.keep_days))
            task_logs_to_be_deleted = await qs.order_by("id").limit(total_success - task.keep_num)
            for task_log_to_be_deleted in task_logs_to_be_deleted:
                await storage_obj.delete(task_log_to_be_deleted.path)
                task_log_to_be_deleted.is_deleted = True
                await task_log_to_be_deleted.save(update_fields=["is_deleted"])
    return task_log.pk
