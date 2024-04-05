from hyper_clipboard.const.object_loggers import LogsManager, ObjectLog, VoidObjectLog

def test_add_log():
    logs_manager = LogsManager([], 2)
    log1 = ObjectLog(1, "log1")
    log2 = ObjectLog(2, "log2")
    log3 = ObjectLog(3, "log3")

    logs_manager.add_log(log1)
    assert logs_manager.get_logs()

    logs_manager.add_log(log2)
    assert logs_manager.get_logs() == [log2, log1]

    # Adding a log when max_logs_length is reached should remove the oldest log
    logs_manager.add_log(log3)
    assert logs_manager.get_logs() == [log3, log2]

def test_is_addable_log():
    logs_manager = LogsManager([], 2)
    log1 = ObjectLog(1, "log1")
    log2 = ObjectLog(2, "log2")

    logs_manager.add_log(log1)
    assert not logs_manager.is_addable_log(log1)
    assert logs_manager.is_addable_log(log2)

def test_get_top():
    logs_manager = LogsManager([], 2)
    log1 = ObjectLog(1, "log1")
    log2 = ObjectLog(2, "log2")

    assert isinstance(logs_manager.get_top(), VoidObjectLog)

    logs_manager.add_log(log1)
    assert logs_manager.get_top() == log1

    logs_manager.add_log(log2)
    assert logs_manager.get_top() == log2