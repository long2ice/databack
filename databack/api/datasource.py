import i18n
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from tortoise.contrib.pydantic import pydantic_queryset_creator
from tortoise.exceptions import IntegrityError

from databack.discover import get_data_source
from databack.enums import DataSourceType
from databack.models import DataSource
from databack.schema.request import Query

router = APIRouter()


class GetDataSourceResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(DataSource, exclude=("options",))  # type: ignore


@router.get("", response_model=GetDataSourceResponse)
async def get_datasource(
    limit: int = 10,
    offset: int = 0,
    name: str = "",
    type: DataSourceType | None = None,
    query: Query = Depends(Query),
):
    qs = DataSource.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if type:
        qs = qs.filter(type=type)
    total = await qs.count()
    data = (
        await qs.only("id", "name", "type", "created_at", "updated_at")
        .order_by(*query.orders)
        .limit(limit)
        .offset(offset)
    )
    return {"total": total, "data": data}


@router.get("/basic")
async def get_datasource_basic():
    data = await DataSource.all().values("id", "name")
    return data


@router.get("/{pk}")
async def get_datasource_(pk: int):
    return await DataSource.get(id=pk)


class CreateDataSourceRequest(BaseModel):
    type: DataSourceType
    name: str
    options: dict


@router.post("", status_code=HTTP_201_CREATED)
async def create_datasource(body: CreateDataSourceRequest):
    data_source_cls = get_data_source(body.type)
    data_source_obj = data_source_cls(**body.options)
    try:
        await data_source_obj.check()
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
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
    data_source_cls = get_data_source(data_source.type)
    data_source_obj = data_source_cls(**data_source.options)  # type: ignore
    try:
        await data_source_obj.check()
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    try:
        await DataSource.filter(id=pk).update(**body.dict(exclude_none=True))
    except IntegrityError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=i18n.t("data_source_exists", name=body.name),
        )


@router.delete("/{pks}", status_code=HTTP_204_NO_CONTENT)
async def delete_datasource(pks: str):
    id_list = [int(pk) for pk in pks.split(",")]
    await DataSource.filter(id__in=id_list).delete()
