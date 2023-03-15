
import random
from time import sleep_ms
from machine import Pin

led = Pin(2, Pin.OUT)

try:
    while True:
        led.value(1)
        sleep_ms(random.randint(30, 300))
        led.value(0)
        sleep_ms(random.randint(30, 300))
except:
    pass
