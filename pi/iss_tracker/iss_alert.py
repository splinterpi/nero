#! /usr/bin/python

from sense_hat import SenseHat
import time

sense = SenseHat()

X = [65, 105, 225]  # Royal Blue
O = [0, 0, 0]  # Black

question_mark = [
X, X, O, O, O, O, X, X,
X, X, O, X, X, O, X, X,
X, X, O, X, X, O, X, X,
X, X, X, X, X, X, X, X,
X, X, O, X, X, O, X, X,
X, X, O, X, X, O, X, X,
X, X, O, O, O, O, X, X,
O, O, O, O, O, O, O, O
]

sense.set_pixels(question_mark)
time.sleep(5)
sense.clear()

