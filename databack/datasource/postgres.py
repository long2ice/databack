from databack.datasource import Base
from databack.enums import DataSourceType


class Postgres(Base):
    type = DataSourceType.postgres
