import asyncio
from bleak import BleakScanner
from hyper_clipboard.const.observable_objects import Observable
from hyper_clipboard.services.bluetooth.bt_device_manager import BTDevicesLog, BTDevicesManager


class BTDiscover:
    def __init__(self,devices_manager:BTDevicesManager) -> None:
        self.devices_manager=devices_manager
        
    async def scan(self,timeout:float=1):
        devices = await BleakScanner.discover(timeout=timeout)
        address_dict={}
        for d in devices:
            address_dict[d.name]=d.address
        return address_dict
    def refresh_device_manager(self):
        address_dict=asyncio.run(self.scan())
        self.devices_manager.add_log(BTDevicesLog(address_dict))
    def get_devices(self):
        return self.devices_manager.get_top()

class DiscoverObservable(Observable):
    def __init__(self,devices_manager:BTDevicesManager,observer_name) -> None:
        self.bt_discover=BTDiscover(devices_manager)
        super().__init__(observer_name=observer_name)
    def get_target(self):
        
        self.bt_discover.refresh_device_manager()
        return self.bt_discover.get_devices()
    def compare_target(self,new,old):
        return new!=old