import abc
import os.path
import tempfile
from datetime import datetime

import aioshutil

from databack.enums import DataSourceType


class Base:
    type: DataSourceType

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.compress = self.kwargs.pop("compress", True)

    @property
    def filename(self):
        return f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'

    @abc.abstractmethod
    async def check(self):
        raise NotImplementedError

    async def backup(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def restore(self, file: str):
        raise NotImplementedError

    async def get_restore(self, file: str):
        if self.compress:
            temp_dir = tempfile.mkdtemp()
            await aioshutil.unpack_archive(file, temp_dir)
            return os.path.join(temp_dir, os.path.basename(file).replace(".tar.gz", ""))
        return file

    async def get_backup(self):
        backup = await self.backup()
        if self.compress:
            return await aioshutil.make_archive(backup, "gztar", root_dir=os.path.dirname(backup))
        return backup
