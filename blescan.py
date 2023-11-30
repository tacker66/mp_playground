
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

import gc
import asyncio
import aioble

devices = dict()
async def scan():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device = result.device.addr_hex()
            if device not in devices:
                device_data = dict()
                device_data["device"]          = result.device
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

def hexdump(bytesset):
    for bs in bytesset:
        bs_hex = ""
        bs_str = ""
        for b in bs:
            bs_hex += f"{b:02x}" + " "
            bs_str += (chr(b) if 32 <= b <= 127 else ".") + " "
        print(" ", bs_hex, bs_str)

FLAG_READ = const(0x0002)

async def discover(device):
    conn = None
    try:
        conn = await device.connect()
    except:
        print("CONNECT FAILED")
    servs = dict()
    if conn != None and conn._conn_handle != None and conn._conn_handle > 0:
        async for serv in conn.services():
            servs[serv] = dict()
        for serv in servs:
            async for char in serv.characteristics():
                servs[serv][char] = list()
        for serv in servs:
            for char in servs[serv]:
                async for desc in char.descriptors():
                    servs[serv][char].append(desc)
        for serv in servs:
            print(" ", serv)
            for char in servs[serv]:
                charval = ""
                if char.properties & FLAG_READ:
                    try: # might fail
                        charval = "- " + str(await char.read())
                    except:
                        charval = "- READ ERROR"
                print("   ", char, charval)
                for desc in servs[serv][char]:
                    descval = ""
                    if desc.properties & FLAG_READ:
                        try: # might fail
                            descval = "- " + str(await desc.read())
                        except:
                            descval = "- READ ERROR"
                    print("     ", desc, descval)
    if conn != None:
        try: # might fail
            await conn.disconnect()
        except:
            print("DISCONNECT TIMEOUT")
    if len(servs) == 0:
        print("  -")
    
async def main():
    while True:
        print("=== Scanning BLE Devices ... ===")
        await scan()
        for device in sorted(devices):
            print()
            print(devices[device]["device"], devices[device]["name"], hex(devices[device]["manufacturer_id"]), devices[device]["rssi"], devices[device]["connectable"])
            print("Manufacturer Data")
            hexdump(devices[device]["manufacturer"])
            if len(devices[device]["manufacturer"]) == 0:
                print("  -")
            print("Advertised Services")
            for service in devices[device]["services"]:
                print(" ", service)
            if len(devices[device]["services"]) == 0:
                print("  -")
            print("Services")
            if devices[device]["connectable"]:
                await discover(devices[device]["device"])
            else:
                print("  -")
        gc.collect()
        print("\n===", len(devices), "Devices found;", int(gc.mem_free()/1024), "kB mem free ===\n")
        await asyncio.sleep_ms(10000)
        
asyncio.run(main())
