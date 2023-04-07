import asyncio
import tempfile

import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Mongo(Base):
    type = DataSourceType.mongo

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = [f"{k}={v}" for k, v in self.kwargs.items()]

    async def check(self):
        if not await aioshutil.which("mongodump"):
            raise RuntimeError("mongodump not found in PATH")
        return True

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        options = self.options
        options.append(f"-o={temp_dir}")
        proc = await asyncio.create_subprocess_exec(
            "mongodump",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"mongodump failed with {proc.returncode}: {stderr.decode()}")
        return temp_dir

    async def restore(self, file: str):
        raise NotImplementedError
