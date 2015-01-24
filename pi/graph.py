#!/usr/bin/python 
# ------------------------------------------------------------------------------
# 07/11/2014 - paul.friel@gmail.com
# ------------------------------------------------------------------------------
# Bucket the tmp readings - create a histogram.
# numpy?
# ------------------------------------------------------------------------------

import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, re, os

from dateutil.relativedelta import relativedelta, MO

# ------------------------------------------------------------------------------

dev_props = {
    "L": { "desc": "Downstairs", "priority": 1, "color": "r" }
,   "B": { "desc": "Upstairs"  , "priority": 2, "color": "b" }
,   "P": { "desc": "Loft"      , "priority": 3, "color": "c" }
}

# ------------------------------------------------------------------------------

class Device:
    def __init__(self, dev_id):
        self.dev_id = dev_id
        self.tmp = []
        self.dt  = []

    def add_reading(self, tmp, dt): 
        self.tmp.append(tmp)
        self.dt.append(dt)

    def desc(self):
        return dev_props[self.dev_id]['desc']

    def priority(self):
        return dev_props[self.dev_id]['priority']

    def color(self):
        return dev_props[self.dev_id]['color']

# ------------------------------------------------------------------------------

class PeriodTmps:
    def __init__(self, start):
        self.start   = start
        self.devices = {}

    def add_reading(self, dev_id, tmp, dt): 
        if dev_id not in self.devices: 
            self.devices[dev_id] = Device(dev_id)

        self.devices[dev_id].add_reading(tmp, dt)

    def devs(self):
        values = self.devices.values()
        values.sort(key=lambda x: x.priority())
        return iter(values)

# ------------------------------------------------------------------------------

class Tmps:
    def __init__(self):
        self.days  = []
        self.weeks = []
  
    def add_reading(self, dev_id, tmp, dt): 
        day = self.get_day(dt)
        day.add_reading(dev_id, tmp, dt)

        week = self.get_week(dt)
        week.add_reading(dev_id, tmp, dt)

    def get_day(self, dt): 
        day = dt.replace(hour=0, minute=0, second=0, microsecond=0)

        if not self.days or self.days[-1].start != day:
            self.days.append(PeriodTmps(day))

        return self.days[-1]
 
    def get_week(self, dt): 
        week = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        week = week + relativedelta(weekday=MO(-1)) 

        if not self.weeks or self.weeks[-1].start != week:
            self.weeks.append(PeriodTmps(week))

        return self.weeks[-1]

# ------------------------------------------------------------------------------

def get_data(): 
    tmps = Tmps()
    
    for l in sys.stdin:
        f = l.split()
        if len(f) != 4: 
            print "Bad line: %s" % l,
            continue
    
        if 'V' in l: 
            print "voltage: %s" % l,
            continue 
    
        sse = int(f[0])
        md  = re.search(r'[+-]\d+', f[3])
    
        if not md: 
            print "Bad line: %s" % l,
            continue
   
        dev_id = f[3][0]
        tmp    = int(md.group(0)) / 1000.0
        dt     = datetime.datetime.fromtimestamp(sse)

        tmps.add_reading(dev_id, tmp, dt)    

    return tmps

# ------------------------------------------------------------------------------

def plot_day(day):
    fig, ax = plt.subplots(1, 1)

    fig.set_figwidth(12)
    fig.set_figheight(8)
    fig.set_dpi(10)

    for dev in day.devs():
        ax.plot(dev.dt, dev.tmp, label=dev.desc(), color=dev.color())

    ax.set_title("Temperature plot for %s" % day.start.strftime("%a, %d %b %Y"))
    ax.set_xlim(day.start, day.start + relativedelta(days=+1))
    
    # format the ticks
    hour_loc  = mdates.HourLocator(interval=1)   
    min_loc   = mdates.MinuteLocator(interval=10)   
    time_fmt  = mdates.DateFormatter('%H')

    ax.xaxis.set_major_locator(hour_loc)
    ax.xaxis.set_minor_locator(min_loc)
    ax.xaxis.set_major_formatter(time_fmt)

    ax.set_xlabel("Hour"       , fontsize=16, color="black")
    ax.set_ylabel("Temperature", fontsize=16, color="black")
    ax.legend(loc=0)
    ax.grid(True)
    
    fname = "tmp-%s.png" % day.start.strftime("%Y-%m-%d")
    print "Writing %s" % fname
    fig.savefig(fname)
    plt.close()

# ------------------------------------------------------------------------------

def plot_week(week):
    fig, ax = plt.subplots(1, 1)

    fig.set_figwidth(18)
    fig.set_figheight(10)
    fig.set_dpi(10)

    for dev in week.devs():
        ax.plot(dev.dt, dev.tmp, label=dev.desc(), color=dev.color())

    ax.set_title("Temperature plot for week starting %s" % week.start.strftime("%d %b %Y - week %U"))
    ax.set_xlim(week.start, week.start + relativedelta(weeks=+1))
    
    # format the ticks
    day_loc  = mdates.DayLocator(interval=1)   
    hour_loc = mdates.HourLocator(interval=4)   
    time_fmt = mdates.DateFormatter('%a-%d')

    ax.xaxis.set_major_locator(day_loc)
    ax.xaxis.set_minor_locator(hour_loc)
    ax.xaxis.set_major_formatter(time_fmt)

    ax.set_xlabel("Day"        , fontsize=16, color="black")
    ax.set_ylabel("Temperature", fontsize=16, color="black")
    ax.legend(loc=0)
    ax.grid(True)
    
    fname = "tmp-week-%s.png" % week.start.strftime("%Y-%m-%d")
    print "Writing %s" % fname
    fig.savefig(fname)
    plt.close()

# ------------------------------------------------------------------------------

def main():
    tmps = get_data()

    for week in tmps.weeks: 
        plot_week(week)

    for day in tmps.days: 
        plot_day(day)

# ------------------------------------------------------------------------------

main()

# ------------------------------------------------------------------------------
