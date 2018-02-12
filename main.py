#Embedded system project EE3-24

from machine import Pin, I2C, unique_id
from ujson import dumps

import network


from umqtt.simple import MQTTClient

import time

def setup_i2c_connection(i2c):
	#micropython main programme for I2C connection
	
	#the code below works on the screen interface
	
	
	#this function allows to check if the slave address is still 72
	i2c.scan()
	
	i2c.writeto(72, bytearray([0x01, 0x44, 0x23]))
	i2c.writeto(72, bytearray([0x00]))

def read_data(i2c):
	data = i2c.readfrom(72, 2)
	int_data = int.from_bytes(data, 'big')
	
	print(str(int_data))
	
	data_record = {
		"reading" : int_data
	}
	
	payload = dumps(data_record)
	
	return payload

def connect_to_network():
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(False)

	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	sta_if.connect('EEERover', 'exhibition')
	
	time.sleep(1)
	
	if sta_if.isconnected():
		print("Success")
	else:
		print("Failure")

def connect_client(client):
	topic = "esys/Embedded_girls(and_Koral)/flex"
	
	client.connect()

def publish(payload, client):
	topic = "esys/Embedded_girls(and_Koral)/flex"
	client.publish(topic, bytes(payload, 'utf-8'))

def test_pin():
	# create an output pin on pin #0
	inputpin = Pin(14, Pin.IN, Pin.PULL_UP)
	# configure an irq callback
	print(inputpin.value())
	return inputpin.value()

#################################################################

#set the connection
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
setup_i2c_connection(i2c)

connect_to_network()

client = MQTTClient(unique_id(), "192.168.0.10")
connect_client(client)

while (test_pin()==0):
	payload = read_data(i2c)
	print(test_pin())
	publish(payload, client)
	time.sleep(1)


