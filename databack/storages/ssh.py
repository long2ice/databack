import asyncssh

from databack.enums import StorageType
from databack.storages import Base


class SSH(Base):
    type = StorageType.ssh
    path: str
    host: str
    port: int
    username: str
    password: str
    private_key: str
    private_key_pass: str

    def __init__(
        self,
        path: str,
        host: str,
        port: int,
        username: str,
        password: str,
        private_key: str,
        private_key_pass: str,
    ):
        super().__init__(
            path=path,
            host=host,
            port=port,
            username=username,
            password=password,
            private_key=private_key,
            private_key_pass=private_key_pass,
        )

    def _get_connection(self):
        return asyncssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            client_keys=[self.private_key],
            passphrase=self.private_key_pass,
        )

    async def upload(self, file: str):
        async with self._get_connection() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(file, self.path)

    async def download(self, file: str):
        async with self._get_connection() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(self.path, file)
