from hyper_clipboard.const.const_values import AppLogger
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
        if self.is_addable_log(log):
            AppLogger.wtf(log.value,header_text='clip manager',use_traceback=False)
            pyperclip.copy(log.value)
        super().add_log(log)

