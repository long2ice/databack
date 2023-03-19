from databack.enums import StorgeType
from databack.storages import Base


class SSH(Base):
    type = StorgeType.ssh
