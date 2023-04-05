import asyncio
import tempfile

import aiofiles
import aioshutil
from loguru import logger

from databack.datasource import Base
from databack.enums import DataSourceType


class Postgres(Base):
    type = DataSourceType.postgres

    def __init__(self, password: str, backup_program: str, **kwargs):
        super().__init__(**kwargs)
        self.options = self.kwargs
        self.password = password
        self.backup_program = backup_program

    async def check(self):
        if not await aioshutil.which(self.backup_program):
            raise ValueError(f"{self.backup_program} not found in PATH")
        return True

    async def backup(self):
        options = [f"{k}={v}" for k, v in self.options.items()]
        temp_dir = tempfile.mkdtemp()
        file = f"{temp_dir}/{self.filename}.sql"
        options.append(f"-f {file}")
        proc = await asyncio.create_subprocess_exec(
            self.backup_program,
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"PGPASSWORD": self.password},
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"pg_dump failed with {proc.returncode}: {stderr.decode()}")
        return file

    async def restore(self, file: str):
        if not await aioshutil.which("pg_restore"):
            raise RuntimeError("pg_restore not found in PATH")
        file = await self.get_restore(file)
        options = self.options
        proc = await asyncio.create_subprocess_exec(
            "pg_restore",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        async with aiofiles.open(file, "r") as f:
            content = await f.read()
        stdout, stderr = await proc.communicate(content.encode())
        if proc.returncode != 0:
            raise RuntimeError(f"pg_restore failed with {proc.returncode}: {stderr.decode()}")
        if stdout:
            logger.info(stdout.decode())
        if stderr:
            logger.info(stderr.decode())
