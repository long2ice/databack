import aioboto3
import aiofiles

from databack.enums import StorageType
from databack.storages import Base


class S3(Base):
    type = StorageType.s3
    access_key_id: str
    secret_access_key: str
    region_name: str
    bucket_name: str
    endpoint_url: str
    path: str

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region_name: str,
        bucket_name: str,
        endpoint_url: str,
        path: str,
    ):
        super().__init__(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region_name=region_name,
            bucket_name=bucket_name,
            endpoint_url=endpoint_url,
            path=path,
        )
        self.session = aioboto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name,
        )

    async def upload(self, file: str):
        async with self.session.resource("s3", endpoint_url=self.endpoint_url) as s3:
            async with aiofiles.open(file, "rb") as f:
                await s3.Bucket(self.bucket_name).put_object(Key=file, Body=f)

    async def download(self, file: str):
        async with self.session.resource("s3", endpoint_url=self.endpoint_url) as s3:
            await s3.Bucket(self.bucket_name).download_file(file, self.path)
