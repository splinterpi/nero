#!/usr/bin/env python
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, re, os

t  = [1,2,3,4]
a  = [10,20,30,40]
b  = [0.5,1.5,2.5,3.5]
c  = [15,25,35,45]


fig, tp = plt.subplots(1, 1)
print fig
print tp
tp.plot(t, a)
tp.plot(t, c)
tp.plot(b, c)

#fig.figsize(5,10)

#tp.format_ydata = price
tp.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
#fig.autofmt_xdate()
fig.savefig("proto.png")
