#! /usr/bin/python

import urllib, json, threading, math, logging, os, time
from sense_hat import SenseHat
from daemon.runner import DaemonRunner, DaemonRunnerStopFailureError

url= "https://api.wheretheiss.at/v1/satellites/25544"
home_lat = 52.1249
home_long = -0.2188
sense = SenseHat()

class Tracker(object):

  def __init__(self): 
    self.stdin_path = '/dev/null'
    self.stdout_path = '/dev/tty'
    self.stderr_path = '/dev/tty'
    self.pidfile_path =  '/tmp/iss_tracker.pid'
    self.pidfile_timeout = 5

  def alert(self):
    O = [0, 0, 0]
    X = [65, 105, 225]  # Royal Blue
    iss_image = [
    X, X, O, O, O, O, X, X,
    X, X, O, X, X, O, X, X,
    X, X, O, X, X, O, X, X,
    X, X, X, X, X, X, X, X,
    X, X, O, X, X, O, X, X,
    X, X, O, X, X, O, X, X,
    X, X, O, O, O, O, X, X,
    O, O, O, O, O, O, O, O
    ]
    sense.set_pixels(iss_image)

  def clear_alert(self):
    sense.clear()

  def work(self, home_lat, home_long):
    try:
      response = urllib.urlopen(url)
      data = json.loads(response.read())
      response.close()
    except: 
      self.log("IOError: Retrying")
      pass
      return
    iss_lat = data['latitude']
    iss_long = data['longitude']
    distance = self.sph_dist(home_lat, home_long, iss_lat, iss_long)
    closest_distance = 401
    if distance < 400:
            self.alert()
            self.logCoordinates(distance, home_lat, home_long, iss_lat, iss_long)
            if distance < closest_distance:
              closest_distance=distance
    else:
            self.clear_alert()
    return closest_distance

  def log(self, message):
    logging.info(message)

  def logCoordinates(self, distance, home_lat, home_long, iss_lat, iss_long):
    logging.info("ISS Latitude = %s Longitude = %s Distance = %s ",iss_lat,iss_long,distance)

  def sph_dist(self, lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    return arc * 3960

  def run(self):
    logging.basicConfig(format='%(asctime)s | iss_tracker | %(levelname)s | %(message)s', filename='track_iss.log',level=logging.INFO) 
    self.log("Started Tracking ISS")
    try:
      while True:
        closest_distance = self.work (home_lat, home_long)
        time.sleep(30)
    except (SystemExit,KeyboardInterrupt):
      self.clear_alert()
      logging.info("Stopped Tracking ISS Closest Distance = %s",closest_distance)
      pass
    except:
      self.clear_alert()
      logging.exception("Unexpected Error: Stopped Tracking ISS")
      raise

if __name__ == '__main__':
  try:
    run = DaemonRunner(Tracker())
    run.daemon_context.working_directory=os.getcwd()
    run.do_action()
  except DaemonRunnerStopFailureError:
    print("iss_tracker is not running")
