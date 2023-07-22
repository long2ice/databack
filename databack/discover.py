from typing import Type

from databack import datasource, storage
from databack.datasource import clickhouse, local, mongo, mysql, postgres, redis, ssh
from databack.enums import DataSourceType, StorageType
from databack.storage import local as local_storage
from databack.storage import s3
from databack.storage import ssh as ssh_storage


def get_data_source(type_: DataSourceType) -> Type[datasource.Base]:
    match type_:
        case DataSourceType.mysql:
            return mysql.MySQL
        case DataSourceType.postgres:
            return postgres.Postgres
        case DataSourceType.local:
            return local.Local
        case DataSourceType.ssh:
            return ssh.SSH
        case DataSourceType.mongo:
            return mongo.Mongo
        case DataSourceType.redis:
            return redis.Redis
        case DataSourceType.clickhouse:
            return clickhouse.ClickHouse


def get_storage(type_: StorageType) -> Type[storage.Base]:
    match type_:
        case StorageType.local:
            return local_storage.Local
        case StorageType.ssh:
            return ssh_storage.SSH
        case StorageType.s3:
            return s3.S3
