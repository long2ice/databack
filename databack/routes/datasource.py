from fastapi import APIRouter
from pydantic import BaseModel, Field
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from tortoise.contrib.pydantic import pydantic_queryset_creator

from databack.models import DataSource

router = APIRouter()


class GetDataSourceResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(DataSource)  # type: ignore


@router.get("", response_model=GetDataSourceResponse)
async def get_datasource(limit: int = 10, offset: int = 0):
    total = await DataSource.all().count()
    data = await DataSource.all().order_by("-id").limit(limit).offset(offset)
    return {"total": total, "data": data}


class CreateDataSourceRequest(BaseModel):
    type: str = Field(..., example="mysql")
    name: str = Field(..., example="test")
    options: dict = Field(
        ...,
        example={
            "--host": "localhost",
            "--port": 3306,
            "--user": "root",
            "--password": "123456",
            "--include-databases": "test",
            "--set-gtid-purged": "OFF",
            "--add-drop-database": True,
        },
    )


@router.post("", status_code=HTTP_201_CREATED)
async def create_datasource(body: CreateDataSourceRequest):
    await DataSource.create(**body.dict())


class UpdateDataSourceRequest(BaseModel):
    type: str | None
    name: str | None
    options: dict | None


@router.patch("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def update_datasource(pk: int, body: UpdateDataSourceRequest):
    data_source = await DataSource.get(id=pk)
    if body.options:
        body.options = {**data_source.options, **body.options}  # type: ignore
    await DataSource.filter(id=pk).update(**body.dict(exclude_none=True))


@router.delete("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def delete_datasource(pk: int):
    await DataSource.filter(id=pk).delete()
