#! /usr/bin/env python

import RPi.GPIO as GPIO
import time
pinNum = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinNum,GPIO.OUT)
#set LED to flash forever

p = GPIO.PWM(pinNum,50)
p.start(0)

try:
	while True:
		for i in range(100):
			p.ChangeDutyCycle(i)
			time.sleep(0.02)
		for i in range(100):
			p.ChangeDutyCycle(100-i)
			time.sleep(0.02)
except KeyboardInterrupt:
	pass

p.stop()

GPIO.cleanup()

#while True:
#  GPIO.output(pinNum,GPIO.HIGH)
#  time.sleep(0.1)
#  GPIO.output(pinNum,GPIO.LOW)
#  time.sleep(0.1)
