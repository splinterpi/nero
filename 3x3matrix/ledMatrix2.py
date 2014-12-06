#! /usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

cathodes = [7,11,15]
anodes = [12,16,22]
sleeptime = 0.001
speed = 25 #low is faster

one = [[0,1,1],
       [1,0,1],
       [1,1,0]]

two = [[1,0,1],
       [1,0,1],
       [1,0,1]]

three = [[1,1,0],
         [1,0,1],
         [0,1,1]]

four = [[1,1,1],
        [0,0,0],
        [1,1,1]]

ani = [ one, two, three, four ]

for cathode in cathodes:
	GPIO.setup(cathode, GPIO.OUT)
	GPIO.output(cathode, 0)

for anode in anodes:
        GPIO.setup(anode, GPIO.OUT)
        GPIO.output(anode, 0)
try:
	while True:
		for frame in range(4):
			for pause in range(speed):
				for i in range(3):
					GPIO.output(cathodes[0],ani[frame][i][0])
					GPIO.output(cathodes[1],ani[frame][i][1])
					GPIO.output(cathodes[2],ani[frame][i][2])
	
					GPIO.output(anodes[i],1)
					time.sleep(sleeptime)
					GPIO.output(anodes[i],0)

except KeyboardInterrupt:
	GPIO.cleanup()
