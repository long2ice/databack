import i18n
from fastapi import APIRouter, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from tortoise import timezone

from databack.auth import access_security
from databack.auth import login as login_oauth
from databack.auth import oauth, refresh_security, verify_password
from databack.models import Admin
from databack.settings import settings

router = APIRouter()


class LoginBody(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login(
    body: LoginBody,
):
    admin = await Admin.filter(email=body.email).first()
    if not admin:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=i18n.t("login.user_not_found")
        )
    if not verify_password(body.password, admin.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=i18n.t("login.password_error")
        )
    admin.last_login_at = timezone.now()
    await admin.save(update_fields=["last_login_at"])
    subject = {
        "id": admin.pk,
    }
    return {
        "access_token": access_security.create_access_token(subject=subject),
        "refresh_token": refresh_security.create_refresh_token(subject=subject),
    }


@router.post("/refresh")
async def refresh(credentials: JwtAuthorizationCredentials = Security(refresh_security)):
    access_token = access_security.create_access_token(subject=credentials.subject)
    refresh_token = refresh_security.create_refresh_token(subject=credentials.subject)
    return {"access_token": access_token, "refresh_token": refresh_token}


class OauthResponse(BaseModel):
    type: str
    url: str


@router.get("/oauth", response_model=list[OauthResponse])
async def oauth_login(request: Request, redirect_uri: str):
    ret = []
    if settings.enable_github_oauth:
        client = oauth.github
        rv = await client.create_authorization_url(redirect_uri)
        await client.save_authorize_data(request, redirect_uri=redirect_uri, **rv)
        ret.append(
            {
                "type": "github",
                "url": rv["url"],
            }
        )
    if settings.enable_google_oauth:
        client = oauth.google
        rv = await client.create_authorization_url(redirect_uri)
        await client.save_authorize_data(request, redirect_uri=redirect_uri, **rv)
        ret.append(
            {
                "type": "google",
                "url": rv["url"],
            }
        )
    return ret


@router.post("/google")
async def auth_via_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]
    email = user["email"]
    nickname = user["name"]
    return await login_oauth(
        email,
        nickname,
    )


@router.post("/github")
async def auth_via_github(request: Request):
    token = await oauth.github.authorize_access_token(request)
    res = await oauth.github.get("/user", token=token)
    ret = res.json()
    email = ret["email"]
    nickname = ret["name"]
    return await login_oauth(
        email,
        nickname,
    )
