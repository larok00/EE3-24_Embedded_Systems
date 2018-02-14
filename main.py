#Embedded system project EE3-24

from machine import Pin, I2C, unique_id, sleep
from ujson import dumps						#for messages formatting in JSON
import network								#establishing network connection
from math import exp		#KORAL: can we delete this now?
from umqtt.simple import MQTTClient			#establishing MQTT connection
import utime								#to measure the time elapsed in using flexo


def read_data(i2c):									#to receive data
	data = i2c.readfrom(72, 2)						#reading bytes
	int_data = int.from_bytes(data, 'big')			#converting string of bytes into int
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

def efficiency(reading, min_value, max_value):				#to calculate how efficient each reading is 
	return (max_value - reading)**2 *100 / (max_value - min_value)**2

def main(i2c, led_red, led_green):
	
	cycle_count = 0
	cycle = []
	cycle_index = 0
	
	squeezing = -1					#alternates between 1 and -1 depending on whether you're squeezing or releasing
	squeeze_strength = []
	
	#threshold values
	min_value = 13200				#the minimum raw data reading we get through testing (with flexsensor unbent)
	
	start= utime.ticks_ms()			 #start measuring time as soon as someone starts using flexo
	
	
	payload = read_data(i2c)		#array is null and we need two extra elements in array to do comparisons later on
	max_value = payload				#the maximum raw data reading we get through testing (with flexsensor highly bent)
	cycle.append(payload) 
	payload = read_data(i2c)
	cycle.append(payload)
	
	while cycle_index<50:			#KORAL: Change to 50 now that we aren't testing? 
		
		reading = read_data(i2c)
		if efficiency(reading, min_value, max_value)< 60:
			led_red.on()
			led_green.off()
		else:
			led_red.off()
			led_green.on()
		cycle.append(reading)
		
		if squeezing*(cycle[cycle_index] - cycle[cycle_index+1]) > 100 and squeezing*(cycle[cycle_index+1] - cycle[cycle_index+2]) > 100:
			
			if squeezing == 1:					#from squeeze to release
				squeezing = -1
			else:								#from release to squeeze
				
				smallest_reading = min(cycle)								#reading we get when our squeeze is maximum for this cycle
				if efficiency(smallest_reading, min_value, max_value) > 25:		#your squeeze-and-release will only be counted if your efficiency is 25% (avoids minor vibrations)
					cycle_count += 1
					print("Cycle done")
				squeeze_strength.append( smallest_reading )				#a list with all the readings we get when our squeeze is maximum per cycle
				
				cycle = []						#after one complete squeeze-and-release cycle, cycle list is nulled
				reading = read_data(i2c)		#array is null and we need two extra elements in array to do comparisons later on
				cycle.append(reading) 
				reading = read_data(i2c)
				cycle.append(reading)
				
				cycle_index = -1
				squeezing = 1

		cycle_index += 1						#if cycle_index > 0, cycle_index*sleeptime(i.e. 0.1 seconds) = the time the user has not squeezed flexo

		utime.sleep(0.1)						#adding delay for 1/10 th of a second 
	
	
	if cycle_count > 0:												#if the user has used flexo
		stop = utime.ticks_ms() - 5000 								#stop measuring time; 5 seconds when user wasn't exercising are subtracted
		time_diff= utime.ticks_diff(stop,start)
		rate = cycle_count/(time_diff/(1000*60))					#rate calculated
		average_strength = float(sum(squeeze_strength))/float(len(squeeze_strength))		#average value of maximum squeeze for entire session calculated
		average_efficiency =  efficiency(average_strength, min_value, max_value)			#average efficiency for entire session calculated
		
		print("total number of squeeze-and-release pairs performed = ", cycle_count)
		print("number of seconds spent exercising = ", (time_diff/1000))
		print("your rate was ", rate, " squeeze-and-release per minute.")
		print("your efficiency in this work out was ", average_efficiency, "%")
		
		payload = create_payload(exercise_no, cycle_count, rate, average_efficiency)  		#KORAL: dont know what to say/add 
		
	else:												#if the user has not used flexo
		print("Squeeze!")
		payload = None									#payload is empty
	
	return payload

#initial setup


i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

i2c.writeto(72, bytearray([0x01, 0x44, 0x23]))
i2c.writeto(72, bytearray([0x00]))

#establishing network connection
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover', 'exhibition')


exercise_no = 1

client = MQTTClient(unique_id(), "192.168.0.10")

#pins used on the ESP8266
inputpin = Pin(14, Pin.IN, Pin.PULL_UP)			#used as a button: user presses the button before starting session
led_start = Pin(16, Pin.OUT)					#KORAL: are we actually using this? if not can you delete
led_red = Pin(2, Pin.OUT)						#red LED is on when the user is not squeezing "enough"
led_green = Pin(0, Pin.OUT)						#green LED is on when the user is squeezing "enough"

while True:
	if (inputpin.value()==0):					#when button pressed (KORAL: right?)
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
	utime.sleep(0.5)				#KORAL: Why 0.5?
