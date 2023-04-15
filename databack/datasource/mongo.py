import asyncio
import os
import tempfile

import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Mongo(Base):
    type = DataSourceType.mongo

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in self.kwargs.items():
            self.options.append(key)
            self.options.append(value)

    async def check(self):
        if not await aioshutil.which("mongodump"):
            raise RuntimeError("mongodump not found in PATH")
        if not await aioshutil.which("mongorestore"):
            raise RuntimeError("mongorestore not found in PATH")
        return True

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        options = self.options
        file = os.path.join(temp_dir, f"{self.filename}.gz")
        options.append(f"--archive={file}")
        options.append("--gzip")
        proc = await asyncio.create_subprocess_exec(
            "mongodump",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"mongodump failed with {proc.returncode}: {stderr.decode()}")
        return file

    async def restore(self, file: str):
        file = await self.get_restore(file)
        options = self.options
        options.append(f"--archive={file}")
        options.append("--gzip")
        proc = await asyncio.create_subprocess_exec(
            "mongorestore",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"mongorestore failed with {proc.returncode}: {stderr.decode()}")
