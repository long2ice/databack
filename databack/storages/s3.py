import os

import aioboto3
import aiofiles
from pydantic import BaseModel

from databack.enums import StorageType
from databack.storages import Base


class S3Options(BaseModel):
    access_key_id: str
    secret_access_key: str
    region_name: str | None
    bucket_name: str
    endpoint_url: str


class S3(Base):
    type = StorageType.s3
    options: S3Options

    def __init__(
        self,
        options: S3Options,
        path: str = "",
    ):
        super().__init__(
            options=options,
            path=path,
        )
        self.endpoint_url = options.endpoint_url
        self.access_key_id = options.access_key_id
        self.secret_access_key = options.secret_access_key
        self.region_name = options.region_name
        self.bucket_name = options.bucket_name
        self.path = path
        self.session = aioboto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name,
        )

    async def check(self):
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as s3:
            return await s3.head_bucket(Bucket=self.bucket_name)

    async def upload(self, file: str):
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as s3:
            async with aiofiles.open(file, "rb") as f:
                key = os.path.join(self.path, os.path.basename(file))
                await s3.put_object(Key=key, Body=await f.read(), Bucket=self.bucket_name)
                return key

    async def download(self, file: str):
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as s3:
            await s3.download_file(Key=file, Filename=self.path, Bucket=self.bucket_name)

    async def delete(self, file: str):
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as s3:
            await s3.delete_objects(Delete={"Objects": [{"Key": file}]}, Bucket=self.bucket_name)
