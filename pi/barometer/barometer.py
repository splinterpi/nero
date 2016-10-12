#! /usr/bin/python

from sense_hat import SenseHat
import time

sense = SenseHat()

pressure_mbar = round(sense.get_pressure(), 2)
pressure_inHg = round(pressure_mbar / 33.86, 2)
print("Pressure = %s mbar" % pressure_mbar)
print("Pressure = %s inHg" % pressure_inHg)

sense.show_message("P: %smbar" % pressure_mbar, text_colour=[255, 0, 0])
sense.show_message("%sinHg" % pressure_inHg, text_colour=[255, 0, 0])
