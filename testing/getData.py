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