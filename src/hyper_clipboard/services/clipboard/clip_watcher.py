from hyper_clipboard.const.observable_objects import Observable
from hyper_clipboard.const.object_loggers import ObjectLog

class ClipObservable(Observable[str]):
    
    def __init__(self,name:str,clipmanager):
        self.clipmanager=clipmanager
        super().__init__(observer_name=name)
        
    def get_target(self):
        self.clipmanager.refresh_logs()
        return self.clipmanager.get_top()
    def compare_target(self,new:ObjectLog,old:ObjectLog):
        return new.value!=old.value