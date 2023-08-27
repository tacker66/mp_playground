
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

import gc
import uasyncio as asyncio
import aioble

devices = dict()
async def scan():
    print("=== scanning BLE devices ... ===")
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device = result.device.addr_hex()
            if device not in devices:
                device_data = dict()
                device_data["manufacturer_id"] = 0
                device_data["manufacturer"]    = set()
                device_data["services"]        = set()
                devices[device] = device_data
            else:
                device_data = devices[device]
            device_data["name"]        = result.name()
            device_data["rssi"]        = result.rssi
            device_data["connectable"] = result.connectable
            for data in result.manufacturer():
                device_data["manufacturer_id"] = data[0]
                if len(device_data["manufacturer"]) < 10:
                    device_data["manufacturer"].add(data[1])
            for service in result.services():
                device_data["services"].add(service)

async def main():
    while True:
        await scan()
        for device in sorted(devices):
            print(device, devices[device]["name"], hex(devices[device]["manufacturer_id"]), devices[device]["rssi"], devices[device]["connectable"])
            print(" ", devices[device]["manufacturer"])
            print(" ", devices[device]["services"])
        gc.collect()
        print("===", len(devices), "devices found;", gc.mem_free(), "free mem ===")
        await asyncio.sleep_ms(10000)
        
asyncio.run(main())
