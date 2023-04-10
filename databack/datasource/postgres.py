import asyncio
import tempfile

import aiofiles
import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Postgres(Base):
    type = DataSourceType.postgres

    def __init__(self, password: str, backup_program: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.options = []
        for k, v in self.kwargs.items():
            if v is True:
                self.options.append(k)
            else:
                self.options.append(f"{k}={v}")
        self.password = password
        self.backup_program = backup_program

    async def check(self):
        if not await aioshutil.which(self.backup_program):
            raise ValueError(f"{self.backup_program} not found in PATH")
        if not await aioshutil.which("psql"):
            raise RuntimeError("psql not found in PATH")
        return True

    def _check_error(self, std):
        if std and "error:" in std.decode():
            raise RuntimeError(f"mysqlpump failed: {std.decode()}")

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        file = f"{temp_dir}/{self.filename}.sql"
        options = self.options
        options.append(f"--file={file}")
        proc = await asyncio.create_subprocess_exec(
            self.backup_program,
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"PGPASSWORD": self.password},
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(
                f"{self.backup_program} failed with {proc.returncode}: {stderr.decode()}"
            )
        self._check_error(stdout)
        self._check_error(stderr)
        return file

    async def restore(self, file: str):
        file = await self.get_restore(file)
        options = self.options
        options.append(f"--file={file}")
        proc = await asyncio.create_subprocess_exec(
            "/usr/local/opt/postgresql@15/bin/psql",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            env={"PGPASSWORD": self.password},
        )
        async with aiofiles.open(file, "r") as f:
            content = await f.read()
        stdout, stderr = await proc.communicate(content.encode())
        if proc.returncode != 0:
            raise RuntimeError(f"pg_restore failed with {proc.returncode}: {stderr.decode()}")
        self._check_error(stdout)
        self._check_error(stderr)
