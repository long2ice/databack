import asyncio
import tempfile

import aiofiles
import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Redis(Base):
    type = DataSourceType.redis

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = kwargs.pop("password", None)
        for key, value in self.kwargs.items():
            if value:
                self.options.append(key)
                self.options.append(value)

    async def check(self):
        if not await aioshutil.which("redis-cli"):
            raise RuntimeError("redis-cli not found in PATH")
        if not await aioshutil.which("redis-dump-go"):
            raise RuntimeError("redis-dump-go not found in PATH")
        return True

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        options = self.options
        file = f"{temp_dir}/{self.filename}.resp"
        proc = await asyncio.create_subprocess_exec(
            "redis-dump-go",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"REDISDUMPGO_AUTH": self.password},
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"redis-cli failed with {proc.returncode}: {stderr.decode()}")
        async with aiofiles.open(file, "wb") as f:
            await f.write(stdout)
        return file

    async def restore(self, file: str):
        file = await self.get_restore(file)
        options = self.options
        options.append("--pipe")
        proc = await asyncio.create_subprocess_exec(
            "redis-cli",
            *options,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        async with aiofiles.open(file, "rb") as f:
            stdout, stderr = await proc.communicate(input=await f.read())
            if proc.returncode != 0:
                raise RuntimeError(f"redis-cli failed with {proc.returncode}: {stderr.decode()}")
