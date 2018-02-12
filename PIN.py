from machine import Pin


# create an output pin on pin #0
inputpin = Pin(14, Pin.IN, Pin.PULL_UP)
	
if (inputpin.value()==0):
	print("0")
else:
	print("1")
