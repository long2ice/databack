import i18n
from starlette.requests import Request

from databack.scheduler import Scheduler


async def refresh_scheduler():
    yield
    await Scheduler.refresh()


async def set_i18n(request: Request):
    lang = request.headers.get("Accept-Language", "en-US")
    lang = lang.split(",")[0]
    i18n.set("locale", lang)
