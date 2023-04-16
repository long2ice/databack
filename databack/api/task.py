import i18n
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from tortoise.contrib.pydantic import pydantic_model_creator

from databack import tasks
from databack.depends import refresh_scheduler
from databack.models import Task
from databack.schema.request import Query

router = APIRouter()


class GetTaskResponse(BaseModel):
    class Task(pydantic_model_creator(Task)):  # type: ignore
        storage_name: str
        data_source_name: str
        data_source_id: int
        storage_id: int

    total: int
    data: list[Task]


@router.get("", response_model=GetTaskResponse)
async def get_tasks(
    limit: int = 10,
    offset: int = 0,
    name: str = "",
    data_source_id: int | None = None,
    storage_id: int | None = None,
    compress: bool | None = None,
    enabled: bool | None = None,
    query: Query = Depends(Query),
):
    qs = Task.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if data_source_id:
        qs = qs.filter(data_source_id=data_source_id)
    if storage_id:
        qs = qs.filter(storage_id=storage_id)
    if compress is not None:
        qs = qs.filter(compress=compress)
    if enabled is not None:
        qs = qs.filter(enabled=enabled)
    total = await qs.count()
    data = (
        await qs.order_by(*query.orders)
        .limit(limit)
        .offset(offset)
        .values(
            "id",
            "name",
            "enabled",
            "cron",
            "created_at",
            "updated_at",
            "keep_num",
            "keep_days",
            "compress",
            "data_source_id",
            "storage_id",
            "sub_path",
            "next_run_at",
            storage_name="storage__name",
            data_source_name="data_source__name",
        )
    )
    return {"total": total, "data": data}


class CreateTaskRequest(BaseModel):
    name: str
    storage_id: int
    data_source_id: int
    compress: bool = True
    keep_num: int = 0
    keep_days: int = 0
    enabled: bool = True
    sub_path: str = ""
    cron: str = Field("", example="0 0 * * *")


@router.post("", status_code=HTTP_201_CREATED, dependencies=[Depends(refresh_scheduler)])
async def create_task(body: CreateTaskRequest):
    await Task.create(**body.dict())


@router.post("/{pk}/run", status_code=HTTP_201_CREATED)
async def run_task(pk: int):
    task = await Task.get(id=pk)
    if not task.enabled:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=i18n.t("task_disabled", name=task.name),
        )
    await tasks.run_backup.delay(pk)


class UpdateTaskRequest(BaseModel):
    name: str | None
    data_source_id: int | None
    storage_id: int | None
    keep_num: int | None
    keep_days: int | None
    sub_path: str | None
    enabled: bool | None
    cron: str | None


@router.patch("/{pk}", status_code=HTTP_204_NO_CONTENT, dependencies=[Depends(refresh_scheduler)])
async def update_task(pk: int, body: UpdateTaskRequest):
    await Task.filter(id=pk).update(**body.dict(exclude_none=True))


@router.delete("/{pks}", status_code=HTTP_204_NO_CONTENT, dependencies=[Depends(refresh_scheduler)])
async def delete_task(
    pks: str,
):
    ids = [int(pk) for pk in pks.split(",")]
    await Task.filter(id__in=ids).delete()
