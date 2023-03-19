from databack.enums import StorgeType
from databack.storages import Base


class S3(Base):
    type = StorgeType.s3
