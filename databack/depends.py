import json

import i18n
from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from databack.auth import access_security
from databack.constants import MASK_KEYS
from databack.models import ActionLog, Admin
from databack.scheduler import Scheduler


async def refresh_scheduler():
    yield
    await Scheduler.refresh()


async def set_i18n(request: Request):
    lang = request.headers.get("Accept-Language", "en-US")
    lang = lang.split(",")[0]
    i18n.set("locale", lang)


async def auth_required(credentials: JwtAuthorizationCredentials = Security(access_security)):
    return credentials.subject["id"]


async def get_current_admin(pk: int = Depends(auth_required)):
    admin = await Admin.get(pk=pk)
    if not admin.is_active:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=i18n.t("auth.not_active"))
    return admin


async def superuser_required(admin: Admin = Depends(get_current_admin)):
    if not admin.is_superuser:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=i18n.t("auth.not_superuser"))
    return admin


def get_client_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host  # type: ignore


async def action_log(
    request: Request, admin: Admin = Depends(get_current_admin), ip=Depends(get_client_ip)
):
    method = request.method
    if method in ["POST", "PUT", "PATCH", "DELETE"]:
        path = request.url.path
        content = {}
        if method != "DELETE":
            body = await request.body()
            if body:
                content = json.loads(body)
        else:
            content = dict(request.query_params)
        for key in content:
            if key in MASK_KEYS:
                content[key] = "******"
        await ActionLog.create(
            admin=admin,
            ip=ip,
            content=content,
            path=path,
            method=method,
        )
