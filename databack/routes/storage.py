from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator

from databack import discover
from databack.enums import StorageType
from databack.models import Storage
from databack.storages import local, s3, ssh

router = APIRouter()


class GetStorageResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(Storage)  # type: ignore


@router.get("", response_model=GetStorageResponse)
async def get_storages(
    limit: int = 10, offset: int = 0, name: str = "", type: StorageType = None
):
    qs = Storage.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if type:
        qs = qs.filter(type=type)
    total = await qs.count()
    storages = (
        await qs.only("id", "name", "type", "created_at", "updated_at")
        .order_by("-id")
        .limit(limit)
        .offset(offset)
    )
    return {"total": total, "data": storages}


@router.get("/{pk}", response_model=pydantic_model_creator(Storage))  # type: ignore
async def get_storage(pk: int):
    return await Storage.get(id=pk)


class CreateStorageRequest(BaseModel):
    type: StorageType = Field(..., example="local")
    name: str = Field(..., example="local")
    options: s3.S3Options | ssh.SSHOptions | local.LocalOptions = Field(
        ..., example={"path": "/tmp"}
    )


@router.post("", status_code=HTTP_201_CREATED)
async def create_storage(body: CreateStorageRequest):
    storage_cls = discover.get_storage(body.type)
    storage_obj = storage_cls(body.options)
    if not await storage_obj.check():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Storage check failed"
        )
    await Storage.create(**body.dict())


class UpdateStorageRequest(BaseModel):
    type: StorageType | None
    name: str | None
    options: s3.S3Options | ssh.SSHOptions | local.LocalOptions | None


@router.patch("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def update_storage(pk: int, body: UpdateStorageRequest):
    storage = await Storage.get(id=pk)
    if body.options:
        body.options = {**storage.options, **body.options.dict()}  # type: ignore
    storage_cls = discover.get_storage(storage.type)
    storage_obj = storage_cls(storage.options_parsed)
    if not await storage_obj.check():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Storage check failed"
        )
    await Storage.filter(id=pk).update(**body.dict(exclude_none=True))


@router.delete("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def delete_storage(pk: int):
    await Storage.filter(id=pk).delete()
