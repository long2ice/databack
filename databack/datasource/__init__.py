import abc
import tempfile

import aioshutil

from databack.enums import DataSourceType


class Base:
    type: DataSourceType

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.compress = self.kwargs.pop("compress", True)

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
            return temp_dir
        return file

    async def get_backup(
        self,
    ):
        backup = await self.backup()
        if self.compress:
            temp_dir = tempfile.mkdtemp()
            return await aioshutil.make_archive(temp_dir, "gztar", backup)
        return backup
