from fastapi import APIRouter, Depends

from databack.api import action_log as action_log_router
from databack.api import (
    admin,
    auth,
    datasource,
    init,
    restore,
    stat,
    storage,
    task,
    task_log,
)
from databack.depends import action_log, auth_required, set_i18n

router = APIRouter(dependencies=[Depends(set_i18n)])
auth_router = APIRouter(dependencies=[Depends(auth_required), Depends(action_log)])

auth_router.include_router(task.router, prefix="/task", tags=["Task"])
auth_router.include_router(storage.router, prefix="/storage", tags=["Storage"])
auth_router.include_router(datasource.router, prefix="/datasource", tags=["Datasource"])
auth_router.include_router(task_log.router, prefix="/task_log", tags=["TaskLog"])
auth_router.include_router(stat.router, prefix="/stat", tags=["Stat"])
auth_router.include_router(restore.router, prefix="/restore", tags=["Restore"])
auth_router.include_router(
    action_log_router.router,
    prefix="/action_log",
    tags=["ActionLog"],
)
auth_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(init.router, prefix="/init", tags=["Init"])
router.include_router(auth_router)
