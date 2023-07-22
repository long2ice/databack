from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from databack.models import ActionLog
from databack.schema.request import Query

router = APIRouter()


class ActionLogResponse(pydantic_model_creator(ActionLog)):  # type: ignore
    admin_id: int


class ActionLogsResponse(BaseModel):
    total: int
    data: list[ActionLogResponse]


@router.get("", response_model=ActionLogsResponse)
async def get_actions_logs(
    admin_id: int | None = None,
    method: str | None = None,
    path: str | None = None,
    query: Query = Depends(Query),
):
    qs = ActionLog.all()
    if admin_id:
        qs = qs.filter(admin_id=admin_id)
    if method:
        qs = qs.filter(method=method)
    if path:
        qs = qs.filter(path__icontains=path)
    total = await qs.count()
    data = await qs.limit(query.limit).offset(query.offset).order_by(*query.orders)
    return {"total": total, "data": data}


@router.delete("/{pks}")
async def delete_action_logs(pks: str):
    id_list = [int(pk) for pk in pks.split(",")]
    await ActionLog.filter(id__in=id_list).delete()
