from databack.datasource import Base
from databack.enums import DataSourceType


class Local(Base):
    type = DataSourceType.local
