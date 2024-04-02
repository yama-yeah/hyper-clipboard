from hyper_clipboard.const.object_loggers import ObjectLog
from hyper_clipboard.const.object_loggers import ChangedObjectLog, LogsManager
import pyperclip
class ClipLogsManager(LogsManager[str]):
    def refresh_logs(self):
        clip=pyperclip.paste()
        top_log_clip=self.get_top().value
        if clip!=top_log_clip:
            self.add_log(ChangedObjectLog(clip))

    def is_addable_log(self, log: ObjectLog[str]) -> bool:
        return super().is_addable_log(log) and log.value != None and self.get_top().value != log.value
    
    def add_log(self, log: ObjectLog[str]) -> None:
        super().add_log(log)
        if self.is_addable_log(log):
            pyperclip.copy(log.value)

