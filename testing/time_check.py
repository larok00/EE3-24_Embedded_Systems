import utime

start= utime.ticks_ms()	
print (start)		
print ("hello world")
print ("bye world")
print ("hello world")
print ("bye world")
stop = utime.ticks_ms() 		
print (stop)						#stop measuring time
time_diff= utime.ticks_diff(stop,start) 