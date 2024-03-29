import asyncio
import datetime
from typing import Any
from hyper_clipboard.const.const_values import AppLogger, UUIDNames,UPDATING_STATE
from hyper_clipboard.const.object_loggers import ChangedObjectLog
from hyper_clipboard.const.observable_objects import Observable, VoidObservable
from hyper_clipboard.services.bluetooth.bt_base_objects import BTObject, BTObjectState, InputBTObjectState
from hyper_clipboard.services.bluetooth.bt_device_manager import BTDevicesLog, BTDevicesManager
from bleak import BleakClient, BleakScanner

class _IsChangeableObjectSealed:
    pass

class NotChangeableState(_IsChangeableObjectSealed):
    pass

class ChangeableState(_IsChangeableObjectSealed):
    value:BTObjectState
    def __init__(self,value:BTObjectState) -> None:
        self.value=value

class BTDiscover:
    def __init__(self,devices_manager:BTDevicesManager,loop) -> None:
        self.loop=loop
        self.devices_manager=devices_manager
        
    async def scan(self):
        # AppLogger.debug('',header_text='DiscoverObservable debug start')
        devices = await BleakScanner.discover()
        address_dict={}
        for d in devices:
            address_dict[d.name]=d.address
        # AppLogger.debug('',header_text='DiscoverObservable debug end')
        return address_dict
    def refresh_device_manager(self):
        address_dict=asyncio.run(self.scan())
        self.devices_manager.add_log(BTDevicesLog(address_dict))
    def get_devices(self):
        return self.devices_manager.get_top()

#　定期実行を目的とするObservableのためBTベースクラスの継承はしない方針
#  返り値のStreamはあくまでログ目的で使用はしない
class DiscoverObservable(Observable):
    def __init__(self,devices_manager:BTDevicesManager,observer_name,loop) -> None:
        self.bt_discover=BTDiscover(devices_manager,loop=loop)
        super().__init__(observer_name=observer_name)
    def get_target(self):
        
        self.bt_discover.refresh_device_manager()
        #AppLogger.debug(self.bt_discover.get_devices().value,header_text='DiscoverObservable debug end')
        return self.bt_discover.get_devices()
    def compare_target(self,new,old):
        return new!=old

class BTClients(BTObject):
    clients:dict[str,BleakClient]={}
    def __init__(self,devices_manager:BTDevicesManager,loop: asyncio.AbstractEventLoop) -> None:
        self.is_started=True
        self.devices_manager=devices_manager
        super().__init__(loop=loop)

    def connect(self):
        address_dict=self.devices_manager.get_top().value
        connected_names=self.clients.keys()
        tasks: list[asyncio.Task]=[]
        for name,address in address_dict.items():
            if name not in connected_names:
                client=BleakClient(address)
                self.clients[name]=client
                tasks.append(self.loop.create_task(client.connect()))
        while True:
            if len(tasks)==0:
                break
            if all([task.done() for task in tasks]):
                break
            asyncio.run(asyncio.sleep(0.1))
        

    async def run_transmission(self,task,client_name:str):
        client=self.clients[client_name]
        try:
            updating_state=await self._read_gatt_char(client,UUIDNames.UPDATING_STATE)
            updating_state=updating_state[UUIDNames.UPDATING_STATE]
            if updating_state==UPDATING_STATE.UPDATING:
                return
            await client.write_gatt_char(UUIDNames.UPDATING_STATE,bytearray(UPDATING_STATE.UPDATING))
            await task(client)
            await client.write_gatt_char(UUIDNames.UPDATING_STATE,bytearray(UPDATING_STATE.UPDATED))
        except Exception as e:
            AppLogger.error(e,exception=e,header_text='BTClients transmission error')
            await client.disconnect()
            self.clients.pop(client_name)
    
    async def _read_gatt_char(self,client: BleakClient,uuid:str)->dict[str,Any]:
        data=await client.read_gatt_char(uuid)
        data=self.bytearrray_to_data(uuid,data)
        return {uuid:data}

    async def _read_state_from_server(self, client: BleakClient)->_IsChangeableObjectSealed:
        tasks=[self._read_gatt_char(client,UUIDNames.TIMESTAMP),self._read_gatt_char(client,UUIDNames.CLIPBOARD),self._read_gatt_char(client,UUIDNames.CLIPBOARD_ID)]
        results=await asyncio.gather(*tasks)
        results={k:v for d in results for k,v in d.items()}
        timestamp:int=results[UUIDNames.TIMESTAMP]
        if timestamp<=self.state.time_stamp:
            return NotChangeableState()
        clipboard:str=results[UUIDNames.CLIPBOARD]
        if clipboard==self.state.value:
            return NotChangeableState()
        clipboard_id:str=results[UUIDNames.CLIPBOARD_ID]
        if clipboard_id==self.state.id:
            return NotChangeableState()
        state=BTObjectState(
            time_stamp=timestamp,
            value=clipboard,
            id=clipboard_id,
            updating_state=UPDATING_STATE.UPDATED,
        )
        return ChangeableState(state)
    
    async def _update_state_from_server(self,client):
        changeable_state=await self._read_state_from_server(client)
        if isinstance(changeable_state,ChangeableState):
            self.state=changeable_state.value
    
    async def _update_state_from_server_async(self):
        tasks=[]
        for client_name in self.clients.keys():
            task=self.loop.create_task(self.run_transmission(self._update_state_from_server,client_name))
            tasks.append(task)
        while True:
            if all([task.done() for task in tasks]):
                break
            await asyncio.sleep(0.1)
        
    def update_state_from_server(self):
        self.loop.run_until_complete(self._update_state_from_server_async())
        
    async def _writable_state_to_server(self,client: BleakClient)->bool:
        updating_state=await self._read_gatt_char(client,UUIDNames.UPDATING_STATE)
        if updating_state[UUIDNames.UPDATING_STATE]==bytearray(UPDATING_STATE.UPDATING):
            return False
        timestamp=await self._read_gatt_char(client,UUIDNames.TIMESTAMP)
        timestamp=timestamp[UUIDNames.TIMESTAMP]
        uuid= await self._read_gatt_char(client,UUIDNames.CLIPBOARD_ID)
        uuid=uuid[UUIDNames.CLIPBOARD_ID]
        if timestamp>=self.state.time_stamp or uuid==self.state.id:
            return False
        return True

    async def _write_server_from_state(self, client: BleakClient):
        if not await self._writable_state_to_server(client):
            return
        bytes_dict=self.state.to_bytes_dict()
        for key in bytes_dict:
            await client.write_gatt_char(key,bytes_dict[key])
    
    async def _update_server_from_input_async(self, input_state: InputBTObjectState):
        if not self.check_updatable_state(input_state,self.state):
            return
        self.state=input_state.to_BTServerState()
        self.state.updating_state=UPDATING_STATE.UPDATING
        tasks=[]
        for client_name in self.clients.keys():
            task=self.loop.create_task(self.run_transmission(self._write_server_from_state,client_name))
            tasks.append(task)
        while True:
            if all([task.done() for task in tasks]):
                break
            await asyncio.sleep(0.1)
        self.state.updating_state=UPDATING_STATE.UPDATED

    def update_server_from_input(self, input_state: InputBTObjectState):
        self.loop.run_until_complete(self._update_server_from_input_async(input_state))
        

# class ClientStateObservable(Observable):
#     def __init__(self, observer_name: str, bt_clients: BTClients) -> None:
#         self.bt_clients=bt_clients
#         super().__init__(observer_name)
#     def get_target(self):
#         return self.bt_clients.state
#     def _compare_target(self,new,old):
#         return new!=old
    
# import asyncio
# from bleak import BleakScanner
# now=datetime.datetime.now()
# async def main():
#     devices = await BleakScanner.discover(timeout=1)
#     for d in devices:
#         print(d.address, d.name)

# asyncio.run(main())
# import asyncio
# import datetime
# # from bleak import BleakClient

# address = "A656D587-801A-BF62-E8D1-D3801604A521"
# #0:00:02.873504
# 
# async def main(address):
#     client=BleakClient(address)
#     await client.connect()
    
#     cb = await client.read_gatt_char(UUIDNames.CLIPBOARD)
#     print(cb.decode("utf-8"))
#     input()
#     await client.disconnect()
# client=BTClient(BTDevicesManager())
# # asyncio.run(client.update_state_from_server())
# print(client.state)
# t=datetime.datetime.now()-now
# print(t)
