import asyncio
import os
import tempfile

import aiofiles
import aioshutil
from loguru import logger

from databack.datasource import Base
from databack.enums import DataSourceType


class MySQL(Base):
    type = DataSourceType.mysql
    sql_file = "dump.sql"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = [f"{k}={v}" for k, v in self.kwargs.items()]

    async def check(self):
        pass

    async def backup(self):
        if not await aioshutil.which("mysqlpump"):
            raise RuntimeError("mysqlpump not found in PATH")
        temp_dir = tempfile.mkdtemp()
        options = self.options
        options.append(f"--result-file={temp_dir}/{self.sql_file}")
        proc = await asyncio.create_subprocess_exec(
            "mysqlpump",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"mysqlpump failed with {proc.returncode}: {stderr.decode()}")
        if stdout:
            logger.info(stdout.decode())
        if stderr:
            logger.info(stderr.decode())
        return temp_dir

    async def restore(self, file: str):
        if not await aioshutil.which("mysql"):
            raise RuntimeError("mysql not found in PATH")
        temp_dir = await self.get_restore(file)
        options = self.options
        proc = await asyncio.create_subprocess_exec(
            "mysql",
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
            raise RuntimeError(f"mysql failed with {proc.returncode}: {stderr.decode()}")
        if stdout:
            logger.info(stdout.decode())
        if stderr:
            logger.info(stderr.decode())
