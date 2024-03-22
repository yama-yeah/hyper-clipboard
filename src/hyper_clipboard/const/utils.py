from datetime import datetime,timezone
from typing import Callable, Optional

def make_id_from_name(name:str)->int:
    list_ = [str(ord(c)) for c in name]
    return int("" . join(list_[:4]))

def get_milli_unix_time()->int:
    utc_time = datetime.now(timezone.utc)
    float_unix_time = utc_time.timestamp()
    mili_unix_time = int(float_unix_time*1000)
    return mili_unix_time

# this method is copied from the bisect module
def bisect_right(a, x, lo=0, hi=None, *, compareXthanY=lambda x,y:x<y):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(i, x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.

    A custom key function can be supplied to customize the sort order.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    while lo < hi:
        mid = (lo + hi) // 2
        if compareXthanY(x,a[mid]):
            hi = mid
        else:
            lo = mid + 1
    return lo

def binsort(a, x, lo=0,hi=None,*, compareXthanY=lambda x,y:x<y):
    i = bisect_right(a, x,lo,hi, compareXthanY=compareXthanY)
    a.insert(i, x)