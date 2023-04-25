import os

import aiofiles.os
import aiofiles.ospath
import aioshutil

from databack.enums import StorageType
from databack.storage import Base


class Local(Base):
    type = StorageType.local

    async def check(self):
        return await aiofiles.ospath.exists(self.path)

    async def upload(self, file: str):
        await aioshutil.move(file, self.path)
        return os.path.join(self.path, os.path.basename(file))

    async def download(self, file: str):
        await aioshutil.copy(file, self.path)

    async def delete(self, file: str):
        try:
            await aiofiles.os.remove(os.path.join(self.path, file))
        except FileNotFoundError:
            pass
