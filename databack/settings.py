import sentry_sdk
from pydantic_settings import BaseSettings
from sentry_sdk.integrations.redis import RedisIntegration


class Settings(BaseSettings):
    DEBUG: bool = False
    SENTRY_DSN: str | None
    ENV: str = "production"
    DB_URL: str
    REDIS_URL: str
    WORKER: bool = True
    SECRET_KEY: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    @property
    def enable_github_oauth(self):
        return self.GITHUB_CLIENT_ID and self.GITHUB_CLIENT_SECRET

    @property
    def enable_google_oauth(self):
        return self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET

    class Config:
        env_file = ".env"


settings = Settings()
TORTOISE_ORM = {
    "apps": {
        "models": {
            "models": ["databack.models", "aerich.models"],
            "default_connection": "default",
        },
        "rearq": {
            "models": ["rearq.server.models"],
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
