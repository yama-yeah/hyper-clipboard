from logging import StreamHandler, getLogger
import logging
from socket import gethostname
# pyright: reportPrivateImportUsage=false
from sqids import Sqids
hostname = gethostname()
squids=Sqids(blocklist=[])
from dataclasses import dataclass
from enum import Enum

@dataclass
class UUIDNames:
    MAIN="A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
    TIMESTAMP="120615a4-aaa6-481f-bcdc-5e222bf3551d"
    CLIPBOARD="c96fec7b-c13e-44d3-8291-9408db876f27"
    CLIPBOARD_ID="c2eef872-8779-474c-9361-f2db13cf1d7b"
    UPDATING_STATE="b4d0dc3d-8474-4810-a873-97387cd18d35"
    @staticmethod
    def get_name_from_uuid(uuid:str)->str:
        for name in UUIDNames.__dict__:
            if UUIDNames.__dict__[name]==uuid:
                return name
        raise ValueError(f"uuid:{uuid} is not found in UUIDNames")
@dataclass
class UPDATING_STATE:
    NOT_UPDATING=b"0"
    UPDATING=b"1"
    UPDATED=b"2"
@dataclass
class ObserverNames:
    CLIP="clip"
    BLE_SERVER="ble_server"
    BLE_CLIENT="ble_client"
    BLE_DISCOVERER="ble_discoverer"

class AppEvents(Enum):
    NEUTRAL= "neutral"
    CLIPBOARD_CHANGED = "clipboard_changed"
    BLE_CLIP_RECEIVED = "ble_clip_received"

from better_logger import BetterLogger
logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = StreamHandler()
logger.addHandler(stream_handler)
AppLogger=BetterLogger(logger)