import pytest
from hyper_clipboard.const.observable_objects import _StreamData, ChangedStreamData, DidNotChangeStreamData, Observable,ObservableStreamer,ObservableAsyncStreamer
from hyper_clipboard.const.object_loggers import ObjectLog
import asyncio
import random
import time

class MockCountObservable(Observable):
    def __init__(self, observer_name: str, observable_streamer:list[ObservableStreamer],from_count:int=0,interval: float = 0.1,how_many_times:int=3):
        self.observable_streamer=observable_streamer
        self.how_many_times=how_many_times+from_count
        self._count=from_count
        super().__init__(observer_name, interval)
        
    def get_target(self) -> ObjectLog[int]:
        self._count+=1
        if self._count>self.how_many_times:
            self.observable_streamer[0].running=False
        return ObjectLog(self._count,f"{self.observer_name}:{self._count}")
    def compare_target(self, new: ObjectLog[int], old: ObjectLog[int]) -> bool:
        return new.value!=old.value

class MockAsyncRandomStrObservable(Observable):
    def __init__(self, observer_name: str, observable_streamer:list[ObservableAsyncStreamer],random_list:list=['a','b','c'],interval: float = 0.1,how_many_times:int=3):
        self.observable_streamer=observable_streamer
        self.how_many_times=how_many_times
        self._count=0
        self.random_list=random_list
        self.random_wait_sum=0
        super().__init__(observer_name, interval)
        
    def get_target(self) -> ObjectLog[str]:
        self._count+=1
        if self._count>self.how_many_times:
            self.observable_streamer[0].running=False
        random_index=random.randint(0,len(self.random_list)-1)
        random_obj=self.random_list.pop(random_index)
        random_wait=random.random()
        self.random_wait_sum+=random_wait
        asyncio.run(asyncio.sleep(random_wait))
        return ObjectLog(random_obj,f"{self.observer_name}:{self._count}")
    def compare_target(self, new: ObjectLog[str], old: ObjectLog[str]) -> bool:
        return new.value!=old.value

class ObservanleStreamTester(Observable):
    count=0
    def __init__(self, observer_name: str, interval: float = 0.1,is_changed=True):
        self.is_changed=is_changed
        super().__init__(observer_name, interval)
    def get_target(self) -> ObjectLog:
        return ObjectLog('MockData',f"{self.observer_name}:{self.count}")
    def compare_target(self, new: ObjectLog, old: ObjectLog) -> bool:
        return self.is_changed

def test_Observable_get_stream():
    changed_observable=ObservanleStreamTester("observer1",0.1)
    data=changed_observable.get_stream_data()
    data=changed_observable.get_stream_data()
    assert isinstance(data,ChangedStreamData)
    did_not_changed_observable=ObservanleStreamTester("observer2",0.1,False)
    data=did_not_changed_observable.get_stream_data()
    data=did_not_changed_observable.get_stream_data()
    assert isinstance(data,DidNotChangeStreamData)


def test_ObservableStreamer():
    observable_streamer_list=[]
    count_observable1 = MockCountObservable("observer1",observable_streamer_list,0)
    count_observable2 = MockCountObservable("observer2",observable_streamer_list,1)
    observers:list[Observable]=[count_observable1,count_observable2]
    observable_streamer=ObservableStreamer(observers,0)
    observable_streamer_list.append(observable_streamer)
    stream = observable_streamer.sink()
    count=2
    
    for data in stream:
        count+=0.5
        log:ObjectLog=data.data
        assert log.value==int(count)
    

def test_ObservableAsyncStreamer():
    observable_streamer_list=[]
    random_list1=['a','b','c']
    random_list2=['d','e','f']
    how_many_times=3
    interval=0.1
    count_observable1 = MockAsyncRandomStrObservable("observer1",observable_streamer_list,random_list1,interval,how_many_times)
    count_observable2 = MockAsyncRandomStrObservable("observer2",observable_streamer_list,random_list2,interval,how_many_times)
    observers:list[Observable]=[count_observable1,count_observable2]
    observable_streamer=ObservableAsyncStreamer(observers,0,asyncio.get_event_loop())
    observable_streamer_list.append(observable_streamer)
    stream = observable_streamer.sink()
    start=time.time()
    for data in stream:
        log:ObjectLog=data.data
        assert log.value in ['a','b','c','d','e','f']
    diff=time.time()-start
    assert diff<count_observable1.random_wait_sum+count_observable2.random_wait_sum+interval*how_many_times*len(observers)
    


def test_StreamData():
    value = ObjectLog(1, "log1")
    stream_data = _StreamData(value)
    assert stream_data.value == value

def test_ChangedStreamData():
    value = ObjectLog(1, "log1")
    changed_stream_data = ChangedStreamData(value)
    assert changed_stream_data.value == value

def test_DidNotChangeStreamData():
    value = ObjectLog(1, "log1")
    did_not_change_stream_data = DidNotChangeStreamData(value)
    assert did_not_change_stream_data.value == value

# Add tests for StreamLog class here