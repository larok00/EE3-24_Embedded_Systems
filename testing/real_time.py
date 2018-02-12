#Embedded system project EE3-24

from machine import Pin, I2C, unique_id
from ujson import dumps

import network


from umqtt.simple import MQTTClient

import time
import utime

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
	#print(str(int_data))

	data_record = {"reading": int_data } 

	
	payload = dumps(data_record)
	
	return payload

def connect_to_network():
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(False)

	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	sta_if.connect('EEERover', 'exhibition')
	
	time.sleep(1)
"""	
	if sta_if.isconnected():
		print("Success")
	else:
		print("Failure")
"""

def connect_client(client):
	topic = "esys/Embedded_girls(and_Koral)/flex"
	client.connect()


def sample_func(array):
	count = 0
	for x in range(0,len(array)):
		count += 1

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
count = 0.0
x = 0
firsthalf_count = False
secondhalf_count = False
cycle_complete = True
squeeze_strength = []
array = []
array2 = []
first_time = True

while (test_pin()==0): 			

	if(cycle_complete == True):
		payload = read_data(i2c)
		array.append(payload) 

		payload = read_data(i2c)
		array.append(payload)

		cycle_complete = False

	payload = read_data(i2c)
	array.append(payload)

	#if (array[x] > array[x+1] and array[x+1] > array[x+2] and firsthalf_count == False):
	#print( int(array[x][11:17]) )
	if ((int(array[x][11:17]) - int(array[x+1][11:17]) > 1000) and (int(array[x+1][11:17]) - int(array[x+2][11:17]) > 1000) and (firsthalf_count == False)):
		if(first_time ==True): 
			start= utime.ticks_ms()			 #start measuring time as soon as someone starts using flexo 
			first_time = False

		count += 0.5
		firsthalf_count = True
		secondhalf_count = False

	
	if firsthalf_count == True:
		if ((int(array[x+1][11:17]) - int(array[x][11:17]) > 1000) and (int(array[x+2][11:17]) - int(array[x+1][11:17]) > 1000) and (secondhalf_count == False)):
			count += 0.5
			secondhalf_count = True
			firsthalf_count = False
			squeeze_strength.append( min(array) )
			array = []
			cycle_complete = True
			####print(count) - want to publish this
			x = -1

	x += 1
	publish(payload, client)
	time.sleep(0.1)

	if(x ==50):  #if 5 seconds pass and no change observed, exit
		break
	

if count > 0:
	stop = utime.ticks_ms() - 5000 								#stop measuring time; 5 seconds when user wasnt exercising
	time_diff= utime.ticks_diff(stop,start) 
	print("total number of squeeze-and-release pairs performed = ", count)
	print("your total time spent exercising = ", time_diff/1000)
	Rate = count/(time_diff/1000)
	print("your rate was ", Rate, " squeeze-and-release per second.")


	for y in range(0, len(squeeze_strength)):
		squeeze_strength_num = int(squeeze_strength[y][11:17])
		array2.append(squeeze_strength_num)
	
	efficiency =  13000 *100	/ (sum(array2)/len(array2)) 
	print("your efficiency in this work out was ", efficiency, "%")

else:
	print("squeeze it mate")


#testing gives min value 13000
