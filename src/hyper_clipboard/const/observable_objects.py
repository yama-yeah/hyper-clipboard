from abc import ABC, abstractmethod
from typing import TypeVar, Generic,Callable
from dataclasses import dataclass
import time
import threading
from pprint import pprint


# kotlinのsealed classみたいなことをしたい
class _StreamData(ABC):
    def __init__(self,value):
        self.value=value

class ChangedStreamData(_StreamData):
    def __init__(self,value):
        super().__init__(value)

class DidNotChangeStreamData(_StreamData):
    def __init__(self,value):
        super().__init__(value)

#RXSwiftみたいに変更を監視したい
T = TypeVar('T')
class Observable(ABC,Generic[T]):
    def __init__(self,name:str):
        self.old = self.get_target()
        self.name = name
    @abstractmethod
    def get_target(self)->T:
        pass
    @abstractmethod
    def compare_target(self,new,old)->bool:
        pass
    def get_stream_data(self)->_StreamData:
        new = self.get_target()
        if self.compare_target(new,self.old):
            self.old=new
            return ChangedStreamData(new)
        else:
            return DidNotChangeStreamData(new)

@dataclass
class StreamLog:
    from_:str
    data:object

#今回の実装だとここに全部のObservableを入れて監視する設計になっている
#自由度は低いけど、今回の規模ならちょうどいいかも
class ObservableStreamer:
    def __init__(self,observables:list[Observable],interval:float):
        super().__init__()
        self.observables = observables
        self.running = True
        self.interval = interval
    def sink(self):
        while self.running:
            for observable in self.observables:
                data=observable.get_stream_data()
                if isinstance(data,ChangedStreamData):
                    yield StreamLog(from_=observable.name,data=data.value)
            time.sleep(self.interval)

#debug用のクラス
class ObservableLogger(threading.Thread):
    @staticmethod
    def print_log(log:StreamLog):
        print(f"=============================")
        print(f"Observable: {log.from_}")
        pprint(log.data)
        print(f"=============================")

    def __init__(self,observables:list[Observable],interval:float,hook:Callable[[StreamLog],None]|None=print_log):
        super().__init__()
        self.observables = observables
        self.running = True
        self.hook=hook
        self.interval = interval
    
    def run(self):
        while self.running:
            for observable in self.observables:
                data=observable.get_stream_data()
                if isinstance(data,ChangedStreamData):
                    log=StreamLog(from_=observable.name,data=data)
                    if self.hook:
                        self.hook(log)
            time.sleep(self.interval)

    def stop(self):
        self.running=False
        self.join()

#後々のためにObservableStackerを作っておく    
class ObservableStacker(threading.Thread):
    def __init__(self,observables:list[Observable],interval:float,max_stack_size:int|None=None):
        super().__init__()
        self.observables = observables
        self.running = True
        self.interval = interval
        self.stack:list[StreamLog]=[]
        self.max_stack_size=max_stack_size
    def run(self):
        while self.running:
            for observable in self.observables:
                data=observable.get_stream_data()
                if isinstance(data,ChangedStreamData):
                    log=StreamLog(from_=observable.name,data=data)
                    if self.max_stack_size and len(self.stack) >= self.max_stack_size:
                        self.stack.pop(0)
                    self.stack.append(log)
            time.sleep(self.interval)
    def stop(self):
        self.running=False
        self.join()
    def clear(self):
        self.stack.clear()
    def pop(self,num:int):
        return self.stack.pop(num)

