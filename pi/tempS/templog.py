#! /usr/bin/env python
import datetime

tfile = open("/sys/bus/w1/devices/28-000006741a54/w1_slave")

text = tfile.read()

tfile.close()

secondline = text.split("\n")[1]

temperaturedata = secondline.split(" ")[9]

temperature = float(temperaturedata[2:])

temperature = temperature / 1000

temperature = round(temperature,1)

print temperature,
#print chr(176) + 'C'
print 'C'

date = datetime.datetime.now()

datafile = open("/home/reesd/temp_data.log", "a")
datafile.write(str(date) + "\t" + str(temperature) + "\n")

datafile.close()
