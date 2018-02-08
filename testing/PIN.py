from machine import Pin

p14 = Pin(14, Pin.IN, Pin.PULL_UP)

print(p14.value())
