# translated from ARDUINO prototype code (please kill me)

from scipy import integrate

numReadings = int(10)
# int readings[numReadings] wtf does this do
readIndex = int(0)
total = float(0)
average = float(0)
sensorPin = "A5"
# pressed = True ????
l = 0 # why
decToPct = 100 # why
current = int(0)
buttonStatusLeft = 0
coutner = float(0)
aState = int(0)
aLastState = int(0)
button = int(6) # ref digital pin 6 as a digital pin
mode = int(0) # init variable
rollerButtonPin = int(3) # ref digital pin 3 as a button pin
rollerSignalPin = int(4) # ref digital pin 4 as a signal pin
rollerSignalPinPhase = int(5) # ref digital pin 5 as a phase pin
currentLength = float(0) # init variable
circumference = float(0) # init variable
rollerButton = int(0) # init variable
