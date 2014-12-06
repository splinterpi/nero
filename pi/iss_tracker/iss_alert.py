from sense_hat import SenseHat
import time

sense = SenseHat()

X = [30, 144, 255]  # Blue
O = [0, 0, 0]  # Black


def display_alert():

  iss = [
  X, X, O, O, O, O, X, X,
  X, X, O, X, X, O, X, X,
  X, X, O, X, X, O, X, X,
  X, X, X, X, X, X, X, X,
  X, X, O, X, X, O, X, X,
  X, X, O, O, O, O, X, X,
  X, X, O, O, O, O, X, X,
  O, O, O, O, O, O, O, O
  ]

  sense.set_pixels(iss)

def clear_screen():
  sense.clear()

display_alert()
time.sleep(5)
clear_screen()
