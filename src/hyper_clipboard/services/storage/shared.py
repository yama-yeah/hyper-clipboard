import json
import os
from typing import Any
from hyper_clipboard.const.const_values import AppLogger
from hyper_clipboard.services.storage.storage_base import StorageIO, StorageSettings


class SharedJsonStorage(StorageIO):
    def __init__(self,storage_settings:StorageSettings,prefix_path:str=""):
        self.file_path=os.path.join(prefix_path,storage_settings.storage_type+".json")
        super().__init__(storage_settings)

    async def read_all(self) -> dict[str, Any]:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            AppLogger.info("File not found, creating new file",header_text="SharedJsonStorage")
            with open(self.file_path, "w") as f:
                json.dump({}, f)
                return {}

    async def write(self, key: str, value: Any):
        with open(self.file_path, "w") as f:
            json.dump(self._memory_cache, f)
