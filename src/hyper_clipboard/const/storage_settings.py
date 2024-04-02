from dataclasses import dataclass
from hyper_clipboard.services.storage.storage_base import StorageSettings
from hyper_clipboard.const.const_values import AppBTMode


class AppConfigKeys:
    storage_type:str="app_config"
    CLIPBOARD_INTERVAL = "clipboard_interval"
    BT_CLIENTS_INTERVAL = "bt_clients_interval"
    BT_SERVER_INTERVAL = "bt_server_interval"
    BT_DISCOVER_INTERVAL = "bt_discover_interval"
    ALLOWED_DEVICES = "allowed_devices"
    APP_BT_MODE="app_bt_mode"

@dataclass
class AppConfigStorageSettings(StorageSettings):
    storage_type:str="app_config"
    default_data={
        AppConfigKeys.CLIPBOARD_INTERVAL:0.5,
        AppConfigKeys.BT_CLIENTS_INTERVAL:0.5,
        AppConfigKeys.BT_SERVER_INTERVAL:0.5,
        AppConfigKeys.BT_DISCOVER_INTERVAL:0.7,
        AppConfigKeys.ALLOWED_DEVICES:[],
        AppConfigKeys.APP_BT_MODE:AppBTMode.CLIENT
    }