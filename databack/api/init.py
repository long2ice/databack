import i18n
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from tortoise.exceptions import IntegrityError

from databack.auth import get_password_hash
from databack.models import Admin

router = APIRouter()


class InitBody(BaseModel):
    nickname: str
    email: EmailStr
    password: str


@router.post("/admin")
async def init_admin(
    body: InitBody,
):
    if await Admin.exists():
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=i18n.t("admin_inited"))
    try:
        await Admin.create(
            nickname=body.nickname,
            email=body.email,
            password=get_password_hash(body.password),
            is_superuser=True,
        )
    except IntegrityError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=i18n.t("admin_exists"))


@router.get("")
async def get_init():
    return {"inited": await Admin.exists()}
