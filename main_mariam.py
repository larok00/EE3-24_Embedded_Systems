#Embedded system project EE3-24

from machine import Pin, I2C, unique_id
from ujson import dumps

import network


from umqtt.simple import MQTTClient

import time
import utime

from machine import RTC

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


def count_function(array): #WORKS
	count = 0.0
	firsthalf_count = False
	secondhalf_count = False
	for x in range(0, (len(array)-2)):	
		if (array[x] > array[x+1] and array[x+1] > array[x+2] and firsthalf_count == False):
			count += 0.5
			firsthalf_count = True
			secondhalf_count = False

		if firsthalf_count == True:
			if (array[x] < array[x+1] and array[x+1] < array[x+2] and secondhalf_count == False):
				count += 0.5
				secondhalf_count = True
				firsthalf_count = False
	return count		



def publish(payload, client):
	topic = "esys/Embedded_girls(and_Koral)/flex"
	client.publish(topic, bytes(payload, 'utf-8'))

def test_pin():
	inputpin = Pin(14, Pin.IN)
	return inputpin.value()

#################################################################

#set the connection
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
setup_i2c_connection(i2c)

connect_to_network()

client = MQTTClient(unique_id(), "192.168.0.10")
connect_client(client)
array = []
start= utime.ticks_ms()								 #start measuring time

while (test_pin()==0 and len(array) <50): 			#length of array is 50
	payload = read_data(i2c)
	array.append(payload) 
	publish(payload, client)
	time.sleep(0.2)
	
print(max(array))
print(min(array))
#TotalCount = count_function(array)
#stop= utime.ticks_ms() 								#stop measuring time
#time_diff= utime.ticks_diff(stop,start) 
#print(TotalCount)
#print(time_diff/1000)
#Rate = TotalCount/(time_diff/1000)
#print(Rate)
#Efficiency = efficiency(array)



