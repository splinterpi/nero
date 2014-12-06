import urllib, json, threading, math, time
from sense_hat import SenseHat

url= "https://api.wheretheiss.at/v1/satellites/25544"
home_lat = 52.1249
home_long = -0.2188

sense = SenseHat()

def work(home_lat, home_long):
  response = urllib.urlopen(url)
  data = json.loads(response.read())
  response.close()
  iss_lat = data['latitude']
  iss_long = data['longitude']
  distance = sph_dist(home_lat, home_long, iss_lat, iss_long)
  if distance < 400:
     display_alert()
  else:
     clear_screen()
  printCoordinates(distance, home_lat, home_long, iss_lat, iss_long)
  threading.Timer(30.0, work, [home_lat, home_long]).start()
  
def printCoordinates(distance, home_lat, home_long, iss_lat, iss_long):
  print "The International Space Station's current coordinates are "
  print "Latitude =",iss_lat," ","Longitude =",iss_long
  print "Current distance to the ISS: ",distance

def sph_dist(lat1, long1, lat2, long2):
  degrees_to_radians = math.pi/180.0
  phi1 = (90.0 - lat1)*degrees_to_radians
  phi2 = (90.0 - lat2)*degrees_to_radians
  theta1 = long1*degrees_to_radians
  theta2 = long2*degrees_to_radians
  cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
  math.cos(phi1)*math.cos(phi2))
  arc = math.acos( cos )
  return arc * 3960

def display_alert():
  X = [30, 144, 255]  # Blue
  O = [0, 0, 0]  # Black
  
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

work (home_lat, home_long) 
