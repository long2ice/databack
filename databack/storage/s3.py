import os

import aioboto3
import aiofiles
from botocore.client import Config
from pydantic import BaseModel

from databack.enums import StorageType
from databack.storage import Base


class S3Options(BaseModel):
    access_key_id: str
    secret_access_key: str
    region_name: str | None
    bucket_name: str
    endpoint_url: str
    access_style: str = "auto"


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
        self.access_style = options.access_style
        self.path = path
        self.session = aioboto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name,
        )
        self.s3_config = Config(s3={"addressing_style": self.access_style})

    def _get_client(self):
        return self.session.client("s3", endpoint_url=self.endpoint_url, config=self.s3_config)

    async def check(self):
        async with self._get_client() as s3:
            return await s3.head_bucket(Bucket=self.bucket_name)

    async def upload(self, file: str):
        async with self._get_client() as s3:
            async with aiofiles.open(file, "rb") as f:
                key = os.path.join(self.path, os.path.basename(file))
                await s3.put_object(Key=key, Body=await f.read(), Bucket=self.bucket_name)
                return key

    async def download(self, file: str):
        async with self._get_client() as s3:
            await s3.download_file(Key=file, Filename=self.path, Bucket=self.bucket_name)

    async def delete(self, file: str):
        async with self._get_client() as s3:
            await s3.delete_objects(Delete={"Objects": [{"Key": file}]}, Bucket=self.bucket_name)
