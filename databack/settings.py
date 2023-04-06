import sentry_sdk
from pydantic import BaseSettings
from sentry_sdk.integrations.redis import RedisIntegration


class Settings(BaseSettings):
    DEBUG: bool = False
    SENTRY_DSN: str | None = None
    ENV = "production"
    DB_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
TORTOISE_ORM = {
    "apps": {
        "models": {
            "models": ["databack.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "connections": {"default": settings.DB_URL},
}
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENV,
        integrations=[RedisIntegration()],
        traces_sample_rate=1.0,
    )
