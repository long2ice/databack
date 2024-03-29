import os
import tempfile

import aioshutil

from databack.datasource import Base
from databack.enums import DataSourceType


class Local(Base):
    type = DataSourceType.local

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path = self.kwargs.get("path")

    async def check(self):
        return os.path.exists(self.path)

    async def backup(self):
        temp_dir = tempfile.mkdtemp()
        if os.path.isdir(self.path):
            destination = os.path.join(temp_dir, self.filename, os.path.basename(self.path))
            await aioshutil.copytree(self.path, destination)
        else:
            destination = os.path.join(temp_dir, self.filename)
            os.makedirs(destination, exist_ok=True)
            await aioshutil.copy(self.path, destination)
            return destination

    async def restore(self, file: str):
        file = await self.get_restore(file)
        await aioshutil.move(file, self.path)
