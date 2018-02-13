#Embedded system project EE3-24

from machine import Pin, I2C, unique_id
from ujson import dumps

import network
from math import exp

from umqtt.simple import MQTTClient

import utime	#to measure the time elapsed in using flexo


def read_data(i2c):
	data = i2c.readfrom(72, 2)
	int_data = int.from_bytes(data, 'big')
	return int_data

def create_payload(exercise_no, cycle_count, rate, efficiency):
	summary = {
		"excercise_no" : exercise_no,
		"count" : cycle_count,
		"rate" : rate,
		"efficiency" : efficiency,
	}
	
	payload = dumps(summary)
	
	return payload

def publish(payload, client):
	topic = "esys/Embedded_girls(and_Koral)/flex"
	#client.publish(topic, bytes(payload, 'utf-8'), 1)

def test_pin():
	inputpin = Pin(14, Pin.IN)
	return (inputpin.value()==0)

#initial setup


i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
#this function allows to check if the slave address is still 72
#i2c.scan()

i2c.writeto(72, bytearray([0x01, 0x44, 0x23]))
i2c.writeto(72, bytearray([0x00]))


ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover', 'exhibition')


exercise_no = 1

client = MQTTClient(unique_id(), "192.168.0.10")

test_result = True

while (test_result):
	client.connect()
	
	cycle_count = 0
	cycle = []
	cycle_index = 0
	
	squeezing = -1
	squeeze_strength = []
	
	#threshold values
	min_value = 13200				#the minimum raw data reading we get through testing (with flexsensor unbent)	
	max_value = 19000				#the maximum raw data reading we get through testing (with flexsensor highly bent)	
	
	start= utime.ticks_ms()			 #start measuring time as soon as someone starts using flexo
	
	
	payload = read_data(i2c)		#array is null and we need two extra elements in array to do comparisons later on
	max_value = payload
	cycle.append(payload) 
	payload = read_data(i2c)
	cycle.append(payload)
	
	while cycle_index<50:
		
		payload = read_data(i2c)
		cycle.append(payload)
		
		if squeezing*(cycle[cycle_index] - cycle[cycle_index+1]) > 100 and squeezing*(cycle[cycle_index+1] - cycle[cycle_index+2]) > 100:
			
			if squeezing == 1:		#from squeeze to release
				cycle_count += 1
				squeezing = -1
			else:		#from release to squeeze
				squeeze_strength.append( min(cycle) )
				
				cycle = []
				payload = read_data(i2c)		#array is null and we need two extra elements in array to do comparisons later on
				cycle.append(payload) 
				payload = read_data(i2c)
				cycle.append(payload)
				
				cycle_index = -1
				squeezing = 1

		cycle_index += 1
		

		utime.sleep(0.1)
	
	
	if cycle_count > 0:
		stop = utime.ticks_ms() - 5000 								#stop measuring time; 5 seconds when user wasn't exercising
		time_diff= utime.ticks_diff(stop,start)
		rate = cycle_count/(time_diff/(1000*60))
		average_strength = float(sum(squeeze_strength))/float(len(squeeze_strength))
		efficiency =  (max_value - average_strength)**2 *100 / (max_value - min_value)**2
		
		print("total number of squeeze-and-release pairs performed = ", cycle_count)
		print("number of seconds spent exercising = ", (time_diff/1000))
		print("your rate was ", rate, " squeeze-and-release per minute.")
		print("your efficiency in this work out was ", efficiency, "%")
		
		payload = create_payload(exercise_no, cycle_count, rate, efficiency)
		publish(payload, client)
		
		exercise_no += 1
	else:
		print("squeeze!")

	client.disconnect()
	
	test_result = test_pin()
