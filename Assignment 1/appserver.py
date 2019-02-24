# Daniel Garcia
# ID: 111157499

from socket import *
from struct import *
from _thread import *
import sys
import csv

# Create and start the server for the application
def startServer():

    # Create server socket; Exit server if creation fails
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        print("SUCCESS: Server socket created!")
    except error:
        print("ERROR: Server socket failed to create.")
        sys.exit(0)

    # Set up host and port
    serverHost = "127.0.0.1"
    serverPort = 8887

    # Bind the server socket to the host; Exit server if bind fails
    try:
        serverSocket.bind((serverHost, serverPort))
    except error:
        print("ERROR: Server socket failed to bind with host and port.")
        sys.exit(0)

    # Start listening for connections
    serverSocket.listen(1)
    print("SUCCESS: Server created! Now listening for connections...\n")

    # Set up infinite loop to send/receive requests
    while True:

        # Send message to client once client connects; Exit server if sending fails
        try:
            connectionSocket, connectionAddress = serverSocket.accept()
            print("SUCCESS: Connected to", connectionAddress, "\n")
            connectionSocket.send(str.encode("SUCCESS: Connected to server!"))
        except error:
            print("ERROR: Server socket failed to connect with host and port.")
            sys.exit(0)
        
        # Start new thread when new client is connected
        thread = start_new_thread(clientThread, (connectionSocket, connectionAddress))

def clientThread(connectionSocket, connectionAddress):

    while True:

    # Wait for client request (Formatted as struct)
        try:
            dataReceived = connectionSocket.recv(257)
            if (dataReceived == b''):
                break
        except ConnectionResetError:
            break

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
        # Else, set success response
        else:
            response = "SUCCESS: \"" + message + "\" belongs to \"" + response + "\""
            # Check if response is over 255 bytes long
            if (len(response) > 255):
                response = "WARNING: Response message exceeded 255 bytes. Email found in database."
        
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
        print("Message:", response)
        print("-------------------------------------------------------\n")

    # Close socket when thread ends
    print("SUCCESS: Connection", connectionAddress, "has closed.\n")
    connectionSocket.close()

# Method to return the full name of an associated email address
def findName(message):
    with open('database.csv') as databaseCSV:
        csvReader = csv.reader(databaseCSV, delimiter=",")
        for row in csvReader:
            messageLower = message.lower()
            if (messageLower == row[0]):
                return str(row[1])
        return -1

startServer()