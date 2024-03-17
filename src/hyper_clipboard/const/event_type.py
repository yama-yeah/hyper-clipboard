from enum import Enum
class AppEvents(Enum):
    NEUTRAL= "neutral"
    CLIPBOARD_CHANGED = "clipboard_changed"
    BLE_CLIP_RECEIVED = "ble_clip_received"