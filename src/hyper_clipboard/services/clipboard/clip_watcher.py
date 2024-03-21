import threading
import time
from ...const.observable_objects import ObservableStreamer,Observable
from .clip_manager import ClipLogsManager
from ...const.object_loggers import _ObjectLog
import pyperclip
class ClipObservable(Observable[str]):
    def __init__(self,name:str,clipmanager=ClipLogsManager()):
        self.clipmanager=clipmanager
        super().__init__(observer_name=name)
        
    def get_target(self):
        self.clipmanager.refresh_logs()
        return self.clipmanager.get_top()
    def compare_target(self,new:_ObjectLog,old:_ObjectLog):
        return new.value!=old.value