import asyncio
from contextlib import asynccontextmanager

from aerich import Command
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from rearq.server.app import app as rearq_server
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist

from databack import locales
from databack.api import router
from databack.exceptions import (
    custom_http_exception_handler,
    exception_handler,
    not_exists_exception_handler,
    validation_exception_handler,
)
from databack.log import init_logging
from databack.scheduler import Scheduler
from databack.settings import TORTOISE_ORM, settings
from databack.static import SPAStaticFiles
from databack.tasks import rearq


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_logging()
    locales.init()
    aerich = Command(TORTOISE_ORM)
    await aerich.init()
    await aerich.upgrade(True)
    asyncio.ensure_future(Scheduler.start())
    if settings.WORKER:
        await rearq_server.start_worker()
    yield
    await Scheduler.stop()


if settings.DEBUG:
    app = FastAPI(
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
else:
    app = FastAPI(
        debug=settings.DEBUG,
        lifespan=lifespan,
        redoc_url=None,
        docs_url=None,
    )
app.include_router(router, prefix="/api")
app.mount("/rearq", rearq_server)
app.mount("/", SPAStaticFiles(directory="static", html=True), name="static")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

rearq_server.set_rearq(rearq)
register_tortoise(
    app,
    config=TORTOISE_ORM,
)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(DoesNotExist, not_exists_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, exception_handler)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
