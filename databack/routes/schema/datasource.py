from fastapi import APIRouter

from databack.enums import DataSourceType
from databack.schemas import SSH, DatabaseConnection, Local

router = APIRouter()


@router.get("/{type}")
async def get_datasource_schema(type: DataSourceType):
    match type:
        case DataSourceType.local:
            return Local.schema()
        case DataSourceType.ssh:
            return SSH.schema()
        case DataSourceType.postgres, DataSourceType.mysql:
            return DatabaseConnection.schema()
        case _:
            raise ValueError("Unknown datasource type")
