import os

import asyncssh
from pydantic import BaseModel

from databack.enums import StorageType
from databack.storage import Base


class SSHOptions(BaseModel):
    host: str
    port: int
    username: str
    password: str
    private_key: str
    private_key_pass: str


class SSH(Base):
    type = StorageType.ssh
    options: SSHOptions

    def __init__(
        self,
        options: SSHOptions,
        path: str = "",
    ):
        super().__init__(
            options=options,
            path=path,
        )
        self.host = options.host
        self.port = options.port
        self.username = options.username
        self.password = options.password
        self.private_key = options.private_key
        self.private_key_pass = options.private_key_pass

    async def check(self):
        async with self._get_connection() as conn:
            return await conn.run("ls", self.path, check=True)

    def _get_connection(self):
        private_key = asyncssh.import_private_key(self.private_key, self.private_key_pass)
        return asyncssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            known_hosts=None,
            client_keys=private_key,
        )

    async def upload(self, file: str):
        async with self._get_connection() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(file, self.path)
                return os.path.join(self.path, os.path.basename(file))

    async def download(self, file: str):
        async with self._get_connection() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(file, self.path)

    async def delete(self, file: str):
        async with self._get_connection() as conn:
            await conn.run("rm", os.path.join(self.path, file))
