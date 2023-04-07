import asyncio
import tempfile

import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Redis(Base):
    type = DataSourceType.redis

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = [f"{k}={v}" for k, v in self.kwargs.items()]

    async def check(self):
        if not await aioshutil.which("redis-cli"):
            raise RuntimeError("redis-cli not found in PATH")
        return True

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        options = self.options
        file = f"{temp_dir}/{self.filename}.rdb"
        options.append(f"--rdb={file}")
        proc = await asyncio.create_subprocess_exec(
            "redis-cli",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"redis-cli failed with {proc.returncode}: {stderr.decode()}")
        return file

    async def restore(self, file: str):
        raise NotImplementedError
