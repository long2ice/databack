import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Type

from databack import datasource, storage
from databack.enums import DataSourceType, StorageType


def _discover(module: ModuleType, t: Type[datasource.Base] | Type[storage.Base]):
    ret = {}
    for m in pkgutil.iter_modules(module.__path__):
        mod = importlib.import_module(f"{module.__name__}.{m.name}")
        for _, member in inspect.getmembers(mod, inspect.isclass):
            if issubclass(member, t) and member is not t:
                ret[member.type] = member
    return ret


_data_sources = _discover(datasource, datasource.Base)


def get_data_source(type_: DataSourceType) -> Type[datasource.Base]:
    return _data_sources[type_]


_storages = _discover(storage, storage.Base)


def get_storage(type_: StorageType) -> Type[storage.Base]:
    return _storages[type_]
