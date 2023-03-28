import asyncio

from aerich import Command
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from rearq.server.app import app as rearq_server
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist

from databack.exceptions import (
    custom_http_exception_handler,
    exception_handler,
    not_exists_exception_handler,
    validation_exception_handler,
)
from databack.log import init_logging
from databack.routes import router
from databack.scheduler import Scheduler
from databack.settings import TORTOISE_ORM, settings
from databack.tasks import rearq

if settings.DEBUG:
    app = FastAPI(
        debug=settings.DEBUG,
    )
else:
    app = FastAPI(
        debug=settings.DEBUG,
        redoc_url=None,
        docs_url=None,
    )
app.include_router(router)
app.mount("/rearq", rearq_server)
rearq_server.set_rearq(rearq)
register_tortoise(
    app,
    config=TORTOISE_ORM,
)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(DoesNotExist, not_exists_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, exception_handler)


@app.on_event("startup")
async def startup():
    await rearq.init()
    init_logging()
    aerich = Command(TORTOISE_ORM)
    await aerich.init()
    await aerich.upgrade()
    asyncio.ensure_future(Scheduler.start())


@app.on_event("shutdown")
async def shutdown():
    await Scheduler.stop()
