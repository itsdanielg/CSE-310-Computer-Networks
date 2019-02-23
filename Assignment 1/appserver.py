# Daniel Garcia
# ID: 111157499

from socket import *
from struct import *
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
    try:
        serverSocket.bind((serverHost, serverPort))
    except error:
        print("ERROR: Server socket failed to bind with host and port.")
        sys.exit(0)

    # Start listening for connections
    serverSocket.listen(1)
    print("SUCCESS: Server created! Now listening for connections...")

    # Send message to client once client connects
    try:
        connectionSocket, connectionAddress = serverSocket.accept()
        print("SUCCESS: Connected to", connectionAddress, "\n")
        connectionSocket.send(str.encode("SUCCESS: Connected to server!"))
    except error:
        print("ERROR: Server socket failed to connect with host and port.")
        sys.exit(0)

    # Set up infinite loop to send/receive requests
    while True:

        # Wait for client request (Formatted as struct)
        dataReceived = connectionSocket.recv(257)

        # Unpack struct into tuple
        messageLength = dataReceived[1]
        structFormat = 'cB' + str(messageLength) + 's'
        dataReceived = unpack(structFormat, dataReceived)
        messageType = dataReceived[0].decode("utf-8")
        message = dataReceived[2].decode("utf-8")

        # Print data received from client to terminal
        print("-------------------------------------------------------")
        print("Client:", connectionAddress, "\n")
        print("Data Received:")
        print("Message Type:", messageType)
        print("Message Length:", messageLength)
        print("Message:", message, "\n")

        # Invoke method to find name from database
        response = findName(message)

        # Set error response if email is invalid
        if (response == -1):
            response = "ERROR: Invalid email address entered."
        # Set error response if name could not be found
        elif (response == 0):
            response = "ERROR: Name could not be found in the database."
        # Else, set success response
        else:
            response = "SUCCESS: \"" + message + "\" belongs to \"" + response + "\""

        # Pack response into struct
        responseLength = len(response)
        structFormat = 'cB' + str(responseLength) + 's'
        responseType = b'R'
        responseBytes = response.encode("utf-8")
        responseStruct = pack(structFormat, responseType, responseLength, responseBytes)
        connectionSocket.send(responseStruct)
        
        # Print data sent to client to terminal
        print("Data Sent:")
        print("Message Type:", responseType.decode("utf-8"))
        print("Message Length:", responseLength)
        print("Message:", response, "\n")
        print("-------------------------------------------------------")

# Method to return the full name of an associated email address
def findName(message):
    if (message == "a"):
        return -1
    elif (message == "b"):
        return 0
    else:
        return "Daniel Garcia"

startServer()