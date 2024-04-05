import pytest
from hyper_clipboard.const.const_values import UUIDNames, UPDATING_STATE

def test_UUIDNames_get_name_from_uuid():
    assert UUIDNames.get_name_from_uuid(UUIDNames.MAIN) == "MAIN"
    assert UUIDNames.get_name_from_uuid(UUIDNames.TIMESTAMP) == "TIMESTAMP"
    assert UUIDNames.get_name_from_uuid(UUIDNames.CLIPBOARD) == "CLIPBOARD"
    assert UUIDNames.get_name_from_uuid(UUIDNames.CLIPBOARD_ID) == "CLIPBOARD_ID"
    with pytest.raises(ValueError):
        UUIDNames.get_name_from_uuid("nonexistent-uuid")