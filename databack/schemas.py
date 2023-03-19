from pydantic import BaseModel


class S3(BaseModel):
    access_key: str
    secret_key: str
    bucket: str
    endpoint: str


class Local(BaseModel):
    path: str


class SSH(BaseModel):
    host: str
    port: int
    user: str
    password: str | None
    private_key: str | None
    private_key_pass: str | None
    path: str


class DatabaseConnection(BaseModel):
    host: str
    port: int
    user: str
    password: str | None
    database: str
