import tempfile

import aiofiles.ospath
import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Local(Base):
    type = DataSourceType.local

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path = self.kwargs.get("path")

    async def check(self):
        return await aiofiles.ospath.exists(self.path)

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        destination = f"{temp_dir}/{self.filename}"
        await aioshutil.copytree(self.path, destination)
        return destination

    async def restore(self, file: str):
        file = await self.get_restore(file)
        await aioshutil.move(file, self.path)
