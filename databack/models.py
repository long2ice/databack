from tortoise import Model, fields

from databack.enums import DataSourceType, StorageType, TaskStatus
from databack.storages.local import LocalOptions
from databack.storages.s3 import S3Options
from databack.storages.ssh import SSHOptions
from databack.validators import CronValidator


class BaseModel(Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class Storage(BaseModel):
    type = fields.CharEnumField(StorageType)
    name = fields.CharField(max_length=255, unique=True)
    options = fields.JSONField()

    @property
    def options_parsed(self):
        match self.type:
            case StorageType.local:
                return LocalOptions(**self.options)
            case StorageType.s3:
                return S3Options(**self.options)
            case StorageType.ssh:
                return SSHOptions(**self.options)
            case _:
                raise ValueError(f"Unknown storage type: {self.type}")


class DataSource(BaseModel):
    type = fields.CharEnumField(DataSourceType)
    name = fields.CharField(max_length=255, unique=True)
    options = fields.JSONField()


class Task(BaseModel):
    name = fields.CharField(max_length=255, unique=True)
    storage: fields.ForeignKeyRelation[Storage] = fields.ForeignKeyField("models.Storage")
    data_source: fields.ForeignKeyRelation[DataSource] = fields.ForeignKeyField("models.DataSource")
    compress = fields.BooleanField(default=True)
    keep_num = fields.IntField(default=0)
    keep_days = fields.IntField(default=0)
    enabled = fields.BooleanField(default=True)
    cron = fields.CharField(max_length=255, validators=[CronValidator()])


class TaskLog(BaseModel):
    task: fields.ForeignKeyRelation[Task] = fields.ForeignKeyField("models.Task")
    status = fields.CharEnumField(TaskStatus)
    path = fields.CharField(max_length=255, null=True)
    size = fields.IntField(null=True)
    message = fields.TextField(null=True)
    is_deleted = fields.BooleanField(default=False)
    start_at = fields.DatetimeField()
    end_at = fields.DatetimeField(null=True)
