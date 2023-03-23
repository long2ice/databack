from fastapi import APIRouter
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from tortoise.contrib.pydantic import pydantic_queryset_creator

from databack.models import Task

router = APIRouter()


class GetTaskResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(Task)  # type: ignore


@router.get("", response_model=GetTaskResponse)
async def get_task(limit: int = 10, offset: int = 0):
    total = await Task.all().count()
    data = await Task.all().order_by("-id").limit(limit).offset(offset)
    return {"total": total, "data": data}


class CreateTaskRequest(BaseModel):
    name: str
    storage_id: int
    data_source_id: int
    compress: bool = True
    keep_num: int = 0
    enabled: bool = True
    cron: str = "* * * * *"


@router.post("", status_code=HTTP_201_CREATED)
async def create_task(body: CreateTaskRequest):
    await Task.create(**body.dict())


class UpdateTaskRequest(BaseModel):
    name: str | None
    storage_id: int | None
    data_source_id: int | None
    compress: bool | None
    keep_num: int | None
    enabled: bool | None
    cron: str | None


@router.patch("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def update_task(pk: int, body: UpdateTaskRequest):
    await Task.filter(id=pk).update(**body.dict(exclude_none=True))


@router.delete("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def delete_task(pk: int):
    await Task.filter(id=pk).delete()
