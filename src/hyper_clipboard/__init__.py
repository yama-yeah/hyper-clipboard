# import time
# from .const.observable_objects import ObservableStreamer,Observable
# from .services.clip_watcher import ClipObservable

# def main():
#     stream=ObservableStreamer([ClipObservable("clip")],0.5).sink()
#     for data in stream:
#         print(data)
#         time.sleep(1)
import asyncio
from bleak import BleakClient, BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        yield d

async def connect(address):
    client = BleakClient(address)
    try:
        await client.connect()
        if client.is_connected:
            print(client.services.services)
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

async def main():
    async for device in scan():
        print(device)

asyncio.run(main())