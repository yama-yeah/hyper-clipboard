from hyper_clipboard.const.const_values import UUIDNames,UPDATING_STATE
from hyper_clipboard.services.bluetooth.bt_base_objects import BTObject, BTObjectState, InputBTObjectState
from bleak import BleakClient

class _IsChangeableObjectSealed:
    pass

class NotChangeableState(_IsChangeableObjectSealed):
    pass

class ChangeableState(_IsChangeableObjectSealed):
    value:BTObjectState
    def __init__(self,value:BTObjectState) -> None:
        self.value=value


class BTClient(BTObject):
    def __init__(self) -> None:
        super().__init__()

    async def _read_a_state_from_server(self, client: BleakClient)->_IsChangeableObjectSealed:
        updating_state=await client.read_gatt_char(UUIDNames.UPDATING_STATE)
        if updating_state==bytearray(UPDATING_STATE.UPDATING):
            return NotChangeableState()
        await client.write_gatt_char(UUIDNames.UPDATING_STATE,bytearray(UPDATING_STATE.UPDATING))
        timestamp=await client.read_gatt_char(UUIDNames.TIMESTAMP)
        timestamp=int.from_bytes(timestamp,"big")
        if timestamp<=self.state.time_stamp:
            return NotChangeableState()
        clipboard=await client.read_gatt_char(UUIDNames.CLIPBOARD)
        clipboard=clipboard.decode("utf-8")
        if clipboard==self.state.value:
            return NotChangeableState()
        clipboard_id=await client.read_gatt_char(UUIDNames.CLIPBOARD_ID)
        clipboard_id=clipboard_id.decode("utf-8")
        if clipboard_id==self.state.id:
            return NotChangeableState()
        state=BTObjectState(
            time_stamp=timestamp,
            value=clipboard,
            id=clipboard_id,
            updating_state=UPDATING_STATE.UPDATED,
        )
        await client.write_gatt_char(UUIDNames.UPDATING_STATE,bytearray(UPDATING_STATE.UPDATED))
        
        return ChangeableState(state)


