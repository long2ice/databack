from fastapi import APIRouter

from databack.routes.schema import datasource, storage

router = APIRouter()
router.include_router(storage.router, prefix="/storage", tags=["Storage"])
router.include_router(datasource.router, prefix="/datasource", tags=["Datasource"])
