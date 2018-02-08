#Embedded system project EE3-24
#micropython main programme for I2C connection

#the code below works on the screen interface
#set the connection
from machine import Pin, I2C
from ujson import dumps

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

#this function allows to check if the slave address is still 72
i2c.scan()

i2c.writeto(72, bytearray([0x01, 0x44, 0x23]))
i2c.writeto(72, bytearray([0x00]))
data = i2c.readfrom(72, 2)
int_data = int.from_bytes(data, 'big')

print(str(int_data))

data_record = {
	"reading" : int_data
}

payload = dumps(data_record)

####################################################################

import network

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover', 'exhibition')

#################################################################

import time
time.sleep(1)

if sta_if.isconnected():
	print("Success")
else:
	print("Failure")

########################################################

import machine
from umqtt.simple import MQTTClient

topic = "esys/Embedded_girls(and_Koral)/flex"

client = MQTTClient(machine.unique_id(), "192.168.0.10")
client.connect()

client.publish(topic, bytes(payload, 'utf-8'))

###################################################################

time.sleep(1)

###########################################################

data = i2c.readfrom(72, 2)
int_data = int.from_bytes(data, 'big')

print(str(int_data))

data_record = {
	"reading" : int_data
}

payload = dumps(data_record)

############################################

client.publish(topic, bytes(payload, 'utf-8'))

########################################
from machine import Pin

# create an output pin on pin #0
p5 = Pin(5)
p5 = Pin(5, Pin.IN)
# configure an irq callback
print(p5.value())

