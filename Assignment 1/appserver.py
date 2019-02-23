# Daniel Garcia
# ID: 111157499

from socket import *
import sys

# Create and start the server for the application
def startServer():

    # Create server socket; return false if creation fails
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        print("SUCCESS: Server socket created!")
    except error:
        print("ERROR: Server socket failed to create.")
        sys.exit(0)

    # Set up host and port
    serverHost = "127.0.0.1"
    serverPort = 8887

    # Bind the server socket to the host
    serverSocket.bind((serverHost, serverPort))

    # Start listening for connections
    serverSocket.listen(1)
    print("SUCCESS: Server created! Now listening for connections...")

    # Send message to client once client connects
    connectionSocket, connectionAddress = serverSocket.accept()
    print("SUCCESS: Connected to", connectionAddress, "\n")
    connectionSocket.send(str.encode("SUCCESS: Connected to server!"))

    # Set up infinite loop to send/receive requests
    while True:
        dataReceived = connectionSocket.recv(257)
        dataReceived = dataReceived.decode("utf-8")
        print("Data Received:", dataReceived)
        dataToSend = findName(dataReceived)
        if (dataToSend == -1):
            dataToSend = "ERROR: Email Address Not Found"
            connectionSocket.send(str.encode(dataToSend))
        else:
            dataToSend = "SUCCESS: \"" + dataReceived + "\" belongs to \"" + dataToSend + "\""
            connectionSocket.send(str.encode(dataToSend))
        print("Data Sent:", len(dataToSend), "\n")
        

# Method to return the full name of an associated email address
def findName(email):
    if (email == "a"):
        return -1
    else:
        return "Daniel Garcia"

startServer()