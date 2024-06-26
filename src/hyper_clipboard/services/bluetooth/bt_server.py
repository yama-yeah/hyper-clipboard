# pyright: reportPrivateImportUsage=false
from abc import ABC, abstractmethod
import asyncio
import sys
import threading
from typing import Union, Any

from hyper_clipboard.services.bluetooth.bt_base_objects import BTObject, InputBTObjectState
from hyper_clipboard.const.const_values import UPDATING_STATE, AppLogger, hostname,UUIDNames
from dataclasses import dataclass

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)



class BTServer(BTObject):
    
    gatt: dict = {
        UUIDNames.MAIN: {
            UUIDNames.TIMESTAMP: {
                "Properties": (
                    GATTCharacteristicProperties.read
                    | GATTCharacteristicProperties.write
                    | GATTCharacteristicProperties.indicate
                ),
                "Permissions": (
                    GATTAttributePermissions.readable
                    | GATTAttributePermissions.writeable
                ),
                "Value": None,
            },
            UUIDNames.CLIPBOARD: {
                "Properties": (
                    GATTCharacteristicProperties.read
                    | GATTCharacteristicProperties.write
                    | GATTCharacteristicProperties.indicate
                ),
                "Permissions": (
                    GATTAttributePermissions.readable
                    | GATTAttributePermissions.writeable
                ),
                "Value": None,
            },
            UUIDNames.CLIPBOARD_ID: {
                "Properties": (
                    GATTCharacteristicProperties.read
                    | GATTCharacteristicProperties.write
                    | GATTCharacteristicProperties.indicate
                ),
                "Permissions": (
                    GATTAttributePermissions.readable
                    | GATTAttributePermissions.writeable
                ),
                "Value": None,
            },
            UUIDNames.UPDATING_STATE: {
                "Properties": (
                    GATTCharacteristicProperties.read
                    | GATTCharacteristicProperties.write
                    | GATTCharacteristicProperties.indicate
                ),
                "Permissions": (
                    GATTAttributePermissions.readable
                    | GATTAttributePermissions.writeable
                ),
                "Value": None,
            },
        },
    }
    is_started=False
    def __init__(self,loop:asyncio.AbstractEventLoop,server_name:str="HC-"+hostname,initiall_clipboard_value:str=""):
        super().__init__(loop)
        self.trigger: Union[asyncio.Event, threading.Event]
        server_name=server_name[:12]
        if sys.platform in ["darwin", "win32"]:
            self.trigger = threading.Event()
        else:
            self.trigger = asyncio.Event()
        self.state.value=initiall_clipboard_value
        self.server:BlessServer=BlessServer(server_name,self.loop)
    
    def read_request(self,characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray: # type: ignore
        return characteristic.value
    def write_request(self,characteristic: BlessGATTCharacteristic, value: Any, **kwargs): # type: ignore
        characteristic.value = value

    async def _main(self):
        self.trigger.clear()
        await self.server.add_gatt(self.gatt)
        self.server.read_request_func = self.read_request #type: ignore
        self.server.write_request_func = self.write_request #type: ignore
        AppLogger.info("Server started",header_text='BTServer message',use_traceback=True)
        await self.server.start()
        AppLogger.info("Advertising",header_text='BTServer message')
        self._update_a_value_from_state(UUIDNames.UPDATING_STATE)
        self._update_values_from_state()
        self.state.updating_state=UPDATING_STATE.NOT_UPDATING
        self._update_a_value_from_state(UUIDNames.UPDATING_STATE)
        self.is_started=True
        if self.trigger.__module__ == "threading":
            while not self.trigger.is_set():
                await asyncio.sleep(1)
        else:
            await self.trigger.wait() #type: ignore
        AppLogger.info("Server stopped",header_text='BTServer message')
        await self.server.stop()

    def run(self):
        self.loop.create_task(self._main())

    def _update_a_value_from_state(self,uuid:str):
        charact =self.server.get_characteristic(uuid)
            
        if charact is None:
            raise ValueError(f"Invalid characteristic: {uuid}")
        charact.value=self.state.to_bytes_dict()[uuid]
        self.server.update_value(UUIDNames.MAIN,uuid)

    
    def _update_values_from_state(self):
        for key in self.state.to_dict():
            self._update_a_value_from_state(key)
    def update_server_from_input(self,input_state:InputBTObjectState):
        self.state=input_state.to_BTServerState()
        self._update_values_from_state()
        self.state.updating_state=UPDATING_STATE.UPDATED
        self._update_a_value_from_state(UUIDNames.UPDATING_STATE)
    def update_state_from_server(self):
        if not self.is_started:
            return
        for key in self.state.to_dict():
            charact =self.server.get_characteristic(key)
            if charact is None:
                raise ValueError(f"Invalid characteristic: {key}")
            self.state[key]=self.bytearrray_to_data(key,charact.value)
        self.state.updating_state=UPDATING_STATE.NOT_UPDATING
        self._update_a_value_from_state(UUIDNames.UPDATING_STATE)
    def update_input_from_server(self,input_state:InputBTObjectState):
        if self.check_updatable_state(input_state,self.state):
            self.state=input_state.to_BTServerState()
            self.update_state_from_server()

        
    
