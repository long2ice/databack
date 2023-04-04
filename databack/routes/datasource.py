import i18n
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from tortoise.exceptions import IntegrityError

from databack.discover import get_data_source
from databack.enums import DataSourceType
from databack.models import DataSource

router = APIRouter()


class GetDataSourceResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(DataSource)  # type: ignore


@router.get("", response_model=GetDataSourceResponse)
async def get_datasource(
    limit: int = 10, offset: int = 0, name: str = "", type: DataSourceType = None
):
    qs = DataSource.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if type:
        qs = qs.filter(type=type)
    total = await qs.count()
    data = (
        await qs.only("id", "name", "type", "created_at", "updated_at")
        .order_by("-id")
        .limit(limit)
        .offset(offset)
    )
    return {"total": total, "data": data}


@router.get("/{pk}", response_model=pydantic_model_creator(DataSource))  # type: ignore
async def get_datasource(pk: int):
    return await DataSource.get(id=pk)


class CreateDataSourceRequest(BaseModel):
    type: DataSourceType = Field(..., example=DataSourceType.mysql)
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
    data_source_cls = get_data_source(body.type)
    data_source_obj = data_source_cls(**body.options)
    if not await data_source_obj.check():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Data source check failed"
        )
    try:
        await DataSource.create(**body.dict())
    except IntegrityError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=i18n.t("data_source_exists", name=body.name),
        )


class UpdateDataSourceRequest(BaseModel):
    type: str | None
    name: str | None
    options: dict | None


@router.patch("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def update_datasource(pk: int, body: UpdateDataSourceRequest):
    data_source = await DataSource.get(id=pk)
    if body.options:
        body.options = {**data_source.options, **body.options}  # type: ignore
    data_source_cls = get_data_source(data_source.type)
    data_source_obj = data_source_cls(**data_source.options)  # type: ignore
    if not await data_source_obj.check():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Data source check failed"
        )
    try:
        await DataSource.filter(id=pk).update(**body.dict(exclude_none=True))
    except IntegrityError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=i18n.t("data_source_exists", name=body.name),
        )


@router.delete("/{pk}", status_code=HTTP_204_NO_CONTENT)
async def delete_datasource(pk: int):
    await DataSource.filter(id=pk).delete()
