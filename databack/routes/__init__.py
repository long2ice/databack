from fastapi import APIRouter, Depends

from databack.depends import set_i18n
from databack.routes import datasource, storage, task

router = APIRouter(dependencies=[Depends(set_i18n)])
router.include_router(task.router, prefix="/task", tags=["Task"])
router.include_router(storage.router, prefix="/storage", tags=["Storage"])
router.include_router(datasource.router, prefix="/datasource", tags=["Datasource"])
