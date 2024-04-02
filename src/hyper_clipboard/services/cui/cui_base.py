
from abc import ABC, abstractmethod
import sys

class FlushPrinter:
    def __init__(self):
        self.row_count = 0
    def row_counting(self, obj:object):
        obj = str(obj)
        return len(obj.split('\n'))
    def __enter__(self):
        return self
    def input(self, obj:object):
        self.row_count += self.row_counting(obj)
        return input(obj)
    def print(self, *values: object,sep: str | None = " ",end: str | None = "\n",):
        for value in values:
            self.row_count += self.row_counting(value)
            print(value,sep=sep,end=end)
    def __exit__(self, exc_type, exc_val, exc_tb):
        for _ in range(self.row_count):
            sys.stdout.write("\x1b[1A")
            sys.stdout.write("\x1b[2K")
        


class WidgetOperation(ABC):
    pass

class PushWidget(WidgetOperation):
    next:'Widget'
    def __init__(self,next:'Widget'):
        self.next=next

class PopWidget(WidgetOperation):
    pass

class RebuidWidget(WidgetOperation):
    pass

class ReplaceWidget(WidgetOperation):
    next:'Widget'
    def __init__(self,next:'Widget'):
        self.next=next

class Widget(ABC):
    @abstractmethod
    def build(self)->WidgetOperation:
        pass

class RootWidget(Widget):
    children:list[Widget]=[]
    def __init__(self,child:Widget):
        self.children.append(child)
    
    def build(self) -> WidgetOperation:
        return self.children[-1].build()
    
    def run(self):
        while len(self.children)>0:
            operation=self.build()
            if isinstance(operation,PushWidget):
                self.children.append(operation.next)
            elif isinstance(operation,PopWidget):
                self.children.pop()
            elif isinstance(operation,RebuidWidget):
                pass
            elif isinstance(operation,ReplaceWidget):
                self.children.pop()
                self.children.append(operation.next)
            else:
                raise ValueError('Invalid Widget Operation')
