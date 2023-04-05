import i18n
from crontab import CronTab
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from tortoise.validators import Validator


class CronValidator(Validator):
    def __call__(self, value: str):
        try:
            CronTab(value)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=i18n.t("cron_invalid", cron=value),
            )
