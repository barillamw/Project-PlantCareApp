#!/usr/bin/python3
# import gpiozero
from socket import *
from time import sleep

serverName = '192.168.50.47'
serverPort = 50000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

try:
    while 1:
        # get user input
        sentence = input("Input a command: ")
        # send the byte string that we want
        clientSocket.send(str.encode(sentence))
        # receive the response from the server
        response = clientSocket.recv(1024)
        # print out the response
        print("From Server: %s" % (response.decode()))
except KeyboardInterrupt as interrupt:
    # close the socket if the user as hit ctrl+c
    clientSocket.close()
