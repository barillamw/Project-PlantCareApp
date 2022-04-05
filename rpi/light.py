#!/usr/bin/python3
# for interacting with GPIO pins
import gpiozero
import sys
import time
lightPin = 6
light = gpiozero.LED(lightPin, active_high = False)

# check command line argument if we should turn on or off
if sys.argv[1] == "on":
    light.on()
    while light.is_lit:
        # sleep for an hour then check if we should run
        time.sleep(60*60)
elif sys.argv[1] == "off":
    light.off()
