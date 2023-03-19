from databack.datasource import Base
from databack.enums import DataSourceType


class MySQL(Base):
    type = DataSourceType.mysql
