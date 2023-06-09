from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED
from tortoise import timezone
from tortoise.contrib.pydantic import pydantic_model_creator

from databack.enums import DataSourceType, TaskStatus
from databack.models import RestoreLog
from databack.schema.request import Query
from databack.tasks import run_restore

router = APIRouter()


class GetRestoreResponse(BaseModel):
    class RestoreLogModel(pydantic_model_creator(RestoreLog)):  # type: ignore
        task_log_id: int

    total: int
    data: list[RestoreLogModel]


class RestoreRequest(BaseModel):
    options: dict
    task_log_id: int
    restore_type: DataSourceType


@router.get("", response_model=GetRestoreResponse)
async def get_restore_logs(
    limit: int = 10,
    offset: int = 0,
    status: TaskStatus | None = None,
    query: Query = Depends(Query),
):
    qs = RestoreLog.all()
    if status:
        qs = qs.filter(status=status)
    total = await qs.count()
    orders = query.orders if query.orders else ["-id"]
    data = await qs.order_by(*orders).limit(limit).offset(offset)
    return {"total": total, "data": data}


@router.post("", status_code=HTTP_201_CREATED)
async def restore_task_log(req: RestoreRequest):
    log = await RestoreLog.create(
        task_log_id=req.task_log_id,
        start_at=timezone.now(),
        options=req.options,
        restore_type=req.restore_type,
    )
    await run_restore.delay(log.pk)


@router.delete("/{pks}")
async def delete_restore_log(pks: str):
    id_list = [int(pk) for pk in pks.split(",")]
    await RestoreLog.filter(id__in=id_list).delete()
