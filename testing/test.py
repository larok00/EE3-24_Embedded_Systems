from machine import RTC
import utime

rtc = RTC()
now = utime.time()
tm = utime.localtime(now)
future_time = utime.mktime((tm[0], tm[1] + 7, tm[2], tm[3], tm[4], tm[5], tm[6], tm[7]))

print(utime.localtime(future_time))