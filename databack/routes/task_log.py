from datetime import datetime

from fastapi import APIRouter

from databack.discover import get_storage
from databack.enums import TaskStatus
from databack.models import TaskLog

router = APIRouter()


@router.get("")
async def get_task_logs(
    limit: int = 10,
    offset: int = 0,
    task_id: int | None = None,
    status: str | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    is_deleted: bool | None = None,
):
    qs = TaskLog.all()
    if task_id:
        qs = qs.filter(task_id=task_id)
    if status:
        qs = qs.filter(status=status)
    if started_at:
        qs = qs.filter(started_at__gte=started_at)
    if ended_at:
        qs = qs.filter(ended_at__lte=ended_at)
    if is_deleted is not None:
        qs = qs.filter(is_deleted=is_deleted)
    total = await qs.count()
    data = await qs.order_by("-id").limit(limit).offset(offset)
    return {"total": total, "data": data}


@router.delete("/{pk}")
async def delete_task_log(pk: int):
    log = await TaskLog.get(id=pk).select_related("task__storage")
    storage = log.task.storage
    storage_cls = get_storage(storage.type)
    storage_obj = storage_cls(options=storage.options_parsed, path=storage.path)  # type: ignore
    if log.status == TaskStatus.success:
        await storage_obj.delete(log.path)
    await log.delete()
