from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic,Callable
from socket import gethostname
import random
import uuid
import bisect
from .utils import get_milli_unix_time,make_id_from_name
from .const_values import squids,hostname
# pyright: reportPrivateImportUsage=false



T = TypeVar('T')
class _ObjectLog(Generic[T]):
    def __init__(self,value:T,log_id:Optional[str]=None,time_stamp:Optional[int]=None):
        self.id = log_id if log_id else squids.encode([make_id_from_name(hostname),id(self)])
        self.value = value
        self.time_stamp = time_stamp if time_stamp else get_milli_unix_time()
    def compare(self,other:'_ObjectLog')->bool:
        if self.time_stamp==other.time_stamp:
            return self.id<other.id
        else:
            return self.time_stamp<other.time_stamp
    def __lt__(self, other: '_ObjectLog') -> bool:
        return self.compare(other)
    

class ChangedObjectLog(_ObjectLog[T]):
    def __init__(self,value:T,log_id:Optional[str]=None,time_stamp:Optional[int]=None):
        super().__init__(value,log_id,time_stamp)

class DidNotChangeObjectLog(_ObjectLog[T]):
    def __init__(self,value:T,log_id:Optional[str]=None,time_stamp:Optional[int]=None):
        super().__init__(value,log_id,time_stamp)

class VoidObjectLog(_ObjectLog[T]):
    def __init__(self):
        self.value=None
        self.id=None
        self.time_stamp=0
    def compare(self,other:'_ObjectLog')->bool:
        return True
        
class LogsManager(Generic[T]):
    def __init__(self,init_logs:list[_ObjectLog[T]]=[],max_logs_length:int=1) -> None:
        self._logs = init_logs
        self.max_logs_length = max_logs_length
    def get_logs(self)->list[_ObjectLog[T]]:
        return self._logs
    #使用用途によっては、このメソッドをオーバーライドする
    def is_addable_log(self,log:_ObjectLog[T])->bool:
        flag=True
        for log_ in self._logs:
            if log_.id==log.id:
                flag=False
                break
        return flag
    def add_log(self,log:_ObjectLog[T])->None:
        if self.is_addable_log(log):
            bisect.insort(self._logs,log)
            if len(self._logs)>self.max_logs_length:
                self._logs.pop(0)
    def get_top(self)->_ObjectLog[T]:
        if len(self._logs)==0:
            return VoidObjectLog[T]()
        return self._logs[-1]