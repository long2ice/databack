from fastapi import APIRouter, Depends

from databack.api import datasource, restore, stat, storage, task, task_log
from databack.depends import set_i18n

router = APIRouter(dependencies=[Depends(set_i18n)])
router.include_router(task.router, prefix="/task", tags=["Task"])
router.include_router(storage.router, prefix="/storage", tags=["Storage"])
router.include_router(datasource.router, prefix="/datasource", tags=["Datasource"])
router.include_router(task_log.router, prefix="/task_log", tags=["TaskLog"])
router.include_router(stat.router, prefix="/stat", tags=["Stat"])
router.include_router(restore.router, prefix="/restore", tags=["Restore"])
