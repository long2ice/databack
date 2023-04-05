import os

import aiofiles.os
import aiofiles.ospath
import aioshutil
from pydantic import BaseModel

from databack.enums import StorageType
from databack.storages import Base


class LocalOptions(BaseModel):
    path: str


class Local(Base):
    type = StorageType.local
    options: LocalOptions

    async def check(self):
        return await aiofiles.ospath.exists(self.options.path)

    async def upload(self, file: str):
        await aioshutil.move(file, self.options.path)
        return os.path.join(self.options.path, os.path.basename(file))

    async def download(self, file: str):
        return os.path.join(self.options.path, file)

    async def delete(self, file: str):
        try:
            await aiofiles.os.remove(os.path.join(self.options.path, file))
        except FileNotFoundError:
            pass
