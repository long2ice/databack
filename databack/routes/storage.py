from fastapi import APIRouter
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from tortoise.contrib.pydantic import pydantic_queryset_creator

from databack.models import Storage

router = APIRouter()


class GetStorageResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(Storage)  # type: ignore


@router.get("", response_model=GetStorageResponse)
async def get_storage(limit: int = 10, offset: int = 0):
    total = await Storage.all().count()
    storages = await Storage.all().order_by("-id").limit(limit).offset(offset)
    return {"total": total, "data": storages}


class CreateStorageRequest(BaseModel):
    type: str
    name: str
    connection: dict


@router.post("", status_code=HTTP_201_CREATED)
async def create_storage(body: CreateStorageRequest):
    await Storage.create(**body.dict())


class UpdateStorageRequest(BaseModel):
    type: str | None
    name: str | None
    connection: dict | None


@router.patch("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def update_storage(pk: int, body: UpdateStorageRequest):
    await Storage.filter(id=pk).update(**body.dict(exclude_none=True))


@router.delete("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def delete_storage(pk: int):
    await Storage.filter(id=pk).delete()
