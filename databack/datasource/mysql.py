import asyncio
import tempfile

import aiofiles
import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class MySQL(Base):
    type = DataSourceType.mysql

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = []
        for k, v in self.kwargs.items():
            if v is True:
                self.options.append(k)
            else:
                self.options.append(f"{k}={v}")

    async def check(self):
        if not await aioshutil.which("mysqlpump"):
            raise RuntimeError("mysqlpump not found in PATH")
        if not await aioshutil.which("mysql"):
            raise RuntimeError("mysql not found in PATH")
        return True

    @classmethod
    def _check_error(cls, std: bytes):
        if std and "[ERROR]" in std.decode():
            raise RuntimeError(f"mysqlpump failed: {std.decode()}")

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        options = self.options
        file = f"{temp_dir}/{self.filename}.sql"
        options.append(f"--result-file={file}")
        proc = await asyncio.create_subprocess_exec(
            "mysqlpump",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"mysqlpump failed with {proc.returncode}: {stderr.decode()}")
        self._check_error(stdout)
        self._check_error(stderr)
        return file

    async def restore(self, file: str):
        file = await self.get_restore(file)
        options = self.options
        proc = await asyncio.create_subprocess_exec(
            "mysql",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        async with aiofiles.open(file, "rb") as f:
            content = await f.read()
        stdout, stderr = await proc.communicate(content)
        if proc.returncode != 0:
            raise RuntimeError(f"mysql failed with {proc.returncode}: {stderr.decode()}")
        self._check_error(stdout)
        self._check_error(stderr)
