import os
import tempfile

import asyncssh

from databack.datasource import Base
from databack.enums import DataSourceType


class SSH(Base):
    type = DataSourceType.ssh

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path = self.kwargs.get("path")
        self.host = self.kwargs.get("host")
        self.port = self.kwargs.get("port")
        self.username = self.kwargs.get("username")
        self.password = self.kwargs.get("password")
        self.private_key = self.kwargs.get("private_key")
        self.private_key_pass = self.kwargs.get("private_key_pass")

    async def check(self):
        async with self._get_connection() as conn:
            return await conn.run(f"ls {self.path}", check=True)

    def _get_connection(self):
        private_key = asyncssh.import_private_key(self.private_key, self.private_key_pass)
        return asyncssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            client_keys=private_key,
            known_hosts=None,
        )

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        async with self._get_connection() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(self.path, temp_dir, recurse=True)
        return os.path.join(temp_dir, os.path.basename(self.path))

    async def restore(self, file: str):
        async with self._get_connection() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(file, self.path, recurse=True)
