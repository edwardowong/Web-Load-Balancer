#CS3357 Assignment 4 balancer.py
#By Edward Wong
#December 9 2020
import socket
import sys
import os
import select
import random
import datetime
import time
from itertools import cycle

#Define a constant for the buffer size
BUFFER_SIZE = 1024

#Define a constant for how many minutes the balancer should run until it times out
MINUTES = 1

# A function that creates an HTTP header
def createHeader(sock):
    message = 'HTTP/1.1 301 Moved Permanently \r\nLocation: '+str(sock.getpeername()[0])+':'+str(sock.getpeername()[1])+' \r\n\r\n'
    return message


# A function to create a HTTP GET message
def createGetMessage(ip, port, fileName):
    request = f'GET {fileName} HTTP/1.1\r\nHost: {ip}:{port}\r\n\r\n'
    return request

class loadBalancer(object):
    socketList = list()
    timeout = time.time() + 60*MINUTES

    def __init__(self):
        self.ip = 'localhost'
        self.port = 0
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientSocket.bind((self.ip, int(self.port)))
        self.clientSocket.listen(10)
        print("Balancer's address and port:", self.clientSocket.getsockname())

    # Function used to redirect client to the server
    def start(self):
        while True:
            print("Balancer is listening...")
            if time.time() > self.timeout:
                print("Reconfiguring servers...")
                self.timeout = time.time() + 60*MINUTES
                self.setup()
                self.start()
            try:
                connection, addr = self.clientSocket.accept()
                print("Got connection from", addr)
                serverSocket = self.select()
                request = connection.recv(BUFFER_SIZE).decode()
                message = createHeader(serverSocket)
                connection.send(message.encode())
            except socket.error:
                #If a server crashes, remove it from the list
                self.setup()

    # Function used to configure the server sockets and pick a socket to use for the client
    def setup(self):
        compList = []
        self.socketList.clear()
        if len(sys.argv) <= 1:
            print("Please enter servers in the command line!")
            sys.exit(1)
        print("Available servers:")
        #Runs performance test
        for i in range(0, len(sys.argv)-1):
            try:
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                splitAddress = sys.argv[i+1].split(":")
                serverIP = splitAddress[0]
                serverPort = splitAddress[1]
                serverSocket.connect((serverIP, int(serverPort)))
                message = createGetMessage(serverIP, serverPort, 'test.txt')
                startTime = datetime.datetime.now()
                serverSocket.send(message.encode())
                while True:
                    received = serverSocket.recv(BUFFER_SIZE)
                    if not received:
                        break
                endTime = datetime.datetime.now()
                totalTime = (endTime - startTime).microseconds
                compList.append(totalTime)
                self.socketList.append(serverSocket)
                print(serverSocket.getpeername())
            except:
                print("('" + serverIP + "', "+serverPort+") is not available.")

        if len(compList) == 0:
            print("There are no servers remaining!")
            sys.exit(1)

        #Increases the chance of using a faster socket by appending more faster sockets
        for i in range(0, len(compList)):
            for j in range(0, len(compList)):
                if j > i:
                    self.socketList.append(self.socketList[j])

    def select(self):
        return random.choice(self.socketList)

if __name__ == '__main__':
    try:
        balancer = loadBalancer()
        balancer.setup()
        balancer.start()
    except KeyboardInterrupt:
        print("Interrupt detected! Exiting the balancer...")
        sys.exit(1)




