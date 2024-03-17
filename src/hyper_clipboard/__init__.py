import time
from .const.observable_objects import ObservableStreamer,Observable
from .services.clip_watcher import ClipObservable

def main():
    stream=ObservableStreamer([ClipObservable("clip")],0.5).sink()
    for data in stream:
        print(data)
        time.sleep(1)
