from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from tortoise.contrib.pydantic import pydantic_queryset_creator

from databack.depends import refresh_scheduler
from databack.models import Task
from databack.tasks import run_task

router = APIRouter()


class GetTaskResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(Task)  # type: ignore


@router.get("", response_model=GetTaskResponse)
async def get_tasks(
    limit: int = 10, offset: int = 0, name: str = "", enabled: bool = None
):
    qs = Task.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if enabled is not None:
        qs = qs.filter(enabled=enabled)
    total = await qs.count()
    data = await qs.order_by("-id").limit(limit).offset(offset)
    return {"total": total, "data": data}


class CreateTaskRequest(BaseModel):
    name: str
    storage_id: int
    data_source_id: int
    compress: bool = True
    keep_num: int = 0
    enabled: bool = True
    cron: str = "* * * * *"


@router.post(
    "", status_code=HTTP_201_CREATED, dependencies=[Depends(refresh_scheduler)]
)
async def create_task(body: CreateTaskRequest):
    await Task.create(**body.dict())


@router.post("/{pk}/trigger", status_code=HTTP_201_CREATED)
async def trigger_task(pk: int):
    task = await Task.get(id=pk)
    if not task.enabled:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Task is disabled")
    await run_task.delay(pk)


class UpdateTaskRequest(BaseModel):
    name: str | None
    data_source_id: int | None
    keep_num: int | None
    enabled: bool | None
    cron: str | None


@router.patch(
    "/{pk}", status_code=HTTP_204_NO_CONTENT, dependencies=[Depends(refresh_scheduler)]
)
async def update_task(pk: int, body: UpdateTaskRequest):
    await Task.filter(id=pk).update(**body.dict(exclude_none=True))


@router.delete(
    "/{pk}", status_code=HTTP_204_NO_CONTENT, dependencies=[Depends(refresh_scheduler)]
)
async def delete_task(
    pk: int,
):
    await Task.filter(id=pk).delete()
