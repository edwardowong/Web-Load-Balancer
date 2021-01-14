#CS3357 Assignment 4 client.py
#By Edward Wong
#December 9 2020
import socket
import sys

#Define a constant for the buffer size
BUFFER_SIZE = 1024


# A function to create a HTTP GET message
def createGetMessage(ip, port, fileName):
    request = f'GET {fileName} HTTP/1.1\r\nHost: {ip}:{port}\r\n\r\n'
    return request


#A function used to copy a file from the server
def saveFile(socket, fileName):
    with open(fileName, 'wb') as file:
        while True: #Creates a new file containing information from the file given by the server
            data = socket.recv(BUFFER_SIZE)   			    #Get the chunk of the file
            if not data:
                break
            file.write(data)                			    #Write the chunk into a new file
    print("File obtained.")
    file.close()


def main():
    argList = sys.argv
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #Creates a TCP connection for the client
    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       #Creates a TCP connection to redirects
    while True:                                                 #Loops until a valid address and port are entered
        try:
            serverip = input("Input an address: ")    #Takes the server address as input
            serverPort = input("Input a port: ")     #Takes the server port as input
            clientSocket.connect((serverip, int(serverPort)))   #Connects the client to the host
            break
        except (ConnectionRefusedError, ValueError, OSError):   #Retry if an error occurs
            pass
            print("This is not a valid address! Please retry.")

    print("Connected to the address!")
    #Requests a file from the server by taking the filename as input
    request = input("Input the name of the file you would like to retrieve: ")
    message = createGetMessage(serverip, serverPort, request)
    clientSocket.send(message.encode())

    #Retrieves a response from the server
    response = clientSocket.recv(BUFFER_SIZE).decode()
    print(response)
    responseList = response.split(' ')
    status = responseList[1]
    if status == '301':
        #Requests a file from the redirected server
        splitAddress = responseList[5].split(':')
        serverIP = splitAddress[0]
        serverPort = splitAddress[1]

        newSocket.connect((serverIP, int(serverPort)))
        message = createGetMessage(serverIP, serverPort, request)
        newSocket.send(message.encode())

        #Retrieve response and save file
        response = newSocket.recv(BUFFER_SIZE).decode()
        print(response)
        saveFile(newSocket, request)
    elif status != '200':
        print(status, "error was received.")
    #Continues if the server returns a 200 message indicating everything is fine
    else:
        saveFile(clientSocket, request)
    newSocket.close()
    clientSocket.close()
    print("Connection closed.")

if __name__ == '__main__':
    main()
