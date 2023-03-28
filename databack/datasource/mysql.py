import asyncio
import tempfile

import aiofiles
import aioshutil
from loguru import logger

from databack.datasource import Base
from databack.enums import DataSourceType


class MySQL(Base):
    type = DataSourceType.mysql

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = [f"{k}={v}" for k, v in self.kwargs.items()]

    async def check(self):
        if not await aioshutil.which("mysqlpump"):
            raise RuntimeError("mysqlpump not found in PATH")
        return True

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
        if stdout:
            logger.info(stdout.decode())
        if stderr:
            logger.info(stderr.decode())
        return file

    async def restore(self, file: str):
        if not await aioshutil.which("mysql"):
            raise RuntimeError("mysql not found in PATH")
        file = await self.get_restore(file)
        options = self.options
        proc = await asyncio.create_subprocess_exec(
            "mysql",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        async with aiofiles.open(file, "r") as f:
            content = await f.read()
        stdout, stderr = await proc.communicate(content.encode())
        if proc.returncode != 0:
            raise RuntimeError(f"mysql failed with {proc.returncode}: {stderr.decode()}")
        if stdout:
            logger.info(stdout.decode())
        if stderr:
            logger.info(stderr.decode())
