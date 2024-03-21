from hyper_clipboard.const.object_loggers import _ObjectLog
from ...const.object_loggers import ChangedObjectLog, LogsManager
import pyperclip
class ClipLogsManager(LogsManager[str]):
    def refresh_logs(self):
        clip=pyperclip.paste()
        top_log_clip=self.get_top().value
        if clip!=top_log_clip:
            self.add_log(ChangedObjectLog(clip))
    
    def add_log(self, log: _ObjectLog[str]) -> None:
        if self.is_addable_log(log):
            self._logs.append(log)
            if len(self._logs) > self.max_logs_length:
                self._logs.pop(0)
            pyperclip.copy(log.value)

