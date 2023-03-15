
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

import uasyncio as asyncio
import bluetooth
import aioble

devices = dict()

async def scan():
    print("=== scanning BLE devices ... ===")
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_data = dict()
            device_data["name"] = result.name()
            device_data["rssi"] = result.rssi
            device_data["connectable"] = result.connectable
            services = ""
            for service in result.services():
                if services != "":
                    services = services + "\n"
                services = "  " + str(service)
            device_data["services"] = services
            if result.connectable or result.device.addr_hex() not in devices:
                devices[result.device.addr_hex()] = device_data
    for device in devices:
        print(devices[device]["name"], devices[device]["rssi"], devices[device]["connectable"], device)
        if devices[device]["services"] != "":
            print(devices[device]["services"])
    print("=== finished ===")
     
async def main():
    await scan()
    
asyncio.run(main())
