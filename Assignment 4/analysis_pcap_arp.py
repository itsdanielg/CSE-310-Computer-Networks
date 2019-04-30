# Daniel Garcia
# ID: 111157499

import dpkt
import sys

# Name of PCAP file to be parsed through
fileName = 'assignment4_my_arp.pcap'

# Boolean to check only ONE ARP exchange
packetRequest = False
packetReply = False

def main():

    # Output results to a separate file
    sys.stdout = open('pcapsummary.txt', 'w')

    # Open and read the PCAP file in bytes
    pcapFile = open(fileName, "rb")
    pcap = dpkt.pcap.Reader(pcapFile)

    print("---------- One ARP Packet Exchange ----------")
    
    # Iterate through each packet in the PCAP file
    packetCounter = 1
    for ts, buf in pcap:

        # Check if this packet is an ARP packet
        packetType = buf[12:14]
        if packetType == b'\x08\x06':

            # Get destination address
            destinationAddress = ""
            counter = 0
            for byte in buf[0:6]:
                if counter != 0:
                    destinationAddress += ":" + str(hex(byte))[2:4]
                else:
                    destinationAddress = str(hex(byte))[2:4]
                counter += 1

            # Get source address
            sourceAddress = ""
            counter = 0
            for byte in buf[6:12]:
                if counter != 0:
                    sourceAddress += ":" + str(hex(byte))[2:4]
                else:
                    sourceAddress = str(hex(byte))[2:4]
                counter += 1
            
            # Get hardware type
            hardwareType = "0x" + str(buf[14:16])[4:6] + str(buf[14:16])[8:10]
            hardwareType = int(hardwareType, 16)
            hardwareType = getHardware(hardwareType) + " (" + str(hardwareType) + ")"
            
            # Get protocol type
            protocolType = "0x" + str(buf[16:18])[4:6] + str(buf[16:18])[8:10]
            protocolType = getProtocol(protocolType) + " (" + protocolType + ")"

            # Get hardware size
            hardwareSize = buf[18]

            # Get protocol size
            protocolSize = buf[19]

            # Get opcode
            opcode = "0x" + str(buf[20:22])[4:6] + str(buf[20:22])[8:10]
            opcode = int(opcode, 16)
            opcode = getOpcode(opcode) + " (" + str(opcode) + ")"

            # Get sender MAC address
            senderMACAddress = ""
            counter = 0
            for byte in buf[22:28]:
                if counter != 0:
                    senderMACAddress += ":" + str(hex(byte))[2:4]
                else:
                    senderMACAddress = str(hex(byte))[2:4]
                counter += 1

            # Get sender IP address
            senderIPAddress = ""
            counter = 0
            for byte in buf[28:32]:
                if counter != 0:
                    senderIPAddress += "." + str(byte)
                else:
                    senderIPAddress = str(byte)
                counter += 1

            # Get target MAC address
            targetMACAddress = ""
            counter = 0
            for byte in buf[32:38]:
                if counter != 0:
                    targetMACAddress += ":" + str(hex(byte))[2:4]
                else:
                    targetMACAddress = str(hex(byte))[2:4]
                counter += 1

            # Get target IP address
            targetIPAddress = ""
            counter = 0
            for byte in buf[38:42]:
                if counter != 0:
                    targetIPAddress += "." + str(byte)
                else:
                    targetIPAddress = str(byte)
                counter += 1

            # Print all information
            
            # Stop printing if there's already been one ARP packet exchange
            if packetRequest and packetReply:
                continue
            else:
                print("")
                print("Packet Number:", packetCounter, "(ARP)")
                print("Ethernet Source Address:", sourceAddress)
                print("Ethernet Destination Address:", destinationAddress)
                print("Hardware Type:", hardwareType)
                print("Protocol Type:", protocolType)
                print("Hardware Size:", hardwareSize)
                print("Protocol Size:", protocolSize)
                print("Opcode:", opcode)
                print("Sender MAC Address:", senderMACAddress)
                print("Sender IP Address:", senderIPAddress)
                print("Target MAC Address:", targetMACAddress)
                print("Target IP Addresss:", targetIPAddress)

        packetCounter += 1

    # Close the PCAP file
    pcapFile.close()

# Helper method to get hardware type
def getHardware(hardwareType):
    if hardwareType == 1:
        return "Ethernet"
    elif hardwareType == 6:
        return "IEEE 802 Networks"
    elif hardwareType == 7:
        return "ARCNET"
    elif hardwareType == 15:
        return "Frame Relay"
    elif hardwareType == 16:
        return "Asynchronous Transfer Mode [ATM]"
    elif hardwareType == 17:
        return "HDLC"
    elif hardwareType == 18:
        return "Fibre Channel"
    elif hardwareType == 19:
        return "Asynchronous Transfer Mode [ATM]"
    elif hardwareType == 20:
        return "Serial Line"
    else:
        return ""

# Helper method to get protocol type
def getProtocol(protocolType):
    if protocolType == '0x0800':
        return "IPv4"
    else:
        return ""

def getOpcode(opcode):
    if opcode == 1:
        packetRequest = True
        return "ARP Request"
    elif opcode == 2:
        packetReply = True
        return "ARP Reply"
    elif opcode == 3:
        packetRequest = True
        return "RARP Request"
    elif opcode == 4:
        packetReply = True
        return "RARP Reply"
    elif opcode == 5:
        packetRequest = True
        return "DRARP Request"
    elif opcode == 6:
        packetReply = True
        return "DRARP Reply"
    elif opcode == 7:
        return "DRARP Error"
    elif opcode == 8:
        packetRequest = True
        return "InARP Request"
    elif opcode == 9:
        packetReply = True
        return "InARP Reply"
    else:
        return ""
        


# Run the program
main()