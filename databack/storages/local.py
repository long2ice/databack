from databack.enums import StorgeType
from databack.storages import Base


class Local(Base):
    type = StorgeType.local
