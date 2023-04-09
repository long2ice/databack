from fastapi import APIRouter
from tortoise.expressions import RawSQL
from tortoise.functions import Count

from databack.models import DataSource, Storage, Task, TaskLog, RestoreLog

router = APIRouter()


@router.get("")
async def get_stats():
    datasource_count = await DataSource.all().count()
    storage_count = await Storage.all().count()
    task_count = await Task.all().count()
    task_log_count = await TaskLog.all().count()
    restore_log_count = await RestoreLog.all().count()
    task_logs = (
        await TaskLog.annotate(count=Count("id"), date=RawSQL("date(created_at)"))
        .group_by("status", "date")
        .values("status", "count", "date")
    )
    return {
        "datasource_count": datasource_count,
        "storage_count": storage_count,
        "task_count": task_count,
        "task_log_count": task_log_count,
        "restore_log_count": restore_log_count,
        "task_logs": task_logs,
    }
