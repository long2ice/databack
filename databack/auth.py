from authlib.integrations.starlette_client import OAuth
from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer
from passlib.context import CryptContext
from tortoise import timezone

from databack.models import Admin
from databack.settings import settings

access_security = JwtAccessBearer(secret_key=settings.SECRET_KEY)
refresh_security = JwtRefreshBearer(
    secret_key=settings.SECRET_KEY,
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


oauth = OAuth()

if settings.enable_google_oauth:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
if settings.enable_github_oauth:
    oauth.register(
        name="github",
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )


async def login(email: str, nickname: str):
    admin = await Admin.filter(email=email).first()
    if not admin:
        admin = await Admin.create(nickname=nickname, email=email, password="", is_superuser=False)

    admin.last_login_at = timezone.now()
    admin.nickname = nickname
    await admin.save(update_fields=["last_login_at", "nickname"])
    subject = {
        "id": admin.pk,
    }
    return {
        "access_token": access_security.create_access_token(subject=subject),
        "refresh_token": refresh_security.create_refresh_token(subject=subject),
    }
