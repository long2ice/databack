from aerich import Command
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
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
from databack.settings import TORTOISE_ORM, settings

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
    init_logging()
    aerich = Command(TORTOISE_ORM)
    await aerich.init()
    await aerich.upgrade()
