from hyper_clipboard.const.object_loggers import ObjectLog, LogsManager
type NameAddressDict = dict[str,str]

class BTDevicesLog(ObjectLog[NameAddressDict]):
    _instance = None
    def __init__(self,value:NameAddressDict):
        super().__init__(value)
    def clean_log(self,allowed_devices:list[str]):
        
        self.value = {k:v for k,v in self.value.items() if k in allowed_devices}
        

class BTDevicesManager(LogsManager[NameAddressDict]):
    allow_devices = []
    def __init__(self,addable_devices:list[str]=[], init_logs: list[ObjectLog[NameAddressDict]] = [], max_logs_length: int = 1) -> None:
        self.allow_devices = addable_devices
        super().__init__(init_logs,max_logs_length)
    def add_log(self, log: BTDevicesLog) -> None:
        log.clean_log(self.allow_devices)
        super().add_log(log)
    def add_allow_device(self,device:str):
        self.allow_devices.append(device)
    def remove_allow_device(self,device:str):
        self.allow_devices.remove(device)

