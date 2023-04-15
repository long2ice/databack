import abc
import os.path
import tempfile

import aioshutil
from tortoise import timezone

from databack.enums import DataSourceType


class Base:
    type: DataSourceType

    def __init__(self, **kwargs):
        other_options = kwargs.pop("other_options", None)
        self.options = other_options.split() if other_options else []
        self.kwargs = kwargs
        self.compress = self.kwargs.pop("compress", True)

    @property
    def filename(self):
        return f'{timezone.now().strftime("%Y-%m-%d_%H-%M-%S")}'

    async def check(self):
        return True

    @abc.abstractmethod
    async def backup(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def restore(self, file: str):
        raise NotImplementedError

    async def get_restore(self, file: str):
        if self.compress:
            temp_dir = tempfile.mkdtemp()
            await aioshutil.unpack_archive(file, temp_dir)
            ret = os.path.join(temp_dir, os.path.basename(file).replace(".tar.gz", ""))
            if os.path.isdir(file):
                await aioshutil.rmtree(file)
            else:
                os.remove(file)
            return ret
        return file

    async def get_backup(self):
        backup = await self.backup()
        if self.compress:
            ret = await aioshutil.make_archive(backup, "gztar", root_dir=os.path.dirname(backup))
            if os.path.isdir(backup):
                await aioshutil.rmtree(backup)
            else:
                os.remove(backup)
            return ret
        return backup
