#CS3357 Assignment 4 server.py
#By Edward Wong
#December 9 2020
import socket
import os

BUFFER_SIZE = 1024  #Define a constant for the buffer size

# A function that creates an HTTP header
def createHeader(value):
    message = 'HTTP/1.1 '
    if value == '200':
        message = message + value + ' OK\r\n'
    elif value == '404':
        message = message + value + ' Not Found\r\n'
    elif value == '501':
        message = message + value + ' Method Not Implemented\r\n'
    elif value == '505':
        message = message + value + ' Version Not Supported\r\n'
    elif value == '304':
        message = message + value + ' Not Modified\r\n'
    return message

# A function that generates file information
def fileInfo(fileName):
    if ((fileName.endswith('.jpg')) or (fileName.endswith('.jpeg'))):
        type = 'image/jpeg'
    elif (fileName.endswith('.gif')):
        type = 'image/gif'
    elif (fileName.endswith('.png')):
        type = 'image/jpegpng'
    elif ((fileName.endswith('.html')) or (fileName.endswith('.htm'))):
        type = 'text/html'
    else:
        type = 'application/octet-stream'
    size = os.path.getsize(fileName)
    return 'Content-Type: '+type+'\r\nContent-Length: '+str(size)+'\r\n\r\n'

# A function that returns the header and file info, as well as the file through the socket
def sendResponse(connection, code, fileName):
    header = createHeader(code) + fileInfo(fileName)
    connection.send(header.encode())
    file = open(fileName, 'rb')
    line = file.read(BUFFER_SIZE)
    while line:                                     #Loops the transfer of the file over the connection
        connection.send(line)                       #Sends the file in chunks
        line = file.read(BUFFER_SIZE)               #Reads the file in chunks
    file.close()

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creates a TCP connection for the server
    serverSocket.bind(('localhost', 0)) #Binds the TCP connection to our address

    while True:
        serverSocket.listen(1) #Server waits for two connections
        print("\nServer's address and port:", serverSocket.getsockname())
        print("Waiting for a connection...")

        connection, addr = serverSocket.accept()        #Accepts the connection from the client
        print("Got connection from", addr)
        message = connection.recv(BUFFER_SIZE).decode() #Server gets the client's request
        splitMessage = message.split()
        fileName = splitMessage[1]                   #Retrieve the file name from the GET request

        if splitMessage[0] != 'GET':                 #Detect if we did not receive a GET request
            print("Invalid request, sending 501 error.")
            sendResponse(connection, '501', '501.html')
        elif splitMessage[2] != 'HTTP/1.1':          #Detect if we did not get the proper HTTP version
            print("Invalid HTTP version, sending 505 error.")
            sendResponse(connection, '505', '505.html')
        else:
            try:
                reqFileTime = splitMessage[-1]
                while fileName[0] == '/':    #Strip '/' from file name if it exists
                    fileName = fileName[1:]
                print("Sending", fileName)
                open(fileName, 'rb')
                sendResponse(connection, '200', fileName)
            except FileNotFoundError:
                print("File not found, sending 404 error.")
                sendResponse(connection, '404', '404.html')

        connection.close()
    serverSocket.close()

if __name__ == '__main__':
    main()
