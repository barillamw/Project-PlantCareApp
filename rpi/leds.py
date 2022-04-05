#!/usr/bin/python3

import board
import neopixel
import sys

#Set the Colors for the Grow Lights
growColors = [[0,70,255],[255,0,0],[161,0,0],[0,70,255],[255,0,0],[0,70,255],[161,0,0],[255,0,0],[0,70,255],[255,0,0],[161,0,0]]

#Create light strands
lightLength = len(growColors)
grow = neopixel.NeoPixel(board.D18,lightLength*2)
backlight = neopixel.NeoPixel(board.D12, 20)

#Grow Light Command uses binary to control the Lights
#Command: sudo python3 leds.py grow <light 1> <light 2>

if (sys.argv[1] == "grow"):
    #Reset Grow Lights
	grow.fill((0,0,0))
    if (sys.argv[2] == "1"):
        #Turn Grow light 1 on
		for i in range(0,lightLength-1):
            grow[i] = (growColors[i])
    if (sys.argv[3] == "1"):
        #Turn Grow light 2 on
		for i in range (0,lightLength-1):
            grow[i+lightLength] = (growColors[i])
			
#Backlight command takes in RGB vlaues as arguments
#Command: sudo python3 leds.py backlight <red> <green> <blue>

elif (sys.argv[1] == "backlight"):
    if(sys.argv[2] == "off"):
        #Turn off the Backlight
		backlight.fill((0,0,0))
    else:
        #Parse the argument color Codes
		red = int(sys.argv[2])
        green = int(sys.argv[3])
        blue = int(sys.argv[4])

		#Set Backlight Color 
		backlight.fill((red,green,blue))