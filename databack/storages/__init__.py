import abc

from databack.enums import StorageType


class Base:
    type: StorageType

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abc.abstractmethod
    async def upload(self, file: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def download(self, file: str):
        raise NotImplementedError
