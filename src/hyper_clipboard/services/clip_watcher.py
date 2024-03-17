import threading
import time
from ..const.observable_objects import ObservableStreamer,Observable
import pyperclip
class ClipObservable(Observable[str]):
    def __init__(self,name:str):
        super().__init__(name=name)
    def get_target(self)->str:
        return pyperclip.paste()
    def compare_target(self,new,old)->bool:
        return new != old