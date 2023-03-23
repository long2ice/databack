from tortoise import Model, fields

from databack.enums import DataSourceType, StorageType, TaskStatus


class BaseModel(Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class Storage(BaseModel):
    type = fields.CharEnumField(StorageType)
    name = fields.CharField(max_length=255, unique=True)
    options = fields.JSONField()


class DataSource(BaseModel):
    type = fields.CharEnumField(DataSourceType)
    name = fields.CharField(max_length=255, unique=True)
    options = fields.JSONField()


class Task(BaseModel):
    name = fields.CharField(max_length=255, unique=True)
    storage: fields.ForeignKeyRelation[Storage] = fields.ForeignKeyField("models.Storage")
    data_source: fields.ForeignKeyRelation[DataSource] = fields.ForeignKeyField("models.DataSource")
    compress = fields.BooleanField(default=True)
    keep_num = fields.IntField(default=3)
    enabled = fields.BooleanField(default=True)
    cron = fields.CharField(max_length=255)
    last_run_at = fields.DatetimeField(null=True)


class TaskLog(BaseModel):
    task: fields.ForeignKeyRelation[Task] = fields.ForeignKeyField("models.Task")
    status = fields.CharEnumField(TaskStatus)
    message = fields.TextField(null=True)
    start_at = fields.DatetimeField()
    end_at = fields.DatetimeField(null=True)


class Backup(BaseModel):
    task: fields.ForeignKeyRelation[Task] = fields.ForeignKeyField("models.Task")
    path = fields.CharField(max_length=255)
    size = fields.IntField()
