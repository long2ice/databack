from fastapi import APIRouter

from databack.enums import StorgeType
from databack.schemas import S3, SSH, Local

router = APIRouter()


@router.get("/{type}")
async def get_storage_schema(type: StorgeType):
    match type:
        case StorgeType.local:
            return Local.schema()
        case StorgeType.s3:
            return S3.schema()
        case StorgeType.ssh:
            return SSH.schema()
        case _:
            raise ValueError("Unknown storage type")
