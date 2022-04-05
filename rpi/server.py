#!/usr/bin/python3
# for timing and scheduling
import datetime
import time
import sched
# for mutliprocessing
import multiprocessing as mp
# for interacting with GPIO pins
import gpiozero
# for networking
from socket import *
# for saving the state
import pickle
import os.path
# for interacting with sensors
from board import SCL, SDA
import busio
import board
import neopixel
from adafruit_seesaw.seesaw import Seesaw

# TODO get database setup and give it a way to access
# https://www.tutorialspoint.com/python/python_database_access.htm

# TODO make this work for the lights to turn on on a schedule
# https://schedule.readthedocs.io/en/stable/faq.html#how-can-i-pass-arguments-to-the-job-function

# setup pins, these are placeholders for now
servoPin1 = 19
servoPin2 = 26
pumpPin = 13
lightPin = 6
# set up the soil sensor
i2c_bus = busio.I2C(SCL, SDA)
ss = Seesaw(i2c_bus, addr=0x36)

# initialize all sensor readings to 0
uvIndex = 0
soilIndex = 0

# initialize the two servos
servo1 = gpiozero.Servo(servoPin1, initial_value = 0)
servo2 = gpiozero.Servo(servoPin2, initial_value = 0)

# variable to keep track of which plant is getting watered
# default 0 is everything closed
state = 0
pump = gpiozero.LED(pumpPin, active_high = False)
# timers for the pump and light
# 4 hours in seconds
lightTimer = 60 * 60 * 4
# constants for the lights
#Set the Colors for the Grow Lights
growColors = [[0,70,255],[255,0,0],[161,0,0],[0,70,255],[255,0,0],[0,70,255],[161,0,0],[255,0,0],[0,70,255],[255,0,0],[161,0,0],[0,70,255],[255,0,0],[161,0,0],[0,70,255]]
#Create light strands
lightLength = len(growColors)
grow = neopixel.NeoPixel(board.D18,lightLength*2)
backlight = neopixel.NeoPixel(board.D12, 20)

# one for each plant, measured in seconds
pumpTimer = [10, 10, 10, 10]
filename = "lastWateredSave.pk"

# figure out if the server has been run before by checking if there is saved data
if not os.path.isfile(filename):
    lastWatered = ["", "", "", ""]
else:
    # load the previous run's data
    with open(filename, 'rb') as file:
        lastWatered = pickle.load(file)

# I don't think we need a queue of pumping actions - srhollan
pumpLock = mp.Lock()

# open up the socket on the server end
TCP_IP = '192.168.1.109'
TCP_PORT = 50000
BUFFER_SIZE = 1024
    
# create a TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)
# bind it to the correct port and IP address
serverSocket.bind((TCP_IP, TCP_PORT))
# listen for only five clients
serverSocket.listen()

# keep an array of all the threads running
allProcesses = []

"""
function that contains the main server code to receive clients
INPUTS: NONE
OUTPUTS: NONE
"""
def main():
    scheduledProcess = mp.Process(target = scheduledProcesses)
    scheduledProcess.start()
    allProcesses.append(scheduledProcess)
    try:
        while True:
            # accept connections
            clientSocket, clientAddr = serverSocket.accept()
            # the connected address
            print('Connection address:' + str(clientAddr))
            process = mp.Process(target=newClient, args=(clientSocket, clientAddr))
            process.start()
            allProcesses.append(process)
    except KeyboardInterrupt as interrupt:
        # teardown since we hit a keyboard interrupt
        grow.fill((0,0,0))
        backlight.fill((0,0,0))
        pump.off()
        serverSocket.shutdown(SHUT_RDWR)
        serverSocket.close()
        # shut everything down, process-wise
        for p in allProcesses:
            p.terminate()
        
"""
initiates the scheduled processes that will occur like 
watering the plant and turning the lamp on and off
INPUTS: an amount of time that we want to check
OUTPUTS: NONE
"""
def scheduledProcesses():
    # start the scheduler that we'll be using
    s = sched.scheduler(time.time, time.sleep)
    # TODO figure out what to put here, will probs deal with the database once that is set up    
    plantNum = 1
    timeInterval = 1000
    s.enter(timeInterval, 1, scheduledWater, argument=(s, timeInterval, plantNum,))
    s.run()

"""
function that waters the plant on a set schedule
the watering is done if the moisture is too low
adds another watering to the queue
INPUTS:
    scheduler - the scheduling queue
    timeInterval - a float of time before the next watering
    plantNum - which plant is getting watered
OUTPUTS: NONE
"""
def scheduledWater(scheduler, timeInterval, plantNum):
    global lastWatered
    # TODO have it check the sensors to see if it needs to be watered and set a timer saying when it should water again. Might need to be dry for a while
    waterPlant( plantNum )
    scheduler.enter(timeInterval, 1, scheduledWater, argument=(scheduler, timeInterval, plantNum,))

"""
function to handle a new client connection
INPUTS: clientSocket - the socket of the new client
        clientAddr - the address of the new client
OUTPUTS: NONE
"""
def newClient(clientSocket, clientAddr):
    try:
        while True:
            # receive data from client
            data = clientSocket.recv(BUFFER_SIZE)
            #print("received data: " + data.decode())
            if not data: break
            # turn the data from a byte string to a str
            data = data.decode()
            print("received data: " + data)
            # parse the command fully
            out = parse( clientSocket, data )
            # send a message back to the client saying we got it
            clientSocket.sendall(str.encode(out + "\n"))
    finally:
        clientSocket.close()

"""
parses an incoming command and delegates to the appropriate function to utilize the hardware
INPUTS: data - string of the command, similar to a url specifying object then function.
                ex) "light/on"
OUTPUTS: NONE
"""
def parse( clientSock, data ):
    #print(data)
    # split up the input string by forward slash
    allArgs = data.strip().split("/")
    # this should be the object that is going to perform the operation
    system = allArgs[0]
    # initialize return string
    returnStr = ""
    # check to see if it matches one of our operations
    if system == "light":
        returnStr = lightCommand( allArgs[1:] )
    elif system == "pump":
        returnStr = pumpCommand( allArgs[1:] )
    else:
        clientSock.sendall(b"Invalid Command")
        print("Invalid Command")
        returnStr = "InvalidCommand"
    return returnStr

"""
sets up the hardware for directing the water
INPUTS: NONE
OUTPUTS: NONE
"""
def setup():
    # close both the servos
    servo1.min()
    servo2.min()
    # time for the servos to move
    time.sleep(1)
    
"""
function that determines what to do with the lights
INPUTS: command - str what the light should do
OUTPUTS: NONE
"""
def lightCommand( allCommands ):
    command = allCommands[0]
    
    outStr = ""
    if command == "on":
        # 1 for grow light 1, 2 for grow light 2, 3 for backlight
        individualLight = int(allCommands[1])
        if individualLight == 3:
            color = allCommands[2]
            colorArrStr = color.replace("(","").replace(")","").split(",")
            colorArr = tuple(map(int, colorArrStr))
            lightOnOffColor( True, 3, colorArr)
        else:
            # Turn the light on and report to the Client
            lightOnOff( True, individualLight )

        outStr += "light on"
    elif (command == "off") :
        #Turn the Light off and report to the client
        lightOnOff( False, 0 )
        outStr += "light off"
    elif (command == "sensor") :
        # TODO figure out how to do this in python
        # Read the Light Sensor, Store in uvIndex and report to Client
        # uvIndex = analogRead(lightSensor)*10
        outStr += "The UV Index is..."
        outStr += uvIndex
    elif (command == "status"):
        # Report the Status of the Light to the Client
        outStr += "light is "
        if light.is_lit: 
            outStr += "on"
        else: 
            outStr += "off"
    else :
        # Report the unknown command to the client
        outStr += "Error: Unknown Light Command."
    return outStr

"""
function that turns the light on or off
INPUTS: onOff - boolean, true if on, false if off
OUTPUTS: NONE
"""
def lightOnOff( onOff , light):
    if ( onOff ):
        if light == 1:
            for i in range(0, lightLength-1):
                grow[i] = (growColors[i])
        if light == 2:
            for i in range (0, lightLength-1):
                grow[i+lightLength] = (growColors[i])
    else:
        grow.fill((0,0,0))

"""
function that turns the light on or off
INPUTS: onOff - boolean, true if on, false if off
OUTPUTS: NONE
"""
def lightOnOffColor( onOff , light, colorArr):
    if ( onOff ):
        if light == 3:
            backlight.fill(colorArr)
    else:
        backlight.fill((0,0,0))

"""
function that determines what to do with the pump
INPUTS: command - str what the pump should do
OUTPUTS: NONE
"""
def pumpCommand( commandArr ):
    global state
    global lastWatered
    # see if we are turning it on or off
    command = commandArr[0]
    # initialize the output
    outStr = ""
    if command == "status":
        #Report the Status of the pump to the client
        outStr += "Pump is at position " + str(state) 
        if pump.is_lit: 
            outStr += "and on"
        else: 
            outStr += "and off"

    elif command == "on" and commandArr[1] in "1234567890": 
    # Turn the pump on and report to client
        state = int(commandArr[1])
        outStr += waterPlant( state )
        
    elif command == "off":
        #Turn the pump off and report to the client
        pump.off()
        outStr += "Pump Turned Off."
    
    elif command == "close":
        try:
            pumpLock.acquire()
            controlFlow(0)
            outStr += "The valves are closed"
        finally:
            pumpLock.release()
        
    elif command == "sensor":
        outStr += readSoilSensor()

    elif command == "time" and commandArr[1] in "1234567890":
        plantNum = int(commandArr[1])
        outStr += "pumpTimer:" + lastWatered[plantNum - 1]

    else:
        #Report unknown command to the Client
        outStr += "Error: Pump Command Unkown."

    return outStr

"""
function that abstract reading data from the soil sensor
INPUTS: NONE
OUTPUTS: string in the format 'pumpSensor:tempInDegF,moistureLevel
"""
def readSoilSensor():
    # read moisture level through cpacitive touch pad
    touch = ss.moisture_read()

    # read temperature from the temperature sensor in celsius
    tempC = ss.get_temp()
    # convert to F
    tempF = round((tempC * 9/5) + 32, 1)

    # print("temp: " + str(tempF) + " moisture: " + str(touch))
    return "pumpSensor:" + str(tempF) + "," + str(touch)

"""
controls where the water goes based on the two servos
INPUTS: plantNum - a number 0-4 of which plant should be watered
        0 - all closed
        1 - plant #1
        2 - plant #2
        3 - plant #3
        4 - plant #4
OUTPUTS: NONE
"""
def controlFlow( plantNum ):
    # determine which plant to water
    if plantNum == 0:
        servo1.min()
        servo2.min()
    elif plantNum == 1:
        servo1.max()
        servo2.min()
    elif plantNum == 2:
        servo1.mid()
        servo2.min()
    elif plantNum == 3:
        servo1.min()
        servo2.mid()
    elif plantNum == 4:
        servo1.min()
        servo2.max()
    else:
        servo1.min()
        servo2.min()
    # print("pos: %d" % (plantNum))
    time.sleep(1)
    return plantNum


"""
function that abstracts watering a plant down to which plant should be watered
INPUTS: plantNum - the number of the plant we want to water, 1-4
OUTPUTS: outStr - string that is parseable by the Android app
"""
def waterPlant( plantNum ):
    global lastWatered
    # acquire the lock so only the current thread can get the lock for the pump to operate
    outStr = ""
    pumpLock.acquire()
    try:
        # move the servos to direct towards the right pump
        out = controlFlow(plantNum)
        # set to the new state
        state = plantNum
        # turn the pump off so we know its state
        pump.off()
        # turn the pump on for the number of seconds specified in pumpTimer for the plant
        # that is on_time, off_time is going to be one second, n is how many times we "blink" so only once since we only want
        # one power cycle
        pump.blink(on_time=pumpTimer[plantNum - 1], off_time = 1, n = 1, background = False)
        # updates the last time the plant was watered
        now = datetime.datetime.now()
        nowFormatted = now.strftime("%D %r")
        # update the time the plant has been watered
        lastWatered[plantNum - 1] = nowFormatted
        # string to return back to the phone
        outStr += "pumpTimer:" + nowFormatted
        # save the state of when the plants were last watered
        with open(filename, 'wb') as file:
            # dump water data into the file
            pickle.dump(lastWatered, file)
    finally:
        # release the lock no matter what happened so we don't deadlock
        pumpLock.release()
    return outStr


# start the script
if __name__ == "__main__":
    main()