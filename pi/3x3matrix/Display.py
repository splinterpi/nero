#! /usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

cathodes = [7,11,15]
anodes = [12,16,22]
sleeptime = 0.001
speed = 250 #low is faster

zero = [[1,1,1],[1,0,1],[1,1,1]]
ten = [[0,1,1],[0,1,1],[0,1,1]]
twenty = [[0,0,1],[0,0,1],[0,0,1]]
thirty = [[0,0,0],[0,0,0],[0,0,0]]
one = [[0,1,1],[1,1,1],[1,1,1]]
two = [[0,0,1],[1,1,1],[1,1,1]]
three = [[0,0,0],[1,1,1],[1,1,1]]
four = [[0,0,0],[0,1,1],[1,1,1]]
five = [[0,0,0],[0,0,1],[1,1,1]]
six = [[0,0,0],[0,0,0],[1,1,1]]
seven = [[0,0,0],[0,0,0],[0,1,1]]
eight = [[0,0,0],[0,0,0],[0,0,1]]
nine = [[0,0,0],[0,0,0],[0,0,0]]

# hardcoded value
tens = thirty 
ones = four

ani = [ tens, ones ]

for cathode in cathodes:
	GPIO.setup(cathode, GPIO.OUT)
	GPIO.output(cathode, 0)

for anode in anodes:
        GPIO.setup(anode, GPIO.OUT)
        GPIO.output(anode, 0)
try:
	while True:
		for frame in range(2):
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
