from abc import abstractmethod
import asyncio
from better_logger import BetterLog, Color

from hyper_clipboard.const.const_values import AppBTMode
from hyper_clipboard.const.storage_settings import AppConfigKeys, AppConfigStorageSettings
from hyper_clipboard.services.bluetooth.bt_device_manager import BTDevicesManager
from hyper_clipboard.services.bluetooth.bt_discover import BTDiscover
from hyper_clipboard.services.cui.character import Characters, get_character
from hyper_clipboard.services.cui.cui_base import FlushPrinter, PopWidget, PushWidget, RebuidWidget, RootWidget, Widget, WidgetOperation
from hyper_clipboard.services.cui.menu_render_funcs import get_menu, get_selectable_texts
from hyper_clipboard.services.storage.shared import SharedJsonStorage
from hyper_clipboard.services.storage.storage_base import StorageIOCombine, StorageIODataPath, StorageIOWriteData



        
class SettingPageWidget(Widget):
    def __init__(self,name:str,storage:StorageIOCombine,) -> None:
        self.name=name
        self.storage=storage
        super().__init__()
    @abstractmethod
    def build(self) -> WidgetOperation:
        pass

class AllowDevicePage(SettingPageWidget):
    def __init__(self,storage:StorageIOCombine) -> None:
        self.selected_index=0
        device_manager=BTDevicesManager()
        self.discover=BTDiscover(device_manager)
        self.storage=storage
        self.allowed_devices=self.storage.read(StorageIODataPath(AppConfigStorageSettings().storage_type,AppConfigKeys.ALLOWED_DEVICES))
        self.is_scaned=False
        self.address_dict={}

        
        super().__init__('接続デバイス登録',storage)
    
    def _build_scanning(self):
        self.is_scaned=True
        header=BetterLog(('スキャン中',),Color.CYAN,'',100,'💭',formatter=lambda x:str(x),header_text=self.name).output()
        character=get_character(Characters.ThinkMan,'どれどれ')
        with FlushPrinter() as p:
            p.print(header)
            p.print(character)
            self.address_dict=asyncio.run(self.discover.scan())
        return RebuidWidget()
    def _build_scanned(self):
        selectable_texts=['再スキャン']
        names=[]
        for name,address in self.address_dict.items():
            if name in self.allowed_devices or name is None:
                continue
            names.append(name)
            selectable_texts.append(f'{name}:{address}')
        
        selectable_texts=get_selectable_texts(tuple(selectable_texts))
        header=get_menu(selectable_texts,self.name)
        character=get_character(Characters.ListenMan,'名前が設定されていないデバイスは登録できないよ')
        with FlushPrinter() as p:
            p.print(header)
            p.print(character)
            selected=p.input('選択してください:')
            try:
                selected=int(selected)
            except ValueError:
                selected=-1
                return RebuidWidget()
        if selected==1:
            self.is_scaned=False
            return RebuidWidget()
        for i in range(2,len(names)+2):
            if selected==i:
                self.allowed_devices.append(names[i-2])
                self.storage.write(StorageIOWriteData(StorageIODataPath(AppConfigKeys.storage_type,AppConfigKeys.ALLOWED_DEVICES),self.allowed_devices))
        if selected==len(selectable_texts):
            return PopWidget()
        return RebuidWidget()
    def build(self) -> WidgetOperation:
        if not self.is_scaned:
            return self._build_scanning()
        return self._build_scanned()

class DisAllowDevicePage(SettingPageWidget):
    def __init__(self,storage:StorageIOCombine) -> None:
        self.selected_index=0
        
        super().__init__('接続デバイス解除',storage)
    def build(self) -> WidgetOperation:
        allowed_devices:list=self.storage.read(StorageIODataPath(AppConfigStorageSettings().storage_type,AppConfigKeys.ALLOWED_DEVICES))
        selectable_texts=get_selectable_texts(tuple(allowed_devices))
        header=get_menu(tuple(selectable_texts),self.name)
        character=get_character(Characters.ListenMan,'名前が設定されていないデバイスは登録できないよ')
        with FlushPrinter() as p:
            p.print(header)
            p.print(character)
            selected=p.input('選択してください:')
            try:
                selected=int(selected)
            except ValueError:
                selected=-1
                return RebuidWidget()
        for i in range(len(allowed_devices)):
            if selected==i+1:
                allowed_devices.pop(i)
                self.storage.write(StorageIOWriteData(StorageIODataPath(AppConfigKeys.storage_type,AppConfigKeys.ALLOWED_DEVICES),allowed_devices))
                return RebuidWidget()
        if selected==len(selectable_texts):
            return PopWidget()
        return RebuidWidget() 

class SwitchAppModePage(SettingPageWidget):
    def __init__(self,storage:StorageIOCombine) -> None:
        self.selected_index=0
        
        super().__init__('アプリモード切り替え',storage)
    def build(self) -> WidgetOperation:
        app_mode=self.storage.read(StorageIODataPath(AppConfigStorageSettings().storage_type,AppConfigKeys.APP_BT_MODE))
        selectable_texts=['サーバーモード','クライアントモード']
        selectable_texts=get_selectable_texts(tuple(selectable_texts))
        header=get_menu(tuple(selectable_texts),self.name)
        character=get_character(Characters.ListenMan,'どちらにしますか？')
        with FlushPrinter() as p:
            p.print(header)
            p.print(character)
            selected=p.input('選択してください:')
            try:
                selected=int(selected)
            except ValueError:
                selected=-1
                return RebuidWidget()
        if selected==1:
            app_mode=AppBTMode.SERVER
            return PopWidget()
        elif selected==2:
            app_mode=AppBTMode.CLIENT
            return PopWidget()
        elif selected==len(selectable_texts):
            return PopWidget()
        self.storage.write(StorageIOWriteData(StorageIODataPath(AppConfigKeys.storage_type,AppConfigKeys.APP_BT_MODE),app_mode))
        return RebuidWidget()


class MainPage(Widget):
    def __init__(self,pages:list[SettingPageWidget]) -> None:
        self.pages=pages
        super().__init__()
    def build(self) -> WidgetOperation:
        page_names=[page.name for page in self.pages]
        selectable_texts=get_selectable_texts(tuple(page_names))
        
        header=get_menu(selectable_texts,'メインメニュー')
        character=get_character(Characters.ListenMan,'望みは何かな？')
        with FlushPrinter() as p:
            p.print(header)
            p.print(character)
            selected=p.input('選択してください:')
            try:
                selected=int(selected)
            except ValueError:
                selected=-1
        for i in range(len(self.pages)):
            if selected==i+1:
                return PushWidget(self.pages[i])
        if selected==len(selectable_texts):
            return PopWidget()
        return RebuidWidget()
if __name__ == "__main__":
    app_config_storage_settings=AppConfigStorageSettings()
    app_config_storage=SharedJsonStorage(app_config_storage_settings,'./')
    storage=StorageIOCombine([app_config_storage])
    pages=[AllowDevicePage(storage),DisAllowDevicePage(storage),SwitchAppModePage(storage)]
    RootWidget(MainPage(pages)).run()