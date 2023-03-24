
print("=== boot.py ===")

import gc
import uos as os
import uerrno as errno
import time
import machine

#print("Enable a Debugger to connect ...")
#time.sleep(5)

IS_DIR = 0x4000
IS_REGULAR = 0x8000

start = ""

s = os.statvfs('//')
print('{0} MB free flash memory'.format((s[0]*s[3])/1048576))
print('{0} MB free RAM'.format((gc.mem_free())/1048576))
print('{0} MHz clock frequeny'.format(machine.freq()))

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
