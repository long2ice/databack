from fastapi import APIRouter

from databack.routes import datasource, storage, task

router = APIRouter()
router.include_router(task.router, prefix="/task", tags=["Task"])
router.include_router(storage.router, prefix="/storage", tags=["Storage"])
router.include_router(datasource.router, prefix="/datasource", tags=["Datasource"])
