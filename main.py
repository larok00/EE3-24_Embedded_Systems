#Embedded system project EE3-24

from machine import Pin, I2C, unique_id, sleep
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
	client.publish(topic, bytes(payload, 'utf-8'), 1)

def efficiency(reading, min_value, max_value):
	return (max_value - reading)**2 *100 / (max_value - min_value)**2

def main(i2c, led_red, led_green):
	
	cycle_count = 0
	cycle = []
	cycle_index = 0
	
	squeezing = -1
	squeeze_strength = []
	
	#threshold values
	min_value = 13200				#the minimum raw data reading we get through testing (with flexsensor unbent)
	
	start= utime.ticks_ms()			 #start measuring time as soon as someone starts using flexo
	
	
	payload = read_data(i2c)		#array is null and we need two extra elements in array to do comparisons later on
	max_value = payload				#the maximum raw data reading we get through testing (with flexsensor highly bent)
	cycle.append(payload) 
	payload = read_data(i2c)
	cycle.append(payload)
	
	while cycle_index<50:
		
		reading = read_data(i2c)
		if efficiency(reading, min_value, max_value)< 60:
			led_red.on()
			led_green.off()
		else:
			led_red.off()
			led_green.on()
		cycle.append(reading)
		
		if squeezing*(cycle[cycle_index] - cycle[cycle_index+1]) > 100 and squeezing*(cycle[cycle_index+1] - cycle[cycle_index+2]) > 100:
			
			if squeezing == 1:		#from squeeze to release
				squeezing = -1
			else:		#from release to squeeze
				
				smallest_reading = min(cycle)
				if efficiency(smallest_reading, min_value, max_value) > 25:
					cycle_count += 1
					print("Cycle done")
				squeeze_strength.append( smallest_reading )
				
				cycle = []
				reading = read_data(i2c)		#array is null and we need two extra elements in array to do comparisons later on
				cycle.append(reading) 
				reading = read_data(i2c)
				cycle.append(reading)
				
				cycle_index = -1
				squeezing = 1

		cycle_index += 1
		

		utime.sleep(0.1)
	
	
	if cycle_count > 0:
		stop = utime.ticks_ms() - 5000 								#stop measuring time; 5 seconds when user wasn't exercising
		time_diff= utime.ticks_diff(stop,start)
		rate = cycle_count/(time_diff/(1000*60))
		average_strength = float(sum(squeeze_strength))/float(len(squeeze_strength))
		average_efficiency =  efficiency(average_strength, min_value, max_value)
		
		print("total number of squeeze-and-release pairs performed = ", cycle_count)
		print("number of seconds spent exercising = ", (time_diff/1000))
		print("your rate was ", rate, " squeeze-and-release per minute.")
		print("your efficiency in this work out was ", average_efficiency, "%")
		
		payload = create_payload(exercise_no, cycle_count, rate, average_efficiency)
		
	else:
		print("Squeeze!")
		payload = None
	
	return payload

#initial setup


i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

i2c.writeto(72, bytearray([0x01, 0x44, 0x23]))
i2c.writeto(72, bytearray([0x00]))


ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover', 'exhibition')


exercise_no = 1

client = MQTTClient(unique_id(), "192.168.0.10")

inputpin = Pin(14, Pin.IN, Pin.PULL_UP)
led_start = Pin(16, Pin.OUT)
led_red = Pin(2, Pin.OUT)
led_green = Pin(0, Pin.OUT)

while True:
	if (inputpin.value()==0):
		client.connect()
		led_start.off()
		payload = main(i2c, led_red, led_green)
		if payload:
			print(payload)
			publish(payload, client)
			exercise_no += 1
		client.disconnect()
	led_red.off()
	led_green.off()
	led_start.on()
	utime.sleep(0.5)
