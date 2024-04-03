from abc import ABC, abstractmethod
from typing import Generator, TypeVar, Generic,Callable
from dataclasses import dataclass
import time
import threading
from pprint import pprint
import asyncio

from hyper_clipboard.const.const_values import AppLogger
from hyper_clipboard.const.object_loggers import ObjectLog

T = TypeVar('T')





# kotlinのsealed classみたいなことをしたい
@dataclass
class _StreamData(ABC,Generic[T]):
    value:ObjectLog[T]
    def __init__(self,value):
        self.value=value

class ChangedStreamData(_StreamData):
    def __init__(self,value):
        super().__init__(value)

class DidNotChangeStreamData(_StreamData):
    def __init__(self,value):
        super().__init__(value)

#RXSwiftみたいに変更を監視したい
@dataclass
class StreamLog(Generic[T]):
    from_:str
    data:ObjectLog[T]

class Observable(ABC,Generic[T]):
    _inited=False
    _closed=False
    is_power_on=True
    
    def __init__(self,observer_name:str,interval:float=0.1):
        self.observer_name = observer_name
        self.old = self.get_target()
        self.interval = interval
        
    @abstractmethod
    def get_target(self)->ObjectLog[T]:
        pass
    @abstractmethod
    def compare_target(self,new:ObjectLog[T],old:ObjectLog[T])->bool:
        pass
    def _compare_target(self,new,old)->bool:
        if not self._inited:
            self._inited=True
            return True
        return self.compare_target(new,old)
    def close_func(self):
        pass
    def check_can_observe(self)->bool:
        return True
    def get_stream_data(self)->_StreamData:
        new = self.get_target()
        if self._compare_target(new,self.old):
            self.old=new
            return ChangedStreamData(new)
        else:
            return DidNotChangeStreamData(new)

class LambdaObservable(Observable[T]):
    def __init__(self,observer_name:str,get_target:Callable[['LambdaObservable'],ObjectLog[T]],compare_target:Callable[[ObjectLog[T],ObjectLog[T]],bool],check_can_observe:Callable[[],bool]=lambda:True):
        self.lam_get_target=get_target
        self.lam_compare_target=compare_target
        self.lam_check_can_observe=check_can_observe
        super().__init__(observer_name)
    def get_target(self):
        return self.lam_get_target(self)
    def compare_target(self,new,old):
        try:
            return self.lam_compare_target(new,old)
        except Exception as e:
            AppLogger.error(e,exception=e,header_text=f"LambdaObservable:{self.observer_name}")
    def check_can_observe(self):
        return self.lam_check_can_observe()

# 帰る値がないObservable
class VoidObservable(Observable):
    def __init__(self,observer_name:str):
        super().__init__(observer_name)
    @abstractmethod
    def get_target(self):
        pass
    def _compare_target(self,new,old):
        return False


#今回の実装だとここに全部のObservableを入れて監視する設計になっている
#自由度は低いけど、今回の規模ならちょうどいいかも
class ObservableStreamer:
    def __init__(self,observables:list[Observable],interval:float):
        super().__init__()
        self.observables = observables
        self.running = True
        self.interval = interval
        
    def sink(self)->Generator[StreamLog,None,None]:
        while self.running:
            while True:
                flag=True
                for observable in self.observables:
                    if not observable.check_can_observe():
                        flag=False
                        break
                if flag:
                    break
                asyncio.run(asyncio.sleep(self.interval))
            for observable in self.observables:
                data=observable.get_stream_data()
                if isinstance(data,ChangedStreamData):
                    yield StreamLog(from_=observable.observer_name,data=data.value)
                #AppLogger.wtf(self.observables_response_store,header_text=f"response_store")
            asyncio.run(asyncio.sleep(self.interval))
            #AppLogger.wtf('end',header_text=f"stream",use_traceback=False)
        for observable in self.observables:
            observable.close_func()

class ObservableAsyncStreamer(ObservableStreamer):
    observables_response_store={}
    observing_threads=[]
    tasks:list[asyncio.Task]=[]
    def __init__(self,observables:list[Observable],interval:float,loop:asyncio.AbstractEventLoop):
        response_observables=[]
        self.loop=loop
        for observable in observables:
            self.observables_response_store[observable.observer_name]=observable.get_target()
            get_target=lambda s:self.observables_response_store[s.observer_name]
            compare_target=observable.compare_target
            check_can_observe=observable.check_can_observe
            response_observable=LambdaObservable(observable.observer_name,get_target,compare_target,check_can_observe)
            response_observables.append(response_observable)
        for observable in observables:
            self.tasks.append(self.loop.create_task(self.run_observable(observable)))
        self.running = True
        self.interval = interval
        super().__init__(response_observables,interval)
        
    async def run_observable(self,observable:Observable):
        AppLogger.wtf('start',header_text=f"stream:{observable.observer_name}")
        
        while self.running:
            while not observable.check_can_observe():
                await asyncio.sleep(0.1)
            
            data=observable.get_stream_data()
            if isinstance(data,ChangedStreamData):
                self.observables_response_store[observable.observer_name]=data.value
                # AppLogger.info(data.value,header_text=f"stream:{observable.observer_name}")
                    
            await asyncio.sleep(observable.interval)
        observable.close_func()
    
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
                    log=StreamLog(from_=observable.observer_name,data=data.value)
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
                    log=StreamLog(from_=observable.observer_name,data=data.value)
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

