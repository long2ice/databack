from enum import Enum


class StorgeType(str, Enum):
    local = "local"
    ssh = "ssh"
    s3 = "s3"


class DataSourceType(str, Enum):
    mysql = "mysql"
    postgres = "postgres"
    local = "local"
    ssh = "ssh"


class TaskStatus(str, Enum):
    success = "success"
    failed = "failed"
    running = "running"
