import os

import aioshutil

from databack.enums import StorageType
from databack.storages import Base


class Local(Base):
    type = StorageType.local
    path: str

    def __init__(self, path: str):
        super().__init__(path=path)

    async def upload(self, file: str):
        await aioshutil.move(file, self.path)

    async def download(self, file: str):
        return os.path.join(self.path, file)
