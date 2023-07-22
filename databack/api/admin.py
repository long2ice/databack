import i18n
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q

from databack import auth
from databack.auth import access_security, get_password_hash
from databack.depends import get_current_admin, superuser_required
from databack.models import Admin
from databack.schema.request import Query

router = APIRouter()


class GetAdminResponse(BaseModel):
    total: int
    data: pydantic_queryset_creator(  # type: ignore
        Admin,
    )


@router.get("", response_model=GetAdminResponse)
async def get_admin(
    search: str | None = None,
    is_active: bool | None = None,
    is_superuser: bool | None = None,
    query: Query = Depends(Query),
):
    qs = Admin.all()
    if search:
        qs = qs.filter(Q(nickname__icontains=search) | Q(email__icontains=search))
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if is_superuser is not None:
        qs = qs.filter(is_superuser=is_superuser)
    total = await qs.count()
    data = await qs.limit(query.limit).offset(query.offset).order_by(*query.orders)
    return {"total": total, "data": data}


@router.get("/me", response_model=pydantic_model_creator(Admin, exclude=("password",)))
async def get_me(
    credentials: JwtAuthorizationCredentials = Security(access_security),
):
    pk = credentials.subject["id"]
    admin = await Admin.get(pk=pk)
    return admin


@router.delete("/{pks}", dependencies=[Depends(superuser_required)])
async def delete_admins(pks: str):
    id_list = [int(pk) for pk in pks.split(",")]
    await Admin.filter(id__in=id_list).delete()


class CreateAdminBody(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    is_superuser: bool
    is_active: bool


@router.post("", dependencies=[Depends(superuser_required)])
async def create_admin(body: CreateAdminBody):
    try:
        await Admin.create(
            email=body.email,
            password=get_password_hash(body.password),
            nickname=body.nickname,
            is_superuser=body.is_superuser,
            is_active=body.is_active,
        )
    except IntegrityError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=i18n.t("admin_exists"))


class UpdateAdminBody(BaseModel):
    email: EmailStr | None
    password: str | None
    nickname: str | None
    is_superuser: bool | None
    is_active: bool | None


class ChangePasswordBody(BaseModel):
    old_password: str
    new_password: str


@router.patch("/password", status_code=HTTP_204_NO_CONTENT)
async def change_password(body: ChangePasswordBody, admin: Admin = Depends(get_current_admin)):
    if not auth.verify_password(body.old_password, admin.password):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=i18n.t("password_incorrect"))
    admin.password = get_password_hash(body.new_password)
    await admin.save(update_fields=["password"])


@router.patch("/{pk}", dependencies=[Depends(superuser_required)])
async def update_admin(pk: int, body: UpdateAdminBody):
    admin = await Admin.get(pk=pk)
    if body.email:
        admin.email = body.email
    if body.password:
        admin.password = get_password_hash(body.password)
    if body.nickname:
        admin.nickname = body.nickname
    if body.is_superuser is not None:
        admin.is_superuser = body.is_superuser
    if body.is_active is not None:
        admin.is_active = body.is_active
    await admin.save()
