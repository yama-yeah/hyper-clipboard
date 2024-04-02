from hyper_clipboard.const.observable_objects import Observable, ObservableAsyncStreamer
from hyper_clipboard.const.storage_settings import AppConfigKeys, AppConfigStorageSettings
from hyper_clipboard.const.utils import get_config_path
from hyper_clipboard.services.bluetooth.bt_base_objects import BTObjectObservable
from hyper_clipboard.services.bluetooth.bt_client import BTClients
from hyper_clipboard.services.bluetooth.bt_device_manager import BTDevicesManager
from hyper_clipboard.services.bluetooth.bt_discover import DiscoverObservable
from hyper_clipboard.services.clipboard.clip_manager import ClipLogsManager
from hyper_clipboard.services.clipboard.clip_watcher import ClipObservable
from hyper_clipboard.services.bluetooth.bt_server import BTServer, InputBTObjectState
from hyper_clipboard.const.const_values import AppBTMode, AppLogger, ObserverNames
import asyncio
import nest_asyncio

from hyper_clipboard.services.cui.cui_base import RootWidget
from hyper_clipboard.services.cui.pages import AllowDevicePage, DisAllowDevicePage, MainPage, SwitchAppModePage
from hyper_clipboard.services.storage.shared import SharedJsonStorage
from hyper_clipboard.services.storage.storage_base import StorageIOCombine, StorageIODataPath, StorageObservable
nest_asyncio.apply()

def _main():
    main_loop=asyncio.get_event_loop()
    app_config_storage=SharedJsonStorage(AppConfigStorageSettings(),get_config_path(app_name="hyper_clipboard"))
    storage=StorageIOCombine([app_config_storage])
    mode=storage.read(StorageIODataPath(AppConfigStorageSettings().storage_type,AppConfigKeys.APP_BT_MODE))
    observers_dict:dict[str,Observable]={}

    if mode==AppBTMode.CLIENT:
        
        addable_devices=storage.read(StorageIODataPath(AppConfigStorageSettings().storage_type,AppConfigKeys.ALLOWED_DEVICES))
        devices_manager=BTDevicesManager(addable_devices=addable_devices)
        bt_clients=BTClients(devices_manager,main_loop)
        devices_discover_observable=DiscoverObservable(devices_manager,ObserverNames.BLE_DISCOVERER)
        clients_state_observable=BTObjectObservable(bt_clients,ObserverNames.BLE_CLIENT)
        observers_dict[ObserverNames.BLE_DISCOVERER]=devices_discover_observable
        observers_dict[ObserverNames.BLE_CLIENT]=clients_state_observable

    elif mode==AppBTMode.SERVER:
        server=BTServer(main_loop)
        server.run()
        server_state_observable=BTObjectObservable(server,ObserverNames.BLE_SERVER)
        observers_dict[ObserverNames.BLE_SERVER]=server_state_observable
    else:
        raise ValueError(f"mode:{mode} is not supported")

    
    clip_logs_manager=ClipLogsManager([])
    clip_observable=ClipObservable(ObserverNames.CLIP,clip_logs_manager)
    observers_dict[ObserverNames.CLIP]=clip_observable
    
    storage_observable=StorageObservable(ObserverNames.STORAGE,storage)
    observers_dict[ObserverNames.STORAGE]=storage_observable
    
    observer_list=list(observers_dict.values())
    stream=ObservableAsyncStreamer(observer_list,2,main_loop).sink()
    
    for data in stream:
        
        match data.from_:
            case ObserverNames.CLIP:
                AppLogger.info(data.data,header_text=f"stream:{data.from_}")
                if mode==AppBTMode.CLIENT:
                    bt_clients.update_server_from_input(InputBTObjectState.from_object_log(data.data))
                elif mode==AppBTMode.SERVER:
                    server.update_server_from_input(InputBTObjectState.from_object_log(data.data))
            case ObserverNames.BLE_DISCOVERER:
                bt_clients.connect()
            case ObserverNames.BLE_SERVER:
                clip_logs_manager.add_log(data.data)
            case ObserverNames.BLE_CLIENT:
                clip_logs_manager.add_log(data.data)
            case ObserverNames.STORAGE:
                app_config=data.data.value[AppConfigKeys.storage_type]
                clip_observable.interval=app_config[AppConfigKeys.CLIPBOARD_INTERVAL]
                if mode==AppBTMode.CLIENT:
                    clients_state_observable.interval=app_config[AppConfigKeys.BT_CLIENTS_INTERVAL]
                elif mode==AppBTMode.SERVER:
                    server_state_observable.interval=app_config[AppConfigKeys.BT_SERVER_INTERVAL]
                
                devices_discover_observable.interval=app_config[AppConfigKeys.BT_DISCOVER_INTERVAL]
                devices_manager.allow_devices=app_config[AppConfigKeys.ALLOWED_DEVICES]
        

def main():
    try:
        _main()
    except Exception as e:
        AppLogger.critical(e,exception=e,header_text="main exception")

def setting():
    app_config_storage_settings=AppConfigStorageSettings()
    app_config_storage=SharedJsonStorage(app_config_storage_settings,'./')
    storage=StorageIOCombine([app_config_storage])
    pages=[AllowDevicePage(storage),DisAllowDevicePage(storage),SwitchAppModePage(storage)]
    RootWidget(MainPage(pages)).run()