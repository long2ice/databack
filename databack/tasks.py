import os.path
import tempfile
from datetime import timedelta

import aioshutil
from loguru import logger
from rearq import ReArq
from rearq.constants import JOB_TIMEOUT_UNLIMITED
from tortoise import Tortoise, timezone

from databack.discover import get_data_source, get_storage
from databack.enums import TaskStatus
from databack.models import RestoreLog, Task, TaskLog
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


@rearq.task(job_timeout=JOB_TIMEOUT_UNLIMITED)
async def run_backup(pk: int):
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
    storage_path = storage.path
    sub_path = task.sub_path
    storage_obj = storage_cls(
        options=storage.options_parsed, path=os.path.join(storage_path, sub_path)
    )
    try:
        backup = await data_source_obj.get_backup()
        task_log.size = await get_file_size(backup)
        file = await storage_obj.upload(backup)
        await storage_obj.delete(backup)
        task_log.status = TaskStatus.success
        task_log.path = file
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


@rearq.task(job_timeout=JOB_TIMEOUT_UNLIMITED)
async def run_restore(pk: int):
    restore_log = await RestoreLog.get(pk=pk).select_related("task_log__task__storage")
    task_log = restore_log.task_log  # type: TaskLog
    task = task_log.task
    if task_log.is_deleted or task_log.status != TaskStatus.success:
        return "TaskLog is deleted or not success"
    storage = task_log.task.storage
    data_source_cls = get_data_source(restore_log.restore_type)
    data_source_obj = data_source_cls(compress=task.compress, **restore_log.options)  # type: ignore
    storage_cls = get_storage(storage.type)
    local_path = tempfile.mkdtemp()
    try:
        local_file = os.path.join(local_path, os.path.basename(task_log.path))
        storage_obj = storage_cls(options=storage.options_parsed, path=local_file)
        await storage_obj.download(task_log.path)
        await data_source_obj.restore(local_file)
        await aioshutil.rmtree(local_path)
        restore_log.status = TaskStatus.success
    except Exception as e:
        logger.exception(e)
        restore_log.status = TaskStatus.failed
        restore_log.message = str(e)
    restore_log.end_at = timezone.now()
    await restore_log.save()
