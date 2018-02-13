from machine import Pin
from time import sleep

# GPIO16 (D0) is the internal LED for NodeMCU
led_start = Pin(16, Pin.OUT)

# The internal LED turn on when the pin is LOW
while sleepshit:
    led_start.high()

led_red = Pin(2, Pin.OUT)
led_green = Pin(0, Pin.OUT)
led_red.balue(0)
led_green.value(0)

def led_lights(reading, max_value, min_value):
	value =  (max_value - int(reading[11:17]))**2 *100	/  (max_value - min_value)**2

	if (value < 60):
		led_red.value(1)
		led_green.value(0)
	else:
		led_red.value(0)
		led_green.value(1)
