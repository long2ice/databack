import abc

from pydantic import BaseModel

from databack.enums import StorageType


class Base:
    type: StorageType
    path: str
    options: BaseModel

    def __init__(self, options: BaseModel, path: str):
        self.options = options
        self.path = path

    @abc.abstractmethod
    async def check(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def upload(self, file: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def download(self, file: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, file: str):
        raise NotImplementedError
