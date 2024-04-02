from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Any

from hyper_clipboard.const.const_values import AppLogger
from hyper_clipboard.const.observable_objects import Observable, ObjectLog
import frozendict


class StorageSettings(ABC):
    storage_type:str=""
    default_data:dict[str,Any]={}


@dataclass
class KeyObject:
    key: str
    default_value: Any

@dataclass
class StorageIODataPath:
    storage_type:str
    key:str


@dataclass
class StorageIOWriteData:
    path:StorageIODataPath
    value:Any

class StorageIOBase(ABC):
    _memory_cache: dict[str, Any]={}
    def __init__(self,storage_settings:StorageSettings):
        self.__storage_settings=storage_settings
    @abstractmethod
    async def read_all(self) -> dict[str, Any]:
        pass
    @abstractmethod
    def write(self,key:object,value:Any):
        pass
    def _initialize(self):
        self._memory_cache=asyncio.run(self.read_all())
        for key in self.__storage_settings.default_data.keys():
            if key not in self._memory_cache.keys():
                AppLogger.info(f"key:{key} not found in storage, writing default value")
                self._write_sync_cache(key,self.__storage_settings.default_data[key])

    @abstractmethod
    def _write_sync_cache(self,key:object,value:Any):
        pass
    @property
    def storage_type(self):
        return self.__storage_settings.storage_type

class StorageIO(StorageIOBase):
    def __init__(self,storage_settings:StorageSettings):
        super().__init__(storage_settings)
    @abstractmethod
    async def read_all(self) -> dict[str, Any]:
        pass
    @abstractmethod
    async def write(self,key:str,value:Any):
        pass
    def _write_sync_cache(self,key:str,value:Any):
        self._memory_cache[key]=value
        asyncio.run(self.write(key,value))

class StorageIOCombine:
    __storage_instance_dict:dict[str,StorageIO]={}
    __memory_cache: dict[str, dict[str, Any]]={}
    def __init__(self,storage_list:list[StorageIO]):
        for storage in storage_list:
            self.__storage_instance_dict[storage.storage_type]=storage
            storage._initialize()
            # dictがmutableなのを利用している
            self.__memory_cache[storage.storage_type]=storage._memory_cache
    def write(self,data:StorageIOWriteData):
        data_path=data.path
        self.__storage_instance_dict[data_path.storage_type]._write_sync_cache(data_path.key,data.value)
    def read_all(self):
        return frozendict.frozendict(self.__memory_cache)
    def read(self,path:StorageIODataPath):
        return self.__memory_cache[path.storage_type][path.key]
    
class StorageObservable(Observable):
    def __init__(self,observer_name:str,storage:StorageIOCombine):
        self.storage=storage
        super().__init__(observer_name)
    def get_target(self):
        return ObjectLog(self.storage.read_all())
    def compare_target(self,new:ObjectLog,old:ObjectLog):
        return new.value!=old.value
        

if __name__=="__main__":
    class TestStorageSettings(StorageSettings):
        storage_type="memory"
        default_data={"test_key":"test_value"}
    class MemoryStorage(StorageIO):
        memory={'test_storaged':'test_value'}
        def __init__(self):
            super().__init__(TestStorageSettings())
        async def read_all(self) -> dict[str, Any]:
            return self.memory
        async def write(self,key:str,value:Any):
            self.memory[key]=value

    ms=MemoryStorage()
    storage=StorageIOCombine([ms])
    storage.write(StorageIOWriteData(StorageIODataPath("memory","key"),"value"))
    AppLogger.debug(storage.read_all())
    AppLogger.debug(ms.memory)