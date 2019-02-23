# Daniel Garcia
# ID: 111157499

from socket import *
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
    clientSocket.connect((serverHost, serverPort))

    # Receive server connect message and print to client
    connectSuccessMessage = clientSocket.recv(1024)
    print(connectSuccessMessage.decode("utf-8"), "\n")

    # Print Welcome Message
    print("Hello! Welcome to the Addressbook application!\n")

    # Set up infinite loop to send/receive requests
    message = input("Please Enter a Valid Email Address: (Enter q to Quit Application) ")
    while (message != "q"):
        clientSocket.send(str.encode(message))
        dataReceived = clientSocket.recv(1024)
        dataReceived = dataReceived.decode("utf-8")
        print(dataReceived, "\n")
        message = input("Please Enter a Valid Email Address: (Enter q to Quit Application) ")
    clientSocket.close()

startClient()