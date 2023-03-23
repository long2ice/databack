import asyncio
import os
import tempfile

import aiofiles
import aioshutil
from loguru import logger

from databack.datasource import Base
from databack.enums import DataSourceType


class Postgres(Base):
    type = DataSourceType.postgres
    sql_file = "dump.sql"

    def __init__(self, password: str, **kwargs):
        super().__init__(**kwargs)
        self.options = self.kwargs
        self.password = password

    async def check(self):
        pass

    async def backup(self):
        if not await aioshutil.which("pg_dump"):
            raise ValueError("pg_dump not found in PATH")
        options = [f"{k}={v}" for k, v in self.options.items()]
        temp_dir = tempfile.mkdtemp()
        options.append(f"-f {temp_dir}/{self.sql_file}")
        proc = await asyncio.create_subprocess_exec(
            "pg_dump",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"PGPASSWORD": self.password},
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"pg_dump failed with {proc.returncode}: {stderr.decode()}")
        return temp_dir

    async def restore(self, file: str):
        if not await aioshutil.which("pg_restore"):
            raise RuntimeError("pg_restore not found in PATH")
        temp_dir = await self.get_restore(file)
        options = self.options
        proc = await asyncio.create_subprocess_exec(
            "pg_restore",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        sql_file = os.path.join(temp_dir, self.sql_file)
        async with aiofiles.open(sql_file, "r") as f:
            content = await f.read()
        stdout, stderr = await proc.communicate(content.encode())
        if proc.returncode != 0:
            raise RuntimeError(f"pg_restore failed with {proc.returncode}: {stderr.decode()}")
        if stdout:
            logger.info(stdout.decode())
        if stderr:
            logger.info(stderr.decode())
