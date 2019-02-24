# Daniel Garcia
# ID: 111157499

from socket import *
from struct import *
import sys

# Create and start a client for the application
def startClient():

    # Create client socket; Exit client if socket creation fails
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        print("SUCCESS: Client socket created!")
    except error:
        print("ERROR: Client socket failed to create.")
        sys.exit(1)

    # Set up host and port to connect to
    serverHost = "127.0.0.1"
    serverPort = 8887

    # Connect the client socket to the host
    try:
        clientSocket.connect((serverHost, serverPort))
    except error:
        print("ERROR: Client socket failed to connect with host and port.")
        sys.exit(0)

    # Receive server connect message and print to client
    connectSuccessMessage = clientSocket.recv(1024)
    print(connectSuccessMessage.decode("utf-8"), "\n")

    # Print welcome message to terminal
    print("Hello! Welcome to the Addressbook application!\n")

    # Ask for user input
    message = input("Please Enter a Valid Email Address: (Enter q to Quit Application) ")
    
    # If user input is "q", end loop
    while (message != "q"):

        # Ask for user input again if message is over 255 characters long
        if (len(message) > 255):
            print("\nInput is over 255 characters long. Please try again.")
            message = input("Please Enter a Valid Email Address: (Enter \"q\" to Quit Application) ")
            continue

        # Pack message into struct
        structFormat = 'cB' + str(len(message)) + 's'
        messageType = b'Q'
        messageBytes = message.encode("utf-8")
        messageStruct = pack(structFormat, messageType, len(message), messageBytes)

        # Encode user input and send to server
        try:
            clientSocket.send(messageStruct)
        except ConnectionResetError:
            print("Server has shutdown. Application will now close.")
            break

        # Wait for server response and store in dataReceived variable
        dataReceived = clientSocket.recv(257)

        # Unpack struct into tuple
        responseLength = dataReceived[1]
        structFormat = 'cB' + str(responseLength) + 's'
        dataReceived = unpack(structFormat, dataReceived)
        responseType = dataReceived[0].decode("utf-8")
        responseMessage = dataReceived[2].decode("utf-8")

        # Print response received to terminal
        print(responseMessage, "\n")

        # Ask for user input again
        message = input("Please Enter a Valid Email Address: (Enter \"q\" to Quit Application) ")
    
    # Close client socket
    clientSocket.close()

# Initialize client
startClient()