from bleak import BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        yield d
