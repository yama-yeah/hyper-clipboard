from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union
from hyper_clipboard.const.const_values import UPDATING_STATE, UUIDNames
from hyper_clipboard.const.object_loggers import _ObjectLog


@dataclass
class InputBTObjectState(_ObjectLog[str]):
    time_stamp:int
    value:Union[None,str]
    id:Union[None,str]
    def to_dict(self)->dict:
        return {
            UUIDNames.TIMESTAMP:self.time_stamp,
            UUIDNames.CLIPBOARD:self.value,
            UUIDNames.CLIPBOARD_ID:self.id,
            UUIDNames.UPDATING_STATE:UPDATING_STATE.UPDATING
        }
    def __getitem__(self,key:str):
        return self.to_dict()[key]
    def __setitem__(self,key:str,value):
        d=self.to_dict()
        d[key]=value
        self.time_stamp=d[UUIDNames.TIMESTAMP]
        self.value=d[UUIDNames.CLIPBOARD]
        self.id=d[UUIDNames.CLIPBOARD_ID]
        self.updating_state=d[UUIDNames.UPDATING_STATE]
    def to_BTServerState(self)->'BTObjectState':
        return BTObjectState.from_dict(self.to_dict())
    @staticmethod
    def from_object_log(log:_ObjectLog[str]):
        return InputBTObjectState(
            time_stamp=log.time_stamp,
            value=log.value,
            id=log.id
        )
@dataclass
class BTObjectState(InputBTObjectState):
    updating_state:Union[None,bytes]=UPDATING_STATE.NOT_UPDATING
    def to_dict(self)->dict:
        return {
            UUIDNames.TIMESTAMP:self.time_stamp,
            UUIDNames.CLIPBOARD:self.value,
            UUIDNames.CLIPBOARD_ID:self.id,
            UUIDNames.UPDATING_STATE:self.updating_state
        }
    def to_bytes_dict(self):
        d=self.to_dict()
        for key in d:
            data=d[key]
            if isinstance(data,str):
                data=data.encode("utf-8")
            if isinstance(data,int):
                data=data.to_bytes((data.bit_length() + 7) // 8, 'big')
            elif data is None:
                data=b""
            d[key]=bytearray(data)
        return d
    @staticmethod
    def from_dict(d:dict):
        return BTObjectState(
            time_stamp=d[UUIDNames.TIMESTAMP],
            value=d[UUIDNames.CLIPBOARD],
            id=d[UUIDNames.CLIPBOARD_ID],
            updating_state=d[UUIDNames.UPDATING_STATE]
        )
    def __setitem__(self, key, value):
        return super().__setitem__(key, value)

class BTObject(ABC):
    state=BTObjectState.from_dict({
        UUIDNames.TIMESTAMP:0,
        UUIDNames.CLIPBOARD:None,
        UUIDNames.CLIPBOARD_ID:None,
        UUIDNames.UPDATING_STATE:UPDATING_STATE.UPDATING,
    })
    @abstractmethod
    def update_state_from_server(self):
        pass
    @abstractmethod
    def update_server_from_input(self,input_state:InputBTObjectState):
        pass

    def check_updatable_state(self,updating_state:InputBTObjectState,old_state:InputBTObjectState):
        return updating_state.time_stamp>old_state.time_stamp and updating_state.id!=old_state.id