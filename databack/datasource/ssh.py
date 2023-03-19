from databack.datasource import Base
from databack.enums import DataSourceType


class SSH(Base):
    type = DataSourceType.ssh
