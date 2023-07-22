from enum import Enum


class StorageType(str, Enum):
    local = "local"
    ssh = "ssh"
    s3 = "s3"


class DataSourceType(str, Enum):
    clickhouse = "clickhouse"
    mysql = "mysql"
    postgres = "postgres"
    local = "local"
    ssh = "ssh"
    mongo = "mongo"
    redis = "redis"


class TaskStatus(str, Enum):
    success = "success"
    failed = "failed"
    running = "running"
