
print("=== boot.py ===")

import gc
import uos as os
import uerrno as errno
import time
import machine
import micropython

print("Enable a Debugger to connect ...")
time.sleep(3)

IS_DIR = 0x4000
IS_REGULAR = 0x8000

start = ""

print('{0} MHz clock frequeny'.format(machine.freq()))
micropython.mem_info()
s = os.statvfs('//')
print('{0} MB free flash memory'.format((s[0]*s[3])/1048576))

found = False
iter = os.ilistdir()
while True:
    try:
        entry = next(iter)
        filename = entry[0]
        filetype = entry[1]
        if filetype == IS_REGULAR:
            print("FILE", filename)
            if filename == start:
                found = True
        if filetype == IS_DIR:
            print(" DIR", filename)
    except StopIteration:
        break

if found:
    print("=== exec", start, "===")
    exec(open(start).read(), globals())

print("=== finished ===")
